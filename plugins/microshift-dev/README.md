# MicroShift Dev Tools

A collection of development tools for MicroShift workflows.

## Skills

### golang-cve-analyzer

Analyzes MicroShift Jira CVE tickets against the Go toolchain CVEs fixed in the latest Brew nightly builds.

Given a Jira ticket ID, the skill:

1. Validates the ticket is a CVE bug with MicroShift component (via Jira MCP)
2. Extracts the target OCP minor version from the ticket
3. Finds the latest MicroShift nightly Brew build for that version
4. Discovers which Go toolchain was used to build it
5. Checks if the ticket's CVE is already fixed in that Go version's changelog

```bash
/microshift-dev:golang-cve-analyzer OCPBUGS-12345
/microshift-dev:golang-cve-analyzer OCPBUGS-12345 --verbose
```

### add-enhancement

Creates a new MicroShift Enhancement Proposal (EP) based on the official template from the openshift/enhancements repository. Generates a comprehensive enhancement document with all required sections, metadata, and guidance.

```bash
/microshift-dev:add-enhancement [area] <name> <description> <jira>
```

Must be run from inside the openshift/enhancements repository or a fork.

### analyze-start-time

Analyzes MicroShift journal logs to extract service startup timing statistics. Parses `MICROSHIFT READY` and `SERVICE READY` log patterns across multiple restarts and produces a sorted performance table.

```bash
/microshift-dev:analyze-start-time <journal-logs-file>
```

### analyze-sos-report

Investigates MicroShift runtime problems from SOS reports. Analyzes journal logs, pod status, container logs, etcd health, OVN networking, and configuration. Optionally cross-references with Robot Framework test logs.

```bash
/microshift-dev:analyze-sos-report <sos-report-path> [log.html-url]
```

### generate-tests

Generates comprehensive Robot Framework test coverage for MicroShift features based on Jira OCPSTRAT tickets. Analyzes existing test coverage, creates the top 10 missing test cases, and optionally creates a git branch with implemented tests.

```bash
/microshift-dev:generate-tests OCPSTRAT-1234
```

A customizable template (`TEMPLATE.md`) is included alongside this skill for adapting the workflow to other projects or testing frameworks.

## Prerequisites

| Requirement | Source |
|-------------|--------|
| VPN | Brew/Koji API access requires Red Hat VPN |
| `mcp-atlassian` plugin | Install via `/plugin marketplace add openshift-eng/edge-tooling` |
| `JIRA_USERNAME` | Your Atlassian email |
| `JIRA_API_TOKEN` | [Atlassian API tokens](https://id.atlassian.com/manage-profile/security/api-tokens) |
| Python `requests` | `pip install requests` |

## Dependencies

This plugin depends on:

- **mcp-atlassian** — for Jira ticket queries
