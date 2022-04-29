#!/usr/bin/python

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

# STARTREMOVE (downstream)
DOCUMENTATION = r"""
module: openshift_adm_migrate_template_instances
short_description: Update TemplateInstances to point to the latest group-version-kinds
version_added: "2.2.0"
author: Alina Buzachis (@alinabuzachis)
description:
    - Update TemplateInstances to point to the latest group-version-kinds.
    - Analogous to C(oc adm migrate template-instances).
extends_documentation_fragment:
    - kubernetes.core.k8s_auth_options
    - kubernetes.core.k8s_wait_options
options:
    namespace:
        description:
            - The namespace that the template can be found in.
            - If no namespace if specified, migrate objects in all namespaces.
        type: str
requirements:
  - python >= 3.6
  - kubernetes >= 12.0.0
"""

EXAMPLES = r"""
  - name: Migrate TemplateInstances in namespace=test
    community.okd.openshift_adm_migrate_template_instances:
      namespace: test
    register: _result

  - name: Migrate TemplateInstances in all namespaces
    community.okd.openshift_adm_migrate_template_instances:
    register: _result
"""

RETURN = r"""
result:
    description:
        -  List with all TemplateInstances that have been migrated.
    type: list
    returned: success
    elements: dict
    sample: [
        {
            "apiVersion": "template.openshift.io/v1",
            "kind": "TemplateInstance",
            "metadata": {
                "creationTimestamp": "2021-11-10T11:12:09Z",
                "finalizers": [
                    "template.openshift.io/finalizer"
                ],
                "managedFields": [
                    {
                        "apiVersion": "template.openshift.io/v1",
                        "fieldsType": "FieldsV1",
                        "fieldsV1": {
                            "f:spec": {
                                "f:template": {
                                    "f:metadata": {
                                        "f:name": {}
                                    },
                                    "f:objects": {},
                                    "f:parameters": {}
                                }
                            }
                        },
                        "manager": "kubectl-create",
                        "operation": "Update",
                        "time": "2021-11-10T11:12:09Z"
                    },
                    {
                        "apiVersion": "template.openshift.io/v1",
                        "fieldsType": "FieldsV1",
                        "fieldsV1": {
                            "f:metadata": {
                                "f:finalizers": {
                                    ".": {},
                                    "v:\"template.openshift.io/finalizer\"": {}
                                }
                            },
                            "f:status": {
                                "f:conditions": {}
                            }
                        },
                        "manager": "openshift-controller-manager",
                        "operation": "Update",
                        "time": "2021-11-10T11:12:09Z"
                    },
                    {
                        "apiVersion": "template.openshift.io/v1",
                        "fieldsType": "FieldsV1",
                        "fieldsV1": {
                            "f:status": {
                                "f:objects": {}
                            }
                        },
                        "manager": "OpenAPI-Generator",
                        "operation": "Update",
                        "time": "2021-11-10T11:12:33Z"
                    }
                ],
                "name": "demo",
                "namespace": "test",
                "resourceVersion": "545370",
                "uid": "09b795d7-7f07-4d94-bf0f-2150ee66f88d"
            },
            "spec": {
                "requester": {
                    "groups": [
                        "system:masters",
                        "system:authenticated"
                    ],
                    "username": "system:admin"
                },
                "template": {
                    "metadata": {
                        "creationTimestamp": null,
                        "name": "template"
                    },
                    "objects": [
                        {
                            "apiVersion": "v1",
                            "kind": "Secret",
                            "metadata": {
                                "labels": {
                                    "foo": "bar"
                                },
                                "name": "secret"
                            }
                        },
                        {
                            "apiVersion": "apps/v1",
                            "kind": "Deployment",
                            "metadata": {
                                "name": "deployment"
                            },
                            "spec": {
                                "replicas": 0,
                                "selector": {
                                    "matchLabels": {
                                        "key": "value"
                                    }
                                },
                                "template": {
                                    "metadata": {
                                        "labels": {
                                            "key": "value"
                                        }
                                    },
                                    "spec": {
                                        "containers": [
                                            {
                                                "image": "k8s.gcr.io/e2e-test-images/agnhost:2.32",
                                                "name": "hello-openshift"
                                            }
                                        ]
                                    }
                                }
                            }
                        },
                        {
                            "apiVersion": "v1",
                            "kind": "Route",
                            "metadata": {
                                "name": "route"
                            },
                            "spec": {
                                "to": {
                                    "name": "foo"
                                }
                            }
                        }
                    ],
                    "parameters": [
                        {
                            "name": "NAME",
                            "value": "${NAME}"
                        }
                    ]
                }
            },
            "status": {
                "conditions": [
                    {
                        "lastTransitionTime": "2021-11-10T11:12:09Z",
                        "message": "",
                        "reason": "Created",
                        "status": "True",
                        "type": "Ready"
                    }
                ],
                "objects": [
                    {
                        "ref": {
                            "apiVersion": "v1",
                            "kind": "Secret",
                            "name": "secret",
                            "namespace": "test",
                            "uid": "33fad364-6d47-4f9c-9e51-92cba5602a57"
                        }
                    },
                    {
                        "ref": {
                            "apiVersion": "apps/v1",
                            "kind": "Deployment",
                            "name": "deployment",
                            "namespace": "test",
                            "uid": "3b527f88-42a1-4811-9e2f-baad4e4d8807"
                        }
                    },
                    {
                        "ref": {
                            "apiVersion": "route.openshift.io/v1.Route",
                            "kind": "Route",
                            "name": "route",
                            "namespace": "test",
                            "uid": "5b5411de-8769-4e27-ba52-6781630e4008"
                        }
                    }
                ]
            }
        },
        ...
    ]
"""
# ENDREMOVE (downstream)

import traceback

from ansible.module_utils._text import to_native

try:
    from kubernetes.dynamic.exceptions import DynamicApiError

    HAS_KUBERNETES_COLLECTION = True
except ImportError as e:
    HAS_KUBERNETES_COLLECTION = False
    k8s_collection_import_exception = e
    K8S_COLLECTION_ERROR = traceback.format_exc()

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.kubernetes.core.plugins.module_utils.args_common import (
    AUTH_ARG_SPEC,
    WAIT_ARG_SPEC,
)

from ansible_collections.kubernetes.core.plugins.module_utils.common import (
    K8sAnsibleMixin,
    get_api_client,
)


transforms = {
    "Build": "build.openshift.io/v1",
    "BuildConfig": "build.openshift.io/v1",
    "DeploymentConfig": "apps.openshift.io/v1",
    "Route": "route.openshift.io/v1",
}


class OpenShiftMigrateTemplateInstances(K8sAnsibleMixin):
    def __init__(self, module):
        self.module = module
        self.fail_json = self.module.fail_json
        self.exit_json = self.module.exit_json

        if not HAS_KUBERNETES_COLLECTION:
            self.module.fail_json(
                msg="The kubernetes.core collection must be installed",
                exception=K8S_COLLECTION_ERROR,
                error=to_native(k8s_collection_import_exception),
            )

        super(OpenShiftMigrateTemplateInstances, self).__init__(self.module)

        self.params = self.module.params
        self.check_mode = self.module.check_mode
        self.client = get_api_client(self.module)

    def patch_template_instance(self, resource, templateinstance):
        result = None

        try:
            result = resource.status.patch(templateinstance)
        except Exception as exc:
            self.module.fail_json(
                msg="Failed to migrate TemplateInstance {0} due to: {1}".format(
                    templateinstance["metadata"]["name"], to_native(exc)
                )
            )

        return result.to_dict()

    @staticmethod
    def perform_migrations(templateinstances):
        ti_list = []
        ti_to_be_migrated = []

        ti_list = (
            templateinstances.get("kind") == "TemplateInstanceList"
            and templateinstances.get("items")
            or [templateinstances]
        )

        for ti_elem in ti_list:
            objects = ti_elem["status"].get("objects")
            if objects:
                for i, obj in enumerate(objects):
                    object_type = obj["ref"]["kind"]
                    if (
                        object_type in transforms.keys()
                        and obj["ref"].get("apiVersion") != transforms[object_type]
                    ):
                        ti_elem["status"]["objects"][i]["ref"][
                            "apiVersion"
                        ] = transforms[object_type]
                        ti_to_be_migrated.append(ti_elem)

        return ti_to_be_migrated

    def execute_module(self):
        templateinstances = None
        namespace = self.params.get("namespace")
        results = {"changed": False, "result": []}

        resource = self.find_resource(
            "templateinstances", "template.openshift.io/v1", fail=True
        )

        if namespace:
            # Get TemplateInstances from a provided namespace
            try:
                templateinstances = resource.get(namespace=namespace).to_dict()
            except DynamicApiError as exc:
                self.fail_json(
                    msg="Failed to retrieve TemplateInstances in namespace '{0}': {1}".format(
                        namespace, exc.body
                    ),
                    error=exc.status,
                    status=exc.status,
                    reason=exc.reason,
                )
            except Exception as exc:
                self.module.fail_json(
                    msg="Failed to retrieve TemplateInstances in namespace '{0}': {1}".format(
                        namespace, to_native(exc)
                    ),
                    error="",
                    status="",
                    reason="",
                )
        else:
            # Get TemplateInstances from all namespaces
            templateinstances = resource.get().to_dict()

            ti_to_be_migrated = self.perform_migrations(templateinstances)

            if ti_to_be_migrated:
                if self.check_mode:
                    self.module.exit_json(
                        **{"changed": True, "result": ti_to_be_migrated}
                    )
                else:
                    for ti_elem in ti_to_be_migrated:
                        results["result"].append(
                            self.patch_template_instance(resource, ti_elem)
                        )
                    results["changed"] = True

        self.module.exit_json(**results)


def argspec():
    argument_spec = {}
    argument_spec.update(AUTH_ARG_SPEC)
    argument_spec.update(WAIT_ARG_SPEC)
    argument_spec["namespace"] = dict(type="str")

    return argument_spec


def main():
    argument_spec = argspec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    openshift_process = OpenShiftMigrateTemplateInstances(module)
    openshift_process.argspec = argument_spec
    openshift_process.execute_module()


if __name__ == "__main__":
    main()
