FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Install just
RUN curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin

# Copy project files
COPY . .

# Create virtual environment and install dependencies
# We use -e . to install the project in editable mode, which is common for dev,
# but for a built image, standard install is fine.
RUN uv venv && . .venv/bin/activate && uv pip install .

# Ensure the virtual environment is on the PATH for the runtime
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Default command runs the TUI
# Note: To run interactively, use: docker run -it <image_name>
CMD ["python", "-m", "jl.tui"]
