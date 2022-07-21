# OLM-Package-Repo-For-Cluster-Operator
Scripts to generate OLM (Operator-LifeCycle-Manager) Bundles for our operators </br>

This repo, will contains scripts to generate OLM Bundles starting from release.yaml files for our K8s operators to then be able to publish on OperatorHUB.</br>

Guidelines to follow: </br>

https://olm.operatorframework.io/docs/tasks/creating-operator-bundle/ </br>

How to create, publish and test an OLM Bundle:</br>

https://devopstales.github.io/home/oml/


# How to use the script

The script OLM-Package-Repo/generate_OLM/generate_OLM_cluster_operator/generate-olm-package.py will generate the OLM package needed to run the operator on respect the Operator Lifecycle management rule. <\br>

It can be used in this way: </br>

python3 generate-olm-package.py ./manifests_crds/cluster-operator.yaml 1.14.0 ./../../OLM/rabbitmq-cluster-operator </br>

First parameter is the cluster-operator release file </br>
The second parameter the version of the Bundle we are creating (Same version of the cluster operator) </br>
Third parameter is the output folder where the bundle is generated

The script can be then executed by a cluster-operator git worlflow in order to automatize the process on every release.
