# Ollama

[Ollama](https://github.com/ollama/ollama) is an open-source platform that lets you download, manage, and run large language models (LLMs) directly on your own computer.

## Role Variables

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| **Runtime Orchestration Engine and Service State** | | | |
| `ollama_container_engine` | `str` | Container engine: `docker`, `podman` | `docker` |
| `ollama_state` | `str` | Desired service state: `present`, `absent`, `teardown` | `present` |
| `ollama_debug_mode` | `bool` | Enable additional debug output during role execution. | `false` |
| **Optional Service Management** | | | |
| `ollama_manage_web_ui` | `bool` | Enable management and deployment of Open WebUI. | `true` |
| `ollama_manage_n8n` | `bool` | Enable management and deployment of n8n workflow automation. | `true` |
| `ollama_manage_mcp` | `bool` | Enable management and deployment of Docker MCP Gateway. | `true` |
| `ollama_manage_searxng` | `bool` | Enable management and deployment of SearXNG and its supporting services. | `true` |
| **Service Container Images and Engine Versions** | | | |
| `ollama_backend_image` | `str` | Container image used for the Ollama backend. | `docker.io/ollama/ollama:latest` |
| `ollama_webui_image` | `str` | Container image used for Open WebUI. | `ghcr.io/open-webui/open-webui:main` |
| `ollama_n8n_image` | `str` | Container image used for n8n workflow automation. | `docker.n8n.io/n8nio/n8n:latest` |
| `ollama_mcp_gateway_image` | `str` | Container image used for Docker MCP Gateway. | `docker/mcp-gateway:latest` |
| `ollama_searxng_image` | `str` | Container image used for the SearXNG search engine. | `docker.io/searxng/searxng:latest` |
| `ollama_searxng_valkey_image` | `str` | Container image used for the SearXNG Valkey backend. | `docker.io/valkey/valkey:9-alpine` |
| **Container Names** | | | |
| `ollama_backend_container_name` | `str` | Container name assigned to the Ollama backend. | `ollama` |
| `ollama_webui_container_name` | `str` | Container name assigned to Open WebUI. | `ollama-webui` |
| `ollama_n8n_container_name` | `str` | Container name assigned to n8n. | `ollama-n8n` |
| `ollama_mcp_gateway_container_name` | `str` | Container name assigned to Docker MCP Gateway. | `ollama-mcp-gateway` |
| `ollama_searxng_container_name` | `str` | Container name assigned to SearXNG. | `searxng` |
| `ollama_searxng_valkey_container_name` | `str` | Container name assigned to the SearXNG Valkey backend. | `searxng-valkey` |
| **Infrastructure Storage and Path Routing** | | | |
| `ollama_base_dir` | `path` | Base directory for Ollama application data and deployment files. | `/opt/ollama` |
| **Telly Terminal Configuration** | | | |
| `ollama_backend_tty` | `bool` | Allocate a pseudo-TTY for the Ollama backend container. | `true` |
| **Networking Configuration** | | | |
| `ollama_host_bind_ip` | `str` | Host IP address used to bind published container ports. | `0.0.0.0` |
| `ollama_internal_bind_ip` | `str` | Internal IP address on which the Ollama backend listens inside its container. | `0.0.0.0` |
| `ollama_external_port` | `int` | Host port mapped to the Ollama backend container. | `11434` |
| `ollama_webui_external_port` | `int` | Host port mapped to the Open WebUI frontend container. | `3000` |
| `ollama_n8n_external_port` | `int` | Host port mapped to the n8n container. | `5678` |
| `ollama_mcp_gateway_external_port` | `int` | Host port mapped to Docker MCP Gateway. | `8811` |
| `ollama_searxng_external_port` | `int` | Host port mapped to the SearXNG container. | `8081` |
| `ollama_internal_port` | `int` | Internal listening port of the Ollama backend. | `11434` |
| `ollama_webui_internal_port` | `int` | Internal listening port of Open WebUI. | `3000` |
| `ollama_n8n_internal_port` | `int` | Internal listening port of n8n. | `5678` |
| `ollama_mcp_gateway_internal_port` | `int` | Internal listening port of Docker MCP Gateway. | `8811` |
| `ollama_searxng_internal_port` | `int` | Internal listening port of SearXNG. | `8080` |
| **Application Security Credentials** | | | |
| `ollama_webui_url` | `str` | Public URL used to access Open WebUI. Leave empty when no external URL is configured. | `""` |
| `ollama_webui_no_proxy` | `str` | Comma-separated addresses that bypass configured HTTP proxies. | `localhost,127.0.0.1,ollama` |
| `ollama_webui_secret_key` | `str` | Persistent secret key used by Open WebUI for session and application security. | `change_this_to_a_secure_random_string_in_production` |
| `ollama_webui_enable_signup` | `bool` | Allow new users to register accounts in Open WebUI. | `false` |
| **n8n Automation Configuration** | | | |
| `ollama_n8n_host` | `str` | Hostname used by n8n when generating application URLs. | `""` |
| `ollama_n8n_protocol` | `str` | Protocol used by n8n: `http`, `https` | `http` |
| `ollama_n8n_listen_address` | `str` | Network address on which n8n listens. | `0.0.0.0` |
| `ollama_n8n_secure_cookie` | `bool` | Require secure cookies for n8n authentication. Enable when using HTTPS. | `false` |
| `ollama_n8n_timezone` | `str` | Timezone used by n8n workflows and scheduled operations. | `America/Los_Angeles` |
| `ollama_n8n_proxy_hops` | `int` | Number of trusted reverse proxy hops in front of n8n. | `0` |
| `ollama_n8n_encryption_key` | `str` | Persistent encryption key used by n8n to protect stored credentials. Empty allows n8n to generate and persist its own key. | `""` |
| `ollama_n8n_editor_base_url` | `str` | Optional externally accessible n8n editor URL. | `""` |
| `ollama_n8n_webhook_url` | `str` | Optional externally accessible n8n webhook URL. | `""` |
| `ollama_n8n_mcp_base_url` | `str` | Optional externally accessible n8n MCP URL. | `""` |
| **Docker MCP Gateway Configuration** | | | |
| `ollama_mcp_gateway_transport` | `str` | Transport protocol used by Docker MCP Gateway. | `streaming` |
| `ollama_mcp_gateway_servers` | `list[str]` | Docker MCP catalog servers enabled by the gateway. | `["duckduckgo"]` |
| `ollama_mcp_gateway_auth_token` | `str` | Optional persistent authentication token for Docker MCP Gateway. Empty allows the gateway to generate its own token. | `""` |
| **SearXNG Search Configuration** | | | |
| `ollama_searxng_secret_key` | `str` | Secret key used by SearXNG for application security. | `change_this_to_a_secure_random_string_in_production` |
| `ollama_searxng_instance_name` | `str` | Display name assigned to the SearXNG instance. | `SearXNG` |
| `ollama_searxng_safe_search` | `int` | Safe search level: `0` (off), `1` (moderate), `2` (strict). | `1` |
| `ollama_searxng_limiter` | `bool` | Enable SearXNG request rate limiting. | `true` |
| `ollama_searxng_image_proxy` | `bool` | Enable image proxying through SearXNG. | `true` |
| `ollama_searxng_valkey_url` | `str` | Valkey connection URL used by SearXNG. | `valkey://searxng-valkey:6379/0` |
| **Open WebUI Web Search Integration** | | | |
| `ollama_webui_enable_rag_web_search` | `bool` | Enable web search integration for Open WebUI RAG. | `true` |
| `ollama_webui_rag_web_search_engine` | `str` | Search provider used by Open WebUI RAG web search. | `duckduckgo` |
| `ollama_webui_searxng_query_url` | `str` | Internal SearXNG search endpoint used by Open WebUI. | `http://searxng:8080/search` |
| `ollama_webui_searxng_language` | `str` | Language preference passed to SearXNG for Open WebUI searches. | `all` |
| **Resource and Engine Controls** | | | |
| `ollama_enable_gpu` | `bool` | Enable NVIDIA GPU access for the Ollama backend. | `true` |
| `ollama_docker_runtime` | `str` | Container runtime used for NVIDIA GPU access. | `nvidia` |
| `ollama_gpu_device_ids` | `list[str]` | GPU device IDs exposed to the Ollama container. | `["all"]` |
| `ollama_gpu_capabilities` | `list[str]` | NVIDIA GPU capabilities requested by the Ollama container. | `["gpu", "compute", "utility"]` |
| **Post-Provisioning Model Preloading** | | | |
| `ollama_manage_models` | `bool` | Enable management of Ollama AI models. | `false` |
| `ollama_preload_models` | `list[str]` | Ollama models to download after the backend becomes available. Models already installed are skipped. | `["deepseek-r1:32b", "qwen2.5-coder:32b", "qwen2.5-coder:7b", "llama3.1:8b", "qwen2.5-coder:1.5b-base", "nomic-embed-text:latest"]` |

## Authors Notes

1. [docker-compose](https://github.com/mythrantic/ollama-docker)  

## Author Information

Maintained by **Jared Cook** as part of the core infrastructure and container management ecosystem.

<!--
## Authors Notes

### Helpful Links

1. [Setup Guide](https://timesketch.org/guides/admin/install/)

-->
