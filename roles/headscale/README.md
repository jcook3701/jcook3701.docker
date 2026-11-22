
# Headscale

[Headscale](https://github.com/juanfont/headscale) is an open-source, self-hosted implementation of the Tailscale coordination server. It manages node registration, tailnet address assignment, MagicDNS, and access policies, while Tailscale clients provide the encrypted mesh connections.

This Ansible role deploys Headscale using Docker Compose, with persistent SQLite storage and an Ansible-managed Headscale configuration file. An optional [Headplane](https://headplane.net/) web dashboard provides browser-based administration.

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

**Warning:** `teardown` removes the SQLite database, keys, configuration, and any Headplane data under `/opt/headscale`. Back up this directory before purging it.

The lifecycle operations follow the existing `jcook3701.utils.container_engine` integration used elsewhere in the collection.

## Required Settings Before Client Registration

The defaults are intended for an initial host-local deployment. The example domains are placeholders. Override them before registering clients:

```yaml
headscale_server_url: "https://headscale.example.com"
headscale_dns_base_domain: "tailnet.example.com"
```

Use your actual public HTTPS control-server hostname as `headscale_server_url` and a **different** DNS domain as `headscale_dns_base_domain`.

The control server should normally be available through a trusted HTTPS reverse proxy on TCP 443.

Headscale documents that Cloudflare Tunnel and Cloudflare Proxy do not support its required POST-based control-protocol upgrade.

Nginx or Apache can forward requests to Headscale. For a proxy running in another Docker container, use appropriate network access rather than assuming the container can access the host's loopback address.

A healthy container does not prove that the public control-server URL is reachable.

## Optional Headplane Dashboard

Headplane provides a browser-based administration interface for Headscale.

Enable it with:

```yaml
headscale_manage_headplane: true
```

The role adds the Headplane container to the existing Headscale Compose stack.

Headplane connects to Headscale internally using the Docker network. It does not require a hardcoded Docker host IP address.

### Dashboard Networking

The default Headplane port configuration is:

```yaml
headscale_headplane_host_bind_ip: "0.0.0.0"
headscale_headplane_external_port: 3001
headscale_headplane_internal_port: 3000
```

This avoids conflicts with Headscale and typical reverse-proxy ports.

The role automatically derives the initial Headplane browser URL from the Ansible host FQDN and external port.

Override `headscale_headplane_base_url` when a different public URL is required.

The dashboard is available at:

```text
http://<server-hostname>:3001/admin
```

**Security:** Direct HTTP access transmits browser credentials without TLS. Limit access to a trusted network and configure HTTPS before using Headplane over untrusted connections.

### First Login

Headplane uses a Headscale API key for authentication.

Generate a key from the running Headscale container:

```shell
sudo docker compose -f /opt/headscale/compose.yml \
  exec headscale headscale apikeys create --expiration 90d
```

Treat the returned API key as a secret.

Open the Headplane dashboard and authenticate with the generated key.

The role automatically creates a persistent 32-character session secret for Headplane.

### Initial Integration Scope

The optional Headplane service provides API-backed browser administration.

The initial configuration does not mount the Docker socket or grant Headplane write access to the Ansible-managed Headscale configuration.

Consequently, advanced Headplane features that require Docker integration, including editing certain network settings from the UI, are not enabled.

Configuration changes should continue to be managed through Ansible.

Disabling `headscale_manage_headplane` removes the role-managed dashboard container without deleting its persistent data.

### HTTPS Reverse Proxy

When using an HTTPS reverse proxy, configure an appropriate browser-facing URL:

```yaml
headscale_headplane_base_url: "https://headplane.example.com"
headscale_headplane_cookie_secure: true
```

The reverse proxy must forward to the Headplane HTTP service and preserve the `/admin` path.

TLS certificates are managed independently of this Headscale role.

## Role Variables

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `headscale_container_engine` | str | Container engine used by the shared lifecycle role. Choices: `docker`, `podman`. | `docker` |
| `headscale_state` | str | Desired lifecycle: `present`, `absent`, `teardown`. | `present` |
| `headscale_debug_mode` | boolean | Enable optional role diagnostics. | `false` |
| `headscale_image` | str | Version-pinned Headscale container image. | `docker.io/headscale/headscale:0.29.7` |
| `headscale_container_name` | str | Headscale container name. | `headscale` |
| `headscale_pull_policy` | str | Image pull policy. Choices: `always`, `missing`, `never`. | `always` |
| `headscale_restart_policy` | str | Container restart policy. | `unless-stopped` |
| `headscale_base_dir` | path | Deployment, data, and configuration directory. | `/opt/headscale` |
| `headscale_host_bind_ip` | str | Host interface for the Headscale control port. | `127.0.0.1` |
| `headscale_external_port` | integer | Headscale host TCP port. | `8080` |
| `headscale_internal_port` | integer | Headscale container TCP port. | `8080` |
| `headscale_metrics_enabled` | boolean | Enable the optional metrics listener. | `false` |
| `headscale_metrics_external_port` | integer | Metrics host TCP port. | `9090` |
| `headscale_metrics_internal_port` | integer | Metrics container TCP port. | `9090` |
| `headscale_server_url` | str | Public HTTPS Headscale control-server URL. | `https://headscale.example.com` |
| `headscale_trusted_proxies` | list[string] | Trusted reverse-proxy CIDRs. | `[]` |
| `headscale_log_level` | str | Headscale logging level. | `info` |
| `headscale_log_format` | str | Logging format. Choices: `text`, `json`. | `text` |
| `headscale_prefix_v4` | str | Tailnet IPv4 allocation prefix. | `100.64.0.0/10` |
| `headscale_prefix_v6` | str | Tailnet IPv6 allocation prefix. | `fd7a:115c:a1e0::/48` |
| `headscale_prefix_allocation` | str | IP allocation. Choices: `sequential`, `random`. | `sequential` |
| `headscale_dns_magic_dns` | boolean | Enable MagicDNS. | `true` |
| `headscale_dns_base_domain` | str | MagicDNS namespace. | `tailnet.example.com` |
| `headscale_dns_override_local_dns` | boolean | Push DNS resolvers to clients. | `true` |
| `headscale_dns_nameservers_global` | list[string] | Global DNS resolvers. | `["1.1.1.1", "1.0.0.1"]` |
| `headscale_dns_nameservers_split` | dictionary | Split DNS mappings. | `{}` |
| `headscale_dns_search_domains` | list[string] | DNS search domains. | `[]` |
| `headscale_dns_extra_records` | list[dictionary] | Additional DNS records. | `[]` |
| `headscale_derp_embedded_enabled` | boolean | Enable embedded DERP. | `false` |
| `headscale_derp_urls` | list[string] | DERP map URLs. | `["https://controlplane.tailscale.com/derpmap/default"]` |
| `headscale_derp_auto_update_enabled` | boolean | Automatically update DERP maps. | `true` |
| `headscale_derp_update_frequency` | str | DERP update interval. | `3h` |
| `headscale_policy_mode` | str | Access policy source. Choices: `file`, `database`. | `file` |
| `headscale_policy_path` | str | Optional policy path. | `""` |
| `headscale_taildrop_enabled` | boolean | Enable Taildrop. | `true` |
| `headscale_logtail_enabled` | boolean | Enable logtail. | `false` |
| `headscale_extra_environment` | dictionary | Additional Headscale environment variables. | `{}` |
| **Optional Headplane Web Dashboard** | | | |
| `headscale_manage_headplane` | boolean | Manage the optional Headplane dashboard. | `false` |
| `headscale_headplane_image` | str | Headplane container image. | `ghcr.io/tale/headplane:0.8.1` |
| `headscale_headplane_container_name` | str | Headplane container name. | `headplane` |
| `headscale_headplane_host_bind_ip` | str | Dashboard host bind IP. | `0.0.0.0` |
| `headscale_headplane_external_port` | integer | Dashboard host TCP port. | `3001` |
| `headscale_headplane_internal_port` | integer | Dashboard container TCP port. | `3000` |
| `headscale_headplane_base_url` | str | Browser-facing base URL; empty derives FQDN and port. | `""` |
| `headscale_headplane_cookie_secure` | boolean | Require HTTPS for session cookies. | `false` |

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
    │   └── cookie_secret
    └── data/
```

The `config` mount is read-only inside Headscale, while `/var/lib/headscale` stores the database and generated private keys.

Headplane stores its own configuration, persistent application data, and session secret separately.

The Headplane session secret is created only when absent, so repeated deployments preserve existing browser sessions.

The initial Headplane integration mounts the Headscale configuration read-only.

Enabling the embedded DERP server additionally requires planning for UDP STUN and HTTPS access.

If `headscale_policy_mode` is `file` and an external policy path is configured, that file must be created and mounted separately.

## Container Management

Validate the generated Docker Compose file:

```shell
sudo docker compose -f /opt/headscale/compose.yml config -q
```

Check running containers:

```shell
sudo docker compose -f /opt/headscale/compose.yml ps
```

Inspect logs:

```shell
sudo docker compose -f /opt/headscale/compose.yml logs --tail 100
```

Inspect Headplane logs when enabled:

```shell
sudo docker compose -f /opt/headscale/compose.yml logs --tail 100 headplane
```

Validate the Headscale configuration:

```shell
sudo docker compose -f /opt/headscale/compose.yml exec headscale headscale configtest
```

Create your first Headscale user:

```shell
sudo docker compose -f /opt/headscale/compose.yml exec headscale headscale users create homelab
```

List Headscale users:

```shell
sudo docker compose -f /opt/headscale/compose.yml exec headscale headscale users list
```

Register a client after configuring HTTPS and DNS:

```shell
tailscale up --login-server https://headscale.example.com
```

Using a different login server does not import existing client registrations from Tailscale's hosted service.

## Helpful Links

1. [Headscale GitHub](https://github.com/juanfont/headscale)
2. [Headscale Documentation](https://headscale.net/stable/)
3. [Headscale Container Setup](https://headscale.net/0.29.7/setup/install/container/)
4. [Headscale Configuration Example, v0.29.7](https://github.com/juanfont/headscale/blob/v0.29.7/config-example.yaml)
5. [Headscale Reverse Proxy](https://headscale.net/stable/ref/integration/reverse-proxy/)
6. [Headplane GitHub](https://github.com/tale/headplane)
7. [Headplane Docker Installation](https://headplane.net/install/docker)
8. [Headplane Configuration](https://headplane.net/configuration/)

## Author Information

Maintained by **Jared W. Cook** as part of the core infrastructure and container management ecosystem.
