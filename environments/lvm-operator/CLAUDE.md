# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Environment Purpose

This workspace serves as a **LVM Operator development environment template**. LVMS is an OpenShift operator that provides local storage utilizing the LVM storage driver which is wrapped by TopoLVM

**Workflow:**
1. Developers/QA clone this repo as their workspace root
2. All LVMS source repositories are cloned under the `repos/` folder
3. Work with Claude from this top-level directory to get full context across all repos
4. Navigate into specific `repos/<repo-name>/` directories to implement changes

**The `repos/` folder contains all source code.** This CLAUDE.md provides a summary of each repository's relevance to LVMS, so Claude understands how to navigate and use them effectively.

### Source of Truth Priority

**IMPORTANT**: When answering questions or implementing changes related to LVMS:
1. **Always look at repos in this workspace FIRST** before using internal knowledge or web searches
2. If a component has a repo here, that repo is the **authoritative source of truth**
3. Code in `repos/` reflects the latest development state, which may differ from public documentation

### Fork Model

All repositories **except `konflux-release-data`** use a fork model for contributions:
- Push changes to your personal fork first, not directly to upstream
- Create pull requests from your fork to the upstream repository
- `konflux-release-data` utilizes a branching strategy that matches this branch naming format: `<user_alias>/<changeset_summary>`

### Repository Categories

Repositories are grouped by their primary purpose:

| Category | Repositories | Description |
|----------|--------------|-------------|
| **Testing** | `release` | Prow Based CI/CD configuration |
| **Deployment** | `konflux-release-data`, `product-definitions` | Konflux Based CI/CD, Product Security configuration for products |
| **Development** | `lvm-operator`, `topolvm` | Core LVM Operator source code |

### Typical Tasks

#### Exploration
<!-- TODO: Add guidance for codebase exploration tasks -->

#### Development
<!-- TODO: Add guidance for development workflow tasks -->

#### Troubleshooting
<!-- TODO: Add guidance for debugging and troubleshooting tasks -->

---

## Repositories

All repositories are located in the `repos/` folder.

### lvm-operator (`repos/lvm-operator/`)
**Category**: Development

**Purpose**: Core LVM Operator source code repository

**LVMS Relevance**:
- Operator Bundle source code
- Must Gather source code
- Tekton pipeline definitions
- Testing framework definitions
- Catalog definitions
- Containerfiles for release images

**When to use this repo**:
- Developing new features for LVMS
- Modifying the tekton CI/CD pipelines for LVMS
- Adding or modifying tests
- Building the operator for testing

**Key folders**:
- `.tekton/` - Contains the Konflux pipeline definitions for building and testing the different operator components
- `api/` - Contains LVM operator API definitions
- `bundle/` - Contains auto-generated manifests for the bundle
- `catalog/` - Contains catalog definitions for testing in Prow
- `cmd/` - Primary entrypoints for the operator binaries
- `config/` - Manifest definitions for the operator and bundle
- `internal/` - The primary source code of the operator
- `must-gather/` - The primary source code for the must-gather image
- `release/` - Containerfiles and related pieces for generating a release-ready bundle and catalog
- `test/` - Contains the unit tests, integration tests, and QE end to end tests for the operator

### topolvm (`repos/topolvm/`)
**Category**: Development

**Purpose**: The underlying CSI driver that LVM-Operator imports to manage the host LVM

### release (`repos/release/`)
**Category**: Testing

**Purpose**: OpenShift CI/CD configuration repository for Prow jobs and test workflows

**LVMS Relevance**: Central orchestration point for LVMS CI based testing

**How OpenShift CI works**:
- **Prow**: Kubernetes-based CI system that runs jobs
- **ci-operator**: OpenShift-specific test orchestrator
- **Step registry**: Reusable test steps, chains, and workflows
- Workflows compose steps for full test scenarios

**Key LVMS paths**:
configurations:
  - `ci-operator/config/openshift/lvm-operator/`
    - Contains the PR and periodic LVMS job definitions for building and testing the operator in Prow

### konflux-release-data (`repos/konflux-release-data/`)
**Category**: Deployment

**Purpose**: Red Hat build and release management orchestration

**LVMS Relevance**: Primary orchestration point for LVMS Konflux and tekton based building, testing, and releasing for both the staging and production environments

**Key LVMS paths**:
- Component Configurations:
  - `tenants-config/cluster/stone-prd-rh01/tenants/logical-volume-manag-tenant/lvm-operator/` - Operator Bundle component defitions, tests, release plans, and image repositories
  - `tenants-config/cluster/stone-prd-rh01/tenants/logical-volume-manag-tenant/lvm-operator-catalog` - Operator catalog component, release plan, and image registry definitions
  - `tenants-config/cluster/stone-prd-rh01/tenants/logical-volume-manag-tenant/nudge-renovate-config.yaml` - Component nudging definition for all LVM Operator and catalog components
  - `tenants-config/auto-generated/cluster/stone-prd-rh01/tenants/logical-volume-manag-tenant/` - Autogenerated configuration files (in Kubernetes CR form) that gets applied to the Konflux cluster and manages the tekton build, test and release pipelines
  - `tenants-config/build-single.sh` - The script used to autogenerate files in the `tenants-config/auto-generated/` folder
    - **Note**: this should be called with the tenant namespace as an argument in this form:
    ```bash
    $ ./tenants-config/build-single.sh logical-volume-manag-tenant
    ```

- Release Plan Admissions
  - `config/stone-prd-rh01.pg1f.p1/product/ReleasePlanAdmission/logical-volume-manag/` - Contains the Release Plan Admission definitions for both the Operator bundle and the Catalog

- Enterprise contract policies
  - `config/stone-prd-rh01.pg1f.p1/product/EnterpriseContractPolicy/fbc-logical-volume-manag-prod.yaml` - custom production environment policy for the LVM Operator file based catalog
  - `config/stone-prd-rh01.pg1f.p1/product/EnterpriseContractPolicy/fbc-logical-volume-manag-stage.yaml` - custom staging environment policy for the LVM Operator file based catalog
  - `config/common/product/EnterpriseContractPolicy/registry-standard.yaml` - Standard production policy that we should not make changes to
  - `config/common/product/EnterpriseContractPolicy/registry-standard-stage.yaml` - Standard staging policy that we should not make changes to

- Product definitions
  - `prodsec/logical-volume-manag.yaml` - Prodsec definition that relates to the `product-definitions` repository
  - `constraints/product/logical-volume-manag.yaml` - Product release constraints for LVM Operator and the catalog

### product-definitions (`repos/product-definitions`)
**Category**: Deployment

**Purpose**: Red Hat Product Security Gatekeeper

**LVMS Relevance**: Contains the LVMS product versions that are approved to be built and released via Konflux

**Key LVMS paths**:
- `data/openshift/ps_products.json` - Top level product definitions
  - `ps_products.lvms-operator` - The JSON path to the operator product definition
- `data/openshift/ps_update_streams.json` - The version and CPE information for products
  - `ps_update_streams.lvms-operator-*` - The JSON path (regex) to LVMS version definitions
- `data/openshift/ps_modules.json` - The module version definitions for openshift products
  - `ps_modules.lvms-operator-4` - The JSON  path to the LVMS v4 module versions 

---

## LVM Operator Architecture
<!-- TODO: Add key concepts for LVMS and how it is structured -->

## TopoLVM CSI Driver Architecture
<!-- TODO: Add key concepts for TopoLVM and how it is structured -->

## Prow Architecture
<!-- TODO: Add key concepts for Prow and how LVMS utilizes Prow -->

## Konflux Architecture
<!-- TODO: Add key concepts for Konflux and how LVMS utilizes Konflux -->

### LVMS Konflux Build Chain Overview
```
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │                           BUILD CHAIN DIAGRAM                                │
  ├──────────────────────────────────────────────────────────────────────────────┤
  │                                                                              │
  │  ┌──────────────┐   ┌───────────────────┐   ┌─────────────┐                  │
  │  │   topolvm    │   │   lvm-operator    │   │ must-gather │                  │
  │  │  (topolvm    │   │  (lvm-operator    │   │(lvm-operator│                  │
  │  │    repo)     │   │     repo)         │   │    repo)    │                  │
  │  └──────┬───────┘   └────────┬──────────┘   └──────┬──────┘                  │
  │         │                    │                     │                         │
  │         │    NUDGE           │    NUDGE            │   NUDGE                 │
  │         └────────────────────┼─────────────────────┘                         │
  │                              ▼                                               │
  │                   ┌────────────────────┐                                     │
  │                   │ lvm-operator-bundle│  ◄── Single Arch Build!             │
  │                   │  (lvm-operator     │                                     │
  │                   │      repo)         │                                     │
  │                   └─────────┬──────────┘                                     │
  │                             │                                                │
  │                             │    NUDGE                                       │
  │                             ▼                                                │
  │                   ┌────────────────────┐                                     │
  │                   │lvm-operator-catalog│                                     │
  │                   │  (lvm-operator     │                                     │
  │                   │      repo)         │                                     │
  │                   └────────────────────┘                                     │
  └──────────────────────────────────────────────────────────────────────────────┘  
```
