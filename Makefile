# Also needs to be updated in galaxy.yml
VERSION = 0.1.0

build:
	ansible-galaxy collection build --force

install: build
	ansible-galaxy collection install -p ansible_collections --force community-okd-${VERSION}.tar.gz

ci-prow: install
	molecule test
