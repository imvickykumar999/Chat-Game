# `Call GPT`

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
````

![image](https://github.com/user-attachments/assets/5bc9831c-ac38-4f8f-a3a8-d761b66a5ce2)


| Action | Command | Purpose |
| :--- | :--- | :--- |
| **Download Image** | `docker pull imvickykumar999/myadk-django:latest` | Downloads the application image from Docker Hub to your local machine. |
| **Initial Run** | `docker run -d -p 8000:8000 --name myadk-web-production imvickykumar999/myadk-django:latest` | Creates and starts a **new** container from the image in detached mode, naming it `myadk-web-production` and mapping the ports. |
| **Stop Container** | `docker stop myadk-web-production` | **Gracefully stops** the running container. |
| **Start Container** | `docker start myadk-web-production` | **Restarts** the previously stopped container. |
| **View Running** | `docker ps` | Lists all currently **running** containers. |
| **View All** | `docker ps -a` | Lists **all** containers (running, stopped, etc.). |
| **Remove Container** | `docker rm myadk-web-production` | **Deletes** the container from your system (must be stopped first). |
| **Force Stop** | `docker kill myadk-web-production` | Immediately **forces** the container to stop (less graceful than `docker stop`). |

-----

## Kubernetes Deployment & Local Access Guide

This guide details the steps required to deploy the `myadk-django` Docker image onto a local Kubernetes cluster (Minikube) within your Codespace environment and access it locally via port 8000.

### Prerequisites

  * **Docker** is installed (available by default in Codespaces).
  * The Kubernetes manifest file (`k8s_deployment.yaml`) must be present in the root directory.

-----

### 1\. Minikube Setup & Cluster Start

First, install and start the local Kubernetes cluster:

**A. Install Minikube**

Download the binary and install it to make the `minikube` command available:

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

**B. Start the Cluster**

Start Minikube using the Docker driver. This configures the `kubectl` tool automatically.

```bash
minikube start --driver=docker
```

**C. Verify Connection**

Ensure the cluster is running:

```bash
kubectl get nodes
```

*(Expected Output: `minikube` with `STATUS: Ready`)*

-----

### 2\. Secure Deployment

These steps deploy your application and securely inject your API key.

**A. Securely Inject the API Key (Secret)**

Creates a Kubernetes Secret to pass your API key to the container's `YOUR_API_KEY` environment variable.

```bash
kubectl create secret generic myadk-secrets --from-literal=api-key='YOUR_ACTUAL_API_KEY'
```

**B. Apply the Kubernetes Manifest**

Creates the Deployment (3 running containers) and the LoadBalancer Service defined in your YAML.

```bash
kubectl apply -f k8s_deployment.yaml
```

**C. Monitor Deployment Status**

Wait for the application Pods to be fully up and running:

```bash
kubectl rollout status deployment/myadk-web-deployment
```

-----

### 3\. Local Access and Debugging

Since your Django application expects traffic on port **8000** and we cannot use privileged ports, we forward the service to port 8000.

**A. Forward Traffic to Port 8000**

Run this command in a **new, separate terminal tab** and **leave it running**. This resolves the **permission denied** and **CSRF verification** issues by routing the traffic through the expected port.

```bash
kubectl port-forward service/myadk-web-service 8000:8000
```

**B. Access the Application**

Access the application via your Codespace's **"PORTS"** tab on port **8000**, or navigate directly to:

`http://localhost:8000`

-----

### Cleanup (Stopping the Cluster)

Use these commands to stop and remove all resources when you are finished testing:

| Action | Command | Purpose |
| :--- | :--- | :--- |
| **Stop Forwarding** | (In the terminal running `kubectl port-forward`): **Press `Ctrl+C`** | Stops the local access tunnel. |
| **Delete App** | `kubectl delete -f k8s_deployment.yaml` | Deletes the Deployment and Service. |
| **Stop Minikube** | `minikube stop` | Shuts down the local Kubernetes virtual machine. |
| **Delete Cluster** | `minikube delete` | Completely removes the Minikube cluster and configuration. |

---

### How to Run This Script

1.  **Save the file:** Save the content above as `deploy.sh` in your project root.
2.  **Make it executable:** Run `chmod +x deploy.sh` in your terminal.
3.  **Execute:** Run `./deploy.sh`
4.  The script will print the process ID (`FORWARD_PID`) and instructions for accessing and cleaning up the service.
