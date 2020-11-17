============================
OKD Collection Release Notes
============================

.. contents:: Topics


v1.0.1
======

Bugfixes
--------

- Generate downstream redhat.openshift documentation (https://github.com/ansible-collections/community.okd/pull/59).

v1.0.0
======

Minor Changes
-------------

- Released version 1 to Automation Hub as redhat.openshift (https://github.com/ansible-collections/community.okd/issues/51).

v0.3.0
======

Major Changes
-------------

- Add openshift_process module for template rendering and optional application of rendered resources (https://github.com/ansible-collections/community.okd/pull/44).
- Add openshift_route module for creating routes from services (https://github.com/ansible-collections/community.okd/pull/40).

New Modules
-----------

- openshift_process - Process an OpenShift template.openshift.io/v1 Template
- openshift_route - Expose a Service as an OpenShift Route.

v0.2.0
======

Major Changes
-------------

- openshift_auth - new module (migrated from k8s_auth in community.kubernetes) (https://github.com/ansible-collections/community.okd/pull/33).

Minor Changes
-------------

- Add a contribution guide (https://github.com/ansible-collections/community.okd/pull/37).
- Use the API Group APIVersion for the `Route` object (https://github.com/ansible-collections/community.okd/pull/27).

New Modules
-----------

- openshift_auth - Authenticate to OpenShift clusters which require an explicit login step

v0.1.0
======

Major Changes
-------------

- Add custom k8s module, integrate better Molecule tests (https://github.com/ansible-collections/community.okd/pull/7).
- Add downstream build scripts to build redhat.openshift (https://github.com/ansible-collections/community.okd/pull/20).
- Add openshift connection plugin, update inventory plugin to use it (https://github.com/ansible-collections/community.okd/pull/18).
- Initial content migration from community.kubernetes (https://github.com/ansible-collections/community.okd/pull/3).

Minor Changes
-------------

- Add incluster Makefile target for CI (https://github.com/ansible-collections/community.okd/pull/13).
- Add tests for inventory plugin (https://github.com/ansible-collections/community.okd/pull/16).
- CI Documentation for working with Prow (https://github.com/ansible-collections/community.okd/pull/15).
- Docker container can run as an arbitrary user (https://github.com/ansible-collections/community.okd/pull/12).
- Dockerfile now is properly set up to run tests in a rootless container (https://github.com/ansible-collections/community.okd/pull/11).
- Integrate stale bot for issue queue maintenance (https://github.com/ansible-collections/community.okd/pull/14).
