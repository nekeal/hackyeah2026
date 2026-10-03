# syntax = docker/dockerfile:1.2
FROM python:3.14-slim as backend-base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH=/opt/venv/bin:$PATH
WORKDIR /app

# Install uv package manager
RUN pip install --upgrade pip uv

FROM backend-base as backend-dev
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/ uv sync --group dev
ADD . ./

FROM backend-base as production
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --no-dev --group prod
ADD . ./
RUN uv run python manage.py collectstatic --noinput
