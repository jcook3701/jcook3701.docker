# AGENTS.md — Development Instructions

## Project Overview

This repository is the `jcook3701.docker` Ansible Galaxy collection.

It contains Ansible roles for deploying and managing containerized
applications and related infrastructure.

The collection is maintained by Jared W. Cook.

This document defines repository-wide development rules for AI coding
assistants, including OpenAI Codex.

## 1. Primary Rule: Preserve Existing Project Standards

**The existing project architecture, syntax, formatting, and established
patterns take precedence over an AI assistant's preferences.**

- Read the relevant existing files before proposing or implementing changes.
- Follow the patterns already established in the target role.
- Preserve working syntax, even when another implementation seems cleaner.
- Do not refactor code simply to make it shorter or more efficient.
- Do not remove existing variables, options, tasks, or functionality
  unless explicitly requested or technically necessary.
- Do not modify unrelated files or neighboring roles.
- Do not replace an established project pattern with a new convention
  without explaining the necessity.
- If a different approach is required for correctness, explain why and
  limit the change to what is necessary.
- Present optional improvements as suggestions, not automatic changes.
- Respect explicit user decisions, even when other approaches are valid.

**When in doubt, preserve the existing implementation.**

An architectural improvement is not authorization for unrelated changes.

## 2. Source of Truth and Change Scope

Before modifying an existing role:

1. Inspect its current files and directory structure.
2. Inspect related role defaults, variables, templates, and task files.
3. Review its `meta/argument_specs.yml` and `README.md`.
4. Check relevant repository linting and formatting configuration.
5. Identify the smallest set of changes required by the request.

The current working tree is authoritative.

Do not assume that a GitHub branch, cached file, generated example,
or previous conversation contains the latest local changes.

Do not overwrite uncommitted user changes.

Do not revert or modify changes made by another developer or agent unless
the user explicitly requests it.

Do not create, delete, rename, or reorganize files unnecessarily.

Do not make unrelated formatting changes while implementing a feature.

Do not commit, push, merge, release, or deploy without authorization.

## 3. Ansible Role Architecture

Preserve the architecture already implemented by each role.

Common role components include:

- `defaults/main.yml`
- `vars/main.yml`
- `tasks/main.yml`
- `tasks/state/`
- `tasks/configure/`
- `tasks/post_processing/`
- `handlers/main.yml`
- `templates/`
- `meta/argument_specs.yml`
- `README.md`

Do not automatically create every directory for every role.
Add files only when required.

Preserve existing lifecycle conventions:

- `present`
- `absent`
- `teardown`

Do not change the behavior or meaning of these states.

Preserve the role's existing task delegation, inclusion, and import patterns.

Container lifecycle management should continue using the established
`jcook3701.utils.container_engine` integration where already implemented.

Do not replace that architecture with ad hoc container commands or a
different orchestration framework.

Application administration commands may use the appropriate application
CLI when needed.

Keep configuration, installation, cleanup, and post-processing responsibilities
separated according to the existing role architecture.

Do not combine unrelated deployment responsibilities into one role.

Docker, Podman, Kubernetes, Helm, and KIND are distinct concerns.
Do not introduce one into another without an explicit requirement.

If a separate role is the correct architectural boundary, propose it
before implementing the change.

## 4. YAML Formatting Standards

Follow the repository's `.yamllint` configuration.

- Use two-space indentation unless an existing file requires otherwise.
- Use double quotes for quoted YAML strings.
- Preserve intentionally unquoted YAML booleans, numbers, and values.
- Include the YAML document-start marker (`---`).
- Do not introduce duplicate YAML keys.
- Keep source lines within 120 characters.
- Preserve the existing blank-line and section-comment formatting.
- Do not introduce unnecessary YAML anchors or complex expressions.
- Use readable multiline expressions where appropriate.
- Do not reformat unrelated code while editing a file.

Existing project conventions take precedence over stylistic preferences.

Do not convert quoted values to unquoted values, or vice versa,
without a specific technical reason.

## 5. SPDX and Licensing Headers

Preserve the existing SPDX and license-header conventions.

For new Ansible YAML role files, use the established header:

    # SPDX-FileCopyrightText: Copyright © 2026, Jared W. Cook
    # SPDX-License-Identifier: AGPL-3.0-or-later
    ---

Do not insert blank lines before the first header line.

Do not remove existing full AGPL license headers from files that use them.

Do not replace the project's copyright attribution or license identifiers.

Match the conventions of the surrounding files when adding a new file.

## 6. Jinja2 Template Standards

All new Jinja2 templates must follow the established template pattern.

Required elements:

1. The complete Jinja2 comment containing the project license header.
2. The template's filename and role identification.
3. The existing AGPL license text.
4. A named Jinja2 macro containing the generated output.
5. The generated-file SPDX header inside the macro.
6. The generated-file Ansible notice where appropriate.
7. The macro invocation at the end of the template.

Match the existing role's macro naming and whitespace-control conventions.

For example, follow the patterns used by:

- `templates/compose.yml.j2`
- `templates/headscale-config.yml.j2`
- `templates/headplane-config.yml.j2`

Preserve actual template filenames.

Do not invent new filenames or silently rename templates.

Use the existing Jinja2 formatting conventions.

Use `to_json` where established for safely quoting generated YAML strings.

Ensure that generated YAML remains valid after rendering.

Do not create a template without the expected macro wrapper.

## 7. Variables and Default Values

Preserve the project's variable naming and fallback conventions.

- Use descriptive variables prefixed with the role's existing prefix.
- Follow existing variable names rather than introducing synonyms.
- Do not rename variables without an explicit requirement.
- Add new configurable behavior to `defaults/main.yml` where appropriate.
- Follow existing grouped section comments and variable organization.
- Use `| default(...)` consistently with neighboring code.
- Preserve existing multiline Jinja expressions.
- Use explicit, human-readable fallback values.
- Use complete absolute fallback paths for filesystem paths.
- Do not simplify existing path expressions merely for brevity.
- Keep directory mappings and file mappings in their established structures.
- Do not create duplicate sources of truth for the same setting.
- Do not hardcode application settings that should reasonably be configurable.
- Do not introduce variables for functionality that has not been implemented.

A fallback should remain understandable without tracing several levels
of unrelated variables.

Readability and consistency are more important than reducing character count.

### Configuration Ownership

Ansible-managed configuration remains authoritative by default.

If an application must edit its configuration through a web interface,
explicitly address the ownership conflict between that application and
Ansible before changing file permissions or template overwrite behavior.

Do not silently transfer configuration ownership.

## 8. Argument Specifications

When adding, removing, or changing public role variables, update
`meta/argument_specs.yml` accordingly.

Maintain consistency between:

- `defaults/main.yml`
- `meta/argument_specs.yml`
- Role templates and tasks
- The role's `README.md`

Use appropriate Ansible argument types.

Document choices when values are restricted.

Preserve existing descriptions and defaults unless the request requires changes.

Do not invent validation restrictions without a technical requirement.

Do not add unnecessary assertion tasks to compensate for incomplete design.

## 9. Ansible Tasks and Handlers

Use fully qualified collection names for Ansible modules.

Examples:

- `ansible.builtin.file`
- `ansible.builtin.template`
- `ansible.builtin.command`
- `ansible.builtin.include_tasks`
- `community.docker.docker_container`

Follow the module and task patterns already present in the role.

Every Ansible loop must explicitly define:

- `loop_control`
- `loop_var`
- `label`

Use descriptive task names consistent with the surrounding tasks.

Prefer Ansible modules over shell commands when appropriate, without
unnecessarily replacing working project-specific implementations.

Use `notify` and handlers for follow-up operations triggered by task changes.

Avoid patterns that trigger `ansible-lint[no-handler]`.

Do not introduce unnecessary `changed_when: true` or `changed_when: false`.

Use `changed_when` where required to accurately describe command behavior
and satisfy the applicable linting rules.

Preserve existing handlers and their names.

Do not create duplicate container deployment or restart paths.

## 10. Idempotence and Lifecycle Safety

All Ansible roles must be designed for repeated execution.

- Avoid recreating resources that already exist.
- Check for existing resources before provisioning them.
- Preserve persistent application data across normal deployments.
- Preserve generated credentials unless replacement is explicitly requested.
- Use explicit variables for destructive or replacement operations.
- Do not rotate or revoke credentials as a side effect of unrelated changes.
- Ensure replacement logic does not unnecessarily interrupt existing clients.
- Keep `absent` and `teardown` behavior consistent with the existing role.

When implementing replacement flags, default them to `false` unless
the user explicitly requests otherwise.

Document what happens when a replacement flag remains enabled.

Do not treat a file's existence as proof that an expiring credential remains valid.

## 11. Security and Secrets

Never hardcode personal IP addresses, API keys, passwords, or tokens
into reusable public roles.

Keep deployment-specific settings in the appropriate configuration repository.

Prefer existing Ansible Vault conventions for user-specific secrets.

Generated credentials must be stored securely and should not be exposed
in normal task logs.

Use `no_log: true` for tasks handling sensitive values.

Use restrictive filesystem permissions when storing secrets.

Do not expose the Docker socket, privileged services, or administrative
interfaces without explaining the security implications.

A read-only bind mount of the Docker socket does not make Docker API
operations read-only.

Do not broaden network exposure or filesystem permissions without a
functional requirement.

Do not assume an internal container port is the same as a public-facing port.

Keep host binding, container ports, and public service URLs distinct.

Do not embed proxy port numbers into public URLs unless the externally
reachable service actually requires them.

Avoid hardcoding deployment-specific hostnames in public roles.

## 12. Docker Compose and Container Configuration

Preserve the existing Compose template structure and service ordering.

Use the established image, container name, port, volume, network,
restart policy, and pull policy variables.

Do not change working port mappings or interface bindings without a requirement.

Do not introduce extra services without explaining their purpose.

Optional services must have explicit enable/disable variables.

An enabled feature must include the permissions, mounts, dependencies,
and application configuration required for it to function.

Do not introduce a switch that enables only part of a feature.

Preserve existing persistent volumes and application data locations.

Avoid exposing administrative endpoints unnecessarily.

Use Docker service names and shared networks where appropriate instead
of hardcoded host IP addresses.

Do not assume Nginx, Apache, or another reverse proxy has already been
installed or configured.

## 13. Documentation Requirements

Keep the role's `README.md` synchronized with implemented functionality.

For new role variables, update the existing Role Variables table.

Preserve the established Markdown table columns:

    | Variable | Type | Description / Choices | Default |

Do not rewrite the full README when only a few lines need updating.

Keep documentation consistent with actual implementation.

Do not claim that optional features work unless their supporting
configuration and dependencies are implemented.

Document required deployment prerequisites and important limitations.

Do not add manual installation steps for functionality that the user
explicitly requested to automate.

When manual intervention is inherently required, explain why.

Use complete file content when the user explicitly requests complete files.

Provide code directly in the chat when requested instead of creating archives.

## 14. Linting and Validation

Use the repository's existing linting and validation configurations
as the source of truth.

Relevant files include:

- `.ansible-lint`
- `.yamllint`
- `.pre-commit-config.yaml`
- `cspell.json`
- `pyproject.toml`, where applicable
- `Makefile`, where applicable

Do not invent a separate formatting or linting standard.

Before reporting completion, run applicable checks where tools are available.

For Ansible changes, consider:

- Ansible syntax validation
- `ansible-lint`
- `yamllint`
- Jinja2 template syntax validation
- Rendered YAML validation
- Docker Compose configuration validation, where applicable

For documentation changes, follow the existing spelling and Markdown checks.

For Python changes, follow the configured Python linting and formatting tools.

Do not automatically run lint auto-fix commands that may rewrite
unrelated files.

Do not add lint suppressions without explaining why they are necessary.

Do not update `cspell.json` indiscriminately to hide spelling mistakes.

Do not claim validation passed unless it actually ran successfully.

Report unrun checks and remaining errors explicitly.

## 15. Changes to Existing Files

Prefer surgical changes over full rewrites.

When modifying an existing file:

1. Read the current implementation.
2. Identify the exact required changes.
3. Preserve everything outside the requested scope.
4. Update dependent files only when necessary.
5. Inspect the resulting diff for unrelated modifications.
6. Validate the changed functionality.

Do not remove commented-out configuration or existing TODOs without
a specific reason.

Do not rename existing paths, variables, tasks, or templates for consistency
with a newly invented convention.

If an existing implementation has a real defect, explain the defect and
make the smallest correction that resolves it.

Do not repeatedly change the implementation approach after the user
has already selected one.

## 16. Communication and Development Workflow

Before making significant architectural changes, explain:

- What needs to change.
- Why the existing approach is insufficient.
- Which files will be affected.
- Whether the change impacts existing behavior or compatibility.

For routine, narrowly scoped changes, proceed without unnecessary
confirmation questions.

Distinguish between required changes and optional suggestions.

Never describe untested code as fully working.

Do not say files were written, deployed, committed, or validated
unless those operations actually occurred.

When work cannot be completed, report exactly what remains incomplete.

Do not claim success based only on generating code.

Do not introduce unrelated feature work while fixing a specific error.

Do not repeatedly ask for information already available in the project.

Do not require the maintainer to repeatedly correct established
formatting or architectural conventions.

## 17. Final Review Checklist

Before presenting changes, verify:

- Existing architectural patterns are preserved.
- No unrelated changes were introduced.
- Variable naming follows the role's conventions.
- Default filters and absolute fallback paths follow existing patterns.
- YAML formatting matches the repository configuration.
- SPDX headers are present and correct.
- Jinja2 templates use the required full headers and macro wrappers.
- Every Ansible loop has explicit loop controls.
- Changed-triggered operations use appropriate handlers.
- New public variables appear in argument specs and README documentation.
- Optional features include all required supporting functionality.
- No personal deployment values or credentials were hardcoded.
- Persistent data and credentials are preserved where required.
- Applicable validation was performed and remaining gaps were disclosed.

**If a proposed change violates the existing project standards, stop and
reconsider the implementation before modifying the code.**
