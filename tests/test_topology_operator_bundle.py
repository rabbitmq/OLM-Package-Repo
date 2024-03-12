import asyncio
import logging
import os
from functools import partial

import pytest
import yaml

from rabbitmq_olm_package_repo import (
    create_messaging_topology_operator_bundle,
    main,
)

from .utils import validate_bundle_struct


def test_cluster_operator_bundle():

    topology_operator_release_file = "./rabbitmq_olm_package_repo/manifests_crds_messaging_topology_operator/messaging-topology-operator-with-certmanager.yaml"
    version = "1.14.0"
    output_directory = "./tests/test-bundle"

    os.system("mkdir -p ./rabbitmq_olm_package_repo/overlays")
    os.system("mkdir -p ./rabbitmq_olm_package_repo/tmpmanifests")

    crds_names = [
        "bindings.rabbitmq.com",
        "exchanges.rabbitmq.com",
        "federations.rabbitmq.com",
        "permissions.rabbitmq.com",
        "policies.rabbitmq.com",
        "queues.rabbitmq.com",
        "schemareplications.rabbitmq.com",
        "shovels.rabbitmq.com",
        "superstreams.rabbitmq.com",
        "topicpermissions.rabbitmq.com",
        "users.rabbitmq.com",
        "vhosts.rabbitmq.com",
    ]
    crds_file_names = [
        "rabbitmq.com_bindings.yaml",
        "rabbitmq.com_exchanges.yaml",
        "rabbitmq.com_federations.yaml",
        "rabbitmq.com_permissions.yaml",
        "rabbitmq.com_policies.yaml",
        "rabbitmq.com_queues.yaml",
        "rabbitmq.com_schemareplications.yaml",
        "rabbitmq.com_shovels.yaml",
        "rabbitmq.com_superstreams.yaml",
        "rabbitmq.com_topicpermissions.yaml",
        "rabbitmq.com_users.yaml",
        "rabbitmq.com_vhosts.yaml",
    ]

    create_messaging_topology_operator_bundle(
        topology_operator_release_file, version, output_directory
    )

    validate_bundle_struct(output_directory + "/" + version)
    validate_operator_crds(
        output_directory + "/" + version, crds_file_names, crds_names
    )
    validate_operator_manifest(output_directory + "/" + version, version)

    os.system("rm -fR ./rabbitmq_olm_package_repo/overlays")
    os.system("rm -fR ./rabbitmq_olm_package_repo/tmpmanifests")
    os.system("rm -fR " + output_directory)


# Check at least that the crd has been generated and two main fields (kind and metadata->name are created)
def validate_operator_crds(output_directory, crds_file_names, crds_names):

    output_directory = output_directory + "/manifests"

    directory = os.fsencode(output_directory)

    # check that all crd are present in the bundle
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if (
            filename == "rabbitmq.webhook-service.yaml"
            or filename == "rabbitmq.clusterserviceversion.yaml"
        ):
            continue

        assert filename in crds_file_names

        with open(output_directory + "/" + filename) as stream:
            try:
                crd = yaml.safe_load(stream)
                assert crd["kind"] == "CustomResourceDefinition"
                assert crd["metadata"]["name"] in crds_names
            except yaml.YAMLError as exc:
                logger.error("Error parsing crd")


# Check at least that the crd has been generated and two main fields (kind and metadata->name are created)
def validate_operator_manifest(output_directory, version):

    # check if crd is present in the bundle
    assert os.path.isfile(
        output_directory + "/manifests/rabbitmq.clusterserviceversion.yaml"
    )

    with open(
        output_directory + "/manifests/rabbitmq.clusterserviceversion.yaml"
    ) as stream:
        try:
            manifest = yaml.safe_load(stream)
            assert manifest["kind"] == "ClusterServiceVersion"
            assert (
                manifest["metadata"]["name"]
                == "rabbitmq-messaging-topology-operator.v" + version
            )

            # validate fields we have overlayed
            assert (
                manifest["spec"]["install"]["spec"]["deployments"][0]["name"]
                == "messaging-topology-operator"
            )
            assert (
                manifest["spec"]["install"]["spec"]["permissions"][0][
                    "serviceAccountName"
                ]
                == "messaging-topology-operator"
            )
            assert (
                manifest["spec"]["install"]["spec"]["clusterPermissions"][0][
                    "serviceAccountName"
                ]
                == "messaging-topology-operator"
            )

            # validate webhook
            webhooks = manifest["spec"]["webhookdefinitions"]
            for webhook in webhooks:
                assert webhook["deploymentName"] == "messaging-topology-operator"
                assert "/validate-rabbitmq-com" in webhook["webhookPath"]

        except yaml.YAMLError as exc:
            logger.error("Error parsing rabbitmq.clusterserviceversion file")
