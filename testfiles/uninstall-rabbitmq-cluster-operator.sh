#!/usr/bin/env bash
set -euo pipefail

VERSION=${1:-"0.0.0"}

export IMAGE="quay.io/rabbitmqoperator/rabbitmq-for-kubernetes-olm-cluster-operator-index:$VERSION" 
export CSV="rabbitmq-cluster-operator.v$VERSION"  

ytt -f $PWD/OLM-Package-Repo/testfiles/rabbitmq-cluster-operator-catalog-template.yaml --data-value-yaml image="$IMAGE" > $PWD/OLM-Package-Repo/testfiles/rabbitmq-cluster-operator-catalog.yaml
ytt -f $PWD/OLM-Package-Repo/testfiles/rabbitmq-operator-subscription-template.yaml --data-value-yaml csv="$CSV" > $PWD/OLM-Package-Repo/testfiles/rabbitmq-operator-subscription.yaml


kubectl delete csv rabbitmq-cluster-operator.v"$VERSION" -n rabbitmq-system-olm
kubectl delete -f $PWD/OLM-Package-Repo/testfiles/rabbitmq-operator-subscription.yaml
kubectl delete -f $PWD/OLM-Package-Repo/testfiles/og.yaml
kubectl delete ns rabbitmq-system-olm
kubectl delete -f $PWD/OLM-Package-Repo/testfiles/rabbitmq-cluster-operator-catalog.yaml