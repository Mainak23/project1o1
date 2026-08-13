FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

CMD ["python", "src/new.py"]
