#!/bin/sh

set -e

stethoscope migrate # Apply the database schema
stethoscope collectstatic --no-input # Collect static files for serving
uvicorn --host 0.0.0.0 --port 8000 stethoscope.main.asgi:application
