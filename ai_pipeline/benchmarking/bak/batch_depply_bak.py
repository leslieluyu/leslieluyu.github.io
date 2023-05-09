import os
import argparse
from kubernetes import client, config

def create_deployment_object(name, infer_type):
    container = client.V1Container(
        name=name,
        image="your-image-name",
        env=[client.V1EnvVar(name="INFER_TYPE", value=infer_type)]
    )
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": name}),
        spec=client.V1PodSpec(containers=[container])
    )
    spec = client.V1DeploymentSpec(
        replicas=1,
        template=template,
        selector=client.V1LabelSelector(match_labels={"app": name})
    )
    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=name),
        spec=spec
    )
    return deployment

def create_deployments(num_deployments, infer_types):
    config.load_kube_config()

    apps_v1 = client.AppsV1Api()

    for i in range(num_deployments):
        deployment_name = f"my-deployment-{i}"
        infer_type = infer_types[i % len(infer_types)]
        deployment = create_deployment_object(deployment_name, infer_type)

        response = apps_v1.create_namespaced_deployment(
            body=deployment,
            namespace="default"
        )
        print(f"Deployment created: {response.metadata.name}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create multiple deployments in Kubernetes.')
    parser.add_argument('--template', type=str, required=True, help='Path to deployment YAML template.')
    parser.add_argument('--num', type=int, required=True, help='Number of deployments to create.')
    parser.add_argument('--infer-types', type=str, nargs='+', required=True, help='List of inference types to use for deployments.')
    args = parser.parse_args()

    with open(args.template) as f:
        deployment_yaml = f.read()

    num_deployments = args.num
    infer_types = args.infer_types

    for i in range(num_deployments):
        deployment_name = f"my-deployment-{i}"
        infer_type = infer_types[i % len(infer_types)]
        deployment_yaml = deployment_yaml.replace("{{DEPLOYMENT_NAME}}", deployment_name)
        deployment_yaml = deployment_yaml.replace("{{INFER_TYPE}}", infer_type)

        os.system(f"kubectl apply -f - <<EOF\n{deployment_yaml}\nEOF")

    print(f"Created {num_deployments} deployments using template {args.template}.")
