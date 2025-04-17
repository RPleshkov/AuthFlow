FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app


COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

ENV PATH="/app/.venv/bin:$PATH"
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy


COPY . .


RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project


RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync


RUN chmod +x scripts/prestart.sh

ENTRYPOINT ["bash", "scripts/prestart.sh"]
CMD ["fastapi", "run", "app/main.py"]