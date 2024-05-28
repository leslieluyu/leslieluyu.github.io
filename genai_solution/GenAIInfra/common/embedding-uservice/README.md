# embedding-uservice

Helm chart for deploying embedding microservice.

embedding-uservice depends on TEI, refer to tei for more config details.

## Installing the Chart

To install the chart, run the following:

```console
$ export HFTOKEN="insert-your-huggingface-token-here"
$ export MODELDIR="/mnt"
$ export MODELNAME="m-a-p/OpenCodeInterpreter-DS-6.7B"
$ helm install embedding embedding-uservice --set HUGGINGFACEHUB_API_TOKEN=${HFTOKEN} --set tei.volume=${MODELDIR} --set tei.embedding_MODEL_ID=${MODELNAME}
```

## Values

| Key                      | Type   | Default                               | Description                                                                                                                              |
| ------------------------ | ------ | ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| HUGGINGFACEHUB_API_TOKEN | string | `""`                                  | Your own Hugging Face API token                                                                                                          |
| image.repository         | string | `"opea/embedding-tgi:latest"`               |                                                                                                                                          |
| service.port             | string | `"9000"`                              |                                                                                                                                          |
| tei.EMBEDDING_MODEL_ID         | string | `"m-a-p/OpenCodeInterpreter-DS-6.7B"` | Models id from https://huggingface.co/, or predownloaded model directory                                                                 |
| tei.port                 | string | `"80"`                                | Hugging Face Text Generation Inference service port                                                                                      |
| tei.volume               | string | `"/mnt"`                              | Cached models directory, tgi will not download if the model is cached here. The "volume" will be mounted to container as /data directory |
