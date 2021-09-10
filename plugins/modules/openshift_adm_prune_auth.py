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

module: openshift_adm_prune_auth

short_description: Removes references to the specified roles, clusterroles, users, and groups

version_added: "2.1.0"

author:
  - Aubin Bikouo (@abikouo)

description:
  - This module allow administrators to remove references to the specified roles, clusterroles, users, and groups.
  - Analogous to `oc adm prune auth`.

extends_documentation_fragment:
  - kubernetes.core.k8s_auth_options

options:
  resource:
    description:
    - The specified resource to remove.
    choices:
    - roles
    - clusterroles
    - users
    - groups
    type: str
    required: True
  name:
    description:
    - Use to specify an object name to remove.
    - Mutually exclusive with option I(label_selectors).
    - If neither I(name) nor I(label_selectors) are specified, Prune all resources in the namespace.
    type: str
  namespace:
    description:
    - Use to specify an object namespace.
    - Ignored when I(resource) is set to C(clusterroles)
    type: str
  label_selectors:
    description:
    - Selector (label query) to filter on.
    - Mutually exclusive with option I(name).
    type: list
    elements: str

requirements:
  - python >= 3.6
  - kubernetes >= 12.0.0
'''

EXAMPLES = r'''
- name: Prune all roles from default namespace
  openshift_adm_prune_auth:
    resource: roles
    namespace: testing

- name: Prune clusterroles using label selectors
  openshift_adm_prune_auth:
    resource: roles
    namespace: testing
    label_selectors:
      - phase=production
'''


RETURN = r'''
cluster_role_binding:
  type: list
  description: list of cluster role binding deleted.
  returned: always
role_binding:
  type: list
  description: list of role binding deleted.
  returned: I(resource=users) or I(resource=groups) or I(resource=clusterroles)
security_context_constraints:
  type: list
  description: list of Security Context Constraints deleted.
  returned: I(resource=users) or I(resource=groups)
authorization:
  type: list
  description: list of OAuthClientAuthorization deleted.
  returned: I(resource=users)
group:
  type: list
  description: list of Security Context Constraints deleted.
  returned: I(resource=users)
'''


import copy

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.kubernetes.core.plugins.module_utils.args_common import AUTH_ARG_SPEC
from ansible.module_utils._text import to_native

from kubernetes import client
from kubernetes.dynamic.exceptions import DynamicApiError, NotFoundError


def argument_spec():
    args = copy.deepcopy(AUTH_ARG_SPEC)
    args.update(
        dict(
            resource=dict(type='str', required=True, choices=['roles', 'clusterroles', 'users', 'groups']),
            namespace=dict(type='str'),
            name=dict(type='str'),
            label_selectors=dict(type='list', elements='str'),
        )
    )
    return args


def prune_resource_binding(module, k8s_ansible_mixin, kind, api_version, ref_kind, ref_namespace_names, propagation_policy=None):

    resource = k8s_ansible_mixin.find_resource(kind=kind, api_version=api_version, fail=True)
    candidates = []
    for ref_namespace, ref_name in ref_namespace_names:
        try:
            result = resource.get(name=None, namespace=ref_namespace)
            result = result.to_dict()
            result = result.get('items') if 'items' in result else [result]
            for obj in result:
                namespace = obj['metadata'].get('namespace', None)
                name = obj['metadata'].get('name')
                if ref_kind and obj['roleRef']['kind'] != ref_kind:
                    # skip this binding as the roleRef.kind does not match
                    continue
                if obj['roleRef']['name'] == ref_name:
                    # select this binding as the roleRef.name match
                    candidates.append((namespace, name))
        except NotFoundError:
            continue
        except DynamicApiError as exc:
            msg = "Failed to get {kind} resource due to: {msg}".format(kind=kind, msg=exc.body)
            module.fail_json(msg=msg)
        except Exception as e:
            msg = "Failed to get {kind} due to: {msg}".format(kind=kind, msg=to_native(e))
            module.fail_json(msg=msg)

    if len(candidates) == 0 or module.check_mode:
        return [y if x is None else x + "/" + y for x, y in candidates]

    delete_options = client.V1DeleteOptions()
    if propagation_policy:
        delete_options.propagation_policy = propagation_policy

    for namespace, name in candidates:
        try:
            result = resource.delete(name=name, namespace=namespace, body=delete_options)
        except DynamicApiError as exc:
            msg = "Failed to delete {kind} {namespace}/{name} due to: {msg}".format(kind=kind, namespace=namespace, name=name, msg=exc.body)
            module.fail_json(msg=msg)
        except Exception as e:
            msg = "Failed to delete {kind} {namespace}/{name} due to: {msg}".format(kind=kind, namespace=namespace, name=name, msg=to_native(e))
            module.fail_json(msg=msg)
    return [y if x is None else x + "/" + y for x, y in candidates]


def update_resource_binding(module, k8s_ansible_mixin, ref_kind, ref_names, namespaced=False):

    kind = 'ClusterRoleBinding'
    api_version = "rbac.authorization.k8s.io/v1",
    if namespaced:
        kind = "RoleBinding"
    resource = k8s_ansible_mixin.find_resource(kind=kind, api_version=api_version, fail=True)
    result = resource.get(name=None, namespace=None).to_dict()
    result = result.get('items') if 'items' in result else [result]

    if len(result) == 0:
        return [], False

    def _update_user_group(binding_namespace, subjects):
        users, groups = [], []
        for x in subjects:
            if x['kind'] == 'User':
                users.append(x['name'])
            elif x['kind'] == 'Group':
                groups.append(x['name'])
            elif x['kind'] == 'ServiceAccount':
                namespace = binding_namespace
                if x.get('namespace') is not None:
                    namespace = x.get('namespace')
                if namespace is not None:
                    users.append("system:serviceaccount:%s:%s" % (namespace, x['name']))
        return users, groups

    candidates = []
    changed = False
    for item in result:
        subjects = item.get('subjects', [])
        retainedSubjects = [x for x in subjects if x['kind'] == ref_kind and x['name'] in ref_names]
        if len(subjects) != len(retainedSubjects):
            updated_binding = item
            updated_binding['subjects'] = retainedSubjects
            binding_namespace = item['metadata'].get('namespace', None)
            updated_binding['userNames'], updated_binding['groupNames'] = _update_user_group(binding_namespace, retainedSubjects)
            candidates.append(binding_namespace + "/" + item['metadata']['name'] if binding_namespace else item['metadata']['name'])
            if not module.check_mode:
                try:
                    resource.apply(updated_binding, namespace=binding_namespace)
                    changed = True
                except DynamicApiError as exc:
                    msg = "Failed to apply object due to: {0}".format(exc.body)
                    module.fail_json(msg=msg)
    return candidates, changed


def update_security_context(module, k8s_ansible_mixin, ref_names, key):
    params = {'kind': 'SecurityContextConstraints', 'api_version': 'security.openshift.io/v1'}
    sccs = k8s_ansible_mixin.kubernetes_facts(**params)
    if not sccs['api_found']:
        module.fail_json(msg=sccs['msg'])
    sccs = sccs.get('resources')

    candidates = []
    changed = False
    resource = k8s_ansible_mixin.find_resource(kind="SecurityContextConstraints", api_version="security.openshift.io/v1")
    for item in sccs:
        subjects = item.get(key, [])
        retainedSubjects = [x for x in subjects if x not in ref_names]
        if len(subjects) != len(retainedSubjects):
            candidates.append(item['metadata']['name'])
            if not module.check_mode:
                upd_sc = item
                upd_sc.update({key: retainedSubjects})
                try:
                    resource.apply(upd_sc, namespace=None)
                    changed = True
                except DynamicApiError as exc:
                    msg = "Failed to apply object due to: {0}".format(exc.body)
                    module.fail_json(msg=msg)
    return candidates, changed


def auth_prune_roles(module, k8s_ansible_mixin):
    params = {'kind': 'Role', 'api_version': 'rbac.authorization.k8s.io/v1', 'namespace': module.params.get('namespace')}
    for attr in ('name', 'label_selectors'):
        if module.params.get(attr):
            params[attr] = module.params.get(attr)

    result = k8s_ansible_mixin.kubernetes_facts(**params)
    if not result['api_found']:
        module.fail_json(msg=result['msg'])

    roles = result.get('resources')
    if len(roles) == 0:
        module.exit_json(changed=False, msg="No candidate rolebinding to prune from namespace %s." % module.params.get('namespace'))

    ref_roles = [(x['metadata']['namespace'], x['metadata']['name']) for x in roles]
    candidates = prune_resource_binding(module=module,
                                        k8s_ansible_mixin=k8s_ansible_mixin,
                                        kind="RoleBinding",
                                        api_version="rbac.authorization.k8s.io/v1",
                                        ref_kind="Role",
                                        ref_namespace_names=ref_roles,
                                        propagation_policy='Foreground')
    if len(candidates) == 0 or module.check_mode:
        module.exit_json(changed=False, role_binding=candidates)

    module.exit_json(changed=True, role_binding=candidates)


def auth_prune_clusterroles(module, k8s_ansible_mixin):
    params = {'kind': 'ClusterRole', 'api_version': 'rbac.authorization.k8s.io/v1'}
    for attr in ('name', 'label_selectors'):
        if module.params.get(attr):
            params[attr] = module.params.get(attr)

    result = k8s_ansible_mixin.kubernetes_facts(**params)
    if not result['api_found']:
        module.fail_json(msg=result['msg'])

    clusterroles = result.get('resources')
    if len(clusterroles) == 0:
        module.exit_json(changed=False, msg="No clusterroles found matching input criteria.")

    ref_clusterroles = [(None, x['metadata']['name']) for x in clusterroles]

    # Prune ClusterRoleBinding
    candidates_cluster_binding = prune_resource_binding(module=module,
                                                        k8s_ansible_mixin=k8s_ansible_mixin,
                                                        kind="ClusterRoleBinding",
                                                        api_version="rbac.authorization.k8s.io/v1",
                                                        ref_kind=None,
                                                        ref_namespace_names=ref_clusterroles)

    # Prune Role Binding
    candidates_namespaced_binding = prune_resource_binding(module=module,
                                                           k8s_ansible_mixin=k8s_ansible_mixin,
                                                           kind="RoleBinding",
                                                           api_version="rbac.authorization.k8s.io/v1",
                                                           ref_kind='ClusterRole',
                                                           ref_namespace_names=ref_clusterroles)
    if module.check_mode:
        module.exit_json(changed=False,
                         cluster_role_binding=candidates_cluster_binding,
                         role_binding=candidates_namespaced_binding)

    module.exit_json(changed=True,
                     cluster_role_binding=candidates_cluster_binding,
                     role_binding=candidates_namespaced_binding)


def list_groups(k8s_ansible_mixin, module=None):
    params = {'kind': 'Group', 'api_version': 'user.openshift.io/v1'}
    if module:
        for attr in ('name', 'label_selectors'):
            if module.params.get(attr):
                params[attr] = module.params.get(attr)
    return k8s_ansible_mixin.kubernetes_facts(**params)


def auth_prune_users(module, k8s_ansible_mixin):
    params = {'kind': 'User', 'api_version': 'user.openshift.io/v1'}
    for attr in ('name', 'label_selectors'):
        if module.params.get(attr):
            params[attr] = module.params.get(attr)

    users = k8s_ansible_mixin.kubernetes_facts(**params)
    if len(users) == 0:
        module.exit_json(changed=False, msg="No resource type 'User' found matching input criteria.")

    names = [x['metadata']['name'] for x in users]
    changed = False
    # Remove the user role binding
    rolebinding, changed_role = update_resource_binding(module=module,
                                                        k8s_ansible_mixin=k8s_ansible_mixin,
                                                        ref_kind="User",
                                                        ref_names=names,
                                                        namespaced=True)
    changed = changed or changed_role
    # Remove the user cluster role binding
    clusterrolesbinding, changed_cr = update_resource_binding(module=module,
                                                              k8s_ansible_mixin=k8s_ansible_mixin,
                                                              ref_kind="User",
                                                              ref_names=names)
    changed = changed or changed_cr

    # Remove the user from security context constraints
    sccs, changed_sccs = update_security_context(module, k8s_ansible_mixin, names, 'users')
    changed = changed or changed_sccs

    # Remove the user from groups
    groups = list_groups(k8s_ansible_mixin)
    deleted_groups = []
    resource = k8s_ansible_mixin.find_resource(kind="Group", api_version="user.openshift.io/v1")
    for grp in groups:
        subjects = grp.get('users', [])
        retainedSubjects = [x for x in subjects if x not in names]
        if len(subjects) != len(retainedSubjects):
            deleted_groups.append(grp['metadata']['name'])
            if not module.check_mode:
                upd_group = grp
                upd_group.update({'users': retainedSubjects})
                try:
                    resource.apply(upd_group, namespace=None)
                    changed = True
                except DynamicApiError as exc:
                    msg = "Failed to apply object due to: {0}".format(exc.body)
                    module.fail_json(msg=msg)

    # Remove the user's OAuthClientAuthorizations
    oauth = k8s_ansible_mixin.kubernetes_facts(kind='OAuthClientAuthorization', api_version='oauth.openshift.io/v1')
    deleted_auths = []
    resource = k8s_ansible_mixin.find_resource(kind="OAuthClientAuthorization", api_version="oauth.openshift.io/v1")
    for authorization in oauth:
        if authorization.get('userName', None) in names:
            auth_name = authorization['metadata']['name']
            deleted_auths.append(auth_name)
            if not module.check_mode:
                try:
                    resource.delete(name=auth_name, namespace=None, body=client.V1DeleteOptions())
                    changed = True
                except DynamicApiError as exc:
                    msg = "Failed to delete OAuthClientAuthorization {name} due to: {msg}".format(name=auth_name, msg=exc.body)
                    module.fail_json(msg=msg)
                except Exception as e:
                    msg = "Failed to delete OAuthClientAuthorization {name} due to: {msg}".format(name=auth_name, msg=to_native(e))
                    module.fail_json(msg=msg)

    module.exit_json(changed=changed,
                     cluster_role_binding=clusterrolesbinding,
                     role_binding=rolebinding,
                     security_context_constraints=sccs,
                     authorization=deleted_auths,
                     group=deleted_groups)


def auth_prune_groups(module, k8s_ansible_mixin):
    groups = list_groups(k8s_ansible_mixin=k8s_ansible_mixin, module=module)
    if len(groups) == 0:
        module.exit_json(changed=False, result="No resource type 'Group' found matching input criteria.")

    names = [x['metadata']['name'] for x in groups]

    changed = False
    # Remove the groups role binding
    rolebinding, changed_role = update_resource_binding(module=module,
                                                        k8s_ansible_mixin=k8s_ansible_mixin,
                                                        ref_kind="Group",
                                                        ref_names=names,
                                                        namespaced=True)
    changed = changed or changed_role
    # Remove the groups cluster role binding
    clusterrolesbinding, changed_cr = update_resource_binding(module=module,
                                                              k8s_ansible_mixin=k8s_ansible_mixin,
                                                              ref_kind="Group",
                                                              ref_names=names)
    changed = changed or changed_cr
    # Remove the groups security context constraints
    sccs, changed_sccs = update_security_context(module, k8s_ansible_mixin, names, 'groups')
    changed = changed or changed_sccs

    module.exit_json(changed=changed,
                     cluster_role_binding=clusterrolesbinding,
                     role_binding=rolebinding,
                     security_context_constraints=sccs)


def execute_module(module, k8s_ansible_mixin):
    auth_prune = {
        'roles': auth_prune_roles,
        'clusterroles': auth_prune_clusterroles,
        'users': auth_prune_users,
        'groups': auth_prune_groups,
    }
    auth_prune[module.params.get('resource')](module, k8s_ansible_mixin)


def main():
    mutually_exclusive = [
        ('name', 'label_selectors'),
    ]
    required_if = [
        ['resource', 'roles', ['namespace']],
    ]
    module = AnsibleModule(argument_spec=argument_spec(),
                           mutually_exclusive=mutually_exclusive,
                           required_if=required_if,
                           supports_check_mode=True)
    from ansible_collections.kubernetes.core.plugins.module_utils.common import (
        K8sAnsibleMixin, get_api_client)

    k8s_ansible_mixin = K8sAnsibleMixin(module)
    k8s_ansible_mixin.client = get_api_client(module=module)
    execute_module(module, k8s_ansible_mixin)


if __name__ == '__main__':
    main()
