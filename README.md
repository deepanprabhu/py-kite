1) Install mysql - kubectl apply -f mysql-deployment.yaml, kubectl apply -f mysql-secret.yaml, kubectl apply -f mysql-storage.yaml 
2) eval $(minikube docker-env)
3) docker built -t myservice .
4) docker build -f ModelDockerfile -t mymodel .
5) Install roles - kubectl apply -f job-role-deployment.yaml
6) Install services - kubectl apply -f fastapi-deployment.yaml
7) kubectl port-forward service/mysql 3306:3306


There are 2 services,

1) main.py - fastapi - writes and reads from mysql
2) modelthreads2.py - responsible for reading from mysql, the jobs which are queued, and spawns a model to update status 
to finished - this stays alive and processes models.
