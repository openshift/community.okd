# Copyright 2021 Red Hat | Ansible
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: openshift_taint
short_description: Taint a node in a OpenShift cluster
version_added: "2.1.0"
author: Alina Buzachis (@alinabuzachis)
description:
    - Taint allows a node to refuse Pod to be scheduled unless that Pod has a matching toleration.
    - Untaint will remove taints from nodes as needed.
extends_documentation_fragment:
    - kubernetes.core.k8s_auth_options
    - kubernetes.core.k8s_wait_options
    - kubernetes.core.k8s_resource_options
options:
    state:
        description:
            - Determines whether to add or remove taints.
        type: str
        default: present
        choices: [ present, absent ]
    name:
        description:
            - The name of the node.
        required: true
        type: str
    taints:
        description:
            - List containing the taints.
        type: list
        elements: dict
        suboptions:
            key:
                description:
                    - The taint key to be applied to a node.
                type: str
                required: true
            value:
                description:
                    - The taint value corresponding to the taint key.
                type: str
            effect:
                description:
                    - The effect of the taint on pods that do not tolerate the taint.
                type: str
                required: when I(state=present)
                choices: [ NoSchedule, NoExecute ]
requirements:
  - python >= 3.6
  - kubernetes >= 12.0.0
"""

EXAMPLES = r"""
- name: Taint node "foo"
  kubernetes.core.opensihft_taint:
    state: present
    name: foo
    taints:
        - effect: NoExecute
          key: "key1"
          value: "value1"

- name: Taint node "foo"
  kubernetes.core.opensihft_taint:
    state: present
    name: foo
    taints:
        - effect: NoExecute
          key: "key1"
          value: "value1"
        - effect: NoSchedule
          key: "key1"
          value: "value1"

- name: Remove all taints from "foo" with "key=key1".
  kubernetes.core.k8s_drain:
    state: absent
    name: foo
    taints: "key1"

- name: Remove taint from "foo".
  kubernetes.core.k8s_drain:
    state: absent
    name: foo
    taints:
        - effect: NoExecute
          key: "key1"
          value: "value1"
"""

RETURN = r"""
result:
   description:
        -  Shows if the node has been successfully tainted/untained.
   type: str
   sample: "node/ip-10-0-152-161.eu-central-1.compute.internal untainted"
"""


import copy
import traceback

from ansible.module_utils._text import to_native

from kubernetes import client
from kubernetes.client.api import core_v1_api
from kubernetes.dynamic.exceptions import ApiException

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.kubernetes.core.plugins.module_utils.args_common import (
    AUTH_ARG_SPEC,
)
from ansible_collections.kubernetes.core.plugins.module_utils.common import (
    K8sAnsibleMixin,
    get_api_client,
)


def argument_spec():
    argument_spec = copy.deepcopy(AUTH_ARG_SPEC)
    argument_spec.update(
        dict(
            state=dict(type="str", choices=["present", "absent"], default="present"),
            name=dict(type="str", required=True),
            taints=dict(type="list", required=True),
            overwrite=dict(type="bool", default=False),
        )
    )

    return argument_spec


def _equal_dicts(a, b):
    ignore_keys = ("time_added", "value")
    ka = set(a).difference(ignore_keys)
    kb = set(b).difference(ignore_keys)

    return all(a[k] == b[k] for k in ka if k in kb)


def _get_difference(a, b):
    return [
        a_item for a_item in a if not any(_equal_dicts(a_item, b_item) for b_item in b)
    ]


def _get_intersection(a, b):
    return [a_item for a_item in a if any(_equal_dicts(a_item, b_item) for b_item in b)]


class OpenShiftTaint(AnsibleModule):
    def __init__(self):
        AnsibleModule.__init__(
            self,
            argument_spec=argument_spec(),
            supports_check_mode=True,
        )

        self.k8s_ansible_mixin = K8sAnsibleMixin(module=self)
        self.k8s_ansible_mixin.client = get_api_client(module=self)
        self._api_instance = core_v1_api.CoreV1Api(self.k8s_ansible_mixin.client.client)
    
    @property
    def argument_spec():
        argument_spec = copy.deepcopy(AUTH_ARG_SPEC)
        argument_spec.update(
        dict(
            state=dict(type="str", choices=["present", "absent"], default="present"),
            name=dict(type="str", required=True),
            taints=dict(type="list", required=True),
            overwrite=dict(type="bool", default=False),
        )
    )

        return argument_spec

    def get_current_taints(self, name):
        try:
            node = self._api_instance.read_node(name=name)
        except ApiException as exc:
            if exc.reason == "Not Found":
                self.fail_json(msg="Node '{0}' has not been found.".format(name))
            self.fail_json(
                msg="Failed to retrieve node '{0}' due to: {1}".format(
                    name, exc.reason
                ),
                status=exc.status,
            )
        except Exception as exc:
            self.fail_json(
                msg="Failed to retrieve node '{0}' due to: {1}".format(
                    name, to_native(exc)
                )
            )

        return node.spec.to_dict()["taints"] or []

    def patch_node(self, taints):
        body = {"spec": {"taints": taints}}

        try:
            self._api_instance.patch_node(name=self.params.get("name"), body=body)
        except Exception as exc:
            self.fail_json(
                msg="Failed to patch node due to: {0}".format(to_native(exc))
            )

    def if_failed(fn):
        def wrapper(self, *args):
            result = {}
            res = _get_difference(*args)
            if (
                not res
                and self.params.get("state") == "present"
                and not self.params.get("overwrite")
            ):
                result["result"] = "node/{0} already has ".format(
                    self.params.get("name")
                ) + "{0} taint(s) with same effect(s) and overwrite is false".format(
                    ", ".join(
                        map(
                            lambda t: "%s" % t["key"],
                            _get_intersection((*args)),
                        )
                    )
                )

                self.exit_json(changed=False, **result)

            if res and self.params.get("state") == "absent":
                self.fail_json(
                    msg="{0} not found".format(
                        ", ".join(map(lambda t: "%s" % t["key"], res))
                    )
                )

            return fn(self, *args)

        return wrapper

    @if_failed
    def _taint(self, new_taints, current_taints):
        if not self.params.get("overwrite"):
            self.patch_node(taints=[*current_taints, *new_taints])
        else:
            self.patch_node(taints=new_taints)

    @if_failed
    def _untaint(self, new_taints, current_taints):
        self.patch_node(taints=_get_difference(current_taints, new_taints))

    def execute(self):
        result = {}
        state = self.params.get("state")
        taints = self.params.get("taints")
        name = self.params.get("name")

        current_taints = self.get_current_taints(name)

        def _ensure_dict(a):
            for item_a in a:
                if not isinstance(item_a, dict):
                    a.remove(item_a)
                    a.append({"key": item_a})

        if state == "present":
            self._taint(taints, current_taints)
            result["result"] = "node/{0} tainted".format(name)

        if state == "absent":
            _ensure_dict(taints)
            self._untaint(taints, current_taints)
            result["result"] = "node/{0} untainted".format(name)

        self.exit_json(changed=True, **result)


def main():
    try:
        module = OpenShiftTaint()
        module.execute()
    except Exception as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())


if __name__ == "__main__":
    main()
