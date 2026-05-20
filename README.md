# samba-web

Docker image that exposes a Samba share as an HTTP server with directory listing. Samba is accessed on-demand — every request talks to the SMB server directly, no local cache or sync.

## Usage

```bash
cp .env.example .env
# fill in .env
docker compose up --build
```

Server runs at [http://localhost:8080](http://localhost:8080).

## Environment variables

| Variable | Description | Default |
|---|---|---|
| `SMB_HOST` | Samba server IP or hostname | **required** |
| `SMB_SHARE` | Share name | **required** |
| `SMB_USER` | Username (`guest` = no password) | `guest` |
| `SMB_PASSWORD` | Password | empty |
| `SMB_DOMAIN` | Domain / workgroup | empty |
| `SMB_PATH` | Subdirectory within the share | `/` (root) |
| `PORT` | HTTP port inside the container | `80` |

## Deploying with Coolify

Deploy as a **Dockerfile**. Set environment variables in the Coolify UI. Container port: `80`.

## Behaviour

- **Directory** → HTML directory listing fetched from Samba on each request
- **File** → streamed directly from Samba to the HTTP response in 64 KB chunks
- HTTP 404 for missing paths, HTTP 503 when the SMB server is unreachable
