1. Test Django app
```
python3 manage.py test
```

2. Build image
```
docker build -f Dockerfile \
    -t registry.hub.docker.com/kbekieszczuk/errander:latest \
    -t registry.hub.docker.com/kbekieszczuk/errander:v1 \
    .
```

3. Push container to DockerHub Container Registry
```
docker push registry.hub.docker.com/kbekieszczuk/errander --all-tags
```

4. Update secrets
```
kubectl delete secret errander-web-prod-env
kubectl create secret generic errander-web-prod-env --from-env-file=web/.env.prod
```

5. Update deployment
```
kubectl apply -f k8s/apps/errander.yaml
```

6. Wait for rollout to finish
```
kubectl rollout status deployment/errander-deployment
```

7. Get single pod name
```
export SINGLE_POD_NAME=$(kubectl get pod -l app=errander-deployment -o jsonpath="{.items[0].metadata.name}")
```

8. Migrate database
```
kubectl exec -it $SINGLE_POD_NAME -- bash /web/scripts/production/migrate.sh
```