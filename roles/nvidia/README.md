# Nvidia

The nvidia/cuda:12.8.1-base-ubuntu24.04 is an official Docker container image provided by NVIDIA that packages a minimal CUDA 12.8.1 runtime environment on top of an Ubuntu 24.04 LTS operating system base.

## Role Variables

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `nvidia_container_engine` | `str` | Container engine to configure for NVIDIA GPU access. Choices: `docker`. | `docker` |
| `nvidia_state` | `str` | Whether the NVIDIA Container Toolkit should be installed or removed. Choices: `present`, `absent`. | `present` |
| `nvidia_debug_mode` | `bool` | Enable additional debug output during role execution. | `false` |

Role is equivalent to the below docker command.  The entire purpose of this role is to test the connection between nvidia-container-runtime and docker/podman.

``` shell
docker run --rm --runtime=nvidia --gpus all   nvidia/cuda:12.8.1-base-ubuntu24.04 nvidia-smi
```

## Author Information

Maintained by **Jared W. Cook** as part of the core infrastructure and container management ecosystem.
