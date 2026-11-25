# MCP Inspector

Deploy MCP Inspector through the collection's shared container engine.
Docker Engine, Compose v2, `community.docker`, and `jcook3701.utils` are required.

The default Inspector UI is `http://127.0.0.1:6274`. The Apps sandbox and app origin also
use their published loopback ports. Keep the UI private and use its built-in authentication.
The role seeds the optional server catalog once. Enter the gateway's bearer token in Inspector.
For a migration, use the original data directory and configure the same encryption key.

## Lifecycle

- `present` configures and starts the stack.
- `absent` removes the Compose stack, preserving its data and configuration.
- `teardown` also removes the Compose file. Image and data removal require explicit flags.

The data removal flag removes the entire role deployment directory. Keep this directory
dedicated to this role. Data stored outside it is retained.

## Role Variables

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `mcp_inspector_container_engine` | str | Container engine. Choices: `docker`. | `docker` |
| `mcp_inspector_state` | str | Deployment lifecycle. Choices: `present`, `absent`, `teardown`. | `present` |
| `mcp_inspector_teardown_remove_data` | bool | Permanently remove role files and data within the deployment directory. | `false` |
| `mcp_inspector_teardown_remove_images` | bool | Remove the Compose service images during teardown. | `false` |
| `mcp_inspector_image` | str | Container image reference. | `ghcr.io/modelcontextprotocol/inspector:latest` |
| `mcp_inspector_container_name` | str | Container name. | `mcp-inspector` |
| `mcp_inspector_pull_policy` | str | Compose pull policy. Choices: `missing`, `always`, `never`. | `missing` |
| `mcp_inspector_pull_images` | bool | Ask the shared container engine to force image pulls. | `false` |
| `mcp_inspector_restart_policy` | str | Container restart policy. Choices: `no`, `always`, `on-failure`, `unless-stopped`. | `unless-stopped` |
| `mcp_inspector_base_dir` | path | Deployment directory for Compose files and managed state. | `/opt/mcp-inspector` |
| `mcp_inspector_bind_ip` | str | Published host address. | `127.0.0.1` |
| `mcp_inspector_external_port` | int | Published host port. | `6274` |
| `mcp_inspector_internal_port` | int | Service port inside the container. | `6274` |
| `mcp_inspector_shared_network` | str | Optional existing Docker network for private service connections. | `""` |
| `mcp_inspector_data_dir` | path | Persistent server catalog and session data directory. | `/opt/mcp-inspector/data` |
| `mcp_inspector_sandbox_port` | int | Client and container port for the Apps sandbox. | `6275` |
| `mcp_inspector_app_origin_port` | int | Client and container port for the Apps origin. | `6278` |
| `mcp_inspector_allowed_origins` | list | Explicit allowed browser origins. | `[]` |
| `mcp_inspector_secret_key` | str | Initial encryption key. Empty generates a persistent key. | `""` |
| `mcp_inspector_gateway_url` | str | Optional initial gateway catalog entry. Clients supply its bearer token. | `""` |

## Example

```yaml
---
- name: Deploy MCP Inspector
  hosts: "mcp_inspector_hosts"
  become: true
  roles:
    - role: "jcook3701.docker.mcp_inspector"
```

## Author Information

Maintained by **Jared W. Cook**. Licensed under AGPL-3.0-or-later.
