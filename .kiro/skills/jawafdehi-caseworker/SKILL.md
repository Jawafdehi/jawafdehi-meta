---
name: jawafdehi-caseworker
description: AI assistant for Jawafdehi caseworkers to analyze corruption cases, prepare case documentation, and publish to the Jawafdehi platform
---

# Jawafdehi Caseworker Skill

CIAA/Special court case number is of format (3 digit year-case type-case number) (e.g. 081-CR-0123).

Please prompt the user for the case number. This is absolutely required.

1. Local casework folder should be casework/<CIAA-case-number>. You MUST retrieve the case number to create the casework folder.
2. The goal is to prepare and publish a case in Jawafdehi.org. It wil be something like https://jawafdehi.org/case/<case-identifier> (e.g. https://jawafdehi.org/case/209).

A Jawafdehi case can be in state DRAFT, IN_REVIEW, PUBLISHED, and CLOSED. While working on a case, work in either DRAFT or IN_REVIEW state.

When a case is IN_REVIEW, it is viewable in the Jawafdehi website as an unlisted URL, e.g. https://jawafdehi.org/case/209. DRAFT cases can be worked upon, but aren't visible in the website.

Jawafdehi cases should be in Nepali language whenever possible.


## Steps
1. When a user provides a case number, we should also ask user to provide the Jawafdehi case identifier or case URL.
2. We search the case in jawafdehi using the get_jawafdehi_case MCP tool. We will get the full sources from jawafdehi case.
3. We report some information about the case to the user.
4. We use the `ngm_extract_case_data` tool to download the latest progress on the Special court case in <case folder>/review/case-progress-<Special court case no>.md.
4. We then prompt the user what they would like to do.

Valid options are:
1. Improving the case.
2. Perform a review.
3. Download the sources locally.
4. If and only if the jawafdehi case does not exist, we should check with user if they would like to create a new case, in which we should use the create_jawafdehi_case MCP tool.

### Improving the case
1. Improving the case requires it to be in `DRAFT` or `IN_REVIEW` status.
2. We use the `get_jawafdehi_case` to get current state and `patch_jawafdehi_case` to update using JSON patch.
3. Note that the `description` field supports HTML using TinyMCE.

### Downloading the sources locally.
We should download sources to casework folder when needed. Sources should be downloaded to casework folder/sources/raw, and their markdowns to casework folder/sources/markdown. We use `convert_to_markdown` tool to extract Markdown.

If there are newspaper sources or external links, we should also download them. Then we will use `convert_to_markdown` to convert them into markdown.

### Perform a review

To perform a case review, we must've downloaded the sources locally and converted them to markdown. Verify that the `sources` folder in the casework folder has all the sources downloaded locally, and then converted to markdown.

1. Retrieve the contents of [Jawafdehi Caseworker Knowledge Share](https://docs.google.com/document/d/1-AZedWGhcQjRH4E7a6q1CDWpeBcb_CVqa8S_kRLQCx4) Google Doc file. It contains guidelines on what to confirm against. Let's download and put the markdown or text in casework folder/review/knowledge-share.md/txt. Prefer txt over pdf/docx and let's also prefer curl or wget over fetch.
2. Retrieve the case contents and place them onto review/case-snapshot-<date>.json. If the case is in `IN_REVIEW` or `PUBLISHED` state, we can use `curl` to download this file directly, preserving integety. URL is of this format: https://portal.jawafdehi.org/api/cases/<jawafdehi-case-number>/.

Using the knowledge base and the case snapshot, as well as your knowledge of the case, let's create a file called review-<CIAA-case-number>-<date>.md.

The suggestions need to be categorized on severity. Higher severities appear on top.

## Default Output Format

Use this structure unless the user asks for something else:

```markdown
# समीक्षा सारांश

- प्रकाशित मुद्दा: <URL>
- CIAA केस नम्बर: <case number>
- नतिजा: <approved | approved_with_minor_edits | needs_revision | blocked>

## मैले समीक्षा गरेको सामग्री
- प्रकाशित Jawafdehi मुद्दाको सामग्री
- तुलना गर्न प्रयोग गरिएको temporary published-case फाइलको पाथ
- स्थानीय केस फोल्डरका समीक्षा गरिएका सबै Markdown फाइलहरूको सूची
- परामर्श गरिएका आधिकारिक केस रेकर्ड र स्रोत सामग्री

## निष्कर्षहरू
### १. [severity] — <निष्कर्ष शीर्षक>

- **प्रकाशित मुद्दामा:** ...
- **अभिलेखले देखाउँछ:** ...
- **आवश्यक संशोधन:** ...
- **प्रमाण:** ...

### २. [severity] — <निष्कर्ष शीर्षक>

- **प्रकाशित मुद्दामा:** ...
- **अभिलेखले देखाउँछ:** ...
- **आवश्यक संशोधन:** ...
- **प्रमाण:** ...

## अस्पष्टता वा अनसुल्झिएका प्रश्नहरू
- ...

## सिफारिस गरिएका अर्को सम्पादनहरू
1. ...
2. ...
3. ...
```

### NOTES

1. DO NOT CALL `submit_nes_change` MCP tool because that's not what we need for Jawafdehi cases. Modifies entities related with a Jawafdehi case means we update the case itself, patch the alleged entities list.

1. Whenever downloading case sources/evidences and other information from the web (e.g. newspapers), try using `curl` (or equivalent) first to preserve data integrity. `fetch` prints to stdout, polluting valuable context space, and may also tamper integrity.