#!/usr/bin/env bash
set -euo pipefail

VERSION=${1:-"0.0.0"}

export OPERATOR_IMAGE="quay.io/rabbitmqoperator/rabbitmq-for-kubernetes-olm-cluster-operator-index:0.0.0"
export CSV_OPERATOR_IMAGE="rabbitmq-cluster-operator.v0.0.0"

export MESSAGING_OPERATOR_IMAGE="quay.io/rabbitmqoperator/rabbitmq-for-kubernetes-olm-messaging-topology-operator-index:$VERSION" 
export MESSAGING_OPERATOR_CSV="rabbitmq-messaging-topology-operator.v$VERSION"  

ytt -f $PWD/OLM-Package-Repo/testfiles/rabbitmq-cluster-operator-catalog-template.yaml --data-value-yaml image="$OPERATOR_IMAGE" > $PWD/OLM-Package-Repo/testfiles/rabbitmq-cluster-operator-catalog.yaml
ytt -f $PWD/OLM-Package-Repo/testfiles/rabbitmq-operator-subscription-template.yaml --data-value-yaml csv="$CSV_OPERATOR_IMAGE" > $PWD/OLM-Package-Repo/testfiles/rabbitmq-operator-subscription.yaml

ytt -f $PWD/OLM-Package-Repo/testfiles/rabbitmq-messaging-operator-catalog-template.yaml --data-value-yaml image="$MESSAGING_OPERATOR_IMAGE" >$PWD/OLM-Package-Repo/testfiles/rabbitmq-messaging-operator-catalog.yaml
ytt -f $PWD/OLM-Package-Repo/testfiles/rabbitmq-messaging-operator-subscription-template.yaml --data-value-yaml csv="$MESSAGING_OPERATOR_CSV" > $PWD/OLM-Package-Repo/testfiles/rabbitmq-messaging-operator-subscription.yaml

kubectl create -f $PWD/OLM-Package-Repo/testfiles/rabbitmq-cluster-operator-catalog.yaml
kubectl create -f $PWD/OLM-Package-Repo/testfiles/rabbitmq-messaging-operator-catalog.yaml
kubectl create ns rabbitmq-system-olm
kubectl create -f $PWD/OLM-Package-Repo/testfiles/og.yaml
kubectl create -f $PWD/OLM-Package-Repo/testfiles/rabbitmq-operator-subscription.yaml
kubectl create -f $PWD/OLM-Package-Repo/testfiles/rabbitmq-messaging-operator-subscription.yaml
