#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re
import operator
from functools import reduce
import traceback
from ansible_collections.kubernetes.core.plugins.module_utils.common import (
    K8sAnsibleMixin,
    get_api_client,
)
from ansible.module_utils._text import to_native


try:
    from kubernetes.dynamic.exceptions import DynamicApiError, NotFoundError, ForbiddenError
    HAS_KUBERNETES_COLLECTION = True
except ImportError as e:
    HAS_KUBERNETES_COLLECTION = False
    k8s_collection_import_exception = e
    K8S_COLLECTION_ERROR = traceback.format_exc()


TRIGGER_ANNOTATION = 'image.openshift.io/triggers'
TRIGGER_CONTAINER = re.compile(r"(?P<path>.*)\[((?P<index>[0-9]+)|\?\(@\.name==[\"'\\]*(?P<name>[a-z0-9]([-a-z0-9]*[a-z0-9])?))")


class OKDRawModule(K8sAnsibleMixin):

    def __init__(self, module, k8s_kind=None, *args, **kwargs):
        self.module = module
        self.client = get_api_client(module=module)
        self.check_mode = self.module.check_mode
        self.params = self.module.params
        self.fail_json = self.module.fail_json
        self.fail = self.module.fail_json
        self.exit_json = self.module.exit_json

        super(OKDRawModule, self).__init__(module, *args, **kwargs)

        self.warnings = []

        self.kind = k8s_kind or self.params.get('kind')
        self.api_version = self.params.get('api_version')
        self.name = self.params.get('name')
        self.namespace = self.params.get('namespace')

        self.check_library_version()
        self.set_resource_definitions(module)

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
        # pylint: disable=use-a-generator
        # Use a generator instead 'all(desired.get(key, True) == item.get(key, False) for key in keys)'
        for i, item in enumerate(objects):
            if item and all([desired.get(key, True) == item.get(key, False) for key in keys]):
                return i

    def resolve_imagestream_trigger_annotation(self, existing, definition):
        import yaml

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
