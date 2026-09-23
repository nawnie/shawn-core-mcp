# Shawn Core MCP

Shawn Core MCP is a local-first JSON-RPC MCP server for practical specialist
routing, continuity, and evidence-based handoffs.

The public orchestrator is named **Orchestrator**. It retains a concise map of
every specialist for ordinary tasks and escalates only when deeper proof is
needed. That keeps routing helpful without turning every small request into a
multi-agent ceremony.

Every public specialist has the same 8/10 contract baseline: intake, evidence,
handoff, and public boundary. This measures public operational completeness,
not a claim that every domain has identical technical depth.

## Included core tools

- `orchestrator_route`: return the first specialist and validation plan, including the `mok-router` lane for resource-aware model/backend dispatch.
- `token_master_audit`: inventory token-relevant local configuration facts.
- `changelog_intake`: start a lightweight changelog subprocess plan with an
  Atlas Cartographer handoff, a local Git snapshot, and an `@github` handoff.
- `changelog_finalize`: render a receipt-backed changelog entry at task end.
- `atlas_continuity_record`: write a compact, payload-free Cartographer card
  beneath an operator-selected local continuity root.
- `personal_git_snapshot`: read status and latest commit from an allowlisted
  local Git repository.
- `personal_git_commit`: make an explicit local commit only within roots
  allowlisted by `SHAWN_CORE_GIT_ROOTS`.

The Changelog specialist is configured for `gpt-5.6-luna`, a 64,000-token
compaction target, and a 100,000-token hard ceiling. Those are an execution
contract for the host that runs the subprocess, not an attempt to claim that
an MCP can raise a provider's actual context window.

## Run locally

```powershell
python -m unittest discover -s tests -v
$env:SHAWN_CORE_GIT_ROOTS = "<local-repository-root>"
python -m shawn_core_mcp.server
```

Send newline-delimited JSON-RPC requests over standard input. The server is
local only. It does not open a port, read credentials, change model settings,
or publish to GitHub.

## Public boundary

This repository intentionally excludes personal configuration, model and
dataset paths, cloud credentials, client material, generated outputs, and
private specialist implementations. GitHub publication is performed by the
operator, not by the MCP.

## MoK router boundary

[Model Operating Kernel](https://github.com/nawnie/Model-Operating-Kernel) is the dedicated router/runtime specialist beneath Orchestrator. Orchestrator owns the whole user problem; MoK owns model/backend selection, resource checks, dispatch, bounded fallback, and execution receipts. Kairo remains a separate reasoning/research line and may be routed to as an expert rather than becoming the routing layer itself.
