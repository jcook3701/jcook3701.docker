"""Regression checks for Docker collection role structure and configuration."""

from pathlib import Path
from typing import Any

import pytest
import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
ROLES_DIRECTORY = REPOSITORY_ROOT / "roles"

ROLES = sorted(path for path in ROLES_DIRECTORY.iterdir() if path.is_dir())

COMPOSE_ROLES = [
    role
    for role in ROLES
    if (role / "templates" / "compose.yml.j2").is_file()
    or (role / "templates" / "docker-compose.yml.j2").is_file()
]

SPECIFIED_ROLES = [
    role for role in ROLES if (role / "meta" / "argument_specs.yml").is_file()
]


def load_yaml(path: Path) -> Any:
    """Load a YAML configuration file."""
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("role", ROLES, ids=lambda role: role.name)
def test_role_defaults_exist(role: Path) -> None:
    """Require every role to define its default configuration."""
    assert (role / "defaults" / "main.yml").is_file()


@pytest.mark.parametrize("role", ROLES, ids=lambda role: role.name)
def test_role_tasks_exist(role: Path) -> None:
    """Require every role to provide a task entry point."""
    assert (role / "tasks" / "main.yml").is_file()


@pytest.mark.parametrize("role", ROLES, ids=lambda role: role.name)
def test_role_defaults_are_valid(role: Path) -> None:
    """Require defaults to contain a valid YAML mapping."""
    defaults = load_yaml(role / "defaults" / "main.yml")

    assert isinstance(defaults, dict)


@pytest.mark.parametrize("role", ROLES, ids=lambda role: role.name)
def test_role_tasks_are_valid(role: Path) -> None:
    """Require the task entry point to contain valid YAML."""
    tasks = load_yaml(role / "tasks" / "main.yml")

    assert isinstance(tasks, list)
    assert tasks


@pytest.mark.parametrize("role", ROLES, ids=lambda role: role.name)
def test_role_variable_namespace(role: Path) -> None:
    """Keep public role defaults within their respective namespaces."""
    defaults = load_yaml(role / "defaults" / "main.yml")
    prefix = f"{role.name}_"

    invalid_variables = [
        variable for variable in defaults if not variable.startswith(prefix)
    ]

    assert not invalid_variables, (
        f"{role.name} contains incorrectly namespaced variables: "
        f"{invalid_variables}"
    )


@pytest.mark.parametrize("role", SPECIFIED_ROLES, ids=lambda role: role.name)
def test_role_argument_specs_are_valid(role: Path) -> None:
    """Require a valid main argument specification."""
    specifications = load_yaml(role / "meta" / "argument_specs.yml")

    assert isinstance(specifications, dict)
    assert "argument_specs" in specifications
    assert "main" in specifications["argument_specs"]
    assert "options" in specifications["argument_specs"]["main"]


@pytest.mark.parametrize("role", SPECIFIED_ROLES, ids=lambda role: role.name)
def test_role_argument_defaults_are_consistent(role: Path) -> None:
    """Keep documented argument defaults synchronized with role defaults."""
    defaults = load_yaml(role / "defaults" / "main.yml")
    specifications = load_yaml(role / "meta" / "argument_specs.yml")
    options = specifications["argument_specs"]["main"]["options"]

    for variable, specification in options.items():
        if variable not in defaults or "default" not in specification:
            continue

        assert (
            defaults[variable] == specification["default"]
        ), f"{role.name}: inconsistent default for {variable}"


@pytest.mark.parametrize("role", SPECIFIED_ROLES, ids=lambda role: role.name)
def test_role_default_choices_are_valid(role: Path) -> None:
    """Require default values to satisfy declared argument choices."""
    defaults = load_yaml(role / "defaults" / "main.yml")
    specifications = load_yaml(role / "meta" / "argument_specs.yml")
    options = specifications["argument_specs"]["main"]["options"]

    for variable, specification in options.items():
        if variable not in defaults or "choices" not in specification:
            continue

        value = defaults[variable]
        choices = specification["choices"]

        if isinstance(value, str) and "{{" in value:
            continue

        if isinstance(value, list):
            assert all(item in choices for item in value), variable
        else:
            assert value in choices, variable


@pytest.mark.parametrize("role", COMPOSE_ROLES, ids=lambda role: role.name)
def test_role_compose_template_defines_services(role: Path) -> None:
    """Require container templates to define Compose services."""
    template = role / "templates" / "compose.yml.j2"

    if not template.is_file():
        template = role / "templates" / "docker-compose.yml.j2"

    content = template.read_text(encoding="utf-8")

    assert "services:" in content


@pytest.mark.parametrize("role", ROLES, ids=lambda role: role.name)
def test_role_yaml_files_are_valid(role: Path) -> None:
    """Validate YAML syntax throughout each role."""
    yaml_files = sorted(
        [
            *role.rglob("*.yml"),
            *role.rglob("*.yaml"),
        ]
    )

    for path in yaml_files:
        load_yaml(path)
