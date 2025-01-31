# tei

Helm chart for deploying Redis Vector DB service.

## Installing the Chart

To install the chart, run the following:

```console
$ helm install redis-vector-db redis-vector-db
```


## Values

| Key           | Type   | Default                                           | Description                                                                                                                              |
| ------------- | ------ | ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| redisVectorDb.image.repository   | string | `"redis/redis-stack"` |                                                                                                                                          |
| redisVectorDb.image.tag     | string | `"7.2.0-v9"`                                           |                                                                                                                                       |
| service.port (redis-service) | string | `"6379"`                                            | The redis-service port                                                                                                                         |
| service.port (redis-insight) | string | `"8001"`                                            | The redis-insight port                                                                                                                         |