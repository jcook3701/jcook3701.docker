# n8n

Deploy n8n through the collection's shared container engine.
Docker Engine, Compose v2, `community.docker`, and `jcook3701.utils` are required.

The default editor is `http://127.0.0.1:5678`. For remote HTTPS, configure the external URLs,
secure cookies, and correctly scoped reverse proxy settings. For a migration, stop the bundled
instance first and point `n8n_data_dir` to its original data directory. Retain any existing explicit
encryption key and the data directory's generated n8n configuration.

## Lifecycle

- `present` configures and starts the stack.
- `absent` removes the Compose stack, preserving its data and configuration.
- `teardown` also removes the Compose file. Image and data removal require explicit flags.

The data removal flag removes the entire role deployment directory. Keep this directory
dedicated to this role. Data stored outside it is retained.

## Role Variables

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `n8n_container_engine` | str | Container engine. Choices: `docker`. | `docker` |
| `n8n_state` | str | Deployment lifecycle. Choices: `present`, `absent`, `teardown`. | `present` |
| `n8n_teardown_remove_data` | bool | Permanently remove role files and data within the deployment directory. | `false` |
| `n8n_teardown_remove_images` | bool | Remove the Compose service images during teardown. | `false` |
| `n8n_image` | str | Container image reference. | `docker.n8n.io/n8nio/n8n:latest` |
| `n8n_container_name` | str | Container name. | `n8n` |
| `n8n_pull_policy` | str | Compose pull policy. Choices: `missing`, `always`, `never`. | `missing` |
| `n8n_pull_images` | bool | Ask the shared container engine to force image pulls. | `false` |
| `n8n_restart_policy` | str | Container restart policy. Choices: `no`, `always`, `on-failure`, `unless-stopped`. | `unless-stopped` |
| `n8n_base_dir` | path | Deployment directory for Compose files and managed state. | `/opt/n8n` |
| `n8n_bind_ip` | str | Published host address. | `127.0.0.1` |
| `n8n_external_port` | int | Published host port. | `5678` |
| `n8n_internal_port` | int | Service port inside the container. | `5678` |
| `n8n_data_dir` | path | Persistent workflow and credential directory. | `/opt/n8n/data` |
| `n8n_host` | str | Public hostname. Empty uses the managed host FQDN. | `""` |
| `n8n_protocol` | str | Public protocol. Choices: `http`, `https`. | `http` |
| `n8n_secure_cookie` | bool | Enable secure cookies when clients connect over HTTPS. | `false` |
| `n8n_proxy_hops` | int | Number of trusted reverse proxy hops. | `0` |
| `n8n_timezone` | str | Workflow and container timezone. | `UTC` |
| `n8n_encryption_key` | str | Explicit credential key. Empty uses n8n's stored key. | `""` |
| `n8n_editor_base_url` | str | Public editor URL. | `""` |
| `n8n_webhook_url` | str | Public webhook URL. | `""` |
| `n8n_mcp_base_url` | str | Public URL for n8n's MCP integration. | `""` |

## Example

```yaml
---
- name: Deploy n8n
  hosts: "n8n_hosts"
  become: true
  roles:
    - role: "jcook3701.docker.n8n"
```

## Author Information

Maintained by **Jared W. Cook**. Licensed under AGPL-3.0-or-later.
