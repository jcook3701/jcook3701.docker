# ROS2

[Robot Operating System 2](https://github.com/ros2) (ROS 2) is an open-source framework and set of software libraries and tools used to build robotic applications.

This Ansible role deploys and manages a containerized ROS 2 development environment with configurable networking, DDS discovery, persistent storage, and optional robotics hardware integration.

## Role Variables

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `ros2_container_engine` | string | Container engine used to deploy ROS 2. Choices: `docker`, `podman`. | `docker` |
| `ros2_state` | string | Desired lifecycle state. Choices: `present`, `absent`, `teardown`. | `present` |
| `ros2_debug_mode` | boolean | Enable additional debugging output during role execution. | `false` |
| `ros2_image` | string | Docker container image and ROS 2 distribution used for deployment. | `docker.io/library/ros:jazzy-ros-base` |
| `ros2_container_name` | string | Name assigned to the ROS 2 container. | `ros2` |
| `ros2_pull_policy` | string | Container image pull policy. | `always` |
| `ros2_restart_policy` | string | Container restart policy. | `unless-stopped` |
| `ros2_base_dir` | path | Base directory for persistent ROS 2 workspaces and configuration. | `/opt/ros2` |
| `ros2_tty` | boolean | Allocate a pseudo-TTY for interactive container sessions. | `true` |
| `ros2_stdin_open` | boolean | Keep standard input open for interactive development. | `true` |
| `ros2_command` | list[string] | Command executed when the container starts. Defaults to keeping the development container running. | `["sleep", "infinity"]` |
| `ros2_network_mode` | string | Container networking mode. Host networking supports DDS discovery across the local network. | `host` |
| `ros2_ipc_mode` | string | IPC namespace mode for shared-memory communication. | `host` |
| `ros2_domain_id` | integer | ROS 2 DDS domain identifier used to isolate communication between systems. | `0` |
| `ros2_automatic_discovery_range` | string | Automatic DDS discovery scope. Choices: `SUBNET`, `LOCALHOST`, `OFF`, `SYSTEM_DEFAULT`. | `SUBNET` |
| `ros2_rmw_implementation` | string | Optional ROS middleware implementation. Empty uses the image default. | `""` |
| `ros2_static_peers` | string | Semicolon-separated addresses for static ROS 2 discovery peers. | `""` |
| `ros2_devices` | list[string] | Additional host devices passed through to the container, such as serial or USB devices. | `[]` |
| `ros2_extra_volumes` | list[string] | Additional volume or directory mappings mounted into the container. | `[]` |
| `ros2_extra_environment` | dictionary | Additional environment variables passed into the container. | `{}

## Helpful Links

1. [Docker Docs](https://docs.docker.com/guides/ros2/)
2. [Docker Hub](https://hub.docker.com/_/ros)
3. [ROS 2 Documentation](https://docs.ros.org/en/jazzy/)
4. [ROS 2 GitHub](https://github.com/ros2)

## Author Information

Maintained by **Jared Cook** as part of the core infrastructure and container management ecosystem.
