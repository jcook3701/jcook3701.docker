# Open WebUI

Deploy Open WebUI through the collection's shared container engine.
Docker Engine, Compose v2, `community.docker`, and `jcook3701.utils` are required.

The default web endpoint is `http://127.0.0.1:3000`. Configure a reachable Ollama URL.
Enable web search and supply a reachable SearXNG query URL together to use SearXNG.
For a migration, stop the bundled WebUI first, point `open_webui_data_dir` to its old data,
and supply its existing WebUI secret from Vault.

## Lifecycle

- `present` configures and starts the stack.
- `absent` removes the Compose stack, preserving its data and configuration.
- `teardown` also removes the Compose file. Image and data removal require explicit flags.

The data removal flag removes the entire role deployment directory. Keep this directory
dedicated to this role. Data stored outside it is retained.

## Role Variables

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `open_webui_container_engine` | str | Container engine. Choices: `docker`. | `docker` |
| `open_webui_state` | str | Deployment lifecycle. Choices: `present`, `absent`, `teardown`. | `present` |
| `open_webui_teardown_remove_data` | bool | Permanently remove role files and data within the deployment directory. | `false` |
| `open_webui_teardown_remove_images` | bool | Remove the Compose service images during teardown. | `false` |
| `open_webui_image` | str | Container image reference. | `ghcr.io/open-webui/open-webui:main` |
| `open_webui_container_name` | str | Container name. | `open-webui` |
| `open_webui_pull_policy` | str | Compose pull policy. Choices: `missing`, `always`, `never`. | `missing` |
| `open_webui_pull_images` | bool | Ask the shared container engine to force image pulls. | `false` |
| `open_webui_restart_policy` | str | Container restart policy. Choices: `no`, `always`, `on-failure`, `unless-stopped`. | `unless-stopped` |
| `open_webui_base_dir` | path | Deployment directory for Compose files and managed state. | `/opt/open-webui` |
| `open_webui_bind_ip` | str | Published host address. | `127.0.0.1` |
| `open_webui_external_port` | int | Published host port. | `3000` |
| `open_webui_internal_port` | int | Service port inside the container. | `8080` |
| `open_webui_shared_network` | str | Optional existing Docker network for private service connections. | `""` |
| `open_webui_data_dir` | path | Persistent application data directory. | `/opt/open-webui/data` |
| `open_webui_name` | str | Display name for the web interface. | `Open WebUI` |
| `open_webui_url` | str | Public URL used by Open WebUI integrations. | `""` |
| `open_webui_ollama_url` | str | Ollama API endpoint reachable from the container. | `http://host.docker.internal:11434` |
| `open_webui_secret_key` | str | WebUI secret. Empty generates a persistent secret. | `""` |
| `open_webui_enable_signup` | bool | Allow new users to register. | `false` |
| `open_webui_enable_web_search` | bool | Enable web search through SearXNG. | `false` |
| `open_webui_searxng_query_url` | str | SearXNG query URL reachable from the container. Required for web search. | `""` |
| `open_webui_searxng_language` | str | SearXNG search language. | `all` |

## Example

```yaml
---
- name: Deploy Open WebUI
  hosts: "open_webui_hosts"
  become: true
  roles:
    - role: "jcook3701.docker.open_webui"
```

## Author Information

Maintained by **Jared W. Cook**. Licensed under AGPL-3.0-or-later.
