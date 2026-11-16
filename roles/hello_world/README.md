# 'Hello World' Docker Image

The [hello-world]() image is a prime example of using the scratch image effectively. See hello.c in https://github.com/docker-library/hello-world for the source code of the hello binary included in this image.

Because this image consists of nothing but a single static binary which prints some text to standard output, it can trivially be run as any arbitrary user (docker run --user $RANDOM:$RANDOM hello-world, for example).

## Role Variables

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| **`hello_world_container_engine`** | `str` | The background execution runtime used to manage the hello-world components.<br><br>**Choices:** `docker`, `podman` | `"docker"` |
| **`hello_world_state`** | `str` | The desired state of the hello-world container and its cached local image.<br><br>**Choices:** `present`, `absent`, `teardown` | `"present"` |

## Author Information

Maintained by **Jared Cook** as part of the core infrastructure and container management ecosystem.
