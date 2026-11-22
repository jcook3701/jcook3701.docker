# Headscale

[Headscale](https://github.com/juanfont/headscale) is an open-source, self-hosted implementation of the Tailscale coordination server. It manages node registration, tailnet address assignment, MagicDNS, and access policies, while Tailscale clients provide the encrypted mesh connections.

This Ansible role deploys Headscale using Docker Compose, with persistent SQLite storage and an Ansible-managed Headscale configuration file. The optional [Headplane](https://headplane.net/) dashboard adds browser-based administration.

The initial deployment does not automatically migrate clients from a Tailscale-hosted tailnet.

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

**Warning:** `teardown` removes the SQLite database, private keys, Headplane API key, session secret, and other deployment data under `/opt/headscale`. Back up this directory before purging it.

The lifecycle follows the existing `jcook3701.utils.container_engine` task pattern.

## Required Settings Before Client Registration

The example domains are placeholders. Override these before registering clients:

```yaml
headscale_server_url: "https://headscale.example.com"
headscale_dns_base_domain: "tailnet.example.com"
```

Use the public HTTPS control-server hostname as `headscale_server_url` and a different DNS domain as `headscale_dns_base_domain`. The control server should normally be accessible through an HTTPS reverse proxy on TCP 443. Headscale documents limitations with Cloudflare Tunnel and Cloudflare Proxy for the control endpoint's protocol upgrades.

If no reverse proxy is configured, the server may be healthy while Tailscale clients cannot reach its configured public URL.

## Optional Headplane Dashboard

Enable the dashboard using:

```yaml
headscale_manage_headplane: true
```

The role automatically completes these operations during the same Ansible run:

1. Configure and start Headscale.
2. Generate a Headscale API key, only when no stored key exists.
3. Store the API key with root-only permissions in the Headplane configuration directory.
4. Render the Compose stack with Headplane enabled and deploy the dashboard.

The Headplane container is never started before its API key file has been created. Rerunning the role does not regenerate the key or reset sessions. The key defaults to a 365-day expiry configured by `headscale_headplane_api_key_expiration`. This initial implementation does not automatically rotate existing expired keys; keep that limitation in mind for long-running installations.

The browser dashboard is available at `http://<server-hostname>:3001/admin`, provided the host name resolves and port 3001 is reachable. No host IP address is hardcoded in the role.

### Logging In

The role provisions the Headscale API key, and Headplane uses the stored key for server-side API operations. The browser still requires authentication. API-key browser login is a Headplane security requirement, not a server installation step; the Ansible role cannot securely skip it without an additional authentication provider.

The generated key is stored on the Docker host at:

```text
/opt/headscale/headplane/config/api_key
```

Treat this file as a secret. To read the key for a first-time browser login, use your usual authorized secret-handling process. Do not put it into a public Git repository, normal Ansible log, or an unencrypted playbook.

### HTTPS and Security

By default the dashboard is bound to host port 3001. Use a trusted LAN only during HTTP testing. Expose the dashboard through an authenticated HTTPS proxy before allowing access from untrusted networks. Set `headscale_headplane_cookie_secure: true` when HTTPS is active.

For Headscale and Headplane, the application config files and API key are root-only. The Headplane Compose service explicitly runs as UID/GID 0 to read them, while Docker socket access remains disabled. This is an intentional compatibility choice with the role's existing permissions.

Headplane's advanced settings editor is not enabled: it requires write access to Ansible-managed Headscale configuration and Docker integration. Changes to these settings should continue through Ansible.

## Role Variables

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `headscale_container_engine` | str | Container engine. Choices: `docker`, `podman`. | `docker` |
| `headscale_state` | str | Lifecycle state: `present`, `absent`, `teardown`. | `present` |
| `headscale_debug_mode` | boolean | Enable role diagnostics. | `false` |
| `headscale_image` | str | Headscale container image. | `docker.io/headscale/headscale:0.29.7` |
| `headscale_container_name` | str | Headscale container name. | `headscale` |
| `headscale_pull_policy` | str | Pull policy: `always`, `missing`, `never`. | `always` |
| `headscale_restart_policy` | str | Restart policy. | `unless-stopped` |
| `headscale_base_dir` | path | Deployment directory root. | `/opt/headscale` |
| `headscale_host_bind_ip` | str | Host binding for Headscale's control port. | `127.0.0.1` |
| `headscale_external_port` | int | Headscale host TCP port. | `8080` |
| `headscale_internal_port` | int | Headscale container TCP port. | `8080` |
| `headscale_metrics_enabled` | bool | Enable metrics listener. | `false` |
| `headscale_metrics_external_port` | int | Metrics host TCP port. | `9090` |
| `headscale_metrics_internal_port` | int | Metrics container TCP port. | `9090` |
| `headscale_server_url` | str | Headscale public HTTPS control URL. | `https://headscale.example.com` |
| `headscale_trusted_proxies` | list[str] | Reverse-proxy CIDRs. | `[]` |
| `headscale_log_level` | str | Log level. | `info` |
| `headscale_log_format` | str | `text`, `json`. | `text` |
| `headscale_prefix_v4` | str | Tailnet IPv4 address range. | `100.64.0.0/10` |
| `headscale_prefix_v6` | str | Tailnet IPv6 address range. | `fd7a:115c:a1e0::/48` |
| `headscale_prefix_allocation` | str | Address allocation: `sequential`, `random`. | `sequential` |
| `headscale_dns_magic_dns` | bool | Enable MagicDNS. | `true` |
| `headscale_dns_base_domain` | str | MagicDNS domain. | `tailnet.example.com` |
| `headscale_dns_override_local_dns` | bool | Push DNS resolver settings. | `true` |
| `headscale_dns_nameservers_global` | list[str] | Global DNS resolvers. | `["1.1.1.1", "1.0.0.1"]` |
| `headscale_dns_nameservers_split` | dict | Split DNS mappings. | `{}` |
| `headscale_dns_search_domains` | list[str] | DNS search domains. | `[]` |
| `headscale_dns_extra_records` | list[dict] | Extra DNS records. | `[]` |
| `headscale_derp_embedded_enabled` | bool | Enable embedded DERP. | `false` |
| `headscale_derp_urls` | list[str] | DERP map URLs. | `["https://controlplane.tailscale.com/derpmap/default"]` |
| `headscale_derp_auto_update_enabled` | bool | Update DERP maps. | `true` |
| `headscale_derp_update_frequency` | str | DERP update interval. | `3h` |
| `headscale_policy_mode` | str | Policy source: `file`, `database`. | `file` |
| `headscale_policy_path` | str | Optional policy file. | `""` |
| `headscale_taildrop_enabled` | bool | Enable Taildrop. | `true` |
| `headscale_logtail_enabled` | bool | Enable logtail telemetry. | `false` |
| `headscale_extra_environment` | dict | Extra environment variables. | `{}` |
| `headscale_manage_headplane` | bool | Manage the optional Headplane dashboard. | `false` |
| `headscale_headplane_image` | str | Headplane image. | `ghcr.io/tale/headplane:0.8.1` |
| `headscale_headplane_container_name` | str | Headplane container name. | `headplane` |
| `headscale_headplane_host_bind_ip` | str | Dashboard host bind IP. | `0.0.0.0` |
| `headscale_headplane_external_port` | int | Dashboard host TCP port. | `3001` |
| `headscale_headplane_internal_port` | int | Dashboard container TCP port. | `3000` |
| `headscale_headplane_base_url` | str | Dashboard base URL; empty derives the host FQDN and port. | `""` |
| `headscale_headplane_cookie_secure` | bool | Require secure browser cookies. | `false` |
| `headscale_headplane_api_key_expiration` | str | Duration of initially provisioned API key. | `365d` |
| `headscale_headplane_kubernetes_pod_name` | str | Kubernetes pod name required by Headplane, even when Kubernetes integration is disabled. | `headscale` |
| `headscale_manage_client_preauth_key` | bool | Generate and store a client registration key when absent. | `false` |
| `headscale_client_preauth_user` | str | Headscale user owning enrolled clients; created if absent. | `homelab` |
| `headscale_client_preauth_key_reusable` | bool | Allow the same key to enroll multiple devices. | `true` |
| `headscale_client_preauth_key_expiration` | str | Lifetime of newly generated enrollment keys. | `720h` |
| `headscale_client_preauth_key_replace` | bool | Replace the saved key and expire its previous recorded ID. | `false` |

## Persistent Storage

```text
/opt/headscale/
├── compose.yml
├── config/
│   └── config.yaml
├── lib/
│   ├── db.sqlite
│   └── noise_private.key
├── backups/
└── headplane/
    ├── config/
    │   ├── config.yaml
    │   ├── cookie_secret
    │   └── api_key
    └── data/
```

The Headscale config mount is read-only and `/var/lib/headscale` holds the SQLite database and keys. Headplane uses its own persistent directory, and reads Headscale's config read-only. If the policy file is managed externally, create and mount it separately.

## Container Management

Validate the stack:

```shell
sudo docker compose -f /opt/headscale/compose.yml config -q
sudo docker compose -f /opt/headscale/compose.yml ps
```

Check Headplane errors if it does not start:

```shell
sudo docker compose -f /opt/headscale/compose.yml logs --tail 100 headplane
```

Check Headscale configuration and health:

```shell
sudo docker compose -f /opt/headscale/compose.yml exec headscale headscale configtest
```

Create the first Headscale user before registering clients:

```shell
sudo docker compose -f /opt/headscale/compose.yml exec headscale headscale users create homelab
```

Register a Tailscale client against the configured public control URL:

```shell
tailscale up --login-server https://headscale.example.com
```

This does not import previous registrations from Tailscale's hosted service.

## Helpful Links

1. [Headscale GitHub](https://github.com/juanfont/headscale)
2. [Headscale Documentation](https://headscale.net/stable/)
3. [Headscale Container Setup](https://headscale.net/0.29.7/setup/install/container/)
4. [Headscale Reverse Proxy](https://headscale.net/stable/ref/integration/reverse-proxy/)
5. [Headplane GitHub](https://github.com/tale/headplane)
6. [Headplane Docker Installation](https://headplane.net/install/docker)
7. [Headplane Configuration](https://headplane.net/configuration/)

## Author Information

Maintained by **Jared W. Cook** as part of the core infrastructure and container management ecosystem.
