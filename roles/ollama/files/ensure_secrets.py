#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright © 2026, Jared W. Cook
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Ensure Ollama stack secrets persist in a private Compose .env file.

Existing nonempty values and unrelated .env settings are preserved. New secrets
are securely generated and written atomically with mode 0600.
"""

from __future__ import annotations

import os
from pathlib import Path
import secrets
import sys
import tempfile

REQUIRED = (
    "OLLAMA_WEBUI_SECRET_KEY",
    "OLLAMA_SEARXNG_SECRET_KEY",
    "OLLAMA_MCP_GATEWAY_AUTH_TOKEN",
)
INSECURE = {
    "change_this_to_a_secure_random_string_in_production",
    "change_me",
    "changeme",
}


def main() -> int:
    """Create missing keys without rotating already-provisioned credentials."""
    if len(sys.argv) != 2:
        print("usage: ensure_secrets.py /absolute/path/to/.env", file=sys.stderr)
        return 2

    destination = Path(sys.argv[1])
    if not destination.is_absolute() or destination.name != ".env":
        print("Expected an absolute path ending with .env", file=sys.stderr)
        return 2

    os.umask(0o077)
    try:
        if destination.is_symlink():
            raise ValueError("Refusing to modify a symlinked secrets file")
        original = (
            destination.read_text(encoding="utf-8") if destination.exists() else ""
        )
        lines = original.splitlines(keepends=True)
        present: dict[str, str] = {}
        for raw in lines:
            if raw.lstrip().startswith("#") or "=" not in raw:
                continue
            name, value = raw.split("=", 1)
            if name in REQUIRED:
                present[name] = value.strip().strip("\"'")

        changed = False
        for key in REQUIRED:
            existing = present.get(key)
            if not existing or existing.lower() in INSECURE:
                value = secrets.token_hex(32)
                for i, line in enumerate(lines):
                    if line.startswith(key + "="):
                        lines[i] = f"{key}={value}\\n".replace("\\n", "\n")
                        break
                else:
                    if lines and not lines[-1].endswith("\n"):
                        lines.append("\n")
                    lines.append(f"{key}={value}\n")
                changed = True

        if changed or not destination.exists():
            fd, tmp_name = tempfile.mkstemp(
                prefix=".ollama-env-", dir=destination.parent
            )
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as output:
                    output.writelines(lines)
                os.chmod(tmp_name, 0o600)
                os.replace(tmp_name, destination)
            finally:
                if os.path.exists(tmp_name):
                    os.unlink(tmp_name)
        if destination.stat().st_mode & 0o077:
            os.chmod(destination, 0o600)
            changed = True
    except (OSError, ValueError) as error:
        print(f"Could not initialize Ollama secrets: {error}", file=sys.stderr)
        return 1

    print("changed" if changed else "ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
