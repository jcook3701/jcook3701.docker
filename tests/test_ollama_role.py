"""Regression checks for the Ollama role's MCP Gateway integration."""

from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
OLLAMA_ROLE = REPOSITORY_ROOT / "roles" / "ollama"
PINNED_GATEWAY_IMAGE = (
    "docker/mcp-gateway@"
    "sha256:f5a679a05fc39022a046167bef92aeeb01bcd59485ad27843ae5227db7950688"
)


def test_mcp_gateway_image_is_immutable_and_consistent() -> None:
    """Keep the role default and public argument specification synchronized."""
    defaults = (OLLAMA_ROLE / "defaults" / "main.yml").read_text(encoding="utf-8")
    argument_specs = (OLLAMA_ROLE / "meta" / "argument_specs.yml").read_text(
        encoding="utf-8"
    )
    gateway_spec = argument_specs.split("ollama_mcp_gateway_image:", maxsplit=1)[1]
    gateway_spec = gateway_spec.split("\n\n", maxsplit=1)[0]

    assert f'ollama_mcp_gateway_image: "{PINNED_GATEWAY_IMAGE}"' in defaults
    assert f'default: "{PINNED_GATEWAY_IMAGE}"' in gateway_spec


def test_mcp_gateway_compose_waits_for_readiness() -> None:
    """Require an application health probe before MCP Inspector starts."""
    template = (OLLAMA_ROLE / "templates" / "compose.yml.j2").read_text(
        encoding="utf-8"
    )

    expected_health_url = (
        "http://127.0.0.1:{{ ollama_mcp_gateway_internal_port }}/health"
    )
    assert expected_health_url in template
    assert "condition: service_healthy" in template
