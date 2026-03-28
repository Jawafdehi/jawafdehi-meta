# NGM Index v2.0 — Structure & Reference

The NGM index is a hierarchical JSON document tree served from the NGM Store at `https://ngm-store.jawafdehi.org`. It exposes all scraped documents (CIAA press releases, CIAA annual reports, Kanun Patrika) in a consistent format that the [NGM frontend](https://ngm.jawafdehi.org) and any programmatic consumer can traverse.

---

## Entry Point

```
https://ngm-store.jawafdehi.org/index-v2.json
```

This is the **root index**, always available at a stable URL. It lists the top-level sections of the archive as child stubs referencing date-versioned index files.

### Root Index Shape

```json
{
  "name": "root",
  "path": "/",
  "children": [
    {
      "name": "kanun-patrika",
      "path": "/kanun-patrika",
      "$ref": "https://ngm-store.jawafdehi.org/indices/2026-03-25/index.kanun-patrika.json"
    },
    {
      "name": "ciaa-annual-reports",
      "path": "/ciaa-annual-reports",
      "$ref": "https://ngm-store.jawafdehi.org/indices/2026-03-25/index.ciaa-annual-reports.json"
    },
    {
      "name": "ciaa-press-releases",
      "path": "/ciaa-press-releases",
      "$ref": "https://ngm-store.jawafdehi.org/indices/2026-03-25/index.ciaa-press-releases.json"
    }
  ],
  "next": null
}
```

The `$ref` URLs point to a **date-versioned** index directory (`/indices/YYYY-MM-DD/`). The date reflects when the index was last rebuilt, not the publication dates of the documents inside.

---

## Node Types

Every node in the tree is either a **branch** (has `children`) or a **leaf** (has `manuscripts`). A node can also be a **ref stub**: a lightweight pointer with only `name`, `path`, and `$ref` — used inside parent index files so that each child has its own separately-fetched file.

### Branch Node (with `$ref` stubs)

```json
{
  "name": "kanun-patrika",
  "path": "/kanun-patrika",
  "children": [...]   // OR "$ref" at the parent level
}
```

### Leaf Node (with manuscripts)

```json
{
  "name": "ciaa-press-releases",
  "path": "/ciaa-press-releases",
  "manuscripts": [...],
  "next": null          // or a URL for the next page
}
```

### Pagination

Leaf nodes with more than 30 manuscripts are paginated. The first page is at the canonical URL (`index.ciaa-press-releases.json`), and subsequent pages are linked via `"next"`:

```
index.ciaa-press-releases.json         → page 1
index.ciaa-press-releases.page-2.json  → page 2
...                                    (next: null on last page)
```

Consumers must follow `next` links until `null` to collect all manuscripts.

---

## Manuscript Schema

Each manuscript is a single downloadable file with attached metadata:

```json
{
  "url": "https://ngm-store.jawafdehi.org/uploads/...",
  "file_name": "3355. संस्कृति ... - 1.doc",
  "metadata": { ... }
}
```

Metadata fields vary by collection:

### `ciaa-press-releases` metadata

| Field | Type | Description |
|---|---|---|
| `press_id` | integer | Unique press release ID from `ciaa.gov.np/pressrelease/{id}` |
| `title` | string | Nepali-language title extracted from the press release page |
| `full_text` | string | Body text of the press release in Nepali |
| `publication_date` | string | Date in **BS (Bikram Sambat)** `YYYY-MM-DD` format, e.g. `"2082-12-08"` |
| `source_url` | string | Canonical URL on the CIAA website |
| `file_names` | array of strings | All attachment filenames belonging to this press release |

> **Note**: A single press release may have multiple attachments (PDF + DOC). Each attachment becomes its own `Manuscript` entry in the index, all sharing the same `press_id` in their metadata. The frontend groups them by `press_id` before display.

### `ciaa-annual-reports` metadata

| Field | Type | Description |
|---|---|---|
| `title` | string | Report title |
| `serial_number` | string | Report serial/issue number |
| `date` | string | Publication date |

### `kanun-patrika` metadata

No structured metadata — filenames are used directly as display names.

---

## Storage Layout

The raw files live in GCS under `ngm-store.jawafdehi.org`:

```
uploads/
  ciaa/
    press-releases/
      files/        ← attachment downloads (PDF, DOC)
      metadata/     ← one JSON file per press release (press_id.json)
      .checkpoint   ← last scraped press release ID
    annual-reports/
      pdf/          ← annual report PDFs
      metadata/     ← one JSON file per report
  supreme-court/
    kanun-patrika/  ← Kanun Patrika PDFs

indices/
  YYYY-MM-DD/       ← versioned index snapshot
    index.json                           ← root node
    index.kanun-patrika.json
    index.ciaa-annual-reports.json
    index.ciaa-press-releases.json       ← page 1
    index.ciaa-press-releases.page-2.json
    ...

index-v2.json   ← always points to latest versioned index
```

---

## Searching CIAA Press Releases

The index is a static JSON document — it has no server-side search API. To search press releases:

1. **Fetch all pages** starting from `$ref` in `index-v2.json`, following `next` links.
2. **Filter in memory** using `metadata.title`, `metadata.full_text`, or `metadata.publication_date`.

### Key searchable fields

| Field | Notes |
|---|---|
| `title` | Nepali. Contains names of accused persons/entities and charge description. |
| `full_text` | Nepali. Body of the press release — often truncated with a download note. |
| `publication_date` | BS date string. Filter by year: `"2082-..."`, `"2081-..."`, etc. |
| `press_id` | Integer. Monotonically increasing; newer releases have higher IDs. |
| `source_url` | Link back to `ciaa.gov.np` for the original page. |

### Example: Find press releases mentioning "केदार बहादुर अधिकारी"

```js
// 1. Fetch all manuscripts (follow pagination)
const manuscripts = await fetchAllManuscripts(pressReleasesRef);

// 2. Deduplicate by press_id (each file is a separate manuscript)
const unique = new Map();
for (const m of manuscripts) {
  const id = m.metadata.press_id;
  if (!unique.has(id)) unique.set(id, { meta: m.metadata, files: [] });
  unique.get(id).files.push(m);
}

// 3. Search
const query = "केदार बहादुर अधिकारी";
const results = [...unique.values()].filter(({ meta }) =>
  meta.title?.includes(query) || meta.full_text?.includes(query)
);
```

### Example: Filter by BS year

```js
const results = [...unique.values()].filter(({ meta }) =>
  String(meta.publication_date).startsWith("2082-")
);
```

---

## Index Rebuild

The index is rebuilt by the `ngm` scraper service on a schedule (GitHub Actions). The rebuild process:

1. Scrapers collect new press releases / documents into GCS (`uploads/`).
2. `python -m ngm.index.build_index` (via `ngm/index/build_index.py`) reads all metadata from `uploads/`, builds the tree, and writes:
   - `indices/YYYY-MM-DD/*.json` — the new versioned snapshot.
   - `index-v2.json` — updated to point to the new snapshot (root copy).

**Page size**: 30 manuscripts per page (configurable via `DEFAULT_PAGE_SIZE`).

---

## Related Files

| Path | Description |
|---|---|
| `services/ngm/ngm/index/models.py` | `Manuscript` and `IndexNode` dataclasses |
| `services/ngm/ngm/index/build_index.py` | `IndexBuilder` — builds and writes the tree |
| `services/ngm/ngm/ngscrape/spiders/ciaa_press_releases.py` | Scrapy spider that discovers and downloads CIAA press releases |
| `services/ngm/ngm/ngscrape/spiders/ciaa_annual_reports.py` | Scrapy spider for CIAA annual reports |
| `services/ngm/ngm/ngscrape/spiders/kanun_patrika.py` | Scrapy spider for Kanun Patrika |
| `services/ngm-frontend/src/components/IndexViewer.tsx` | React component consuming the index |
