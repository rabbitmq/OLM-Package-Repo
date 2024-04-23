import logging
import os
import sys

from .cluster_operator_bundle import (
    create_cluster_operator_bundle,
)
from .topology_operator_bundle import (
    create_messaging_topology_operator_bundle,
)
from .utils import OperatorType, get_operator_name


def main():
    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    if len(sys.argv) != 4:
        logger.error(
            "the script needs at least a manifests (cluster-operator or messaging-operator) a version and the output directory where store the Bundle as arguments in order to create the OLM structure"
        )
        sys.exit()

    operator_release_file = sys.argv[1]
    version = sys.argv[2]
    output_directory = sys.argv[3]

    operator_type = get_operator_name(operator_release_file)

    # create temporary folder if not exists
    logger.info("creating temporary folders")
    os.system("mkdir -p ./rabbitmq_olm_package_repo/overlays")
    os.system("mkdir -p ./rabbitmq_olm_package_repo/tmpmanifests")

    if operator_type == OperatorType.CLUSTER_OPERATOR:
        logger.info("Creating OLM Bundle for RabbitMQ cluster operator")
        cluster_operator_release_file = (
            "./rabbitmq_olm_package_repo/tmpmanifests/cluster-operator.yaml"
        )
        os.system(
            "ytt -f "
            + operator_release_file
            + " -f ./rabbitmq_olm_package_repo/generators/cluster_operator_generators/cluster-operator-namespace-scope-overlay.yml > "
            + cluster_operator_release_file
        )
        os.system('echo "\n---" >> ' + cluster_operator_release_file)
        create_cluster_operator_bundle(
            cluster_operator_release_file, version, output_directory
        )

    elif operator_type == OperatorType.MESSAGING_TOPOLOGY_OPERATOR:
        logger.info("Creating OLM Bundle for RabbitMQ messaging topology operator")
        messaging_topology_operator_release_file = (
            "./rabbitmq_olm_package_repo/tmpmanifests/cluster-operator.yaml"
        )
        os.system(
            "ytt -f "
            + operator_release_file
            + " -f ./rabbitmq_olm_package_repo/generators/messaging_topology_operator_generators/topology-operator-namespace-scope-overlay.yml > "
            + messaging_topology_operator_release_file
        )

        os.system('echo "\n---" >> ' + messaging_topology_operator_release_file)
        create_messaging_topology_operator_bundle(
            messaging_topology_operator_release_file, version, output_directory
        )

    else:
        logger.warning(
            "Input manifest not valid: It doesn't match a cluster operator or messaging operator manifest"
        )

    logger.info("Clean up")
    # os.system("rm -fR ./rabbitmq_olm_package_repo/overlays")
    # os.system("rm -fR ./rabbitmq_olm_package_repo/tmpmanifests")


# start main function
if __name__ == "__main__":
    main()
