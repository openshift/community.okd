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

DOCUMENTATION = r'''

module: openshift_adm_prune_builds

short_description: Prune openshift builds

version_added: "2.1.0"

author:
  - Aubin Bikouo (@abikouo)

description:
  - Remove old completed and failed builds
  - Analogous to `oc adm prune builds`.

extends_documentation_fragment:
  - kubernetes.core.k8s_auth_options

options:
  namespace:
    description:
    - Use to specify namespace for deployments to be deleted.
    type: str
  keep_younger_than:
    description:
    - Specify the minimum age (in minutes) of a Build for it to be considered a candidate for pruning.
    type: int
  orphans:
    description:
    - If true, prune all builds whose associated BuildConfig no longer exists and whose status is complete,
      failed, error, or cancelled.
    type: bool
    default: False

requirements:
  - python >= 3.6
  - kubernetes >= 12.0.0
'''

EXAMPLES = r'''
- name: Prune all builds whose associated BuildConfig no longer exists from namespace testing
  openshift_adm_prune_builds:
    namespace: testing
    orphans: yes
'''


RETURN = r'''
builds:
  type: list
  description: list of builds candidate for pruning.
  returned: always
'''

import copy
import traceback
import datetime

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.kubernetes.core.plugins.module_utils.args_common import AUTH_ARG_SPEC
from ansible_collections.kubernetes.core.plugins.module_utils.common import (K8sAnsibleMixin, get_api_client)
from ansible.module_utils._text import to_native

from kubernetes.dynamic.exceptions import DynamicApiError


def argument_spec():
    args = copy.deepcopy(AUTH_ARG_SPEC)
    args.update(
        dict(
            namespace=dict(type='str',),
            keep_younger_than=dict(type='int',),
            orphans=dict(type='bool', default=False),
        )
    )
    return args


class OpenShiftAdmPruneBuilds(AnsibleModule):
    def __init__(self):
        AnsibleModule.__init__(
            self,
            argument_spec=argument_spec(),
            supports_check_mode=True,
        )

        self.k8s_ansible_mixin = K8sAnsibleMixin(module=self)
        self.k8s_ansible_mixin.client = get_api_client(module=self)

    def resolve(self, builds):

        def _complete_failed(obj):
            try:
                return obj['status']['phase'] in ('Failed', 'Complete')
            except Exception:
                return False

        def _younger(obj):
            creation_timestamp = datetime.datetime.strptime(obj['metadata']['creationTimestamp'], '%Y-%m-%dT%H:%M:%SZ')
            now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            age = (now - creation_timestamp).seconds / 60
            return age > self.params['keep_younger_than']

        def _orphan(obj):
            try:
                if obj['status']['phase'] in ('Cancelled', 'Complete', 'Error', 'Failed'):
                    build_config = obj['status'].get('config')
                    # when status.config is None, Build is considered Orphan
                    if not build_config:
                        return True
                    # check if the parent BuildConfig exists
                    params = {
                        'kind': 'BuildConfig', 
                        'api_version': 'build.openshift.io/v1',
                        'namespace': build_config['namespace'],
                        'name': build_config['name'],
                    }
                    exists = self.k8s_ansible_mixin.kubernetes_facts(**params)
                    return exists['resources'] == []
            except Exception:
                return False

        predicates = [_complete_failed]
        if self.params['orphans']:
            predicates.append(_orphan)
        if self.params['keep_younger_than']:
            predicates.append(_younger)

        results = []
        for x in builds:
            if all([pred(x) for pred in predicates]):
                results.append((x['metadata']['namespace'], x['metadata']['name']))
        return results

    def execute(self):
        # list builds
        kind = 'Build'
        api_version = 'build.openshift.io/v1'
        builds = self.k8s_ansible_mixin.kubernetes_facts(kind=kind, api_version=api_version, namespace=self.params.get('namespace'))

        prunable_builds = self.resolve(builds=builds['resources'])
        if prunable_builds == []:
            self.exit_json(changed=False, msg="No candidate Builds for pruning.")
        if self.check_mode:
            self.exit_json(changed=False, builds=[x + '/' + y for x, y in prunable_builds])
        else:
            resource = self.k8s_ansible_mixin.find_resource(kind=kind, api_version=api_version, fail=True)
            for namespace, name in prunable_builds:
                try:
                    resource.delete(name=name, namespace=namespace)
                except DynamicApiError as exc:
                    msg = "Failed to delete Build {namespace}/{name} due to: {msg}".format(namespace=namespace, name=name, msg=exc.body)
                    self.fail_json(msg=msg)
                except Exception as e:
                    msg = "Failed to delete Build {namespace}/{name} due to: {msg}".format(namespace=namespace, name=name, msg=to_native(e))
                    self.fail_json(msg=msg)
            self.exit_json(changed=False, builds=[x + '/' + y for x, y in prunable_builds])


def main():
    try:
        module = OpenShiftAdmPruneBuilds()
        module.execute()
    except Exception as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()
