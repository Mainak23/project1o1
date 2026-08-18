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