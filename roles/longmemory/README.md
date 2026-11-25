# LongMemory

Deploy [LongMemory](https://github.com/CaviraOSS/LongMemory) using the collection's
`jcook3701.utils.container_engine` lifecycle, modeled on `freellmapi` in `feat-001`.
The role is independent of FreeLLMAPI and Ollama. It provides an authenticated
memory REST/MCP endpoint and optional dashboard. Clients must explicitly retrieve
and store memories; deploying this role does not inject memory into every request.

## Requirements

Docker Engine, Compose v2, `community.docker`, `jcook3701.utils.container_engine`,
Git for the dashboard, and an accessible Ollama instance with `nomic-embed-text`.
Run `docker exec ollama ollama pull nomic-embed-text` before deployment.

## Security and lifecycle

The API key is generated once or supplied from Vault as 64 hexadecimal characters.
It is persisted in `/opt/longmemory/.env` (root-only). Back up this file and the
external Docker volume `longmemory_data`. The named volume matches upstream and
allows Docker to initialize permissions from the image's non-root data directory.
Only one stack per host is supported. The dashboard holds the API key; keep both
ports on loopback or behind an authenticated TLS reverse proxy. Do not expose the
dashboard directly to untrusted users. Docker administrators can inspect secrets.
`present` deploys; `absent` stops without deleting memories; `teardown` removes the
Compose file, retaining data and key unless explicitly opted into deletion.
The image-removal flag operates through the shared engine and requires the Compose
file to still exist. Data removal deletes the external volume and deployment root.

## Role Variables

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `longmemory_container_engine` | str | Container orchestration engine. Choices: docker. | `docker` |
| `longmemory_state` | str | Desired deployment lifecycle. Choices: present, absent, teardown. | `present` |
| `longmemory_debug_mode` | bool | Display non-sensitive diagnostics. | `false` |
| `longmemory_teardown_remove_data` | bool | Permanently remove memory data and secrets. | `false` |
| `longmemory_teardown_remove_images` | bool | Remove stack images during teardown. | `false` |
| `longmemory_image` | str | Official backend image; pin a tested release for production. | `ghcr.io/caviraoss/longmemory:latest` |
| `longmemory_container_name` | str | Backend container name. | `longmemory` |
| `longmemory_pull_policy` | str | Backend Compose pull policy. Choices: always, missing, never. | `missing` |
| `longmemory_pull_images` | bool | Request image pulls through the shared engine. | `false` |
| `longmemory_restart_policy` | str | Container restart policy. Choices: no, always, on-failure, unless-stopped. | `unless-stopped` |
| `longmemory_base_dir` | path | Absolute deployment root ending in longmemory. | `/opt/longmemory` |
| `longmemory_api_key` | str | Initial 64-character hexadecimal API key; empty generates one. | `` |
| `longmemory_bind_ip` | str | Published host address. | `127.0.0.1` |
| `longmemory_external_port` | int | Published API and MCP port. | `7331` |
| `longmemory_internal_port` | int | Backend listen port. | `7331` |
| `longmemory_enable_dashboard` | bool | Build and deploy upstream dashboard. | `true` |
| `longmemory_dashboard_external_port` | int | Published dashboard port. | `7332` |
| `longmemory_dashboard_image` | str | Local dashboard build image. | `longmemory-dashboard:local` |
| `longmemory_repo_url` | str | Dashboard source repository. | `https://github.com/CaviraOSS/LongMemory.git` |
| `longmemory_repo_version` | str | Dashboard source branch, tag or commit. | `main` |
| `longmemory_enable_mcp` | bool | Enable HTTP MCP. | `true` |
| `longmemory_allowed_origins` | str | Comma-separated allowed origins. | `http://127.0.0.1:7332` |
| `longmemory_rate_limit_enabled` | bool | Enable API rate limiting. | `true` |
| `longmemory_rate_limit_max_requests` | int | API request limit. | `100` |
| `longmemory_embedding_provider` | str | Embedding provider. | `ollama` |
| `longmemory_embedding_tier` | str | Embedding tier. | `deep` |
| `longmemory_embedding_dimension` | int | Embedding vector dimension. | `768` |
| `longmemory_ollama_url` | str | Existing Ollama endpoint. | `http://host.docker.internal:11434` |
| `longmemory_ollama_embedding_model` | str | Ollama embedding model. | `nomic-embed-text` |
| `longmemory_extra_environment` | dict | Additional backend environment variables; managed keys prohibited. | `{}` |
| `longmemory_memory_limit` | str | Backend memory limit. | `2g` |
| `longmemory_cpu_limit` | str | Backend CPU limit. | `2.0` |
| `longmemory_pids_limit` | int | Backend process limit. | `256` |
| `longmemory_stop_grace_period` | str | Graceful shutdown duration. | `30s` |

## Example playbook

```yaml
---
- name: Deploy LongMemory
  hosts: "longmemory_hosts"
  become: true
  roles:
    - role: "jcook3701.docker.longmemory"
      vars:
        longmemory_api_key: "{{ vault_longmemory_api_key }}"
```

## Verification

- API health: `curl --fail http://127.0.0.1:7331/health`
- Dashboard: `http://127.0.0.1:7332`
- MCP: `http://127.0.0.1:7331/mcp` with `Authorization: Bearer <key>`.
- Inspect: `sudo docker compose -f /opt/longmemory/compose.yml ps`.

Do not change embedding dimensions or models after ingesting memories without a
migration plan. FreeLLMAPI is not assumed to supply embeddings: Ollama is the
verified upstream embedding integration. The shared engine must support Compose
builds for the optional dashboard; disable the dashboard if it does not.

## Validation and versioning

Backend `latest` and dashboard `main` are upstream defaults, not a verified
matching pinned release. Set compatible immutable versions before production.
YAML parsing and template rendering were checked locally; repository ansible-lint,
shared engine execution and Docker runtime deployment were not run.

## Author Information

Jared W. Cook — AGPL-3.0-or-later.
