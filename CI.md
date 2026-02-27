# Continuous Integration (CI)

## Overview

The `community.okd` collection uses a dual-tier testing approach:
- **GitHub Actions** for upstream testing (sanity, unit tests, linters, changelog)
- **OpenShift Prow** for integration tests against live OpenShift/K8s clusters

The collection extends `kubernetes.core` and therefore inherits many testing patterns and requirements from that collection.

## GitHub Actions - Upstream Testing

GitHub Actions are used to run CI for the community.okd collection. The workflows can be found [here](https://github.com/openshift/community.okd/tree/main/.github/workflows).

The collection uses reusable workflows from [ansible-network/github_actions](https://github.com/ansible-network/github_actions) for standardized testing, similar to other Ansible network collections.

### PR Testing Workflows

The following tests run on every pull request to `main` and `stable-*` branches:

| Job | Description | OS | Python Versions | Test Command |
| --- | ----------- | -- | --------------- | ------------ |
| Changelog | Validates changelog fragments (can be skipped with `skip-changelog` label) | ubuntu-latest | 3.12 | Custom validation script |
| Linters (tox) | Runs `tox -e linters` (black, flake8, ansible-lint) | ubuntu-latest | 3.10 | `tox -e linters -vv` |
| Linters (ansible-lint) | Runs ansible-lint as separate validation | ubuntu-latest | Latest | `ansible-lint` v25.1.2 |
| Sanity | Runs ansible sanity checks across matrix | ubuntu-latest | See table below | `ansible-test sanity --requirements --color` |
| Unit tests | Executes unit tests across matrix | ubuntu-latest | See table below | `pytest tests/unit --showlocals --ansible-host-pattern localhost` |

### Python Version Compatibility by ansible-core Version

These are determined by the reusable workflows from [ansible-network/github_actions](https://github.com/ansible-network/github_actions) and the collection's minimum requirements.

For the official Ansible core support matrix, see the [Ansible documentation](https://docs.ansible.com/ansible/latest/reference_appendices/release_and_maintenance.html#ansible-core-support-matrix).

The collection requires:
- **ansible-core**: >=2.15.0
- **Python**: >=3.9
- **kubernetes.core**: >=6.0.0

#### Compatibility Matrix

The reusable workflows test the following combinations (after exclusions):

| ansible-core Version | Sanity Tests | Unit Tests |
| -------------------- | ------------ | ---------- |
| devel (2.21+) | 3.12, 3.13, 3.14 | 3.12, 3.13 |
| stable-2.20 | 3.12, 3.13, 3.14 | 3.12, 3.13, 3.14 |
| stable-2.19 | 3.11, 3.12, 3.13 | 3.11, 3.12, 3.13 |
| stable-2.18 | 3.11, 3.12, 3.13 | 3.11, 3.12, 3.13 |
| stable-2.17 | 3.10, 3.11, 3.12 | 3.10, 3.11, 3.12 |
| stable-2.16 | 3.10, 3.11 | 3.10, 3.11 |

**Matrix exclusions** (from reusable workflows):
- devel: excludes Python 3.10, 3.11
- stable-2.20: excludes Python 3.10, 3.11
- stable-2.19: excludes Python 3.10, 3.14
- stable-2.18: excludes Python 3.10, 3.14
- stable-2.17: excludes Python 3.13, 3.14
- stable-2.16: excludes Python 3.12, 3.13, 3.14

**Notes**:
- ansible-core 2.15 reached EOL in November 2024 (not tested in upstream workflows)
- ansible-core 2.16 reached EOL in May 2025
- ansible-core 2.17 reached EOL in November 2025
- **devel** version tests continue on error (unstable)
- Control node and target node Python support differs; see [Ansible roadmap](https://docs.ansible.com/ansible/devel/roadmap/ROADMAP_2_20.html)

## OpenShift Prow - Integration Testing

Integration tests for community.okd are executed via OpenShift Prow, OpenShift's CI/CD system for testing against live clusters. This provides testing on actual OpenShift and Kubernetes environments.

### Prow Configuration

The Prow configuration for this collection is maintained in the [openshift/release](https://github.com/openshift/release) repository, specifically in the file `openshift-community.okd-main.yaml`.

### Integration Test Details

Integration tests have specific characteristics:

- **Framework**: Molecule test framework
- **Test location**: `molecule/default/` directory
- **Cluster requirement**: Live OpenShift or Kubernetes cluster (>=1.24)
- **Test sequence**: dependency → syntax → prepare → converge → idempotence → verify
- **Coverage requirements**: Tests must cover check mode, creation, idempotency, modification, and deletion

#### Molecule Test Configuration

From `molecule/default/molecule.yml`:
- **Driver**: default (assumes existing cluster)
- **Provisioner**: Ansible with verbose logging (`vvv`)
- **Namespace**: `molecule-tests` (defined in playbook_namespace)
- **Collections path**: Uses `OVERRIDE_COLLECTION_PATH` or project directory
- **Virtual environment**: Creates ephemeral virtualenv for test isolation

#### Molecule Test Targets

Integration tests in `molecule/default/tasks/` include:
- `openshift_auth.yml` - Authentication module tests
- `openshift_route.yml` - Route resource management
- `openshift_process.yml` - Template processing
- `openshift_builds.yml` - Build configuration and management
- `openshift_import_images.yml` - Image import operations
- `openshift_prune_images.yml` - Image pruning
- `openshift_adm_prune_auth_roles.yml` - Role pruning
- `openshift_adm_prune_auth_clusterroles.yml` - ClusterRole pruning
- `openshift_adm_prune_deployments.yml` - Deployment pruning

And role-based tests in `molecule/default/roles/`:
- `openshift_adm_groups` - LDAP group synchronization (tests rfc2307, activeDirectory, augmentedActiveDirectory)

### Additional Dependencies

The collection depends on the following for integration testing:

- **Kubernetes cluster**: OpenShift or Kubernetes >=1.24
- **Python packages**: kubernetes>=12.0.0, requests-oauthlib
- **Collections**: kubernetes.core (>=6.0.0) - installed from git main branch
- **Test dependencies**: coverage==4.5.4, pytest, pytest-xdist, pytest-forked, pytest-ansible

### Running Integration Tests Locally

```bash
# Requires a running OpenShift/K8s cluster with proper credentials
make molecule           # Run full molecule test suite

# Or use molecule directly
molecule test           # Full test sequence
molecule converge       # Run converge phase only
molecule verify         # Run verify phase only
```

**Prerequisites**:
- Active kubeconfig with cluster access
- Cluster-admin or sufficient permissions for testing
- Namespace creation permissions

### In-Cluster Testing

For CI environments, integration tests can be run inside the cluster using:

```bash
make test-integration-incluster
```

This executes the `ci/incluster_integration.sh` script, which:
1. Creates a Kubernetes Job named `molecule-integration-test`
2. Runs tests inside a container with the `molecule-test-runner` image
3. Grants cluster-admin role to the default service account
4. Uses configurable IMAGE_FORMAT and PULL_POLICY environment variables

## Downstream Testing

This collection has a downstream variant (redhat-openshift). The `ci/downstream.sh` script handles building and testing the downstream version by removing code fragments between `STARTREMOVE/ENDREMOVE` markers.

### Downstream Test Commands

```bash
make downstream-test-sanity       # Run sanity tests on downstream build
make downstream-test-units        # Run unit tests on downstream build
make downstream-test-integration  # Run integration tests on downstream build
make downstream-build             # Build downstream collection
```

### Combined Testing

To run both upstream and downstream tests:

```bash
make test-sanity        # Upstream + downstream sanity
make test-units         # Upstream + downstream unit tests
make test-integration   # Upstream + downstream integration tests
```

## Local Development Testing

### Linting

The collection uses tox for linting:

```bash
tox -e linters      # Run all linters (black, flake8, ansible-lint)
tox -e black        # Format code with black
tox -e ansible-lint # Run ansible-lint only
```

Linter configuration:
- **black**: >=25.0, <26.0
- **ansible-lint**: >=25.1.2 (also runs as separate GitHub Action job)
- **flake8**: See `tox.ini` for ignore rules (E123, E125, E203, E402, E501, E741, F401, F811, F841, W503)

### Sanity Tests

```bash
make sanity                      # Run ansible-test sanity with default Python
PYTHON_VERSION=3.11 make sanity  # Test with specific Python version

# With additional arguments
SANITY_TEST_ARGS="--docker --color" make sanity
```

**Default arguments**: `--docker --color`

### Unit Tests

```bash
make units                       # Run ansible-test units with default Python
PYTHON_VERSION=3.11 make units   # Test with specific Python version

# With additional arguments
UNITS_TEST_ARGS="--docker --color" make units
```

**Default arguments**: `--docker --color`

### Build and Install

```bash
make build    # Build collection tarball
make install  # Build and install to ansible_collections/
make clean    # Remove build artifacts
```

## Test Requirements

### Minimum Versions

- **Ansible**: >=2.15.0
- **Python**: >=3.9
- **Kubernetes**: >=1.24 (for integration tests)
- **kubernetes.core**: >=6.0.0

### Python Dependencies

From `requirements.txt`:
- kubernetes>=12.0.0
- requests-oauthlib

From `test-requirements.txt`:
- coverage==4.5.4
- pytest
- pytest-xdist
- pytest-forked
- pytest-ansible

### Collection Dependencies

The collection requires `kubernetes.core` to be installed before running tests. Sanity tests automatically install it via:

```yaml
# tests/sanity/requirements.yml
collections:
  - name: https://github.com/ansible-collections/kubernetes.core.git
    type: git
    version: main
```

This is passed to the sanity workflow via the `collection_pre_install` parameter.

### System Dependencies

For Python 3.12+, the following system packages are required (automatically installed in CI):
- build-essential
- libssl-dev
- libssh-dev

These are needed for building ansible-pylibssh from source.

## Concurrency Control

All workflows use concurrency groups to prevent duplicate runs:
- **Group**: `${{ github.workflow }}-${{ github.ref }}`
- **Cancel in progress**: `true`

This ensures that when new commits are pushed to a PR, old workflow runs are cancelled.

## Contributing Tests

When contributing new modules or features, ensure tests cover:

1. **Check mode** - Module runs successfully with `--check`
2. **Creation** - Resource is created successfully
3. **Idempotency** - Re-running the same task doesn't change anything
4. **Modification** - Changes to existing resources work correctly
5. **Deletion** - Resources are removed successfully

See [CONTRIBUTING.md](CONTRIBUTING.md) for the complete test criteria checklist.

## Troubleshooting CI Failures

### Changelog Failures

If the changelog check fails:
- Add a changelog fragment to `changelogs/fragments/`
- OR add the `skip-changelog` label to the PR (for non-user-facing changes)

### Linter Failures

Run linters locally before pushing:
```bash
tox -e linters
```

Common issues:
- **black**: Code formatting (run `tox -e black` to auto-format)
- **flake8**: Code style violations (see `tox.ini` for ignored rules)
- **ansible-lint**: Ansible best practices violations

### Sanity Test Failures

Run sanity tests locally:
```bash
make sanity
```

Common issues:
- Import errors: Missing dependencies in `meta/runtime.yml`
- Documentation errors: Invalid DOCUMENTATION strings in modules
- Python compatibility: Code not compatible with tested Python versions

### Unit Test Failures

Run unit tests locally:
```bash
make units
```

Ensure:
- Tests pass locally before pushing
- Dependencies are properly mocked
- Tests cover both success and failure cases
