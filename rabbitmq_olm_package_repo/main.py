from .utils import get_operator_name
from .utils import OperatorType
from .generate_cluster_operator_olm_package import create_cluster_operator_bundle
from .generate_messaging_topology_operator_olm_package import create_messaging_topology_operator_bundle
import sys
import os

def main():
    operator_release_file = sys.argv[1] 
    version = sys.argv[2]
    output_directory = sys.argv[3]

    operator_type= get_operator_name(operator_release_file)

    # create temporary folder if not exists
    os.system("mkdir -p overlays")
    os.system("mkdir -p tmpmanifests")


    if operator_type == OperatorType.CLUSTER_OPERATOR:
        print("Creating OLM Bundle for RabbitMQ cluster operator")
        cluster_operator_release_file = "./rabbitmq_olm_package_repo/generators/cluster_operator_generators/cluster-operator.yaml"
        os.system("cp " + operator_release_file + " " + cluster_operator_release_file)
        os.system("echo \"\n---\" >> "+cluster_operator_release_file )
        create_cluster_operator_bundle(cluster_operator_release_file, version, output_directory)
        os.system("rm " + cluster_operator_release_file)

    elif operator_type == OperatorType.MESSAGING_TOPOLOGY_OPERATOR:
        print("Creating OLM Bundle for RabbitMQ messaging topology operator")
        messaging_topology_operator_release_file = "./rabbitmq_olm_package_repo/generators/messaging_topology_operator_generators/cluster-operator.yaml"
        os.system("cp " + operator_release_file + " " + messaging_topology_operator_release_file)
        os.system("echo \"\n---\" >> "+messaging_topology_operator_release_file )
        create_messaging_topology_operator_bundle(messaging_topology_operator_release_file, version, output_directory)
        os.system("rm " + messaging_topology_operator_release_file)


    else:
        print("Input manifest not valid: It doesn't match a cluster operator or messaging operator manifest")

# start main function
if __name__ == "__main__":
    main()