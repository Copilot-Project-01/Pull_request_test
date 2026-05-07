# Kubernetes Cluster Practice Simulation

This directory contains Kubernetes manifests for practising cluster setup and management.

## Files

- `namespace.yaml` - Creates a dedicated namespace (`practice-cluster`) for the simulation
- `deployment.yaml` - Deploys a sample nginx application with 2 replicas
- `service.yaml` - Exposes the deployment within the cluster via a ClusterIP service

## Prerequisites

- A running Kubernetes cluster (e.g. minikube, kind, or a cloud provider)
- `kubectl` configured to connect to your cluster

## Usage

### 1. Create the namespace

```bash
kubectl apply -f namespace.yaml
```

### 2. Deploy the sample application

```bash
kubectl apply -f deployment.yaml
```

### 3. Create the service

```bash
kubectl apply -f service.yaml
```

### 4. Verify the resources

```bash
kubectl get all -n practice-cluster
```

### 5. Clean up

```bash
kubectl delete namespace practice-cluster
```
