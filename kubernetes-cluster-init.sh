#!/bin/bash
################################################################################
# Kubernetes Cluster Initialization Script
# 
# This script automates the initialization of a Kubernetes cluster using kubeadm
# It includes pre-flight checks, system configuration, and cluster setup
################################################################################

set -e

# Configuration Variables
KUBERNETES_VERSION="1.28.0"
POD_NETWORK_CIDR="10.244.0.0/16"
SERVICE_CIDR="10.96.0.0/12"
CONTROL_PLANE_ENDPOINT=""
LOG_FILE="/var/log/k8s-init.log"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Pre-flight checks
preflight_checks() {
    log "Starting pre-flight checks..."
    
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        error "This script must be run as root"
    fi
    
    # Check system requirements
    TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$TOTAL_MEM" -lt 2 ]; then
        warning "System has less than 2GB RAM. Kubernetes may not run optimally."
    fi
    
    # Check if required ports are available
    log "Checking required ports..."
    REQUIRED_PORTS=(6443 2379 2380 10250 10251 10252)
    for port in "${REQUIRED_PORTS[@]}"; do
        if netstat -tuln | grep -q ":$port "; then
            warning "Port $port is already in use"
        fi
    done
    
    log "Pre-flight checks completed"
}

# Disable swap (required for Kubernetes)
disable_swap() {
    log "Disabling swap..."
    swapoff -a
    sed -i '/ swap / s/^/#/' /etc/fstab
    log "Swap disabled successfully"
}

# Configure kernel modules
configure_kernel_modules() {
    log "Configuring kernel modules..."
    
    cat <<EOF | tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF
    
    modprobe overlay
    modprobe br_netfilter
    
    log "Kernel modules configured"
}

# Configure sysctl parameters
configure_sysctl() {
    log "Configuring sysctl parameters..."
    
    cat <<EOF | tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF
    
    sysctl --system
    log "Sysctl parameters configured"
}

# Install container runtime (containerd)
install_containerd() {
    log "Installing containerd..."
    
    apt-get update
    apt-get install -y containerd
    
    # Configure containerd
    mkdir -p /etc/containerd
    containerd config default | tee /etc/containerd/config.toml
    
    # Enable SystemdCgroup
    sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
    
    systemctl restart containerd
    systemctl enable containerd
    
    log "Containerd installed and configured"
}

# Install Kubernetes components
install_kubernetes() {
    log "Installing Kubernetes components..."
    
    # Add Kubernetes repository
    apt-get update
    apt-get install -y apt-transport-https ca-certificates curl
    
    curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /etc/apt/keyrings/kubernetes-archive-keyring.gpg
    
    echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | tee /etc/apt/sources.list.d/kubernetes.list
    
    apt-get update
    apt-get install -y kubelet kubeadm kubectl
    apt-mark hold kubelet kubeadm kubectl
    
    log "Kubernetes components installed"
}

# Initialize Kubernetes cluster
initialize_cluster() {
    log "Initializing Kubernetes cluster..."
    
    INIT_CMD="kubeadm init --pod-network-cidr=$POD_NETWORK_CIDR --service-cidr=$SERVICE_CIDR"
    
    if [ -n "$CONTROL_PLANE_ENDPOINT" ]; then
        INIT_CMD="$INIT_CMD --control-plane-endpoint=$CONTROL_PLANE_ENDPOINT"
    fi
    
    $INIT_CMD | tee -a "$LOG_FILE"
    
    log "Cluster initialized successfully"
}

# Configure kubectl for non-root user
configure_kubectl() {
    log "Configuring kubectl..."
    
    mkdir -p $HOME/.kube
    cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
    chown $(id -u):$(id -g) $HOME/.kube/config
    
    log "kubectl configured"
}

# Install network plugin (Calico)
install_network_plugin() {
    log "Installing network plugin (Calico)..."
    
    kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
    
    log "Network plugin installed"
}

# Main execution
main() {
    log "Starting Kubernetes cluster initialization..."
    
    preflight_checks
    disable_swap
    configure_kernel_modules
    configure_sysctl
    install_containerd
    install_kubernetes
    initialize_cluster
    configure_kubectl
    install_network_plugin
    
    log "Kubernetes cluster initialization completed successfully!"
    log "Join command has been saved to $LOG_FILE"
    log "Run 'kubectl get nodes' to verify cluster status"
}

# Run main function
main
