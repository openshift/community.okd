#!/usr/bin/env bash

# create inventory pod resources
ansible-playbook playbooks/setup.yml "$@"

set -eux

function cleanup() {
    ansible-playbook playbooks/teardown.yml "$@"
    exit 1
}

trap 'cleanup "${@}"'  ERR

export ANSIBLE_INVENTORY_ENABLED="community.okd.openshift"

# test inventory
ansible-playbook playbooks/run.yml -i files/inventory.yaml "$@"

# cleanup testing environment
ansible-playbook playbooks/teardown.yml "$@"
