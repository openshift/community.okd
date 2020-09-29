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
      - TLS certificate configuration for the newly created route.
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
      - allow
      - disable
      - redirect
    default: disable
  termination:
    description:
      - The termination type of the Route.
    choices:
      - edge
      - passthrough
      - reencrypt
    default: edge
'''

EXAMPLES = r'''
- name: Create hello-world deployment
  community.okd.k8s:
    definition:
      apiVersion: apps/v1
      kind: Deployment
      metadata:
        name: hello-kubernetes
        namespace: default
      spec:
        replicas: 3
        selector:
          matchLabels:
            app: hello-kubernetes
        template:
          metadata:
            labels:
              app: hello-kubernetes
          spec:
            containers:
            - name: hello-kubernetes
              image: paulbouwer/hello-kubernetes:1.8
              ports:
              - containerPort: 8080

- name: Create Service for the hello-world deployment
  community.okd.k8s:
    definition:
      apiVersion: v1
      kind: Service
      metadata:
        name: hello-kubernetes
        namespace: default
      spec:
        ports:
        - port: 80
          targetPort: 8080
        selector:
          app: hello-kubernetes

- name: Expose the insecure hello-world service externally
  community.okd.openshift_expose:
    service: hello-kubernetes
    namespace: default
    insecure_policy: allow
    termination: edge
  register: route
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
     duration:
       description: elapsed time of task in seconds
       returned: when C(wait) is true
       type: int
       sample: 48
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
        ))
        spec['insecure_policy'] = dict(type='str', choices=['Allow', 'Disable', 'Redirect'], default='Disable')
        spec['termination'] = dict(choices=['Edge', 'Passthrough', 'Reencrypt'], default='Edge')

        return spec

    def execute_module(self):
        self.client = self.get_api_client()
        v1_services = self.find_resource('Service', 'v1', fail=True)
        v1_routes = self.find_resource('Route', 'route.openshift.io/v1', fail=True)

        service_name = self.params['service']
        namespace = self.params['namespace']
        insecure_policy=self.params.get('insecure_policy', 'Disable').capitalize()
        termination_type = self.params.get('termination', 'Edge').capitalize()

        route_name = self.params.get('name') or  service_name
        labels = self.params.get('labels')
        hostname = self.params.get('hostname')
        path = self.params.get('path')
        wildcard_policy = self.params.get('wildcard_policy')
        port = self.params.get('port')

        if self.params.get('tls'):
            tls_ca_cert = self.params['tls'].get('ca_certificate')
            tls_cert = self.params['tls'].get('certificate')
            tls_dest_ca_cert = self.params['tls'].get('destination_ca_certificate')
            tls_key = self.params['tls'].get('key')
        else:
            tls_ca_cert = tls_cert = tls_dest_ca_cert = tls_key = None

        try:
            target_service = v1_services.get(name=service_name, namespace=namespace)
        except DynamicApiError as exc:
            self.fail_json(msg='Failed to retrieve service to be exposed: {0}'.format(exc.body),
                           error=exc.status, status=exc.status, reason=exc.reason)
        except Exception as exc:
            self.fail_json(msg='Failed to retrieve service to be exposed: {0}'.format(to_native(exc)),
                           error='', status='', reason='')


        route = {
            'apiVersion': 'route.openshift.io/v1',
            'kind': 'Route',
            'metadata': {
                'name': route_name,
                'namespace': namespace,
                'labels': labels,
            },
            'spec': {
                'tls': {
                    'insecureEdgeTerminationPolicy': insecure_policy,
                    'termination': termination_type,
                },
                'to': {
                    'kind': 'Service',
                    'name': service_name,
                },
                'wildcardPolicy': wildcard_policy
            }
        }

        # Want to conditionally add these so we don't overwrite what is automically added when nothing is provided
        if hostname:
            route['spec']['host'] = hostname
        if path:
            route['spec']['path'] = path
        if port:
            route['port'] = {
                'targetPort': port
            }
        if tls_ca_cert:
            route['tls']['caCertificate'] = tls_ca_cert
        if tls_cert:
            route['tls']['certificate'] = tls_cert
        if tls_dest_ca_cert:
            route['tls']['destinationCACertificate'] = tls_dest_ca_cert
        if tls_key:
            route['tls']['key'] = tls_key

        result = self.perform_action(v1_routes, route)

        self.module.exit_json(result=result)


def main():
    OpenShiftExpose().execute_module()


if __name__ == '__main__':
    main()
