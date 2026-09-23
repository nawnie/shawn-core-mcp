"""Public specialist registry shared by routing and MCP responses."""

from __future__ import annotations

SPECIALISTS = {
    "orchestrator": {"role": "whole-problem ownership, concise cross-domain reasoning, routing, validation, and recovery", "aliases": ["@orchestrator", "orchestrator"]},
    "mok-router": {"role": "resource-aware local model and backend selection, dispatch, fallback, and execution receipts", "aliases": ["@mok", "@mok-router", "@router"]},
    "pgv": {"role": "hospitality, property, acquisition, construction, and operations", "aliases": ["@pgv"]},
    "ted": {"role": "finance, business economics, and CFO controls", "aliases": ["@ted"]},
    "victoria": {"role": "marketing, SEO, campaigns, and discovery", "aliases": ["@victoria"]},
    "agent-t": {"role": "security, compliance readiness, and production assurance", "aliases": ["@agent-t"]},
    "verifier": {"role": "independent falsification and acceptance evidence", "aliases": ["@verifier"]},
    "rocky-advisor": {"role": "opt-in owner and operator advisory", "aliases": ["@rocky"]},
    "researcher": {"role": "research, source grading, and knowledge proposals", "aliases": ["@researcher"]},
    "legal-readiness": {"role": "document completeness and counsel handoff", "aliases": ["@legal-readiness"]},
    "cad": {"role": "mechanical CAD, geometry, manufacturing, Blender, and Unreal validation", "aliases": ["@cad"]},
    "wren": {"role": "sites, briefing pages, and design validation", "aliases": ["@wren"]},
    "carl": {"role": "Bethesda Creation Kit, xEdit, dependency, packaging, and crash isolation", "aliases": ["@carl"]},
    "al": {"role": "AI and machine learning architecture, models, training, and inference", "aliases": ["@al"]},
    "token-master": {"role": "token efficiency, context retention, and compaction policy research", "aliases": ["@token-master"]},
    "changelog": {"role": "start-of-task continuity intake and end-of-task receipt-backed changelog", "aliases": ["@changelog"], "subprocess": {"model": "gpt-5.6-luna", "compact_at_tokens": 64000, "hard_context_limit_tokens": 100000}},
}
KEYWORDS = {
    "mok-router": ("router", "routing", "backend", "model selection", "vram", "ollama", "llama.cpp", "vllm", "fallback"),
    "changelog": ("changelog", "worklog", "release notes", "what changed"),
    "token-master": ("token", "context", "compaction", "compression"),
    "carl": ("creation kit", "xedit", "starfield", "skyrim", "fallout", "papyrus", "sfse", "skse", "f4se"),
    "cad": ("blender", "unreal", "mesh", "cad", "3d print"),
    "al": ("machine learning", "ai model", "training", "inference", "quantization"),
    "victoria": ("marketing", "seo", "campaign", "sitemap"),
    "ted": ("budget", "funding", "finance", "economics"),
    "agent-t": ("security", "vulnerability", "compliance", "audit"),
}

# This is contract coverage, not a claim that every specialist has identical
# depth in every domain. It gives every public role the same intake, evidence,
# handoff, and boundary baseline before specialist-specific tooling is added.
PUBLIC_CONTRACT = {
    "intake": "Orchestrator keeps a concise domain summary and opens a specialist lane only when deeper proof is needed.",
    "evidence": "Return inspected inputs, deterministic checks, and explicit unknowns.",
    "handoff": "Return unresolved cross-domain work to Orchestrator for rerouting.",
    "boundary": "Do not publish, spend, expose credentials, or claim runtime success without explicit authorization and receipts.",
    "public_contract_completeness_out_of_10": 8,
}

for specialist in SPECIALISTS.values():
    specialist["public_contract"] = PUBLIC_CONTRACT.copy()
