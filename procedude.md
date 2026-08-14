
advantage:
Rootless containers reduce the privilege available to a compromised container compared with running the container runtime as root.


ssh mainak@http://localhost:8080/
#jankins -MLflow configureation
ssh <username>@<jenkins-server-ip>


You might have been somewhere Jenkins could access:

/tmp
sudo -u jenkins -s
mainak
   │
   └── /home/mainak
          │
          └── sudo → jenkins
                     ↓
              jenkins@mainak:/home/mainak$




sudo
 └── -i            → login shell
 └── -u jenkins    → as Jenkins

It says:

"Become Jenkins as if Jenkins had logged in normally."

sudo -iu jenkins
mainak
   │
   └── sudo -iu jenkins
             ↓
       Jenkins user
             ↓
       Jenkins home
             ↓
            $





cheack:
whoami
cd /tmp

remove stale runtime state:(temporary runtime state is stale because the machine rebooted.)
rm -rf /tmp/storage-run-111/containers
rm -rf /tmp/storage-run-111/libpod/tmp


ERRO[0002] Refreshing container bd48876902648144a3e92dc7d2375cbf0f32627978d164bab106d480d1bce039: acquiring lock 3 for container bd48876902648144a3e92dc7d2375cbf0f32627978d164bab106d480d1bce039: file exists 
ERRO[0002] Refreshing container 6e2ebca9e7c0a8fd6b86ec5c767b6db5a480cab23410066d13ebfa9b30b896c0: acquiring lock 1 for container 6e2ebca9e7c0a8fd6b86ec5c767b6db5a480cab23410066d13ebfa9b30b896c0: file exists 
ERRO[0002] Refreshing volume mlflow-data: acquiring lock 0 for volume mlflow-data: file exists 
ERRO[0002] Refreshing volume minio-data: acquiring lock 2 for volume minio-data: file exists 
ERRO[0002] Refreshing volume trivy-cache: acquiring lock 5 for volume trivy-cache: file exists 

ss -ltnp | grep :5000

rootless services/tools running as a specific Linux user, like your Jenkins + rootless Podman setup.
"Where should programs put temporary files that belong to my currently running user session?"

id -u jenkins
export XDG_RUNTIME_DIR=/run/user/111 

#the temporary runtime/IPC area belonging to Jenkins.("Set this variable, and pass it to programs I launch from this shell.")

export
  ↓
make available to child processes

XDG_RUNTIME_DIR
  ↓
variable name

/run/user/111
  ↓
value


Podman configuration:

1.user-created Podman network gives you a clean, explicit network boundary and container DNS/service-name resolution.

podman network create ml-network
podman network ls
podman ps -a

controls container-to-container communication.
controls host-to-container access.

2.For now, create one persistent Podman volume:
podman volume create mlflow-data
podman volume inspect mlflow-data

{
          "Name": "mlflow-data",
          "Driver": "local",
          "Mountpoint": "/var/lib/jenkins/.local/share/containers/storage/volumes/mlflow-data/_data",
          "CreatedAt": "2026-08-12T10:00:52.499906116+05:30",
          "Labels": {},
          "Scope": "local",
          "Options": {},
          "MountCount": 0,
          "NeedsCopyUp": true,
          "NeedsChown": true,
          "LockNumber": 0
     }


/
└── var/
    └── lib/
        └── jenkins/
            └── .local/
                └── share/
                    └── containers/
                        └── storage/
                            └── volumes/
                                └── mlflow-data/
                                    └── _data/

| Field               | Meaning                                                                | Production implication                                  |
| ------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------- |
| `Name: mlflow-data` | Your volume's logical name                                             | ✅ Good                                                  |
| `Driver: local`     | Data is stored on the **same machine**                                 | ⚠️ Not highly available                                 |
| `Mountpoint`        | Actual physical location of the volume                                 | ⚠️ Tied to this Jenkins server                          |
| `Scope: local`      | Volume belongs to this Podman host                                     | ⚠️ Cannot transparently move with the container         |
| `MountCount: 0`     | Currently no container is using it                                     | Normal                                                  |
| `NeedsCopyUp: true` | Podman may copy existing container data into the volume on first mount | Not a production architecture concern                   |
| `NeedsChown: true`  | Podman needs to adjust ownership/permissions for the container user    | Important for permissions, but not storage architecture |

need 
HOST
/var/lib/jenkins/.local/share/containers/storage/volumes/mlflow-data/_data"
                 │
                 │ Podman volume mapping
                 ▼
CONTAINER
/mlflow-data

HOST
┌─────────────────────┐
│ mlflow-data volume  │
│                     │
│ mlflow.db           │
│ artifacts/          │
└──────────┬──────────┘
           │
           │ mounted
           ▼
CONTAINER
┌─────────────────────┐
│ /mlflow-data        │
│                     │
│ mlflow.db           │
│ artifacts/          │
└─────────────────────┘

Container crash       → data survives ✅
Podman crash           → data survives ✅
Container deletion     → data survives ✅
Jenkins restart        → normally survives ✅
Host disk failure      → data lost ❌
Host machine failure  → data unavailable ❌


3.download image
podman pull ghcr.io/mlflow/mlflow:latest
podman images | grep mlflow



3.now create cointainer and run

podman run
    ↓
starts the container

mlflow server ...
    ↓
starts MLflow INSIDE that container

a."Start my MLflow container in the background, connect it to my network, expose port 5000, and attach my persistent volume

Create the mlflow container and immediately start whatever command the image defines as its custom command.
podman run -d \
    --name mlflow \
    --network ml-network \
    -p 5000:5000 \
    -v mlflow-data:/mlflow-data \
    mlflow:latest
    sleep infinity

podman exec -d mlflow \
    mlflow server \
    --host 0.0.0.0 \
    --port 5000 \
    --backend-store-uri sqlite:////mlflow-data/mlflow.db \
    --default-artifact-root /mlflow-data/artifacts \
    --allowed-hosts "mlflow:5000,localhost:5000,127.0.0.1:5000"



b."Where should you store your database and artifacts

Create the mlflow container and immediately start whatever command the image defines as its custom command.




podman run -d \
    --name mlflow \
    --network ml-network \
    -p 5000:5000 \
    -v mlflow-data:/mlflow-data \
    ghcr.io/mlflow/mlflow:latest \
    mlflow server \
    --host 0.0.0.0 \
    --port 5000 \
    --backend-store-uri sqlite:////mlflow-data/mlflow.db \
    --default-artifact-root /mlflow-data/artifacts \
    --allowed-hosts "mlflow:5000,localhost:5000,127.0.0.1:5000"


cheack helth:curl http://127.0.0.1:5000/health
Verify your persistent volume:podman exec mlflow ls -lah /mlflow-data
which user MLflow is actually running as,:podman exec mlflow id

uid=0(root) gid=0(root) groups=0(root)

uid=0(root)
   ↑
   user ID 0 = root

gid=0(root)
   ↑
   group ID 0 = root


MLflow container
│
├── User: root
│
└── /mlflow-data
      │
      ├── owner: root
      ├── group: root
      └── mlflow.db

This means inside your MLflow container, the mounted directory is currently owned by root.
d rwx r-x r-x 2 root root
│ │   │   │   │ │    │
│ │   │   │   │ │    └── group
│ │   │   │   │ └─────── owner
│ │   │   │   └───────── hard links
│ │   │   └───────────── others
│ │   └───────────────── group permissions
│ └───────────────────── owner permissions
└─────────────────────── type

note*
If MLflow is compromised, a root process potentially has much greater privileges inside the container.

A better production design is:
Host
│
├── Podman
│
└── MLflow container
       │
       └── mlflow user
             │
             └── /mlflow-data

Rootless Podman uses user namespaces to map container users to host users.

This is one of the major security advantages of your Jenkins + rootless Podman setup.

You can see your Podman mode with:

podman info --format '{{.Host.Security.Rootless}}'

If it returns:

true


podman run -d
      │
      ├── --name mlflow
      ├── --network ml-network
      ├── -p 5000:5000
      ├── -v mlflow-data:/mlflow-data
      │
      ▼
ghcr.io/mlflow/mlflow:latest
      │
      ▼
mlflow server
      │
      ├── database → /mlflow-data/mlflow.db
      └── artifacts → /mlflow-data/artifacts


mlflow-data volume
│
├── mlflow.db
│     └── experiments
│     └── runs
│     └── metrics
│     └── parameters
│
└── artifacts/
      ├── models
      ├── plots
      ├── files
      └── other artifacts


And your tracking flow becomes:
Jenkins
   │
   │ podman run
   ▼
Training container
   │
   │ MLFLOW_TRACKING_URI
   │ http://mlflow:5000
   ▼
MLflow container
   │
   ├── mlflow.db
   │
   └── artifacts/
   │
   ▼
mlflow-data volume

check:
podman exec mlflow \
    python -c "
import sqlite3
conn = sqlite3.connect('/mlflow-data/mlflow.db')

print('Experiments:')
for row in conn.execute('SELECT experiment_id, name FROM experiments'):
    print(row)

print('\nRuns:')
for row in conn.execute('SELECT run_uuid, experiment_id, status FROM runs ORDER BY start_time DESC'):
    print(row)
"

Check the metrics
podman exec mlflow \
    python -c "
import sqlite3
conn = sqlite3.connect('/mlflow-data/mlflow.db')

for row in conn.execute('''
    SELECT run_uuid, key, value
    FROM metrics
    ORDER BY run_uuid
'''):
    print(row)
"

goal :I want every MLflow run to tell me exactly which Git commit produced this model.

git comit with mlflow:
Git commit
   ↓
a8f32c1
   ↓
MLflow run
   ↓
model

                 Jenkins
                    │
             Git checkout
                    │
              GIT_COMMIT
                    │
                    ▼
          Training container
                    │
                    ▼
                 MLflow

GIT_PYTHON_REFRESH tells GitPython what to do when Git cannot be initialized.

Jenkins
│
├── GIT_COMMIT
│      └── actual code version
│
├── MLFLOW_TRACKING_URI
│      └── where MLflow lives
│
└── GIT_PYTHON_REFRESH
       └── how GitPython behaves
              when Git isn't available

So you don't "get" GIT_PYTHON_REFRESH from Jenkins or GitHub. You define it because you're telling the training environment how to behave.And in your case, quiet is reasonable because Jenkins is already supplying the authoritative commit SHA.

                    JENKINS
                       │
              checkout Git commit
                       │
                       │ GIT_COMMIT
                       ▼
              ┌─────────────────┐
              │ Training        │
              │ Container       │
              │                 │
              │ Python          │
              │   │             │
              │   ├── MLflow ───────────┐
              │   │  tracking URI       │
              │   │                     │
              │   └── GitPython         │
              │       │                 │
              │       └── warning       │
              │          suppression    │
              └─────────────────┘       │
                                        │
                                        ▼
                              ┌─────────────────┐
                              │ MLflow Container│
                              │                 │
                              │ mlflow:5000     │
                              │      │          │
                              │   mlflow.db     │
                              │   artifacts     │
                              └─────────────────┘

Bottom line: MLFLOW_TRACKING_URI is communication with MLflow; GIT_COMMIT is build provenance; GIT_PYTHON_REFRESH is merely a local GitPython warning-control setting.

MinIO
✅ MinIO container
✅ MinIO persistent volume
✅ MinIO bucket
✅ MLflow configured to use MinIO

artifact location 
podman exec mlflow python -c "
import mlflow

client = mlflow.MlflowClient()

for e in client.search_experiments():
    print(
        'EXPERIMENT:',
        e.name,
        '| ARTIFACT LOCATION:',
        e.artifact_location
    )
"

podman pull quay.io/minio/minio:latest
podman volume create minio-data
podman volume inspect minio-data

podman run -d \
    --name minio \
    --network ml-network \
    -p 9000:9000 \
    -p 9001:9001 \
    -v minio-data:/data \
    -e MINIO_ROOT_USER=minioadmin \
    -e MINIO_ROOT_PASSWORD=minioadmin123 \
    quay.io/minio/minio:latest \
    server /data \
    --console-address ":9001"

if we need to migrate it 

podman rm -f mlflow
podman run -d \
    --name mlflow \
    --network ml-network \
    -p 5000:5000 \
    -v mlflow-data:/mlflow-data \   

    -v HOST_VOLUME : CONTAINER_PATH 
    
     "Take the Podman volume called mlflow-data and make it available inside the container at /mlflow-data."


    -e AWS_ACCESS_KEY_ID=minioadmin \
    -e AWS_SECRET_ACCESS_KEY=minioadmin123 \
    -e MLFLOW_S3_ENDPOINT_URL=http://minio:9000 \
    ghcr.io/mlflow/mlflow:latest \
    mlflow server \
    --host 0.0.0.0 \
    --port 5000 \
    --backend-store-uri sqlite:////mlflow-data/mlflow.db \
    --default-artifact-root s3://mlflow-artifacts \
    --allowed-hosts "mlflow:5000,localhost:5000,127.0.0.1:5000"

                 ml-network
                     │
        ┌────────────┴────────────┐
        │                         │
      MLflow                    MinIO
        │                         │
        │ HTTP/S3 API             │
        │                         │
        └──────► :9000 ◄──────────┘
                                  │
                                  ▼
                            minio-data
                                  │
                                  ▼
                            actual storage

MLflow
  ❌ does NOT directly access minio-data

MLflow
  ✅ accesses http://minio:9000

MinIO
  ✅ accesses minio-data

one note we need boto3

Rule to remember:

Put a dependency in the image of the component that actually executes/imports it.

Here the error is:

MLflow → import boto3 → ❌

Therefore:

MLflow image → boto3 ✅

not:

Training image → boto3 ❌ unnecessary
Your MLflow server understands:

s3://mlflow-artifacts

and tries to use the S3 API, but the MLflow container doesn't have the Python library boto3 installed.

That's why you get:

ModuleNotFoundError: No module named 'boto3'
Why do you need boto3?

Think of it like this:

MLflow
   │
   │ "I need to store this artifact"
   ▼
boto3
   │
   │ speaks S3 protocol
   ▼
MinIO
   │
   ▼
mlflow-artifacts bucket

boto3 is the Python client that MLflow uses to communicate with S3-compatible storage.

And importantly:

boto3 does NOT mean you need AWS.

MinIO implements the S3 API, so boto3 can talk to MinIO.

boto3
  │
  ├── AWS S3
  │
  └── MinIO ✅

and MLflow UI should show:

Run
└── Artifacts
    └── model

So zero Python changes. The problem is entirely on the MLflow server → MinIO side.

podman exec -it mlflow bash
python -c "import boto3; print(boto3.__version__)"
podman restart mlflow
podman exec mlflow python -c "import boto3; print(boto3.__version__)"

start it necxt day 
podman start mlflow
podman start minio

we have
volume mounts ✅
network ✅
port mappings ✅
environment variables ✅
container name ✅
command/entrypoint ✅

-v mlflow-data:/mlflow-data

git comit unknow 

