# tender-scout runs as a one-shot command, not a server: it starts, writes a
# digest, and exits. The image carries only the code. config.yaml, seen.json and
# digest.md live on a volume mounted at /data so they survive between runs.

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# --- dependencies ---------------------------------------------------------
WORKDIR /app

# README.md is not optional here: pyproject.toml declares readme = "README.md",
# so the build backend fails without it.
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/

# --frozen: fail if uv.lock disagrees with pyproject, rather than quietly
#           resolving versions that were never tested.
# --no-dev: keep pytest and ruff out of the shipped image.
RUN uv sync --frozen --no-dev

# --- runtime --------------------------------------------------------------
# Every path in the app is relative (cli.py config.yaml and seen.json, run.py
# digest.md), so the working directory decides where they land. /data is the
# mount point for the Azure File share.
WORKDIR /data

# Absolute path: we are no longer in /app.
ENTRYPOINT ["/app/.venv/bin/tender-scout"]
