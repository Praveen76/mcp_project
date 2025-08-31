FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# system deps
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# copy project metadata (include README.md if referenced in pyproject)
COPY pyproject.toml uv.lock README.md ./

RUN pip install --no-cache-dir uv

# ⬅️ bring in code BEFORE installing
COPY src ./src

# install package (editable into system site-packages)
RUN uv pip install --system -e .

EXPOSE 8080
CMD ["uv", "run", "uvicorn", "mcp_project.app:app", "--host", "0.0.0.0", "--port", "8080"]
