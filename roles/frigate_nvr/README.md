# Frigate NVR

[Frigate](https://frigate.video/) is a local network video recorder with
real-time object detection. The `jcook3701.docker.frigate_nvr` role renders its
configuration and Docker Compose stack, then uses the collection's established
`jcook3701.utils.container_engine` integration to manage the service lifecycle.

## Requirements

- Docker Engine and Docker Compose v2 on the target host. Podman remains an
  experimental option through the shared container engine integration.
- The `jcook3701.utils.container_engine` role and `community.docker` collection.
- Network access to GHCR on the first image pull.
- Camera stream URLs and any required accelerator devices supplied through
  inventory or Ansible Vault.

The role does not install camera drivers, accelerator drivers, or an MQTT
broker. Its existing `jcook3701.pkgs.docker_ce` dependency provides Docker.

## Configuration ownership

The default `frigate_nvr_config_owner: "ansible"` makes the rendered
`config.yml` read-only inside the container and overwrites it on every role run.
This keeps inventory authoritative, but configuration changes made in the
Frigate UI cannot be saved permanently.

Set `frigate_nvr_config_owner: "frigate"` to seed `config.yml` only when it is
absent and mount it read-write. Frigate then owns all subsequent UI changes;
later Ansible variable changes do not replace the existing file. Choose one
ownership model rather than switching back and forth.

## Network and security model

The authenticated UI and API are published on port `8971`. Frigate generates an
administrator account on first startup and writes the initial password to its
container logs. Change that password after the first login. The current default
endpoint does not provide TLS, so use a trusted network or TLS reverse proxy to
protect credentials and video traffic in transit.

Port `5000` is an internal unauthenticated administrator interface and is not
published by default. If a trusted local integration requires it, set
`frigate_nvr_publish_unauthenticated_port: true`; it remains bound to
`127.0.0.1` unless explicitly changed. RTSP restreams on port `8554` are also
unauthenticated by default; configure go2rtc authentication or limit host
network access when restreams are sensitive.

MQTT is disabled by default. When enabled, its connection values are passed
through Docker environment variables and the root-only Compose file. Keep the
password in Ansible Vault. Docker administrators can still read container
environment variables through inspection.

Hardware access is opt-in. Add only the required mappings to
`frigate_nvr_devices`; avoid `frigate_nvr_privileged: true` unless the selected
accelerator cannot work with narrower device access.

## Data lifecycle

- `present`: create persistent directories, render or seed configuration, and
  deploy Frigate.
- `absent`: stop and remove the container while preserving configuration,
  recordings, and the image.
- `teardown`: stop the stack and remove the Compose file while preserving
  Frigate configuration, recordings, and the database by default.
- `frigate_nvr_teardown_remove_images: true`: ask the shared engine role to
  remove the Frigate image during teardown.
- `frigate_nvr_teardown_remove_data: true`: permanently remove the entire base
  directory, including configuration, database, recordings, clips, and exports.

Back up persistent data before enabling the destructive teardown option.

## Role Variables

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| `frigate_nvr_container_engine` | str | Choices: `docker`, experimental `podman`. | `docker` |
| `frigate_nvr_state` | str | Lifecycle. Choices: `present`, `absent`, `teardown`. | `present` |
| `frigate_nvr_debug_mode` | bool | Display non-sensitive diagnostics. | `false` |
| `frigate_nvr_teardown_remove_data` | bool | Permanently delete all persistent data during teardown. | `false` |
| `frigate_nvr_teardown_remove_images` | bool | Remove the image during teardown. | `false` |
| `frigate_nvr_image` | str | Official image repository. | `ghcr.io/blakeblackshear/frigate` |
| `frigate_nvr_version` | str | Image tag. | `stable` |
| `frigate_nvr_container_name` | str | Container name. | `frigate` |
| `frigate_nvr_pull_policy` | str | Compose pull policy. Choices: `always`, `missing`, `never`. | `missing` |
| `frigate_nvr_pull_images` | bool | Force image pulls through the shared engine role. | `false` |
| `frigate_nvr_restart_policy` | str | Standard Compose restart policy. | `unless-stopped` |
| `frigate_nvr_base_dir` | path | Deployment and persistent data root. | `/opt/frigate_nvr` |
| `frigate_nvr_config_dir` | path | Configuration and runtime metadata directory. | `/opt/frigate_nvr/config` |
| `frigate_nvr_logs_dir` | path | Reserved deployment log directory. | `/opt/frigate_nvr/logs` |
| `frigate_nvr_storage_dir` | path | Recordings, clips, exports, and database directory. | `/opt/frigate_nvr/storage` |
| `frigate_nvr_config_owner` | str | Choices: `ansible`, `frigate`. | `ansible` |
| `frigate_nvr_bind_ip` | str | Host address for authenticated UI, RTSP, and WebRTC. | `0.0.0.0` |
| `frigate_nvr_web_port` | int | Authenticated UI/API host port. | `8971` |
| `frigate_nvr_rtsp_port` | int | RTSP restream host port. | `8554` |
| `frigate_nvr_webrtc_port` | int | WebRTC TCP host port. | `8555` |
| `frigate_nvr_webrtc_udp_port` | int | WebRTC UDP host port. | `8555` |
| `frigate_nvr_publish_unauthenticated_port` | bool | Publish Frigate's internal unauthenticated port. | `false` |
| `frigate_nvr_unauthenticated_bind_ip` | str | Bind address for optional unauthenticated access. | `127.0.0.1` |
| `frigate_nvr_unauthenticated_port` | int | Host port mapped to container port `5000`. | `5000` |
| `frigate_nvr_privileged` | bool | Give the container broad host access. | `false` |
| `frigate_nvr_shm_size` | str | Shared memory for decoded frames. | `512mb` |
| `frigate_nvr_tmpfs_size` | int | In-memory recording cache size in bytes. | `1000000000` |
| `frigate_nvr_stop_grace_period` | str | Graceful shutdown allowance. | `30s` |
| `frigate_nvr_timezone` | str | Container timezone. | `UTC` |
| `frigate_nvr_devices` | list[str] | Accelerator device mappings. | `[]` |
| `frigate_nvr_mqtt_enabled` | bool | Enable optional MQTT integration. | `false` |
| `frigate_nvr_mqtt_host` | str | MQTT broker hostname. | `localhost` |
| `frigate_nvr_mqtt_user` | str | Optional MQTT username. | `` |
| `frigate_nvr_mqtt_password` | str | Vault-managed MQTT password. | `` |
| `frigate_nvr_detectors` | dict | Detector definitions; empty uses Frigate's CPU default. | `{}` |
| `frigate_nvr_record` | dict | Global recording settings. | See `defaults/main.yml`. |
| `frigate_nvr_snapshots` | dict | Global snapshot settings. | See `defaults/main.yml`. |
| `frigate_nvr_extra_config` | dict | Additional top-level configuration excluding role-owned keys. | `{}` |
| `frigate_nvr_cameras` | list[dict] | Camera definitions. | `[]` |

The role owns `mqtt`, `database`, `detectors`, `record`, `snapshots`, and
`cameras`. Do not repeat those keys in `frigate_nvr_extra_config`. Each camera
can provide `extra_config` for additional per-camera options, but it cannot
replace that camera's `enabled`, `ffmpeg`, `detect`, or `zones` blocks.

## Example playbook

```yaml
---
- name: Deploy Frigate NVR
  hosts: "frigate_hosts"
  become: true
  roles:
    - role: "jcook3701.docker.frigate_nvr"
      vars:
        frigate_nvr_state: "present"
        frigate_nvr_timezone: "America/Los_Angeles"
        frigate_nvr_cameras:
          - name: "front_door"
            inputs:
              - path: "{{ vault_front_door_rtsp_url }}"
                roles:
                  - "detect"
                  - "record"
```

For a USB Coral, configure both the detector and the device mapping:

```yaml
frigate_nvr_devices:
  - "/dev/bus/usb:/dev/bus/usb"
frigate_nvr_detectors:
  coral:
    type: "edgetpu"
    device: "usb"
```

## Verification

After deployment, inspect the stack and retrieve the first-login credentials:

```bash
sudo docker compose -f /opt/frigate_nvr/compose.yml ps
sudo docker logs frigate
```

Then open `http://<host>:8971`, or the HTTPS address of a reverse proxy that
terminates TLS before forwarding to Frigate port `8971`.

## Helpful links

- [Frigate installation](https://docs.frigate.video/frigate/installation/)
- [Frigate configuration](https://docs.frigate.video/configuration/config/)
- [Frigate authentication](https://docs.frigate.video/configuration/authentication/)
- [Frigate repository](https://github.com/blakeblackshear/frigate)

## Author Information

Maintained by **Jared W. Cook** as part of the core infrastructure and container
management ecosystem. Licensed under AGPL-3.0-or-later.
