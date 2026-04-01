# DRAFT REVIEW Instructions

Use this guide to review a local `case-draft.md` before submission to Jawafdehi.

## Inputs

- CIAA case number (for naming outputs)
- `casework/<case-number>/case-draft.md`
- All markdown evidence in `casework/<case-number>/sources/markdown/`
- Any additional local notes in the case folder

If `case-draft.md` is missing, stop and report `blocked`.

## Objective

Confirm that draft claims are accurate, source-backed, and submission-ready for `IN_REVIEW`.

Default review language is Nepali unless user explicitly asks for English.

## Review Procedure

1. Read `case-draft.md` fully.
2. Enumerate all markdown files under `sources/markdown/`.
3. Cross-check claims one-by-one against local sources:
   - Allegation wording and legal framing
   - Entity names and roles (accused/related)
   - Timeline dates and sequence
   - Evidence references and source fidelity
   - Financial figures and counts
4. Validate Nepali language quality:
   - clear and formal tone
   - consistent terminology
   - no ambiguous machine-translated phrasing
5. Flag missing mandatory submission fields:
   - title
   - description
   - at least one key allegation
   - at least one accused entity

## Severity Model

- `critical`: factually wrong, misleading, or unsupported; blocks submission
- `major`: important omission or inconsistency; requires revision before submission
- `minor`: low-risk quality issue; should be cleaned up
- `informative`: optional improvement suggestion

## Decision

End with exactly one decision:

- `approved`
- `approved_with_minor_edits`
- `needs_revision`
- `blocked`

Decision rules:
- any `critical` finding => `blocked`
- any `major` finding (with no critical) => `needs_revision`
- only `minor`/`informative` findings => `approved_with_minor_edits`
- no findings => `approved`

## Output Format

Save review as: `review-<CIAA-case-number>-<date-time>.md`

Use this structure:

```markdown
# समीक्षा सारांश

- CIAA केस नम्बर: <case number>
- समीक्षा वस्तु: <local case-draft path>
- नतिजा: <approved | approved_with_minor_edits | needs_revision | blocked>

## मैले समीक्षा गरेको सामग्री
- case-draft फाइल
- समीक्षा गरिएका स्थानीय Markdown स्रोत फाइलहरूको सूची

## निष्कर्षहरू
### १. [severity] — <शीर्षक>

- **ड्राफ्टमा:** ...
- **स्रोतले देखाउँछ:** ...
- **आवश्यक संशोधन:** ...
- **प्रमाण:** ...

## अस्पष्टता वा अनसुल्झिएका प्रश्नहरू
- ...

## सिफारिस गरिएका अर्को सम्पादनहरू
1. ...
2. ...
```
