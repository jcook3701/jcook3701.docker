# SkillSpector

[NVIDIA SkillSpector](https://github.com/NVIDIA/SkillSpector) is an
open-source security scanner for AI agent skills.

This Ansible role builds a version-pinned SkillSpector Docker image
and installs an on-demand scanner launcher.

The role uses the official upstream Dockerfile and does not install
SkillSpector Python packages directly on the host.

SkillSpector runs only when explicitly invoked. It does not require
a permanently running container.

## Role Variables

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| **Runtime Orchestration Engine and Service State** | | | |
| `skillspector_container_engine` | `str` | Container engine. Choices: `docker`. | `docker` |
| `skillspector_state` | `str` | Desired lifecycle state. Choices: `present`, `absent`, `teardown`. | `present` |
| `skillspector_debug_mode` | `bool` | Enable additional debugging output. | `false` |
| **Upstream Source and Container Image** | | | |
| `skillspector_repository` | `str` | Official SkillSpector source repository. | `https://github.com/NVIDIA/SkillSpector.git` |
| `skillspector_version` | `str` | Version tag of the locally built container image. | `2.13.6` |
| `skillspector_revision` | `str` | Pinned upstream Git commit. | `e2674da339b0bddc6e565d059c0577c6d9cd25da` |
| `skillspector_image` | `str` | Name assigned to the local Docker image. | `skillspector-local` |
| `skillspector_rebuild_image` | `bool` | Force rebuilding an existing image. | `false` |
| **Deployment Paths and Dedicated Sandbox Identity** | | | |
| `skillspector_base_dir` | `path` | Root directory used for the source checkout. | `/opt/skillspector` |
| `skillspector_wrapper_path` | `path` | Installation path of the scanner launcher. | `/usr/local/bin/skillspector-docker` |
| `skillspector_user` | `str` | Dedicated non-root account used by the scanner. | `chat-gpt` |
| `skillspector_group` | `str` | Dedicated group used by the scanner. | `chat-gpt` |
| `skillspector_user_home` | `path` | Home directory of the dedicated scanner account. | `/home/chat-gpt` |
| `skillspector_workspace_dir` | `path` | Base workspace for scanner inputs and reports. | `{{ skillspector_user_home }}/workbench` |
| `skillspector_scan_dir` | `path` | Directory containing local scan inputs. | `{{ skillspector_workspace_dir }}/skill-scans` |
| `skillspector_reports_dir` | `path` | Directory containing generated scan reports. | `{{ skillspector_workspace_dir }}/skill-reports` |
| **Runtime Security and Resource Controls** | | | |
| `skillspector_network_mode` | `str` | Container networking. Choices: `bridge`, `none`. | `bridge` |
| `skillspector_memory_limit` | `str` | Maximum container memory allocation. | `2g` |
| `skillspector_cpu_limit` | `str` | Maximum CPU allocation. | `2.0` |
| `skillspector_pids_limit` | `int` | Maximum number of container processes. | `256` |
| `skillspector_tmpfs_size` | `str` | Maximum size of the temporary filesystem. | `512m` |
| **Optional Local Ollama Analysis** | | | |
| `skillspector_enable_llm` | `bool` | Enable semantic analysis using a local Ollama model. | `false` |
| `skillspector_ollama_base_url` | `str` | Ollama API endpoint accessible to the scanner. | `http://host.docker.internal:11434/v1` |
| `skillspector_ollama_model` | `str` | Ollama model used for semantic analysis. | `qwen2.5-coder:7b` |

## Prerequisites

The following dependencies are required:

- Docker Engine installed and running.
- Ansible with the `community.docker` collection.
- Git installed on the managed host.
- A dedicated non-root system user and group.
- An existing home directory owned by the dedicated account.
- Network access to the upstream repository during installation.
- Docker Engine 25 or newer for recursive bind-mount restrictions.

The role does not create system users or groups.

The configured account home directory must be a real directory
owned by the dedicated account. The role enforces owner-only
permissions (`0700`) before completing validation.

## Installation

Include the role in an Ansible playbook:

```yaml
---
- name: "Deploy the SkillSpector scanner"
  hosts: "scanner_hosts"
  become: true

  roles:
    - role: "jcook3701.docker.skillspector"
      vars:
        skillspector_state: "present"
```

Replace `scanner_hosts` with the appropriate inventory group.

The installation performs these operations:

1. Validates the configured scanner account and directories.
2. Applies the required directory ownership and permissions.
3. Creates the source and scanner workspace directories.
4. Checks out the configured upstream Git revision.
5. Builds the version-pinned Docker image.
6. Installs the on-demand scanner launcher.

No permanent scanner container is started.

### Uninstall

To remove the launcher and Docker image while preserving source
files and generated reports:

```yaml
skillspector_state: "absent"
```

### Teardown

To remove the launcher, Docker image, and role-managed source
checkout:

```yaml
skillspector_state: "teardown"
```

**Warning:** The `teardown` state removes the configured
`skillspector_base_dir` directory.

Scanner inputs and generated reports are preserved.

## Scanner Usage

After installation, the scanner is available through the
`skillspector-docker` command.

Execute this command from a host environment authorized to use
the Docker Engine.

### Remote Repository Scanning

Scan a remote skill repository:

```shell
skillspector-docker https://github.com/example/agent-skill
```

Generate a JSON report:

```shell
skillspector-docker https://github.com/example/agent-skill \
  --format json \
  --output /reports/example.json
```

Remote skills are retrieved for analysis without being installed
as agent capabilities.

Review the generated findings before using a scanned skill.

### Local Skill Scanning

Place local skill files inside the configured
`skillspector_scan_dir` directory.

Example directory structure:

```text
workbench/
├── skill-scans/
│   └── example-skill/
└── skill-reports/
```

Run a local scan:

```shell
skillspector-docker ./example-skill
```

Generate a Markdown report:

```shell
skillspector-docker ./example-skill \
  --format markdown \
  --output /reports/example-skill.md
```

The launcher maps:

- `skillspector_scan_dir` to `/scan` as read-only.
- `skillspector_reports_dir` to `/reports` as read-write.

Local scan targets must be inside the configured scanner input
directory.

Generated reports are stored inside the configured reports
directory.

## Optional Ollama Integration

SkillSpector supports optional semantic analysis using a locally
hosted Ollama model.

Static analysis is enabled by default.

Configure the following variables to enable Ollama integration:

```yaml
skillspector_enable_llm: true
skillspector_network_mode: "bridge"
skillspector_ollama_base_url: "http://host.docker.internal:11434/v1"
skillspector_ollama_model: "qwen2.5-coder:7b"
```

The configured Ollama API must already be running and reachable
from the scanner container.

The launcher uses the Docker host-gateway alias to access the
configured Ollama service.

When `skillspector_enable_llm` is disabled, the launcher uses
SkillSpector's `--no-llm` option.

This role does not require cloud AI provider credentials.

## Container Security

The scanner runs in a restricted Docker container.

The launcher applies the following protections:

- Runs with the dedicated account's numeric UID and GID.
- Uses a read-only container root filesystem.
- Drops all Linux capabilities.
- Enables `no-new-privileges`.
- Limits available memory, CPU, and processes.
- Provides a private temporary filesystem.
- Mounts scanner input files read-only.
- Mounts the reports directory read-write.
- Disables recursive bind mounts.
- Does not enable privileged mode.
- Does not use the host PID namespace.
- Does not mount the host Docker socket.

The `bridge` network mode supports remote scanning and optional
Ollama integration.

The `none` network mode disables container networking and is
suitable for offline scans of local skill files.

Container isolation reduces the attack surface but does not
guarantee that untrusted material is harmless.

## Container Management

Inspect the installed container image:

```shell
docker image inspect skillspector-local:2.13.6
```

Verify the scanner launcher is installed:

```shell
command -v skillspector-docker
```

Inspect the launcher's container restrictions:

```shell
grep -E -- '--cap-drop|--read-only|--mount|--network' \
  /usr/local/bin/skillspector-docker
```

Execute a test scan against an existing local skill:

```shell
skillspector-docker ./example-skill \
  --format json \
  --output /reports/test-scan.json
```

The scanner container exits when the scan completes.

## Authors Notes

### Deployment Lifecycle

The role supports the standard lifecycle states:

| State | Description |
| :--- | :--- |
| `present` | Configure the scanner, build the image, and install the launcher. |
| `absent` | Remove the launcher and image while preserving scanner data. |
| `teardown` | Uninstall the scanner and remove the role-managed source checkout. |

### Container Engine Integration

SkillSpector is an on-demand command-line application rather than
a continuously running service.

The role uses `community.docker.docker_image` to build and manage
its Docker image.

The scanner launcher runs the image only when explicitly invoked.

This avoids automatically starting a scan during Ansible
deployment.

### Helpful Links

1. [NVIDIA SkillSpector](https://github.com/NVIDIA/SkillSpector)
2. [Docker Engine Documentation](https://docs.docker.com/engine/)
3. [Ansible Community Docker Collection](https://docs.ansible.com/ansible/latest/collections/community/docker/)

## Author Information

Maintained as part of the `jcook3701.docker` Ansible collection.
