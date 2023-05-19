1. Test Django app
```
python3 manage.py test
```

2. Build and push Docker image with docker/build-push-action
```
with:
  context: web
  file: ./web/Dockerfile
  push: true
  tags: kbekieszczuk/errander:latest, kbekieszczuk/errander:${{ github.sha }}
  cache-from: |
```

3. Update secrets
```
kubectl delete secret errander-web-prod-env
kubectl create secret generic errander-web-prod-env --from-env-file=web/.env.prod
```

4. Update and restart deployment
```
kubectl apply -f k8s/apps/errander.yaml
kubectl set image deployment/errander-deployment errander=${{ secrets.DOCKERHUB_USERNAME }}/errander:${{ github.sha }}
kubectl rollout restart deployment/errander-deployment
```

5. Wait for rollout to finish
```
kubectl rollout status deployment/errander-deployment
```

6. Get single pod name
```
export SINGLE_POD_NAME=$(kubectl get pod -l app=errander-deployment -o jsonpath="{.items[0].metadata.name}")
```

7. Migrate database
```
kubectl exec -it $SINGLE_POD_NAME -- bash /web/scripts/production/migrate.sh
```