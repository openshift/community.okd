# Also needs to be updated in galaxy.yml
VERSION = 1.0.1

# To run sanity tests in a venv, set SANITY_TEST_ARGS to '--venv'
SANITY_TEST_ARGS ?= --docker --color

clean:
	rm -f community-okd-$(VERSION).tar.gz
	rm -rf ansible_collections

build: clean
	ansible-galaxy collection build

install-kubernetes-src:
	ansible-galaxy collection install -p ansible_collections kubernetes.core

install: build install-kubernetes-src
	ansible-galaxy collection install -p ansible_collections community-okd-$(VERSION).tar.gz

test-integration-incluster:
	./ci/incluster_integration.sh

test-sanity: upstream-test-sanity downstream-test-sanity

test-integration: upstream-test-integration downstream-test-integration

upstream-test-integration: install
	molecule test

upstream-test-sanity: install
	cd ansible_collections/community/okd && ansible-test sanity --exclude ci/ -v $(SANITY_TEST_ARGS)

downstream-test-sanity:
	./ci/downstream.sh -s

downstream-test-integration:
	./ci/downstream.sh -i

downstream-build:
	./ci/downstream.sh -b
