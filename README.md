# OLM-Package-Repo-For-Cluster-Operator
Script to generate OLM (Operator-LifeCycle-Manager) Bundles for RabbitMQ operators </br>

Starting from our operator manifests:

[cluster-operator-manifest](https://github.com/rabbitmq/cluster-operator/releases/download/v2.7.0/cluster-operator.yml) </br>
[messaging-topology-operator-manifest](https://github.com/rabbitmq/messaging-topology-operator/releases/download/v1.13.0/messaging-topology-operator-with-certmanager.yaml)

The script is producing bundles like:

[cluster-operator-olm-bundle](https://github.com/redhat-openshift-ecosystem/community-operators-prod/tree/main/operators/rabbitmq-cluster-operator) </br>
[messaging-topology-operator-olm-bundle](https://github.com/redhat-openshift-ecosystem/community-operators-prod/tree/main/operators/rabbitmq-messaging-topology-operator)

That can be published to operatorhub/openshift marketplace 

This script is mainly used by our operator pipelines:

[operator-pipeline](https://github.com/rabbitmq/cluster-operator/blob/main/.github/workflows/testing_and_publishing_OLM_bundle.yml)


Basic Guidelines followed: </br>

https://olm.operatorframework.io/docs/tasks/creating-operator-bundle/ </br>

How to create, publish and test an OLM Bundle:</br>

https://devopstales.github.io/home/oml/


## How to use the script

the project is based on poetry 

It can be used in this way: </br>

```
poetry run generate_bundle ./rabbitmq_olm_package_repo/manifests_crds/cluster-operator.yaml 2.7.0 ./OLM_generated_bundle_example/rabbitmq-cluster-operator
poetry run generate_bundle ./rabbitmq_olm_package_repo/manifests_crds_messaging_topology_operator/messaging-topology-operator-with-certmanager.yaml 1.14.0 ./../OLM_generated_bundle_example/rabbitmq-messaging-topology-operator
```

First parameter is the operator release file like: 

[cluster-operator-manifest](https://github.com/rabbitmq/cluster-operator/releases/download/v2.7.0/cluster-operator.yml) 

The second parameter the version of the Bundle we are creating (Same version of the cluster operator) </br>
Third parameter is the output folder where the bundle is generated </br>

## How the script works
The script is based on ytt and a set of template files
https://carvel.dev/ytt/

From a generator file containing metadata: </br>

[cluster-operator-generator-manifest](https://github.com/rabbitmq/OLM-Package-Repo/blob/general_clean_up/rabbitmq_olm_package_repo/generators/cluster_operator_generators/cluster-service-version-generator.yml)

the script iss applying a set of ytt overlay defined in: 

https://github.com/rabbitmq/OLM-Package-Repo/blob/general_clean_up/rabbitmq_olm_package_repo/generators/cluster_operator_generators/

## Limitations
The script at the moment doesn't support the detection of new controllers and webhooks in the bundle </br>
This is mainly because the mapping is completely different and at the moment the operators are stable (in the last 3 years just 2 new controllers were added in the messaging topology operator).</br>

In case a new controller needs to be added you need to manually add it in the generator file: </br>
[messaging-topology-operator-generator-manifest](https://github.com/rabbitmq/OLM-Package-Repo/blob/general_clean_up/rabbitmq_olm_package_repo/generators/messaging_topology_operator_generators/topology-service-version-generator.yml)

In case the controller uses a webhook (like in case of the messaging topology operator), also the webhook needs to be added in: </br>
[web-hook mapping](https://github.com/rabbitmq/OLM-Package-Repo/blob/general_clean_up/rabbitmq_olm_package_repo/generators/messaging_topology_operator_generators/webhooks-mapping.yaml)

## Run tests

You can run test with:

```
poetry run pytest
```


Test are automatically run by our github flow on every PR or merge on main.