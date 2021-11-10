from __future__ import absolute_import, division, print_function

__metaclass__ = type


import pytest

from ansible_collections.community.okd.plugins.modules.openshift_adm_migrate_template_instances import (
    OpenShiftMigrateTemplateInstances,
)


testdata = [
    ("input", "output"),
    [
        (
            {
                "status": {
                    "objects": [
                        {"ref": {"kind": "DeploymentConfig", "apiVersion": "v1"}}
                    ]
                }
            },
            [
                {
                    "status": {
                        "objects": [
                            {
                                "ref": {
                                    "kind": "DeploymentConfig",
                                    "apiVersion": "apps.openshift.io/v1",
                                }
                            }
                        ]
                    }
                }
            ],
        ),
        (
            {"status": {"objects": [{"ref": {"kind": "DeploymentConfig"}}]}},
            [
                {
                    "status": {
                        "objects": [
                            {
                                "ref": {
                                    "kind": "DeploymentConfig",
                                    "apiVersion": "apps.openshift.io/v1",
                                }
                            }
                        ]
                    }
                }
            ],
        ),
        (
            {
                "status": {
                    "objects": [
                        {
                            "ref": {
                                "kind": "DeploymentConfig",
                                "apiVersion": "apps.openshift.io/v1",
                            }
                        }
                    ]
                }
            },
            [],
        ),
        (
            {
                "status": {
                    "objects": [{"ref": {"kind": "BuildConfig", "apiVersion": "v1"}}]
                }
            },
            [
                {
                    "status": {
                        "objects": [
                            {
                                "ref": {
                                    "kind": "BuildConfig",
                                    "apiVersion": "build.openshift.io/v1",
                                }
                            }
                        ]
                    }
                }
            ],
        ),
        (
            {"status": {"objects": [{"ref": {"kind": "BuildConfig"}}]}},
            [
                {
                    "status": {
                        "objects": [
                            {
                                "ref": {
                                    "kind": "BuildConfig",
                                    "apiVersion": "build.openshift.io/v1",
                                }
                            }
                        ]
                    }
                }
            ],
        ),
        (
            {
                "status": {
                    "objects": [
                        {
                            "ref": {
                                "kind": "BuildConfig",
                                "apiVersion": "build.openshift.io/v1",
                            }
                        }
                    ]
                }
            },
            [],
        ),
        (
            {"status": {"objects": [{"ref": {"kind": "Build", "apiVersion": "v1"}}]}},
            [
                {
                    "status": {
                        "objects": [
                            {
                                "ref": {
                                    "kind": "Build",
                                    "apiVersion": "build.openshift.io/v1",
                                }
                            }
                        ]
                    }
                }
            ],
        ),
        (
            {"status": {"objects": [{"ref": {"kind": "Build"}}]}},
            [
                {
                    "status": {
                        "objects": [
                            {
                                "ref": {
                                    "kind": "Build",
                                    "apiVersion": "build.openshift.io/v1",
                                }
                            }
                        ]
                    }
                }
            ],
        ),
        (
            {
                "status": {
                    "objects": [
                        {
                            "ref": {
                                "kind": "Build",
                                "apiVersion": "build.openshift.io/v1",
                            }
                        }
                    ]
                }
            },
            [],
        ),
        (
            {"status": {"objects": [{"ref": {"kind": "Route", "apiVersion": "v1"}}]}},
            [
                {
                    "status": {
                        "objects": [
                            {
                                "ref": {
                                    "kind": "Route",
                                    "apiVersion": "route.openshift.io/v1",
                                }
                            }
                        ]
                    }
                }
            ],
        ),
        (
            {"status": {"objects": [{"ref": {"kind": "Route"}}]}},
            [
                {
                    "status": {
                        "objects": [
                            {
                                "ref": {
                                    "kind": "Route",
                                    "apiVersion": "route.openshift.io/v1",
                                }
                            }
                        ]
                    }
                }
            ],
        ),
        (
            {
                "status": {
                    "objects": [
                        {
                            "ref": {
                                "kind": "Route",
                                "apiVersion": "route.openshift.io/v1",
                            }
                        }
                    ]
                }
            },
            [],
        ),
        (
            {
                "status": {
                    "objects": [{"ref": {"kind": "FakeKind", "apiVersion": "v1"}}]
                }
            },
            [],
        ),
    ],
]


@pytest.mark.parametrize(*testdata)
def test_templateinstance_migrations(input, output):
    assert OpenShiftMigrateTemplateInstances.perform_migrations(input) == output
