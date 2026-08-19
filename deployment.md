MLflow Model Registry
        │
        │ candidate model version
        ▼
      KServe
        │
        ├── model server
        ├── autoscaling
        ├── canary traffic
        ├── rolling revision
        └── inference API
        │
        ▼
      Client


                 MLflow
                   │
             candidate alias
                   │
                   ▼
          deploy_candidate.py
                   │
        ┌──────────┴───────────┐
        │                      │
   model version          artifact URI
        │                      │
        └──────────┬───────────┘
                   ▼
            Generate YAML
                   │
          ┌────────┴────────┐
          │                 │
      KServe config     MinIO access
          │                 │
          └────────┬────────┘
                   ▼
             kubectl apply
                   │
                   ▼
                KServe
             ┌─────┴─────┐
             │           │
         champion    candidate
             │           │
            90%         10%


ls -lah /var/lib/jenkins/workspace/mlops101


┌──────────────────────────────────────────────┐
│                 Linux machine                │
│                                              │
│  ┌───────────────┐       ┌───────────────┐   │
│  │    Jenkins    │       │      K3s      │   │
│  │               │       │               │   │
│  │ Podman        │       │ Kubernetes    │   │
│  │ MLflow        │       │ KServe        │   │
│  │ MinIO         │       │               │   │
│  │ Build images  │       │ Serve models  │   │
│  └───────┬───────┘       └───────▲───────┘   │
│          │                         │           │
│          │ kubectl                 │           │
│          └─────────────────────────┘           │
│                                              │
└──────────────────────────────────────────────┘


KServe is not a cluster. K3s is your Kubernetes cluster. KServe is a Kubernetes application/platform installed inside that cluster.

┌─────────────────────────────────────┐
│              K3s cluster            │
│                                     │
│  Kubernetes                         │
│       │                             │
│       ├── KServe                    │
│       │    ├── InferenceService     │
│       │    ├── autoscaling          │
│       │    └── canary               │
│       │                             │
│       ├── your other workloads      │
│       └── ...                       │
└─────────────────────────────────────┘

Linux
  │
  └── K3s
       │
       └── Kubernetes cluster
            │
            └── KServe
                 │
                 └── InferenceService
                      │
                      └── Model Pods


sudo systemctl start k3s
kubectl get nodes

kube-system
├── coredns
├── traefik
├── metrics-server
├── local-path-provisioner
└── svclb-traefik

| Component                  | Simple meaning              | Why you need it                           |
| -------------------------- | --------------------------- | ----------------------------------------- |
| **CoreDNS**                | Kubernetes' internal DNS    | Lets pods find each other by name         |
| **Traefik**                | Traffic/HTTP router         | Lets external HTTP traffic reach services |
| **Metrics Server**         | Collects CPU/memory metrics | Needed for resource-based autoscaling     |
| **Local Path Provisioner** | Creates local storage       | Gives pods persistent/local volumes       |
| **svclb-traefik**          | K3s load-balancer helper    | Exposes Traefik outside the cluster       |

                     K3s
                      │
        ┌─────────────┼─────────────┐
        │             │             │
     CoreDNS       Traefik      Metrics Server
        │             │             │
        │             │             │
        │          Networking     Scaling
        │
   Service discovery

                   K3s
                 │
        ┌────────┴────────┐
        │                 │
   Kubernetes         Metrics Server
   knows pods         knows resource usage
        │                 │
        └────────┬────────┘
                 ▼
             Autoscaler
                 │
          ┌──────┴──────┐
          ▼             ▼
       1 pod          3 pods

kubectl top nodes

Metrics Server
    │
    └── Kubernetes resource metrics
                │
                ▼
          HPA-style scaling


KServe/Knative
    │
    └── inference-serving autoscaling


Deployment
+
Service
+
autoscaling
+
model-serving configuration
+
canary
+
model storage configuration

WITHOUT KServe

Kubernetes
 ├── Deployment
 ├── Service
 ├── HPA
 ├── Ingress
 ├── rollout configuration
 └── your FastAPI/model server


WITH KServe

Kubernetes
 └── KServe
      └── InferenceService
           ├── serving
           ├── scaling
           ├── traffic management
           └── model configuration


             Node
              │
       ┌──────┴───────┐
       │              │
  ML-serving       Other Pod
       │              │
 request:          request:
 500m CPU          100m CPU
 512Mi RAM         128Mi RAM
       │
 limit:
 2 CPU
 2Gi RAM


NAME     CPU(cores)   CPU(%)   MEMORY(bytes)   MEMORY(%)

Exactly — this output is where you start making resource decisions for your Kubernetes cluster.

NAME     CPU(cores)   CPU(%)   MEMORY(bytes)   MEMORY(%)
mainak   738m         18%      6397Mi          81%

Let's decode it.

1. CPU
738m
18%

m means millicores.

1000m = 1 CPU core

So:

738m = 0.738 CPU cores

Your node is using only:

18% CPU

So CPU is not currently your bottleneck.

2. Memory is the concern

You have:

6397Mi
81%

So Kubernetes currently sees roughly:

6.4 GiB RAM being used

and:

81% of available node memory

That means your machine is already fairly memory-loaded.

If your machine has roughly 8 GB RAM:

Total       ≈ 7.7 GiB
Used        ≈ 6.4 GiB
Available   ≈ 1.3 GiB

So if you deploy a model that needs another 1–2 GB:

Current
6.4 GB
  +
Model
2.0 GB
  =
8.4 GB

💥 You don't have enough RAM.

              ML-serving container
                     │
        ┌────────────┴────────────┐
        │                         │
      REQUEST                    LIMIT
        │                         │
 CPU   250m                    CPU   1 core
 RAM   512Mi                   RAM   1Gi

 Jenkins
   │
   │ build #17
   ▼
ml-serving:17
   │
   │ Kubernetes starts it
   ▼
┌─────────────────────────┐
│ Container               │
│                         │
│ FastAPI                 │
│                         │
│ 0.0.0.0:8080            │
└───────────┬─────────────┘
            │
            │ port 8080
            ▼
        Kubernetes

        Your container can still listen on 8080 even if the host/node's 8080 is already occupied. Kubernetes has its own networking layer.


Podman
┌───────────────────────────────┐
│ ml-serving-test-19            │
│                               │
│ MLFLOW_TRACKING_URI=...       │
│ MLFLOW_S3_ENDPOINT_URL=...    │
│ AWS_ACCESS_KEY_ID=...         │
│ AWS_SECRET_ACCESS_KEY=...     │
└───────────────────────────────┘

Then Kubernetes starts a completely new container
kubectl apply -f deployment.yaml

Podman container
       ❌
       │
       │ completely separate
       │
       ▼
Kubernetes Pod
┌───────────────────────────────┐
│ ml-serving                    │
│                               │
│ ??? MLFLOW_TRACKING_URI       │
│ ??? AWS_ACCESS_KEY_ID         │
└───────────────────────────────┘

env:
  - name: MLFLOW_TRACKING_URI
    value: "http://mlflow:5000"

  - name: MLFLOW_S3_ENDPOINT_URL
    value: "http://minio:9000"

  - name: AWS_ACCESS_KEY_ID
    value: "minioadmin"

  - name: AWS_SECRET_ACCESS_KEY
    value: "minioadmin123"


This:

http://mlflow:5000
http://minio:9000

worked in Podman because you created:
--network ml-network

and Podman can resolve:
mlflow
minio

through that network.

Your Kubernetes pods cannot automatically use Podman's ml-network.

They live inside Kubernetes networking.

So eventually your architecture should look like:

Kubernetes
│
├── ml-serving
│
├── MLflow Service
│      └── mlflow:5000
│
└── MinIO Service
       └── minio:9000

       containers:
  - name: ml-serving
    image: ml-serving:19

    env:
      - name: MLFLOW_TRACKING_URI
        value: "http://mlflow:5000"

And once you move entirely to Kubernetes, the Podman -e options are no longer relevant to the Kubernetes deploymen


Then how does ml-serving find MLflow?

This is where Kubernetes Service + DNS comes in.

Suppose you create:

apiVersion: v1
kind: Service
metadata:
  name: mlflow
spec:
  selector:
    app: mlflow


  ports:
    - port: 5000
      targetPort: 5000

Kubernetes creates a DNS name:

mlflow

Then your serving pod can simply use:

env:
  - name: MLFLOW_TRACKING_URI
    value: "http://mlflow:5000"

ghcr.io/mainak23/ml-serving:19
│       │       │          │
│       │       │          └── tag/version
│       │       └───────────── image name
│       └───────────────────── GitHub owner
└───────────────────────────── registry

ls -lah /var/lib/jenkins/workspace/mlops101

mlops101
│
├── model-deployment.yaml
│
│       cp
│       ↓
│
└── deployment-repo
        │
        └── model-deployment.yaml
                │
                ↓
             git add
                ↓
             git commit
                ↓
             git push
                ↓
     github.com/Mainak23/deployment
