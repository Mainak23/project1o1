FROM python:3.13-slim

WORKDIR /ap

COPY requirements.txt .


RUN python -m venv /op/venv

ENV PATH="/op/venv/bin:$PATH"

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY serv/ ./serv/

RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /ap

USER appuser

CMD ["python", "serv/main.py"]