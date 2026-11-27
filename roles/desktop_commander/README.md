# Desktop Commander Docker role

`jcook3701.docker.desktop_commander` deploys the Desktop Commander remote
device agent in a restricted Docker container using the collection's shared
`jcook3701.utils.container_engine` lifecycle role.

The role optionally builds a dedicated development image containing Git,
GitHub CLI, Python, and other development utilities.

This is a host filesystem isolation deployment, not a general-purpose
administrative access agent. The only host bind mount is `/home/chat-gpt`;
the container also has its own private `/tmp`.

## Critical safety requirements

- Run on a host with a dedicated `chat-gpt` account whose home directory is
  owned by that account and has mode `0700`.
- Stop and disable all previous unsandboxed Remote Desktop Commander agents
  before deployment.
- Do not bind-mount `/var/run/docker.sock`, `/`, personal home directories,
  backup directories, storage directories, or privileged host devices.
- No nested mounts are allowed beneath `/home/chat-gpt`.
- Preserve host filesystem permissions as an additional security boundary.
- The default Docker network permits outbound connections, potentially
  including private LAN services.
- Attach only explicitly trusted services to the optional shared network.
- Container isolation is not a guarantee against kernel or container runtime
  vulnerabilities.

The optional development image does not grant root access or Docker
administration privileges.

## Requirements

- Docker Engine and Docker Compose v2 on the target host.
- The `jcook3701.utils.container_engine` role.
- The `community.docker` collection.
- A dedicated `chat-gpt` account with `/home/chat-gpt` owned by that account
  and configured with mode `0700`.
- Network access to npm and Desktop Commander's remote services.
- Network access to Debian package repositories when building the optional
  development image.

The role does not install or reconfigure Docker or create host accounts.

## Development environment

Enable the optional development image using:

```yaml
desktop_commander_build_development_image: true
desktop_commander_development_image: "desktop-commander-development:local"
```

The image includes:

- Node.js, npm, and npx.
- Git and GitHub CLI.
- OpenSSH client.
- Python 3, pip, and virtual environment support.
- GCC, Make, and standard compilation utilities.
- curl, wget, jq, and ripgrep.
- rsync and archive utilities.

The image creates a non-root `chat-gpt` account matching the host account's
UID and GID. Conflicting account identifiers cause the build to fail.

The Desktop Commander package version remains explicitly configured through
`desktop_commander_package_version`.

The base image and Debian packages are not pinned to immutable digests or
individual package versions. Rebuilds remain operator-controlled.

Python applications, Ansible, and project-specific development dependencies
should be installed into virtual environments under `/home/chat-gpt`.

The container's root filesystem remains read-only.

The private `/tmp` mount remains non-executable. If a trusted development
operation requires executable temporary files, use a private temporary
directory beneath `/home/chat-gpt` for that operation.

## Shared service networking

The optional shared network allows Desktop Commander to communicate with
explicitly selected Docker services.

```yaml
desktop_commander_shared_network: "desktop_commander_ai"
```

When configured, the role creates an internal Docker bridge network while
preserving its normal outbound network.

Other services must explicitly join the same external Compose network.

For FreeLLMAPI:

```yaml
freellmapi_agent_network: "desktop_commander_ai"
```

Deploy Desktop Commander first so the external network exists before
deploying FreeLLMAPI.

The FreeLLMAPI endpoint is then available inside Desktop Commander at:

```text
http://freellmapi:3001/v1
```

This network is not an application-level authorization mechanism. All
application authentication and provider usage restrictions still apply.

The normal outbound network remains available for GitHub, npm, Python
packages, and Desktop Commander's remote connection.

Use a dedicated network name that is not already assigned to another
application.

The shared network is not removed during uninstall or teardown because
other applications may still depend on it.

## Role Variables

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `desktop_commander_container_engine` | str | Docker-only runtime. | `docker` |
| `desktop_commander_state` | str | Choices: `present`, `absent`, `teardown`. | `present` |
| `desktop_commander_debug_mode` | bool | Enable non-sensitive diagnostics. | `false` |
| `desktop_commander_image` | str | Node.js runtime and development image base. | `docker.io/library/node:24-bookworm-slim` |
| `desktop_commander_package_version` | str | Pinned Desktop Commander npm version. | `0.3.4` |
| `desktop_commander_container_name` | str | Remote agent container name. | `desktop-commander` |
| `desktop_commander_pull_policy` | str | Pull policy when not building locally. | `missing` |
| `desktop_commander_pull_images` | bool | Force pulls when not building locally. | `false` |
| `desktop_commander_restart_policy` | str | Container restart policy. | `unless-stopped` |
| `desktop_commander_build_development_image` | bool | Build a local image with development utilities. | `false` |
| `desktop_commander_development_image` | str | Local development image name and tag. | `desktop-commander-development:local` |
| `desktop_commander_base_dir` | path | Root-owned deployment directory; never mounted. | `/opt/desktop_commander` |
| `desktop_commander_system_user` | str | Required dedicated Linux account. | `chat-gpt` |
| `desktop_commander_host_home` | path | The only permitted host bind mount. | `/home/chat-gpt` |
| `desktop_commander_shared_network` | str | Optional internal Docker network. | `""` |
| `desktop_commander_tmpfs_size` | str | Private `/tmp` size. | `256m` |
| `desktop_commander_memory_limit` | str | Container memory limit. | `1g` |
| `desktop_commander_pids_limit` | int | Container process limit. | `128` |

The account, home path, Docker engine, and base directory are intentionally
checked against fixed safe values.

## Lifecycle

- `present`: validate the account and filesystem boundary, optionally
  build the development image, configure networking, and deploy.
- `absent`: stop and remove the Compose stack while preserving deployment
  files, account data, and images.
- `teardown`: remove the stack and its root-owned deployment directory.

Neither uninstall nor teardown deletes `/home/chat-gpt`, saved device
credentials, development repositories, or the shared network.

## Example playbook

```yaml
---
- name: "Install isolated Remote Desktop Commander"
  hosts: "desktop_commander_hosts"
  become: true
  roles:
    - role: "jcook3701.docker.desktop_commander"
      vars:
        desktop_commander_state: "present"
        desktop_commander_build_development_image: true
        desktop_commander_shared_network: "desktop_commander_ai"
```

## First-time pairing

The remote agent prints a verification URL and code during its first
startup.

```bash
sudo docker compose -f /opt/desktop_commander/compose.yml logs -f desktop_commander
```

Open the verification URL on a trusted browser and authorize the device.

The persistent device credentials are stored beneath:

```text
/home/chat-gpt/.desktop-commander-device/
```

Do not commit or share these credentials.

Existing pairing information is preserved across container rebuilds.

## GitHub configuration

Authenticate GitHub CLI using a dedicated GitHub account:

```bash
sudo docker exec -it desktop-commander gh auth login
```

Configure Git to use GitHub CLI for authentication:

```bash
sudo docker exec -it desktop-commander gh auth setup-git
```

Configure the dedicated account's Git author identity:

```bash
sudo docker exec -it desktop-commander \
    git config --global user.name "YOUR_GITHUB_ACCOUNT_NAME"

sudo docker exec -it desktop-commander \
    git config --global user.email "YOUR_GITHUB_ACCOUNT_EMAIL"
```

GitHub configuration and Git settings persist beneath `/home/chat-gpt`.

Grant the dedicated account access only to the repositories it needs.

Never include authentication tokens in repository files or image build
arguments.

## Python development environment

Create virtual environments within individual project directories:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,tools]"
```

Use the dependency configuration provided by the individual project.

Do not modify host Python environments or install Python dependencies into
the container's read-only system directories.

## Verify containment

Confirm the container's mounts:

```bash
sudo docker inspect desktop-commander --format '{{json .Mounts}}'
```

Confirm the agent runs as the dedicated non-root account:

```bash
sudo docker exec desktop-commander id
sudo docker exec desktop-commander whoami
```

Confirm that the development tools are available:

```bash
sudo docker exec desktop-commander git --version
sudo docker exec desktop-commander gh --version
sudo docker exec desktop-commander python3 --version
sudo docker exec desktop-commander node --version
```

Confirm the persistent workspace and private temporary storage are writable:

```bash
sudo docker exec desktop-commander \
    sh -c 'test -w /home/chat-gpt && test -w /tmp'
```

Confirm the root filesystem is read-only:

```bash
sudo docker inspect desktop-commander \
    --format '{{.HostConfig.ReadonlyRootfs}}'
```

Confirm the Docker socket is unavailable:

```bash
sudo docker exec desktop-commander \
    sh -c 'test ! -e /var/run/docker.sock'
```

When FreeLLMAPI is attached to the optional shared network, verify
connectivity:

```bash
sudo docker exec desktop-commander \
    curl --fail --silent http://freellmapi:3001/api/ping
```

Application credentials are still required for authenticated inference and
administrative endpoints.

## Limitations

A privileged Docker administrator or Docker runtime compromise can bypass
the container filesystem boundary.

The development image deliberately does not include the Docker CLI or mount
the Docker socket.

The shared network does not replace authentication or outbound firewall
rules.

Host processes running directly as the dedicated account remain governed
by host operating system permissions.

## Author Information

Maintained by **Jared W. Cook** as part of the core infrastructure and container management ecosystem.
