from kubernetes import client, config

# Load kubernetes configuration from default location
config.load_kube_config()

# Set namespace and deployment name
namespace = 'default'
deployment_name = 'ei-sample-pose-bf16-amx-deployment'

# Create Kubernetes API client objects
core_api = client.CoreV1Api()
apps_api = client.AppsV1Api()

# Get the deployment object
deployment = apps_api.read_namespaced_deployment(deployment_name, namespace)

# Get the labels from the deployment's pod template
labels = deployment.spec.template.metadata.labels

# Get the pods associated with the deployment
pod_list = core_api.list_namespaced_pod(namespace, label_selector=','.join([f'{k}={v}' for k, v in labels.items()]))

# define the infer_type
infer_type = ['pose-bf16-amx-01','pose-bf16-amx-02']
# Print each pod's main info and set environment variables
i = 0
for pod in pod_list.items:
    print(f'Pod name: {pod.metadata.name}')
    print(f'Pod status: {pod.status.phase}')
    print(f'Pod IP: {pod.status.pod_ip}')
    print(f'Env:', pod.spec.containers[0].env)
    
    # Set environment variables for the pod
    env_vars = [
        client.V1EnvVar(name='VAR1', value='value1'),
        client.V1EnvVar(name='VAR2', value='value2')
    ]
    #pod.spec.containers[0].env = env_vars
    patch = {
        "spec": {
            "containers": [
                {
                    "name": pod.spec.containers[0].name,
                    "env": [
                        {
                            "name": "INFER_TYPE",
                            "value": infer_type[i]
                        }
                    ]
                }
            ]
        }
    }
    i = i+1
    #core_api.patch_namespaced_pod(pod.metadata.name, namespace, pod)
    core_api.patch_namespaced_pod(name=pod.metadata.name, namespace=namespace, body=patch) 
    print('Environment variables set for pod.')
