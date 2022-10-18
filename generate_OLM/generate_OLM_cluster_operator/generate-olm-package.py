import os
import sys

# insert at position 1 in the path, as 0 is the path of this file.
sys.path.insert(1, './../../common_code')

from common_functions import create_overlay
from common_functions import replace_rabbitmq_cluster_operator_version_overlay
from common_functions import replace_rabbitmq_cluster_operator_image

if len(sys.argv) == 3:
   print('the script needs at least a cluster operator manifests a version and the output directory where store the Bundle as arguments in order to create the OLM structure')
   sys.exit()

operator_release_file = sys.argv[1] 
version = sys.argv[2]
output_directory = sys.argv[3]

f = open("./generators/replace.txt")
replaces = f.readline().strip()
oldversion= f.readline().strip()
f.close()

replace_rabbitmq_cluster_operator_image("./generators/cluster-service-version-generator.yml","rabbitmqoperator/cluster-operator:0.0.0", "rabbitmqoperator/cluster-operator:"+version)
replace_rabbitmq_cluster_operator_image("./generators/cluster-service-version-generator-openshift.yml","rabbitmqoperator/cluster-operator:0.0.0", "rabbitmqoperator/cluster-operator:"+version)
# Apply version to the service-version generator
ytt_command_add_version = "ytt -f ./generators/cluster-service-version-generator.yml --data-value-yaml name=rabbitmq-cluster-operator.v"+version+" --data-value-yaml version="+version+ " --data-value-yaml replaces="+replaces+ "> ./tmpmanifests/cluster-service-version-generator.yaml"
os.system(ytt_command_add_version)

# Create a copy of the cluster operator and add --- at the end of the file
cluster_operator_release_file = "./generators/cluster-operator.yaml"

os.system("cp " + operator_release_file + " " + cluster_operator_release_file)
os.system("echo \"\n---\" >> "+cluster_operator_release_file )

# Finalize the overlay
create_overlay(cluster_operator_release_file, "kind: Role", "rules:", "---", "./generators/overlay-permission-generator.yaml", "./overlays/overlay-permission.yaml")       
create_overlay(cluster_operator_release_file, "kind: ClusterRole", "rules:", "---", "./generators/overlay-cluster-permission-generator.yaml", "./overlays/overlay-cluster-permission.yaml")    
create_overlay(cluster_operator_release_file, "kind: Deployment", "spec:", "terminationGracePeriodSeconds", "./generators/overlay-deployment-generator.yaml", "./overlays/overlay-deployment.yaml")  

replace_rabbitmq_cluster_operator_version_overlay("./overlays/overlay-permission.yaml", "rabbitmq-cluster-operator.v*", "rabbitmq-cluster-operator.v"+version)
replace_rabbitmq_cluster_operator_version_overlay("./overlays/overlay-cluster-permission.yaml", "rabbitmq-cluster-operator.v*", "rabbitmq-cluster-operator.v"+version)
replace_rabbitmq_cluster_operator_version_overlay("./overlays/overlay-deployment.yaml", "rabbitmq-cluster-operator.v*", "rabbitmq-cluster-operator.v"+version)

# Apply the overlay and generate the ClusterServiceVersion file from overlay
os.system("ytt -f ./overlays/overlay-permission.yaml -f ./tmpmanifests/cluster-service-version-generator.yaml  > ./tmpmanifests/cluster-service-version-permission.yaml")
os.system("ytt -f ./overlays/overlay-cluster-permission.yaml -f ./tmpmanifests/cluster-service-version-permission.yaml > ./tmpmanifests/cluster-service-version-cluster-permission.yaml")
os.system("cat ./generators/license.yaml > ./tmpmanifests/rabbitmq.clusterserviceversion.yaml")
os.system("ytt -f ./overlays/overlay-deployment.yaml -f ./tmpmanifests/cluster-service-version-cluster-permission.yaml >> ./tmpmanifests/rabbitmq.clusterserviceversion.yaml")

# Create the bundle structure
rabbitmq_cluster_operator_dir=output_directory+"/" + version 
rabbitmq_cluster_operator_dir_manifests=rabbitmq_cluster_operator_dir+"/manifests"
rabbitmq_cluster_operator_dir_metadata=rabbitmq_cluster_operator_dir+"/metadata"
replace_rabbitmq_cluster_operator_image("./tmpmanifests/rabbitmq.clusterserviceversion.yaml","rabbitmqoperator/cluster-operator:"+version, "docker.io/rabbitmqoperator/cluster-operator:"+version)
os.system("mkdir -p " + rabbitmq_cluster_operator_dir_manifests)
os.system("mkdir -p " + rabbitmq_cluster_operator_dir_metadata)
os.system("cp ./tmpmanifests/rabbitmq.clusterserviceversion.yaml " + rabbitmq_cluster_operator_dir_manifests)
os.system("cat ./generators/license.yaml >" + rabbitmq_cluster_operator_dir_manifests+"/crds.yaml")
os.system("tail -n +8 ./manifests_crds/crds.yaml >>" + rabbitmq_cluster_operator_dir_manifests+"/crds.yaml")
os.system("cp ./generators/bundle.Dockerfile " + rabbitmq_cluster_operator_dir)
os.system("cp ./generators/annotations.yaml " + rabbitmq_cluster_operator_dir+"/metadata")

# Cleanup
#os.system("echo rabbitmq-cluster-operator.v"+version + " >./generators/replace.txt")
#os.system("echo "+version + " >>./generators/replace.txt")
os.system("rm ./tmpmanifests/*")
os.system("rm ./overlays/*")










