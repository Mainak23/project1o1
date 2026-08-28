
# Enterprise ML Platform Architecture

This repository defines the multi-tier architecture patterns for scaling Machine Learning workloads from a Single-Node Proof-of-Concept (POC) to a fully automated, resilient Production environment.

---

## 1. Proof-of-Concept (POC) Architecture

The POC setup is optimized for rapid experimentation, validation, and single-node deployment using lightweight components.

```mermaid
graph TD
    subgraph Data Pipeline
        A[Source Systems] -->|Ingestion| B[Kafka]
        B --> C[Staging DB / Raw Zone]
        C --> D[Data Processing / Cleaning]
        D --> E[(S3 / MinIO)]
    end

    subgraph CI Pipeline - Jenkins
        F[Code Commit] --> G[Build & Unit Test]
        G --> H[Data Validation]
        H --> I[Model Training & Eval]
        I --> J[Compare & Commit]
    end

    subgraph Deployment - Single Node AKS
        J --> K[Container Registry]
        K --> L[Kubectl Apply]
        L --> M[Traefik Ingress]
        M --> N[ml-serving Pod]
    end

    E -.->|Processed Data| I
    N --> O[MLflow Tracking]



graph TD
    subgraph Production Data & CI
        A[Source Systems] -->|Kafka| B[Staging DB]
        B --> C[Data Processing]
        C --> D[(S3 / Data Lake)]
        
        E[Code Commit] --> F[Build & Test]
        F --> G[Quality Gates: Trivy/SonarQube]
        G --> H[Model Training]
        H --> I[Container Registry]
    end

    subgraph GitOps & Scalable Serving
        I -->|Argo CD Sync| J[K8s Multi-Node Cluster]
        J --> K[API Gateway / Ingress]
        K --> L[HPA / Autoscaler]
        L --> M[ml-serving Pod 1..n]
    end

    D -.->|Delta/Parquet| H
    M --> N[MLflow Tracking]
    M --> O[Prometheus & Grafana]
