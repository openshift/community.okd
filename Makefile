.PHONY: molecule

# Also needs to be updated in galaxy.yml
VERSION = 3.0.0

SANITY_TEST_ARGS ?= --docker --color
UNITS_TEST_ARGS ?= --docker --color
PYTHON_VERSION ?= `python3 -c 'import platform; print("{0}.{1}".format(platform.python_version_tuple()[0], platform.python_version_tuple()[1]))'`
# this expression compute the install path once for all the execution
# See: https://stackoverflow.com/questions/44114466/how-to-declare-a-deferred-variable-that-is-computed-only-once-for-all
INSTALL_PATH ?= $(eval INSTALL_PATH := $(shell mktemp -d -p ~/))$(INSTALL_PATH)

clean:
	rm -f community-okd-$(VERSION).tar.gz
	rm -f redhat-openshift-$(VERSION).tar.gz
	rm -rf $(INSTALL_PATH)

build: clean
	ansible-galaxy collection build

install: build
	ansible-galaxy collection install --force -p $(INSTALL_PATH) community-okd-$(VERSION).tar.gz

sanity: install
	cd $(INSTALL_PATH)/ansible_collections/community/okd && ansible-test sanity -v --python $(PYTHON_VERSION) $(SANITY_TEST_ARGS) && rm -rf $(INSTALL_PATH)

units: install
	cd $(INSTALL_PATH)/ansible_collections/community/okd && ansible-test units -v --python $(PYTHON_VERSION) $(UNITS_TEST_ARGS) && rm -rf $(INSTALL_PATH)

molecule: install
	cd $(INSTALL_PATH)/ansible_collections/community/okd && molecule test

test-integration: upstream-test-integration downstream-test-integration

test-sanity: upstream-test-sanity downstream-test-sanity

test-units: upstream-test-units downstream-test-units

test-integration-incluster:
	./ci/incluster_integration.sh

upstream-test-sanity: sanity

upstream-test-units: units

upstream-test-integration: molecule

downstream-test-sanity:
	./ci/downstream.sh -s

downstream-test-units:
	./ci/downstream.sh -u

downstream-test-integration:
	./ci/downstream.sh -i

downstream-build:
	./ci/downstream.sh -b
