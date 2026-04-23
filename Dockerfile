# --- Build image ---
FROM python:3.14-alpine AS builder

# Compile application wheels
WORKDIR /src
COPY . .
RUN pip wheel --no-cache-dir --wheel-dir /wheels ./[all]


# --- Runtime image ---
FROM python:3.14-alpine

EXPOSE 8000

# Disable Python byte code caching and output buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Configure application settings with container friendly defaults
ENV CONFIG_STATIC_DIR=/app/stethoscope/static

# Install tools for health checks
RUN apk add --no-cache curl

# Install application wheels
COPY --from=builder /wheels /wheels
RUN pip install --no-compile --no-cache-dir /wheels/* && rm -rf /wheels
ENV PATH="/usr/local/bin:$PATH"

# Switch to non-root user
RUN adduser -D stethoscope
USER stethoscope
WORKDIR /app/stethoscope

# Use the API health checks to report container health
HEALTHCHECK CMD curl --fail --location localhost:8000/ || exit 1

# Launch the application
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "stethoscope.main.asgi:application"]
