# SearXNG

Deploy SearXNG through the collection's shared container engine.
Docker Engine, Compose v2, `community.docker`, and `jcook3701.utils` are required.

The default web and JSON endpoint is `http://127.0.0.1:8081`. The dedicated Valkey service
shares the Compose project's private network. Ansible owns the generated search configuration.
For a migration, retain the existing secret and copy any desired cache data while both stacks are stopped.

## Lifecycle

- `present` configures and starts the stack.
- `absent` removes the Compose stack, preserving its data and configuration.
- `teardown` also removes the Compose file. Image and data removal require explicit flags.

The data removal flag removes the entire role deployment directory. Keep this directory
dedicated to this role. Data stored outside it is retained.

## Role Variables

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `searxng_container_engine` | str | Container engine. Choices: `docker`. | `docker` |
| `searxng_state` | str | Deployment lifecycle. Choices: `present`, `absent`, `teardown`. | `present` |
| `searxng_teardown_remove_data` | bool | Permanently remove role files and data within the deployment directory. | `false` |
| `searxng_teardown_remove_images` | bool | Remove the Compose service images during teardown. | `false` |
| `searxng_image` | str | Container image reference. | `docker.io/searxng/searxng:latest` |
| `searxng_container_name` | str | Container name. | `searxng` |
| `searxng_pull_policy` | str | Compose pull policy. Choices: `missing`, `always`, `never`. | `missing` |
| `searxng_pull_images` | bool | Ask the shared container engine to force image pulls. | `false` |
| `searxng_restart_policy` | str | Container restart policy. Choices: `no`, `always`, `on-failure`, `unless-stopped`. | `unless-stopped` |
| `searxng_base_dir` | path | Deployment directory for Compose files and managed state. | `/opt/searxng` |
| `searxng_bind_ip` | str | Published host address. | `127.0.0.1` |
| `searxng_external_port` | int | Published host port. | `8081` |
| `searxng_internal_port` | int | Service port inside the container. | `8080` |
| `searxng_shared_network` | str | Optional existing Docker network for private service connections. | `""` |
| `searxng_valkey_image` | str | Dedicated Valkey image. | `docker.io/valkey/valkey:9-alpine` |
| `searxng_instance_name` | str | Instance name shown in the UI. | `SearXNG` |
| `searxng_secret_key` | str | Instance secret. Empty generates a persistent secret. | `""` |
| `searxng_safe_search` | int | Safe search level. Choices: `0`, `1`, `2`. | `1` |
| `searxng_limiter` | bool | Enable the limiter when behind a trusted proxy. | `false` |
| `searxng_limiter_pass_ips` | list | Addresses or networks accepted by the limiter. | `[]` |
| `searxng_image_proxy` | bool | Proxy image results through SearXNG. | `true` |

## Example

```yaml
---
- name: Deploy SearXNG
  hosts: "searxng_hosts"
  become: true
  roles:
    - role: "jcook3701.docker.searxng"
```

## Author Information

Maintained by **Jared W. Cook**. Licensed under AGPL-3.0-or-later.
