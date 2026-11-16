# Timesketch

[Timesketch](https://timesketch.org/) is an open-source tool for collaborative forensic timeline analysis. Using sketches you and your collaborators can organize and work together.

## Role Variables

| Variable | Type | Description / Choices | Default |
| :--- | :--- | :--- | :--- |
| **timesketch_container_engine** | `str` | The targeted container virtualization abstraction runtime platform engine.<br>Choices: `docker`, `podman` | `"docker"` |
| **timesketch_state** | `str` | Desired structural assertion state of the deployment components.<br>Choices: `present`, `absent` | `"present"` |
| **timesketch_debug_mode** | `bool` | Toggles verbose tracing flags across configuration initialization processes. | `true` |
| **timesketch_image** | `str` | The complete upstream remote image repository URI target path name reference. | `"us-docker.pkg.dev/osdfir-registry/timesketch/timesketch:latest"` |
| **timesketch_opensearch_version** | `str` | Version tag identifier reference for the OpenSearch data storage indexing layer. | `"2.11.0"` |
| **timesketch_postgres_version** | `str` | Version tag identifier reference for the backend relational PostgreSQL datastore engine. | `"15-alpine"` |
| **timesketch_redis_version** | `str` | Version tag identifier reference for the persistent memory cache task messaging queue broker. | `"7-alpine"` |
| **timesketch_base_dir** | `path` | Root structural parent file path tracking system variables on the destination host node. | `"/opt/timesketch"` |
| **timesketch_config_dir** | `path` | Target folder routing configuration manifest files for application mounting hooks. | `"{{ timesketch_base_dir }}/config"` |
| **timesketch_upload_dir** | `path` | Target location storing uploaded binary evidence files processed by analyzer routines. | `"{{ timesketch_base_dir }}/upload"` |
| **timesketch_postgres_data_dir** | `path` | Target location mapping backing blocks for relational database state preservation files. | `"{{ timesketch_base_dir }}/postgres_data"` |
| **timesketch_opensearch_data_dir** | `path` | Target location mapping persistent structural document stores for search records. | `"{{ timesketch_base_dir }}/opensearch_data"` |
| **timesketch_listen_port** | `int` | The host network adapter ingress network tracking port allocation number mapping target. | `8444` |
| **timesketch_network_name** | `str` | The custom bridge isolated local runtime container virtual interface mapping name identifier. | `"timesketch_net"` |
| **timesketch_admin_user** | `str` | The primary administrative credential control user account login handle access name. | `"admin"` |
| **timesketch_admin_password** | `str` | The primary administrative control profile login pass phrase token authorization key string. *(Sensitive information masked)* | `"SetSecurePasswordHere"` |
| **timesketch_db_user** | `str` | Relational service platform programmatic management engine entry point user connection handle. | `"timesketch"` |
| **timesketch_db_password** | `str` | Relational database platform structural schema authentication token encryption access key pass. *(Sensitive information masked)* | `"SetSecureDatabasePasswordHere"` |
| **timesketch_db_name** | `str` | Target relational scheme namespace folder created for internal data tables. | `"timesketch"` |
| **timesketch_opensearch_jvm_opts** | `str` | Java virtual machine garbage memory constraint threshold tuning argument control string hooks. | `"-Xms2g -Xmx2g"` |

## Author Information

Maintained by **Jared Cook** as part of the core infrastructure and container management ecosystem.

<!--
## Authors Notes

### Helpful Links

1. [Setup Guide](https://timesketch.org/guides/admin/install/)

-->
