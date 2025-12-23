# ---- builder ----
FROM python:3.12-slim AS builder

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# deps básicas (ajuste se você tiver libs nativas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
  && rm -rf /var/lib/apt/lists/*

# instala uv
RUN pip install --no-cache-dir uv

# copia apenas arquivos de lock primeiro (cache melhor)
COPY pyproject.toml uv.lock ./

# cria o venv e instala deps (sem dev)
RUN uv sync --frozen --no-dev

# agora copia o código
COPY . .

# garante que o projeto (editable) está sincronizado
RUN uv sync --frozen --no-dev


# ---- runtime ----
FROM python:3.12-slim AS runtime

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# copia app + venv prontinhos
COPY --from=builder /app /app

# (opcional) rodar como usuário não-root
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Não define CMD aqui; o docker-compose define por serviço
