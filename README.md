# Stethoscope

A lightweight heartbeat monitor for tracking deployed application counts.

## Quickstart

Stethoscope requires access to a PostgreSQL database.
Start by creating credentials for the service account.
These values are stored as environmental variables and are referenced automatically by the application.

```shell
export DB_NAME=stethoscope
export DB_USER=stethoscope_svc
export DB_PASSWORD=$(openssl rand -base64 32)
```

Using the new credentials, deploy a database server using Docker.

```shell
docker run -d \
  --name stethoscope-db \
  -e POSTGRES_DB=$DB_NAME \
  -e POSTGRES_USER=$DB_USER \
  -e POSTGRES_PASSWORD=$DB_PASSWORD \
  -p 5432:5432 \
  postgres
```

With the database running, execute the application's setup tasks.
This includes applying the database schema and initializing static content.

```shell
stethoscope migrate
stethoscope collectstatic
```

Finally, create a new admin user account and launch a development sever.

```shell
stethoscope createsuperuser
stethoscope runserver
```

## Application Settings

Application settings are configured by setting environmental variables inside the container.
The following table outlines the available settings and their defaults.

### Security Settings

Settings used to configure application security.

| Environment Variable     | Default                | Description                                                        |
|--------------------------|------------------------|--------------------------------------------------------------------|
| `SECURE_SECRET_KEY`      | `<randomly generated>` | Secret key used for cryptographic signing.                         |
| `SECURE_ALLOWED_HOSTS`   | `localhost,127.0.0.1`  | CSV list of application server hostnames.                          |
| `SECURE_SSL_REDIRECT`    | `False`                | Redirect all non-HTTPS requests to HTTPS.                          |
| `SECURE_HSTS_PRELOAD`    | `False`                | Include the `preload` directive in the HSTS header.                |
| `SECURE_HSTS_SECONDS`    | `0`                    | Duration in seconds to set the HSTS `max-age`. `0` disables HSTS.  |
| `SECURE_HSTS_SUBDOMAINS` | `False`                | Include subdomains in the HSTS policy.                             |
| `SECURE_REQUIRE_AUTH`    | `TRUE`                 | Whether to require authentication when recording heartbeat events. |

### API Settings

Settings for regulating the incoming HTTP request load.

| Environment Variable | Default  | Description                                                |
|----------------------|----------|------------------------------------------------------------|
| `API_THROTTLE_ANON`  | `60/min` | Request rate limit applied to unauthenticated API clients. |
| `API_THROTTLE_USER`  | `60/min` | Request rate limit applied to authenticated API users.     |

### Database Settings

Database connection settings.

| Environment Variable | Default       | Description                |
|----------------------|---------------|----------------------------|
| `DB_NAME`            | `stethoscope` | Postgres database name.    |
| `DB_HOST`            |               | Postgres server host.      |
| `DB_USER`            |               | Postgres server username.  |
| `DB_PASSWORD`        |               | Postgres server password.  |
| `DB_PORT`            | `5432`        | Postgres server port.      |
