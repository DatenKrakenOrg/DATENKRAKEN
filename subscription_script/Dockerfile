# Multistage Template taken and edited from: https://docs.astral.sh/uv/guides/integration/docker/#non-editable-installs
FROM python:3.13-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Change the working directory to the `app` directory
WORKDIR /app

# Copy the project into the intermediate image
COPY . /app

# Sync the project
RUN uv sync --locked --no-editable

FROM python:3.13-slim

# Copy the environment, but not the source code
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Run the application
CMD ["/app/.venv/bin/subscription-script"]
