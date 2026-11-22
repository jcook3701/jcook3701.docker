# Ollama

[Ollama](https://ollama.com/) runs open-source models locally. This Ansible role
(`jcook3701.docker.ollama`) deploys a Docker Compose stack with optional
[Open WebUI](https://docs.openwebui.com/), [n8n](https://docs.n8n.io/),
[Docker MCP Gateway](https://github.com/docker/mcp-gateway), and
[SearXNG](https://docs.searxng.org/) with Valkey.

The role preserves the original `present`, `absent`, and `teardown` structure and
calls `jcook3701.utils.container_engine`. Docker Compose is the tested target
of this role; Podman support remains experimental, and Docker MCP Gateway
requires a Docker daemon and socket.

## Installation and upgrade

1. Copy the entire role directory to `roles/ollama` in `jcook3701.docker`.
2. Keep your existing persistent `/opt/ollama` data and Compose stack until you
   have backed them up. Updating the role does not automatically erase them.
3. Run your existing playbook with `ollama_state: present`.
4. Check `docker compose -f /opt/ollama/compose.yml ps` and verify the new service
   healthchecks before relying on the applications.

The role generates `/opt/ollama/.env` (mode `0600`) containing stable, random
secrets for Open WebUI, SearXNG, and Docker MCP Gateway. Existing nonempty values
in this file are preserved on subsequent runs. You may instead provide the
`ollama_webui_secret_key`, `ollama_searxng_secret_key`, and
`ollama_mcp_gateway_auth_token` options from Ansible Vault. **Changing an existing
Open WebUI secret may invalidate existing sessions/OAuth integrations.** Do not
change n8n's existing encryption key if its stored credentials depend on it.

### Bindings (default)

| Service | Host binding | Host port |
| :--- | :--- | ---: |
| Ollama API | `0.0.0.0` (LAN) | 11434 |
| Open WebUI | `0.0.0.0` (LAN) | 3000 |
| n8n | `127.0.0.1` | 5678 |
| Docker MCP Gateway | `127.0.0.1` | 8811 |
| SearXNG | `127.0.0.1` | 8081 |

For trusted-LAN registration, set `ollama_webui_enable_signup: true` in inventory.
Consider a firewall or an HTTPS reverse proxy before exposing any service beyond
that network. The Ollama backend API has no built-in user authentication.

### Connect Docker MCP Gateway to Open WebUI

The Compose stack starts a streaming HTTP MCP Gateway at
`http://ollama-mcp-gateway:8811/mcp` **on the shared Docker network**. It
requires a Bearer token (persistent in the `.env` file unless set with Vault).

In Open WebUI, navigate to **Settings → Integrations (admin) → External Tool
Servers → Add Connection** and select **MCP (Streamable HTTP)**. Use the internal
URL above and **Bearer** authentication using the exact gateway token. Do not
select OpenAPI or point WebUI to `localhost:8811` (that would be the WebUI
container, not the MCP Gateway). Tool registration is an administrator action;
this role deliberately doesn't overwrite previously saved Open WebUI connections.
Continue in VS Code requires its own MCP client registration.

**Docker socket warning:** the Gateway mounts the host's writable
`/var/run/docker.sock`. This grants powerful Docker daemon access. Keep the
Gateway private, authenticate clients, and enable only trusted MCP servers.
Loopback host binding protects the published port, not clients already on the
shared Docker network.

### GPU settings

By default the role preserves `ollama_gpu_device_ids: ["all"]` and
correctly renders it as `count: all` in Docker Compose rather than treating
"all" as a literal GPU device ID. For specific GPU IDs, set `ollama_gpu_device_ids` to valid device
IDs shown by `nvidia-smi -L`. Docker and the NVIDIA Container Toolkit must already
support GPU access.

### Data lifecycle

- `present`: Generate configuration, deploy the stack, optionally preload models.
- `absent`: Stop and remove containers, retaining data, Compose file and images.
- `teardown`: Stop the stack while still preserving persistent data by default.
- `ollama_teardown_remove_images: true`: Explicitly ask the helper to delete images.
- `ollama_teardown_remove_data: true`: **Permanently delete** `ollama_base_dir`
  including models, Open WebUI users/data, n8n workflows and credentials,
  SearXNG files, backups stored there, and generated `.env` secrets.

Always back up `/opt/ollama` before using the destructive override. The shared
`jcook3701.utils.container_engine` currently requests recreation on every
`present` deployment; avoiding unnecessary recreation would require a separate
change to that utility role.

### Image reproducibility and healthchecks

Images are configurable via role variables. The defaults retain upstream `latest`
/ `main` tags for compatibility; **pin tested version tags or image digests** in
inventory for stable production deployments. `ollama_pull_images: false` avoids
forcing a pull from `container_engine`, but mutable `latest` tags may still be
refreshed by Compose itself. Ollama, Open WebUI, n8n, SearXNG and Valkey have
healthchecks; MCP Gateway uses its own readiness logging and `/health` endpoint.

### Web search

Open WebUI is pointed at the internal SearXNG JSON search API. `settings.yml`
permits the `json` result format and Valkey supports the SearXNG limiter. If an
existing Open WebUI database already stores web-search settings, the administrator
may need to align those persisted settings with the new environment values.
Search availability does not guarantee that an Ollama model will call tools
correctly; model tool-call capability is separate from search infrastructure.

## Role Variables

### Runtime orchestration and service lifecycle

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_container_engine` | str | Container engine. Choices: `docker`, `podman` (experimental). | `docker` |
| `ollama_state` | str | Desired deployment lifecycle. Choices: `present`, `absent`, `teardown`. | `present` |
| `ollama_debug_mode` | bool | Enable safe, non-secret debugging output. | `false` |
| `ollama_teardown_remove_data` | bool | Explicitly delete the entire persistent data directory during teardown; destructive. | `false` |
| `ollama_teardown_remove_images` | bool | Explicitly remove stack images during teardown. | `false` |

### Optional services

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_manage_web_ui` | bool | Deploy Open WebUI alongside Ollama. | `true` |
| `ollama_manage_n8n` | bool | Deploy the n8n workflow editor and backend. | `true` |
| `ollama_manage_mcp` | bool | Deploy Docker MCP Gateway. Requires access to the Docker host socket. | `true` |
| `ollama_manage_searxng` | bool | Deploy SearXNG plus the supporting Valkey instance. | `true` |

### Images and restart policy

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_backend_image` | str | Ollama container image; pin tag or digest for repeatability. | `docker.io/ollama/ollama:latest` |
| `ollama_webui_image` | str | Open WebUI container image; pin tag or digest for repeatability. | `ghcr.io/open-webui/open-webui:main` |
| `ollama_n8n_image` | str | n8n container image; pin tag or digest for repeatability. | `docker.n8n.io/n8nio/n8n:latest` |
| `ollama_mcp_gateway_image` | str | Docker MCP Gateway container image; pin tag or digest for repeatability. | `docker/mcp-gateway:latest` |
| `ollama_searxng_image` | str | SearXNG container image; pin tag or digest for repeatability. | `docker.io/searxng/searxng:latest` |
| `ollama_searxng_valkey_image` | str | Valkey backend container image. | `docker.io/valkey/valkey:9-alpine` |
| `ollama_pull_policy` | str | Docker Compose service image pull policy; the latest tag may still be refreshed. Choices: `missing`, `always`, `never`, `build`. | `missing` |
| `ollama_pull_images` | bool | Ask the shared container_engine helper to pull images during deployment. | `false` |
| `ollama_restart_policy` | str | Restart policy for the container services. Choices: `no`, `always`, `on-failure`, `unless-stopped`. | `unless-stopped` |

### Container names

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_backend_container_name` | str | Ollama backend Docker container name. | `ollama` |
| `ollama_webui_container_name` | str | Open WebUI Docker container name. | `ollama-webui` |
| `ollama_n8n_container_name` | str | n8n Docker container name. | `ollama-n8n` |
| `ollama_mcp_gateway_container_name` | str | Docker MCP Gateway container name. | `ollama-mcp-gateway` |
| `ollama_searxng_container_name` | str | SearXNG Docker container name. | `searxng` |
| `ollama_searxng_valkey_container_name` | str | Valkey Docker container name. | `searxng-valkey` |

### Data and backend

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_base_dir` | path | Base path for persistent state, Compose file and generated secrets. | `/opt/ollama` |
| `ollama_backend_tty` | bool | Allocate a TTY for the Ollama backend. | `true` |
| `ollama_backend_keep_alive` | str | Ollama model keep-alive setting. | `24h` |

### Networking

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_host_bind_ip` | str | Legacy default bind IP for Ollama and WebUI, preserved for LAN use. | `0.0.0.0` |
| `ollama_backend_bind_ip` | str | Host binding address for the Ollama API. | `{{ ollama_host_bind_ip }}` |
| `ollama_webui_bind_ip` | str | Host binding address for Open WebUI. | `{{ ollama_host_bind_ip }}` |
| `ollama_n8n_bind_ip` | str | Host binding address for n8n; loopback by default. | `127.0.0.1` |
| `ollama_mcp_gateway_bind_ip` | str | Host binding address for Docker MCP Gateway; loopback by default. | `127.0.0.1` |
| `ollama_searxng_bind_ip` | str | Host binding address for SearXNG; loopback by default. | `127.0.0.1` |
| `ollama_external_port` | int | Host port for Ollama. | `11434` |
| `ollama_webui_external_port` | int | Host port for Open WebUI. | `3000` |
| `ollama_n8n_external_port` | int | Host port for n8n. | `5678` |
| `ollama_mcp_gateway_external_port` | int | Host port for the MCP Gateway. | `8811` |
| `ollama_searxng_external_port` | int | Host port for SearXNG. | `8081` |
| `ollama_internal_bind_ip` | str | Interface Ollama binds to inside the backend container. | `0.0.0.0` |
| `ollama_internal_port` | int | Ollama internal service port. | `11434` |
| `ollama_webui_internal_port` | int | Open WebUI internal service port. | `8080` |
| `ollama_n8n_internal_port` | int | n8n internal service port. | `5678` |
| `ollama_mcp_gateway_internal_port` | int | MCP Gateway internal service port. | `8811` |
| `ollama_searxng_internal_port` | int | SearXNG internal service port. | `8080` |

### Open WebUI configuration

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_webui_url` | str | Public Open WebUI URL; optionally set behind a reverse proxy. | `` |
| `ollama_webui_no_proxy` | str | List of hostnames bypassing HTTP proxies. | `localhost,127.0.0.1,ollama` |
| `ollama_webui_secret_key` | str | Optional Vault-provided persistent WebUI secret; empty generates /opt/ollama/.env value. | `` |
| `ollama_webui_auth` | bool | Require authentication in Open WebUI. | `true` |
| `ollama_webui_enable_signup` | bool | Enable Open WebUI account registration; opt in for trusted LAN users. | `false` |
| `ollama_webui_name` | str | Open WebUI display name. | `Ollama WebUI` |
| `ollama_webui_environment` | str | Open WebUI runtime environment. | `prod` |
| `ollama_backend_internal_url` | str | Internal Ollama service URL used by WebUI. | `http://ollama:11434` |

### n8n configuration

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_n8n_host` | str | Hostname n8n uses when generating links; empty uses ansible_fqdn. | `` |
| `ollama_n8n_protocol` | str | Protocol n8n reports in generated URLs. Choices: `http`, `https`. | `http` |
| `ollama_n8n_listen_address` | str | n8n container internal bind address. | `0.0.0.0` |
| `ollama_n8n_secure_cookie` | bool | Enable secure n8n cookies behind HTTPS. | `false` |
| `ollama_n8n_timezone` | str | Timezone for n8n workflows. | `America/Los_Angeles` |
| `ollama_n8n_proxy_hops` | int | Trusted reverse proxy hop count for n8n. | `0` |
| `ollama_n8n_encryption_key` | str | Optional Vault-provided n8n encryption key; empty preserves n8n-generated key. | `` |
| `ollama_n8n_editor_base_url` | str | Optional external n8n editor URL. | `` |
| `ollama_n8n_webhook_url` | str | Optional external webhook URL. | `` |
| `ollama_n8n_mcp_base_url` | str | Optional n8n MCP URL. | `` |

### Docker MCP Gateway

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_mcp_gateway_transport` | str | Docker MCP Gateway transport. Choices: `streaming`, `sse`. | `streaming` |
| `ollama_mcp_gateway_servers` | list[str] | Names of enabled Docker MCP catalog servers. | `["duckduckgo"]` |
| `ollama_mcp_gateway_auth_token` | str | Optional Vault-managed gateway bearer token; empty uses persistent generated token. | `` |

### SearXNG

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_searxng_secret_key` | str | Optional Vault-managed SearXNG secret; empty generates persistent secret. | `` |
| `ollama_searxng_instance_name` | str | SearXNG instance name displayed in its UI. | `SearXNG` |
| `ollama_searxng_safe_search` | int | SearXNG safe search level (0=off, 1=moderate, 2=strict). Choices: `0`, `1`, `2`. | `1` |
| `ollama_searxng_limiter` | bool | Enable SearXNG bot detection limiter. | `true` |
| `ollama_searxng_limiter_pass_ips` | list[str] | Explicitly trusted IPs or CIDRs bypassing SearXNG limits. | `[]` |
| `ollama_searxng_image_proxy` | bool | Enable SearXNG image proxying. | `true` |
| `ollama_searxng_valkey_url` | str | Internal Valkey URL consumed by SearXNG. | `valkey://searxng-valkey:6379/0` |

### Web search integration

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_webui_enable_rag_web_search` | bool | Enable WebUI web search when the local SearXNG service is enabled. | `true` |
| `ollama_webui_rag_web_search_engine` | str | WebUI web search engine selection. | `searxng` |
| `ollama_webui_searxng_query_url` | str | SearXNG search URL from Open WebUI network. | `http://searxng:8080/search` |
| `ollama_webui_searxng_language` | str | Default SearXNG search language. | `all` |

### NVIDIA GPU

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_enable_gpu` | bool | Enable NVIDIA GPU runtime and device reservations for Ollama. | `true` |
| `ollama_docker_runtime` | str | Docker runtime used for NVIDIA GPU allocation. | `nvidia` |
| `ollama_gpu_device_ids` | list[str] | NVIDIA device IDs; `["all"]` requests all GPUs using Compose `count: all`. | `["all"]` |
| `ollama_gpu_device_count` | str/int | GPU reservation count, or all when device_ids is empty. | `all` |
| `ollama_gpu_capabilities` | list[str] | GPU reservation capabilities. | `["gpu", "compute", "utility"]` |
| `ollama_nvidia_driver_capabilities` | str | NVIDIA_DRIVER_CAPABILITIES for Ollama. | `compute,utility` |

### Model preloading

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_manage_models` | bool | Enable post-deployment model downloads. | `false` |
| `ollama_preload_models` | list[str] | List of Ollama model names to preload when management is enabled. | `["deepseek-r1:32b", "qwen2.5-coder:32b", "qwen2.5-coder:7b", "llama3.1:8b", "qwen2.5-coder:1.5b-base", "nomic-embed-text:latest"]` |

## Internal Variables

`vars/main.yml` deliberately groups paths into the `ollama_directory` and
`ollama_file` dictionaries with explicit Jinja2 `default()` expressions,
matching the existing project conventions. The added `ollama_file.secrets`
entry points to the persistent root-only `.env` file. No generated secrets are
stored in the Ansible repository.

## Author Information

Maintained by **Jared W. Cook** as part of the core infrastructure and container
management ecosystem. Licensed under AGPL-3.0-or-later.

## Helpful links

- [Ollama Docker documentation](https://docs.ollama.com/docker)
- [Docker Compose GPU support](https://docs.docker.com/compose/how-tos/gpu-support/)
- [Open WebUI MCP integration](https://docs.openwebui.com/features/extensibility/mcp/)
- [Docker MCP Gateway docs](https://github.com/docker/mcp-gateway)
- [SearXNG Docker setup](https://docs.searxng.org/admin/installation-docker.html)
- [n8n Docker setup](https://docs.n8n.io/hosting/installation/docker/)
