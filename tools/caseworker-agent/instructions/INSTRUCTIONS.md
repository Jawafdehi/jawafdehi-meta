## Caseworker instructions

You are an expert agentic workflow runner and you are helping build a fact-based database of corruption cases for Nepal. You are responsible for integral case drafting into the Jawafdehi system.

Follow the user stories strictly in `prd.json`. Start by reading INSTRUCTIONS.md file from the tools/caseworker-agent/instructions folder, and then read progress.log and PRD.json from the casework folder thereafter. Verify the state from `prd.json` and keep track of your steps in `progress.log`. When you are updating progress.log, also include the system date/time. Execute one user story task at a time and then shut down.

NOTE: BEFORE start your work, aloways update progress.log. THEN, AFTER you have finished your work, you will need to conclude the progress log that you created.

CRITICAL: Once all user stories in `prd.json` are complete and the final Jawafdehi case is prepared, you MUST update the `is_complete` global flag in `prd.json` to `true`. This signals the workflow runner to stop iterating. If, for some reason, you are unable to complete the user stores, you may also mark `failed` which signals the runner that the workflow has failed and that it should stop.

CRITICAL: Once all user stories in `prd.json` are complete and the final Jawafdehi case is prepared, you MUST update the `is_complete` global flag in `prd.json` to `true`. This signals the workflow runner to stop iterating.

## US-001: Casework Folder Structure

Your working environment for each case is isolated within a unique case folder located at `casework/<case_number>`. This folder contains the following structure:

- `prd.json`: The Product Requirements Document containing the sequence of user stories/tasks you must follow.
- `progress.log`: The log file where you must record your steps and track completion progress.
- `instructions/`: A directory containing these instructions and potentially other reference materials.
- `sources/raw/`: A directory for storing raw source documents (like PDFs, HTML files, or images) before processing.
- `sources/markdown/`: A directory for storing the extracted or converted markdown versions of the source documents.

Any temporary files, drafts, or exported evidence for the case should be generated within this `casework/<case_number>` directory to keep the workspace organized.


## US-002: Collecting important information

### Case data

Use the `ngm_extract_case_data` tool to extract the full case data from the NGM database. You must save it in the casework folder as `sources/case_<case_number>_<date-time>.md`.

### CIAA Press releases
Find the CIAA press release for Special court case 081-CR-0123.

The CIAA press releases are located at URLs like https://ciaa.gov.np/pressrelease/2000. The press release ID seems to be sorted in ascending order.

Usually, CIAA press release are on the date when the case is filed to special court.

Download and save it at sources/raw/ciaa-press-release-<press-release-id>.pdf

Sample dates:
- https://ciaa.gov.np/pressrelease/1000: मिति २०७६/०१/१२ गते । 
- https://ciaa.gov.np/pressrelease/2000: मिति २०७८/०६/१९ गते ।
- https://ciaa.gov.np/pressrelease/3000: मिति २०८१/१२/१४ गते।

To download the file, use `curl` or equivalent tools.

> NOTE: CIAA press releases are also available in tools/caseworker-agent/data/ciaa-press-releases.csv. It might be easier to get the press release URL.

Once you find the URL, check for .doc, .docx, or .pdf files in the web page. Use this url to download the file.

### Charge sheet.

Get the charge sheet for Special court case 081-CR-0123.

It needs to be collected from Attorney General website located at https://ag.gov.np/abhiyog.

Save it to sources/raw/charge-sheet-<case-number>.pdf

The publication date is usually when CIAA publishes the press release; it's also the same date when the Special court case is registered.

Once you identify the year and month, you can use a curl like this to download the charge sheet:

curl 'https://ag.gov.np/abhiyogpatras?month_id=50&code=sgao&description=undefined'.

The month ID is determined as follows:
2078 baisakh = 1
2078 Jestha = 2
...
2079 Baisakh = 13
...

## US-003: Fetching news items from Web search

Use the web search tool to find and fetch relevant news items regarding the case from Web search. This helps build out the context and details of the allegations. Ensure you search using case details like case number, defendants' names, and the relevant court. Try searching near the court case registration date or the CIAA press release date.

If you are unable to discover any news items that's also fine. Just update the progress log and move on to the next user story. But please write a file called sources/markdown/news-search-results.md in the casework folder.

Also, for checkpoint, after every 10 or so web searches, keep updating the search results in sources/markdown/news-search-progress.md.


## US-005: Preparing the Case Draft Locally
We'll create a markdown file called case-draft in the casework folder. It will follow the template added in `instructions/case-template.md` in the casework folder.

Use the jawafdehi-caseworker skill to review this case draft. NOTE explicitly that we won't have a case in Jawafdehi.org, so we will have to make do with the local files that we have. The review should be saved in the usual location, naming it review-<CIAA-case-number>-<date-time>.md.

## US-006: Uploading the Case Draft to Jawafdehi

TODO.

For now, Update the PRD, Let's mark the workflow as a failure (set is_complete=true, and failed=true). Tell the user this isn't implemented yet.

