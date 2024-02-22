#!/usr/bin/env bash
set -euo pipefail

kubectl delete csv rabbitmq-cluster-operator.v0.0.0 -n rabbitmq-system-olm
kubectl delete -f $PWD/OLM-Package-Repo/testfiles/rabbitmq-operator-subscription.yaml
kubectl delete -f $PWD/OLM-Package-Repo/testfiles/og.yaml
kubectl delete ns rabbitmq-system-olm
kubectl delete -f $PWD/OLM-Package-Repo/testfiles/rabbitmq-cluster-operator-catalog.yaml