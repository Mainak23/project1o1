# -------------------------
# Stage 1: Builder
# -------------------------
FROM python:3.13-slim AS builder

WORKDIR /build

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc \
       g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# -------------------------
# Stage 2: Runtime
# -------------------------
FROM python:3.13-slim

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY src/ ./src/

RUN useradd \
        --create-home \
        --shell /bin/bash \
        appuser \
    && chown -R appuser:appuser /app

USER appuser

CMD ["python", "src/new.py"]