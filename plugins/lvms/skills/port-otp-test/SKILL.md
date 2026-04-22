---
name: lvms:port-otp-test
argument-hint: <test-package> <test-case>
description: Port a test from openshift-tests-private to the local lvm-operator repository
user-invocable: true
allowed-tools: Bash, Read, Write, Glob, Grep, WebFetch
---

# lvms:port-otp-test

## Synopsis

```bash
/lvms:port-otp-test <test-package> <test-case>
```

**Examples:**
```bash
# Port a specific LVMS test
/lvms:port-otp-test test/extended/storage/lvms.go "Author:rdeore-Critical-61586-[LVMS] [Block] Clone a pvc with Block VolumeMode"

# Port another test
/lvms:port-otp-test test/extended/storage/lvms.go "should create volume group with device paths"
```

## Description

Ports and validates existing tests from the openshift-tests-private repo into the local lvm-operator repository. Handles the complete porting process: code migration, framework conversion, build validation, and flakiness checks.

## Arguments

- **$1** (test-package): Relative path from openshift-tests-private repository root to the test file (e.g., `test/extended/storage/lvms.go`)
- **$2** (test-case): The exact name of the test case as it appears in the `It()` block

## Prerequisites

- Access to https://github.com/openshift/openshift-tests-private repository
- Understanding of the test case being ported
- Knowledge of openshift-tests-extension framework basics
- Local cluster access (optional, for validation)

## Test Framework Guidelines

### Ginkgo Framework
- Uses **Ginkgo** BDD-style with Describe/Context/It blocks
- MUST NOT use `BeforeAll`, `AfterAll` hooks
- MUST NOT use `ginkgo.Serial` -- use the `[Serial]` annotation in the test name instead

### Import Style and Aliases

All ported tests MUST use:
```go
import (
    // Standard library
    "context"
    "fmt"
    "time"

    // Ginkgo/Gomega with standard aliases
    g "github.com/onsi/ginkgo/v2"
    o "github.com/onsi/gomega"

    // Kubernetes imports
    corev1 "k8s.io/api/core/v1"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"

    e2e "k8s.io/kubernetes/test/e2e/framework"
)
```

**Critical rules:**
- ALWAYS use `g` for `github.com/onsi/ginkgo/v2`
- ALWAYS use `o` for `github.com/onsi/gomega`
- Use `g.Describe`, `g.It`, `g.By` prefixes
- Use `o.Expect`, `o.BeNil` prefixes
- DO NOT import `github.com/openshift/origin/test/extended/util`

### Cluster Client Initialization

**ALWAYS** use `NewTestClient()`:
```go
var tc = NewTestClient("test-namespace-prefix")
```

- NEVER use `kubernetes.Clientset` directly
- NEVER use `clientcmd.BuildConfigFromFlags`
- NEVER use `exutil.NewCLI()` -- use `NewTestClient()` instead
- Use `tc.AdminKubeClient()` for Kubernetes clientset
- Use `tc.Config` for rest config
- **Prefer type-safe APIs**: `tc.Get()`, `tc.List()`, `tc.Create()` over CLI commands

### Repository-Specific Guidelines (lvm-operator)

- Integration tests: `test/integration/tests/lvms.go`
- Utilities: `test/integration/tests/lvms_utils.go`
- MUST NOT use `_test.go` suffix (excluded by `go build`)
- Files are in the `tests` package imported in `test/integration/integration.go`
- Keep original test name
- MUST NOT remove `[Disruptive]` tag
- After adding a test, **MUST** rebuild:
  ```bash
  cd test/integration && make integration-build
  ```
- Verify test is listed:
  ```bash
  ./integration-test list | grep "test-case-name"
  ```

## Implementation

### 1. Locate Source Test
- Clone/fetch from https://github.com/openshift/openshift-tests-private
- Find the test package and specific test case
- Identify dependencies and imports

### 2. Analyze Test Structure
- Extract test case logic from Describe/It blocks
- Identify required imports and utilities
- Note test fixtures or data files needed

### 3. Port Test Code
- Create/update test file in `test/integration/tests/lvms.go`
- Migrate utilities to `test/integration/tests/lvms_utils.go` or other `*_utils.go` files
- Apply import conversions (see below)
- Apply client conversions (see below)
- Maintain original test name
- Follow `test/integration/MIGRATION.md`

### 4. Validate Test Structure
- Ensure no BeforeAll/AfterAll hooks
- Check for [Serial] annotations if needed
- Verify Ginkgo patterns

### 5. Build and Verify
- Run `make integration-build`
- Verify test appears in `integration-test list`
- Run the test case to validate
- Run 3-5 times to check for flakiness

## Framework Conversion Reference

### Import Conversions
```go
// OLD (openshift-tests-private):
import (
    . "github.com/onsi/ginkgo/v2"
    . "github.com/onsi/gomega"
    exutil "github.com/openshift/origin/test/extended/util"
    compat_otp "github.com/openshift/origin/test/extended/util/compat_otp"
)

// NEW (lvm-operator):
import (
    g "github.com/onsi/ginkgo/v2"
    o "github.com/onsi/gomega"
)
```

### Client Initialization Conversions
```go
// OLD:
var oc = exutil.NewCLI("test-prefix")
var oc = compat_otp.NewCLI("test-prefix")

// NEW:
var tc = NewTestClient("test-prefix")
```

### Function Parameter Conversions
```go
// OLD:
func someFunction(oc *exutil.CLI) {
    output, _ := oc.Run("get").Args("pods").Output()
}

// NEW:
func someFunction(tc *TestClient) {
    output, _ := tc.Run("get").Args("pods").Output()
}
```

### Type-Safe API (Preferred)
```go
// CLI style (works but not recommended):
output, _ := tc.Run("get").Args("lvmcluster", name, "-o", "json").Output()
state := gjson.Get(output, "status.state").String()

// Type-safe (preferred):
cluster, _ := tc.GetLVMCluster(name, namespace)
state := string(cluster.Status.State)
```

## Migration Resources

- `test/integration/MIGRATION.md` -- Complete migration guide
- `test/integration/MIGRATION_COMPARISON.md` -- Real code examples
- `test/integration/tests/testclient.go` -- TestClient implementation
- `test/integration/tests/*_utils.go` -- Ported utility functions

### Why TestClient?
- **Smaller dependencies**: No massive openshift/origin module (~850MB savings)
- **Type-safe APIs**: Direct Kubernetes API access via controller-runtime
- **Better integration**: Same client library as operator code
- **Dual interface**: CLI-style commands AND type-safe operations

## Validation Steps

```bash
# Verify test appears
./integration-test list | grep "test-case-name"

# Run test (if cluster available)
./integration-test run "test-case-name"

# Check for flakiness
for i in {1..5}; do ./integration-test run "test-case-name"; done
```

## Expected Outcome

After successful porting:
- Test exists in `test/integration/tests/lvms.go`
- All imports use `g` and `o` aliases -- no exutil or compat_otp
- Client uses `tc = NewTestClient()` pattern
- All function parameters: `tc *TestClient` (not `oc *exutil.CLI`)
- All Ginkgo/Gomega calls use `g.`/`o.` prefixes
- Test appears in `integration-test list`
- Test runs successfully (if cluster available)
- No flakiness over multiple runs
- Migration follows `test/integration/MIGRATION.md`

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Test not listed after build | Verify no `_test.go` suffix; check package import in `integration.go`; review build errors |
| Import errors | Use openshift-tests-extension imports; update module dependencies |
| Test fails after porting | Verify cluster prerequisites; check hardcoded assumptions; review timeouts |
