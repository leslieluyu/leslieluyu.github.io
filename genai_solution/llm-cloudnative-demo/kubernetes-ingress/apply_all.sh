#1. Configure RBAC
kubectl apply -f common/ns-and-sa.yaml
kubectl apply -f rbac/rbac.yaml
kubectl apply -f rbac/ap-rbac.yaml
kubectl apply -f rbac/apdos-rbac.yaml

#2. Create Common Resources
kubectl apply -f ./examples/shared-examples/default-server-secret/default-server-secret.yaml
kubectl apply -f common/nginx-config.yaml
#uncomment the annotation ingressclass.kubernetes.io/is-default-class
kubectl apply -f common/ingress-class.yaml 

#3. Create Custom Resources
kubectl apply -f common/crds/k8s.nginx.org_virtualservers.yaml
kubectl apply -f common/crds/k8s.nginx.org_virtualserverroutes.yaml
kubectl apply -f common/crds/k8s.nginx.org_transportservers.yaml
kubectl apply -f common/crds/k8s.nginx.org_policies.yaml
kubectl apply -f common/crds/k8s.nginx.org_globalconfigurations.yaml

#4. Deploying NGINX Ingress Controller
#4.1 Running NGINX Ingress Controller
kubectl apply -f deployment/nginx-ingress.yaml

#**5. Getting Access to NGINX Ingress Controller**
#**5.1 Create a Service for the NGINX Ingress Controller Pods**
kubectl create -f service/nodeport.yaml
