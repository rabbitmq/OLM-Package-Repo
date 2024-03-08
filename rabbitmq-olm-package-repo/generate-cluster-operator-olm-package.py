import os
import sys

sys.path.insert(1, './../common_code')

from common_functions import create_overlay
from common_functions import replace_rabbitmq_cluster_operator_version_overlay
from common_functions import replace_rabbitmq_cluster_operator_image

def create_cluster_operator_bundle(operator_release_file, version, output_directory):

   get_replace_version(version)

   create_and_finalize_overlays(version, operator_release_file)

   create_olm_bundle(version, output_directory)

   clean_up()


def get_replace_version(version):

   f = open("./cluster_operator_generators/replace.txt")
   replaces = f.readline().strip()
   old_version= f.readline().strip()
   f.close()
   ytt_command_add_version = "ytt -f ./cluster_operator_generators/cluster-service-version-generator.yml --data-value-yaml name=rabbitmq-cluster-operator.v"+version+" --data-value-yaml version="+version+ " --data-value-yaml image=rabbitmqoperator/cluster-operator:"+version+ " --data-value-yaml replaces="+replaces+ "> ./tmpmanifests/cluster-operator-service-version-generator.yaml"
   os.system(ytt_command_add_version)

def create_and_finalize_overlays(version, operator_release_file):

   # Finalize the overlay
   create_overlay(operator_release_file, "kind: Role", "rules:", "---", "./cluster_operator_generators/overlay-permission-generator.yaml", "./overlays/cluster-operator-overlay-permission.yaml")       
   create_overlay(operator_release_file, "kind: ClusterRole", "rules:", "---", "./cluster_operator_generators/overlay-permission-generator.yaml", "./overlays/cluster-operator-overlay-cluster-permission.yaml")    
   create_overlay(operator_release_file, "kind: Deployment", "spec:", "terminationGracePeriodSeconds", "./cluster_operator_generators/overlay-deployment-generator.yaml", "./overlays/cluster-operator-overlay-deployment.yaml")  

   replace_rabbitmq_cluster_operator_version_overlay("./overlays/cluster-operator-overlay-permission.yaml", "rabbitmq-cluster-operator.v*", "rabbitmq-cluster-operator.v"+version)
   replace_rabbitmq_cluster_operator_version_overlay("./overlays/cluster-operator-overlay-cluster-permission.yaml", "rabbitmq-cluster-operator.v*", "rabbitmq-cluster-operator.v"+version)
   replace_rabbitmq_cluster_operator_version_overlay("./overlays/cluster-operator-overlay-deployment.yaml", "rabbitmq-cluster-operator.v*", "rabbitmq-cluster-operator.v"+version)

   # Apply the overlay and generate the ClusterServiceVersion file from overlay
   os.system("ytt -f ./overlays/cluster-operator-overlay-permission.yaml -f ./tmpmanifests/cluster-operator-service-version-generator.yaml  > ./tmpmanifests/cluster-operator-service-version-permission.yaml")
   os.system("ytt -f ./overlays/cluster-operator-overlay-cluster-permission.yaml -f ./tmpmanifests/cluster-operator-service-version-permission.yaml > ./tmpmanifests/cluster-operator-service-version-cluster-permission.yaml")
   os.system("cat ./cluster_operator_generators/license.yaml > ./tmpmanifests/rabbitmq.clusterserviceversion.yaml")
   os.system("ytt -f ./overlays/cluster-operator-overlay-deployment.yaml -f ./tmpmanifests/cluster-operator-service-version-cluster-permission.yaml >> ./tmpmanifests/rabbitmq.clusterserviceversion.yaml")


def create_olm_bundle(version, output_directory):
   rabbitmq_cluster_operator_dir=output_directory+"/" + version 
   rabbitmq_cluster_operator_dir_manifests=rabbitmq_cluster_operator_dir+"/manifests"
   rabbitmq_cluster_operator_dir_metadata=rabbitmq_cluster_operator_dir+"/metadata"
   replace_rabbitmq_cluster_operator_image("./tmpmanifests/rabbitmq.clusterserviceversion.yaml","rabbitmqoperator/cluster-operator:"+version, "docker.io/rabbitmqoperator/cluster-operator:"+version)
   os.system("mkdir -p " + rabbitmq_cluster_operator_dir_manifests)
   os.system("mkdir -p " + rabbitmq_cluster_operator_dir_metadata)
   os.system("cp ./tmpmanifests/rabbitmq.clusterserviceversion.yaml " + rabbitmq_cluster_operator_dir_manifests)
   os.system("cat ./cluster_operator_generators/license.yaml >" + rabbitmq_cluster_operator_dir_manifests+"/crds.yaml")
   os.system("tail -n +8 ./manifests_crds/crds.yaml >>" + rabbitmq_cluster_operator_dir_manifests+"/crds.yaml")
   os.system("cp ./cluster_operator_generators/bundle.Dockerfile " + rabbitmq_cluster_operator_dir)
   os.system("cp ./cluster_operator_generators/annotations.yaml " + rabbitmq_cluster_operator_dir+"/metadata")

def clean_up():

   # Cleanup
   #os.system("rm -fR ./tmpmanifests")
   #os.system("rm -fR ./overlays")

   # Remove tmp file
   os.system("rm cluster_operator_generators/cluster-operator.yaml")


def main():
   operator_release_file = sys.argv[1] 
   version = sys.argv[2]
   output_directory = sys.argv[3]

   # create temporary folder if not exists
   os.system("mkdir -p overlays")
   os.system("mkdir -p tmpmanifests")

   cluster_operator_release_file = "./cluster_operator_generators/cluster-operator.yaml"

   os.system("cp " + operator_release_file + " " + cluster_operator_release_file)
   os.system("echo \"\n---\" >> "+cluster_operator_release_file )

   create_cluster_operator_bundle(cluster_operator_release_file, version, output_directory)

# start main function
if __name__ == "__main__":
    main()


