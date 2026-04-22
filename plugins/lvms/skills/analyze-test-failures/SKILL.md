---
name: lvms:analyze-test-failures
argument-hint: <api-token> <reportportal-url>
description: Analyze LVMS test failures from ReportPortal
user-invocable: true
allowed-tools: Bash, Read, Write, Glob, Grep, WebFetch
---

# lvms:analyze-test-failures

## Synopsis

```bash
/lvms:analyze-test-failures <api-token> <reportportal-url>
```

**Examples:**
```bash
# Prow launch
/lvms:analyze-test-failures "eyJhbGci..." https://reportportal-openshift.apps.dno.ocp-hub.prod.psi.redhat.com/ui/#prow/launches/2121

# LVMS QE launch
/lvms:analyze-test-failures "eyJhbGci..." https://reportportal-openshift-qe.apps.ocp-c1.prod.psi.redhat.com/ui/#openshift-qe_lvms/launches/all/12345

# Specific test item
/lvms:analyze-test-failures "eyJhbGci..." https://reportportal-openshift.apps.dno.ocp-hub.prod.psi.redhat.com/ui/#prow/launches/2121/813416/142352903
```

## Description

Fetches launch data from ReportPortal, extracts failed LVMS test cases, and generates a comprehensive Markdown report with failure analysis.

## Implementation

### Step 1: Parse Input Arguments

Parse the two required arguments:
1. **API Token** (first argument): JWT or Bearer token for authentication
2. **ReportPortal URL** (second argument): Full URL to the launch or test item

From the URL, extract:
- Base domain (e.g., `reportportal-openshift.apps.dno.ocp-hub.prod.psi.redhat.com`)
- Project name (e.g., `prow`, `openshift-qe_lvms`)
- Launch ID (first number after `/launches/`)
- Optional: Item ID (if URL points to specific test item)

**URL Pattern Examples:**
- `https://{domain}/ui/#{project}/launches/{launch_id}`
- `https://{domain}/ui/#{project}/launches/{launch_id}/{item_id}`
- `https://{domain}/ui/#{project}/launches/{launch_id}/{parent_id}/{item_id}`

### Step 2: Construct ReportPortal API Endpoints

```
API base: https://{domain}/api/v1/{project}
```

Endpoints:
- Launch metadata: `{base_url}/launch/{launch_id}`
- Failed test items: `{base_url}/item?filter.eq.launchId={launch_id}&filter.in.status=FAILED,INTERRUPTED&page.size=300`
- Specific item (if item ID available): `{base_url}/item/{item_id}`

### Step 3: Fetch Launch Metadata

```bash
curl -s -H "Authorization: Bearer {api_token}" \
  "{base_url}/launch/{launch_id}"
```

Extract: launch name, status, start/end time, duration, attributes (LVMS_version, OCP_version, profile).

### Step 4: Fetch LVMS Test Items

Automatically filters for LVMS-specific tests containing "[LVMS]" in their name.

```bash
curl -s -H "Authorization: Bearer {api_token}" \
  "{base_url}/item?filter.eq.launchId={launch_id}&filter.eq.type=STEP&filter.in.status=FAILED,INTERRUPTED,SKIPPED&filter.cnt.name=LVMS&page.size=500"
```

**Handle pagination**: If `page.totalPages > 1`, fetch additional pages.

Extract per test: name, status, error/failure message, test item ID, attributes, path names.

### Step 5: Construct Direct Links

For each failed test item:
```
https://{domain}/ui/#{project}/launches/{launch_id}/{item_id}
```

Use `pathNames` from API response if available for exact URL paths.

### Step 6: Normalize Metadata

1. If test-level metadata is missing, use launch-level metadata
2. If launch-level is also missing, mark as "N/A"
3. Clean up test names (remove prefixes, extract readable name)
4. Truncate error messages to 150 characters if too long

### Step 7: Generate Markdown Report

#### 7.1 Launch Overview
```markdown
# LVMS Test Failure Analysis

## Launch Overview
- **Launch ID**: <launch_id>
- **Launch Name**: <launch_name>
- **Status**: <status>
- **Start Time**: <start_time>
- **End Time**: <end_time>
- **Duration**: <duration>
- **LVMS Version**: <lvms_version>
- **OCP Version**: <ocp_version>
- **Profile**: <profile>
- **ReportPortal Link**: <reportportal_link>
```

#### 7.2 Failed Tests Table
```markdown
## Failed Tests

| Profile | LVMS Version | OCP Version | Test Name | Failure Reason | Link |
|---------|--------------|-------------|-----------|----------------|------|
```

**For Skipped Tests:**
```markdown
## Skipped LVMS Tests

| Profile | OCP Version | Test Name | Status | Link |
|---------|-------------|-----------|--------|------|
```

If ALL LVMS tests are skipped, note that LVMS is likely not configured for this profile.

#### 7.3 Summary
```markdown
## Summary

### Statistics
- **Total Failed Tests**: <total_count>
- **Affected Profiles**: <profile_list>
- **Unique Failure Types**: <unique_error_count>

### Top Failure Reasons
1. <error_pattern_1> (<count_1> occurrence(s))
2. <error_pattern_2> (<count_2> occurrence(s))

### Failure Categories
- Infrastructure Failures: <infra_count>
- Test Assertion Failures: <assertion_count>
- Setup/Teardown Failures: <setup_count>
- Unknown/Other: <other_count>

## Next Steps
<analysis_recommendations>

---
*Report generated on <timestamp>*
```

### Step 8: Save Report

1. Generate filename: `lvms-failure-report-<launch_id>-<YYYYMMDD-HHMMSS>.md`
2. Save to current directory
3. Display success message with filename and path
4. Show preview (first 30-50 lines)

## Error Handling

| Error | Action |
|-------|--------|
| Invalid Launch ID | Display: "Launch ID not found. Verify the URL." |
| API request failure | Display error details |
| No LVMS tests found | Display: "No LVMS tests found in this launch." |
| All LVMS tests skipped | Note that LVMS is not configured for the profile |
| Missing attributes | Mark as "N/A" |
| Partial data | Generate report with available data, note missing sections |

## Notes

- **Getting API Token**: Log in to ReportPortal UI -> browser DevTools -> Network tab -> find `Authorization: Bearer <token>` header -> copy token value (without "Bearer " prefix).
- **Token Expiration**: JWT tokens expire. If you get 401 errors, obtain a fresh token.
- **Rate Limiting**: Be mindful of API rate limits for large test data sets.
- **Multiple Instances**: Different instances may have different project names (`prow`, `openshift-qe_lvms`).

## Troubleshooting

| Problem | Solution |
|---------|----------|
| 401/403 errors | Token is invalid or expired. Get a fresh one. |
| 503 Service Unavailable | ReportPortal is down. Wait or contact admin. |
| Launch ID not found (404) | Verify launch ID, project name, and access. |
| No test items despite UI failures | Check for SKIPPED/INTERRUPTED status. |
| Truncated error messages | Fetch detailed logs: `{base_url}/item/{item_id}/log` |
| URL parsing fails | Ensure URL follows `https://{domain}/ui/#{project}/launches/{launch_id}` |
| Token in command history | Clear shell history or use env var for token. |

## Security Considerations

- Do not share tokens or commit them to version control
- Store tokens in environment variables or secrets managers
- Review generated reports before sharing -- they may contain sensitive data
