# Config CPU policies

## Requirements

To well support LLM workload, we want CPU allocations to follow some rules:

- Aligns CPU allocations of a pod at the NUMA boundary, do not distribute CPU allocations accross different NUMA nodes.
- Allocate full physical cores.

## K8s CPU Manager Policy

K8s CPU Manager policy can be used to satisfy the requirements.

1. Remove the old CPU manager state file.

```
sudo rm /var/lib/kubelet/cpu_manager_state
```

2. Edit the kubelet configuration `/var/lib/kubelet/config.yaml` to change the CPU manager policy to `static` by appending below lines:

```
cpuManagerPolicy: static
systemReserved:
  cpu: 500m
  memory: 256M
kubeReserved:
  cpu: 500m
```

3. Edit the kubelet boot flags `/var/lib/kubelet/kubeadm-flags.env` to config static policy options by appending below options to `KUBELET_KUBEADM_ARGS`:

```
"--feature-gates=CPUManagerPolicyAlphaOptions=true --cpu-manager-policy-options=align-by-socket=true --cpu-manager-policy-options=distribute-cpus-across-numa=true"
```

The `KUBELET_KUBEADM_ARGS` may look like:
```
KUBELET_KUBEADM_ARGS="--container-runtime-endpoint=unix:///var/run/containerd/containerd.sock --pod-infra-container-image=registry.k8s.io/pause:3.9 --feature-gates=CPUManagerPolicyAlphaOptions=true --cpu-manager-policy-options=align-by-socket=true --cpu-manager-policy-options=distribute-cpus-across-numa=true"
```

4. Restart kubelet

```
sudo systemctl restart kubelet
```

5. Verify CPU Manager policies work by creating Nginx deployment, scaling it and checking the allocated CPU numbers.

Create 4 replica of Nginx pods by:
```
$ cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  selector:
    matchLabels:
      app: nginx
  replicas: 4
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        ports:
        - containerPort: 80
		resources:
          limits:
            cpu: 10
            memory: 1Gi
          requests:
            cpu: 10
            memory: 1Gi	
EOF
```

Check the CPU allocation of each pod and verify if the CPU allocation policies are satisfied:
```
$ for a in `kubectl get pods| grep nginx | grep Running |awk -F ' ' '{print $1}'`; do kubectl exec $a -- cat /proc/1/status |grep Cpus_allowed_list; done
Cpus_allowed_list:      11-20,59-68
Cpus_allowed_list:      34-43,82-91
Cpus_allowed_list:      24-33,72-81
Cpus_allowed_list:      1-10,49-58
```