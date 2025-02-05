##############
# Base Image #
##############
FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim AS base

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

#####################
# Development Image #
#####################
FROM base AS development

COPY --from=base /app/.venv /app/.venv

COPY . /app

RUN uv sync --frozen

ENV GRADIO_SERVER_NAME="0.0.0.0"

CMD ["uv", "run", "python", "-m", "src.app"]