# Intake Sources Registry

Use this registry for every external source reviewed through `intake/`.

## Fields

- `source_id`: short stable identifier
- `title`: source title
- `type`: book/repo/article/paper/video/etc.
- `url`: canonical URL
- `version_or_commit`: tag/version/commit (if applicable)
- `license`: declared license, if known
- `retrieved_on`: UTC date (`YYYY-MM-DD`)
- `notes`: short relevance note for Cortex

## Entries

| source_id | title | type | url | version_or_commit | license | retrieved_on | notes |
|---|---|---|---|---|---|---|---|
| source/agentic_engineering_book_v0 | Building an Agentic System | repo/book | https://github.com/gerred/building-an-agentic-system | eec7f0226fb0d0019c67dc6f209a80b61720117e | CC BY 4.0 | 2026-02-18 | Reference source for agentic engineering patterns to distill into Cortex playbooks/policies. |
