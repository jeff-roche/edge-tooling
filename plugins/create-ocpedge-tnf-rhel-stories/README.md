# create-ocpedge-tnf-rhel-stories

Create OCPEDGE stories for TNF RHEL verification tickets, link them to the RHEL bugs, and set the required components (`Two Node Fencing`, `QE`, `RHEL-Verification`).

## Installation

Install via Claude Code's plugin system:

```text
/plugin marketplace add openshift-eng/edge-tooling
/plugin install create-ocpedge-tnf-rhel-stories
```

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) (provides `uvx`)
- `JIRA_USERNAME` environment variable set with your Red Hat email
- `JIRA_PERSONAL_TOKEN` environment variable set with a [Jira API token](https://id.atlassian.com/manage-profile/security/api-tokens)

The plugin includes an `.mcp.json` that automatically configures the `mcp-atlassian` MCP server.

## Usage

### Auto-discover untested tickets (recommended)

```
/create-ocpedge-tnf-rhel-stories
```

Automatically searches for `[TNF]` resource-agents RHEL tickets with `Preliminary Testing = Requested` and no `Test Coverage`, groups them, and proposes OCPEDGE stories.

### Dry run (preview without changes)

```
/create-ocpedge-tnf-rhel-stories --dry-run
```

### Specific tickets

```
/create-ocpedge-tnf-rhel-stories RHEL-12345 RHEL-12346 RHEL-12347
```

### JQL query

```
/create-ocpedge-tnf-rhel-stories jql:project = RHEL AND component = "resource-agents" AND status != Closed ORDER BY created DESC
```

## Features

- **Auto-discovery**: Finds untested TNF resource-agents RHEL tickets (aligned with OCPEDGE RHEL Verification board filter)
- **Clone expansion**: Walks the full clone tree so all sibling clones are linked
- **Dry-run mode**: Preview the plan without modifying Jira
- **Closed story handling**: Creates new stories for untested tickets when existing story is Closed
- **Subtask creation**: Adds "Bug fix verification" and "Automation" subtasks to each story

## Author

lucaconsalvi
