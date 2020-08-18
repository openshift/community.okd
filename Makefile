# Also needs to be updated in galaxy.yml
VERSION = 0.1.0

# To run sanity tests in docker, set SANITY_TEST_ARGS to '--docker'
SANITY_TEST_ARGS ?= '--venv'

clean:
	rm -f community-okd-$(VERSION).tar.gz
	rm -rf ansible_collections

build: clean
	ansible-galaxy collection build

install: build
	ansible-galaxy collection install -p ansible_collections community-okd-$(VERSION).tar.gz

test-sanity: install
	cd ansible_collections/community/okd && ansible-test sanity -v --color $(SANITY_TEST_ARGS)

test-integration: install
	molecule test
