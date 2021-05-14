.PHONY: molecule

# Also needs to be updated in galaxy.yml
VERSION = 1.1.2

TEST_ARGS ?= ""
PYTHON_VERSION ?= `python -c 'import platform; print("{0}.{1}".format(platform.python_version_tuple()[0], platform.python_version_tuple()[1]))'`

clean:
	rm -f community-okd-$(VERSION).tar.gz
	rm -f redhat-openshift-$(VERSION).tar.gz
	rm -rf ansible_collections

build: clean
	ansible-galaxy collection build

install: build
	ansible-galaxy collection install -p ansible_collections community-okd-$(VERSION).tar.gz

sanity: install
	cd ansible_collections/community/okd && ansible-test sanity --docker -v --color --python $(PYTHON_VERSION) $(?TEST_ARGS)

molecule:
	molecule test

test-integration: upstream-test-integration downstream-test-integration

test-sanity: upstream-test-sanity downstream-test-sanity

test-integration-incluster:
	./ci/incluster_integration.sh

upstream-test-sanity: sanity

upstream-test-integration: molecule

downstream-test-sanity:
	./ci/downstream.sh -s

downstream-test-integration:
	./ci/downstream.sh -i

downstream-build:
	./ci/downstream.sh -b
