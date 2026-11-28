# SPDX-FileCopyrightText: Copyright © 2026, Jared W. Cook
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Relay selected FreeLLMAPI or LongMemory tools over an MCP stdio connection."""

import json
import os
import sys
from http.client import HTTPConnection, HTTPException, HTTPResponse, HTTPSConnection
from urllib.parse import urlsplit

FREELLMAPI_TOOLS = frozenset({"ask_freellmapi", "list_models", "healthcheck"})
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


def read_event(response: HTTPResponse, request_id: object) -> dict:
    """Read the matching SSE event without waiting for the stream to close."""
    remaining = MAX_MESSAGE
    event = []
    while remaining > 0:
        line = response.readline(remaining + 1)
        remaining -= len(line)
        if not line or remaining < 0:
            break
        if line.startswith(b"data:"):
            event.append(line[5:].removeprefix(b" ").rstrip(b"\r\n"))
        elif line in {b"\n", b"\r\n"} and event:
            reply = json.loads(b"\n".join(event))
            if isinstance(reply, dict) and reply.get("id") == request_id:
                return reply
            event.clear()
    raise ValueError("No matching MCP event within the response limit")


def read_response(
    response: HTTPResponse, message: dict, service: str, tool_names: frozenset[str]
) -> dict | None:
    """Validate the upstream response and limit the exposed tool list."""
    request_id = message.get("id")
    if response.status == 202 and "id" not in message:
        return None
    if response.status != 200:
        return rpc_error(
            request_id, -32000, f"{service} returned HTTP {response.status}"
        )
    if response.getheader("Content-Type", "").split(";", 1)[0] == "text/event-stream":
        reply = read_event(response, request_id)
    else:
        payload = response.read(MAX_MESSAGE + 1)
        if len(payload) > MAX_MESSAGE:
            return rpc_error(
                request_id, -32000, f"{service} response exceeded the relay limit"
            )
        reply = json.loads(payload)
    if not isinstance(reply, dict) or reply.get("id") != request_id:
        return rpc_error(request_id, -32000, f"Invalid {service} JSON-RPC response")
    result = reply.get("result")
    if isinstance(result, dict):
        if message["method"] == "tools/list":
            result["tools"] = [
                tool
                for tool in result.get("tools", [])
                if isinstance(tool, dict) and tool.get("name") in tool_names
            ]
        elif message["method"] == "initialize":
            result.pop("instructions", None)
    return reply


def relay(
    message: dict, endpoint: str, api_key: str, service: str, tool_names: frozenset[str]
) -> dict | None:
    """Send one request to the fixed endpoint. Never follow redirects."""
    request_id = message.get("id")
    method = message.get("method")
    if not isinstance(method, str) or method not in RPC_METHODS:
        return rpc_error(request_id, -32601, "Method unavailable through this relay")
    if method == "tools/call":
        params = message.get("params")
        name = params.get("name") if isinstance(params, dict) else None
        if not isinstance(name, str) or name not in tool_names:
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
        return read_response(connection.getresponse(), message, service, tool_names)
    except (HTTPException, OSError, TypeError, ValueError):
        return rpc_error(request_id, -32000, f"{service} MCP request failed")
    finally:
        if connection is not None:
            connection.close()


def serve(
    endpoint: str, api_key: str, service: str, tool_names: frozenset[str]
) -> None:
    """Read newline-delimited MCP messages and keep stdout reserved for JSON."""
    while line := sys.stdin.buffer.readline(MAX_MESSAGE + 1):
        if len(line) > MAX_MESSAGE:
            print(f"{service} relay input exceeded the message limit", file=sys.stderr)
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
        reply = relay(message, endpoint, api_key, service, tool_names)
        if reply is not None and "id" in message:
            print(json.dumps(reply, ensure_ascii=True), flush=True)


def main() -> int:
    """Validate startup options before accepting input."""
    if sys.argv[1:] == ["longmemory"]:
        service = "LongMemory"
        tool_names = frozenset(
            name
            for name in os.environ.get("LONGMEMORY_TOOLS", "").split(",")
            if name.startswith("longmemory_")
        )
    elif len(sys.argv) == 1:
        service = "FreeLLMAPI"
        tool_names = FREELLMAPI_TOOLS
    else:
        print("Unsupported MCP relay service", file=sys.stderr)
        return 1
    prefix = service.upper()
    endpoint = os.environ.get(f"{prefix}_MCP_URL", "")
    parsed = urlsplit(endpoint)
    api_key = os.environ.get(f"{prefix}_API_KEY", "")
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.path != "/mcp"
        or parsed.query
        or parsed.fragment
        or not api_key
        or not tool_names
    ):
        print(f"Set the {service} MCP endpoint, API key, and tools", file=sys.stderr)
        return 1
    serve(endpoint, api_key, service, tool_names)
    return 0


if __name__ == "__main__":
    sys.exit(main())
