# tei

Helm chart for deploying Hugging Face Text Generation Inference service.

## Installing the Chart

To install the chart, run the following:

```console
$ export MODELDIR=/mnt
$ export MODELNAME="bigscience/bloom-560m"
$ helm install tei tei --set hftei.volume=${MODELDIR} --set hftei.modelId=${MODELNAME}
```

By default, the tei service will downloading the "bigscience/bloom-560m" which is about 1.1GB.

If you already cached the model locally, you can pass it to container like this example:

MODELDIR=/home/ubuntu/hfmodels

MODELNAME="/data/models--bigscience--bloom-560m"

## Values

| Key           | Type   | Default                                           | Description                                                                                                                              |
| ------------- | ------ | ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| hftei.modelId | string | `"BAAI/bge-base-en-v1.5"`                         | Models id from https://huggingface.co/, or predownloaded model directory                                                                 |
| hftei.port    | string | `"80"`                                            | Hugging Face Text Generation Inference service port                                                                                      |
| hftei.volume  | string | `"/mnt/model"`                                          | Cached models directory, tei will not download if the model is cached here. The "volume" will be mounted to container as /data directory |
| hftei.image   | string | `"ghcr.io/huggingface/text-embeddings-inference"` |                                                                                                                                          |
| hftei.tag     | string | `"cpu-1.2"`                                           |                                                                                                                                          |
| service.port  | string | `"80"`                                            | The service port                                                                                                                         |