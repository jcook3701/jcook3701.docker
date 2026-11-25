# FreeLLMAPI

[FreeLLMAPI](https://github.com/tashfeenahmed/freellmapi) is a single-user
OpenAI-compatible gateway and dashboard for routing requests across local and
hosted model providers. The `jcook3701.docker.freellmapi` role deploys its
official container through the collection's established
`jcook3701.utils.container_engine` lifecycle integration.

FreeLLMAPI is intentionally a separate role from `ollama`. It owns a dashboard,
unified client keys, encrypted provider credentials, a SQLite database, and a
stable encryption key. Ollama is only one optional upstream provider, so either
service can be installed, upgraded, stopped, or torn down independently.

## Requirements

- Docker Engine and Docker Compose v2 on the target host.
- The `jcook3701.utils.container_engine` role and `community.docker` collection.
- Network access to GHCR for the pinned image on first deployment.
- Network access from FreeLLMAPI to the selected model providers.

The role does not install or reconfigure Docker.

## Security model

The default publication is `127.0.0.1:3001` because upstream describes
FreeLLMAPI as a single-user service. The dashboard stores provider credentials
encrypted at rest with AES-256-GCM, but the running gateway necessarily
decrypts those credentials in memory and sends requests to the configured
providers. Docker administrators can also inspect container configuration and
processes. Do not treat the gateway as a multi-tenant security boundary.

On first deployment, `freellmapi_encryption_key` may contain a Vault-managed
64-character hexadecimal key. When it is empty, the role securely generates a
key and stores it in the root-owned `/opt/freellmapi/.env` file with mode
`0600`. The key is never rotated automatically. If a supplied key later differs
from the persistent value, the role fails instead of making stored provider
credentials unreadable.

Back up both `/opt/freellmapi/data` and `/opt/freellmapi/.env`. Losing or
changing the encryption key prevents recovery of encrypted provider keys. A
separate encrypted database backup can be configured with either
`freellmapi_db_backup_path` or `freellmapi_db_backup_url`.

Remote publication exposes both the dashboard and API. If
`freellmapi_bind_ip` is changed from loopback, use only a trusted private
network or an authenticated TLS reverse proxy. While no account exists,
creating the first account remotely also requires the one-time setup code
printed in the container logs.

The role does not deploy upstream's optional Watchtower service. That service
requires the root-equivalent Docker socket; image upgrades remain explicit and
Ansible-managed through `freellmapi_image`.

## Data lifecycle

- `present`: create private persistent storage and an encryption key, render
  Compose configuration, and deploy the gateway.
- `absent`: stop and remove the container while preserving configuration,
  SQLite data, encryption key, and image.
- `teardown`: stop the stack and remove the Compose file while preserving the
  database and encryption key by default.
- `freellmapi_teardown_remove_images: true`: explicitly ask the shared engine
  role to remove the stack image during teardown.
- `freellmapi_teardown_remove_data: true`: permanently remove the entire
  `freellmapi_base_dir`, including the database, encryption key, unified keys,
  provider credentials, settings, analytics, and local backups.

Back up the persistent data and encryption key before enabling destructive
teardown.

## Role Variables

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `freellmapi_container_engine` | str | Container engine. Choice: `docker`. | `docker` |
| `freellmapi_state` | str | Lifecycle. Choices: `present`, `absent`, `teardown`. | `present` |
| `freellmapi_debug_mode` | bool | Display additional non-sensitive diagnostics. | `false` |
| `freellmapi_teardown_remove_data` | bool | Permanently delete the database, key, and state. | `false` |
| `freellmapi_teardown_remove_images` | bool | Remove the image during teardown. | `false` |
| `freellmapi_image` | str | Version-pinned official image. | `ghcr.io/tashfeenahmed/freellmapi:v0.16.42` |
| `freellmapi_container_name` | str | Gateway container name. | `freellmapi` |
| `freellmapi_pull_policy` | str | Compose pull policy. Choices: `always`, `missing`, `never`. | `missing` |
| `freellmapi_pull_images` | bool | Force image pulls through the shared engine role. | `false` |
| `freellmapi_restart_policy` | str | Restart policy; standard Compose choices. | `unless-stopped` |
| `freellmapi_base_dir` | path | Compose, secret, and persistent data root. | `/opt/freellmapi` |
| `freellmapi_container_uid` | int | Persistent data owner UID for the official image. | `1000` |
| `freellmapi_container_gid` | int | Persistent data owner GID for the official image. | `1000` |
| `freellmapi_encryption_key` | str | Initial Vault-managed 64-character hex key; empty generates one. | `` |
| `freellmapi_bind_ip` | str | Published host address; loopback is strongly recommended. | `127.0.0.1` |
| `freellmapi_external_port` | int | Published host port. | `3001` |
| `freellmapi_internal_port` | int | Application port inside the container. | `3001` |
| `freellmapi_shared_network` | str | Optional existing Docker network for private service connections. | `""` |
| `freellmapi_proxy_rate_limit_rpm` | int | Per-IP proxy requests per minute; zero disables. | `120` |
| `freellmapi_admin_rate_limit_rpm` | int | Per-IP dashboard requests per minute; zero disables. | `600` |
| `freellmapi_stream_keepalive_ms` | int | SSE heartbeat interval; zero disables, otherwise minimum `1000`. | `0` |
| `freellmapi_request_analytics_retention_days` | int | Analytics retention days; zero removes age limit. | `90` |
| `freellmapi_request_analytics_max_rows` | int | Analytics row limit; zero removes row limit. | `100000` |
| `freellmapi_db_backup_path` | str | Encrypted backup below `/app/server/data`; exclusive with URL. | `` |
| `freellmapi_db_backup_url` | str | HTTP(S) encrypted backup endpoint; exclusive with path. | `` |
| `freellmapi_db_backup_token` | str | Optional Vault-managed bearer token for the backup URL. | `` |
| `freellmapi_db_backup_key` | str | Optional separate Vault-managed 64-character backup key. | `` |
| `freellmapi_db_backup_interval_ms` | int | Milliseconds between encrypted backups. | `300000` |
| `freellmapi_extra_environment` | dict | Extra string environment values; managed keys are rejected. | `{}` |
| `freellmapi_memory_limit` | str | Container memory limit. | `2g` |
| `freellmapi_cpu_limit` | str | Container CPU limit. | `2.0` |
| `freellmapi_pids_limit` | int | Maximum container process count. | `256` |
| `freellmapi_stop_grace_period` | str | Graceful shutdown period. | `30s` |

When changing `freellmapi_image`, verify the image's runtime UID/GID and update
`freellmapi_container_uid` and `freellmapi_container_gid` together.

## Example playbook

```yaml
---
- name: Deploy FreeLLMAPI
  hosts: "freellmapi_hosts"
  become: true
  roles:
    - role: "jcook3701.docker.freellmapi"
      vars:
        freellmapi_state: "present"
        freellmapi_encryption_key: "{{ vault_freellmapi_encryption_key }}"
```

Generate a suitable Vault value with `openssl rand -hex 32`. It is an
infrastructure encryption key rather than a password you type regularly.

For an encrypted local database backup stored with the main data:

```yaml
freellmapi_db_backup_path: "/app/server/data/freellmapi.db.backup"
freellmapi_db_backup_key: "{{ vault_freellmapi_db_backup_key }}"
```

## Ollama integration

The Compose stack maps `host.docker.internal` to the Docker host gateway on
Linux. In the FreeLLMAPI dashboard, add a custom provider with:

- Label: `Ollama`
- Base URL: `http://host.docker.internal:11434/v1`
- Models: the Ollama models available on the host

Ollama must publish its OpenAI-compatible endpoint on an address reachable
from Docker containers. Keep Ollama and FreeLLMAPI in separate roles even when
they run on the same host.

## Client configuration and verification

After deployment, open `http://127.0.0.1:3001`, create the first dashboard
account, add provider credentials, and create a unified `freellmapi-...` client
key. OpenAI-compatible clients use `http://127.0.0.1:3001/v1` as the base URL.

Verify readiness locally:

```bash
curl --fail --silent http://127.0.0.1:3001/api/ping
sudo docker compose -f /opt/freellmapi/compose.yml ps
```

Upstream describes this project as personal experimentation and learning, not
production infrastructure. Each provider's own account, free-tier, licensing,
and acceptable-use terms still apply when FreeLLMAPI proxies requests.

## Helpful links

- [FreeLLMAPI repository](https://github.com/tashfeenahmed/freellmapi)
- [Docker deployment guide](https://github.com/tashfeenahmed/freellmapi/blob/main/docs/en/deployment/01-docker.md)
- [Installation and backup guide](https://github.com/tashfeenahmed/freellmapi/blob/main/docs/en/install/01-install.md)
- [Encryption keys](https://github.com/tashfeenahmed/freellmapi/blob/main/docs/en/env/02-security-and-keys.md)

## Author Information

Maintained by **Jared W. Cook** as part of the core infrastructure and container
management ecosystem. Licensed under AGPL-3.0-or-later.
