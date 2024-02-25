#!/usr/bin/env bash
set -euo pipefail

VERSION=${1:-"0.0.0"}

sed -i -e "s/0.0.0/$VERSION/g" $PWD/OLM-Package-Repo/testfiles/rabbitmq-cluster-operator-catalog.yaml
sed -i -e "s/0.0.0/$VERSION/g" $PWD/OLM-Package-Repo/testfiles/rabbitmq-operator-subscription.yaml

kubectl create -f $PWD/OLM-Package-Repo/testfiles/rabbitmq-cluster-operator-catalog.yaml
kubectl create ns rabbitmq-system-olm
kubectl create -f $PWD/OLM-Package-Repo/testfiles/og.yaml
kubectl create -f $PWD/OLM-Package-Repo/testfiles/rabbitmq-operator-subscription.yaml