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
   11. `mcp_workspace_mcp_start_google_auth` - Initiate Google OAuth authentication required before accessing Google Workspace tools.

3. **Fetch MCP Server to get the `fetch` tool.**


## Notes
1. Your manager will provide the Google OAuth Client ID/Secrets.
2. User must be authorized to the OAuth2.0 app; Please reach out to manager for this.
3. You need to set corret NGM_DATABASE_URL for the MCP server access.


## MCP Configuration Example


```json
{
  "mcpServers": {
    "workspace-mcp": {
      "command": "uvx",
      "args": [
        "workspace-mcp",
        "--single-user",
        "--read-only",
        "--tools",
        "drive",
        "docs",
        "sheets"
      ],
      "env": {
        "GOOGLE_OAUTH_CLIENT_ID": "xxx",
        "GOOGLE_OAUTH_CLIENT_SECRET": "yyy",
        "USER_GOOGLE_EMAIL": "your-email@gmail.com"
      },
      "disabled": false
    },
    "fetch": {
      "command": "uvx",
      "args": [
        "mcp-server-fetch"
      ],
      "env": {},
      "disabled": false,
      "autoApprove": []
    },
    "jawafdehi": {
      "command": "${path-to}/services/jawafdehi-mcp/.venv/bin/jawafdehi-mcp",
      "args": [],
      "env": {
        "NGM_DATABASE_URL": "postgresql://ngm-database-url"
      },
      "disabled": false,
      "autoApprove": [
        "ngm_query_judicial",
        "get_nes_tags",
        "search_nes_entities",
        "get_nes_entities"
      ],
      "disabledTools": []
    }
  }
}
```