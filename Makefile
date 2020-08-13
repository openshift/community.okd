# Also needs to be updated in galaxy.yml
VERSION = 0.1.0

clean:
	rm -f community-okd-${VERSION}.tar.gz
	rm -rf ansible_collections

build: clean
	ansible-galaxy collection build

install: build
	ansible-galaxy collection install -p ansible_collections community-okd-${VERSION}.tar.gz

ci-prow: install
	molecule test
