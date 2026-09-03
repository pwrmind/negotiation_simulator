FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
# ... копия файлов ...
RUN uv sync --frozen
