import os
import yaml
from kubernetes import client, config

def create_deployment_object(deployment_template, infer_type):
    with open(deployment_template) as f:
        dep = yaml.safe_load(f)
    metadata = dep["metadata"]
    metadata["name"] = f"{metadata['name']}-{infer_type}-deployment"
    containers = dep["spec"]["template"]["spec"]["containers"]
    for c in containers:
        envs = c["env"]
        for e in envs:
            if e["name"] == "INFER_TYPE":
                e["value"] = infer_type
    return dep

def create_deployments(deployment_template, num_deployments):
    config.load_kube_config()
    api_instance = client.AppsV1Api()

    for i in range(num_deployments):
        infer_type = f"pose-bf16-amx-{i+1:02d}"
        deployment_obj = create_deployment_object(deployment_template, infer_type)
        api_instance.create_namespaced_deployment(
            body=deployment_obj, namespace="default"
        )

def select_option():
    options = ['ei-sample', 'ei-infer', 'NO']

    print('Please select an option:')
    for i, option in enumerate(options):
        print(f'{i + 1}: {option}')

    selected_option = None
    while selected_option is None:
        try:
            choice = int(input('Enter the number of your choice: '))
            if choice < 1 or choice > len(options):
                raise ValueError
            selected_option = options[choice - 1]
        except ValueError:
            print('Invalid choice. Please enter a number between 1 and', len(options))

    print(f'You selected: {selected_option}')
    return selected_option

if __name__ == "__main__":
    deployment_template_path = input("Enter the path to deployment_template.yaml: ")
    num_deployments = int(input("Enter the number of deployments: "))
    create_deployments(deployment_template_path, num_deployments)
