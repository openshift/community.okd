# Continuous Integration (CI)

## OpenShift Upstream Testing

GitHub Actions are used to run the CI for the community.okd collection. The workflows used for the CI can be found in the [.github/workflows](.github/workflows) directory.

### PR Testing Workflows

The following tests run on every pull request:

| Job | Description | Python Versions | ansible-core Versions |
| --- | ----------- | --------------- | --------------------- |
| [Changelog](.github/workflows/changelog.yaml) | Checks for the presence of changelog fragments | 3.12 | devel |
| [Linters](.github/workflows/linters.yaml) | Runs `black`, `flake8`, and `ansible-lint` on plugins and tests | 3.10 | devel |
| [Sanity](.github/workflows/sanity-tests.yaml) | Runs ansible sanity checks | See compatibility table below | devel, stable-2.16, stable-2.17, stable-2.18, stable-2.19, stable-2.20 |
| [Unit tests](.github/workflows/unit-tests.yaml) | Executes unit test cases | See compatibility table below | devel, stable-2.16, stable-2.17, stable-2.18, stable-2.19, stable-2.20 |
| [Integration](.github/workflows/integration-tests.yaml) | Executes integration test suites using OpenShift Prow (see below) | N/A | N/A |

**Note:** Integration tests are executed via OpenShift Prow against live OpenShift/Kubernetes clusters. See the [Prow section](#openshift-prow---integration-testing) below.

### Python Version Compatibility by ansible-core Version

These are outlined in the collection's [tox.ini](tox.ini) file (`envlist`) and GitHub Actions workflow exclusions.

| ansible-core Version | Sanity Tests | Unit Tests |
| -------------------- | ------------ | ---------- |
| devel | 3.12, 3.13, 3.14 | 3.12, 3.13 |
| stable-2.20 | 3.12, 3.13, 3.14 | 3.12, 3.13, 3.14 |
| stable-2.19 | 3.11, 3.12, 3.13 | 3.11, 3.12, 3.13 |
| stable-2.18 | 3.11, 3.12, 3.13 | 3.11, 3.12, 3.13 |
| stable-2.17 | 3.10, 3.11, 3.12 | 3.10, 3.11, 3.12 |
| stable-2.16 | 3.10, 3.11 | 3.10, 3.11 |

## OpenShift Prow - Integration Testing

Integration tests for community.okd are executed via [OpenShift Prow](https://github.com/kubernetes/test-infra/blob/master/prow/README.md), OpenShift's CI/CD system for testing against live clusters.

The Prow configuration for this collection is maintained in the [openshift/release](https://github.com/openshift/release) repository in the file `openshift-community.okd-main.yaml`.

Integration tests use the Molecule framework and require a live OpenShift or Kubernetes cluster (>=1.24). Tests are located in the `molecule/default/` directory and cover check mode, creation, idempotency, modification, and deletion scenarios.
