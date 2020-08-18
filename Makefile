# Also needs to be updated in galaxy.yml
VERSION = 0.1.0

# To run sanity tests in a venv, set SANITY_TEST_ARGS to '--venv'
SANITY_TEST_ARGS ?= --docker --color

clean:
	rm -f community-okd-$(VERSION).tar.gz
	rm -rf ansible_collections

build: clean
	ansible-galaxy collection build

install-kubernetes-src:
	mkdir -p ansible_collections/community/kubernetes
	rm -rf ansible_collections/community/kubernetes/*
	curl -L https://github.com/ansible-collections/community.kubernetes/archive/main.tar.gz | tar -xz -C ansible_collections/community/kubernetes --strip-components 1

# TODO: Once we no longer rely on features in main we should drop the install-kubernetes-src dependency
install: build install-kubernetes-src

release: build
	ansible-galaxy collection publish community-okd-${VERSION}.tar.gz

test-molecule: install
	molecule test

test-sanity: 
	ansible-test sanity --exclude ci/ -v $(SANITY_TEST_ARGS)

test-integration-incluster:
	./ci/incluster_integration.sh

downstream-test-sanity: 
	./utils/downstream.sh -s

downstream-test-integration: 
	./utils/downstream.sh -i

downstream-build: 
	./utils/downstream.sh -b
