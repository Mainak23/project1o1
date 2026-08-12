
advantage:
Rootless containers reduce the privilege available to a compromised container compared with running the container runtime as root.

#jankins -MLflow configureation
ssh <username>@<jenkins-server-ip>
sudo -u jenkins -s
cheack:
whoami
cd /tmp

remove stale runtime state:(temporary runtime state is stale because the machine rebooted.)
rm -rf /tmp/storage-run-111/containers
rm -rf /tmp/storage-run-111/libpod/tmp

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


