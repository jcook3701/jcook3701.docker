# Nginx

[Nginx](https://nginx.org/) is a web server and reverse proxy. This role deploys
one Nginx container for independently managed Docker applications, with
configurable HTTP/HTTPS listeners, virtual hosts, and optional UniFi inform traffic.

Applications opt in to proxy routing by joining the shared Docker network and
being explicitly enabled under `nginx_proxy_sites`. **No backend routes or UniFi
inform forwarding are enabled by default.**

## Role Variables

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| **Runtime Orchestration Engine and Service State** | | | |
| `nginx_container_engine` | `str` | Container engine used by the shared lifecycle role. Choices: `docker`. | `docker` |
| `nginx_state` | `str` | Desired lifecycle state. Choices: `present`, `absent`, `teardown`. | `present` |
| `nginx_debug_mode` | `bool` | Enable role debug output. | `false` |
| **Service Container Image and Identity** | | | |
| `nginx_image` | `str` | Official Nginx container image. | `docker.io/library/nginx:1.30.7-alpine3.24` |
| `nginx_container_name` | `str` | Nginx service container name. | `nginx` |
| `nginx_pull_policy` | `str` | Docker Compose image pull policy. Choices: `always`, `missing`, `never`. | `missing` |
| `nginx_pull_images` | `bool` | Enable image pulls during deployment. | `false` |
| `nginx_restart_policy` | `str` | Docker Compose restart policy. Choices: `no`, `always`, `on-failure`, `unless-stopped`. | `unless-stopped` |
| **Infrastructure Storage and Path Routing** | | | |
| `nginx_base_dir` | `path` | Root directory for the Compose deployment and configuration. | `/opt/nginx` |
| **Networking Configuration** | | | |
| `nginx_host_bind_ip` | `str` | Host address on which Nginx publishes its listeners. | `0.0.0.0` |
| `nginx_http_external_port` | `int` | Host HTTP listener port. | `8080` |
| `nginx_http_internal_port` | `int` | Container HTTP listener port. | `8080` |
| `nginx_https_external_port` | `int` | Host HTTPS listener port. | `8443` |
| `nginx_https_internal_port` | `int` | Container HTTPS listener port. | `8443` |
| `nginx_proxy_network_name` | `str` | Shared external Docker bridge network for proxied services. | `jcook3701_proxy` |
| **TLS Configuration** | | | |
| `nginx_tls_bootstrap_self_signed` | `bool` | Generate a bootstrap self-signed certificate when absent. | `true` |
| `nginx_tls_bootstrap_days` | `int` | Validity in days for newly generated bootstrap certificates. | `365` |
| `nginx_tls_bootstrap_subject_alt_names` | `list[str]` | Optional DNS: and IP: entries for a new bootstrap certificate. | `[]` |
| **Reverse Proxy Routing** | | | |
| `nginx_proxy_sites` | `dict` | Mapping of explicitly enabled virtual hosts to upstream targets. | `{}` |
| `nginx_unifi_inform_enabled` | `bool` | Enable forwarding of UniFi device /inform requests. | `false` |
| `nginx_unifi_inform_upstream_host` | `str` | Docker DNS host of the UniFi inform endpoint. | `unifi-network` |
| `nginx_unifi_inform_upstream_port` | `int` | Internal TCP port of the UniFi inform endpoint. | `8080` |
| **Proxy Connection Handling** | | | |
| `nginx_client_max_body_size` | `str` | Maximum permitted client request body size. | `100m` |
| `nginx_proxy_connect_timeout` | `str` | Timeout while connecting to backend services. | `10s` |
| `nginx_proxy_read_timeout` | `str` | Timeout while reading from backend services. | `3600s` |
| `nginx_proxy_send_timeout` | `str` | Timeout while sending requests to backend services. | `3600s` |

## Installation

Use the same role lifecycle convention as other `jcook3701.docker` roles:

```yaml
---
- name: "Deploy the shared Nginx reverse proxy"
  hosts: "proxy_hosts"
  roles:
    - role: "jcook3701.docker.nginx"
      vars:
        nginx_state: "present"
```

The role creates `/opt/nginx`, renders `config/nginx.conf` and `compose.yml`,
creates the `jcook3701_proxy` Docker bridge network, and uses
`jcook3701.utils.container_engine` to deploy the Nginx Compose service.

The default ports are **HTTP 8080** and **HTTPS 8443**, not 80 and 443.
The role does not install or configure a host-level Nginx service.
OpenSSL must be installed on the managed host for bootstrap certificate generation.

### HTTPS Certificates

By default, Ansible generates a **self-signed bootstrap certificate** in
`/opt/nginx/certs/` if the certificate and key do not already exist. This lets
both listeners start without requiring an external certificate service.
Browsers will not trust this certificate. Before exposing services to users,
replace `/opt/nginx/certs/server.crt` and `/opt/nginx/certs/server.key` with a
matching trusted certificate and private key, then set:

```yaml
nginx_tls_bootstrap_self_signed: false
```

Make the private key readable by root only. The Nginx container mounts the
certificate directory read-only. Certificate renewal is not managed by this
role. Restart/recreate the proxy after replacing certificate files.

## Configuring Proxy Routes

Routes are **opt-in**. Use a dictionary keyed by an administrative route name:

```yaml
nginx_proxy_sites:
  open_webui:
    enabled: true
    server_name: "ai.example.com"
    upstream_host: "ollama-webui"
    upstream_port: 8080
    upstream_scheme: "http"
    websocket: true

  n8n:
    enabled: false
    server_name: "n8n.example.com"
    upstream_host: "ollama-n8n"
    upstream_port: 5678
    upstream_scheme: "http"
    websocket: true

  unifi:
    enabled: false
    server_name: "unifi.example.com"
    upstream_host: "unifi-network"
    upstream_port: 8443
    upstream_scheme: "https"
    proxy_ssl_verify: false
```

- Enabled routes receive an HTTPS virtual host on port 8443 and an HTTP-to-HTTPS
  redirect on 8080. Disabled routes are omitted from the generated configuration.
- Route targets must be reachable by Docker DNS over the shared proxy network.
- `websocket` enables Upgrade and Connection forwarding for applications needing
  WebSocket connections.
- `allowed_clients` optionally restricts HTTPS requests to a list of IP
  addresses or CIDRs. Omit the option to use Nginx's default access policy.
- Set `proxy_buffering: false` for routes that should deliver streamed responses
  as the backend sends them.
- `proxy_ssl_verify: false` is useful for self-signed internal HTTPS backends;
  it disables verification of that backend's certificate. Avoid disabling
  verification for untrusted upstream networks.
- Nginx resolves backend names dynamically; a temporarily absent backend does
  not prevent the Nginx container from starting, but requests may return 502.

### Attaching Other Docker Applications

Each application remains owned by its **own Ansible role and Compose project**.
Connect just the applications you intend to proxy to the externally created
network, while preserving their existing application-specific networks:

```yaml
services:
  example-app:
    networks:
      - "default"
      - "proxy"

networks:
  proxy:
    external: true
    name: "jcook3701_proxy"
```

This is an example of the additional network connection needed in an
application's Compose template; it is **not** a replacement for the application's
existing network or its own Ansible role.

If an application's host port conflicts with Nginx port 8080 or 8443, change the
application's published host port or remove that publishing after confirming
its Docker-network connection. Internal application ports do not need to change.

### UniFi Device Inform Traffic

Device communication over `/inform` is independent of the UniFi management UI.
It is **disabled by default** until UniFi is connected to the shared proxy network
and its original 8080 host-port publishing has been released:

```yaml
nginx_unifi_inform_enabled: true
nginx_unifi_inform_upstream_host: "unifi-network"
nginx_unifi_inform_upstream_port: 8080
```

The default HTTP listener on Nginx's host port 8080 forwards `/inform` requests
when enabled. HTTPS management can be exposed as a separate virtual host using
`nginx_proxy_sites`. Keep UniFi's other required TCP/UDP ports configured in
its own role. Do not change existing device inform addresses until the replacement
route is reachable and tested. This Nginx role does not reconfigure UniFi devices.

## Persistent Storage

```text
/opt/nginx/
├── compose.yml
├── config/
│   └── nginx.conf
└── certs/
    ├── server.crt
    └── server.key
```

`certs/server.key` uses root-only file permissions. On teardown, the entire
role-managed directory, including locally generated certificates, is deleted.
The shared proxy network is left in place because other Compose projects may
still be attached to it.

## Container Management

Validate the rendered Compose model:

```shell
docker compose -f /opt/nginx/compose.yml config --quiet
```

Inspect the service:

```shell
docker compose -f /opt/nginx/compose.yml ps
docker compose -f /opt/nginx/compose.yml logs --tail 100 nginx
```

Check the Nginx configuration inside the container:

```shell
docker compose -f /opt/nginx/compose.yml exec nginx nginx -t
```

Test the HTTP health endpoint:

```shell
curl -fsS http://127.0.0.1:8080/nginx-health
```

The default TLS virtual host rejects unmatched hostnames. Add an enabled
virtual host and matching DNS before expecting a response on HTTPS 8443.

To stop Nginx while keeping the configuration and certificate files:

```yaml
nginx_state: "absent"
```

To remove the container and **delete `/opt/nginx`** (including certificates):

```yaml
nginx_state: "teardown"
```

## Authors Notes

### Integration

This role follows the same Compose-based directory structure and
`present`/`absent`/`teardown` lifecycle as other `jcook3701.docker` roles. It
uses `jcook3701.utils.container_engine` for Compose lifecycle operations.

The role does not automatically modify or proxy any other application's Compose
configuration, and never enables routes merely because a backend is installed.

### Helpful Links

1. [Nginx documentation](https://nginx.org/en/docs/)
2. [Docker Compose networking](https://docs.docker.com/compose/how-tos/networking/)
3. [Docker Official Nginx image](https://hub.docker.com/_/nginx)

## Author Information

Maintained as part of the `jcook3701.docker` Ansible collection.
