# Desktop Commander Docker role

`jcook3701.docker.desktop_commander` deploys the Desktop Commander **remote device agent** in a restricted Docker container using the collection's shared `jcook3701.utils.container_engine` lifecycle role.

This is a **host filesystem isolation** deployment, not a general-purpose administrative access agent. The one host bind mount is `/home/chat-gpt`; the container also has its own private `/tmp`. Container system files in its read-only image are not host files.

## Critical safety requirements

- Run on a host with a dedicated `chat-gpt` account whose `/home/chat-gpt` directory is owned by that account and is mode `0700`.
- Stop and disable **all previous unsandboxed Remote Desktop Commander agents** before deployment. A host-running agent is not confined by this role.
- Do **not** bind-mount `/var/run/docker.sock`, `/`, `/home/jcook`, `/backups`, `/storage`, or privileged host devices into the container.
- No nested mounts are allowed beneath `/home/chat-gpt`. The role checks the existing mount table before installation; this is not a substitute for a separate long-term mount policy.
- The host's `/home/jcook` permissions and the explicit `chat-gpt` ACL denials for `/backups` and `/storage` remain valuable defense in depth.
- The default Docker network **allows outbound connections**, potentially to private LAN services. This role does not implement an outbound firewall or prevent data exfiltration over the network. Apply explicit host/network egress controls if required.
- Container isolation is not a security guarantee against kernel or container runtime vulnerabilities. Consider rootless Docker or Docker user namespace remapping as additional hardening after testing compatibility.

## Requirements

- Docker Engine and Docker Compose v2 available on the target host.
- `jcook3701.utils.container_engine` role and `community.docker` collection installed.
- A dedicated `chat-gpt` account, `/home/chat-gpt` owned by it, mode `0700`.
- Network access to npm for the pinned package on first startup, and to Desktop Commander's cloud services for pairing and connections.

The role intentionally does **not** install or reconfigure Docker and does not create host accounts. This avoids unexpected host-level changes during a security-sensitive deployment.

## Defaults and lifecycle

| Variable | Type | Default | Meaning |
| :--- | :--- | :--- | :--- |
| `desktop_commander_container_engine` | string | `docker` | Docker-only runtime |
| `desktop_commander_state` | string | `present` | `present`, `absent`, or `teardown` |
| `desktop_commander_debug_mode` | bool | `false` | Optional non-sensitive diagnostics |
| `desktop_commander_image` | string | `docker.io/library/node:24-bookworm-slim` | Node runtime image |
| `desktop_commander_package_version` | string | `0.3.4` | Pinned npm remote agent version |
| `desktop_commander_container_name` | string | `desktop-commander` | Docker container name |
| `desktop_commander_pull_policy` | string | `missing` | Image pull policy |
| `desktop_commander_pull_images` | bool | `false` | Force pulls through shared role |
| `desktop_commander_restart_policy` | string | `unless-stopped` | Container restart policy |
| `desktop_commander_base_dir` | path | `/opt/desktop_commander` | Root-owned host deployment configuration; not mounted |
| `desktop_commander_system_user` | string | `chat-gpt` | Required dedicated Linux account |
| `desktop_commander_host_home` | path | `/home/chat-gpt` | The **only** host bind mount |
| `desktop_commander_tmpfs_size` | string | `256m` | Private `/tmp` size |
| `desktop_commander_memory_limit` | string | `1g` | Memory cap |
| `desktop_commander_pids_limit` | integer | `128` | Process cap |

The account, home path, Docker engine, and base directory are intentionally checked against fixed safe values. If overridden, installation fails rather than weakening the security boundary.

- `present`: validates account/path/mount safety, writes Compose configuration to `/opt/desktop_commander`, and deploys the container.
- `absent`: stops/removes only the Compose stack; preserves `/opt/desktop_commander` and `/home/chat-gpt`.
- `teardown`: removes the stack and the `/opt/desktop_commander` deployment configuration; **never** deletes `/home/chat-gpt` or its saved device credentials. Does not delete shared Docker images.

## Deploy using a playbook

```yaml
---
- name: "Install isolated Remote Desktop Commander"
  hosts: "second-chance"
  become: true
  roles:
    - role: "jcook3701.docker.desktop_commander"
      vars:
        desktop_commander_state: "present"
```

## First-time pairing

The remote agent prints a verification URL and code during its first startup. View logs locally:

```bash
sudo docker compose -f /opt/desktop_commander/compose.yml logs -f desktop_commander
```

Open the printed verification URL on a trusted browser, verify the code, and authorize the device. Its persistent credential file is under `/home/chat-gpt/.desktop-commander-device/device.json`; do not commit or share that file. The OAuth flow does not need host port publication.

## Verify containment before connecting ChatGPT

```bash
# Confirm only one host bind mount exists.
sudo docker inspect desktop-commander --format '{{json .Mounts}}'

# Confirm the process runs as a non-root numeric user.
sudo docker exec desktop-commander id

# These host directory paths must not exist in the container.
sudo docker exec desktop-commander sh -c 'for p in /home/jcook /backups /storage; do if test -e "$p"; then echo "EXPOSED: $p"; else echo "HIDDEN: $p"; fi; done'

# Confirm private container /tmp is writable.
sudo docker exec desktop-commander sh -c 'test -w /tmp && echo "TMP OK"'
```

Also check the host has no separate unsandboxed agent and that the container did not receive unexpected mounts. Be careful with `docker exec` into the running container: it gives the command all of the container's existing permissions and tools.

**Limitations:** A privileged Docker administrator or a Docker runtime compromise can bypass this boundary. The Docker bridge permits outbound connections unless blocked separately. The role does not prevent a host process running as `chat-gpt` outside Docker from accessing other host files that OS permissions allow.
