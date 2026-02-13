# Notice

**This repo is outdated**. This functionality was moved to the operators repositories. See [1][2]

[1] https://github.com/rabbitmq/cluster-operator/tree/main/olm <br>
[2] https://github.com/rabbitmq/messaging-topology-operator/tree/main/olm

-----

# OLM-Package-Repo-For-RabbitMQ-K8s-Operators
Script to generate OLM (Operator-LifeCycle-Manager) Bundles for RabbitMQ Kubernetes operators </br>

Starting from our operator manifests:

[cluster-operator-manifest](https://github.com/rabbitmq/cluster-operator/releases/download/v2.7.0/cluster-operator.yml) </br>
[messaging-topology-operator-manifest](https://github.com/rabbitmq/messaging-topology-operator/releases/download/v1.13.0/messaging-topology-operator-with-certmanager.yaml)

The script is producing bundles like:

[cluster-operator-olm-bundle](https://github.com/redhat-openshift-ecosystem/community-operators-prod/tree/main/operators/rabbitmq-cluster-operator) </br>
[messaging-topology-operator-olm-bundle](https://github.com/redhat-openshift-ecosystem/community-operators-prod/tree/main/operators/rabbitmq-messaging-topology-operator)

That can be published to operatorhub/openshift marketplace 

This script is mainly used by our operator pipelines:

[operator-pipeline](https://github.com/rabbitmq/cluster-operator/blob/main/.github/workflows/testing_and_publishing_OLM_bundle.yml)  </br>

But it can be used for testing/extension ecc...

Basic Guidelines followed: </br>

https://olm.operatorframework.io/docs/tasks/creating-operator-bundle/ </br>

How to create, publish and test an OLM Bundle:</br>

https://devopstales.github.io/home/oml/


## How to use the script

the project is based on poetry 

It can be used in this way: </br>

```
poetry run generate_bundle ./rabbitmq_olm_package_repo/manifests_crds/cluster-operator.yaml 2.7.0 ./OLM_generated_bundle_example/rabbitmq-cluster-operator
poetry run generate_bundle ./rabbitmq_olm_package_repo/manifests_crds_messaging_topology_operator/messaging-topology-operator-with-certmanager.yaml 1.14.0 ./OLM_generated_bundle_example/rabbitmq-messaging-topology-operator
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

## How using OLM is different from the standard installation

When using the OLM packaging to install and use the two RabbitMQ Kubernetes Operators: (RabbitMQ cluster operator and RabbitMQ Messaging Topology Operator) you need to follow the OLM general documentation:

https://olm.operatorframework.io/docs/

Interesting section are about (Installation and Upgrade):

https://docs.openshift.com/container-platform/4.15/operators/admin/olm-upgrading-operators.html

OG and Subscriptions:

https://docs.openshift.com/container-platform/4.15/operators/understanding/olm/olm-understanding-operatorgroups.html

https://olm.operatorframework.io/docs/advanced-tasks/operator-scoping-with-operatorgroups/

https://olm.operatorframework.io/docs/concepts/crds/subscription/

There are a few scenarios like (upgrade, certificate management, volume management) that may be different when using OLM.

In particular a few scenarios that diverge from the standard RabbitMQ operator documentation are:

* In the Messaging Topology Operator there is no need to use cert-manager as OLM already deploy and rotate certificates for the webhooks as described here: https://olm.operatorframework.io/docs/advanced-tasks/adding-admission-and-conversion-webhooks/
  Also it is not possible (at the moment) for a user to provide their own certificates (as described as limitation in the same page). See also https://github.com/rabbitmq/OLM-Package-Repo/issues/21
* There are scenarios that requires a modifications on the Operator Deployment (for example mounting volumes or adding environment variables). This can't be done directly in OLM because the CSV will automatically revert these modifications.
  These scenarios can be implemented by templating the Subscription as described here: https://github.com/operator-framework/operator-lifecycle-manager/blob/master/doc/design/subscription-config.md#configuring-operators-deployed-by-olm
  See also https://github.com/rabbitmq/OLM-Package-Repo/issues/11

## Run tests

You can run test with:

```
poetry run pytest
```


Test are automatically run by our github flow on every PR or merge on main.
