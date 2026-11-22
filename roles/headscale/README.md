# Headscale

[Headscale](https://github.com/juanfont/headscale) is an open-source, self-hosted implementation of the Tailscale coordination server. It manages node registration, tailnet address assignment, MagicDNS, and access policies, while Tailscale clients provide the encrypted mesh connections.

This Ansible role deploys Headscale using Docker Compose, with persistent SQLite storage and an Ansible-managed Headscale configuration file. The initial deployment does not automatically migrate clients from a Tailscale-hosted tailnet.

## Installation

Deploy **Headscale**:

```shell
ansible-playbook jcook3701.docker.headscale.yml -K
```

Stop and remove the containers while preserving persistent data:

```shell
ansible-playbook jcook3701.docker.headscale.yml -K -e "headscale_state=absent"
```

Remove the containers and the entire persistent deployment directory:

```shell
ansible-playbook jcook3701.docker.headscale.yml -K -e "headscale_state=teardown"
```

**Warning:** `teardown` removes the SQLite database, keys, and configuration under `/opt/headscale`. Back up this directory before purging it. The three lifecycle operations assume the same `jcook3701.utils.container_engine` task pattern used in your Ollama role.

## Required Settings Before Client Registration

The defaults are deliberately safe for an initial host-local deployment, but the example domains are placeholders. Override these before registering any clients:

```yaml
headscale_server_url: "https://headscale.example.com"
headscale_dns_base_domain: "tailnet.example.com"
```

Use your actual public HTTPS control-server hostname as `headscale_server_url` and a **different** DNS domain as `headscale_dns_base_domain`. The control server should normally be available via an HTTPS reverse proxy on TCP 443. **Do not use Cloudflare Tunnel or Cloudflare Proxy for the Headscale control endpoint:** Headscale documents that these services do not support its required POST-based control-protocol upgrade. Nginx or Apache can proxy to `127.0.0.1:8080` on the Docker host. Keep `headscale_host_bind_ip: "127.0.0.1"` when the proxy runs on the same host; if the proxy is another container, adapt its network access instead of publishing the endpoint broadly. Configure WebSocket/HTTP upgrade handling according to the Headscale reverse-proxy documentation.

When a dedicated reverse proxy has not been configured, the container may become healthy but remote Tailscale clients **cannot reach** the placeholder URL. Do not treat a healthy container as proof of externally accessible control-plane connectivity.

## Role Variables

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `headscale_container_engine` | str | Container engine used by the shared lifecycle role. Choices: `docker`, `podman`. | `docker` |
| `headscale_state` | str | Desired lifecycle: present, absent, or teardown. Choices: `present`, `absent`, `teardown`. | `present` |
| `headscale_debug_mode` | boolean | Enable optional role diagnostics. | `false` |
| `headscale_image` | str | Version-pinned official Headscale container image. | `docker.io/headscale/headscale:0.29.7` |
| `headscale_container_name` | str | Name assigned to the Headscale container. | `headscale` |
| `headscale_pull_policy` | str | Docker Compose image pull policy. Choices: `always`, `missing`, `never`. | `always` |
| `headscale_restart_policy` | str | Docker Compose container restart policy. Choices: `no`, `always`, `on-failure`, `unless-stopped`. | `unless-stopped` |
| `headscale_base_dir` | path | Host root for the deployment, data, and configuration. | `/opt/headscale` |
| `headscale_host_bind_ip` | str | Host IP on which to publish the Headscale control port; localhost by default. | `127.0.0.1` |
| `headscale_external_port` | integer | Host TCP port mapped to the control API. | `8080` |
| `headscale_internal_port` | integer | Container TCP port on which Headscale listens. | `8080` |
| `headscale_metrics_enabled` | boolean | Enable metrics listener; published only on host loopback. | `false` |
| `headscale_metrics_external_port` | integer | Host loopback port mapped to optional metrics listener. | `9090` |
| `headscale_metrics_internal_port` | integer | Container port used by the optional metrics listener. | `9090` |
| `headscale_server_url` | str | Public HTTPS URL reachable by Tailscale clients; change placeholder before use. | `https://headscale.example.com` |
| `headscale_trusted_proxies` | list[string] | Trusted reverse-proxy CIDRs permitted to supply forwarded client IP headers. | `[]` |
| `headscale_log_level` | str | Headscale log level. Choices: `panic`, `fatal`, `error`, `warn`, `info`, `debug`, `trace`. | `info` |
| `headscale_log_format` | str | Headscale log output format. Choices: `text`, `json`. | `text` |
| `headscale_prefix_v4` | str | IPv4 prefix for allocating tailnet addresses; must be within 100.64.0.0/10. | `100.64.0.0/10` |
| `headscale_prefix_v6` | str | IPv6 prefix for allocating tailnet addresses; must be within fd7a:115c:a1e0::/48. | `fd7a:115c:a1e0::/48` |
| `headscale_prefix_allocation` | str | Tailnet IP allocation strategy. Choices: `sequential`, `random`. | `sequential` |
| `headscale_dns_magic_dns` | boolean | Enable MagicDNS hostnames for tailnet clients. | `true` |
| `headscale_dns_base_domain` | str | DNS domain for MagicDNS; distinct from the control-server hostname. | `tailnet.example.com` |
| `headscale_dns_override_local_dns` | boolean | Push configured DNS resolvers to tailnet nodes. | `true` |
| `headscale_dns_nameservers_global` | list[string] | Global DNS resolver addresses advertised to clients. | `["1.1.1.1", "1.0.0.1"]` |
| `headscale_dns_nameservers_split` | dictionary | Split DNS mapping of domains to resolver address lists. | `{}` |
| `headscale_dns_search_domains` | list[string] | Additional DNS search domains advertised to clients. | `[]` |
| `headscale_dns_extra_records` | list[dictionary] | Extra MagicDNS A or AAAA record definitions. | `[]` |
| `headscale_derp_embedded_enabled` | boolean | Enable the embedded DERP relay; requires additional HTTPS/STUN routing. | `false` |
| `headscale_derp_urls` | list[string] | Remote DERP map URLs distributed to clients. | `["https://controlplane.tailscale.com/derpmap/default"]` |
| `headscale_derp_auto_update_enabled` | boolean | Automatically refresh DERP maps. | `true` |
| `headscale_derp_update_frequency` | str | Frequency at which DERP maps are refreshed. | `3h` |
| `headscale_policy_mode` | str | Location of access policy: file or database. Choices: `file`, `database`. | `file` |
| `headscale_policy_path` | str | Absolute path in the container to an optional HuJSON policy file. | `""` |
| `headscale_taildrop_enabled` | boolean | Enable tailnet file sharing (Taildrop). | `true` |
| `headscale_logtail_enabled` | boolean | Allow forwarding client logtail telemetry to Tailscale. | `false` |
| `headscale_extra_environment` | dictionary | Additional environment variables for the Headscale container. | `{}` |

## Persistent Storage

```text
/opt/headscale/
├── compose.yml
├── config/
│   └── config.yaml
├── lib/
│   ├── db.sqlite             # Created by Headscale
│   └── noise_private.key     # Created by Headscale
└── backups/                 # Reserved for your backup workflow
```

The `config` mount is read-only within the container, and `/var/lib/headscale` holds the SQLite database and generated private keys. The container runs with a read-only root filesystem and a temporary Unix-socket directory. Enabling the embedded DERP server also publishes UDP/3478 for STUN; it additionally requires a publicly reachable HTTPS control endpoint and appropriate firewall/NAT forwarding.

If you enable `headscale_policy_mode: "file"` and point `headscale_policy_path` at a HuJSON ACL file, you must create and mount that policy file separately. By default, no custom ACL file is loaded, so define an access policy before enrolling clients that require traffic restrictions.

## Container Management

Validate Compose and start-up status:

```shell
sudo docker compose -f /opt/headscale/compose.yml config -q
sudo docker compose -f /opt/headscale/compose.yml ps
sudo docker compose -f /opt/headscale/compose.yml logs --tail 100 headscale
```

Validate the Headscale configuration:

```shell
sudo docker compose -f /opt/headscale/compose.yml exec headscale headscale configtest
```

Test the HTTP health endpoint on the Docker host:

```shell
curl -fsS http://127.0.0.1:8080/health
```

Create your first Headscale user after configuring HTTPS and DNS:

```shell
sudo docker compose -f /opt/headscale/compose.yml exec headscale headscale users create homelab
sudo docker compose -f /opt/headscale/compose.yml exec headscale headscale users list
```

On a client machine, register using its Headscale control URL:

```shell
tailscale up --login-server https://headscale.example.com
```

Follow the Headscale registration instructions to approve the node. **Using `tailscale up --login-server` changes the control server for that Tailscale client; it does not import existing registrations from Tailscale's hosted service.**

## Helpful Links

1. [Headscale GitHub](https://github.com/juanfont/headscale)
2. [Headscale Documentation](https://headscale.net/stable/)
3. [Headscale Container Setup](https://headscale.net/0.29.7/setup/install/container/)
4. [Headscale Configuration Example, v0.29.7](https://github.com/juanfont/headscale/blob/v0.29.7/config-example.yaml)
5. [Headscale Getting Started](https://headscale.net/stable/usage/getting-started/)
6. [Headscale Reverse Proxy](https://headscale.net/stable/ref/integration/reverse-proxy/)

## Author Information

Maintained by **Jared W. Cook** as part of the core infrastructure and container management ecosystem.
