#! /bin/bash


if [[ "$1" == "create" ]]
then
    kubectl apply -f ./namespace
    kubectl apply -f ./secret
    kubectl apply -f ./configmap
    kubectl apply -f ./pvs
    kubectl apply -f ./deployment
    kubectl apply -f ./service
elif [[ "$1" == "delete" ]]
then
  kubectl delete all --namespace=job-collector-ns --all
  kubectl delete configmap --all --namespace=job-collector-ns
  kubectl delete secret --all --namespace=job-collector-ns
else
  echo "Supported commands: create, delete"
fi