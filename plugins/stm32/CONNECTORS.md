# Connectors

## How tool references work

Plugin files use `~~category` as a placeholder for whatever tool you connect in that category. Skills describe workflows in terms of categories, not specific products, so they work with any tool you use. Every skill works without any connector; connectors only add convenience.

## Connectors for this plugin

| Category | Placeholder | Options |
|---|---|---|
| Source control | `~~source control` | GitHub, GitLab, Bitbucket |
| Project tracker | `~~project tracker` | Linear, Asana, Jira |
| Knowledge base | `~~knowledge base` | Notion, Confluence, Google Drive (datasheets, errata, team notes) |

## Not connectors

Debug probes, flashing tools, compilers, and GDB are used through the command line in your own environment. Skills name the standard Arm GNU Toolchain commands (`arm-none-eabi-*`) and describe what to look for, and they work the same with any probe or IDE.
