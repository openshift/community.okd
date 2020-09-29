#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r'''
module: openshift_expose

short_description: Expose a Service as an OpenShift Route.

version_added: "1.1.0"

author: "Fabian von Feilitzsch (@fabianvf)"

description:
  - Looks up a Service and creates a new Route based on it.
  - Analogous to `oc expose` for creating Routes, but does not support creating Services.
  - For creating Services from other resources, see community.kubernetes.k8s_expose

extends_documentation_fragment:
  - community.kubernetes.k8s_auth_options
  - community.kubernetes.k8s_wait_options

requirements:
  - "python >= 2.7"
  - "openshift >= 0.11.0"
  - "PyYAML >= 3.11"

options:
  service:
    description:
      - The name of the service to expose.
    type: str
    required: yes
    aliases: ['svc']
  namespace:
    description:
      - The namespace of the resource being targeted.
      - The Route will be created in this namespace as well.
    required: yes
    type: str
  labels:
    description:
      - Specify the labels to apply to the created Route.
      - 'A set of key: value pairs.'
    type: dict
  name:
    description:
      - The desired name of the Route to be created.
      - Defaults to the value of I(service)
    type: str
  hostname:
    description:
      - The hostname for the Route.
    type: str
  path:
    description:
      - The path for the Route
    type: str
  wildcard_policy:
    description:
      - The wildcard policy for the hostname.
    choices:
      - None
      - Subdomain
    default: None
    type: str
  port:
    description:
      - Name or number of the port the Route will route traffic to.
    type: str
  tls:
    description:
      - TLS configuration for the newly created route.
    type: object
    contains:
      ca_certificate:
        description:
          - Path to a CA certificate file on the target host.
        type: str
      certificate:
        description:
          - Path to a certificate file on the target host.
        type: str
      destination_ca_certificate:
        description:
          - Path to a CA certificate file used for securing the connection.
          - Defaults to the Service CA
        type: str
      key:
        description:
          - Path to a key file on the target host.
        type: str
      insecure_policy:
        description:
          - Sets the InsecureEdgeTerminationPolicy for the Route.
        type: str
        choices:
          - Allow
          - Disable
          - Redirect
        default: Disable
      termination:
        description:
          - The termination type of the Route.
        choices:
          - Edge
          - Passthrough
          - Reencrypt
        default: Edge
'''

EXAMPLES = r'''
- name: Create a Service for an nginx deployment that connects port 80 to port 8000 in the container
  community.okd.openshift_expose:
    deployment: nginx
    namespace: default
    port: '80'
    target_port: '8000'
  register: nginx_service

- name: Create a second service based on the above service, that connects port 443 to port 8443 in the container
  community.okd.openshift_expose:
    service: '{{ nginx_service.result.metadata.name }}'
    namespace: default
    port: '443'
    target_port: '8443'
    name: nginx-https

- name: Create a service for a pod
  community.okd.openshift_expose:
    pod: hello-world
    namespace: default
    name: hello-world
'''

RETURN = r'''
result:
  description:
  - The Route object that was created or updated
  returned: success
  type: complex
  contains:
    metadata:
      type: complex
    spec:
      type: complex
    status:
      type: complex
'''

import copy

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.kubernetes.plugins.module_utils.common import (
    K8sAnsibleMixin, AUTH_ARG_SPEC, WAIT_ARG_SPEC
)


class OpenShiftExpose(K8sAnsibleMixin):

    def __init__(self):
        self.module = AnsibleModule(
            argument_spec=self.argspec,
            supports_check_mode=True,
        )
        self.params = self.module.params
        self.fail_json = self.module.fail_json
        super(OpenShiftExpose, self).__init__()

    @property
    def argspec(self):
        spec = copy.deepcopy(AUTH_ARG_SPEC)
        spec.update(copy.deepcopy(WAIT_ARG_SPEC))

        spec['service'] = dict(type='str', required=True, aliases=['svc'])
        spec['namespace'] = dict(required=True, type='str')
        spec['labels'] = dict(type='dict')
        spec['name'] = dict(type='str')
        spec['hostname'] = dict(type='str')
        spec['path'] = dict(type='str')
        spec['wildcard_policy'] = dict(choices=['None', 'Subdomain'], default=None, type='str')
        spec['port'] = dict(type='str')
        spec['tls'] = dict(type='object', contains=dict(
            ca_certificate=dict(type='str'),
            certificate=dict(type='str'),
            destination_ca_certificate=dict(type='str'),
            key=dict(type='str'),
            insecure_policy=dict(type='str', choices=['Allow', 'Disable', 'Redirect'], default='Disable'),
            termination=dict(choices=['Edge', 'Passthrough', 'Reencrypt'], default='Edge'),
        )
        return spec

    def execute_module(self):
        raise NotImplementedError


def main():
    OpenShiftExpose().execute_module()


if __name__ == '__main__':
    main()
