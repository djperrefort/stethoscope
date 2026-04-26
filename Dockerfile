# --- Build image ---
FROM python:3.14-alpine AS builder

# Compile application wheels
WORKDIR /src
COPY . .
RUN pip wheel --no-cache-dir --wheel-dir /wheels ./

# --- Runtime image ---
FROM python:3.14-alpine

EXPOSE 8000

# Disable Python byte code caching and output buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install tools for health checks
RUN apk add --no-cache curl

# Install the application wheels
COPY --from=builder /wheels /wheels
RUN pip install --no-compile --no-cache-dir /wheels/* && rm -rf /wheels
ENV PATH="/usr/local/bin:$PATH"

# Switch to a non-root user
RUN adduser -D stethoscope
USER stethoscope
WORKDIR /app/stethoscope

# Use the application's HTTP status to report container health
HEALTHCHECK CMD curl --fail --location localhost:8000/ || exit 1

# Launch the application
COPY --chown=stethoscope:stethoscope --chmod=770 entrypoint.sh /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
