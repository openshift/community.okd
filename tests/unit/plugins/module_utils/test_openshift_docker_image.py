from __future__ import absolute_import, division, print_function

__metaclass__ = type


from ansible_collections.community.okd.plugins.module_utils.openshift_docker_image import (
    convert_storage_to_bytes,
    parse_docker_image_ref,
)
import pytest


def test_convert_storage_to_bytes():

    data = [
        ("1000", 1000),
        ("1000Ki", 1000 * 1024),
        ("890Ki", 890 * 1024),
        ("890Mi", 890 * 1024 * 1024),
        ("90Gi", 90 * 1024 * 1024 * 1024),
        ("192Ti", 192 * 1024 * 1024 * 1024 * 1024),
        ("452Pi", 452 * 1024 * 1024 * 1024 * 1024 * 1024),
        ("23Ei", 23 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024),
    ]

    for x in data:
        result = convert_storage_to_bytes(x[0])
        assert result == x[1]

    failed = "123ki"
    with pytest.raises(ValueError):
        convert_storage_to_bytes(failed)


def validate_docker_response(resp, **kwargs):
    assert isinstance(resp, dict)
    for key in ("hostname", "digest", "tag", "name", "namespace"):
        assert key in resp

    hostname = kwargs.get("hostname", "docker.io")
    assert resp["hostname"] == hostname

    namespace = kwargs.get("namespace")
    assert resp["namespace"] == namespace

    name = kwargs.get("name")
    assert resp["name"] == name

    digest = kwargs.get("digest")
    assert resp["digest"] == digest

    tag = kwargs.get("tag")
    assert resp["tag"] == tag


def test_parse_docker_image_ref_valid_image_with_digest():

    image = "registry.access.redhat.com/ubi8/dotnet-21@sha256:f7718f5efd3436e781ee4322c92ab0c4ae63e61f5b36f1473a57874cc3522669"
    response, err = parse_docker_image_ref(image)
    assert err is None

    validate_docker_response(response,
                             hostname="registry.access.redhat.com",
                             namespace="ubi8",
                             name="dotnet-21",
                             digest="sha256:f7718f5efd3436e781ee4322c92ab0c4ae63e61f5b36f1473a57874cc3522669")


def test_parse_docker_image_ref_valid_image_with_tag_latest():

    image = "registry.access.redhat.com/ubi8/dotnet-21:latest"
    response, err = parse_docker_image_ref(image)
    assert err is None

    validate_docker_response(response,
                             hostname="registry.access.redhat.com",
                             namespace="ubi8",
                             name="dotnet-21",
                             tag="latest")


def test_parse_docker_image_ref_valid_image_with_tag_int():

    image = "registry.access.redhat.com/ubi8/dotnet-21:0.0.1"
    response, err = parse_docker_image_ref(image)
    assert err is None

    validate_docker_response(response,
                             hostname="registry.access.redhat.com",
                             namespace="ubi8",
                             name="dotnet-21",
                             tag="0.0.1")


def test_parse_docker_image_ref_invalid_image():

    # The hex value of the sha256 is not valid
    image = "registry.access.redhat.com/dotnet-21@sha256:f7718f5efd3436e781ee4322c92ab0c4ae63e61f5b36f1473a57874cc3522"
    response, err = parse_docker_image_ref(image)
    assert err and err.startswith("Invalid length for digest hex")


def test_parse_docker_image_ref_valid_image_without_hostname():

    image = "ansible:2.10.0"
    response, err = parse_docker_image_ref(image)
    assert err is None

    validate_docker_response(response, name="ansible", tag="2.10.0")


def test_parse_docker_image_ref_valid_image_without_hostname_and_with_digest():

    image = "ansible@sha256:f7718f5efd3436e781ee4322c92ab0c4ae63e61f5b36f1473a57874cc3522669"
    response, err = parse_docker_image_ref(image)
    assert err is None

    validate_docker_response(response, name="ansible", digest="sha256:f7718f5efd3436e781ee4322c92ab0c4ae63e61f5b36f1473a57874cc3522669")


def test_parse_docker_image_ref_valid_image_with_name_only():

    image = "ansible"
    response, err = parse_docker_image_ref(image)
    assert err is None

    validate_docker_response(response, name="ansible")


def test_parse_docker_image_ref_valid_image_without_hostname_with_namespace_and_name():

    image = "ibmcom/pause@sha256:fcaff905397ba63fd376d0c3019f1f1cb6e7506131389edbcb3d22719f1ae54d"
    response, err = parse_docker_image_ref(image)
    assert err is None

    validate_docker_response(response,
                             name="pause",
                             namespace="ibmcom",
                             digest="sha256:fcaff905397ba63fd376d0c3019f1f1cb6e7506131389edbcb3d22719f1ae54d")


def test_parse_docker_image_ref_valid_image_with_complex_namespace_name():

    image = "registry.redhat.io/jboss-webserver-5/webserver54-openjdk11-tomcat9-openshift-rhel7:1.0"
    response, err = parse_docker_image_ref(image)
    assert err is None

    validate_docker_response(response,
                             hostname="registry.redhat.io",
                             name="webserver54-openjdk11-tomcat9-openshift-rhel7",
                             namespace="jboss-webserver-5",
                             tag="1.0")
