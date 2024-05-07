import logging
import os
import sys
from datetime import datetime

from .utils import (
    create_overlay,
    get_operator_last_tag,
    replace_rabbitmq_cluster_operator_image,
    replace_rabbitmq_cluster_operator_version_overlay,
)


def create_cluster_operator_bundle(operator_release_file, version, output_directory):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    logger.info("Get Operator last tag")
    replaces = get_operator_last_tag("cluster-operator")

    logger.info("Replacing replace version to manifest")
    # work around needed for our github action because we don't have a previous version to replace
    # opm is complaining in this case.
    # if version == "0.0.0":
    replaces = " "
    _set_replace_version(version, replaces)

    # else:
    #    _set_replace_version(version, replaces)

    logger.info("Creating and finalizing ytt overlays")
    _create_and_finalize_overlays(version, operator_release_file)

    logger.info("Creating and olm bundle")
    _create_olm_bundle(version, output_directory)


# set the replace version in the manifest
def _set_replace_version(version, replaces):
    now = datetime.now()
    createdAt = now.strftime("%m/%d/%Y")

    ytt_command_add_version = (
        "ytt -f ./rabbitmq_olm_package_repo/generators/cluster_operator_generators/cluster-service-version-generator.yml --data-value-yaml name=rabbitmq-cluster-operator.v"
        + version
        + " --data-value-yaml version="
        + version
        + " --data-value-yaml image=rabbitmqoperator/cluster-operator:"
        + version
        + " --data-value-yaml replaces="
        + replaces
        + " --data-value-yaml createdAt="
        + str(createdAt)
        + "> ./rabbitmq_olm_package_repo/tmpmanifests/cluster-operator-service-version-generator.yaml"
    )
    os.system(ytt_command_add_version)


# creates overlay for permission, and cluster-operator-permission
def _create_and_finalize_overlays(version, operator_release_file):
    # Finalize the overlay
    create_overlay(
        operator_release_file,
        "kind: Role",
        "rules:",
        "---",
        "./rabbitmq_olm_package_repo/generators/cluster_operator_generators/overlay-permission-generator.yaml",
        "./rabbitmq_olm_package_repo/overlays/cluster-operator-overlay-permission.yaml",
    )
    create_overlay(
        operator_release_file,
        "kind: ClusterRole",
        "rules:",
        "---",
        "./rabbitmq_olm_package_repo/generators/cluster_operator_generators/overlay-cluster-permission-generator.yaml",
        "./rabbitmq_olm_package_repo/overlays/cluster-operator-overlay-cluster-permission.yaml",
    )
    create_overlay(
        operator_release_file,
        "kind: Deployment",
        "spec:",
        "---",
        "./rabbitmq_olm_package_repo/generators/cluster_operator_generators/overlay-deployment-generator.yaml",
        "./rabbitmq_olm_package_repo/overlays/cluster-operator-overlay-deployment.yaml",
    )

    replace_rabbitmq_cluster_operator_version_overlay(
        "./rabbitmq_olm_package_repo/overlays/cluster-operator-overlay-permission.yaml",
        "rabbitmq-cluster-operator.v*",
        "rabbitmq-cluster-operator.v" + version,
    )
    replace_rabbitmq_cluster_operator_version_overlay(
        "./rabbitmq_olm_package_repo/overlays/cluster-operator-overlay-cluster-permission.yaml",
        "rabbitmq-cluster-operator.v*",
        "rabbitmq-cluster-operator.v" + version,
    )
    replace_rabbitmq_cluster_operator_version_overlay(
        "./rabbitmq_olm_package_repo/overlays/cluster-operator-overlay-deployment.yaml",
        "rabbitmq-cluster-operator.v*",
        "rabbitmq-cluster-operator.v" + version,
    )

    # Apply the overlay and generate the ClusterServiceVersion file from overlay
    os.system(
        "ytt -f ./rabbitmq_olm_package_repo/overlays/cluster-operator-overlay-permission.yaml -f ./rabbitmq_olm_package_repo/tmpmanifests/cluster-operator-service-version-generator.yaml  > ./rabbitmq_olm_package_repo/tmpmanifests/cluster-operator-service-version-permission.yaml"
    )
    os.system(
        "ytt -f ./rabbitmq_olm_package_repo/overlays/cluster-operator-overlay-cluster-permission.yaml -f ./rabbitmq_olm_package_repo/tmpmanifests/cluster-operator-service-version-permission.yaml > ./rabbitmq_olm_package_repo/tmpmanifests/cluster-operator-service-version-cluster-permission.yaml"
    )
    os.system(
        "cat ./rabbitmq_olm_package_repo/generators/cluster_operator_generators/license.yaml > ./rabbitmq_olm_package_repo/tmpmanifests/rabbitmq.clusterserviceversion.yaml"
    )
    os.system(
        "ytt -f ./rabbitmq_olm_package_repo/overlays/cluster-operator-overlay-deployment.yaml -f ./rabbitmq_olm_package_repo/tmpmanifests/cluster-operator-service-version-cluster-permission.yaml >> ./rabbitmq_olm_package_repo/tmpmanifests/rabbitmq.clusterserviceversion.yaml"
    )


# Creates the final bundle structure
def _create_olm_bundle(version, output_directory):
    rabbitmq_cluster_operator_dir = output_directory + "/" + version
    rabbitmq_cluster_operator_dir_manifests = (
        rabbitmq_cluster_operator_dir + "/manifests"
    )
    rabbitmq_cluster_operator_dir_metadata = rabbitmq_cluster_operator_dir + "/metadata"
    replace_rabbitmq_cluster_operator_image(
        "./rabbitmq_olm_package_repo/tmpmanifests/rabbitmq.clusterserviceversion.yaml",
        "rabbitmqoperator/cluster-operator:" + version,
        "docker.io/rabbitmqoperator/cluster-operator:" + version,
    )
    os.system("mkdir -p " + rabbitmq_cluster_operator_dir_manifests)
    os.system("mkdir -p " + rabbitmq_cluster_operator_dir_metadata)
    if version != "0.0.0":
        os.system(
            "kbld -f ./rabbitmq_olm_package_repo/tmpmanifests/rabbitmq.clusterserviceversion.yaml > ./rabbitmq_olm_package_repo/tmpmanifests/rabbitmq.clusterserviceversion.kbld.yaml"
        )
        os.system(
            "cp ./rabbitmq_olm_package_repo/tmpmanifests/rabbitmq.clusterserviceversion.kbld.yaml "
            + rabbitmq_cluster_operator_dir_manifests
            + "/rabbitmq.clusterserviceversion.yaml "
        )
    else:
        os.system(
            "cp ./rabbitmq_olm_package_repo/tmpmanifests/rabbitmq.clusterserviceversion.yaml "
            + rabbitmq_cluster_operator_dir_manifests
            + "/rabbitmq.clusterserviceversion.yaml "
        )

    os.system(
        "cat ./rabbitmq_olm_package_repo/generators/cluster_operator_generators/license.yaml >"
        + rabbitmq_cluster_operator_dir_manifests
        + "/crds.yaml"
    )
    os.system(
        "tail -n +8 ./rabbitmq_olm_package_repo/manifests_crds/crds.yaml >>"
        + rabbitmq_cluster_operator_dir_manifests
        + "/crds.yaml"
    )
    os.system(
        "cp ./rabbitmq_olm_package_repo/generators/cluster_operator_generators/bundle.Dockerfile "
        + rabbitmq_cluster_operator_dir
    )
    os.system(
        "cp ./rabbitmq_olm_package_repo/generators/cluster_operator_generators/annotations.yaml "
        + rabbitmq_cluster_operator_dir
        + "/metadata"
    )
