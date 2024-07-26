~/OPEA/Demo_ChatQnA/ChatQnA/kubernetes/manifests/kustomization/scale.sh --namespace benchmarking --scale tgi1
./stresscli.py load-test --profile run-v8-500x4.yaml

~/OPEA/Demo_ChatQnA/ChatQnA/kubernetes/manifests/kustomization/scale.sh --namespace benchmarking --scale tgi8
./stresscli.py load-test --profile run-v8-500x4.yaml

~/OPEA/Demo_ChatQnA/ChatQnA/kubernetes/manifests/kustomization/scale.sh --namespace benchmarking --scale tgi16
./stresscli.py load-test --profile run-v8-500x4.yaml

~/OPEA/Demo_ChatQnA/ChatQnA/kubernetes/manifests/kustomization/scale.sh --namespace benchmarking --scale tgi32
./stresscli.py load-test --profile run-v8-500x4.yaml

