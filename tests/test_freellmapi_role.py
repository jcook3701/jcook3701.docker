"""Regression checks for the FreeLLMAPI role."""

from pathlib import Path

import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
FREELLMAPI_ROLE = REPOSITORY_ROOT / "roles" / "freellmapi"


def test_freellmapi_image_is_version_pinned() -> None:
    """Prevent unintentional upgrades to the latest container image."""
    defaults = yaml.safe_load(
        (FREELLMAPI_ROLE / "defaults" / "main.yml").read_text(encoding="utf-8")
    )

    image = defaults["freellmapi_image"]

    assert image.startswith("ghcr.io/tashfeenahmed/freellmapi:")
    assert not image.endswith(":latest")


def test_freellmapi_defaults_are_private() -> None:
    """Keep the gateway private and destructive operations disabled."""
    defaults = yaml.safe_load(
        (FREELLMAPI_ROLE / "defaults" / "main.yml").read_text(encoding="utf-8")
    )

    assert defaults["freellmapi_bind_ip"] == "127.0.0.1"
    assert defaults["freellmapi_teardown_remove_data"] is False
    assert defaults["freellmapi_teardown_remove_images"] is False


def test_freellmapi_preserves_encryption_key() -> None:
    """Prevent replacement of the persistent encryption key."""
    configuration = (FREELLMAPI_ROLE / "tasks" / "configure" / "01_seed.yml").read_text(
        encoding="utf-8"
    )

    assert "force: false" in configuration
    assert "ENCRYPTION_KEY=" in configuration
    assert 'mode: "0600"' in configuration
    assert "no_log: true" in configuration


def test_freellmapi_uses_shared_container_engine() -> None:
    """Preserve the collection's container lifecycle architecture."""
    for filename in ("install.yml", "uninstall.yml", "teardown.yml"):
        content = (FREELLMAPI_ROLE / "tasks" / "state" / filename).read_text(
            encoding="utf-8"
        )

        assert "jcook3701.utils.container_engine" in content


def test_freellmapi_compose_security_controls() -> None:
    """Preserve container security and persistent storage controls."""
    template = (FREELLMAPI_ROLE / "templates" / "compose.yml.j2").read_text(
        encoding="utf-8"
    )

    assert "no-new-privileges:true" in template
    assert "create_host_path: false" in template
    assert "freellmapi_file.secrets" in template
    assert "freellmapi_directory.data" in template
    assert "/app/server/data" in template
    assert "/api/ping" in template
