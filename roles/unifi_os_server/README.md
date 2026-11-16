# Unifi OS Server

## Role Variables

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| **unifi_os_server_container_engine** | str | The underlying tool environment platform executing service deployment stacks. <br> Choices: `docker`, `podman` | `"docker"` |
| **unifi_os_server_state** | str | The target installation or cleanup baseline enforcement configuration layer profile state indicator. <br> Choices: `present`, `absent` | `"present"` |
| **unifi_os_server_image** | str | The container image registry path for the UniFi application. | `"jacobalberty/unifi"` |
| **unifi_os_server_version** | str | The version tag of the UniFi image to deploy. | `"latest"` |
| **unifi_os_server_base_dir** | str | The absolute base directory path on the host for all persistent container deployment subdirectories. | `"/opt/unifi-os"` |
| **unifi_os_server_data_dir** | str | Host directory mapping path for persistent internal database files. | `"{{ unifi_os_server_base_dir }}/data"` |
| **unifi_os_server_log_dir** | str | Host directory mapping path for centralized service log file output collection. | `"{{ unifi_os_server_base_dir }}/logs"` |
| **unifi_os_server_cert_dir** | str | Host directory mapping path tracking custom secure layer communication certificate entries. | `"{{ unifi_os_server_base_dir }}/cert"` |
| **unifi_os_server_container_name** | str | The identifier tracking the initialized engine execution container instance. | `"unifi-os-server"` |
| **unifi_os_server_network_name** | str | The designated isolated virtual bridge backend networking structure namespace identifier. | `"unifi-network"` |
| **unifi_os_server_restart_policy** | str | Engine runtime recovery routine evaluation metrics framework context logic choice tracking rules. <br> Choices: `no`, `always`, `on-failure`, `unless-stopped` | `"unless-stopped"` |
| **unifi_os_server_port_http** | int | Port binding mapping for device initialization inform utility services communication pipelines. | `8080` |
| **unifi_os_server_port_https** | int | Port binding mapping for local area browser user dashboard interface web control portals. | `8443` |
| **unifi_os_server_port_portal** | int | Port binding mapping routing processing structures handling secure guest access verification capture landings. | `8843` |
| **unifi_os_server_port_speedtest** | int | Port binding mapping verifying link throughput capacity assessment check benchmarks metric collection tasks. | `6789` |
| **unifi_os_server_port_stun** | int | Port binding mapping managing session traversal validation echo signals communication routes network layers. | `3478` |
| **unifi_os_server_port_discovery** | int | Port binding mapping handling automated broad layer component sweep broadcast discovery resolution loops. | `10001` |
| **unifi_os_server_port_syslog** | int | Port binding mapping routing structural remote infrastructure tracking event telemetry daemon relays downstream. | `5514` |
| **unifi_os_server_jvm_init_xms** | str | The initial execution block environment memory reservation metric requested by runtime applications. | `"1024m"` |
| **unifi_os_server_jvm_max_xmx** | str | The ceiling constraint limit memory processing block standard boundary context parameter values allowed. | `"2048m"` |

## Author Information

Maintained by **Jared Cook** as part of the core infrastructure and container management ecosystem.
