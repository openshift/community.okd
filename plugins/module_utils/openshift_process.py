#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import traceback

from ansible_collections.kubernetes.core.plugins.module_utils.common import (
    K8sAnsibleMixin,
    get_api_client,
)
from ansible.module_utils._text import to_native


try:
    from kubernetes.dynamic.exceptions import DynamicApiError, NotFoundError
    HAS_KUBERNETES_COLLECTION = True
except ImportError as e:
    HAS_KUBERNETES_COLLECTION = False
    k8s_collection_import_exception = e
    K8S_COLLECTION_ERROR = traceback.format_exc()

try:
    from kubernetes.dynamic.exceptions import DynamicApiError, NotFoundError
except ImportError:
    pass


class OpenShiftProcess(K8sAnsibleMixin):
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

        super(OpenShiftProcess, self).__init__(self.module)

        self.params = self.module.params
        self.check_mode = self.module.check_mode
        self.client = get_api_client(self.module)

    def execute_module(self):
        v1_templates = self.find_resource(
            "templates", "template.openshift.io/v1", fail=True
        )
        v1_processed_templates = self.find_resource(
            "processedtemplates", "template.openshift.io/v1", fail=True
        )

        name = self.params.get("name")
        namespace = self.params.get("namespace")
        namespace_target = self.params.get("namespace_target")
        definition = self.params.get("resource_definition")
        src = self.params.get("src")

        state = self.params.get("state")

        parameters = self.params.get("parameters") or {}
        parameter_file = self.params.get("parameter_file")

        if (name and definition) or (name and src) or (src and definition):
            self.fail_json("Only one of src, name, or definition may be provided")

        if name and not namespace:
            self.fail_json("namespace is required when name is set")

        template = None

        if src or definition:
            self.set_resource_definitions(self.module)
            if len(self.resource_definitions) < 1:
                self.fail_json(
                    "Unable to load a Template resource from src or resource_definition"
                )
            elif len(self.resource_definitions) > 1:
                self.fail_json(
                    "Multiple Template resources found in src or resource_definition, only one Template may be processed at a time"
                )
            template = self.resource_definitions[0]
            template_namespace = template.get("metadata", {}).get("namespace")
            namespace = template_namespace or namespace or namespace_target or "default"
        elif name and namespace:
            try:
                template = v1_templates.get(name=name, namespace=namespace).to_dict()
            except DynamicApiError as exc:
                self.fail_json(
                    msg="Failed to retrieve Template with name '{0}' in namespace '{1}': {2}".format(
                        name, namespace, exc.body
                    ),
                    error=exc.status,
                    status=exc.status,
                    reason=exc.reason,
                )
            except Exception as exc:
                self.module.fail_json(
                    msg="Failed to retrieve Template with name '{0}' in namespace '{1}': {2}".format(
                        name, namespace, to_native(exc)
                    ),
                    error="",
                    status="",
                    reason="",
                )
        else:
            self.fail_json(
                "One of resource_definition, src, or name and namespace must be provided"
            )

        if parameter_file:
            parameters = self.parse_dotenv_and_merge(parameters, parameter_file)

        for k, v in parameters.items():
            template = self.update_template_param(template, k, v)

        result = {"changed": False}

        try:
            response = v1_processed_templates.create(
                body=template, namespace=namespace
            ).to_dict()
        except DynamicApiError as exc:
            self.fail_json(
                msg="Server failed to render the Template: {0}".format(exc.body),
                error=exc.status,
                status=exc.status,
                reason=exc.reason,
            )
        except Exception as exc:
            self.module.fail_json(
                msg="Server failed to render the Template: {0}".format(to_native(exc)),
                error="",
                status="",
                reason="",
            )
        result["message"] = ""
        if "message" in response:
            result["message"] = response["message"]
        result["resources"] = response["objects"]

        if state != "rendered":
            self.resource_definitions = response["objects"]
            self.kind = self.api_version = self.name = None
            self.namespace = self.params.get("namespace_target")
            self.append_hash = False
            self.apply = False
            self.params["validate"] = None
            self.params["merge_type"] = None
            super(OpenShiftProcess, self).execute_module()

        self.module.exit_json(**result)

    def update_template_param(self, template, k, v):
        for i, param in enumerate(template["parameters"]):
            if param["name"] == k:
                template["parameters"][i]["value"] = v
                return template
        return template

    def parse_dotenv_and_merge(self, parameters, parameter_file):
        import re

        DOTENV_PARSER = re.compile(
            r"(?x)^(\s*(\#.*|\s*|(export\s+)?(?P<key>[A-z_][A-z0-9_.]*)=(?P<value>.+?)?)\s*)[\r\n]*$"
        )
        path = os.path.normpath(parameter_file)
        if not os.path.exists(path):
            self.fail(msg="Error accessing {0}. Does the file exist?".format(path))
        try:
            with open(path, "r") as f:
                multiline = ""
                for line in f.readlines():
                    line = line.strip()
                    if line.endswith("\\"):
                        multiline += " ".join(line.rsplit("\\", 1))
                        continue
                    if multiline:
                        line = multiline + line
                        multiline = ""
                    match = DOTENV_PARSER.search(line)
                    if not match:
                        continue
                    match = match.groupdict()
                    if match.get("key"):
                        if match["key"] in parameters:
                            self.fail_json(
                                msg="Duplicate value for '{0}' detected in parameter file".format(
                                    match["key"]
                                )
                            )
                        parameters[match["key"]] = match["value"]
        except IOError as exc:
            self.fail(msg="Error loading parameter file: {0}".format(exc))
        return parameters
