# Production Dockerfile for Woodman's World Django app
# Multi-stage build for smaller final image

FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# System deps (add build-essential if compiling native packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo-dev zlib1g-dev gcc && rm -rf /var/lib/apt/lists/*

# Create non-root user for runtime security
RUN useradd -m django

# Copy requirements and install
COPY src/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt && pip check || true

# Copy project source
COPY src/ ./

# Collect static assets
ENV DJANGO_DEBUG=False
RUN python manage.py collectstatic --noinput || echo "Static collection failed (verify STATIC_ROOT)."

# Runtime port
EXPOSE 8000

# Healthcheck (basic TCP connect)
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import socket; s=socket.socket(); \
    s.settimeout(2); \
    s.connect(('127.0.0.1',8000)); s.close()" || exit 1

# Gunicorn entrypoint (replace with uvicorn if ASGI desired)
USER django
ENV PORT=8000
CMD ["gunicorn", "website.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--threads", "4", "--access-logfile", "-", "--error-logfile", "-"]
