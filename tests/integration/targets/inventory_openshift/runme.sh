#!/usr/bin/env bash

set -eux

export ANSIBLE_INVENTORY_ENABLED=community.okd.openshift
export ANSIBLE_PYTHON_INTERPRETER=auto_silent

ansible-playbook playbooks/play.yml -i playbooks/test.inventory_openshift.yml "$@"
