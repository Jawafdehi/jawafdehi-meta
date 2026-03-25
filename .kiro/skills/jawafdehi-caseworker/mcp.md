# MCP Tools Required for Jawafdehi Caseworker

This document outlines the MCP tools needed to effectively assist caseworkers in documenting CIAA corruption cases for Jawafdehi.org.

## Tools Required

1. **Jawafdehi MCP Server**
   1. `mcp_jawafdehi_ngm_query_judicial` - Query Nepal's court database (1.5M+ cases, 4.5M+ hearings) with SQL to retrieve case details, hearings, and entities.
   2. `mcp_jawafdehi_search_jawafdehi_cases` - Search published Jawafdehi cases by keywords or tags to review similar cases for reference.
   3. `mcp_jawafdehi_get_jawafdehi_case` - Retrieve detailed information about specific published cases including allegations, evidence, and timeline.
   4. `mcp_jawafdehi_search_nes_entities` - Search Nepal Entity Service for persons and organizations to verify entity names and get NES IDs.
   5. `mcp_jawafdehi_get_nes_entities` - Retrieve complete entity profiles by ID to access detailed information about individuals and organizations.
   6. `mcp_jawafdehi_get_nes_tags` - Fetch all available entity tags in the NES database to understand entity categorization.
   7. `mcp_jawafdehi_convert_date` - Convert dates between AD (Gregorian) and BS (Bikram Sambat) calendars for accurate date handling.
   8. `mcp_jawafdehi_convert_to_markdown` - Convert documents to Markdown. Supports:
      - Nepal government PDFs: Use `doc_type="ciaa-press-release"` for best Nepali text handling
      - Office documents: DOCX, PPTX, XLSX (omit `doc_type`)
      - General PDFs: Omit `doc_type` (⚠️ Nepali text may not be accurate)
      - Web pages: Use `uri` parameter with http:// or https:// URLs
      - Parameters: `file_path` or `uri`, `doc_type` (optional), `output_path` (optional)

2. **Google Workspace MCP Server**
   1. `mcp_workspace_mcp_search_drive_files` - Search for files in Google Drive by name or content to locate case folders and documents.
   2. `mcp_workspace_mcp_list_drive_items` - List files and folders in specific Drive locations to browse case folder contents.
   3. `mcp_workspace_mcp_get_drive_file_permissions` - Check file sharing status and permissions to verify document accessibility.
   4. `mcp_workspace_mcp_get_drive_shareable_link` - Get shareable links for files and folders to share case materials with team members.
   5. `mcp_workspace_mcp_get_doc_as_markdown` - Read Google Docs content as markdown to access CIAA press releases with preserved formatting.
   6. `mcp_workspace_mcp_get_doc_content` - Read Google Docs or Office files as plain text to extract content from various document formats.
   7. `mcp_workspace_mcp_get_drive_file_content` - Read various file types from Drive including native Google formats, Office files, and PDFs.
   8. `mcp_workspace_mcp_get_drive_file_download_url` - Download files to local workspace or get temporary download URLs with format export options.
   9. `mcp_workspace_mcp_read_sheet_values` - Read data from Google Sheets to access case timelines and tracking spreadsheets.
  10. `mcp_workspace_mcp_list_spreadsheet_comments` - List comments from spreadsheets to review collaborative feedback on case data.

3. **Fetch MCP Server**
   1. `mcp_fetch_fetch` - Fetch URL content and convert to markdown for accessing web-based resources.


## Notes
1. Workspace MCP is configured as a hosted HTTP endpoint (`https://google-auth-internal.jawafdehi.org/mcp/`), so local Google OAuth client env vars are no longer required in devcontainers.
2. You need to set correct `NGM_DATABASE_URL` for Jawafdehi MCP server access.


## MCP Configuration Example

See .vscode/mcp.json.
