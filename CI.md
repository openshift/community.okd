# Continuous Integration (CI)

This collection uses two CI systems: **Zuul** for PR validation checks and **Prow** for integration testing.

## Zuul - PR Validation

Zuul runs automated tests on every pull request. The Zuul configuration for this collection is defined in the [ansible/ansible-zuul-jobs](https://github.com/ansible/ansible-zuul-jobs/blob/main/zuul.d/project-templates.yaml) repository under the `ansible-collections-community-okd` template.

### Jobs Run by Zuul

The following jobs run in the `third-party-check` pipeline on every PR:

| Job | Description |
| --- | ----------- |
| `build-ansible-collection` | Builds the collection tarball |
| `ansible-galaxy-importer` | Validates collection structure for Galaxy (non-voting) |
| `ansible-tox-linters` | Runs `black`, `flake8`, and `ansible-lint` via `tox -e linters` (see [tox.ini](tox.ini)) |
| `ansible-test-units-community-okd-python39` | Executes unit tests with Python 3.9 |

**Upstream Sanity Tests:**
- `ansible-test-sanity-docker-devel`
- `ansible-test-sanity-docker-milestone`
- `ansible-test-sanity-docker-stable-2.16`
- `ansible-test-sanity-docker-stable-2.17`
- `ansible-test-sanity-docker-stable-2.18`

**Downstream Sanity Tests** (test the `redhat.openshift` variant):
- `ansible-test-sanity-okd-downstream-devel`
- `ansible-test-sanity-okd-downstream-milestone`
- `ansible-test-sanity-okd-downstream-stable-2.16`
- `ansible-test-sanity-okd-downstream-stable-2.17`
- `ansible-test-sanity-okd-downstream-stable-2.18`

## OpenShift Prow - Integration Testing

Integration tests for community.okd are executed via [OpenShift Prow](https://github.com/kubernetes/test-infra/blob/master/prow/README.md), OpenShift's CI/CD system for testing against live clusters.

### Prow Configuration

The Prow configuration for this collection is maintained in the [openshift/release](https://github.com/openshift/release) repository at `ci-operator/config/openshift/community.okd/openshift-community.okd-main.yaml`.

### Integration Test Workflow

The integration test workflow follows these steps:

1. **Prow builds the test runner image** defined in [ci/Dockerfile](ci/Dockerfile)
   - Based on `registry.access.redhat.com/ubi9/ubi`
   - Includes Python 3.12, ansible-core, molecule, kubernetes client, and OKD CLI tools

2. **Prow executes `make test-integration-incluster`**
   - This runs [ci/incluster_integration.sh](ci/incluster_integration.sh)

3. **The script spawns a Kubernetes Job** that runs `make test-integration` using the previously built image
   - Job runs with cluster-admin permissions
   - 30-minute timeout
   - Backoff limit of 2 retries

4. **`make test-integration` runs both upstream and downstream tests:**
   - **Upstream tests** (`upstream-test-integration`): Runs molecule tests for `community.okd` collection
   - **Downstream tests** (`downstream-test-integration`): Runs `ci/downstream.sh -i` to convert the collection to `redhat.openshift` and test the downstream variant

### Test Framework

Integration tests use the Molecule framework and require a live OpenShift or Kubernetes cluster (>=1.24). Tests are located in the `molecule/default/` directory and cover check mode, creation, idempotency, modification, and deletion scenarios.
