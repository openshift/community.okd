#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r'''
module: openshift_process

short_description: Process an OpenShift template.openshift.io/v1 Template

version_added: "1.1.0"

author: "Fabian von Feilitzsch (@fabianvf)"

description:
  - Processes a specified OpenShift template with the provided template.
  - Templates can be provided inline, from a file, or specified by name and namespace in the cluster.
  - Analogous to `oc process`.
  - For CRUD operations on Template resources themselves, see the community.okd.k8s module.

extends_documentation_fragment:
  - community.kubernetes.k8s_auth_options
  - community.kubernetes.k8s_wait_options
  - community.kubernetes.k8s_state_options
  - community.kubernetes.k8s_resource_options

requirements:
  - "python >= 2.7"
  - "openshift >= 0.11.0"
  - "PyYAML >= 3.11"

options:
  name:
    description:
      - The name of the Template to process.
      - The Template must be present in the cluster.
      - When provided, I(namespace) is required.
      - Mutually exlusive with I(resource_definition) or I(src)
    type: str
  namespace:
    description:
      - The namespace that the template can be found in.
    type: str
  parameters:
    description:
      - 'A set of key: value pairs that will be used to set/override values in the Template.'
      - Corresponds to the `--param` argument to oc process.
    type: dict
  parameter_file:
    description:
      - A path to a file containing template parameter values to override/set values in the Template.
      - Corresponds to the `--param-file` argument to oc process.
    type: str
'''

EXAMPLES = r'''
'''

RETURN = r'''
'''

import re
import os
import copy
import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native

try:
    from ansible_collections.community.kubernetes.plugins.module_utils.common import (
        K8sAnsibleMixin, AUTH_ARG_SPEC, WAIT_ARG_SPEC, COMMON_ARG_SPEC, RESOURCE_ARG_SPEC
    )
    HAS_KUBERNETES_COLLECTION = True
except ImportError as e:
    HAS_KUBERNETES_COLLECTION = False
    k8s_collection_import_exception = e
    K8S_COLLECTION_ERROR = traceback.format_exc()
    K8sAnsibleMixin = object
    AUTH_ARG_SPEC = WAIT_ARG_SPEC = COMMON_ARG_SPEC = RESOURCE_ARG_SPEC = {}

try:
    from openshift.dynamic.exceptions import DynamicApiError, NotFoundError
except ImportError:
    pass

DOTENV_PARSER = re.compile(r"(?x)^(\s*(\#.*|\s*|(export\s+)?(?P<key>[A-z_][A-z0-9_.]*)=(?P<value>.+?)?)\s*)[\r\n]*$")


class OpenShiftProcess(K8sAnsibleMixin):

    def __init__(self):
        self.module = AnsibleModule(
            argument_spec=self.argspec,
            supports_check_mode=True,
        )
        self.fail_json = self.module.fail_json

        if not HAS_KUBERNETES_COLLECTION:
            self.module.fail_json(
                msg="The community.kubernetes collection must be installed",
                exception=K8S_COLLECTION_ERROR,
                error=to_native(k8s_collection_import_exception)
            )

        super(OpenShiftProcess, self).__init__()

        self.params = self.module.params
        self.check_mode = self.module.check_mode

    @property
    def argspec(self):
        spec = copy.deepcopy(AUTH_ARG_SPEC)
        spec.update(copy.deepcopy(WAIT_ARG_SPEC))
        spec.update(copy.deepcopy(COMMON_ARG_SPEC))
        spec.update(copy.deepcopy(RESOURCE_ARG_SPEC))

        spec['namespace'] = dict(type='str')
        spec['parameters'] = dict(type='dict')
        spec['name'] = dict(type='str')
        spec['parameter_file'] = dict(type='str')

        return spec

    def execute_module(self):
        self.client = self.get_api_client()

        v1_templates = self.find_resource('templates', 'template.openshift.io/v1', fail=True)
        v1_processed_templates = self.find_resource('processedtemplates', 'template.openshift.io/v1', fail=True)

        name = self.params.get('name')
        namespace = self.params.get('namespace')
        definition = self.params.get('resource_definition')
        src = self.params.get('src')

        state = self.params.get('state')

        parameters = self.params.get('parameters', {})
        parameter_file = self.params.get('parameter_file')

        if (name and definition) or (name and src) or (src and definition):
            self.fail_json("Only one of src, name, or definition may be provided")

        if name and not namespace:
            self.fail_json("namespace is required when name is set")

        template = None

        if src or definition:
            self.set_resource_definitions()
            if len(self.resource_definitions) < 1:
                self.fail_json('Unable to load a Template resource from src or resource_definition')
            elif len(self.resource_definitions) > 1:
                self.fail_json('Multiple Template resources found in src or resource_definition, only one Template may be processed at a time')
            template = self.resource_definitions[0]

        if name and namespace:
            try:
                template = v1_templates.get(name=name, namespace=namespace).to_dict()
            except DynamicApiError as exc:
                self.fail_json(msg="Failed to retrieve Template with name '{0}' in namespace '{1}': {2}".format(name, namespace, exc.body),
                               error=exc.status, status=exc.status, reason=exc.reason)
            except Exception as exc:
                self.module.fail_json(msg="Failed to retrieve Template with name '{0}' in namespace '{1}': {2}".format(name, namespace, to_native(exc)),
                                      error='', status='', reason='')
        elif not template:
            self.fail_json("One of resource_definition, src, or name and namespace must be provided")

        if parameter_file:
            parameters = self.parse_dotenv_and_merge(parameters, parameter_file)

        for k, v in parameters.items():
            template = self.update_template_params(template, k, v)

        result = {'changed': False}

        try:
            response = v1_processed_templates.create(body=template).to_dict()
        except DynamicApiError as exc:
            self.fail_json(msg="Server failed to render the Template: {0}".format(exc.body),
                           error=exc.status, status=exc.status, reason=exc.reason)
        except Exception as exc:
            self.module.fail_json(msg="Server failed to render the Template: {0}".format(to_native(exc)),
                                  error='', status='', reason='')

        result['message'] = response['message']
        result['objects'] = response['objects']

        self.module.exit_json(**result)

    def update_template_params(self, template, k, v):
        for i, param in enumerate(template['parameters']):
            if param['name'] == k:
                template['parameters'][i]['value'] = v
                return template
        return template

    def parse_dotenv_and_merge(self, parameters, parameter_file):
        path = os.path.normpath(parameter_file)
        if not os.path.exists(path):
            self.fail(msg="Error accessing {0}. Does the file exist?".format(path))
        try:
            with open(path, 'r') as f:
                for line in f.readlines():
                    match = DOTENV_PARSER.search(line).groupdict()
                    if match.get('key'):
                        if match['key'] in parameters:
                            self.fail_json(msg="Duplicate value for '{0}' detected in parameter file".format(match['key']))
                        parameters[match['key']] = match['value']
        except IOError as exc:
            self.fail(msg="Error loading parameter file: {0}".format(exc))
        return parameters


def main():
    OpenShiftProcess().execute_module()


if __name__ == '__main__':
    main()
