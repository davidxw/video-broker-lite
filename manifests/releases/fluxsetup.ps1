
$CLUSTER=storeaks
$RG=hci-dev-aae

az k8s-configuration flux create -g $RG -c storeaks $CLUSTER `
-n broker `
--namespace broker-flux `
-t connectedClusters `
--scope cluster `
--interval 1m0s `
-u https://github.com/davidxw/video-broker-lite `
--branch main  `
--kustomization name=broker-helm path=./manifests/releases sync_interval=1m0s prune=true 

#az k8s-configuration flux delete -g $RG -c $CLUSTER -n broker -t connectedClusters