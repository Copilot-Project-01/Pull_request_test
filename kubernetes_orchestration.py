"""
Kubernetes Orchestration Module

This module provides a comprehensive interface for managing Kubernetes resources
including deployments, services, pods, and namespaces.
"""

from kubernetes import client, config
from kubernetes.client.rest import ApiException
import logging
from typing import Dict, List, Optional


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KubernetesOrchestrator:
    """
    A class to manage Kubernetes cluster operations.
    
    This class provides methods to interact with Kubernetes API for managing
    deployments, services, pods, and other resources.
    """
    
    def __init__(self, config_file: Optional[str] = None, in_cluster: bool = False):
        """
        Initialize the Kubernetes orchestrator.
        
        Args:
            config_file: Path to kubeconfig file. If None, uses default location.
            in_cluster: If True, uses in-cluster configuration.
        """
        try:
            if in_cluster:
                config.load_incluster_config()
                logger.info("Loaded in-cluster Kubernetes configuration")
            elif config_file:
                config.load_kube_config(config_file=config_file)
                logger.info(f"Loaded Kubernetes configuration from {config_file}")
            else:
                config.load_kube_config()
                logger.info("Loaded Kubernetes configuration from default location")
            
            self.core_v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            self.batch_v1 = client.BatchV1Api()
            
        except Exception as e:
            logger.error(f"Failed to initialize Kubernetes client: {e}")
            raise
    
    def create_namespace(self, namespace: str) -> bool:
        """
        Create a new namespace.
        
        Args:
            namespace: Name of the namespace to create.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            namespace_manifest = client.V1Namespace(
                metadata=client.V1ObjectMeta(name=namespace)
            )
            self.core_v1.create_namespace(body=namespace_manifest)
            logger.info(f"Namespace '{namespace}' created successfully")
            return True
        except ApiException as e:
            if e.status == 409:
                logger.warning(f"Namespace '{namespace}' already exists")
            else:
                logger.error(f"Failed to create namespace: {e}")
            return False
    
    def delete_namespace(self, namespace: str) -> bool:
        """
        Delete a namespace.
        
        Args:
            namespace: Name of the namespace to delete.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            self.core_v1.delete_namespace(name=namespace)
            logger.info(f"Namespace '{namespace}' deleted successfully")
            return True
        except ApiException as e:
            logger.error(f"Failed to delete namespace: {e}")
            return False
    
    def list_namespaces(self) -> List[str]:
        """
        List all namespaces in the cluster.
        
        Returns:
            List of namespace names.
        """
        try:
            namespaces = self.core_v1.list_namespace()
            namespace_names = [ns.metadata.name for ns in namespaces.items]
            logger.info(f"Found {len(namespace_names)} namespaces")
            return namespace_names
        except ApiException as e:
            logger.error(f"Failed to list namespaces: {e}")
            return []
    
    def create_deployment(
        self,
        name: str,
        namespace: str,
        image: str,
        replicas: int = 1,
        container_port: Optional[int] = None,
        env_vars: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Create a deployment.
        
        Args:
            name: Name of the deployment.
            namespace: Namespace for the deployment.
            image: Container image to use.
            replicas: Number of replicas.
            container_port: Container port to expose.
            env_vars: Environment variables as key-value pairs.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Build container spec
            container = client.V1Container(
                name=name,
                image=image,
                env=[
                    client.V1EnvVar(name=k, value=v)
                    for k, v in (env_vars or {}).items()
                ]
            )
            
            if container_port:
                container.ports = [client.V1ContainerPort(container_port=container_port)]
            
            # Build pod template
            template = client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": name}),
                spec=client.V1PodSpec(containers=[container])
            )
            
            # Build deployment spec
            spec = client.V1DeploymentSpec(
                replicas=replicas,
                selector=client.V1LabelSelector(match_labels={"app": name}),
                template=template
            )
            
            # Create deployment object
            deployment = client.V1Deployment(
                api_version="apps/v1",
                kind="Deployment",
                metadata=client.V1ObjectMeta(name=name),
                spec=spec
            )
            
            self.apps_v1.create_namespaced_deployment(
                namespace=namespace,
                body=deployment
            )
            logger.info(f"Deployment '{name}' created in namespace '{namespace}'")
            return True
        except ApiException as e:
            logger.error(f"Failed to create deployment: {e}")
            return False
    
    def delete_deployment(self, name: str, namespace: str) -> bool:
        """
        Delete a deployment.
        
        Args:
            name: Name of the deployment.
            namespace: Namespace of the deployment.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            self.apps_v1.delete_namespaced_deployment(
                name=name,
                namespace=namespace
            )
            logger.info(f"Deployment '{name}' deleted from namespace '{namespace}'")
            return True
        except ApiException as e:
            logger.error(f"Failed to delete deployment: {e}")
            return False
    
    def scale_deployment(self, name: str, namespace: str, replicas: int) -> bool:
        """
        Scale a deployment to a specified number of replicas.
        
        Args:
            name: Name of the deployment.
            namespace: Namespace of the deployment.
            replicas: Desired number of replicas.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Get the deployment
            deployment = self.apps_v1.read_namespaced_deployment(name, namespace)
            
            # Update replicas
            deployment.spec.replicas = replicas
            
            # Patch the deployment
            self.apps_v1.patch_namespaced_deployment(
                name=name,
                namespace=namespace,
                body=deployment
            )
            logger.info(f"Deployment '{name}' scaled to {replicas} replicas")
            return True
        except ApiException as e:
            logger.error(f"Failed to scale deployment: {e}")
            return False
    
    def list_deployments(self, namespace: str = "default") -> List[str]:
        """
        List all deployments in a namespace.
        
        Args:
            namespace: Namespace to query (default: "default").
            
        Returns:
            List of deployment names.
        """
        try:
            deployments = self.apps_v1.list_namespaced_deployment(namespace)
            deployment_names = [d.metadata.name for d in deployments.items]
            logger.info(f"Found {len(deployment_names)} deployments in '{namespace}'")
            return deployment_names
        except ApiException as e:
            logger.error(f"Failed to list deployments: {e}")
            return []
    
    def create_service(
        self,
        name: str,
        namespace: str,
        selector: Dict[str, str],
        port: int,
        target_port: int,
        service_type: str = "ClusterIP"
    ) -> bool:
        """
        Create a Kubernetes service.
        
        Args:
            name: Name of the service.
            namespace: Namespace for the service.
            selector: Label selector to match pods.
            port: Service port.
            target_port: Target port on pods.
            service_type: Type of service (ClusterIP, NodePort, LoadBalancer).
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            service = client.V1Service(
                api_version="v1",
                kind="Service",
                metadata=client.V1ObjectMeta(name=name),
                spec=client.V1ServiceSpec(
                    selector=selector,
                    ports=[client.V1ServicePort(
                        port=port,
                        target_port=target_port
                    )],
                    type=service_type
                )
            )
            
            self.core_v1.create_namespaced_service(
                namespace=namespace,
                body=service
            )
            logger.info(f"Service '{name}' created in namespace '{namespace}'")
            return True
        except ApiException as e:
            logger.error(f"Failed to create service: {e}")
            return False
    
    def delete_service(self, name: str, namespace: str) -> bool:
        """
        Delete a service.
        
        Args:
            name: Name of the service.
            namespace: Namespace of the service.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            self.core_v1.delete_namespaced_service(
                name=name,
                namespace=namespace
            )
            logger.info(f"Service '{name}' deleted from namespace '{namespace}'")
            return True
        except ApiException as e:
            logger.error(f"Failed to delete service: {e}")
            return False
    
    def list_pods(self, namespace: str = "default") -> List[Dict]:
        """
        List all pods in a namespace with their status.
        
        Args:
            namespace: Namespace to query (default: "default").
            
        Returns:
            List of dictionaries containing pod information.
        """
        try:
            pods = self.core_v1.list_namespaced_pod(namespace)
            pod_info = [
                {
                    "name": pod.metadata.name,
                    "status": pod.status.phase,
                    "ip": pod.status.pod_ip,
                    "node": pod.spec.node_name
                }
                for pod in pods.items
            ]
            logger.info(f"Found {len(pod_info)} pods in namespace '{namespace}'")
            return pod_info
        except ApiException as e:
            logger.error(f"Failed to list pods: {e}")
            return []
    
    def get_pod_logs(
        self,
        pod_name: str,
        namespace: str = "default",
        tail_lines: Optional[int] = None
    ) -> str:
        """
        Get logs from a pod.
        
        Args:
            pod_name: Name of the pod.
            namespace: Namespace of the pod.
            tail_lines: Number of lines from the end of the logs to show.
            
        Returns:
            Pod logs as a string.
        """
        try:
            logs = self.core_v1.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                tail_lines=tail_lines
            )
            logger.info(f"Retrieved logs for pod '{pod_name}'")
            return logs
        except ApiException as e:
            logger.error(f"Failed to get pod logs: {e}")
            return ""
    
    def delete_pod(self, pod_name: str, namespace: str = "default") -> bool:
        """
        Delete a pod.
        
        Args:
            pod_name: Name of the pod.
            namespace: Namespace of the pod.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            self.core_v1.delete_namespaced_pod(
                name=pod_name,
                namespace=namespace
            )
            logger.info(f"Pod '{pod_name}' deleted from namespace '{namespace}'")
            return True
        except ApiException as e:
            logger.error(f"Failed to delete pod: {e}")
            return False
    
    def get_cluster_info(self) -> Dict:
        """
        Get basic cluster information.
        
        Returns:
            Dictionary containing cluster information.
        """
        try:
            version = client.VersionApi().get_code()
            nodes = self.core_v1.list_node()
            
            cluster_info = {
                "version": f"{version.major}.{version.minor}",
                "git_version": version.git_version,
                "platform": version.platform,
                "node_count": len(nodes.items),
                "nodes": [node.metadata.name for node in nodes.items]
            }
            logger.info("Retrieved cluster information")
            return cluster_info
        except ApiException as e:
            logger.error(f"Failed to get cluster info: {e}")
            return {}


def main():
    """
    Example usage of the KubernetesOrchestrator class.
    """
    try:
        # Initialize orchestrator
        k8s = KubernetesOrchestrator()
        
        # Get cluster info
        cluster_info = k8s.get_cluster_info()
        print("Cluster Information:")
        for key, value in cluster_info.items():
            print(f"  {key}: {value}")
        
        # List namespaces
        namespaces = k8s.list_namespaces()
        print(f"\nNamespaces: {', '.join(namespaces)}")
        
        # List pods in default namespace
        pods = k8s.list_pods("default")
        print(f"\nPods in default namespace:")
        for pod in pods:
            print(f"  - {pod['name']}: {pod['status']}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")


if __name__ == "__main__":
    main()
