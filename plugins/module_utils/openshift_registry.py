#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import traceback
import os
from urllib.parse import urlparse

from ansible.module_utils._text import to_native

try:
    from ansible_collections.kubernetes.core.plugins.module_utils.common import (
        K8sAnsibleMixin,
        get_api_client,
    )
    HAS_KUBERNETES_COLLECTION = True
except ImportError as e:
    HAS_KUBERNETES_COLLECTION = False
    k8s_collection_import_exception = e
    K8S_COLLECTION_ERROR = traceback.format_exc()

from ansible_collections.community.okd.plugins.module_utils.openshift_docker_image import (
    parse_docker_image_ref,
)

try:
    import requests
    from requests.auth import HTTPBasicAuth
    HAS_REQUESTS_MODULE = True
except ImportError as e:
    HAS_REQUESTS_MODULE = False
    requests_import_exception = e
    REQUESTS_MODULE_ERROR = traceback.format_exc()


def ping_docker_registry(url):
    if not HAS_REQUESTS_MODULE:
        return dict(
            reached=False,
            msg="This module requires the python 'requests' package. Try `pip install requests`.",
            error=requests_import_exception
        )

    try:

        host = urlparse(url)
        registry = url
        if len(host.scheme) == 0:
            registry = "https://" + url

        registry = os.path.join(registry, "v2") + "/"
        resp = requests.get(registry, verify=False)
        registry_version = resp.headers.get("docker-distribution-api-version")
        code = resp.status_code
        if not registry_version and not (code not in (401, 403) or (code >= 200 and code < 300)):
            return dict(
                reached=False,
                msg="Registry responded to v2 Docker endpoint, but has no header for Docker Distribution",
                error=resp.reason,
                status_code=resp.status_code
            )

        return dict(
            reached=True
        )

    except Exception as err:
        return dict(
            reached=False,
            msg="registry could not be contacted at %s: %s" % (url, err)
        )


class OpenShiftRegistry(K8sAnsibleMixin):
    def __init__(self, module):
        self.module = module
        self.fail_json = self.module.fail_json
        self.exit_json = self.module.exit_json

        if not HAS_KUBERNETES_COLLECTION:
            self.fail_json(
                msg="The kubernetes.core collection must be installed",
                exception=K8S_COLLECTION_ERROR,
                error=to_native(k8s_collection_import_exception),
            )

        super(OpenShiftRegistry, self).__init__(self.module)

        self.params = self.module.params
        self.check_mode = self.module.check_mode
        self.client = get_api_client(self.module)

        self.check = self.params.get("check")

    def list_image_streams(self, namespace=None):
        kind = "ImageStream"
        api_version = "image.openshift.io/v1"

        params = dict(
            kind=kind,
            api_version=api_version,
            namespace=namespace
        )
        result = self.kubernetes_facts(**params)
        imagestream = []
        if len(result["resources"]) > 0:
            imagestream = result["resources"]
        return imagestream

    def find_registry_info(self):

        def _determine_registry(image_stream):
            public, internal = None, None
            docker_repo = image_stream["status"].get("publicDockerImageRepository")
            if docker_repo:
                ref, err = parse_docker_image_ref(docker_repo, self.module)
                public = ref["hostname"]

            docker_repo = image_stream["status"].get("dockerImageRepository")
            if docker_repo:
                ref, err = parse_docker_image_ref(docker_repo, self.module)
                internal = ref["hostname"]
            return internal, public

        # Try to determine registry hosts from Image Stream from 'openshift' namespace
        for stream in self.list_image_streams(namespace="openshift"):
            internal, public = _determine_registry(stream)
            if not public and not internal:
                self.fail_json(msg="The integrated registry has not been configured")
            return internal, public

        # Unable to determine registry from 'openshift' namespace, trying with all namespace
        for stream in self.list_image_streams():
            internal, public = _determine_registry(stream)
            if not public and not internal:
                self.fail_json(msg="The integrated registry has not been configured")
            return internal, public

        self.fail_json(msg="No Image Streams could be located to retrieve registry info.")

    def info(self):
        result = {}
        result["internal_hostname"], result["public_hostname"] = self.find_registry_info()

        if self.check:
            public_registry = result["public_hostname"]
            if not public_registry:
                result["check"] = dict(
                    reached=False,
                    msg="Registry does not have a public hostname."
                )
            else:
                result["check"] = ping_docker_registry(public_registry)

        self.exit_json(**result)
