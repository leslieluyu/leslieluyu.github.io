helm install chatqna . \
--set global.HUGGINGFACEHUB_API_TOKEN=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 \
--set chatqna-ui.nodeSelector.${LABEL} \
--set tei.nodeSelector.${LABEL} \
--set teirerank.nodeSelector.${LABEL} \
--set data-prep.nodeSelector.${LABEL} \
--set embedding-usvc.nodeSelector.${LABEL} \
--set llm-uservice.nodeSelector.${LABEL} \
--set redis-vector-db.nodeSelector.${LABEL} \
--set reranking-usvc.nodeSelector.${LABEL} \
--set retriever-usvc.nodeSelector.${LABEL} \
--set tgi.nodeSelector.${LABEL} \
--set vllm.nodeSelector.${LABEL} \
--set nodeSelector.${LABEL} \
--create-namespace \
--namespace ${NS} \
-f - 