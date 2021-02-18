#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2018, Chris Houseknecht <@chouseknecht>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
__metaclass__ = type

# STARTREMOVE (downstream)
DOCUMENTATION = '''

module: k8s

short_description: Manage OpenShift objects

author:
    - "Chris Houseknecht (@chouseknecht)"
    - "Fabian von Feilitzsch (@fabianvf)"

description:
  - Use the OpenShift Python client to perform CRUD operations on K8s objects.
  - Pass the object definition from a source file or inline. See examples for reading
    files and using Jinja templates or vault-encrypted files.
  - Access to the full range of K8s APIs.
  - Use the M(k8s_info) module to obtain a list of items about an object of type C(kind)
  - Authenticate using either a config file, certificates, password or token.
  - Supports check mode.
  - Optimized for OKD/OpenShift Kubernetes flavors

extends_documentation_fragment:
  - kubernetes.core.k8s_state_options
  - kubernetes.core.k8s_name_options
  - kubernetes.core.k8s_resource_options
  - kubernetes.core.k8s_auth_options

notes:
  - If your OpenShift Python library is not 0.9.0 or newer and you are trying to
    remove an item from an associative array/dictionary, for example a label or
    an annotation, you will need to explicitly set the value of the item to be
    removed to `null`. Simply deleting the entry in the dictionary will not
    remove it from openshift or kubernetes.

options:
  merge_type:
    description:
    - Whether to override the default patch merge approach with a specific type. By default, the strategic
      merge will typically be used.
    - For example, Custom Resource Definitions typically aren't updatable by the usual strategic merge. You may
      want to use C(merge) if you see "strategic merge patch format is not supported"
    - See U(https://kubernetes.io/docs/tasks/run-application/update-api-object-kubectl-patch/#use-a-json-merge-patch-to-update-a-deployment)
    - Requires openshift >= 0.6.2
    - If more than one merge_type is given, the merge_types will be tried in order
    - If openshift >= 0.6.2, this defaults to C(['strategic-merge', 'merge']), which is ideal for using the same parameters
      on resource kinds that combine Custom Resources and built-in resources. For openshift < 0.6.2, the default
      is simply C(strategic-merge).
    - mutually exclusive with C(apply)
    choices:
    - json
    - merge
    - strategic-merge
    type: list
    elements: str
  wait:
    description:
    - Whether to wait for certain resource kinds to end up in the desired state. By default the module exits once Kubernetes has
      received the request
    - Implemented for C(state=present) for C(Deployment), C(DaemonSet) and C(Pod), and for C(state=absent) for all resource kinds.
    - For resource kinds without an implementation, C(wait) returns immediately unless C(wait_condition) is set.
    default: no
    type: bool
  wait_sleep:
    description:
    - Number of seconds to sleep between checks.
    default: 5
    type: int
  wait_timeout:
    description:
    - How long in seconds to wait for the resource to end up in the desired state. Ignored if C(wait) is not set.
    default: 120
    type: int
  wait_condition:
    description:
    - Specifies a custom condition on the status to wait for. Ignored if C(wait) is not set or is set to False.
    suboptions:
      type:
        type: str
        description:
        - The type of condition to wait for. For example, the C(Pod) resource will set the C(Ready) condition (among others)
        - Required if you are specifying a C(wait_condition). If left empty, the C(wait_condition) field will be ignored.
        - The possible types for a condition are specific to each resource type in Kubernetes. See the API documentation of the status field
          for a given resource to see possible choices.
      status:
        type: str
        description:
        - The value of the status field in your desired condition.
        - For example, if a C(Deployment) is paused, the C(Progressing) C(type) will have the C(Unknown) status.
        choices:
        - True
        - False
        - Unknown
        default: "True"
      reason:
        type: str
        description:
        - The value of the reason field in your desired condition
        - For example, if a C(Deployment) is paused, The C(Progressing) C(type) will have the C(DeploymentPaused) reason.
        - The possible reasons in a condition are specific to each resource type in Kubernetes.
          See the API documentation of the status field for a given resource to see possible choices.
    type: dict
  validate:
    description:
      - how (if at all) to validate the resource definition against the kubernetes schema.
        Requires the kubernetes-validate python module
    suboptions:
      fail_on_error:
        description: whether to fail on validation errors.
        type: bool
      version:
        description: version of Kubernetes to validate against. defaults to Kubernetes server version
        type: str
      strict:
        description: whether to fail when passing unexpected properties
        default: True
        type: bool
    type: dict
  append_hash:
    description:
    - Whether to append a hash to a resource name for immutability purposes
    - Applies only to ConfigMap and Secret resources
    - The parameter will be silently ignored for other resource kinds
    - The full definition of an object is needed to generate the hash - this means that deleting an object created with append_hash
      will only work if the same object is passed with state=absent (alternatively, just use state=absent with the name including
      the generated hash and append_hash=no)
    type: bool
    default: false
  apply:
    description:
    - C(apply) compares the desired resource definition with the previously supplied resource definition,
      ignoring properties that are automatically generated
    - C(apply) works better with Services than 'force=yes'
    - mutually exclusive with C(merge_type)
    type: bool
    default: false

requirements:
  - "python >= 2.7"
  - "openshift >= 0.6"
  - "PyYAML >= 3.11"
'''

EXAMPLES = '''
- name: Create a k8s namespace
  community.okd.k8s:
    name: testing
    api_version: v1
    kind: Namespace
    state: present

- name: Create a Service object from an inline definition
  community.okd.k8s:
    state: present
    definition:
      apiVersion: v1
      kind: Service
      metadata:
        name: web
        namespace: testing
        labels:
          app: galaxy
          service: web
      spec:
        selector:
          app: galaxy
          service: web
        ports:
        - protocol: TCP
          targetPort: 8000
          name: port-8000-tcp
          port: 8000

- name: Remove an existing Service object
  community.okd.k8s:
    state: absent
    api_version: v1
    kind: Service
    namespace: testing
    name: web

# Passing the object definition from a file

- name: Create a Deployment by reading the definition from a local file
  community.okd.k8s:
    state: present
    src: /testing/deployment.yml

- name: >-
    Read definition file from the Ansible controller file system.
    If the definition file has been encrypted with Ansible Vault it will automatically be decrypted.
  community.okd.k8s:
    state: present
    definition: "{{ lookup('file', '/testing/deployment.yml') | from_yaml }}"

- name: Read definition file from the Ansible controller file system after Jinja templating
  community.okd.k8s:
    state: present
    definition: "{{ lookup('template', '/testing/deployment.yml') | from_yaml }}"

- name: fail on validation errors
  community.okd.k8s:
    state: present
    definition: "{{ lookup('template', '/testing/deployment.yml') | from_yaml }}"
    validate:
      fail_on_error: yes

- name: warn on validation errors, check for unexpected properties
  community.okd.k8s:
    state: present
    definition: "{{ lookup('template', '/testing/deployment.yml') | from_yaml }}"
    validate:
      fail_on_error: no
      strict: yes
'''

RETURN = '''
result:
  description:
  - The created, patched, or otherwise present object. Will be empty in the case of a deletion.
  returned: success
  type: complex
  contains:
     api_version:
       description: The versioned schema of this representation of an object.
       returned: success
       type: str
     kind:
       description: Represents the REST resource this object represents.
       returned: success
       type: str
     metadata:
       description: Standard object metadata. Includes name, namespace, annotations, labels, etc.
       returned: success
       type: complex
     spec:
       description: Specific attributes of the object. Will vary based on the I(api_version) and I(kind).
       returned: success
       type: complex
     status:
       description: Current status details for the object.
       returned: success
       type: complex
     items:
       description: Returned only when multiple yaml documents are passed to src or resource_definition
       returned: when resource_definition or src contains list of objects
       type: list
     duration:
       description: elapsed time of task in seconds
       returned: when C(wait) is true
       type: int
       sample: 48
'''
# ENDREMOVE (downstream)

import re
import operator
import traceback
from functools import reduce

from ansible.module_utils._text import to_native

try:
    from ansible_collections.kubernetes.core.plugins.module_utils.raw import KubernetesRawModule
    HAS_KUBERNETES_COLLECTION = True
except ImportError as e:
    HAS_KUBERNETES_COLLECTION = False
    k8s_collection_import_exception = e
    K8S_COLLECTION_ERROR = traceback.format_exc()
    from ansible.module_utils.basic import AnsibleModule as KubernetesRawModule

try:
    import yaml
    from openshift.dynamic.exceptions import DynamicApiError, NotFoundError, ForbiddenError
except ImportError:
    # Exceptions handled in common
    pass

TRIGGER_ANNOTATION = 'image.openshift.io/triggers'
TRIGGER_CONTAINER = re.compile(r"(?P<path>.*)\[((?P<index>[0-9]+)|\?\(@\.name==[\"'\\]*(?P<name>[a-z0-9]([-a-z0-9]*[a-z0-9])?))")


class OKDRawModule(KubernetesRawModule):

    def __init__(self):
        if not HAS_KUBERNETES_COLLECTION:
            self.fail_json(
                msg="The kubernetes.core collection must be installed",
                exception=K8S_COLLECTION_ERROR,
                error=to_native(k8s_collection_import_exception)
            )
        super(OKDRawModule, self).__init__()

    def perform_action(self, resource, definition):
        state = self.params.get('state', None)
        name = definition['metadata'].get('name')
        namespace = definition['metadata'].get('namespace')

        if state != 'absent':

            if resource.kind in ['Project', 'ProjectRequest']:
                try:
                    resource.get(name, namespace)
                except (NotFoundError, ForbiddenError):
                    return self.create_project_request(definition)
                except DynamicApiError as exc:
                    self.fail_json(msg='Failed to retrieve requested object: {0}'.format(exc.body),
                                   error=exc.status, status=exc.status, reason=exc.reason)

            try:
                existing = resource.get(name=name, namespace=namespace).to_dict()
            except Exception:
                existing = None

            if existing:
                if resource.kind == 'DeploymentConfig':
                    if definition.get('spec', {}).get('triggers'):
                        definition = self.resolve_imagestream_triggers(existing, definition)
                elif existing['metadata'].get('annotations', {}).get(TRIGGER_ANNOTATION):
                    definition = self.resolve_imagestream_trigger_annotation(existing, definition)

        return super(OKDRawModule, self).perform_action(resource, definition)

    @staticmethod
    def get_index(desired, objects, keys):
        """ Iterates over keys, returns the first object from objects where the value of the key
            matches the value in desired
        """
        for i, item in enumerate(objects):
            if item and all([desired.get(key, True) == item.get(key, False) for key in keys]):
                return i

    def resolve_imagestream_trigger_annotation(self, existing, definition):

        def get_from_fields(d, fields):
            try:
                return reduce(operator.getitem, fields, d)
            except Exception:
                return None

        def set_from_fields(d, fields, value):
            get_from_fields(d, fields[:-1])[fields[-1]] = value

        if TRIGGER_ANNOTATION in definition['metadata'].get('annotations', {}).keys():
            triggers = yaml.safe_load(definition['metadata']['annotations'][TRIGGER_ANNOTATION] or '[]')
        else:
            triggers = yaml.safe_load(existing['metadata'].get('annotations', '{}').get(TRIGGER_ANNOTATION, '[]'))

        if not isinstance(triggers, list):
            return definition

        for trigger in triggers:
            if trigger.get('fieldPath'):
                parsed = self.parse_trigger_fieldpath(trigger['fieldPath'])
                path = parsed.get('path', '').split('.')
                if path:
                    existing_containers = get_from_fields(existing, path)
                    new_containers = get_from_fields(definition, path)
                    if parsed.get('name'):
                        existing_index = self.get_index({'name': parsed['name']}, existing_containers, ['name'])
                        new_index = self.get_index({'name': parsed['name']}, new_containers, ['name'])
                    elif parsed.get('index') is not None:
                        existing_index = new_index = int(parsed['index'])
                    else:
                        existing_index = new_index = None
                    if existing_index is not None and new_index is not None:
                        if existing_index < len(existing_containers) and new_index < len(new_containers):
                            set_from_fields(definition, path + [new_index, 'image'], get_from_fields(existing, path + [existing_index, 'image']))
        return definition

    def resolve_imagestream_triggers(self, existing, definition):

        existing_triggers = existing.get('spec', {}).get('triggers')
        new_triggers = definition['spec']['triggers']
        existing_containers = existing.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [])
        new_containers = definition.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [])
        for i, trigger in enumerate(new_triggers):
            if trigger.get('type') == 'ImageChange' and trigger.get('imageChangeParams'):
                names = trigger['imageChangeParams'].get('containerNames', [])
                for name in names:
                    old_container_index = self.get_index({'name': name}, existing_containers, ['name'])
                    new_container_index = self.get_index({'name': name}, new_containers, ['name'])
                    if old_container_index is not None and new_container_index is not None:
                        image = existing['spec']['template']['spec']['containers'][old_container_index]['image']
                        definition['spec']['template']['spec']['containers'][new_container_index]['image'] = image

                    existing_index = self.get_index(trigger['imageChangeParams'],
                                                    [x.get('imageChangeParams') for x in existing_triggers],
                                                    ['containerNames'])
                    if existing_index is not None:
                        existing_image = existing_triggers[existing_index].get('imageChangeParams', {}).get('lastTriggeredImage')
                        if existing_image:
                            definition['spec']['triggers'][i]['imageChangeParams']['lastTriggeredImage'] = existing_image
                        existing_from = existing_triggers[existing_index].get('imageChangeParams', {}).get('from', {})
                        new_from = trigger['imageChangeParams'].get('from', {})
                        existing_namespace = existing_from.get('namespace')
                        existing_name = existing_from.get('name', False)
                        new_name = new_from.get('name', True)
                        add_namespace = existing_namespace and 'namespace' not in new_from.keys() and existing_name == new_name
                        if add_namespace:
                            definition['spec']['triggers'][i]['imageChangeParams']['from']['namespace'] = existing_from['namespace']

        return definition

    def parse_trigger_fieldpath(self, expression):
        parsed = TRIGGER_CONTAINER.search(expression).groupdict()
        if parsed.get('index'):
            parsed['index'] = int(parsed['index'])
        return parsed

    def create_project_request(self, definition):
        definition['kind'] = 'ProjectRequest'
        result = {'changed': False, 'result': {}}
        resource = self.find_resource('ProjectRequest', definition['apiVersion'], fail=True)
        if not self.check_mode:
            try:
                k8s_obj = resource.create(definition)
                result['result'] = k8s_obj.to_dict()
            except DynamicApiError as exc:
                self.fail_json(msg="Failed to create object: {0}".format(exc.body),
                               error=exc.status, status=exc.status, reason=exc.reason)
        result['changed'] = True
        result['method'] = 'create'
        return result


def main():
    OKDRawModule().execute_module()


if __name__ == '__main__':
    main()
