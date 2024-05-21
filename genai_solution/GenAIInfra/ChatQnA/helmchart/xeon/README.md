# ChatQnA on Xeon

Helm chart for deploying ChatQnA service on Xeon.
  - name: redis-vector-db
    version: 0.1.0
  - name: tei-embedding-service
    version: 0.1.0
  - name: embedding
    version: 0.1.0
  - name: retriever
    version: 0.1.0
  - name: tei-xeon-service
    version: 0.1.0
  - name: reranking
    version: 0.1.0
  - name: tgi-service
    version: 0.1.0
  - name: llm
    version: 0.1.0
  - name: chaqna-xeon
    version: 0.1.0


ChatQnA depends on tei,tgi refer to tei,tgi for more config details.

## Installing the Chart

To install the chart, you need to modify the values.yaml then just run the following command:

```console
$ helm install chaqna-xeon .
```

## Values

| Key               | Type   | Default                               | Description                                                                                                                              |
| ----------------- | ------ | ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| REDIS_URL         | string | `"redis://chaqna-xeon-redis-vector-db.default.svc.cluster.local:6379"`                           |                                                                                                                                          |
| INDEX_NAME      | string | `"rag-redis"`                                |                                                                                                                                          |
| EMBEDDING_MODEL_ID           | string | `"BAAI/bge-base-en-v1.5"`                                  | Your own Hugging Face API token                                                                                                          |
| RERANK_MODEL_ID | string | `"BAAI/bge-reranker-large"` | Reranking Models id from https://huggingface.co/, or predownloaded model directory                                                                 |
| LLM_MODEL_ID    | string | `"Intel/neural-chat-7b-v3-3"`                                |                                                                                       |
| TEI_EMBEDDING_ENDPOINT  | string | `"http://chaqna-xeon-tei-embedding-service-svc.default.svc.cluster.local:6006"`             |                                                                                                                                          |
| TEI_RERANKING_ENDPOINT    | string | `"http://chaqna-xeon-tei-xeon-service-svc.default.svc.cluster.local:8808"`                                |                                                                                       |
| TGI_LLM_ENDPOINT    | string | `"http://chaqna-xeon-tgi-service-svc.default.svc.cluster.local:9009"`                                |                                                                                       |
| MEGA_SERVICE_HOST_IP    | string | `""`                                |           Put your host ip here.                                                                            |
| HUGGINGFACEHUB_API_TOKEN  | string | `""`                              | Your own Hugging Face API |
| CHAT_BASE_URL  | string | `"${chat_qna_backendurl}/v1/chatqna"`                              | chat qna backend url for UI  |

## How to Verify 
```console
# Verify MegaService

chaqna_backend_svc_ip=`kubectl get svc|grep '^chaqna-xeon-svc'|awk '{print $3}'` && echo ${chaqna_backend_svc_ip} 
curl http://${chaqna_backend_svc_ip}:8888/v1/chatqna -H "Content-Type: application/json" -d '{
     "model": "Intel/neural-chat-7b-v3-3",
     "messages": "What is the revenue of Nike in 2023?"
     }'
```
