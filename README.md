# Kubernetes-Custom_Pod_Autoscaler
A Custom Pod Autoscaler for kubernetes that works with Latency and Cluster's costs metrrics

# Usefull prompt commands
helm install custom-pod-autoscaler-operator https://github.com/jthomperoo/custom-pod-autoscaler-operator/releases/download/v1.4.2/custom-pod-autoscaler-operator-v1.4.2.tgz

helm install opencost --repo https://opencost.github.io/opencost-helm-chart opencost --namespace default

kubectl apply -f https://github.com/jthomperoo/custom-pod-autoscaler-operator/releases/download/v1.1.0/cluster.yaml
  
helm install prometheus --repo https://prometheus-community.github.io/helm-charts prometheus --namespace default --set prometheus-pushgateway.enabled=false --set alertmanager.enabled=false -f https://raw.githubusercontent.com/opencost/opencost/develop/kubernetes/prometheus/extraScrapeConfigs.yaml

The Prometheus server can be accessed via port 80 on the following DNS name from within your cluster:
prometheus-server.default.svc.cluster.local

Get the Prometheus server URL by running these commands in the same shell:
  export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=prometheus,app.kubernetes.io/instance=prometheus" -o jsonpath="{.items[0].metadata.name}")
  kubectl --namespace default port-forward $POD_NAME 9090
  
helm install opencost --repo https://opencost.github.io/opencost-helm-chart opencost --namespace default -f helm-values.yaml

helm upgrade prometheus --repo https://prometheus-community.github.io/helm-charts prometheus --namespace default --set prometheus-pushgateway.enabled=false --set alertmanager.enabled=false -f custom-extraScrapeConfigs.yaml

helm upgrade prometheus --repo https://prometheus-community.github.io/helm-charts prometheus --namespace default --set prometheus-pushgateway.enabled=false --set alertmanager.enabled=false --set-file prometheus.additionalScrapeConfigs=custom-extraScrapeConfigs.yaml

kubectl delete -f https://github.com/jthomperoo/custom-pod-autoscaler-operator/releases/download/v1.1.0/cluster.yaml

docker build -t app-target:latest .
docker tag app-target:latest carlito9675/app-target:latest
docker push carlito9675/app-target:latest

kubectl port-forward svc/app-service 8090:90 -n default
kubectl port-forward svc/prometheus-server 9090:80 -n default

kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

kubectl apply -f https://k8s.io/examples/application/php-apache.yaml

kubectl autoscale deployment <deployment-name> --cpu-percent=50 --min=1 --max=10

kubectl get hpa

helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm install grafana grafana/grafana -n default -f grafana.yaml --set service.type=ClusterIP --set adminPassword='admin'

helm upgrade grafana grafana/grafana --namespace default --set service.type=ClusterIP

kubectl port-forward svc/grafana 3000:3000 -n default


kubectl cost --service-port 9003 --service-name opencost --kubecost-namespace default --allocation-path /allocation/compute   namespace --historical --window 5d  --show-cpu --show-memory --show-pv --show-efficiency=false

docker build -t carlito9675/locust:latest .
docker push carlito9675/locust:latest

kubectl apply -f locust-deployment.yaml
kubectl apply -f locust-service.yaml

helm upgrade prometheus --repo https://prometheus-community.github.io/helm-charts prometheus --namespace default -f custom-extraScrapeConfigs.yaml

helm repo add deliveryhero https://charts.deliveryhero.io/
helm repo update

helm install prometheus-locust-exporter deliveryhero/prometheus-locust-exporter --namespace default --set config.locust_uri=http://locust-service.default.svc.cluster.local:8089

kubectl autoscale deployment app-target-hpa --cpu-percent=50 --min=1 --max=10

kubectl get hpa app-target-hpa --watch

kubectl autoscale deployment app-target --cpu-percent=50 --min=1 --max=10

kubectl get hpa app-target --watch

kubectl port-forward svc/grafana 3001:80 -n default
kubectl port-forward -n default svc/prometheus-server 9090:80
kubectl port-forward service/locust-service 8089:8089


