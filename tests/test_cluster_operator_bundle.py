import asyncio
import filecmp
import logging
import os
from functools import partial

import pytest
import yaml

from rabbitmq_olm_package_repo import (
    create_cluster_operator_bundle,
    get_operator_last_tag,
    main,
)

from .utils import validate_bundle_struct

logger = logging.getLogger(__name__)


def test_cluster_operator_bundle():

    operator_release_file = (
        "./rabbitmq_olm_package_repo/manifests_crds/cluster-operator.yaml"
    )
    version = "2.8.0"
    output_directory = "./tests/test-bundle"

    cluster_operator_release_file = "./rabbitmq_olm_package_repo/generators/cluster_operator_generators/cluster-operator.yaml"
    os.system("cp " + operator_release_file + " " + cluster_operator_release_file)
    os.system("echo --- >> " + cluster_operator_release_file)

    os.system("mkdir -p ./rabbitmq_olm_package_repo/overlays")
    os.system("mkdir -p ./rabbitmq_olm_package_repo/tmpmanifests")

    create_cluster_operator_bundle(
        cluster_operator_release_file, version, output_directory
    )

    validate_bundle_struct(output_directory + "/" + version)
    validate_operator_crd(output_directory + "/" + version)
    validate_operator_manifest(output_directory + "/" + version, version)

    os.system("rm -fR ./rabbitmq_olm_package_repo/overlays")
    os.system("rm -fR ./rabbitmq_olm_package_repo/tmpmanifests")
    os.system("rm -fR " + output_directory)
    os.system("rm  " + cluster_operator_release_file)


# Check at least that the crd has been generated and two main fields (kind and metadata->name are created)
def validate_operator_crd(output_directory):

    # check if crd is present in the bundle
    assert os.path.isfile(output_directory + "/manifests/crds.yaml")

    with open(output_directory + "/manifests/crds.yaml") as stream:
        try:
            crd = yaml.safe_load(stream)
            assert crd["kind"] == "CustomResourceDefinition"
            assert crd["metadata"]["name"] == "rabbitmqclusters.rabbitmq.com"
        except yaml.YAMLError as exc:
            logger.error("Error parsing crd")


# Check at least that the crd has been generated and two main fields (kind and metadata->name are created)
def validate_operator_manifest(output_directory, version):

    # check if crd is present in the bundle
    assert os.path.isfile(
        output_directory + "/manifests/rabbitmq.clusterserviceversion.yaml"
    )

    replaces = get_operator_last_tag("cluster-operator")

    with open(
        output_directory + "/manifests/rabbitmq.clusterserviceversion.yaml"
    ) as stream:
        try:
            manifest = yaml.safe_load(stream)
            assert manifest["kind"] == "ClusterServiceVersion"
            assert (
                manifest["metadata"]["name"] == "rabbitmq-cluster-operator.v" + version
            )

            assert manifest["spec"]["replaces"] == replaces

            # Check field we overlayed
            assert (
                manifest["spec"]["install"]["spec"]["deployments"][0]["name"]
                == "rabbitmq-cluster-operator"
            )
            assert (
                manifest["spec"]["install"]["spec"]["permissions"][0][
                    "serviceAccountName"
                ]
                == "rabbitmq-cluster-operator"
            )
            assert (
                manifest["spec"]["install"]["spec"]["clusterPermissions"][0][
                    "serviceAccountName"
                ]
                == "rabbitmq-cluster-operator"
            )
        except yaml.YAMLError as exc:
            logger.error("Error parsing rabbitmq.clusterserviceversion file")
