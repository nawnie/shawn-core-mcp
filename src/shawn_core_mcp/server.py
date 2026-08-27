"""Small dependency-free MCP server for the public Shawn Core control plane."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .specialists import KEYWORDS, SPECIALISTS

SERVER = "shawn-core"
VERSION = "0.1.0"
PROTOCOL = "2025-11-25"


class RequestError(ValueError):
    """An input error safe to return to an MCP client."""


def require_text(arguments: dict[str, Any], key: str, limit: int = 12000) -> str:
    value = arguments.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RequestError(f"{key} must be a non-empty string")
    value = value.strip()
    if len(value) > limit:
        raise RequestError(f"{key} exceeds {limit} characters")
    return value


def allowlisted_repo(arguments: dict[str, Any]) -> Path:
    raw = require_text(arguments, "repo_path", 1000)
    repo = Path(raw).expanduser().resolve()
    roots = [Path(item).expanduser().resolve() for item in os.environ.get("SHAWN_CORE_GIT_ROOTS", "").split(os.pathsep) if item]
    if not roots:
        raise RequestError("SHAWN_CORE_GIT_ROOTS must list an allowed local repository root")
    if not repo.is_dir() or not any(repo == root or root in repo.parents for root in roots):
        raise RequestError("repo_path must be an existing repository inside SHAWN_CORE_GIT_ROOTS")
    return repo


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(["git", "-C", str(repo), *args], text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=30)
    if completed.returncode:
        raise RequestError(completed.stderr.strip() or f"git {' '.join(args)} failed")
    return completed.stdout.strip()


def route(arguments: dict[str, Any]) -> dict[str, Any]:
    task = require_text(arguments, "task").casefold()
    for specialist, phrases in KEYWORDS.items():
        if any(phrase in task for phrase in phrases):
            return {"orchestrator": "Orchestrator", "specialist": specialist, "role": SPECIALISTS[specialist]["role"], "validation": "Return a bounded receipt to Orchestrator for acceptance or rerouting."}
    return {"orchestrator": "Orchestrator", "specialist": "orchestrator", "role": SPECIALISTS["orchestrator"]["role"], "validation": "Handle directly, then route only the missing capability during smoke or validation."}


def git_snapshot(arguments: dict[str, Any]) -> dict[str, Any]:
    repo = allowlisted_repo(arguments)
    return {"repo": git(repo, "rev-parse", "--show-toplevel"), "branch": git(repo, "branch", "--show-current"), "head": git(repo, "log", "-1", "--format=%H"), "subject": git(repo, "log", "-1", "--format=%s"), "status": git(repo, "status", "--short", "--branch")}


def changelog_intake(arguments: dict[str, Any]) -> dict[str, Any]:
    snapshot = git_snapshot(arguments)
    policy = SPECIALISTS["changelog"]["subprocess"]
    return {"specialist": "changelog", "phase": "start", "git_snapshot": snapshot, "atlas_cartographer": {"skill": "atlas-cartographer", "purpose": "retrieve or record a compact continuity card"}, "github": {"mention": "@github", "purpose": "read repository and pull-request context when the connector is available"}, "subprocess_policy": {**policy, "boundary": "The caller must enforce these limits. This MCP does not claim it can raise provider context ceilings."}, "end_of_task": "Call changelog_finalize with verified changes and receipts."}


def changelog_finalize(arguments: dict[str, Any]) -> dict[str, Any]:
    title = require_text(arguments, "title", 200)
    changes = arguments.get("changes", [])
    receipts = arguments.get("receipts", [])
    if not isinstance(changes, list) or not all(isinstance(item, str) and item.strip() for item in changes):
        raise RequestError("changes must be an array of non-empty strings")
    if not isinstance(receipts, list) or not all(isinstance(item, str) and item.strip() for item in receipts):
        raise RequestError("receipts must be an array of non-empty strings")
    body = "\n".join(f"- {item}" for item in changes)
    proof = "\n".join(f"- {item}" for item in receipts) or "- No receipt supplied"
    return {"specialist": "changelog", "phase": "end", "markdown": f"## {title}\n\n### Changed\n{body}\n\n### Verified\n{proof}\n", "acceptance": "Changelog is a record, not proof of deployment or publication."}


def atlas_continuity_record(arguments: dict[str, Any]) -> dict[str, Any]:
    """Write a compact, payload-free continuity card to an operator-selected root."""
    root_value = os.environ.get("SHAWN_CORE_CONTINUITY_HOME")
    if not root_value:
        raise RequestError("SHAWN_CORE_CONTINUITY_HOME must name a local continuity directory")
    root = Path(root_value).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    title = require_text(arguments, "title", 200)
    summary = require_text(arguments, "summary", 2000)
    source = require_text(arguments, "source", 1000)
    card = {"schema": "shawn-core.continuity-card.v1", "id": f"card-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}", "created_utc": datetime.now(timezone.utc).isoformat(), "title": title, "summary": summary, "source": source, "boundary": "Pointers and compact summaries only. Do not place secrets, raw prompts, or private records in cards."}
    destination = root / "cards.jsonl"
    with destination.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(card, sort_keys=True) + "\n")
    return {"specialist": "atlas-cartographer", "card": card, "path": str(destination)}


def git_commit(arguments: dict[str, Any]) -> dict[str, Any]:
    repo = allowlisted_repo(arguments)
    message = require_text(arguments, "message", 200)
    paths = arguments.get("paths", [])
    if not isinstance(paths, list) or not paths or not all(isinstance(path, str) and path and not Path(path).is_absolute() for path in paths):
        raise RequestError("paths must be a non-empty array of relative paths")
    if arguments.get("execute") is not True:
        return {"status": "planned", "repo": str(repo), "paths": paths, "message": message, "next_step": "Set execute=true after reviewing the staged diff."}
    git(repo, "add", "--", *paths)
    cached = git(repo, "diff", "--cached", "--check")
    if cached:
        raise RequestError(cached)
    git(repo, "commit", "-m", message)
    return {"status": "committed", "repo": str(repo), "head": git(repo, "rev-parse", "HEAD")}


def token_master_audit(_: dict[str, Any]) -> dict[str, Any]:
    return {"specialist": "token-master", "boundary": "Read-only recommendations. Provider context windows and host configuration are controlled outside this MCP.", "checks": ["resident MCP schemas", "skill discovery footprint", "compaction policy", "task continuity coverage"]}


def spec(description: str, handler: Any, properties: dict[str, Any], required: list[str] | None = None, read_only: bool = True) -> dict[str, Any]:
    return {"description": description, "handler": handler, "inputSchema": {"type": "object", "properties": properties, "required": required or [], "additionalProperties": False}, "annotations": {"readOnlyHint": read_only, "destructiveHint": False, "idempotentHint": read_only, "openWorldHint": False}}


TOOLS = {
    "orchestrator_context": spec("Return the public specialist registry and its ownership boundaries.", lambda _: {"orchestrator": "Orchestrator", "specialists": SPECIALISTS}, {}),
    "orchestrator_route": spec("Route a task or keep it with Orchestrator until a smoke or validation gate identifies a missing capability.", route, {"task": {"type": "string", "maxLength": 12000}}, ["task"]),
    "token_master_audit": spec("Return Token Master's read-only audit contract.", token_master_audit, {}),
    "personal_git_snapshot": spec("Read status and latest commit from an allowlisted local Git repository.", git_snapshot, {"repo_path": {"type": "string", "maxLength": 1000}}, ["repo_path"]),
    "changelog_intake": spec("Start the Changelog specialist with a Git snapshot, Atlas Cartographer handoff, @github handoff, and Luna execution contract.", changelog_intake, {"repo_path": {"type": "string", "maxLength": 1000}}, ["repo_path"]),
    "changelog_finalize": spec("Render a receipt-backed end-of-task changelog entry.", changelog_finalize, {"title": {"type": "string", "maxLength": 200}, "changes": {"type": "array", "items": {"type": "string"}}, "receipts": {"type": "array", "items": {"type": "string"}}}, ["title", "changes"]),
    "atlas_continuity_record": spec("Write a compact local Atlas Cartographer continuity card beneath SHAWN_CORE_CONTINUITY_HOME.", atlas_continuity_record, {"title": {"type": "string", "maxLength": 200}, "summary": {"type": "string", "maxLength": 2000}, "source": {"type": "string", "maxLength": 1000}}, ["title", "summary", "source"], read_only=False),
    "personal_git_commit": spec("Plan or explicitly create a local commit inside an allowlisted Git root. This never pushes or publishes.", git_commit, {"repo_path": {"type": "string", "maxLength": 1000}, "paths": {"type": "array", "items": {"type": "string"}}, "message": {"type": "string", "maxLength": 200}, "execute": {"type": "boolean", "default": False}}, ["repo_path", "paths", "message"], read_only=False),
}


def respond(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def handle(request: dict[str, Any]) -> dict[str, Any] | None:
    request_id, method, params = request.get("id"), request.get("method"), request.get("params") or {}
    if method == "initialize":
        return respond(request_id, {"protocolVersion": PROTOCOL, "capabilities": {"tools": {"listChanged": False}}, "serverInfo": {"name": SERVER, "version": VERSION}, "instructions": "Orchestrator owns the whole problem. Changelog runs a light intake at task start and records receipt-backed changes at task end."})
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return respond(request_id, {"tools": [{key: value for key, value in tool.items() if key != "handler"} | {"name": name} for name, tool in TOOLS.items()]})
    if method == "tools/call":
        name, arguments = params.get("name"), params.get("arguments") or {}
        if name not in TOOLS or not isinstance(arguments, dict):
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32602, "message": "unknown tool or invalid arguments"}}
        try:
            content = TOOLS[name]["handler"](arguments)
            return respond(request_id, {"content": [{"type": "text", "text": json.dumps(content, sort_keys=True)}], "structuredContent": content, "isError": False})
        except RequestError as error:
            return respond(request_id, {"content": [{"type": "text", "text": str(error)}], "isError": True})
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "method not found"}}


def main() -> None:
    for line in sys.stdin:
        try:
            request = json.loads(line)
            response = handle(request) if isinstance(request, dict) else None
            if response is not None:
                print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            print(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}), flush=True)


if __name__ == "__main__":
    main()
