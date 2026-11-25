# Docker MCP Gateway

Deploy Docker MCP Gateway through the collection's shared container engine.
Docker Engine, Compose v2, `community.docker`, and `jcook3701.utils` are required.

The default listener is `http://127.0.0.1:8811/mcp` and clients send the gateway's bearer token.
The role stores its generated token in a private deployment file. The gateway's writable
Docker socket grants host-level Docker access. Enable only trusted catalog servers.

With the optional relay enabled, join FreeLLMAPI and the gateway to the same Docker network.
In FreeLLMAPI, enable MCP under **Keys → Agent compatibility**, then set
`docker_mcp_gateway_freellmapi_api_key` from Vault using the unified `freellmapi-…` key.
The gateway launches the relay as a Docker MCP server on its own networks. The relay
exposes `ask_freellmapi`, `list_models`, and `healthcheck` to gateway clients.
The gateway keeps its default private-URL checks for remote catalog entries.

To expose LongMemory through the same gateway, start LongMemory with
`longmemory_enable_mcp: true` and join it to `docker_mcp_gateway_shared_network`
using `longmemory_shared_network`. Set `docker_mcp_gateway_enable_longmemory_relay: true`
and supply the same existing Vault key to both roles through `longmemory_api_key`
and `docker_mcp_gateway_longmemory_api_key`. The gateway exposes
`longmemory_recall`, `longmemory_ingest`, and the other supported LongMemory tools.

When migrating from Ollama, supply the existing gateway token as `docker_mcp_gateway_auth_token`
to keep client authentication working.

## Install the complete AI stack

The collection's `playbooks/ai_stack.yml` installs the standalone roles along with
Ollama, FreeLLMAPI, LongMemory, and Headroom. Add your Docker host to the
`ai_stack_hosts` inventory group, then run:

```bash
ansible-playbook -i inventory jcook3701.docker.ai_stack
```

The playbook creates the shared Docker network, configures Open WebUI to use
Ollama and SearXNG, and preloads LongMemory's embedding model. Set
`ai_stack_ollama_models` to preload additional models. When deploying the Ollama
role separately, rerun the stack playbook to restore the shared network connection
if Compose recreated the Ollama container.

For an existing bundled install, first back up its data and remove the bundled
service containers you are moving. The complete playbook checks for those containers
before installing. Migrate one service at a time by running its role separately.
Retain the old data and credentials until the new service is verified.

To enable the FreeLLMAPI relay after initializing FreeLLMAPI, set these inventory
variables and rerun the gateway role with the same shared network:

```yaml
docker_mcp_gateway_enable_freellmapi_relay: true
docker_mcp_gateway_shared_network: "ai-stack"
docker_mcp_gateway_freellmapi_api_key: "{{ vault_freellmapi_unified_api_key }}"
```

Add `http://127.0.0.1:8811/mcp` to a local MCP client using the gateway token.
Confirm the client lists `ask_freellmapi` after starting the relay.

## Lifecycle

- `present` configures and starts the stack.
- `absent` removes the Compose stack, preserving its data and configuration.
- `teardown` also removes the Compose file. Image and data removal require explicit flags.

The data removal flag removes the entire role deployment directory. Keep this directory
dedicated to this role. Data stored outside it is retained.

## Role Variables

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `docker_mcp_gateway_container_engine` | str | Container engine. Choices: `docker`. | `docker` |
| `docker_mcp_gateway_state` | str | Deployment lifecycle. Choices: `present`, `absent`, `teardown`. | `present` |
| `docker_mcp_gateway_teardown_remove_data` | bool | Permanently remove role files and data within the deployment directory. | `false` |
| `docker_mcp_gateway_teardown_remove_images` | bool | Remove the Compose service images during teardown. | `false` |
| `docker_mcp_gateway_image` | str | Container image reference. | `docker/mcp-gateway@sha256:f5a679a05fc39022a046167bef92aeeb01bcd59485ad27843ae5227db7950688` |
| `docker_mcp_gateway_container_name` | str | Container name. | `docker-mcp-gateway` |
| `docker_mcp_gateway_pull_policy` | str | Compose pull policy. Choices: `missing`, `always`, `never`. | `missing` |
| `docker_mcp_gateway_pull_images` | bool | Ask the shared container engine to force image pulls. | `false` |
| `docker_mcp_gateway_restart_policy` | str | Container restart policy. Choices: `no`, `always`, `on-failure`, `unless-stopped`. | `unless-stopped` |
| `docker_mcp_gateway_base_dir` | path | Deployment directory for Compose files and managed state. | `/opt/docker-mcp-gateway` |
| `docker_mcp_gateway_bind_ip` | str | Published host address. | `127.0.0.1` |
| `docker_mcp_gateway_external_port` | int | Published host port. | `8811` |
| `docker_mcp_gateway_internal_port` | int | Service port inside the container. | `8811` |
| `docker_mcp_gateway_shared_network` | str | Optional existing Docker network for private service connections. | `""` |
| `docker_mcp_gateway_transport` | str | Gateway HTTP transport. Choices: `streaming`, `sse`. | `streaming` |
| `docker_mcp_gateway_servers` | list | Docker catalog servers to enable. | `["duckduckgo"]` |
| `docker_mcp_gateway_auth_token` | str | Inbound bearer token. Empty generates a persistent token. | `""` |
| `docker_mcp_gateway_enable_freellmapi_relay` | bool | Enable the optional FreeLLMAPI relay. | `false` |
| `docker_mcp_gateway_freellmapi_mcp_url` | str | FreeLLMAPI MCP endpoint reachable from the relay container. | `http://freellmapi:3001/mcp` |
| `docker_mcp_gateway_freellmapi_api_key` | str | FreeLLMAPI unified bearer key. Required when the relay is enabled. | `""` |
| `docker_mcp_gateway_enable_longmemory_relay` | bool | Enable the optional LongMemory relay. | `false` |
| `docker_mcp_gateway_longmemory_mcp_url` | str | LongMemory MCP endpoint reachable from the relay container. | `http://longmemory:7331/mcp` |
| `docker_mcp_gateway_longmemory_api_key` | str | Existing LongMemory bearer key. Required when the relay is enabled. | `""` |

## Example

```yaml
---
- name: Deploy Docker MCP Gateway
  hosts: "docker_mcp_gateway_hosts"
  become: true
  roles:
    - role: "jcook3701.docker.docker_mcp_gateway"
```

## Author Information

Maintained by **Jared W. Cook**. Licensed under AGPL-3.0-or-later.
