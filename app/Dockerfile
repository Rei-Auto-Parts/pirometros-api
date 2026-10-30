# Duas stages sobre a mesma base. O compose usa `target: dev` (ferramentas de qualidade, codigo
# montado por volume). A ultima stage, `prod`, e a que o Easypanel constroi por padrao.
FROM python:3.12-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

FROM base AS dev

RUN apt-get update \
    && apt-get install -y --no-install-recommends make git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --no-cache-dir -e ".[dev]" || true
COPY . .

CMD ["python3", "main.py"]

FROM base AS prod

COPY pyproject.toml ./
RUN pip install --no-cache-dir .

COPY main.py ./
COPY adapters ./adapters
COPY core ./core
COPY infra ./infra
COPY interfaces ./interfaces

ENV PYTHONPATH=/app
RUN useradd --system --no-create-home pirometros
USER pirometros

EXPOSE 8000
CMD ["python3", "main.py"]
