CLSUTER=aksvanilla
RG=aksvanilla

az extension add -n k8s-configuration
az extension add -n k8s-extension

az extension update -n k8s-configuration
az extension update -n k8s-extension

az k8s-configuration flux create -g $RG -c $CLSUTER \
-n broker \
--namespace broker-flux \
-t managedClusters \
--scope cluster \
--interval 1m0s \
-u https://github.com/davidxw/video-broker-lite \
--branch main  \
--kustomization name=broker-helm path=./manifests/releases sync_interval=1m0s prune=true 

#az k8s-configuration flux delete -g $RG -c $CLSUTER -n broker -t managedClusters

