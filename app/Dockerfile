FROM python:3.12-slim

RUN python --version && pip --version

WORKDIR /code
COPY pyproject.toml .
COPY uv.lock .

RUN pip install uv

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/code/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY ./app/ /code/app/

RUN --mount=type=cache,target=/code/.cache/uv \
    uv sync --frozen --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/code/.venv/bin:$PATH"
ENV PYTHONPATH="/code/app/:$PYTHONPATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Default command: run the FastAPI app with direct access to uvicorn
# Using --reload with specific monitoring patterns to improve reloading
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-include", "*.yml"]