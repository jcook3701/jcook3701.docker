# Ollama

[Ollama](https://ollama.com/) runs open-source models locally. This Ansible role
(`jcook3701.docker.ollama`) deploys a Docker Compose stack with optional
[Open WebUI](https://docs.openwebui.com/), [n8n](https://docs.n8n.io/),
[Docker MCP Gateway](https://github.com/docker/mcp-gateway),
[MCP Inspector](https://github.com/modelcontextprotocol/inspector), and
[SearXNG](https://docs.searxng.org/) with Valkey.

The role preserves the original `present`, `absent`, and `teardown` structure and
calls `jcook3701.utils.container_engine`. Docker Compose is the tested target
of this role; Podman support remains experimental, and Docker MCP Gateway
requires a Docker daemon and socket.

## Installation and upgrade

1. Keep the existing persistent `/opt/ollama` directory and Compose stack
   until you have backed them up.
2. Update the Ollama role files in `jcook3701.docker`.
3. Run your existing playbook with `ollama_state: present`.
4. Check `docker compose -f /opt/ollama/compose.yml ps` and verify the
   service health checks.

The role generates `/opt/ollama/.env` (mode `0600`) containing stable, random
secrets for Open WebUI, SearXNG, and Docker MCP Gateway. Existing nonempty
values in this file are preserved on subsequent runs.

You may instead provide the `ollama_webui_secret_key`,
`ollama_searxng_secret_key`, and `ollama_mcp_gateway_auth_token` options from
Ansible Vault.

Changing an existing Open WebUI secret may invalidate existing sessions
and OAuth integrations. Do not change n8n's existing encryption key if its
stored credentials depend on it.

### Bindings (default)

| Service | Host binding | Host port |
| :--- | :--- | ---: |
| Ollama API | `0.0.0.0` (LAN) | 11434 |
| Open WebUI | `0.0.0.0` (LAN) | 3000 |
| n8n | `127.0.0.1` | 5678 |
| Docker MCP Gateway | `127.0.0.1` | 8811 |
| MCP Inspector UI | `127.0.0.1` | 6274 |
| MCP Inspector Apps sandbox | `127.0.0.1` | 6275 |
| MCP Inspector app origin | `127.0.0.1` | 6278 |
| SearXNG | `127.0.0.1` | 8081 |

For trusted-LAN registration, set `ollama_webui_enable_signup: true` in
inventory. Consider a firewall or an HTTPS reverse proxy before exposing
any service beyond that network.

The Ollama backend API has no built-in user authentication.

### Connect Docker MCP Gateway to Open WebUI

The Compose stack starts a streaming HTTP MCP Gateway at
`http://ollama-mcp-gateway:8811/mcp` on the shared Docker network.

It requires a Bearer token, persistent in `.env` unless supplied through Vault.

In Open WebUI, navigate to **Settings → Integrations (admin) → External Tool
Servers → Add Connection** and select **MCP (Streamable HTTP)**.

Use the internal URL and Bearer authentication with the exact gateway token.

Do not select OpenAPI or point WebUI to `localhost:8811`; that address would
refer to the WebUI container rather than the MCP Gateway.

Tool registration is an administrator action. This role does not overwrite
previously saved Open WebUI connections. Continue in VS Code requires its
own MCP client registration.

**Docker socket warning:** the Gateway mounts the host's writable
`/var/run/docker.sock`. This grants powerful Docker daemon access.

Keep the Gateway private, authenticate clients, and enable only trusted MCP
servers. Loopback host binding protects the published port, not clients
already on the shared Docker network.

## MCP Inspector

MCP Inspector provides a graphical interface for inspecting MCP servers,
discovering tools, examining resources, and testing MCP requests.

The role deploys the official Inspector container through the same
Docker Compose stack as Ollama.

MCP Inspector is enabled by default using:

```yaml
ollama_manage_mcp_inspector: true
```

Set the variable to `false` to exclude Inspector from the generated stack.

### Accessing MCP Inspector

MCP Inspector uses the following local address:

```text
http://127.0.0.1:6274/
```

To use Inspector from a workstation, establish an SSH tunnel to the
host running Docker:

```shell
ssh -N \
  -L 6274:127.0.0.1:6274 \
  -L 6275:127.0.0.1:6275 \
  -L 6278:127.0.0.1:6278 \
  jcook@second-chance.jcook3701.com
```

Open the following URL in the workstation's browser:

```text
http://127.0.0.1:6274/
```

The official image generates an Inspector API token on startup.

Retrieve the authentication link or token from the container logs:

```shell
docker logs ollama-mcp-inspector
```

Do not disable Inspector authentication merely to simplify browser access.

### MCP Inspector and Docker MCP Gateway

When Docker MCP Gateway management is enabled, the Inspector catalog
is initialized with this server:

```json
{
  "mcpServers": {
    "Docker MCP Gateway": {
      "type": "streamable-http",
      "url": "http://ollama-mcp-gateway:8811/mcp"
    }
  }
}
```

The URL uses Docker Compose networking to reach the existing gateway.

The initial catalog does not contain the gateway's Bearer token.

In Inspector, select the Docker MCP Gateway entry and configure an
Authorization header containing the gateway's Bearer token.

The token can be retrieved from the existing root-only `.env` file
when the gateway uses the role-generated secret:

```shell
sudo grep '^OLLAMA_MCP_GATEWAY_AUTH_TOKEN=' /opt/ollama/.env
```

Only copy the token into your authenticated Inspector session.

Do not commit the token or share it in logs or chat messages.

If the gateway token was explicitly supplied using
`ollama_mcp_gateway_auth_token`, use that configured value instead.

### Persistent Inspector storage

MCP Inspector keeps its writable server catalog and session state in:

```text
/opt/ollama/mcp-inspector/
```

The Inspector container mounts that directory at:

```text
/home/node/.mcp-inspector/
```

The default catalog path is:

```text
/opt/ollama/mcp-inspector/mcp.json
```

The role creates the catalog only if it does not already exist.

The Inspector GUI owns subsequent edits to the catalog. Running Ansible
again does not overwrite user-added MCP servers.

The directory is owned by the Inspector container's UID and GID `1000`
and is created with mode `0700`.

### Encrypted Inspector secrets

Inspector v2 can persist OAuth tokens and other supported secrets to its
local secret store when persistent storage is mounted.

The role provides an encryption key file outside that storage directory:

```text
/opt/ollama/mcp-inspector-secret-key
```

The container reads it at:

```text
/run/secrets/mcp_inspector_secret_key
```

using the `MCP_INSPECTOR_SECRET_KEY_FILE` environment variable.

The key is created with mode `0600`, owned by UID and GID `1000`.

When `ollama_mcp_inspector_secret_key` is empty, the role generates a
random key on first deployment and preserves it on subsequent runs.

When a Vault-provided key is configured before first deployment, that
value initializes the file instead.

Changing the variable after the key file exists does not automatically
rotate the stored key. This prevents accidental loss of access to
existing encrypted secrets.

**Back up both the Inspector storage directory and its encryption key.**
Losing the key can make persisted secrets unreadable.

HTTP request headers stored in Inspector's server catalog may still
contain plaintext credentials. Encryption of Inspector's secret store
does not encrypt arbitrary catalog headers.

Protect the catalog, the key, and backups containing either file.

### Security considerations

MCP Inspector is a development and diagnostic tool. Its backend can
launch processes and execute MCP tool calls.

By default, all Inspector ports are bound to `127.0.0.1` on the host.

Do not expose these ports to an untrusted network.

For remote access, prefer an SSH tunnel or an authenticated HTTPS
reverse proxy with appropriate host and origin restrictions.

The Inspector container does not mount the Docker socket directly.

It reaches Docker MCP Gateway through the shared Compose network.
That gateway does have Docker socket access, so the tools exposed
through it should be treated as privileged.

Inspector's ports serve different purposes:

- `6274`: main Inspector web interface.
- `6275`: MCP Apps sandbox.
- `6278`: dedicated app origins.

All three ports are included so Inspector's Apps interface can
work when MCP servers provide embedded applications.

When customizing the ports, the Inspector UI host port must match
its container port. Sandbox and app-origin ports are also published
without remapping.

For access through a reverse proxy, configure the browser origins
and any additional sandbox or app-origin addresses according to
the upstream MCP Inspector documentation.

### MCP Inspector health check

The official Inspector image includes a health check against:

```text
http://127.0.0.1:6274/healthz
```

The endpoint returns a successful status when the Inspector web
backend is ready.

Verify container status using:

```shell
docker compose -f /opt/ollama/compose.yml ps ollama-mcp-inspector
```

Inspect startup logs using:

```shell
docker logs --tail 100 ollama-mcp-inspector
```

## GPU settings

By default the role preserves `ollama_gpu_device_ids: ["all"]` and
correctly renders it as `count: all` in Docker Compose rather than
treating "all" as a literal GPU device ID.

For specific GPU IDs, set `ollama_gpu_device_ids` to valid device IDs
shown by `nvidia-smi -L`.

Docker and the NVIDIA Container Toolkit must already support GPU access.

## Data lifecycle

- `present`: Generate configuration, deploy the stack, optionally preload models.
- `absent`: Stop and remove containers, retaining data, Compose file and images.
- `teardown`: Stop the stack while still preserving persistent data by default.
- `ollama_teardown_remove_images: true`: Explicitly ask the helper to delete images.
- `ollama_teardown_remove_data: true`: Permanently delete `ollama_base_dir`,
  including models, Open WebUI data, n8n workflows and credentials, SearXNG
  files, MCP Inspector data, and generated secrets.

Always back up `/opt/ollama` before using the destructive override.

The shared `jcook3701.utils.container_engine` currently requests recreation
on every `present` deployment; avoiding unnecessary recreation would
require a separate change to that utility role.

The Inspector catalog and encryption key are stored on the host and
survive routine container recreation.

## Image reproducibility and health checks

Images are configurable via role variables.

The defaults retain upstream `latest` and `main` tags for compatibility.
Pin tested version tags or image digests in inventory for stable production
deployments.

`ollama_pull_images: false` avoids forcing a pull from `container_engine`,
but mutable image tags may still be refreshed by Compose itself.

Ollama, Open WebUI, n8n, SearXNG, and Valkey have health checks.

MCP Inspector uses the official image's built-in `/healthz` health check.

MCP Gateway uses its readiness logging and `/health` endpoint.

## Web search

Open WebUI is pointed at the internal SearXNG JSON search API.

`settings.yml` permits the `json` result format. The SearXNG limiter is
disabled by default because direct Compose-network requests do not carry
the trusted client-IP headers that the limiter requires.

Enable it only when SearXNG is behind a trusted reverse proxy that
supplies `X-Forwarded-For` and `X-Real-IP`, then configure
`ollama_searxng_limiter_pass_ips` as needed.

If an existing Open WebUI database already stores web-search settings,
the administrator may need to align those persisted settings with the
new environment values.

Search availability does not guarantee that an Ollama model will call
tools correctly; model tool-call capability is separate from search
infrastructure.

## Role Variables

### Runtime orchestration and service lifecycle

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_container_engine` | str | Container engine: `docker`, `podman` (experimental). | `docker` |
| `ollama_state` | str | Lifecycle: `present`, `absent`, `teardown`. | `present` |
| `ollama_debug_mode` | bool | Enable safe, non-secret debugging output. | `false` |
| `ollama_teardown_remove_data` | bool | Delete persistent data during teardown; destructive. | `false` |
| `ollama_teardown_remove_images` | bool | Remove stack images during teardown. | `false` |

### Optional services

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_manage_web_ui` | bool | Deploy Open WebUI. | `true` |
| `ollama_manage_n8n` | bool | Deploy n8n. | `true` |
| `ollama_manage_mcp` | bool | Deploy Docker MCP Gateway. | `true` |
| `ollama_manage_mcp_inspector` | bool | Deploy MCP Inspector. | `true` |
| `ollama_manage_searxng` | bool | Deploy SearXNG and Valkey. | `true` |

### Images and restart policy

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_backend_image` | str | Ollama image. | `docker.io/ollama/ollama:latest` |
| `ollama_webui_image` | str | Open WebUI image. | `ghcr.io/open-webui/open-webui:main` |
| `ollama_n8n_image` | str | n8n image. | `docker.n8n.io/n8nio/n8n:latest` |
| `ollama_mcp_gateway_image` | str | Docker MCP Gateway image. | `docker/mcp-gateway:latest` |
| `ollama_mcp_inspector_image` | str | MCP Inspector image. | `ghcr.io/modelcontextprotocol/inspector:latest` |
| `ollama_searxng_image` | str | SearXNG image. | `docker.io/searxng/searxng:latest` |
| `ollama_searxng_valkey_image` | str | Valkey image. | `docker.io/valkey/valkey:9-alpine` |
| `ollama_pull_policy` | str | Compose image pull policy. | `missing` |
| `ollama_pull_images` | bool | Request image pulls from the shared helper. | `false` |
| `ollama_restart_policy` | str | Container restart policy. | `unless-stopped` |

### Container names

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_backend_container_name` | str | Ollama container name. | `ollama` |
| `ollama_webui_container_name` | str | Open WebUI container name. | `ollama-webui` |
| `ollama_n8n_container_name` | str | n8n container name. | `ollama-n8n` |
| `ollama_mcp_gateway_container_name` | str | Docker MCP Gateway container name. | `ollama-mcp-gateway` |
| `ollama_mcp_inspector_container_name` | str | Inspector container name. | `ollama-mcp-inspector` |
| `ollama_searxng_container_name` | str | SearXNG container name. | `searxng` |
| `ollama_searxng_valkey_container_name` | str | Valkey container name. | `searxng-valkey` |

### Data and backend

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_base_dir` | path | Persistent stack base directory. | `/opt/ollama` |
| `ollama_backend_tty` | bool | Allocate an Ollama backend TTY. | `true` |
| `ollama_backend_keep_alive` | str | Model keep-alive setting. | `24h` |

### Networking

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_host_bind_ip` | str | Default bind IP for Ollama and WebUI. | `0.0.0.0` |
| `ollama_backend_bind_ip` | str | Ollama host bind IP. | `{{ ollama_host_bind_ip }}` |
| `ollama_webui_bind_ip` | str | WebUI host bind IP. | `{{ ollama_host_bind_ip }}` |
| `ollama_n8n_bind_ip` | str | n8n host bind IP. | `127.0.0.1` |
| `ollama_mcp_gateway_bind_ip` | str | Gateway host bind IP. | `127.0.0.1` |
| `ollama_mcp_inspector_bind_ip` | str | Inspector host bind IP. | `127.0.0.1` |
| `ollama_searxng_bind_ip` | str | SearXNG host bind IP. | `127.0.0.1` |
| `ollama_external_port` | int | Ollama host port. | `11434` |
| `ollama_webui_external_port` | int | WebUI host port. | `3000` |
| `ollama_n8n_external_port` | int | n8n host port. | `5678` |
| `ollama_mcp_gateway_external_port` | int | Gateway host port. | `8811` |
| `ollama_mcp_inspector_external_port` | int | Inspector UI host port. | `6274` |
| `ollama_searxng_external_port` | int | SearXNG host port. | `8081` |
| `ollama_internal_bind_ip` | str | Ollama internal bind IP. | `0.0.0.0` |
| `ollama_internal_port` | int | Ollama internal port. | `11434` |
| `ollama_webui_internal_port` | int | WebUI internal port. | `8080` |
| `ollama_n8n_internal_port` | int | n8n internal port. | `5678` |
| `ollama_mcp_gateway_internal_port` | int | Gateway internal port. | `8811` |
| `ollama_mcp_inspector_internal_port` | int | Inspector UI internal port. | `6274` |
| `ollama_mcp_inspector_sandbox_port` | int | Inspector Apps sandbox port. | `6275` |
| `ollama_mcp_inspector_app_origin_port` | int | Inspector app-origin port. | `6278` |
| `ollama_searxng_internal_port` | int | SearXNG internal port. | `8080` |

### Open WebUI configuration

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_webui_url` | str | Public WebUI URL. | `""` |
| `ollama_webui_no_proxy` | str | Hosts bypassing proxy settings. | `localhost,127.0.0.1,ollama` |
| `ollama_webui_secret_key` | str | Optional persistent WebUI secret. | `""` |
| `ollama_webui_auth` | bool | Enable WebUI authentication. | `true` |
| `ollama_webui_enable_signup` | bool | Enable user registration. | `false` |
| `ollama_webui_name` | str | WebUI display name. | `Ollama WebUI` |
| `ollama_webui_environment` | str | Runtime environment. | `prod` |
| `ollama_backend_internal_url` | str | WebUI Ollama endpoint. | `http://ollama:11434` |

### n8n configuration

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_n8n_host` | str | n8n public hostname override. | `""` |
| `ollama_n8n_protocol` | str | n8n protocol: `http`, `https`. | `http` |
| `ollama_n8n_listen_address` | str | n8n internal bind address. | `0.0.0.0` |
| `ollama_n8n_secure_cookie` | bool | Require HTTPS cookies. | `false` |
| `ollama_n8n_timezone` | str | Workflow timezone. | `America/Los_Angeles` |
| `ollama_n8n_proxy_hops` | int | Trusted proxy hop count. | `0` |
| `ollama_n8n_encryption_key` | str | Optional persistent encryption key. | `""` |
| `ollama_n8n_editor_base_url` | str | External editor URL. | `""` |
| `ollama_n8n_webhook_url` | str | External webhook URL. | `""` |
| `ollama_n8n_mcp_base_url` | str | Optional MCP base URL. | `""` |

### Docker MCP Gateway

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_mcp_gateway_transport` | str | Gateway transport: `streaming`, `sse`. | `streaming` |
| `ollama_mcp_gateway_servers` | list[str] | Enabled Docker MCP catalog servers. | `["duckduckgo"]` |
| `ollama_mcp_gateway_auth_token` | str | Optional Vault-managed bearer token. | `""` |

### MCP Inspector

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_mcp_inspector_allowed_origins` | list[str] | Browser origins allowed to access Inspector; empty uses upstream defaults. | `[]` |
| `ollama_mcp_inspector_secret_key` | str | Optional Vault-provided secret-store encryption key; empty generates a persistent key file. | `""` |

### SearXNG

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_searxng_secret_key` | str | Optional persistent SearXNG secret. | `""` |
| `ollama_searxng_instance_name` | str | SearXNG instance name. | `SearXNG` |
| `ollama_searxng_safe_search` | int | Safe search: `0`, `1`, `2`. | `1` |
| `ollama_searxng_limiter` | bool | Enable limiter behind a trusted proxy. | `false` |
| `ollama_searxng_limiter_pass_ips` | list[str] | Trusted bypass IPs or CIDRs. | `[]` |
| `ollama_searxng_image_proxy` | bool | Enable image proxying. | `true` |
| `ollama_searxng_valkey_url` | str | Valkey connection URL. | `valkey://searxng-valkey:6379/0` |

### Web search integration

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_webui_enable_rag_web_search` | bool | Enable WebUI web search. | `true` |
| `ollama_webui_rag_web_search_engine` | str | Search engine. | `searxng` |
| `ollama_webui_searxng_query_url` | str | Internal search endpoint. | `http://searxng:8080/search` |
| `ollama_webui_searxng_language` | str | Default search language. | `all` |

### NVIDIA GPU

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_enable_gpu` | bool | Enable NVIDIA GPU support. | `true` |
| `ollama_docker_runtime` | str | NVIDIA Docker runtime. | `nvidia` |
| `ollama_gpu_device_ids` | list[str] | Device IDs; `["all"]` requests every GPU. | `["all"]` |
| `ollama_gpu_device_count` | str/int | GPU reservation count. | `all` |
| `ollama_gpu_capabilities` | list[str] | GPU device capabilities. | `["gpu", "compute", "utility"]` |
| `ollama_nvidia_driver_capabilities` | str | NVIDIA driver capabilities. | `compute,utility` |

### Model preloading

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ollama_manage_models` | bool | Enable model preloading. | `false` |
| `ollama_preload_models` | list[str] | Models to preload when enabled. | `["deepseek-r1:32b", "qwen2.5-coder:32b", "qwen2.5-coder:7b", "llama3.1:8b", "qwen2.5-coder:1.5b-base", "nomic-embed-text:latest"]` |

## Internal Variables

`vars/main.yml` groups paths into `ollama_directory` and `ollama_file`
dictionaries using the existing project conventions.

The `ollama_file.secrets` entry points to the persistent root-only `.env`
file. MCP Inspector adds `ollama_directory.mcp_inspector`,
`ollama_file.mcp_inspector_catalog`, and
`ollama_file.mcp_inspector_secret_key`.

No generated secrets are stored in the Ansible repository.

## Author Information

Maintained by **Jared W. Cook** as part of the core infrastructure and
container management ecosystem. Licensed under AGPL-3.0-or-later.

## Helpful links

- [Ollama Docker documentation](https://docs.ollama.com/docker)
- [Docker Compose GPU support](https://docs.docker.com/compose/how-tos/gpu-support/)
- [Open WebUI MCP integration](https://docs.openwebui.com/features/extensibility/mcp/)
- [Docker MCP Gateway docs](https://github.com/docker/mcp-gateway)
- [MCP Inspector documentation](https://github.com/modelcontextprotocol/inspector)
- [MCP Inspector Docker deployment](https://github.com/modelcontextprotocol/inspector/blob/main/docs/docker.md)
- [SearXNG Docker setup](https://docs.searxng.org/admin/installation-docker.html)
- [n8n Docker setup](https://docs.n8n.io/hosting/installation/docker/)
