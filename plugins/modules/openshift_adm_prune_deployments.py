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

module: openshift_adm_prune_deployments

short_description: Remove old completed and failed deployment configs

version_added: "2.1.0"

author:
  - Aubin Bikouo (@abikouo)

description:
  - This module allow administrators to remove old completed and failed deployment configs.
  - Analogous to `oc adm prune deployments`.

extends_documentation_fragment:
  - kubernetes.core.k8s_auth_options

options:
  namespace:
    description:
    - Use to specify namespace for deployments to be deleted.
    type: str
  keep_younger_than:
    description:
    - Specify the minimum age (in minutes) of a deployment for it to be considered a candidate for pruning.
    type: int
  orphans:
    description:
    - If true, prune all deployments where the associated DeploymentConfig no longer exists,
      the status is complete or failed, and the replica size is 0.
    type: bool
    default: False

requirements:
  - python >= 3.6
  - kubernetes >= 12.0.0
'''

EXAMPLES = r'''
- name: Prune Deployments from testing namespace
  openshift_adm_prune_deployments:
    namespace: testing

- name: Prune orphans deployments, keep younger than 2hours
  openshift_adm_prune_deployments:
    orphans: True
    keep_younger_than: 120
'''


RETURN = r'''
replication_controllers:
  type: list
  description: list of replication controllers candidate for pruning.
  returned: always
'''

import copy
import traceback
import datetime

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.kubernetes.core.plugins.module_utils.args_common import AUTH_ARG_SPEC
from ansible_collections.kubernetes.core.plugins.module_utils.common import (K8sAnsibleMixin, get_api_client)
from ansible.module_utils._text import to_native

from kubernetes import client
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


def get_deploymentconfig_for_replicationcontroller(replica_controller):
    # DeploymentConfigAnnotation is an annotation name used to correlate a deployment with the
    # DeploymentConfig on which the deployment is based.
    # This is set on replication controller pod template by deployer controller.
    DeploymentConfigAnnotation = "openshift.io/deployment-config.name"
    try:
        deploymentconfig_name = replica_controller['metadata']['annotations'].get(DeploymentConfigAnnotation)
        if deploymentconfig_name is None or deploymentconfig_name == "":
            return None
        return deploymentconfig_name
    except Exception:
        return None


class OpenShiftAdmPruneDeployment(AnsibleModule):
    def __init__(self):
        AnsibleModule.__init__(
            self,
            argument_spec=argument_spec(),
            supports_check_mode=True,
        )

        self.k8s_ansible_mixin = K8sAnsibleMixin(module=self)
        self.k8s_ansible_mixin.client = get_api_client(module=self)

    def filter_replication_controller(self, replicacontrollers):
        def _deployment(obj):
            return get_deploymentconfig_for_replicationcontroller(obj) is not None

        def _zeroReplicaSize(obj):
            return obj['spec']['replicas'] == 0 and obj['status']['replicas'] == 0

        def _complete_failed(obj):
            DeploymentStatusAnnotation = "openshift.io/deployment.phase"
            try:
                # validate that replication controller status is either 'Complete' or 'Failed'
                deployment_phase = obj['metadata']['annotations'].get(DeploymentStatusAnnotation)
                return deployment_phase in ('Failed', 'Complete')
            except Exception:
                return False

        def _younger(obj):
            creation_timestamp = datetime.datetime.strptime(obj['metadata']['creationTimestamp'], '%Y-%m-%dT%H:%M:%SZ')
            now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            age = (now - creation_timestamp).seconds / 60
            return age > self.params['keep_younger_than']

        def _orphan(obj):
            try:
                # verify if the deploymentconfig associated to the replication controller is still existing
                deploymentconfig_name = get_deploymentconfig_for_replicationcontroller(obj)
                exists = self.k8s_ansible_mixin.kubernetes_facts(kind="DeploymentConfig",
                                                                 api_version="apps.openshift.io/v1",
                                                                 name=deploymentconfig_name,
                                                                 namespace=self.params.get('namespace'))
                return not (exists.get['api_found'] and len(exists['resources']) > 0)
            except Exception:
                return False

        predicates = [_deployment, _zeroReplicaSize, _complete_failed]
        if self.params['orphans']:
            predicates.append(_orphan)
        if self.params['keep_younger_than']:
            predicates.append(_younger)

        results = []
        for item in replicacontrollers:
            if all([pred(item) for pred in predicates]):
                results.append(item)
        return results

    def execute(self):
        # list replicationcontroller candidate for pruning
        kind = 'ReplicationController'
        api_version = 'v1'
        api = self.k8s_ansible_mixin.find_resource(kind=kind, api_version=api_version, fail=True)
        replication_list = api.get()
        candidates = self.filter_replication_controller(replication_list.items)

        if len(candidates) == 0:
            self.exit_json(changed=False, msg="No candidate ReplicationController for pruning.")

        candidates = [(rep['metadata']['namespace'], rep['metadata']['name']) for rep in candidates]
        if self.check_mode:
            self.exit_json(changed=False, replication_controllers=[x + "/" + y for x, y in candidates])
        else:
            resource = self.k8s_ansible_mixin.find_resource(kind="ReplicationController", api_version="v1", fail=True)
            delete_options = client.V1DeleteOptions(propagation_policy='Background')
            for namespace, name in candidates:
                try:
                    resource.delete(name=name, namespace=namespace, body=delete_options)
                except DynamicApiError as exc:
                    msg = "Failed to delete ReplicationController {namespace}/{name} due to: {msg}".format(namespace=namespace, name=name, msg=exc.body)
                    self.fail_json(msg=msg)
                except Exception as e:
                    msg = "Failed to delete ReplicationController {namespace}/{name} due to: {msg}".format(namespace=namespace, name=name, msg=to_native(e))
                    self.fail_json(msg=msg)
            self.exit_json(changed=True, result=[x + "/" + y for x, y in candidates])


def main():
    try:
        module = OpenShiftAdmPruneDeployment()
        module.execute()
    except Exception as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()
