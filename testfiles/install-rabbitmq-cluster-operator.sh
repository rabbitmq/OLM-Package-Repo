#!/usr/bin/env bash
set -euo pipefail

kubectl create -f $PWD/OLM-Package-Repo/testfiles/rabbitmq-cluster-operator-catalog.yaml
kubectl create ns rabbitmq-system-olm
kubectl create -f $PWD/OLM-Package-Repo/testfiles/og.yaml
kubectl create -f $PWD/OLM-Package-Repo/testfiles/rabbitmq-operator-subscription.yaml