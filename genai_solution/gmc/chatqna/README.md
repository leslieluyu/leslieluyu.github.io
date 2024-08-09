# How-To Deploy and Benchmark ChatQnA by GMC in Kubernetes with Gaudi
## Info:
This doc is for deploying ChatQnA by GMC and how to scale the GMC in 1,2 and 4 nodes.
\
The scripts are already in satg-opea-4node-0:/home/yulu/OPEA/GenAIInfra/microservices-connector/config/
\
the node label is "gmc=chatqna"

## Steps:
### 1. Install GMC manager
Please refer  [GMC in GenAIInfra](https://github.com/opea-project/GenAIInfra/tree/main/microservices-connector) to insta GMC manager
### 2. Install ChatQnA Configmap
#### 2.0 tei-rerank running on Xeon or Gaudi?
- For tei-rerank Xeon
    ```
    cp teirerank.yaml.xeon manifests/teirerank.yaml
    ```
- For tei-rerank Gaudi
    ```
    cp teirerank.yaml.gaudi manifests/teirerank.yaml
    ```
#### 2.1 install Configmap
```
export SYSTEM_NAMESPACE=system
kubectl create namespace $SYSTEM_NAMESPACE

kubectl delete cm gmcyaml -n system
kubectl create configmap gmcyaml -n $SYSTEM_NAMESPACE --from-file $(pwd)/manifests
```
### 3. Install ChatQnA GMC

```
kubectl apply -f $(pwd)/chatQnA_dataprep_gaudi.yaml
```

### 4. data prep(MUST DO!!!)
```
dataprep_svc_ip=`kubectl  get svc -n chatqa|grep '^data-prep-svc '|awk '{print $3}'` \
&& echo ${dataprep_svc_ip} &&  \
   curl -X POST "http://${dataprep_svc_ip}:6007/v1/dataprep"     \
    -H "Content-Type: multipart/form-data"     \
    -F "files=@/home/yulu/OPEA/nke-10k-2023.pdf"
```

### 5. scale ChatQnA
```
alias kc='kubectl -n chatqa'
```
#### 5.1 reset node label
```
 kubectl label --overwrite nodes satg-opea-4node-0 gmc-
 kubectl label --overwrite nodes satg-opea-4node-1 gmc-
 kubectl label --overwrite nodes satg-opea-4node-2 gmc-
 kubectl label --overwrite nodes satg-opea-4node-3 gmc-
```

#### 5.2 scale to 1 nodes
    ```
    kubectl label --overwrite nodes satg-opea-4node-0 gmc-
    kubectl label --overwrite nodes satg-opea-4node-1 gmc-
    kubectl label --overwrite nodes satg-opea-4node-2 gmc-
    kubectl label --overwrite nodes satg-opea-4node-3 gmc-
    kubectl label nodes satg-opea-4node-0 gmc=chatqna

    kc scale deploy tgi-gaudi-svc-deployment --replicas=1
    kc scale deploy tei-embedding-svc-deployment --replicas=1
    kc scale deploy router-server --replicas=1
    kc scale deploy tei-reranking-svc-deployment --replicas=1

    ```

 - 1-node rerank-xeon
    
     ```
     kc scale deploy tgi-gaudi-svc-deployment --replicas=8
     ```
 - 1-node rerank-gaudi
    
     ```
     kc scale deploy tgi-gaudi-svc-deployment --replicas=7
     ```
 ### 5.3 scale to 2 nodes
```
    kubectl label --overwrite nodes satg-opea-4node-0 gmc-
    kubectl label --overwrite nodes satg-opea-4node-1 gmc-
    kubectl label --overwrite nodes satg-opea-4node-2 gmc-
    kubectl label --overwrite nodes satg-opea-4node-3 gmc-
    kubectl label nodes satg-opea-4node-0 gmc=chatqna
    kubectl label nodes satg-opea-4node-1 gmc=chatqna
```

 -  2-node rerank-xeon
    ```
    kc scale deploy tgi-gaudi-svc-deployment --replicas=16
    kc scale deploy tei-reranking-svc-deployment --replicas=2
    kc scale deploy tei-embedding-svc-deployment --replicas=2
    kc scale deploy router-server --replicas=2
    ```
 
 - 2-node rerank-gaudi
    ```
    kc scale deploy tgi-gaudi-svc-deployment --replicas=15
    kc scale deploy tei-embedding-svc-deployment --replicas=2
    kc scale deploy router-server --replicas=2
    ```

### 5.4 scale to 4 nodes
    ```
    kubectl label --overwrite nodes satg-opea-4node-0 gmc-
    kubectl label --overwrite nodes satg-opea-4node-1 gmc-
    kubectl label --overwrite nodes satg-opea-4node-2 gmc-
    kubectl label --overwrite nodes satg-opea-4node-3 gmc-
    kubectl label nodes satg-opea-4node-0 gmc=chatqna
    kubectl label nodes satg-opea-4node-1 gmc=chatqna
    kubectl label nodes satg-opea-4node-2 gmc=chatqna
    kubectl label nodes satg-opea-4node-3 gmc=chatqna
    ```
 
- 4-node rerank-xeon
    ```
    kc scale deploy tgi-gaudi-svc-deployment --replicas=32
    kc scale deploy tei-reranking-svc-deployment --replicas=4
    kc scale deploy tei-embedding-svc-deployment --replicas=4
    kc scale deploy router-server --replicas=4
    ```
 
- 4-node rerank-gaudi
    ```
    kc scale deploy tgi-gaudi-svc-deployment --replicas=31
    kc scale deploy tei-embedding-svc-deployment --replicas=4
    kc scale deploy router-server --replicas=4
    kc scale deploy tei-reranking-svc-deployment --replicas=1
    ```

### 6. Use stressCli to benchmark and get result
```
cd /home/yulu/OPEA/cloud.performance.benchmark.OPEAStress
./stresscli.py load-test --profile run-v08-512-gmc.yaml
```

