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