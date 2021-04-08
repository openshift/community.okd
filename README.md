# OKD Collection for Ansible

<!--- STARTREMOVE --->
[![CI](https://github.com/ansible-collections/community.okd/workflows/CI/badge.svg?event=push)](https://github.com/ansible-collections/community.okd/actions) [![Codecov](https://img.shields.io/codecov/c/github/ansible-collections/community.okd)](https://codecov.io/gh/ansible-collections/community.okd)

This repo hosts the `community.okd` Ansible Collection.

The collection includes a variety of Ansible content to help automate the management of applications in OKD clusters, as well as the provisioning and maintenance of clusters themselves.

## Included content

Click on the name of a plugin or module to view that content's documentation:

  - **Connection Plugins**:
    - [oc](https://docs.ansible.com/ansible/2.10/collections/community/general/oc_connection.html)
  - **Inventory Plugins**:
    - [openshift](https://docs.ansible.com/ansible/2.10/collections/community/kubernetes/openshift_inventory.html)
  - **Modules**:
    - [k8s](https://docs.ansible.com/ansible/2.10/collections/community/kubernetes/k8s_inventory.html)
    - [openshift_auth](https://github.com/ansible-collections/community.okd/blob/main/plugins/modules/openshift_auth.py)
    - [openshift_process](https://github.com/ansible-collections/community.okd/blob/main/plugins/modules/openshift_process.py)
    - [openshift_route](https://github.com/ansible-collections/community.okd/blob/main/plugins/modules/openshift_route.py)

> **Note**: Some of these documentation links currently link to older module versions. For the latest module documentation, please use `ansible-doc` in the CLI.

<!--- ENDREMOVE --->

## Installation and Usage

### Installing the Collection from Ansible Galaxy

Before using the OKD collection, you need to install it with the Ansible Galaxy CLI:

    ansible-galaxy collection install community.okd

You can also include it in a `requirements.yml` file and install it via `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: community.okd
    version: 1.1.2
```

### Installing the OpenShift Python Library

Content in this collection requires the [OpenShift Python client](https://pypi.org/project/openshift/) to interact with Kubernetes' APIs. You can install it with:

    pip3 install openshift

### Using modules from the OKD Collection in your playbooks

It's preferable to use content in this collection using their Fully Qualified Collection Namespace (FQCN), for example `community.okd.openshift`:

```yaml
---
plugin: community.okd.openshift
connections:
  - namespaces:
    - testing
```

For documentation on how to use individual plugins included in this collection, please see the links in the 'Included content' section earlier in this README.

<!--- STARTREMOVE --->
## Testing and Development

If you want to develop new content for this collection or improve what's already here, the easiest way to work on the collection is to clone it into one of the configured [`COLLECTIONS_PATHS`](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#collections-paths), and work on it there.

See [Contributing to community.okd](CONTRIBUTING.md).

The `tests` directory contains configuration for running sanity tests using [`ansible-test`](https://docs.ansible.com/ansible/latest/dev_guide/testing_integration.html).

You can run the `ansible-test` sanity tests with the command:

    make test-sanity

The `molecule` directory contains configuration for running integration tests using [`molecule`](https://molecule.readthedocs.io/).

You can run the `molecule` integration tests with the command:

    make test-integration

These commands will create a directory called `ansible_collections` which should not be committed or added to the `.gitignore` (Tracking issue: https://github.com/ansible/ansible/issues/68499)


### Prow

This repository uses the OpenShift [Prow](https://github.com/kubernetes/test-infra/blob/master/prow/README.md) instance for testing against live OpenShift clusters.
The configuration for the CI jobs that this repository runs can be found in the [`openshift/release repository`](https://github.com/openshift/release/blob/master/ci-operator/config/ansible-collections/community.okd/ansible-collections-community.okd-main.yaml).

The [Prow CI integration test job](https://github.com/openshift/release/blob/master/ci-operator/config/ansible-collections/community.okd/ansible-collections-community.okd-main.yaml#L35-L38)
runs the command:

    make test-integration-incluster

which will create a job that runs the normal `make integration` target. In order to mimic the Prow CI job, you must
first build the test image using the Dockerfile in [`ci/Dockerfile`](ci/Dockerfile). Then, push the image
somewhere that it will be accessible to the cluster, and run

    IMAGE_FORMAT=<your image> make test-integration-incluser

where the `IMAGE_FORMAT` environment variable is the full reference to your container (ie, `IMAGE_FORMAT=quay.io/example/molecule-test-runner`)

## Publishing New Versions

Releases are automatically built and pushed to Ansible Galaxy for any new tag. Before tagging a release, make sure to do the following:

  1. Update the version in the following places:
    a. The `version` in `galaxy.yml`
    b. This README's `requirements.yml` example
    c. The `DOWNSTREAM_VERSION` in `ci/downstream.sh`
    d. The `VERSION` in `Makefile`
  1. Update the CHANGELOG:
    1. Make sure you have [`antsibull-changelog`](https://pypi.org/project/antsibull-changelog/) installed.
    1. Make sure there are fragments for all known changes in `changelogs/fragments`.
    1. Run `antsibull-changelog release`.
  1. Commit the changes and create a PR with the changes. Wait for tests to pass, then merge it once they have.
  1. Tag the version in Git and push to GitHub.

After the version is published, verify it exists on the [OKD Collection Galaxy page](https://galaxy.ansible.com/community/okd).
<!--- ENDREMOVE --->

## More Information

For more information about Ansible's Kubernetes and OpenShift integrations, join the `#ansible-kubernetes` channel on Freenode IRC, and browse the resources in the [Kubernetes Working Group](https://github.com/ansible/community/wiki/Kubernetes) Community wiki page.

## License

GNU General Public License v3.0 or later

See LICENCE to see the full text.
