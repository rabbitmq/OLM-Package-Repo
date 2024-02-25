#!/usr/bin/env bash
set -euo pipefail

VERSION=${1:-"0.0.0"}

sed -i -e "s/0.0.0/$VERSION/g" $PWD/OLM-Package-Repo/testfiles/rabbitmq-cluster-operator-catalog.yaml
sed -i -e "s/0.0.0/$VERSION/g" $PWD/OLM-Package-Repo/testfiles/rabbitmq-operator-subscription.yaml

kubectl delete csv rabbitmq-cluster-operator.v"$VERSION" -n rabbitmq-system-olm
kubectl delete -f $PWD/OLM-Package-Repo/testfiles/rabbitmq-operator-subscription.yaml
kubectl delete -f $PWD/OLM-Package-Repo/testfiles/og.yaml
kubectl delete ns rabbitmq-system-olm
kubectl delete -f $PWD/OLM-Package-Repo/testfiles/rabbitmq-cluster-operator-catalog.yaml