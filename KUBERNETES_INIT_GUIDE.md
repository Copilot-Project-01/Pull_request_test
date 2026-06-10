# Kubernetes Cluster Initialization Guide

## Overview

This guide provides comprehensive instructions for initializing a Kubernetes cluster using kubeadm. It covers prerequisites, installation steps, and post-installation configuration.

## Prerequisites

### System Requirements

- **Operating System**: Ubuntu 20.04 LTS or later
- **Memory**: Minimum 2GB RAM (4GB recommended)
- **CPU**: 2 cores minimum
- **Disk Space**: 20GB minimum
- **Network**: Full network connectivity between all machines

### Required Ports

#### Control Plane Node

| Protocol | Direction | Port Range | Purpose                 |
|----------|-----------|------------|-------------------------|
| TCP      | Inbound   | 6443       | Kubernetes API server   |
| TCP      | Inbound   | 2379-2380  | etcd server client API  |
| TCP      | Inbound   | 10250      | Kubelet API             |
| TCP      | Inbound   | 10259      | kube-scheduler          |
| TCP      | Inbound   | 10257      | kube-controller-manager |

#### Worker Nodes

| Protocol | Direction | Port Range  | Purpose           |
|----------|-----------|-------------|-------------------|
| TCP      | Inbound   | 10250       | Kubelet API       |
| TCP      | Inbound   | 30000-32767 | NodePort Services |

## Installation Steps

### Step 1: Prepare the System

#### Disable Swap

Kubernetes requires swap to be disabled:

```bash
sudo swapoff -a
sudo sed -i '/ swap / s/^/#/' /etc/fstab
```

#### Load Required Kernel Modules

```bash
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF

sudo modprobe overlay
sudo modprobe br_netfilter
```

#### Configure Sysctl Parameters

```bash
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

sudo sysctl --system
```

### Step 2: Install Container Runtime

#### Install Containerd

```bash
sudo apt-get update
sudo apt-get install -y containerd

sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml

# Enable SystemdCgroup
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml

sudo systemctl restart containerd
sudo systemctl enable containerd
```

### Step 3: Install Kubernetes Components

```bash
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg

# Add Kubernetes repository
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-archive-keyring.gpg

echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list

# Install kubelet, kubeadm, and kubectl
sudo apt-get update
sudo apt-get install -y kubelet=1.28.0-00 kubeadm=1.28.0-00 kubectl=1.28.0-00
sudo apt-mark hold kubelet kubeadm kubectl
```

### Step 4: Initialize the Cluster

#### On the Control Plane Node

```bash
sudo kubeadm init \
  --pod-network-cidr=192.168.0.0/16 \
  --service-cidr=10.96.0.0/12 \
  --control-plane-endpoint=<CONTROL_PLANE_IP>:6443
```

#### Configure kubectl

```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

### Step 5: Install Network Plugin

#### Calico

```bash
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
```

#### Flannel (Alternative)

```bash
kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml
```

### Step 6: Join Worker Nodes

On each worker node, run the join command provided by `kubeadm init`:

```bash
sudo kubeadm join <CONTROL_PLANE_IP>:6443 \
  --token <TOKEN> \
  --discovery-token-ca-cert-hash sha256:<HASH>
```

## Verification

### Check Node Status

```bash
kubectl get nodes
```

Expected output:
```
NAME           STATUS   ROLES           AGE   VERSION
control-plane  Ready    control-plane   5m    v1.28.0
worker-1       Ready    <none>          2m    v1.28.0
worker-2       Ready    <none>          2m    v1.28.0
```

### Check System Pods

```bash
kubectl get pods -n kube-system
```

## Troubleshooting

### Common Issues

#### Nodes Not Ready

Check kubelet status:
```bash
sudo systemctl status kubelet
sudo journalctl -u kubelet -f
```

#### Network Plugin Issues

Verify pod network:
```bash
kubectl get pods -n kube-system | grep -E 'calico|flannel'
```

#### Certificate Errors

Reset and reinitialize:
```bash
sudo kubeadm reset
sudo kubeadm init [options]
```

## Best Practices

1. **High Availability**: Deploy multiple control plane nodes for production
2. **Security**: Enable RBAC and network policies
3. **Monitoring**: Install monitoring tools (Prometheus, Grafana)
4. **Backup**: Regularly backup etcd data
5. **Updates**: Keep Kubernetes components updated

## Additional Configuration

### Enable kubectl Autocompletion

```bash
echo 'source <(kubectl completion bash)' >> ~/.bashrc
source ~/.bashrc
```

### Set Default Namespace

```bash
kubectl config set-context --current --namespace=<NAMESPACE>
```

## References

- [Official Kubernetes Documentation](https://kubernetes.io/docs/)
- [kubeadm Documentation](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/)
- [Container Runtime Documentation](https://kubernetes.io/docs/setup/production-environment/container-runtimes/)

## Conclusion

Following this guide will help you successfully initialize a Kubernetes cluster. For production deployments, consider using managed Kubernetes services or production-grade installation tools like kubespray or kops.
