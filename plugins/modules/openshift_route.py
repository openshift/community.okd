#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r'''
module: openshift_route

short_description: Expose a Service as an OpenShift Route.

version_added: "1.1.0"

author: "Fabian von Feilitzsch (@fabianvf)"

description:
  - Looks up a Service and creates a new Route based on it.
  - Analogous to `oc expose` and `oc create route` for creating Routes, but does not support creating Services.
  - For creating Services from other resources, see community.kubernetes.k8s_expose

extends_documentation_fragment:
  - community.kubernetes.k8s_auth_options
  - community.kubernetes.k8s_wait_options
  - community.kubernetes.k8s_state_options

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
      - Currently only Subdomain is supported.
      - If not provided, the default of None will be used.
    choices:
      - Subdomain
    type: str
  port:
    description:
      - Name or number of the port the Route will route traffic to.
    type: str
  tls:
    description:
      - TLS configuration for the newly created route.
      - Only used when I(termination) is set.
    type: dict
    suboptions:
      ca_certificate:
        description:
          - Path to a CA certificate file on the target host.
          - Not supported when I(termination) is set to passthrough.
        type: str
      certificate:
        description:
          - Path to a certificate file on the target host.
          - Not supported when I(termination) is set to passthrough.
        type: str
      destination_ca_certificate:
        description:
          - Path to a CA certificate file used for securing the connection.
          - Only used when I(termination) is set to reencrypt.
          - Defaults to the Service CA.
        type: str
      key:
        description:
          - Path to a key file on the target host.
          - Not supported when I(termination) is set to passthrough.
        type: str
      insecure_policy:
        description:
          - Sets the InsecureEdgeTerminationPolicy for the Route.
          - Not supported when I(termination) is set to reencrypt.
          - When I(termination) is set to passthrough, only redirect is supported.
          - If not provided, insecure traffic will be disallowed.
        type: str
        choices:
          - allow
          - redirect
  termination:
    description:
      - The termination type of the Route.
      - If left empty no termination type will be set, and the route will be insecure.
    choices:
      - edge
      - passthrough
      - reencrypt
    type: str
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
  community.okd.openshift_route:
    service: hello-kubernetes
    namespace: default
    insecure_policy: allow
  register: route
'''

RETURN = r'''
result:
  description:
    - The Route object that was created or updated. Will be empty in the case of deletion.
  returned: success
  type: complex
  contains:
    apiVersion:
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
      description: Specification for the Route
      returned: success
      type: complex
    status:
      description: Current status details for the Route
      returned: success
      type: complex
duration:
  description: elapsed time of task in seconds
  returned: when C(wait) is true
  type: int
  sample: 48
'''

import copy
import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native

try:
    from ansible_collections.community.kubernetes.plugins.module_utils.common import (
        K8sAnsibleMixin, AUTH_ARG_SPEC, WAIT_ARG_SPEC, COMMON_ARG_SPEC
    )
    HAS_KUBERNETES_COLLECTION = True
except ImportError as e:
    HAS_KUBERNETES_COLLECTION = False
    k8s_collection_import_exception = e
    K8S_COLLECTION_ERROR = traceback.format_exc()
    K8sAnsibleMixin = object

try:
    from openshift.dynamic.exceptions import DynamicApiError, NotFoundError
except ImportError:
    pass


class OpenShiftRoute(K8sAnsibleMixin):

    def __init__(self):
        self.module = AnsibleModule(
            argument_spec=self.argspec,
            supports_check_mode=True,
        )

        if not HAS_KUBERNETES_COLLECTION:
            self.module.fail_json(
                msg="The community.kubernetes collection must be installed",
                exception=K8S_COLLECTION_ERROR,
                error=to_native(k8s_collection_import_exception)
            )
        super(OpenShiftRoute, self).__init__()

        self.params = self.module.params
        # TODO: should probably make it so that at least some of these aren't required for perform_action to work
        # Or at least explicitly pass them in
        self.append_hash = False
        self.apply = False
        self.check_mode = self.module.check_mode
        self.warnings = []
        self.params['merge_type'] = None

    @property
    def argspec(self):
        spec = copy.deepcopy(AUTH_ARG_SPEC)
        spec.update(copy.deepcopy(WAIT_ARG_SPEC))
        spec.update(copy.deepcopy(COMMON_ARG_SPEC))

        spec['service'] = dict(type='str', required=True, aliases=['svc'])
        spec['namespace'] = dict(required=True, type='str')
        spec['labels'] = dict(type='dict')
        spec['name'] = dict(type='str')
        spec['hostname'] = dict(type='str')
        spec['path'] = dict(type='str')
        spec['wildcard_policy'] = dict(choices=['Subdomain'], type='str')
        spec['port'] = dict(type='str')
        spec['tls'] = dict(type='dict', contains=dict(
            ca_certificate=dict(type='str'),
            certificate=dict(type='str'),
            destination_ca_certificate=dict(type='str'),
            key=dict(type='str'),
            insecure_policy=dict(type='str', choices=['allow', 'redirect']),
        ))
        spec['termination'] = dict(choices=['edge', 'passthrough', 'reencrypt'])

        return spec

    def execute_module(self):
        self.client = self.get_api_client()
        v1_services = self.find_resource('Service', 'v1', fail=True)
        v1_routes = self.find_resource('Route', 'route.openshift.io/v1', fail=True)

        service_name = self.params['service']
        namespace = self.params['namespace']
        termination_type = self.params.get('termination')
        state = self.params.get('state')

        # We need to do something a little wonky to wait if the user doesn't supply a custom condition
        custom_wait = self.params.get('wait') and not self.params.get('wait_condition') and state != 'absent'
        if custom_wait:
            # Don't use default wait logic in perform_action
            self.params['wait'] = False

        route_name = self.params.get('name') or service_name
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
            tls_insecure_policy = self.params['tls'].get('insecure_policy')
        else:
            tls_ca_cert = tls_cert = tls_dest_ca_cert = tls_key = tls_insecure_policy = None

        try:
            target_service = v1_services.get(name=service_name, namespace=namespace)
        except NotFoundError:
            if not port:
                self.module.fail_json(msg="You need to provide the 'port' argument when exposing a non-existent service")
            target_service = None
        except DynamicApiError as exc:
            self.module.fail_json(msg='Failed to retrieve service to be exposed: {0}'.format(exc.body),
                           error=exc.status, status=exc.status, reason=exc.reason)
        except Exception as exc:
            self.module.fail_json(msg='Failed to retrieve service to be exposed: {0}'.format(to_native(exc)),
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
                'tls': {},
                'to': {
                    'kind': 'Service',
                    'name': service_name,
                },
                'port': {
                    'targetPort': self.set_port(target_service, port),
                },
                'wildcardPolicy': wildcard_policy
            }
        }

        # Want to conditionally add these so we don't overwrite what is automically added when nothing is provided
        if termination_type:
            route['spec']['tls'] = dict(termination=termination_type.capitalize())
            if tls_insecure_policy:
                if termination_type == 'edge':
                    route['spec']['tls']['insecureEdgeTerminationPolicy'] = tls_insecure_policy.capitalize()
                elif termination_type == 'passthrough':
                    if tls_insecure_policy != 'redirect':
                        self.module.fail_json("'redirect' is the only supported insecureEdgeTerminationPolicy for passthrough routes")
                    route['spec']['tls']['insecureEdgeTerminationPolicy'] = tls_insecure_policy.capitalize()
                elif termination_type == 'reencrypt':
                    self.module.fail_json("'tls.insecure_policy' is not supported with reencrypt routes")
            else:
                route['spec']['tls']['insecureEdgeTerminationPolicy'] = None
            if tls_ca_cert:
                if termination_type == 'passthrough':
                    self.module.fail_json("'tls.ca_certificate' is not supported with passthrough routes")
                route['tls']['caCertificate'] = tls_ca_cert
            if tls_cert:
                if termination_type == 'passthrough':
                    self.module.fail_json("'tls.certificate' is not supported with passthrough routes")
                route['tls']['certificate'] = tls_cert
            if tls_key:
                if termination_type == 'passthrough':
                    self.module.fail_json("'tls.key' is not supported with passthrough routes")
                route['tls']['key'] = tls_key
            if tls_dest_ca_cert:
                if termination_type != 'reencrypt':
                    self.module.fail_json("'destination_certificate' is only valid for reencrypt routes")
                route['tls']['destinationCACertificate'] = tls_dest_ca_cert
        else:
            route['spec']['tls'] = None
        if hostname:
            route['spec']['host'] = hostname
        if path:
            route['spec']['path'] = path

        result = self.perform_action(v1_routes, route)
        timeout = self.params.get('wait_timeout')
        sleep = self.params.get('wait_sleep')
        if custom_wait:
            success, result['result'], result['duration'] = self._wait_for(v1_routes, route_name, namespace, wait_predicate, sleep, timeout, state)

        self.module.exit_json(**result)

    def set_port(self, service, port_arg):
        if port_arg:
            return port_arg
        for p in service.spec.ports:
            if p.protocol == 'TCP':
                if p.name is not None:
                    return p.name
                return p.targetPort
        return None


def wait_predicate(route):
    if not(route.status and route.status.ingress):
        return False
    for ingress in route.status.ingress:
        match = [x for x in ingress.conditions if x.type == 'Admitted']
        if not match:
            return False
        match = match[0]
        if match.status != "True":
            return False
    return True


def main():
    OpenShiftRoute().execute_module()


if __name__ == '__main__':
    main()
