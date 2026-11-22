# SkillSpector

[NVIDIA SkillSpector](https://github.com/NVIDIA/SkillSpector) is an
open-source security scanner for AI agent skills. It identifies
potential vulnerabilities, malicious patterns, and security risks
before skills are installed.

This Ansible role builds a version-pinned SkillSpector Docker image
and manages its configuration using Docker Compose.

SkillSpector runs on demand. No permanently running scanner
service is required.

## Role Variables

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| **Runtime Orchestration Engine and Service State** | | | |
| `skillspector_container_engine` | `str` | Container engine. Choices: `docker`. | `docker` |
| `skillspector_state` | `str` | Desired lifecycle: `present`, `absent`, `teardown`. | `present` |
| `skillspector_debug_mode` | `bool` | Enable additional role diagnostics. | `false` |
| **Upstream Source and Container Image** | | | |
| `skillspector_repository` | `str` | Official upstream Git repository. | `https://github.com/NVIDIA/SkillSpector.git` |
| `skillspector_version` | `str` | Version tag assigned to the local image. | `2.13.6` |
| `skillspector_revision` | `str` | Pinned upstream Git commit. | `e2674da339b0bddc6e565d059c0577c6d9cd25da` |
| `skillspector_image` | `str` | Local Docker image name. | `skillspector-local` |
| `skillspector_rebuild_image` | `bool` | Force rebuilding an existing image. | `false` |
| **Infrastructure Storage and Path Routing** | | | |
| `skillspector_base_dir` | `path` | Base directory for the source checkout and Compose file. | `/opt/skillspector` |
| `skillspector_wrapper_path` | `path` | Legacy launcher path used for migration cleanup only. | `/usr/local/bin/skillspector-docker` |
| **Scanner Identity and Storage** | | | |
| `skillspector_user` | `str` | Dedicated non-root account used by the scanner. | See role defaults |
| `skillspector_group` | `str` | Dedicated group used by the scanner. | See role defaults |
| `skillspector_user_home` | `path` | Home directory of the scanner account. | See role defaults |
| `skillspector_workspace_dir` | `path` | Workspace containing scanner inputs and reports. | `{{ skillspector_user_home }}/workbench` |
| `skillspector_scan_dir` | `path` | Directory mounted read-only for scanning. | `{{ skillspector_workspace_dir }}/skill-scans` |
| `skillspector_reports_dir` | `path` | Directory containing generated reports. | `{{ skillspector_workspace_dir }}/skill-reports` |
| **Runtime Security and Resource Controls** | | | |
| `skillspector_network_mode` | `str` | Container networking. Choices: `bridge`, `none`. | `bridge` |
| `skillspector_memory_limit` | `str` | Maximum container memory allocation. | `2g` |
| `skillspector_cpu_limit` | `str` | Maximum CPU allocation. | `2.0` |
| `skillspector_pids_limit` | `int` | Maximum number of container processes. | `256` |
| `skillspector_tmpfs_size` | `str` | Maximum temporary filesystem size. | `512m` |
| **Optional Ollama Integration** | | | |
| `skillspector_enable_llm` | `bool` | Enable semantic analysis using local Ollama. | `false` |
| `skillspector_ollama_base_url` | `str` | Local Ollama API endpoint. | `http://host.docker.internal:11434/v1` |
| `skillspector_ollama_model` | `str` | Model used for semantic analysis. | `qwen2.5-coder:7b` |

## Prerequisites

- Docker Engine with Docker Compose support.
- Ansible with the `community.docker` collection installed.
- Git installed on the managed host.
- A dedicated non-root scanner account and group.
- An existing home directory owned by the scanner account.
- Network access to the upstream source repository during installation.

The scanner account must exist before executing the role.

## Installation

Include the role in an Ansible playbook:

```yaml
---
- name: Deploy SkillSpector
  hosts: scanner_hosts
  become: true

  roles:
    - role: jcook3701.docker.skillspector
      vars:
        skillspector_state: "present"
```

The role performs the following operations:

1. Resolves the configured scanner account and group.
2. Creates the required deployment and scanner directories.
3. Deploys the Docker Compose configuration.
4. Checks out the configured upstream Git revision.
5. Builds the version-pinned Docker image.
6. Removes the superseded shell launcher, if present.

The scanner container is not started during installation.

## Scanner Usage

The Compose configuration is installed at:

```text
/opt/skillspector/compose.yml
```

The scanner uses a Docker Compose profile to support execution
on demand.

### Validate Docker Compose

```shell
docker compose -f /opt/skillspector/compose.yml config -q
```

### Scan a Remote Repository

Run a scan against a remote skill repository:

```shell
docker compose -f /opt/skillspector/compose.yml \
  run --rm skillspector https://github.com/example/agent-skill
```

Generate a JSON report:

```shell
docker compose -f /opt/skillspector/compose.yml \
  run --rm skillspector https://github.com/example/agent-skill \
  --format json --output /reports/example.json
```

Remote material is retrieved for analysis. Running a scan
does not install the scanned skill.

### Scan Local Files

Place skill files inside the configured `skillspector_scan_dir`.

Example directory layout:

```text
workbench/
├── skill-scans/
│   └── example-skill/
└── skill-reports/
```

Run a local scan:

```shell
docker compose -f /opt/skillspector/compose.yml \
  run --rm skillspector ./example-skill
```

Generate a Markdown report:

```shell
docker compose -f /opt/skillspector/compose.yml \
  run --rm skillspector ./example-skill \
  --format markdown --output /reports/example-skill.md
```

The Compose configuration mounts:

- `skillspector_scan_dir` at `/scan` with read-only access.
- `skillspector_reports_dir` at `/reports` with read-write access.

Generated reports are available in the configured reports
directory on the managed host.

## Optional Ollama Integration

SkillSpector supports optional semantic analysis using a
locally hosted Ollama model.

Static analysis is used by default.

To enable Ollama integration:

```yaml
skillspector_enable_llm: true
skillspector_network_mode: "bridge"
skillspector_ollama_base_url: "http://host.docker.internal:11434/v1"
skillspector_ollama_model: "qwen2.5-coder:7b"
```

The configured Ollama API must be running and reachable
from the scanner container.

With LLM integration disabled, the Compose configuration
automatically includes the `--no-llm` scanner option.

No cloud AI provider credentials are required.

## Container Security

The Compose configuration applies the following restrictions:

- Runs using the configured non-root account's UID and GID.
- Uses a read-only container root filesystem.
- Drops all Linux capabilities.
- Enables `no-new-privileges`.
- Limits CPU, memory, and process usage.
- Uses a private temporary filesystem.
- Mounts scanner inputs read-only.
- Mounts the reports directory read-write.
- Does not enable privileged mode.
- Does not mount the host Docker socket.
- Does not expose published container ports.

The default `bridge` network supports remote scanning and
optional Ollama integration.

Use `skillspector_network_mode: "none"` for local scans
that do not require network access.

Container restrictions reduce the attack surface but do not
guarantee the safety of untrusted content.

## Container Management

### Inspect the Docker Image

```shell
docker image inspect skillspector-local:2.13.6
```

### Inspect the Compose Configuration

```shell
docker compose -f /opt/skillspector/compose.yml config
```

### Run the Scanner

```shell
docker compose -f /opt/skillspector/compose.yml \
  run --rm skillspector ./example-skill
```

The `--rm` option removes the scanner container after execution.

### Uninstall

Configure the role state:

```yaml
skillspector_state: "absent"
```

This removes the role-managed image and any superseded launcher
while preserving the source checkout and scanner data.

### Teardown

Configure the role state:

```yaml
skillspector_state: "teardown"
```

This performs the uninstall operations and removes the
role-managed deployment directory.

**Warning:** Teardown deletes the contents of
`skillspector_base_dir`, including the source checkout
and generated Compose configuration.

Scanner inputs and generated reports remain preserved
when stored outside the deployment directory.

## Authors Notes

### Docker Compose Integration

This role follows the standard `jcook3701.docker` directory
structure and lifecycle conventions.

The deployment configuration is generated using
`templates/compose.yml.j2`.

SkillSpector uses an on-demand Compose service rather than
a continuously running application.

The service uses the `scan` profile to avoid starting
automatically during normal Compose operations.

The Docker image is built using `community.docker.docker_image`
from the pinned upstream source checkout.

The shared `jcook3701.utils.container_engine` role is used
for Compose removal during uninstall.

### Helpful Links

1. [NVIDIA SkillSpector](https://github.com/NVIDIA/SkillSpector)
2. [Docker Compose Documentation](https://docs.docker.com/compose/)
3. [Docker Compose Profiles](https://docs.docker.com/compose/how-tos/profiles/)
4. [Ansible Community Docker Collection](https://docs.ansible.com/ansible/latest/collections/community/docker/)

## Author Information

Maintained as part of the `jcook3701.docker` Ansible collection.
