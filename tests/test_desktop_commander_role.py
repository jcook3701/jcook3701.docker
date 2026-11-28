"""Regression checks for the isolated Desktop Commander development environment."""

# SPDX-FileCopyrightText: Copyright © 2026, Jared W. Cook
# SPDX-License-Identifier: AGPL-3.0-or-later

import json
from pathlib import Path
from typing import Any

import pytest
import yaml
from jinja2 import Environment, StrictUndefined

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DESKTOP_COMMANDER_ROLE = REPOSITORY_ROOT / "roles" / "desktop_commander"
FREELLMAPI_ROLE = REPOSITORY_ROOT / "roles" / "freellmapi"


def load_defaults(role: Path) -> dict[str, Any]:
    """Load the default configuration for a role."""
    defaults = yaml.safe_load(
        (role / "defaults" / "main.yml").read_text(encoding="utf-8")
    )

    assert isinstance(defaults, dict)
    return defaults


def render_template(
    role: Path,
    template_name: str,
    context: dict[str, Any],
) -> str:
    """Render a template using the required Ansible-compatible filters."""
    environment = Environment(
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
    )

    environment.filters["to_json"] = json.dumps
    environment.filters["bool"] = bool

    template = environment.from_string(
        (role / "templates" / template_name).read_text(encoding="utf-8")
    )

    return template.render(**context)


def render_compose(
    role: Path,
    context: dict[str, Any],
) -> dict[str, Any]:
    """Render and parse a Compose template."""
    rendered = yaml.safe_load(render_template(role, "compose.yml.j2", context))

    assert isinstance(rendered, dict)
    return rendered


def desktop_commander_context() -> dict[str, Any]:
    """Provide a representative dedicated-account configuration."""
    return {
        **load_defaults(DESKTOP_COMMANDER_ROLE),
        "inventory_hostname": "localhost",
        "getent_passwd": {
            "chat-gpt": [
                "x",
                "1004",
                "1005",
                "",
                "/home/chat-gpt",
                "/bin/bash",
            ],
        },
    }


def test_development_image_is_opt_in() -> None:
    """Preserve the original minimal deployment by default."""
    defaults = load_defaults(DESKTOP_COMMANDER_ROLE)

    assert defaults["desktop_commander_build_development_image"] is False
    assert defaults["desktop_commander_shared_network"] == ""


def test_git_and_gh_management_are_opt_in() -> None:
    """Avoid configuring Git identity or credentials by default."""
    defaults = load_defaults(DESKTOP_COMMANDER_ROLE)

    assert defaults["desktop_commander_manage_git"] is False
    assert defaults["desktop_commander_git_user_name"] == ""
    assert defaults["desktop_commander_git_user_email"] == ""
    assert defaults["desktop_commander_git_default_branch"] == "main"
    assert defaults["desktop_commander_manage_gh"] is False
    assert defaults["desktop_commander_gh_username"] == ""
    assert defaults["desktop_commander_gh_token"] == ""


@pytest.mark.parametrize("development_enabled", [False, True])
def test_desktop_commander_preserves_containment(
    development_enabled: bool,
) -> None:
    """Keep development and minimal deployments equally restricted."""
    context = desktop_commander_context()
    context["desktop_commander_build_development_image"] = development_enabled

    compose = render_compose(DESKTOP_COMMANDER_ROLE, context)
    service = compose["services"]["desktop_commander"]

    assert service["user"] == "1004:1005"
    assert service["read_only"] is True
    assert service["cap_drop"] == ["ALL"]
    assert service["security_opt"] == ["no-new-privileges:true"]
    assert service["environment"]["HOME"] == "/home/chat-gpt"

    assert len(service["volumes"]) == 1

    mount = service["volumes"][0]

    assert mount["source"] == "/home/chat-gpt"
    assert mount["target"] == "/home/chat-gpt"
    assert mount["read_only"] is False
    assert mount["bind"]["create_host_path"] is False
    assert mount["bind"]["propagation"] == "rprivate"

    assert "noexec" in service["tmpfs"][0]
    assert not service.get("privileged", False)
    assert "ports" not in service
    assert "devices" not in service
    assert "group_add" not in service
    assert "network_mode" not in service


@pytest.mark.parametrize("development_enabled", [False, True])
def test_desktop_commander_image_selection(
    development_enabled: bool,
) -> None:
    """Select the appropriate runtime without pulling the local image."""
    context = desktop_commander_context()
    context["desktop_commander_build_development_image"] = development_enabled

    compose = render_compose(DESKTOP_COMMANDER_ROLE, context)
    service = compose["services"]["desktop_commander"]

    if development_enabled:
        assert service["image"] == context["desktop_commander_development_image"]
        assert service["pull_policy"] == "build"
        assert service["build"]["context"] == "./build"
        assert service["build"]["dockerfile"] == "Dockerfile"
        assert service["build"]["args"]["DEVELOPMENT_UID"] == "1004"
        assert service["build"]["args"]["DEVELOPMENT_GID"] == "1005"
        assert (
            service["build"]["args"]["BASE_IMAGE"] == context["desktop_commander_image"]
        )
    else:
        assert service["image"] == context["desktop_commander_image"]
        assert service["pull_policy"] == context["desktop_commander_pull_policy"]
        assert "build" not in service


def test_desktop_commander_package_version_is_pinned() -> None:
    """Prevent an unintended change to an unversioned agent installation."""
    context = desktop_commander_context()
    compose = render_compose(DESKTOP_COMMANDER_ROLE, context)
    command = compose["services"]["desktop_commander"]["command"]

    package_version = context["desktop_commander_package_version"]

    assert package_version
    assert package_version != "latest"
    assert f"@wonderwhy-er/desktop-commander@{package_version}" in command


def test_development_image_contains_required_tools() -> None:
    """Ensure the rendered development image includes the required toolchain."""
    dockerfile = render_template(
        DESKTOP_COMMANDER_ROLE,
        "Dockerfile.j2",
        desktop_commander_context(),
    )

    required_tools = {
        "bash",
        "bash-completion",
        "build-essential",
        "ca-certificates",
        "curl",
        "diffutils",
        "dnsutils",
        "file",
        "gh",
        "git",
        "iproute2",
        "iputils-ping",
        "jq",
        "less",
        "libffi-dev",
        "libsqlite3-dev",
        "libssl-dev",
        "libyaml-dev",
        "lsof",
        "nano",
        "netcat-openbsd",
        "openssh-client",
        "openssl",
        "patch",
        "pipx",
        "pkg-config",
        "procps",
        "python3",
        "python3-dev",
        "python3-pip",
        "python3-venv",
        "ripgrep",
        "rsync",
        "shellcheck",
        "sqlite3",
        "tree",
        "unzip",
        "vim-tiny",
        "wget",
        "xz-utils",
        "yamllint",
        "zip",
    }

    assert required_tools.issubset(set(dockerfile.split()))
    assert "USER chat-gpt" in dockerfile
    assert dockerfile.rstrip().endswith("USER chat-gpt")


@pytest.mark.parametrize(
    "template_name",
    [
        "compose.yml.j2",
        "Dockerfile.j2",
    ],
)
def test_github_credentials_are_not_rendered(
    template_name: str,
) -> None:
    """Keep authentication credentials out of deployment templates."""
    context = desktop_commander_context()
    context.update(
        {
            "desktop_commander_build_development_image": True,
            "desktop_commander_manage_git": True,
            "desktop_commander_manage_gh": True,
            "desktop_commander_gh_username": "development-agent",
            "desktop_commander_gh_token": "test-credential-sentinel",
        }
    )

    rendered = render_template(
        DESKTOP_COMMANDER_ROLE,
        template_name,
        context,
    )

    assert context["desktop_commander_gh_token"] not in rendered


def test_github_token_argument_suppresses_logging() -> None:
    """Require the authentication token argument to suppress logging."""
    specifications = yaml.safe_load(
        (DESKTOP_COMMANDER_ROLE / "meta" / "argument_specs.yml").read_text(
            encoding="utf-8"
        )
    )

    options = specifications["argument_specs"]["main"]["options"]

    assert options["desktop_commander_gh_token"]["no_log"] is True


@pytest.mark.parametrize("shared_network", ["", "desktop_commander_ai"])
def test_desktop_commander_shared_network(
    shared_network: str,
) -> None:
    """Attach the optional network without removing normal connectivity."""
    context = desktop_commander_context()
    context["desktop_commander_shared_network"] = shared_network

    compose = render_compose(DESKTOP_COMMANDER_ROLE, context)
    service = compose["services"]["desktop_commander"]

    assert "desktop_commander" in service["networks"]

    if shared_network:
        assert "shared" in service["networks"]
        assert compose["networks"]["shared"]["name"] == shared_network
        assert compose["networks"]["shared"]["external"] is True
    else:
        assert "shared" not in service["networks"]
        assert "shared" not in compose["networks"]


@pytest.mark.parametrize(
    ("shared_network", "agent_network", "expected_networks"),
    [
        ("", "", {"freellmapi"}),
        ("jcook3701_proxy", "", {"freellmapi", "shared"}),
        ("", "desktop_commander_ai", {"freellmapi", "agent"}),
        (
            "jcook3701_proxy",
            "desktop_commander_ai",
            {"freellmapi", "shared", "agent"},
        ),
        (
            "jcook3701_proxy",
            "jcook3701_proxy",
            {"freellmapi", "shared"},
        ),
    ],
)
def test_freellmapi_agent_network_preserves_existing_configuration(
    shared_network: str,
    agent_network: str,
    expected_networks: set[str],
) -> None:
    """Keep existing networking, storage, and host publication unchanged."""
    context = {
        **load_defaults(FREELLMAPI_ROLE),
        "inventory_hostname": "localhost",
        "freellmapi_shared_network": shared_network,
        "freellmapi_agent_network": agent_network,
        "freellmapi_external_port": 3002,
        "freellmapi_file": {
            "secrets": "/opt/freellmapi/.env",
        },
        "freellmapi_directory": {
            "data": "/opt/freellmapi/data",
        },
    }

    compose = render_compose(FREELLMAPI_ROLE, context)
    service = compose["services"]["freellmapi"]

    assert set(service["networks"]) == expected_networks
    assert service["ports"] == ["127.0.0.1:3002:3001"]
    assert service["environment"]["FREEAPI_DB_PATH"] == "/app/server/data/freeapi.db"
    assert service["environment"]["REQUEST_ANALYTICS_MAX_ROWS"] == "100000"
    assert service["env_file"] == ["/opt/freellmapi/.env"]
    assert service["volumes"][0]["source"] == "/opt/freellmapi/data"

    if "shared" in expected_networks:
        assert compose["networks"]["shared"]["name"] == shared_network
        assert compose["networks"]["shared"]["external"] is True

    if "agent" in expected_networks:
        assert compose["networks"]["agent"]["name"] == agent_network
        assert compose["networks"]["agent"]["external"] is True
