FROM python:3.11-slim

WORKDIR /app

# System deps (OR-Tools wheels usually okay, but keep build-essential minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
COPY pyproject.toml /app/pyproject.toml
COPY src /app/src

RUN pip install -U pip \
 && pip install -r /app/requirements.txt \
 && pip install -e /app

EXPOSE 8000
CMD ["uvicorn", "evsolver.api:app", "--host", "0.0.0.0", "--port", "8000"]