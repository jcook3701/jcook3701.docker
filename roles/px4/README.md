# PX4-Autopilot

[PX4-Autopilot](https://github.com/PX4/PX4-Autopilot) (PX4) is an open-source autopilot stack for drones and unmanned vehicles. It supports multirotors, fixed-wing aircraft, VTOL platforms, rovers, and experimental vehicles ranging from racing quadcopters to industrial survey aircraft. PX4 provides development tooling for NuttX, Linux, and macOS and is licensed under BSD 3-Clause.

This Ansible role deploys and manages a containerized PX4 development environment with persistent workspaces, configurable networking, optional hardware access, and Software-in-the-Loop (SITL) simulation support.

## Installation

Setup **PX4-Autopilot** and install:

```shell
$ ansible-playbook jcook3701.docker.px4.yml -K
```

Remove **PX4-Autopilot** containers without deleting persistent application data:

```shell
$ ansible-playbook jcook3701.docker.px4.yml -K -e "px4_state=absent"
```

Remove **PX4-Autopilot** containers and persistent application data:

```shell
$ ansible-playbook jcook3701.docker.px4.yml -K -e "px4_state=teardown"
```

**Warning:** The `teardown` lifecycle is intended to remove the deployment and its persistent data. Back up important PX4 source code and workspaces before executing it.

## Role Variables

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `px4_container_engine` | string | Container engine used to deploy PX4. Choices: `docker`, `podman`. | `docker` |
| `px4_state` | string | Desired lifecycle state. Choices: `present`, `absent`, `teardown`. | `present` |
| `px4_debug_mode` | boolean | Enable additional debugging output during role execution. | `false` |
| `px4_image` | string | Official PX4 development container image and version. | `docker.io/px4io/px4-dev:v1.17.0` |
| `px4_container_name` | string | Name assigned to the PX4 development container. | `px4` |
| `px4_pull_policy` | string | Container image pull policy. | `always` |
| `px4_restart_policy` | string | Container restart policy. | `unless-stopped` |
| `px4_manage_sitl` | boolean | Enable deployment of the optional PX4 SITL simulation container. | `false` |
| `px4_sitl_image` | string | Container image used for PX4 Software-in-the-Loop simulation. | `docker.io/px4io/px4-sitl:latest` |
| `px4_sitl_container_name` | string | Name assigned to the PX4 SITL container. | `px4-sitl` |
| `px4_sitl_model` | string | Optional SITL vehicle model. Empty uses the container image default. | `""` |
| `px4_sitl_extra_environment` | dictionary | Additional environment variables passed to the SITL container. | `{}` |
| `px4_sitl_extra_volumes` | list[string] | Additional volume mappings for the SITL container. | `[]` |
| `px4_base_dir` | path | Base directory for persistent PX4 workspaces and configuration. | `/opt/px4` |
| `px4_tty` | boolean | Allocate a pseudo-TTY for interactive development sessions. | `true` |
| `px4_stdin_open` | boolean | Keep standard input open for interactive container access. | `true` |
| `px4_command` | list[string] | Command executed when the development container starts. | `["sleep", "infinity"]` |
| `px4_container_user` | string | Optional container execution user or UID. Empty preserves the image default. | `""` |
| `px4_network_mode` | string | Container networking mode supporting MAVLink and other robotics communication. | `host` |
| `px4_ipc_mode` | string | Container IPC namespace mode. | `private` |
| `px4_devices` | list[string] | Additional host hardware devices exposed to the PX4 container. | `[]` |
| `px4_extra_volumes` | list[string] | Additional host directories or volumes mounted into the development container. | `[]` |
| `px4_extra_environment` | dictionary | Additional environment variables passed into the development container. | `{}` |

## PX4 SITL Simulation

The role supports an optional PX4 Software-in-the-Loop (SITL) container, allowing PX4 flight-control software to run in a simulated environment without physical flight-controller hardware.

SITL is disabled by default. To enable it, override the following variables:

```yaml
px4_manage_sitl: true
px4_sitl_model: "sihsim_quadcopter"
```

The SIH simulator provides a lightweight simulation environment without requiring Gazebo or a graphical display.

The simulation can be used with external tools such as QGroundControl and MAVSDK, provided the corresponding networking and MAVLink endpoints are configured.

## Persistent Storage

The role uses `/opt/px4` as its default deployment directory.

```text
/opt/px4/
├── compose.yml
├── workspace/
│   └── PX4-Autopilot/
└── ccache/
```

The PX4-Autopilot source directory is populated separately when the project is cloned into the workspace.

Persistent storage allows the development workspace, source files, and compiler cache to survive container recreation.

## Container Management

Check container status:

```shell
sudo docker compose -f /opt/px4/compose.yml ps
```

Enter the PX4 development environment:

```shell
sudo docker compose -f /opt/px4/compose.yml exec px4 bash
```

View SITL logs when simulation is enabled:

```shell
sudo docker compose -f /opt/px4/compose.yml logs -f px4-sitl
```

## Helpful Links

1. [PX4 Docs — Docker](https://docs.px4.io/main/en/test_and_ci/docker)
2. [Docker Hub — PX4](https://hub.docker.com/u/px4io/)
3. [PX4-Containers](https://github.com/PX4/PX4-containers)
4. [PX4-Autopilot GitHub](https://github.com/PX4/PX4-Autopilot)
5. [PX4 Simulation Documentation](https://docs.px4.io/main/en/simulation/)

## Author Information

Maintained by **Jared W. Cook** as part of the core infrastructure and container management ecosystem.
