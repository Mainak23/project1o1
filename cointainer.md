Your computer                  Container

src/                            /app/src/
├── new.py                      ├── new.py
├── model.py       ──────────►  ├── model.py
└── data.py                     └── data.py

COPY <source> <destination>
     │        │
     │        └── ./src/
     │
     └── src/

During image creation, execute this command and save the result into the image.
RUN = while building the image

When somebody creates a container from me, this is the default command to execute.
CMD = when starting the container

                 Dockerfile
                     │
                     ▼
              podman build
                     │
            ┌────────┴────────┐
            │                 │
           RUN               CMD
            │                 │
       BUILD TIME          RUNTIME
            │                 │
      install packages    run Python
            │                 │
            ▼                 ▼
         IMAGE             CONTAINER

One more important thing: podman run can override CMD

ENV PATH="/opt/venv/bin:$PATH"
Make /opt/venv/bin the first place Linux looks when I run commands like python or pip."

PATH is an environment variable containing directories where Linux looks for executable programs.

For example, inside your container:

PATH=
/usr/local/bin
:/usr/bin
:/bin

python:3.13-slim
       │
       ▼
     /app
       │
       ▼
copy requirements.txt
       │
       ▼
create /opt/venv
       │
       ▼
PATH → /opt/venv/bin
       │
       ▼
install ML dependencies
       │
       ▼
copy src/
       │
       ▼
create appuser
       │
       ▼
appuser owns /app
       │
       ▼
USER appuser
       │
       ▼
python src/new.py

1️⃣ Remove unnecessary dependencies
        ↓
2️⃣ Don't package datasets/models/artifacts
        ↓
3️⃣ Use python:3.13-slim
        ↓
4️⃣ Use --no-cache-dir
        ↓
5️⃣ Use .dockerignore
        ↓
6️⃣ Choose CPU/GPU dependencies correctly
        ↓
7️⃣ Multi-stage build if compilation is required
        ↓
8️⃣ Optimize individual heavy libraries

sequirity 
✅ python:3.13-slim
✅ non-root appuser
✅ no secrets in Dockerfile
✅ no --privileged
✅ .dockerignore
✅ pinned dependencies
✅ image scanning
✅ image version = Jenkins BUILD_NUMBER
✅ internal ml-network
✅ resource limits
✅ separate MLflow/MinIO services


RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app

"Create a normal user called appuser, then give that user ownership of /app."

Builder
│
├── gcc
├── g++
├── Python
├── venv
│   ├── MLflow
│   ├── sklearn
│   ├── pandas
│   └── boto3
│
└── temporary build stuff
         │
         │ copy only
         ▼
Runtime
│
├── Python
├── venv
│   ├── MLflow
│   ├── sklearn
│   ├── pandas
│   └── boto3
│
└── your code

COPY --from=builder /opt/venv /opt/venv
"From the builder stage, copy /opt/venv into /opt/venv in the current stage."


BUILDER
python:3.13
│
├── gcc
├── g++
├── build tools
└── /opt/venv
        │
        │ COPY
        ▼
RUNTIME
python:3.13-slim
│
├── /opt/venv
└── src/
This is often the point of multi-stage builds: the builder can be heavier, while the runtime is smaller.

Multi-stage Docker — interview answer

I use multi-stage Docker builds when the application needs build-time dependencies that are not required at runtime.
"Multi-stage reduces the image by removing build-time dependencies; it cannot remove runtime dependencies like PyTorch that the application actually needs."

For PyTorch:

Builder
├── gcc              ← can remove
├── g++              ← can remove
├── build tools      ← can remove
└── PyTorch          ← MUST KEEP

Runtime:

├── PyTorch          ← still needed
├── Transformers     ← still needed
└── application      ← still needed

For example:

Builder:
gcc, g++, make → build Python packages
                    ↓
Runtime:
Python + packages + application

This gives:

Smaller production image
Fewer unnecessary tools/vulnerabilities
Cleaner runtime environment

Trivy identifies the software packages and versions inside the image, matches them against its vulnerability database, assigns/report severities such as LOW, MEDIUM, HIGH and CRITICAL, and Jenkins can use those results as a security quality gate

podman pull docker.io/aquasec/trivy:0.72.0
podman images | grep trivy

                  HOST
┌─────────────────────────────────────┐
│                                     │
│  Podman                             │
│    │                                │
│    │ manages                        │
│    ▼                                │
│  ml-training:91                     │
│                                     │
│    ▲                                │
│    │                                │
│    │ communication                  │
│    │                                │
│  podman.sock 🔌                     │
│    │                                │
│    │ mounted into                   │
│    ▼                                │
│  ┌──────────────────────┐           │
│  │   Trivy container    │           │
│  │                      │           │
│  │   Trivy              │           │
│  │      │               │           │
│  │      └── asks Podman │           │
│  │          to inspect  │           │
│  │          image       │           │
│  └──────────────────────┘           │
│                                     │
└─────────────────────────────────────┘

Container isolation means:

Trivy container cannot automatically see the host's Podman.

Podman socket means:

A communication channel that lets Trivy talk to the host's Podman.

Mounting the socket means:

Give Trivy access to that communication channel.

Start Podman's communication doorway for my user.
systemctl --user enable --now podman.socket

The temporary runtime directory belonging to the current user.
$XDG_RUNTIME_DIR


Does the Podman communication doorway actually exist?"
ls -l $XDG_RUNTIME_DIR/podman/podman.sock

podman run --rm \
  -v "$XDG_RUNTIME_DIR/podman/podman.sock:/podman/podman.sock" \
  docker.io/aquasec/trivy:0.72.0 \
  ls -l /podman/podman.sock