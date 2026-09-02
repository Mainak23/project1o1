# ML Platform: Multi-Tier Architecture Analysis & Repository Guide

This document provides a comprehensive analysis of the transition from a **Proof-of-Concept (POC)** Machine Learning platform to a resilient, enterprise-grade **Production Architecture**. It includes detailed workflow breakdowns and a production-ready `README.md` containing a fully unified Mermaid diagram script.

---

## Executive Summary

Scaling machine learning systems requires moving away from static notebooks and manual deployments toward automated pipelines, robust quality gates, GitOps workflows, and horizontal autoscaling. 

The architecture diagram analyzed contrasts two operational tiers:
1. **POC Architecture (Single-Node AKS):** Designed for agility, rapid model iteration, and lightweight validation.
2. **Production Architecture (Multi-Node AKS + Argo CD):** Designed for high availability, automated security scanning, continuous delivery, and dynamic load handling.

---

## Comparative Architectural Breakdown

| Dimension | Proof-of-Concept (POC) | Production Architecture |
| :--- | :--- | :--- |
| **Infrastructure** | Single-node Azure Kubernetes Service (AKS) | Multi-node AKS cluster with dedicated worker nodes |
| **Data & Storage** | Local or single-instance MinIO (S3-compatible) | Scalable Enterprise Data Lake (Parquet / Delta Lake) |
| **CI/CD & Testing** | Standard build, unit tests, training, and registry push | Jenkins + rigorous **Quality Gates** (Trivy, SonarQube, Dependency & Performance checks, Model Drift tests) |
| **Deployment Method** | Manual or scripted `kubectl apply` | Declarative **GitOps Deployment** via Argo CD using Helm/Kustomize |
| **Model Serving** | Static single pod deployment (`ml-serving`) | Horizontal Pod Autoscaler (HPA) with multi-pod load balancing |
| **Observability** | Basic MLflow tracking (Logs & Metrics) | MLflow + Prometheus & Grafana for advanced monitoring and alerting |

# Enterprise ML Platform Architecture

This repository defines the multi-tier architecture patterns for scaling Machine Learning workloads from a Single-Node Proof-of-Concept (POC) to a fully automated, resilient Production environment.

<p align="center">
  <img src="images/architechture.png" width="900">
</p>

<p align="center">
  <b>Production ML Serving Architecture</b>
</p>



---

## 1. Proof-of-Concept (POC) Architecture

The POC setup is optimized for rapid experimentation, validation, and single-node deployment using lightweight components.
```mermaid
graph TD

    %% =========================
    %% DATA PIPELINE
    %% =========================
    subgraph DP["Data / ML Pipeline"]

        A["Source Systems"]
        B["Kafka"]
        C["Staging DB / Raw Zone"]
        D["Airflow"]
        E["Data Processing / Cleaning"]
        F["Data Validation"]
        G[("S3 / MinIO")]

        A -->|Ingestion| B
        B --> C
        C --> D
        D --> E
        E --> F
        F --> G

        H["Model Training"]
        I["MLflow Tracking"]
        J["Model Evaluation"]
        K["Model Registry"]

        G --> H
        H --> I
        I --> J
        J --> K
    end

    %% =========================
    %% CI/CD
    %% =========================
    subgraph CICD["CI/CD Pipeline"]

        L["Developer"]
        M["Git"]
        N["Jenkins"]
        O["Test / Security Scan"]
        P["Build Container"]
        Q["GHCR"]

        L -->|Commit| M
        M --> N
        N --> O
        O --> P
        P --> Q
    end

    %% =========================
    %% MODEL DEPLOYMENT
    %% =========================
    subgraph SERVING["Model Serving"]

        R["K3s / Kubernetes"]
        S["FastAPI ML Serving"]
        T["Model Inference"]

        Q -->|Deploy Image| R
        R --> S
        S --> T
    end

    %% =========================
    %% MODEL PROMOTION
    %% =========================
    K -->|Promoted Model| N
```
