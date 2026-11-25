# SPDX-FileCopyrightText: Copyright © 2026, Jared W. Cook
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Relay selected FreeLLMAPI JSON-RPC tools over an MCP stdio connection."""

import json
import os
import sys
from http.client import HTTPConnection, HTTPException, HTTPResponse, HTTPSConnection
from urllib.parse import urlsplit

TOOL_NAMES = frozenset({"ask_freellmapi", "list_models", "healthcheck"})
RPC_METHODS = frozenset(
    {"initialize", "notifications/initialized", "ping", "tools/list", "tools/call"}
)
MAX_MESSAGE = 8 * 1024 * 1024


def rpc_error(request_id: object, code: int, message: str) -> dict:
    """Return a compact JSON-RPC error without exposing upstream secrets."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }


def read_response(response: HTTPResponse, message: dict) -> dict | None:
    """Validate the upstream response and limit the exposed tool list."""
    request_id = message.get("id")
    if response.status == 202 and "id" not in message:
        return None
    if response.status != 200:
        return rpc_error(
            request_id, -32000, f"FreeLLMAPI returned HTTP {response.status}"
        )
    payload = response.read(MAX_MESSAGE + 1)
    if len(payload) > MAX_MESSAGE:
        return rpc_error(
            request_id, -32000, "FreeLLMAPI response exceeded the relay limit"
        )
    reply = json.loads(payload)
    if not isinstance(reply, dict) or reply.get("id") != request_id:
        return rpc_error(request_id, -32000, "Invalid FreeLLMAPI JSON-RPC response")
    result = reply.get("result")
    if isinstance(result, dict):
        if message["method"] == "tools/list":
            result["tools"] = [
                tool
                for tool in result.get("tools", [])
                if isinstance(tool, dict) and tool.get("name") in TOOL_NAMES
            ]
        elif message["method"] == "initialize":
            result.pop("instructions", None)
    return reply


def relay(message: dict, endpoint: str, api_key: str) -> dict | None:
    """Send one request to the fixed endpoint. Never follow redirects."""
    request_id = message.get("id")
    method = message.get("method")
    if not isinstance(method, str) or method not in RPC_METHODS:
        return rpc_error(request_id, -32601, "Method unavailable through this relay")
    if method == "tools/call":
        params = message.get("params")
        name = params.get("name") if isinstance(params, dict) else None
        if not isinstance(name, str) or name not in TOOL_NAMES:
            return rpc_error(request_id, -32602, "Tool unavailable through this relay")

    connection = None
    try:
        upstream = urlsplit(endpoint)
        connection_type = (
            HTTPSConnection if upstream.scheme == "https" else HTTPConnection
        )
        connection = connection_type(upstream.hostname, upstream.port, timeout=120)
        connection.request(
            "POST",
            "/mcp",
            body=json.dumps(message).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
        )
        return read_response(connection.getresponse(), message)
    except (HTTPException, OSError, TypeError, ValueError):
        return rpc_error(request_id, -32000, "FreeLLMAPI MCP request failed")
    finally:
        if connection is not None:
            connection.close()


def serve(endpoint: str, api_key: str) -> None:
    """Read newline-delimited MCP messages and keep stdout reserved for JSON."""
    while line := sys.stdin.buffer.readline(MAX_MESSAGE + 1):
        if len(line) > MAX_MESSAGE:
            print("FreeLLMAPI relay input exceeded the message limit", file=sys.stderr)
            break
        try:
            message = json.loads(line)
        except ValueError:
            print(json.dumps(rpc_error(None, -32700, "Invalid JSON")), flush=True)
            continue
        if not isinstance(message, dict):
            print(
                json.dumps(rpc_error(None, -32600, "Expected a JSON-RPC object")),
                flush=True,
            )
            continue
        reply = relay(message, endpoint, api_key)
        if reply is not None and "id" in message:
            print(json.dumps(reply, ensure_ascii=True), flush=True)


def main() -> int:
    """Validate startup options before accepting input."""
    endpoint = os.environ.get("FREELLMAPI_MCP_URL", "")
    parsed = urlsplit(endpoint)
    api_key = os.environ.get("FREELLMAPI_API_KEY", "")
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.path != "/mcp"
        or parsed.query
        or parsed.fragment
        or not api_key
    ):
        print("Set a FreeLLMAPI MCP endpoint and unified API key", file=sys.stderr)
        return 1
    serve(endpoint, api_key)
    return 0


if __name__ == "__main__":
    sys.exit(main())
