import logging
import os
import sys
from datetime import datetime

from .utils import (
    create_overlay,
    get_operator_last_tag,
    replace_if_rabbitmq_webhook,
    replace_rabbitmq_cluster_operator_image,
    replace_rabbitmq_cluster_operator_version_overlay,
)


def create_messaging_topology_operator_bundle(
    operator_release_file, version, output_directory
):

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    logger.info("Get Operator last tag")
    replaces = get_operator_last_tag("messaging-topology-operator")

    logger.info("Replacing replace version to manifest")
    if version == "0.0.0":
        replaces = " "
        _set_replace_version(version, replaces)
    else:
        _set_replace_version(version, replaces)

    logger.info("Creating and finalizing ytt rabbitmq_olm_package_repo/overlays")
    _create_and_finalize_overlays(version, operator_release_file)

    logger.info("Creating and olm bundle")
    _create_olm_bundle(version, output_directory)


def _set_replace_version(version, replaces):

    now = datetime.now()
    createdAt = now.strftime("yyyy-MM-dd")

    # Apply version to the service-version generator
    ytt_command_add_version = (
        "ytt -f ./rabbitmq_olm_package_repo/generators/messaging_topology_operator_generators/topology-service-version-generator.yml --data-value-yaml name=rabbitmq-messaging-topology-operator.v"
        + version
        + "  --data-value-yaml image=rabbitmqoperator/messaging-topology-operator:"
        + version
        + " --data-value-yaml version="
        + version
        + " --data-value-yaml replaces="
        + replaces
        + " --data-value-yaml createdAt="
        + createdAt
        + "> ./rabbitmq_olm_package_repo/tmpmanifests/topology-operator-service-version-generator.yaml"
    )
    os.system(ytt_command_add_version)


def _create_and_finalize_overlays(version, operator_release_file):

    create_overlay(
        operator_release_file,
        "kind: Role",
        "rules:",
        "---",
        "./rabbitmq_olm_package_repo/generators/messaging_topology_operator_generators/overlay-permission-generator.yaml",
        "./rabbitmq_olm_package_repo/overlays/topology-operator-overlay-permission.yaml",
    )
    create_overlay(
        operator_release_file,
        "kind: ClusterRole",
        "rules:",
        "---",
        "./rabbitmq_olm_package_repo/generators/messaging_topology_operator_generators/overlay-cluster-permission-generator.yaml",
        "./rabbitmq_olm_package_repo/overlays/topology-operator-overlay-cluster-permission.yaml",
    )
    create_overlay(
        operator_release_file,
        "kind: Deployment",
        "spec:",
        "---",
        "./rabbitmq_olm_package_repo/generators/messaging_topology_operator_generators/overlay-deployment-generator.yaml",
        "./rabbitmq_olm_package_repo/overlays/topology-operator-overlay-deployment.yaml",
    )

    replace_rabbitmq_cluster_operator_version_overlay(
        "./rabbitmq_olm_package_repo/overlays/topology-operator-overlay-permission.yaml",
        "rabbitmq-messaging-topology-operator.v*",
        "rabbitmq-messaging-topology-operator.v" + version,
    )
    replace_rabbitmq_cluster_operator_version_overlay(
        "./rabbitmq_olm_package_repo/overlays/topology-operator-overlay-cluster-permission.yaml",
        "rabbitmq-messaging-topology-operator.v*",
        "rabbitmq-messaging-topology-operator.v" + version,
    )
    replace_rabbitmq_cluster_operator_version_overlay(
        "./rabbitmq_olm_package_repo/overlays/topology-operator-overlay-deployment.yaml",
        "rabbitmq-messaging-topology-operator.v*",
        "rabbitmq-messaging-topology-operator.v" + version,
    )

    # Apply the overlay and generate the ClusterServiceVersion file from overlay
    os.system(
        "ytt -f ./rabbitmq_olm_package_repo/overlays/topology-operator-overlay-permission.yaml -f ./rabbitmq_olm_package_repo/tmpmanifests/topology-operator-service-version-generator.yaml  > ./rabbitmq_olm_package_repo/tmpmanifests/topology-operator-service-version-permission.yaml"
    )
    os.system(
        "ytt -f ./rabbitmq_olm_package_repo/overlays/topology-operator-overlay-cluster-permission.yaml -f ./rabbitmq_olm_package_repo/tmpmanifests/topology-operator-service-version-permission.yaml > ./rabbitmq_olm_package_repo/tmpmanifests/topology-operator-service-version-cluster-permission.yaml"
    )

    os.system(
        "cat ./rabbitmq_olm_package_repo/generators/messaging_topology_operator_generators/license.yaml > ./rabbitmq_olm_package_repo/tmpmanifests/rabbitmq.clusterserviceversion.yaml"
    )
    os.system(
        "ytt -f ./rabbitmq_olm_package_repo/overlays/topology-operator-overlay-deployment.yaml -f ./rabbitmq_olm_package_repo/tmpmanifests/topology-operator-service-version-cluster-permission.yaml >> ./rabbitmq_olm_package_repo/tmpmanifests/rabbitmq.clusterserviceversion.yaml"
    )
    os.system(
        "cat ./rabbitmq_olm_package_repo/generators/messaging_topology_operator_generators/webhooks-mapping.yaml >> ./rabbitmq_olm_package_repo/tmpmanifests/rabbitmq.clusterserviceversion.yaml"
    )


def _create_olm_bundle(version, output_directory):

    rabbitmq_cluster_operator_dir = output_directory + "/" + version
    rabbitmq_cluster_operator_dir_manifests = (
        rabbitmq_cluster_operator_dir + "/manifests"
    )
    rabbitmq_cluster_operator_dir_metadata = rabbitmq_cluster_operator_dir + "/metadata"
    replace_rabbitmq_cluster_operator_image(
        "./rabbitmq_olm_package_repo/tmpmanifests/rabbitmq.clusterserviceversion.yaml",
        "rabbitmqoperator/messaging-topology-operator:" + version,
        "docker.io/rabbitmqoperator/messaging-topology-operator:" + version,
    )
    os.system("mkdir -p " + rabbitmq_cluster_operator_dir_manifests)
    os.system("mkdir -p " + rabbitmq_cluster_operator_dir_metadata)
    replace_if_rabbitmq_webhook(
        "./rabbitmq_olm_package_repo/tmpmanifests/rabbitmq.clusterserviceversion.yaml"
    )
    os.system(
        "cp ./rabbitmq_olm_package_repo/tmpmanifests/rabbitmq.clusterserviceversion.yaml "
        + rabbitmq_cluster_operator_dir_manifests
    )

    # Adding license tags to custom resource definition files
    for filename in os.scandir(
        "./rabbitmq_olm_package_repo/manifests_crds_messaging_topology_operator/crds"
    ):
        if filename.is_file():
            os.system(
                "cat ./rabbitmq_olm_package_repo/generators/messaging_topology_operator_generators/license.yaml > "
                + rabbitmq_cluster_operator_dir_manifests
                + "/"
                + filename.name
            )
            os.system(
                "tail -n +2 ./rabbitmq_olm_package_repo/manifests_crds_messaging_topology_operator/crds/"
                + filename.name
                + " >> "
                + rabbitmq_cluster_operator_dir_manifests
                + "/"
                + filename.name
            )

    os.system(
        "cp ./rabbitmq_olm_package_repo/generators/messaging_topology_operator_generators/bundle.Dockerfile "
        + rabbitmq_cluster_operator_dir
    )
    os.system(
        "cp ./rabbitmq_olm_package_repo/generators/messaging_topology_operator_generators/annotations.yaml "
        + rabbitmq_cluster_operator_dir_metadata
    )
    os.system(
        "cp ./rabbitmq_olm_package_repo/generators/messaging_topology_operator_generators/rabbitmq.webhook-service.yaml "
        + rabbitmq_cluster_operator_dir_manifests
    )
