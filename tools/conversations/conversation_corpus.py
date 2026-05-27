"""Deterministic conversation-corpus intake helpers.

This module treats docs/archive/conversations as archival evidence. It builds
derived inventory, reader, audit, promotion, and wiki surfaces without editing
imported conversation package files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


REVIEW_DATE = "2026-05-28"
CORPUS_ROOT = Path("docs/archive/conversations")
MANAGED_DIRS = {"_intake", "_reader", "_wiki", "_audit", "_promotion", "_synthesis", "__unsorted"}
HEADER_BINDING = (
    "`docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, "
    "`AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, "
    "`docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`"
)

GENERATED_MARKDOWN_ROOT_FILES = {"README.md", "INDEX.md"}
GENERATED_MARKDOWN_DIRS = {"_intake", "_reader", "_wiki", "_audit", "_promotion", "_synthesis"}

SYNTHESIS_TOPIC_EXPLANATIONS = {
    "architecture": "system boundaries, product shape, engine/game/client/server separation, and repository structure",
    "workbench": "operator-facing validation, evidence, inspection, and later authoring surfaces",
    "determinism": "replay, ordering, proof, fixed identity, RNG discipline, and thread-count invariance",
    "platform": "runtime shell, platform adapter, renderer boundary, operating-system support, and portability",
    "release": "version identity, packaging, setup, update, publication, and release-control concerns",
    "worldgen": "world, universe, celestial, terrain, chronology, and large-scale reality modeling",
    "tooling": "Codex/AIDE/XStack/TestX/RepoX/AuditX tooling and patch workflow",
    "setup_launcher": "setup, repair, rollback, launcher profiles, instances, and product orchestration",
    "governance": "authority order, canon, contracts, refusal, review gates, and agent operation",
    "simulation": "deterministic domains, processes, machines, physical systems, economy, and civilization dynamics",
    "content": "packs, mods, authored payload, GUI/content boundaries, and provider/content separation",
    "timekeeping": "calendar, chronology, timestamp durability, 2038 resilience, and time-domain law",
    "ui": "presentation, tools, editor concepts, perceived model surfaces, and command/result display",
    "xstack_aide": "repo-control and assistant-operation systems around AIDE, XStack, AuditX, RepoX, and TestX",
    "contracts_schema": "machine-readable contracts, schemas, compatibility, manifests, and registries",
}

EXPECTED_KINDS = {
    "manifest",
    "primary_report",
    "spec_sheet",
    "reader_brief",
    "registers",
    "verification",
}

TOPIC_KEYWORDS = {
    "architecture": ["architecture", "api", "abi", "product", "layer", "spine", "foundation"],
    "workbench": ["workbench", "operator", "panel", "command result", "presentation"],
    "determinism": ["determin", "replay", "rng", "fixed-point", "hash", "lockstep"],
    "platform": ["platform", "renderer", "dgfx", "dsys", "window", "native", "win32", "macos", "linux", "web"],
    "release": ["release", "version", "build", "distribution", "update", "publication", "identity"],
    "worldgen": ["world", "universe", "galaxy", "earth", "sol", "celestial", "chronology", "calendar"],
    "tooling": ["tool", "codex", "prompt", "testx", "repox", "auditx", "xstack", "aide"],
    "setup_launcher": ["launcher", "setup", "installer", "instance", "account"],
    "governance": ["governance", "canon", "authority", "contract", "schema", "policy", "review"],
    "simulation": ["simulation", "engine", "actor", "machine", "power", "fluid", "heat", "vehicle", "building"],
    "content": ["content", "pack", "mod", "data", "gui", "binary", "default pack"],
    "timekeeping": ["time", "calendar", "2038", "chronology", "date", "clock"],
    "ui": ["ui", "gui", "tui", "cli", "editor", "dui", "frontend"],
    "xstack_aide": ["xstack", "aide", "repox", "testx", "auditx", "controlx"],
    "contracts_schema": ["contract", "schema", "compat", "manifest", "registry"],
}

BLOCKED_SCOPE_KEYWORDS = {
    "broad_workbench_ui": ["broad workbench ui", "workbench ui", "full workbench", "editor workflow"],
    "runtime_module_loader": ["runtime module loader", "module loader", "dynamic plugin", "hot swap", "hotswap"],
    "provider_runtime": ["provider runtime", "provider", "gateway", "model provider"],
    "package_runtime": ["package runtime", "package mount", "pack runtime", "mod runtime"],
    "gameplay": ["gameplay", "survival", "combat", "economy gameplay", "player loop"],
    "renderer_implementation": ["renderer implementation", "d3d", "vulkan", "metal", "opengl", "dgfx backend"],
    "native_gui": ["native gui", "winui", "winforms", "appkit", "swiftui", "win32 gui"],
    "release_publication": ["release publication", "publish", "storefront", "shipping", "public release"],
}

STALE_EXTERNAL_PATTERNS = [
    "C89",
    "C++98",
    "ISO C89",
    "Win98",
    "Windows 98",
    "Windows NT 2000",
    "Mac OS 9",
    "Mac OS 8",
    "CP/M",
    "286",
    "DX12",
    "iOS",
    "Android",
    "WebGPU",
    "console program",
    "SDK",
]


def ascii_text(value: str) -> str:
    replacements = {
        "\u2014": "-",
        "\u2013": "-",
        "\u2011": "-",
        "\u2010": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2026": "...",
        "\u2192": "->",
        "\u2194": "<->",
        "\u039b": "Lambda",
        "\u03a3": "Sigma",
        "\u03a9": "Omega",
        "\u039e": "Xi",
        "\u03a0": "Pi",
        "\u03a5": "Upsilon",
        "\u03a6": "Phi",
        "\u0396": "Zeta",
        "\ufeff": "",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    return value.encode("ascii", "replace").decode("ascii")


def normalize_rel(path: Path, repo_root: Path) -> str:
    rel = path.resolve().relative_to(repo_root.resolve())
    return rel.as_posix()


def sort_key(path: str) -> Tuple[str, str]:
    return (path.casefold(), path)


def read_text(path: Path, limit: int = 160_000) -> str:
    try:
        data = path.read_bytes()[:limit]
    except OSError:
        return ""
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return data.decode(encoding, errors="replace")
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def slugify(value: str) -> str:
    value = ascii_text(value).lower()
    value = re.sub(r"[^a-z0-9]+", "_", value).strip("_")
    return value or "conversation"


def title_from_slug(value: str) -> str:
    return " ".join(part.capitalize() for part in re.split(r"[_\-\s]+", ascii_text(value)) if part)


def md_header(result: str) -> str:
    return ascii_text(
        "\n".join(
            [
                "Status: DERIVED",
                f"Last Reviewed: {REVIEW_DATE}",
                "Supersedes: none",
                "Superseded By: none",
                "Stability: provisional",
                f"Result: {result}",
                f"Binding Sources: {HEADER_BINDING}",
                "",
            ]
        )
    )


def write_text_if_changed(path: Path, content: str) -> bool:
    content = ascii_text(content)
    path.parent.mkdir(parents=True, exist_ok=True)
    old = None
    if path.exists():
        old = path.read_text(encoding="utf-8")
    if old == content:
        return False
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


def file_kind(path: Path) -> str:
    name = path.name.lower()
    suffix = path.suffix.lower()
    if suffix == ".zip":
        return "zip"
    if suffix in {".yaml", ".yml"}:
        if "spec_sheet" in name:
            return "spec_sheet"
        return "yaml"
    if suffix == ".json":
        return "json"
    if suffix in {".md", ".txt"}:
        if "manifest" in name:
            return "manifest"
        if "human_readable" in name or "full_chat_report" in name or "complete_human_report" in name:
            return "primary_report"
        if "reader_brief" in name or "in_chat_reader" in name:
            return "reader_brief"
        if "registers" in name or "register" in name:
            return "registers"
        if "verification" in name or "audit" in name or "integrity" in name or "checksum" in name:
            return "verification"
        if "context_transfer" in name or "handoff" in name:
            return "handoff"
        if "prompt" in name:
            return "prompt"
        if name.startswith("pasted") or "source" in name:
            return "source_input"
        return "markdown" if suffix == ".md" else "text"
    return suffix.lstrip(".") or "unknown"


def is_binary_kind(kind: str) -> bool:
    return kind in {"zip", "png", "jpg", "jpeg", "gif", "pdf", "unknown"}


@dataclass
class SourceFile:
    path: str
    conversation: str
    kind: str
    size: int
    sha256: str
    title: str = ""
    warnings: List[str] = field(default_factory=list)


@dataclass
class Conversation:
    folder: str
    slug: str
    title: str
    path: str
    files: List[SourceFile] = field(default_factory=list)
    nested_folders: List[str] = field(default_factory=list)
    kinds: Dict[str, int] = field(default_factory=dict)
    completeness_status: str = "unclear"
    completeness_warnings: List[str] = field(default_factory=list)
    source_hash: str = ""
    likely_package_type: str = "unknown"
    authority_class: str = "advisory_only"
    source_class: str = "conversation_handoff_export"
    topics: List[str] = field(default_factory=list)
    primary_source: str = ""
    primary_title: str = ""
    facts: List[str] = field(default_factory=list)
    uncertainties: List[str] = field(default_factory=list)
    future_work: List[str] = field(default_factory=list)
    rejected_or_superseded: List[str] = field(default_factory=list)


def extract_title_from_text(text: str, fallback: str) -> str:
    for line in text.splitlines()[:80]:
        clean = ascii_text(line.strip().lstrip("#").strip())
        if not clean:
            continue
        if clean.lower().startswith("human-readable chat report"):
            return clean.replace("Human-Readable Chat Report", "").strip(" -")
        if clean.lower().startswith("full chat report"):
            return clean.replace("Full Chat Report", "").strip(" -")
        if clean.lower().startswith("chat label"):
            return clean.split("|")[-1].strip() if "|" in clean else clean.split(":", 1)[-1].strip()
    match = re.search(r"Chat label\s*\|\s*([^|\n]+)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return fallback


def extract_lines(text: str, patterns: Sequence[str], limit: int = 10) -> List[str]:
    found: List[str] = []
    seen = set()
    for raw in text.splitlines():
        stripped = raw.strip()
        if stripped.startswith("|") or stripped.startswith("#") or stripped.count("|") > 2:
            continue
        line = re.sub(r"\s+", " ", stripped.strip(" -*\t"))
        if len(line) < 24 or len(line) > 420:
            continue
        lower = line.lower()
        if any(pattern.lower() in lower for pattern in patterns):
            if line not in seen:
                found.append(ascii_text(line))
                seen.add(line)
        if len(found) >= limit:
            break
    return found


def extract_orientation(text: str, fallback: str, max_paragraphs: int = 3) -> str:
    lines = text.splitlines()
    start = 0
    for idx, line in enumerate(lines):
        lower = line.lower()
        if "one-page orientation" in lower or "executive summary" in lower:
            start = idx + 1
            break
    paragraphs: List[str] = []
    current: List[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("#") and current:
            break
        if not stripped:
            if current:
                para = " ".join(current).strip()
                if len(para) > 80:
                    paragraphs.append(para)
                current = []
            if len(paragraphs) >= max_paragraphs:
                break
            continue
        if stripped.startswith("|") or stripped.startswith("- ") or stripped.startswith("* "):
            continue
        current.append(stripped)
    if current and len(paragraphs) < max_paragraphs:
        para = " ".join(current).strip()
        if len(para) > 80:
            paragraphs.append(para)
    if not paragraphs:
        paragraphs = [fallback]
    return "\n\n".join(ascii_text(p) for p in paragraphs[:max_paragraphs])


def scan_conversation_files(repo_root: Path) -> List[Conversation]:
    root = repo_root / CORPUS_ROOT
    conversations: List[Conversation] = []
    if not root.exists():
        return conversations
    for folder in sorted([p for p in root.iterdir() if p.is_dir() and not p.name.startswith("_")], key=lambda p: sort_key(p.name)):
        slug = slugify(folder.name)
        conv = Conversation(
            folder=folder.name,
            slug=slug,
            title=title_from_slug(folder.name),
            path=normalize_rel(folder, repo_root),
        )
        all_hashes: List[str] = []
        nested = set()
        for path in sorted([p for p in folder.rglob("*") if p.is_file()], key=lambda p: sort_key(normalize_rel(p, repo_root))):
            rel = normalize_rel(path, repo_root)
            kind = file_kind(path)
            digest = sha256_file(path)
            all_hashes.append(digest)
            title = ""
            warnings: List[str] = []
            if kind == "zip":
                try:
                    with zipfile.ZipFile(path) as zf:
                        bad = zf.testzip()
                        if bad:
                            warnings.append(f"zip_bad_member:{bad}")
                except zipfile.BadZipFile:
                    warnings.append("zip_unreadable")
            elif not is_binary_kind(kind):
                title = extract_title_from_text(read_text(path, 40_000), "")
            source = SourceFile(rel, folder.name, kind, path.stat().st_size, digest, ascii_text(title), warnings)
            conv.files.append(source)
            conv.kinds[kind] = conv.kinds.get(kind, 0) + 1
            sub_rel = path.relative_to(folder)
            if len(sub_rel.parts) > 1:
                nested.add(sub_rel.parts[0])
        conv.nested_folders = sorted(nested, key=sort_key)
        conv.source_hash = hashlib.sha256("".join(sorted(all_hashes)).encode("ascii")).hexdigest()
        classify_conversation(conv, repo_root)
        conversations.append(conv)
    return conversations


def classify_conversation(conv: Conversation, repo_root: Path) -> None:
    present = set(conv.kinds)
    if conv.kinds.get("zip", 0) > 2 and conv.nested_folders:
        conv.likely_package_type = "nested_package_collection"
    elif "primary_report" in present and "manifest" in present:
        conv.likely_package_type = "conversation_handoff_package"
    elif "manifest" in present and ("zip" in present or "spec_sheet" in present):
        conv.likely_package_type = "preservation_package"
    elif "source_input" in present or "text" in present:
        conv.likely_package_type = "source_material_collection"
    else:
        conv.likely_package_type = "mixed_archive"

    if "primary_report" not in present:
        conv.completeness_warnings.append("missing_primary_report")
    if "manifest" not in present:
        conv.completeness_warnings.append("missing_manifest")
    if "spec_sheet" not in present:
        conv.completeness_warnings.append("missing_spec_sheet")
    if any(file.warnings for file in conv.files):
        conv.completeness_warnings.append("file_warnings_present")
    if "primary_report" in present and "manifest" in present and not any(file.warnings for file in conv.files):
        conv.completeness_status = "complete" if "spec_sheet" in present else "partial"
    elif "manifest" in present or "primary_report" in present:
        conv.completeness_status = "partial"
    else:
        conv.completeness_status = "unclear"

    primary = choose_primary_source(conv)
    if primary:
        conv.primary_source = primary.path
        text = read_text(repo_root / primary.path)
        conv.primary_title = extract_title_from_text(text, conv.title)
        conv.title = conv.primary_title or conv.title
        conv.facts = extract_lines(text, ["FACT:", "decision", "decided", "accepted", "final", "central", "must"], 12)
        conv.uncertainties = extract_lines(text, ["UNCERTAIN", "UNVERIFIED", "unresolved", "caveat", "not decided", "verify", "requires verification"], 12)
        conv.future_work = extract_lines(text, ["future", "next step", "roadmap", "prompt", "task", "phase", "candidate"], 12)
        conv.rejected_or_superseded = extract_lines(text, ["superseded", "rejected", "not final", "blocked", "depriorit", "must not", "do not"], 10)
    topic_text = " ".join([conv.folder, conv.title] + conv.facts + conv.future_work).lower()
    conv.topics = sorted(
        [topic for topic, words in TOPIC_KEYWORDS.items() if any(word in topic_text for word in words)],
        key=sort_key,
    )


def choose_primary_source(conv: Conversation) -> Optional[SourceFile]:
    ordered_kinds = ["primary_report", "reader_brief", "manifest", "handoff", "markdown", "text"]
    for kind in ordered_kinds:
        candidates = [f for f in conv.files if f.kind == kind]
        if not candidates:
            continue
        candidates.sort(key=lambda f: (0 if "human_readable_chat_report" in f.path else 1, f.path.casefold(), f.path))
        return candidates[0]
    return None


def build_manifest(repo_root: Path) -> Tuple[dict, List[Conversation]]:
    conversations = scan_conversation_files(repo_root)
    all_files = [f for conv in conversations for f in conv.files]
    kind_counts: Dict[str, int] = {}
    for f in all_files:
        kind_counts[f.kind] = kind_counts.get(f.kind, 0) + 1
    complete = sum(1 for c in conversations if c.completeness_status == "complete")
    partial = sum(1 for c in conversations if c.completeness_status == "partial")
    unclear = sum(1 for c in conversations if c.completeness_status == "unclear")
    manifest = {
        "schema_id": "dominium.archive.conversation_corpus_manifest",
        "schema_version": "1.0.0",
        "status": "DERIVED",
        "last_reviewed": REVIEW_DATE,
        "authority_class": "advisory_only",
        "source_root": CORPUS_ROOT.as_posix(),
        "binding_sources": [
            "docs/canon/constitution_v1.md",
            "docs/canon/glossary_v1.md",
            "AGENTS.md",
            "docs/planning/AUTHORITY_ORDER.md",
            "docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md",
        ],
        "summary": {
            "conversation_count": len(conversations),
            "source_file_count": len(all_files),
            "kind_counts": dict(sorted(kind_counts.items())),
            "complete_packages": complete,
            "partial_packages": partial,
            "unclear_packages": unclear,
        },
        "conversations": [
            {
                "folder": c.folder,
                "slug": c.slug,
                "title": c.title,
                "path": c.path,
                "authority_class": c.authority_class,
                "source_class": c.source_class,
                "likely_package_type": c.likely_package_type,
                "completeness_status": c.completeness_status,
                "warnings": c.completeness_warnings,
                "source_hash": c.source_hash,
                "primary_source": c.primary_source,
                "topics": c.topics,
                "nested_folders": c.nested_folders,
                "kind_counts": dict(sorted(c.kinds.items())),
                "files": [
                    {
                        "path": f.path,
                        "kind": f.kind,
                        "size": f.size,
                        "sha256": f.sha256,
                        "title": f.title,
                        "warnings": f.warnings,
                    }
                    for f in sorted(c.files, key=lambda item: sort_key(item.path))
                ],
            }
            for c in conversations
        ],
    }
    return manifest, conversations


def link(path: str, label: Optional[str] = None) -> str:
    label = label or path
    return f"[{label}]({path})"


def rel_link_from(base_dir: str, target: str, label: Optional[str] = None) -> str:
    base = Path(base_dir)
    rel = os.path.relpath(target, base.as_posix()).replace("\\", "/")
    return link(rel, label or target)


def write_phase1(repo_root: Path) -> List[str]:
    manifest, conversations = build_manifest(repo_root)
    root = repo_root / CORPUS_ROOT
    intake = root / "_intake"
    changed: List[str] = []
    json_path = intake / "corpus_manifest.json"
    changed += changed_path(json_path, json.dumps(manifest, indent=2, sort_keys=True) + "\n", repo_root)

    all_files = [f for c in conversations for f in c.files]
    sha_lines = [f"{f.sha256}  {f.path}" for f in sorted(all_files, key=lambda item: sort_key(item.path))]
    changed += changed_path(intake / "SHA256SUMS.txt", "\n".join(sha_lines) + "\n", repo_root)

    changed += changed_path(root / "README.md", render_archive_readme(manifest), repo_root)
    changed += changed_path(root / "INDEX.md", render_archive_index(conversations, manifest), repo_root)
    changed += changed_path(intake / "CORPUS_MANIFEST.md", render_corpus_manifest(conversations, manifest), repo_root)
    changed += changed_path(intake / "PACKAGE_COMPLETENESS.md", render_package_completeness(conversations, manifest), repo_root)
    changed += changed_path(intake / "SOURCE_PROVENANCE.md", render_source_provenance(conversations, manifest), repo_root)
    return changed


def changed_path(path: Path, content: str, repo_root: Path) -> List[str]:
    if write_text_if_changed(path, content):
        return [normalize_rel(path, repo_root)]
    return []


def render_archive_readme(manifest: dict) -> str:
    s = manifest["summary"]
    return md_header("archive_scope_declared") + f"""# Conversation Archive

`docs/archive/conversations/` is a derived, non-authoritative archive of imported conversation handoff packages and source material.

This corpus may inform future planning, audits, and promotion candidates. It does not override canon, glossary, `AGENTS.md`, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## Authority Rule

Conversation exports are advisory archival evidence. Claims from these folders must pass through intake, contradiction review, and explicit promotion before they may influence live docs.

## Current Intake Summary

- Conversation folders: `{s["conversation_count"]}`
- Source files: `{s["source_file_count"]}`
- Complete packages: `{s["complete_packages"]}`
- Partial packages: `{s["partial_packages"]}`
- Unclear packages: `{s["unclear_packages"]}`

## Generated Management Layers

- `_intake/`: deterministic corpus manifest, completeness, provenance, and hashes.
- `_reader/`: per-conversation human-readable reader pages.
- `_audit/`: contradiction, drift, uncertainty, duplicate-topic, and coverage reports.
- `_promotion/`: review queue for possible future live-doc updates.
- `_wiki/`: repo-local navigation over topics, workstreams, decisions, tasks, artifacts, questions, and risks.

## Non-Goals

- No canon rewrite.
- No contract or schema changes.
- No architecture doctrine rewrite.
- No implementation changes.
- No release publication.
- No direct promotion of chat claims.
"""


def render_archive_index(conversations: List[Conversation], manifest: dict) -> str:
    lines = [md_header("index_generated"), "# Conversation Corpus Index", ""]
    lines.append("This index lists top-level archived conversation folders. Each entry is advisory only.")
    lines.append("")
    lines.append("| Conversation | Status | Type | Topics | Primary Source |")
    lines.append("| --- | --- | --- | --- | --- |")
    for c in conversations:
        primary = rel_link_from(CORPUS_ROOT.as_posix(), c.primary_source, c.primary_source) if c.primary_source else "none"
        topics = ", ".join(c.topics) if c.topics else "unclassified"
        lines.append(f"| `{c.folder}` | `{c.completeness_status}` | `{c.likely_package_type}` | {topics} | {primary} |")
    lines.append("")
    lines.append("See `_intake/corpus_manifest.json` for the machine-readable inventory.")
    return "\n".join(lines) + "\n"


def render_corpus_manifest(conversations: List[Conversation], manifest: dict) -> str:
    s = manifest["summary"]
    lines = [md_header("manifest_generated"), "# Corpus Manifest", ""]
    lines.append("This is the human-readable companion to `_intake/corpus_manifest.json`.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    for key, value in s.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Package Inventory")
    lines.append("")
    lines.append("| Folder | Title | Files | Hash | Completeness | Warnings |")
    lines.append("| --- | --- | ---: | --- | --- | --- |")
    for c in conversations:
        warnings = ", ".join(c.completeness_warnings) if c.completeness_warnings else "none"
        lines.append(f"| `{c.folder}` | {c.title} | {len(c.files)} | `{c.source_hash[:16]}` | `{c.completeness_status}` | {warnings} |")
    return "\n".join(lines) + "\n"


def render_package_completeness(conversations: List[Conversation], manifest: dict) -> str:
    lines = [md_header("completeness_report_generated"), "# Package Completeness", ""]
    lines.append("Completeness is structural only. It does not mean a conversation claim is authoritative.")
    lines.append("")
    for status in ("complete", "partial", "unclear"):
        subset = [c for c in conversations if c.completeness_status == status]
        lines.append(f"## {status.capitalize()} Packages")
        lines.append("")
        if not subset:
            lines.append("None.")
            lines.append("")
            continue
        lines.append("| Folder | Type | Present Kinds | Warnings |")
        lines.append("| --- | --- | --- | --- |")
        for c in subset:
            kinds = ", ".join(f"{k}:{v}" for k, v in sorted(c.kinds.items()))
            warnings = ", ".join(c.completeness_warnings) if c.completeness_warnings else "none"
            lines.append(f"| `{c.folder}` | `{c.likely_package_type}` | {kinds} | {warnings} |")
        lines.append("")
    return "\n".join(lines)


def render_source_provenance(conversations: List[Conversation], manifest: dict) -> str:
    lines = [md_header("provenance_report_generated"), "# Source Provenance", ""]
    lines.append("Every archived source file is treated as derived archival evidence with a source hash.")
    lines.append("")
    for c in conversations:
        lines.append(f"## `{c.folder}`")
        lines.append("")
        lines.append(f"- Source class: `{c.source_class}`")
        lines.append(f"- Authority class: `{c.authority_class}`")
        lines.append(f"- Source hash: `{c.source_hash}`")
        lines.append(f"- Primary source: `{c.primary_source or 'none'}`")
        if c.nested_folders:
            lines.append(f"- Nested folders: {', '.join(f'`{x}`' for x in c.nested_folders)}")
        lines.append("")
        lines.append("| File | Kind | Size | SHA-256 | Warnings |")
        lines.append("| --- | --- | ---: | --- | --- |")
        for f in sorted(c.files, key=lambda item: sort_key(item.path)):
            warnings = ", ".join(f.warnings) if f.warnings else "none"
            lines.append(f"| `{f.path}` | `{f.kind}` | {f.size} | `{f.sha256}` | {warnings} |")
        lines.append("")
    return "\n".join(lines)


def write_phase2(repo_root: Path) -> List[str]:
    manifest, conversations = build_manifest(repo_root)
    root = repo_root / CORPUS_ROOT
    changed: List[str] = []
    by_chat = root / "_reader" / "by_chat"
    for c in conversations:
        changed += changed_path(by_chat / f"{c.slug}.md", render_reader_page(repo_root, c), repo_root)
    changed += changed_path(root / "_reader" / "conversation_reader_index.md", render_reader_index(conversations), repo_root)
    return changed


def render_reader_page(repo_root: Path, c: Conversation) -> str:
    source_text = read_text(repo_root / c.primary_source) if c.primary_source else ""
    orientation = extract_orientation(source_text, f"This conversation package is archived under `{c.path}`.")
    facts = c.facts or ["No stable decision lines were extracted automatically; inspect the primary source before using this package."]
    undecided = c.uncertainties or ["No explicit uncertainty lines were extracted automatically; this does not imply the package is verified."]
    future = c.future_work or ["No explicit future-work lines were extracted automatically."]
    rejected = c.rejected_or_superseded or ["No explicit rejected or superseded ideas were extracted automatically."]
    artifact_lines = []
    for kind, count in sorted(c.kinds.items()):
        artifact_lines.append(f"- `{kind}`: `{count}`")
    return md_header("reader_page_generated") + f"""Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `{c.path}/`
Promotion Status: not_reviewed

# {c.title} - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

{orientation}

## Why It Mattered

This conversation matters as historical context for the topics tagged here: {", ".join(c.topics) if c.topics else "unclassified"}. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `{c.likely_package_type}` with `{len(c.files)}` source files. The primary extracted source is `{c.primary_source or "none"}`.

## What Was Decided

{bullet_list(facts)}

## What Was Not Decided

{bullet_list(undecided)}

## Ideas Rejected, Superseded, Or Deprioritised

{bullet_list(rejected)}

## What Future Work Came From It

{bullet_list(future)}

## Important Artifacts

{chr(10).join(artifact_lines)}

## Verification Needed

- Verify every implementation, platform, tooling, release, and queue claim against current repo artifacts.
- Treat external platform or SDK claims as stale until independently checked.
- Treat old language-baseline claims as historical unless they match current `README.md` and current contracts.
- Do not infer current authority from the existence of this archive package.

## Candidate Promotions

Candidate promotions, if any, are recorded in `_promotion/PROMOTION_QUEUE.md`. This page does not promote claims.

## Do Not Assume

- Do not assume this conversation established current repo truth.
- Do not assume generated package reports are canonical.
- Do not assume old prompts were executed.
- Do not assume unresolved items are safe to implement.
- Do not use this package to open blocked work without stronger current authority.
"""


def bullet_list(items: Sequence[str]) -> str:
    return "\n".join(f"- {ascii_text(item)}" for item in items)


def render_reader_index(conversations: List[Conversation]) -> str:
    lines = [md_header("reader_index_generated"), "# Conversation Reader Index", ""]
    lines.append("Reader pages are prose-first advisory views over archived conversations.")
    lines.append("")
    lines.append("| Reader | Source Folder | Topics | Promotion Status |")
    lines.append("| --- | --- | --- | --- |")
    for c in conversations:
        reader = f"by_chat/{c.slug}.md"
        topics = ", ".join(c.topics) if c.topics else "unclassified"
        lines.append(f"| {link(reader, c.title)} | `{c.path}` | {topics} | `not_reviewed` |")
    return "\n".join(lines) + "\n"


@dataclass
class Finding:
    finding_id: str
    class_name: str
    source_conversation: str
    source_file: str
    claim: str
    authority_domain: str
    conflict_target: str
    severity: str
    evidence: str
    recommended_disposition: str
    user_review_question: str


def build_findings(repo_root: Path, conversations: List[Conversation]) -> Tuple[List[Finding], List[dict]]:
    findings: List[Finding] = []
    promotions: List[dict] = []
    idx = 1
    promo_idx = 1
    for c in conversations:
        text = read_text(repo_root / c.primary_source) if c.primary_source else ""
        lower = text.lower()
        for scope, words in BLOCKED_SCOPE_KEYWORDS.items():
            if any(word in lower for word in words) and any(word in lower for word in ["implement", "build", "next", "prompt", "roadmap", "work"]):
                findings.append(
                    Finding(
                        f"CONTRA-{idx:04d}",
                        "conversation_vs_current_queue",
                        c.folder,
                        c.primary_source,
                        f"Archived conversation discusses work related to blocked scope `{scope}`.",
                        "planning",
                        ".aide/queue/current.toml",
                        "medium",
                        "Keyword match in archived primary source plus current queue block.",
                        "preserve_as_history; require current queue authority before action",
                        f"Should `{scope}` remain blocked for claims from `{c.folder}`?",
                    )
                )
                idx += 1
        for pattern in STALE_EXTERNAL_PATTERNS:
            if pattern.lower() in lower:
                findings.append(
                    Finding(
                        f"CONTRA-{idx:04d}",
                        "stale_external_claim",
                        c.folder,
                        c.primary_source,
                        f"Archived conversation contains potentially stale external or baseline claim: `{pattern}`.",
                        "structural",
                        "README.md / current platform and language baseline",
                        "low",
                        "Keyword appears in archived package; no external verification performed.",
                        "quarantined until current repo and external facts are checked",
                        f"Is `{pattern}` still intended for current planning, or historical only?",
                    )
                )
                idx += 1
        for claim in c.facts[:3]:
            promotions.append(
                {
                    "id": f"PROMOTE-{promo_idx:04d}",
                    "source_conversation": c.folder,
                    "source_file": c.primary_source,
                    "source_heading": "automatic decision extraction",
                    "claim": claim,
                    "claim_type": "conversation_claim",
                    "proposed_target": "not_selected",
                    "authority_domain": "planning",
                    "current_repo_conflict": "not_checked",
                    "why_it_may_matter": "The claim recurs as a decision-like statement in the archived package.",
                    "risks": "Chat claims may be stale, superseded, or contradicted by current repo artifacts.",
                    "required_review": "human review plus authority-order check",
                    "recommended_disposition": "not_reviewed",
                }
            )
            promo_idx += 1
    pair_claims = [
        ("single game binary with flags", "separate client or server binaries", "conversation_vs_conversation"),
        ("C89", "C17", "conversation_vs_docs"),
        ("C++98", "C++17", "conversation_vs_docs"),
        ("JSON", "TLV", "conversation_vs_conversation"),
        ("WinForms", "WinUI", "conversation_vs_conversation"),
    ]
    corpus_text_by_conv = {c.folder: read_text(repo_root / c.primary_source) if c.primary_source else "" for c in conversations}
    for left, right, cls in pair_claims:
        left_sources = [name for name, text in corpus_text_by_conv.items() if left.lower() in text.lower()]
        right_sources = [name for name, text in corpus_text_by_conv.items() if right.lower() in text.lower()]
        if left_sources and right_sources:
            findings.append(
                Finding(
                    f"CONTRA-{idx:04d}",
                    cls,
                    ", ".join(sorted(set(left_sources + right_sources), key=sort_key)[:8]),
                    "multiple primary sources",
                    f"Corpus contains both `{left}` and `{right}` claims.",
                    "planning",
                    "current repo authority and conversation cross-check",
                    "medium",
                    f"Left sources: {', '.join(left_sources[:5])}; right sources: {', '.join(right_sources[:5])}.",
                    "quarantined until reviewed",
                    f"Which side, if any, should be promoted after current repo verification?",
                )
            )
            idx += 1
    return findings, promotions


def write_phase3(repo_root: Path) -> List[str]:
    manifest, conversations = build_manifest(repo_root)
    findings, promotions = build_findings(repo_root, conversations)
    root = repo_root / CORPUS_ROOT
    changed: List[str] = []
    changed += changed_path(root / "_audit" / "CONTRADICTION_MATRIX.md", render_contradiction_matrix(findings), repo_root)
    changed += changed_path(root / "_audit" / "DOC_DRIFT_REPORT.md", render_doc_drift(findings), repo_root)
    changed += changed_path(root / "_audit" / "STALENESS_AND_VERIFICATION.md", render_staleness(findings, conversations), repo_root)
    changed += changed_path(root / "_audit" / "DUPLICATE_TOPICS.md", render_duplicate_topics(conversations), repo_root)
    changed += changed_path(root / "_audit" / "UNCERTAINTY_REGISTER.md", render_uncertainty_register(conversations), repo_root)
    changed += changed_path(root / "_audit" / "COVERAGE_GAPS.md", render_coverage_gaps(conversations), repo_root)
    changed += changed_path(root / "_promotion" / "PROMOTION_QUEUE.md", render_promotion_queue(promotions), repo_root)
    changed += changed_path(root / "_promotion" / "REVIEW_DECISIONS.md", render_review_decisions(), repo_root)
    changed += changed_path(root / "_promotion" / "CANDIDATE_PATCH_PLAN.md", render_candidate_patch_plan(), repo_root)
    changed += changed_path(root / "_promotion" / "NON_PROMOTED_CONTEXT.md", render_non_promoted_context(conversations), repo_root)
    changed += changed_path(root / "_promotion" / "REJECTED_OR_QUARANTINED_CLAIMS.md", render_rejected_quarantined(findings), repo_root)
    return changed


def render_contradiction_matrix(findings: List[Finding]) -> str:
    lines = [md_header("contradiction_matrix_generated"), "# Contradiction Matrix", ""]
    lines.append("Findings are review queues, not resolved doctrine.")
    lines.append("")
    lines.append("| ID | Class | Source | Claim | Conflict Target | Severity | Disposition |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for f in findings:
        lines.append(f"| `{f.finding_id}` | `{f.class_name}` | `{f.source_conversation}` | {f.claim} | `{f.conflict_target}` | `{f.severity}` | {f.recommended_disposition} |")
    if not findings:
        lines.append("| none | none | none | none | none | none | none |")
    return "\n".join(lines) + "\n"


def render_doc_drift(findings: List[Finding]) -> str:
    drift = [f for f in findings if f.class_name in {"conversation_vs_docs", "stale_external_claim", "conversation_vs_current_queue"}]
    lines = [md_header("doc_drift_report_generated"), "# Document Drift Report", ""]
    lines.append("This report flags archived claims that may drift from current README, queue, language baseline, or authority order.")
    lines.append("")
    for f in drift:
        lines.append(f"## `{f.finding_id}` - `{f.class_name}`")
        lines.append("")
        lines.append(f"- Source conversation: `{f.source_conversation}`")
        lines.append(f"- Source file: `{f.source_file}`")
        lines.append(f"- Claim: {f.claim}")
        lines.append(f"- Conflict target: `{f.conflict_target}`")
        lines.append(f"- Recommended disposition: {f.recommended_disposition}")
        lines.append("")
    if not drift:
        lines.append("No drift findings were generated.")
    return "\n".join(lines) + "\n"


def render_staleness(findings: List[Finding], conversations: List[Conversation]) -> str:
    lines = [md_header("staleness_report_generated"), "# Staleness And Verification", ""]
    lines.append("External platform, SDK, release, language-baseline, and implementation claims are stale until verified.")
    lines.append("")
    lines.append("## Packages With Explicit Uncertainty")
    lines.append("")
    for c in conversations:
        if c.uncertainties:
            lines.append(f"### `{c.folder}`")
            lines.append("")
            lines.extend(f"- {u}" for u in c.uncertainties[:8])
            lines.append("")
    lines.append("## Stale Claim Findings")
    lines.append("")
    for f in findings:
        if f.class_name == "stale_external_claim":
            lines.append(f"- `{f.finding_id}` `{f.source_conversation}`: {f.claim}")
    return "\n".join(lines) + "\n"


def render_duplicate_topics(conversations: List[Conversation]) -> str:
    by_topic: Dict[str, List[Conversation]] = {}
    for c in conversations:
        for t in c.topics:
            by_topic.setdefault(t, []).append(c)
    lines = [md_header("duplicate_topics_report_generated"), "# Duplicate Topics", ""]
    lines.append("A duplicated topic is not a defect. It is a signal that synthesis requires cross-source review.")
    lines.append("")
    for topic, convs in sorted(by_topic.items()):
        if len(convs) < 2:
            continue
        lines.append(f"## `{topic}`")
        lines.append("")
        for c in convs:
            lines.append(f"- `{c.folder}` - {c.title}")
        lines.append("")
    return "\n".join(lines)


def render_uncertainty_register(conversations: List[Conversation]) -> str:
    lines = [md_header("uncertainty_register_generated"), "# Uncertainty Register", ""]
    lines.append("Uncertainty entries are extracted from archived reports and require current repo verification.")
    lines.append("")
    for c in conversations:
        if not c.uncertainties:
            continue
        lines.append(f"## `{c.folder}`")
        lines.append("")
        lines.append(f"- Source file: `{c.primary_source}`")
        for item in c.uncertainties:
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines)


def render_coverage_gaps(conversations: List[Conversation]) -> str:
    lines = [md_header("coverage_gaps_report_generated"), "# Coverage Gaps", ""]
    lines.append("Coverage gaps identify incomplete or structurally unclear archived packages.")
    lines.append("")
    lines.append("| Folder | Status | Warnings | Missing Expected Kinds |")
    lines.append("| --- | --- | --- | --- |")
    for c in conversations:
        present = set(c.kinds)
        missing = sorted(EXPECTED_KINDS - present, key=sort_key)
        if c.completeness_status != "complete" or missing:
            warnings = ", ".join(c.completeness_warnings) if c.completeness_warnings else "none"
            lines.append(f"| `{c.folder}` | `{c.completeness_status}` | {warnings} | {', '.join(missing) if missing else 'none'} |")
    return "\n".join(lines) + "\n"


def render_promotion_queue(promotions: List[dict]) -> str:
    lines = [md_header("promotion_queue_generated"), "# Promotion Queue", ""]
    lines.append("Promotion candidates are not promoted. They are review items for later explicit work.")
    lines.append("")
    for p in promotions:
        lines.append(f"## {p['id']} - {p['claim'][:72]}")
        lines.append("")
        fields = [
            "source_conversation",
            "source_file",
            "source_heading",
            "claim",
            "claim_type",
            "proposed_target",
            "authority_domain",
            "current_repo_conflict",
            "why_it_may_matter",
            "risks",
            "required_review",
            "recommended_disposition",
        ]
        for field in fields:
            lines.append(f"- {field.replace('_', ' ').capitalize()}: {p[field]}")
        lines.append("")
    if not promotions:
        lines.append("No promotion candidates were generated.")
    return "\n".join(lines)


def render_review_decisions() -> str:
    return md_header("review_decisions_initialized") + """# Review Decisions

No conversation claims have been promoted by this intake.

Future review decisions must record:

- promotion ID;
- reviewer;
- date;
- source evidence;
- stronger repo authority checked;
- disposition;
- target paths, if any;
- validation performed.
"""


def render_candidate_patch_plan() -> str:
    return md_header("candidate_patch_plan_initialized") + """# Candidate Patch Plan

No live-doc patch plan is authorized by this intake.

Later patch planning must start from reviewed promotion IDs and must not patch canon, contracts, schemas, implementation, release, or current queue files without explicit stronger authority.
"""


def render_non_promoted_context(conversations: List[Conversation]) -> str:
    lines = [md_header("non_promoted_context_generated"), "# Non-Promoted Context", ""]
    lines.append("All archived conversations remain preserved as historical context unless separately promoted.")
    lines.append("")
    for c in conversations:
        lines.append(f"- `{c.folder}`: `{c.completeness_status}`, promotion status `not_reviewed`.")
    return "\n".join(lines) + "\n"


def render_rejected_quarantined(findings: List[Finding]) -> str:
    lines = [md_header("rejected_quarantined_claims_generated"), "# Rejected Or Quarantined Claims", ""]
    lines.append("No claims are rejected as doctrine here. Conflicting or stale claims are quarantined for review.")
    lines.append("")
    for f in findings:
        if "quarantine" in f.recommended_disposition or "blocked" in f.recommended_disposition:
            lines.append(f"## `{f.finding_id}`")
            lines.append("")
            lines.append(f"- Class: `{f.class_name}`")
            lines.append(f"- Source: `{f.source_conversation}` / `{f.source_file}`")
            lines.append(f"- Claim: {f.claim}")
            lines.append(f"- Disposition: {f.recommended_disposition}")
            lines.append("")
    return "\n".join(lines)


def write_phase4(repo_root: Path) -> List[str]:
    manifest, conversations = build_manifest(repo_root)
    findings, promotions = build_findings(repo_root, conversations)
    root = repo_root / CORPUS_ROOT
    changed: List[str] = []
    changed += changed_path(root / "_wiki" / "index.md", render_wiki_index(conversations), repo_root)
    for name, renderer in [
        ("topics/index.md", render_topic_index),
        ("workstreams/index.md", render_workstreams),
        ("decisions/index.md", render_decisions),
        ("tasks/index.md", render_tasks),
        ("artifacts/index.md", render_artifacts),
        ("open_questions/index.md", render_open_questions),
        ("risks/index.md", lambda cs: render_risks(cs, findings)),
    ]:
        changed += changed_path(root / "_wiki" / name, renderer(conversations), repo_root)
    by_topic: Dict[str, List[Conversation]] = {}
    for c in conversations:
        for topic in c.topics:
            by_topic.setdefault(topic, []).append(c)
    for topic, convs in sorted(by_topic.items()):
        changed += changed_path(root / "_wiki" / "topics" / f"{topic}.md", render_topic_page(topic, convs, findings), repo_root)
    return changed


def reader_link_for(c: Conversation, prefix: str = "../_reader/by_chat") -> str:
    return f"{prefix}/{c.slug}.md"


def render_wiki_index(conversations: List[Conversation]) -> str:
    return md_header("wiki_index_generated") + f"""# Conversation Corpus Wiki

This repo-local wiki is a navigation surface over the archived conversation corpus. It is not a GitHub Wiki and it is not authoritative doctrine.

## Browse

- [Topics](topics/index.md)
- [Workstreams](workstreams/index.md)
- [Decisions](decisions/index.md)
- [Tasks](tasks/index.md)
- [Artifacts](artifacts/index.md)
- [Open Questions](open_questions/index.md)
- [Risks](risks/index.md)

## Scope

- Source conversations: `{len(conversations)}`
- Authority class: `advisory_only`
- Promotion status: `not_reviewed`

Use `_promotion/PROMOTION_QUEUE.md` before proposing any live-doc update.
"""


def render_topic_index(conversations: List[Conversation]) -> str:
    by_topic: Dict[str, List[Conversation]] = {}
    for c in conversations:
        for topic in c.topics:
            by_topic.setdefault(topic, []).append(c)
    lines = [md_header("topic_index_generated"), "# Topic Index", ""]
    for topic, convs in sorted(by_topic.items()):
        lines.append(f"- [{topic}]({topic}.md): {len(convs)} conversations")
    return "\n".join(lines) + "\n"


def render_topic_page(topic: str, convs: List[Conversation], findings: List[Finding]) -> str:
    topic_findings = [f for f in findings if any(c.folder in f.source_conversation for c in convs)]
    lines = [md_header("topic_page_generated"), f"# Topic: {topic}", ""]
    lines.append("## What This Topic Means")
    lines.append("")
    lines.append(f"`{topic}` is an automatically classified conversation-corpus topic. It groups archived conversations by recurring words and package labels, not by authoritative repo ownership.")
    lines.append("")
    lines.append("## Source Conversations")
    lines.append("")
    for c in convs:
        lines.append(f"- [{c.title}](../../_reader/by_chat/{c.slug}.md) - `{c.folder}`")
    lines.append("")
    lines.append("## Recurring Claims")
    lines.append("")
    for c in convs:
        for claim in c.facts[:2]:
            lines.append(f"- `{c.folder}`: {claim}")
    lines.append("")
    lines.append("## Contradictions And Verification Needs")
    lines.append("")
    if topic_findings:
        for f in topic_findings[:20]:
            lines.append(f"- `{f.finding_id}` `{f.class_name}`: {f.claim}")
    else:
        lines.append("- No automatic contradiction findings for this topic.")
    lines.append("")
    lines.append("## Promotion Status")
    lines.append("")
    lines.append("`not_reviewed`; see `_promotion/PROMOTION_QUEUE.md`.")
    return "\n".join(lines) + "\n"


def render_workstreams(conversations: List[Conversation]) -> str:
    lines = [md_header("workstreams_index_generated"), "# Workstreams", ""]
    for topic in sorted(TOPIC_KEYWORDS):
        convs = [c for c in conversations if topic in c.topics]
        if convs:
            lines.append(f"## `{topic}`")
            lines.append("")
            for c in convs:
                lines.append(f"- [{c.title}](../../_reader/by_chat/{c.slug}.md)")
            lines.append("")
    return "\n".join(lines)


def render_decisions(conversations: List[Conversation]) -> str:
    lines = [md_header("decisions_index_generated"), "# Decisions", ""]
    lines.append("Decision-like entries are extracted from archived text and are not promoted.")
    lines.append("")
    for c in conversations:
        if not c.facts:
            continue
        lines.append(f"## [{c.title}](../../_reader/by_chat/{c.slug}.md)")
        lines.append("")
        for fact in c.facts[:8]:
            lines.append(f"- {fact}")
        lines.append("")
    return "\n".join(lines)


def render_tasks(conversations: List[Conversation]) -> str:
    lines = [md_header("tasks_index_generated"), "# Tasks And Future Work", ""]
    lines.append("Task-like entries are historical unless stronger current repo authority opens them.")
    lines.append("")
    for c in conversations:
        if not c.future_work:
            continue
        lines.append(f"## [{c.title}](../../_reader/by_chat/{c.slug}.md)")
        lines.append("")
        for item in c.future_work[:8]:
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines)


def render_artifacts(conversations: List[Conversation]) -> str:
    lines = [md_header("artifacts_index_generated"), "# Artifacts", ""]
    lines.append("Artifact counts are structural inventory only.")
    lines.append("")
    lines.append("| Conversation | Artifact Kinds | Primary Source |")
    lines.append("| --- | --- | --- |")
    for c in conversations:
        kinds = ", ".join(f"{k}:{v}" for k, v in sorted(c.kinds.items()))
        lines.append(f"| [{c.title}](../../_reader/by_chat/{c.slug}.md) | {kinds} | `{c.primary_source or 'none'}` |")
    return "\n".join(lines) + "\n"


def render_open_questions(conversations: List[Conversation]) -> str:
    lines = [md_header("open_questions_index_generated"), "# Open Questions", ""]
    lines.append("Open questions are extracted uncertainty and verification needs.")
    lines.append("")
    for c in conversations:
        if not c.uncertainties:
            continue
        lines.append(f"## [{c.title}](../../_reader/by_chat/{c.slug}.md)")
        lines.append("")
        for item in c.uncertainties[:8]:
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines)


def render_risks(conversations: List[Conversation], findings: List[Finding]) -> str:
    lines = [md_header("risks_index_generated"), "# Risks", ""]
    lines.append("Risks are review triggers, not resolved findings.")
    lines.append("")
    for f in findings:
        lines.append(f"- `{f.finding_id}` `{f.severity}` `{f.class_name}`: {f.claim}")
    return "\n".join(lines) + "\n"


def generated_markdown_files(repo_root: Path) -> List[Path]:
    root = repo_root / CORPUS_ROOT
    files: List[Path] = []
    for name in GENERATED_MARKDOWN_ROOT_FILES:
        path = root / name
        if path.exists():
            files.append(path)
    for name in GENERATED_MARKDOWN_DIRS:
        directory = root / name
        if directory.exists():
            files.extend(path for path in directory.rglob("*.md") if path.is_file())
    return sorted(files, key=lambda path: sort_key(normalize_rel(path, repo_root)))


def markdown_link_targets(text: str) -> Iterable[str]:
    for match in re.finditer(r"(?<!!)\[[^\]]+\]\(([^)\n]+)\)", text):
        target = match.group(1).strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        if not target or target.startswith("#"):
            continue
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            continue
        target = target.split("#", 1)[0].strip()
        if target:
            yield target


def link_integrity_issues(repo_root: Path) -> List[dict]:
    issues: List[dict] = []
    repo_resolved = repo_root.resolve()
    for doc in generated_markdown_files(repo_root):
        text = doc.read_text(encoding="utf-8")
        for target in markdown_link_targets(text):
            resolved = (doc.parent / target).resolve()
            try:
                resolved.relative_to(repo_resolved)
            except ValueError:
                issues.append(
                    {
                        "doc": normalize_rel(doc, repo_root),
                        "target": target,
                        "issue": "target_outside_repo",
                    }
                )
                continue
            if not resolved.exists():
                issues.append(
                    {
                        "doc": normalize_rel(doc, repo_root),
                        "target": target,
                        "issue": "target_missing",
                    }
                )
    return issues


def parse_promotion_candidates(text: str) -> List[dict]:
    candidates: List[dict] = []
    sections = re.split(r"(?m)^##\s+(PROMOTE-\d+)\s+-\s*", text)
    for idx in range(1, len(sections), 2):
        candidate_id = sections[idx]
        body = sections[idx + 1]
        title = body.splitlines()[0].strip() if body.splitlines() else ""
        fields: Dict[str, str] = {}
        for line in body.splitlines():
            if not line.startswith("- "):
                continue
            key, sep, value = line[2:].partition(":")
            if sep:
                fields[key.strip().lower()] = value.strip()
        candidates.append(
            {
                "id": candidate_id,
                "title": ascii_text(title),
                "claim": ascii_text(fields.get("claim", "")),
                "source_conversation": fields.get("Source conversation".lower(), ""),
                "source_file": fields.get("Source file".lower(), ""),
                "recommended_disposition": fields.get("Recommended disposition".lower(), ""),
            }
        )
    return candidates


def acceptance_metrics(repo_root: Path) -> dict:
    root = repo_root / CORPUS_ROOT
    manifest_path = root / "_intake" / "corpus_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    regenerated_manifest, conversations = build_manifest(repo_root)
    source_file_count = manifest["summary"]["source_file_count"]
    regenerated_file_count = regenerated_manifest["summary"]["source_file_count"]
    sha_path = root / "_intake" / "SHA256SUMS.txt"
    sha_lines = [line for line in sha_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    link_issues = link_integrity_issues(repo_root)
    validation_errors = validate_outputs(repo_root)
    findings, promotions = build_findings(repo_root, conversations)

    reader_dir = root / "_reader" / "by_chat"
    expected_reader_names = {f"{c.slug}.md" for c in conversations}
    actual_reader_names = {path.name for path in reader_dir.glob("*.md")} if reader_dir.exists() else set()
    reader_files = sorted(reader_dir.glob("*.md"), key=lambda path: sort_key(path.name)) if reader_dir.exists() else []
    reader_texts = {normalize_rel(path, repo_root): path.read_text(encoding="utf-8") for path in reader_files}
    reader_placeholder_patterns = {
        "no_stable_decision_lines": "No stable decision lines were extracted automatically",
        "no_explicit_uncertainty_lines": "No explicit uncertainty lines were extracted automatically",
        "no_explicit_future_work_lines": "No explicit future-work lines were extracted automatically",
        "no_rejected_or_superseded_lines": "No explicit rejected or superseded ideas were extracted automatically",
    }
    reader_placeholder_counts = {
        name: sum(1 for text in reader_texts.values() if pattern in text)
        for name, pattern in reader_placeholder_patterns.items()
    }
    missing_advisory = [
        path
        for path, text in reader_texts.items()
        if "Authority Class: advisory_only" not in text[:700] or "cannot override" not in text[:1200]
    ]
    short_readers = [path for path, text in reader_texts.items() if len(text) < 1800]

    promotion_text = (root / "_promotion" / "PROMOTION_QUEUE.md").read_text(encoding="utf-8")
    parsed_promotions = parse_promotion_candidates(promotion_text)
    noisy_patterns = [
        "context transfer",
        "downloadable",
        "in-chat reader",
        "archival mode",
        "future chat bootstrap",
        "human-readable report",
        "because the chat",
        "asked for a maximum-fidelity",
        "report files",
        "preserved the discussion",
        "final report",
    ]
    noisy_promotions = [
        p
        for p in parsed_promotions
        if any(pattern in p["claim"].lower() for pattern in noisy_patterns)
    ]
    long_promotions = [p for p in parsed_promotions if len(p["claim"]) > 360]
    not_checked_promotions = promotion_text.count("Current repo conflict: not_checked")

    contradiction_counts: Dict[str, int] = {}
    for finding in findings:
        contradiction_counts[finding.class_name] = contradiction_counts.get(finding.class_name, 0) + 1

    manifest_topics = sorted({topic for conv in manifest["conversations"] for topic in conv.get("topics", [])}, key=sort_key)
    missing_topic_pages = [
        topic
        for topic in manifest_topics
        if not (root / "_wiki" / "topics" / f"{topic}.md").exists()
    ]
    generated_header_issues = []
    for doc in generated_markdown_files(repo_root):
        text = doc.read_text(encoding="utf-8")
        for field_name in ["Status:", "Last Reviewed:", "Stability:", "Result:", "Binding Sources:"]:
            if field_name not in text[:700]:
                generated_header_issues.append(f"{normalize_rel(doc, repo_root)} missing {field_name}")
                break

    file_warning_count = sum(
        1
        for conv in manifest["conversations"]
        for file_entry in conv.get("files", [])
        if file_entry.get("warnings")
    )
    hard_failures = (
        validation_errors
        or link_issues
        or source_file_count != regenerated_file_count
        or len(sha_lines) != source_file_count
        or missing_topic_pages
        or expected_reader_names != actual_reader_names
        or generated_header_issues
    )
    warning_count = (
        len(noisy_promotions)
        + len(long_promotions)
        + sum(reader_placeholder_counts.values())
        + len(short_readers)
        + len(missing_advisory)
    )
    result = "FAIL" if hard_failures else ("PASS_WITH_WARNINGS" if warning_count or len(findings) > 100 else "PASS")
    return {
        "result": result,
        "manifest": manifest,
        "conversation_count": manifest["summary"]["conversation_count"],
        "source_file_count": source_file_count,
        "regenerated_file_count": regenerated_file_count,
        "complete_packages": manifest["summary"]["complete_packages"],
        "partial_packages": manifest["summary"]["partial_packages"],
        "unclear_packages": manifest["summary"]["unclear_packages"],
        "sha_line_count": len(sha_lines),
        "file_warning_count": file_warning_count,
        "validation_errors": validation_errors,
        "link_issues": link_issues,
        "reader_expected_count": len(expected_reader_names),
        "reader_actual_count": len(actual_reader_names),
        "reader_missing": sorted(expected_reader_names - actual_reader_names, key=sort_key),
        "reader_extra": sorted(actual_reader_names - expected_reader_names, key=sort_key),
        "reader_placeholder_counts": reader_placeholder_counts,
        "missing_advisory_readers": missing_advisory,
        "short_readers": short_readers,
        "promotion_count": len(parsed_promotions),
        "promotion_sources": len({p["source_conversation"] for p in parsed_promotions if p["source_conversation"]}),
        "noisy_promotions": noisy_promotions,
        "long_promotions": long_promotions,
        "not_checked_promotions": not_checked_promotions,
        "contradiction_count": len(findings),
        "contradiction_counts": dict(sorted(contradiction_counts.items())),
        "missing_topic_pages": missing_topic_pages,
        "topic_count": len(manifest_topics),
        "generated_markdown_count": len(generated_markdown_files(repo_root)),
        "generated_header_issues": generated_header_issues,
    }


def write_acceptance(repo_root: Path) -> List[str]:
    metrics = acceptance_metrics(repo_root)
    root = repo_root / CORPUS_ROOT
    changed: List[str] = []
    changed += changed_path(root / "_audit" / "INTAKE_ACCEPTANCE_REVIEW.md", render_intake_acceptance_review(metrics), repo_root)
    changed += changed_path(root / "_audit" / "READER_QUALITY_REVIEW.md", render_reader_quality_review(metrics), repo_root)
    changed += changed_path(root / "_audit" / "PROMOTION_QUEUE_QUALITY_REVIEW.md", render_promotion_queue_quality_review(metrics), repo_root)
    changed += changed_path(root / "_audit" / "LINK_INTEGRITY_REVIEW.md", render_link_integrity_review(metrics), repo_root)
    return changed


def render_intake_acceptance_review(metrics: dict) -> str:
    return md_header("acceptance_review_generated") + f"""# Intake Acceptance Review

Result: `{metrics["result"]}`

This review assesses whether the generated conversation-corpus intake is complete and useful enough to support derived synthesis. It does not promote conversation claims.

## Summary

| Check | Result |
| --- | --- |
| Conversation folders represented | `{metrics["conversation_count"]}` |
| Source files represented | `{metrics["source_file_count"]}` |
| Source files re-counted from disk | `{metrics["regenerated_file_count"]}` |
| SHA-256 lines | `{metrics["sha_line_count"]}` |
| Complete packages | `{metrics["complete_packages"]}` |
| Partial packages | `{metrics["partial_packages"]}` |
| Unclear packages | `{metrics["unclear_packages"]}` |
| Source file warnings | `{metrics["file_warning_count"]}` |
| Reader pages expected / actual | `{metrics["reader_expected_count"]}` / `{metrics["reader_actual_count"]}` |
| Promotion candidates | `{metrics["promotion_count"]}` |
| Contradiction findings | `{metrics["contradiction_count"]}` |
| Generated Markdown files reviewed | `{metrics["generated_markdown_count"]}` |
| Link issues | `{len(metrics["link_issues"])}` |

## Acceptance Findings

- All top-level source packages represented: `{metrics["conversation_count"] == metrics["reader_expected_count"]}`.
- All source files hashed: `{metrics["source_file_count"] == metrics["sha_line_count"]}`.
- Manifest re-scan matches committed manifest: `{metrics["source_file_count"] == metrics["regenerated_file_count"]}`.
- Reader pages are present and advisory-scoped: `{not metrics["reader_missing"] and not metrics["missing_advisory_readers"]}`.
- Wiki topic pages cover manifest topics: `{not metrics["missing_topic_pages"]}`.
- Link integrity is clean for generated Markdown: `{not metrics["link_issues"]}`.
- Promotion queue is useful as raw intake, but not clean enough for direct promotion: `{len(metrics["noisy_promotions"]) > 0 or len(metrics["long_promotions"]) > 0}`.
- Contradiction findings are actionable as a review backlog, but remain heuristic and need triage before use as doctrine evidence.

## Warnings Before Synthesis

- Noisy or archival-process promotion candidates: `{len(metrics["noisy_promotions"])}`.
- Overlong promotion candidates: `{len(metrics["long_promotions"])}`.
- Promotion candidates with repo conflict still `not_checked`: `{metrics["not_checked_promotions"]}`.
- Reader placeholder counts: `{metrics["reader_placeholder_counts"]}`.
- Contradiction findings are broad and keyword-assisted; use them as review triggers, not resolved conclusions.

## Decision

`{metrics["result"]}`

The corpus is ready for derived synthesis if synthesis cites reader/wiki/audit sources directly, keeps repo truth separate from conversation-derived intent, and treats the promotion queue as raw review material. It is not ready for direct live-doc promotion.

## Recommended Fixes Before Promotion

- Triage promotion candidates into serious, historical, stale, noisy, and needs-user-decision buckets.
- Reconcile high-value claims against canon, current queue, contracts, schema law, and implementation only in a separate task.
- Keep the current acceptance result visible in the synthesis book front matter.

## Recommended Next Task

`CONVERSATION-SYNTHESIS-BOOK-01`
"""


def render_reader_quality_review(metrics: dict) -> str:
    lines = [md_header("reader_quality_review_generated"), "# Reader Quality Review", ""]
    lines.append(f"Result: `{metrics['result']}`")
    lines.append("")
    lines.append("Reader pages are present for every manifest conversation and preserve advisory authority language.")
    lines.append("")
    lines.append("## Counts")
    lines.append("")
    lines.append(f"- Expected reader pages: `{metrics['reader_expected_count']}`")
    lines.append(f"- Actual reader pages: `{metrics['reader_actual_count']}`")
    lines.append(f"- Missing reader pages: `{len(metrics['reader_missing'])}`")
    lines.append(f"- Extra reader pages: `{len(metrics['reader_extra'])}`")
    lines.append(f"- Readers missing advisory language: `{len(metrics['missing_advisory_readers'])}`")
    lines.append(f"- Short reader pages: `{len(metrics['short_readers'])}`")
    lines.append("")
    lines.append("## Placeholder Signals")
    lines.append("")
    for name, count in metrics["reader_placeholder_counts"].items():
        lines.append(f"- `{name}`: `{count}`")
    lines.append("")
    lines.append("## Assessment")
    lines.append("")
    lines.append("The reader layer is human-readable enough for synthesis orientation. It remains generated prose and should be checked against source files before any claim is promoted.")
    if metrics["reader_missing"]:
        lines.append("")
        lines.append("## Missing Readers")
        lines.append("")
        for item in metrics["reader_missing"]:
            lines.append(f"- `{item}`")
    return "\n".join(lines) + "\n"


def render_promotion_queue_quality_review(metrics: dict) -> str:
    lines = [md_header("promotion_queue_quality_review_generated"), "# Promotion Queue Quality Review", ""]
    lines.append(f"Result: `{metrics['result']}`")
    lines.append("")
    lines.append("The promotion queue is a raw candidate backlog. It is useful for finding review material but too noisy for direct promotion.")
    lines.append("")
    lines.append("## Counts")
    lines.append("")
    lines.append(f"- Candidates: `{metrics['promotion_count']}`")
    lines.append(f"- Source conversations represented: `{metrics['promotion_sources']}`")
    lines.append(f"- Noisy or archival-process candidates: `{len(metrics['noisy_promotions'])}`")
    lines.append(f"- Overlong candidates: `{len(metrics['long_promotions'])}`")
    lines.append(f"- Candidates with `not_checked` repo conflict: `{metrics['not_checked_promotions']}`")
    lines.append("")
    lines.append("## Noisy Candidate Samples")
    lines.append("")
    for item in metrics["noisy_promotions"][:12]:
        lines.append(f"- `{item['id']}` `{item['source_conversation']}`: {item['claim'][:220]}")
    if not metrics["noisy_promotions"]:
        lines.append("- None detected by the current heuristic.")
    lines.append("")
    lines.append("## Assessment")
    lines.append("")
    lines.append("Promotion candidates should be triaged before reconciliation. Many entries are useful design-intent leads, but some are preservation-process notes or broad narrative summaries rather than clean patchable claims.")
    lines.append("")
    lines.append("## Recommended Fix")
    lines.append("")
    lines.append("Create `PROMOTION_TRIAGE_v0.md` after synthesis and classify candidates as serious, preserve-as-history, stale, noisy, rejected, or needs-user-decision.")
    return "\n".join(lines) + "\n"


def render_link_integrity_review(metrics: dict) -> str:
    lines = [md_header("link_integrity_review_generated"), "# Link Integrity Review", ""]
    lines.append(f"Result: `{'FAIL' if metrics['link_issues'] else 'PASS'}`")
    lines.append("")
    lines.append(f"Generated Markdown files checked: `{metrics['generated_markdown_count']}`")
    lines.append(f"Broken or unsafe links: `{len(metrics['link_issues'])}`")
    lines.append("")
    if metrics["link_issues"]:
        lines.append("| Document | Target | Issue |")
        lines.append("| --- | --- | --- |")
        for issue in metrics["link_issues"]:
            lines.append(f"| `{issue['doc']}` | `{issue['target']}` | `{issue['issue']}` |")
    else:
        lines.append("No broken or unsafe generated Markdown links were detected.")
    return "\n".join(lines) + "\n"


def parse_current_queue_constraints(repo_root: Path) -> Dict[str, str]:
    queue_path = repo_root / ".aide" / "queue" / "current.toml"
    constraints: Dict[str, str] = {}
    if not queue_path.exists():
        return constraints
    in_constraints = False
    for raw in queue_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("["):
            in_constraints = line == "[constraints]"
            continue
        if in_constraints and "=" in line:
            key, value = line.split("=", 1)
            constraints[key.strip()] = value.strip().strip('"')
    return constraints


def acceptance_result_from_disk(repo_root: Path) -> str:
    path = repo_root / CORPUS_ROOT / "_audit" / "INTAKE_ACCEPTANCE_REVIEW.md"
    if not path.exists():
        return "not_run"
    text = path.read_text(encoding="utf-8")
    match = re.search(r"Result:\s*`([^`]+)`", text)
    return match.group(1) if match else "unknown"


def reader_ref(c: Conversation) -> str:
    return f"[{c.title}](../_reader/by_chat/{c.slug}.md)"


def topic_refs(conversations: List[Conversation], topic: str, limit: int = 8) -> str:
    convs = [c for c in conversations if topic in c.topics]
    if not convs:
        return "none"
    return ", ".join(reader_ref(c) for c in convs[:limit])


def synthesis_metrics(repo_root: Path) -> dict:
    manifest, conversations = build_manifest(repo_root)
    findings, promotions = build_findings(repo_root, conversations)
    topic_counts = {
        topic: sum(1 for c in conversations if topic in c.topics)
        for topic in sorted(SYNTHESIS_TOPIC_EXPLANATIONS, key=sort_key)
    }
    contradiction_counts: Dict[str, int] = {}
    for finding in findings:
        contradiction_counts[finding.class_name] = contradiction_counts.get(finding.class_name, 0) + 1
    serious_topic_order = sorted(topic_counts.items(), key=lambda item: (-item[1], item[0]))
    constraints = parse_current_queue_constraints(repo_root)
    blocked_constraints = {key: value for key, value in constraints.items() if value == "BLOCKED"}
    decision_candidates = [
        {
            "title": "Promotion candidate triage",
            "why": "The raw promotion queue contains useful leads but also preservation-process noise.",
            "source": "../_promotion/PROMOTION_QUEUE.md",
        },
        {
            "title": "Workbench scope",
            "why": "Old conversations discuss Workbench as rich operator surface, but the current queue blocks broad Workbench UI.",
            "source": "../_wiki/topics/workbench.md",
        },
        {
            "title": "Renderer and platform boundary",
            "why": "Conversations repeatedly discuss renderer/platform plans, while current authority keeps rendering presentational and implementation scope blocked.",
            "source": "../_wiki/topics/platform.md",
        },
        {
            "title": "Provider and content boundaries",
            "why": "Provider, pack, and content discussions need separation from runtime module loading and package runtime blocks.",
            "source": "../_wiki/topics/content.md",
        },
        {
            "title": "World scale and fidelity roadmap",
            "why": "Universe, world, chronology, and simulation conversations need sequencing against current contracts and queue limits.",
            "source": "../_wiki/topics/worldgen.md",
        },
        {
            "title": "Release/publication meaning",
            "why": "Release/versioning conversations should remain planning until release publication authority opens.",
            "source": "../_wiki/topics/release.md",
        },
    ]
    return {
        "manifest": manifest,
        "conversations": conversations,
        "findings": findings,
        "promotions": promotions,
        "topic_counts": dict(serious_topic_order),
        "contradiction_counts": dict(sorted(contradiction_counts.items())),
        "constraints": constraints,
        "blocked_constraints": blocked_constraints,
        "acceptance_result": acceptance_result_from_disk(repo_root),
        "decision_candidates": decision_candidates,
    }


def write_synthesis(repo_root: Path) -> List[str]:
    metrics = synthesis_metrics(repo_root)
    root = repo_root / CORPUS_ROOT / "_synthesis"
    changed: List[str] = []
    changed += changed_path(root / "PROJECT_SYNTHESIS_BOOK_v0.md", render_project_synthesis_book(metrics), repo_root)
    changed += changed_path(root / "EXECUTIVE_BRIEF_v0.md", render_executive_brief(metrics), repo_root)
    changed += changed_path(root / "FULL_PROJECT_PICTURE_v0.md", render_full_project_picture(metrics), repo_root)
    changed += changed_path(root / "WHAT_NEEDS_DECISION_v0.md", render_what_needs_decision(metrics), repo_root)
    changed += changed_path(root / "CONTRADICTIONS_TO_RECONCILE_v0.md", render_contradictions_to_reconcile(metrics), repo_root)
    return changed


def synthesis_header(result: str) -> str:
    return md_header(result) + """Authority Class: advisory_synthesis
Promotion Status: not_promoted
Source Class: conversation_corpus_synthesis

"""


def render_topic_overview(metrics: dict) -> str:
    lines = []
    for topic, count in metrics["topic_counts"].items():
        if count == 0:
            continue
        explanation = SYNTHESIS_TOPIC_EXPLANATIONS.get(topic, "conversation-derived topic")
        lines.append(f"- `{topic}` ({count} conversations): {explanation}. Sources: {topic_refs(metrics['conversations'], topic, 5)}.")
    return "\n".join(lines)


def render_current_repo_truth_block(metrics: dict) -> str:
    blocked = ", ".join(f"`{key}`" for key in sorted(metrics["blocked_constraints"])) or "none listed"
    return f"""Current repo truth, as used by this synthesis:

- [README.md](../../../../README.md) describes Dominium as a deterministic, contract-governed simulation game and operating environment built on the Domino deterministic substrate.
- [docs/canon/constitution_v1.md](../../../canon/constitution_v1.md) binds determinism, process-only mutation, law-gated authority, no runtime mode flags, pack-driven integration, explicit refusal, and truth/perceived/render separation.
- [docs/canon/glossary_v1.md](../../../canon/glossary_v1.md) defines vocabulary such as Engine, Client, AuthorityContext, Domain, Derived artifact, and Contract.
- [AGENTS.md](../../../../AGENTS.md) and [docs/planning/AUTHORITY_ORDER.md](../../../planning/AUTHORITY_ORDER.md) keep archived conversations below canon, glossary, governance, contracts, current queue, and validated repo artifacts.
- [.aide/queue/current.toml](../../../../.aide/queue/current.toml) currently blocks broad feature work including: {blocked}.
"""


def render_project_synthesis_book(metrics: dict) -> str:
    conversations = metrics["conversations"]
    lines = [synthesis_header("project_synthesis_book_generated"), "# Dominium Conversation Corpus Synthesis Book v0", ""]
    lines.append("This book is a derived reading guide over the archived conversation corpus. It is not canon, not architecture doctrine, not a contract, and not an implementation plan.")
    lines.append("")
    lines.append("## 1. Status And Authority")
    lines.append("")
    lines.append(f"- Acceptance review result: `{metrics['acceptance_result']}`.")
    lines.append("- Authority class: `advisory_synthesis`.")
    lines.append("- Promotion status: `not_promoted`.")
    lines.append("- Current repo artifacts outrank every conversation-derived statement in this book.")
    lines.append("")
    lines.append("## 2. Executive Overview")
    lines.append("")
    lines.append("The archive describes Dominium as a long-horizon deterministic simulation product: a game, engine-backed operating environment, validation workbench, content platform, and governance-heavy repository. Across the conversations, the recurring intent is not to build a renderer-owned game loop or a pile of UI screens. The recurring intent is to preserve lawful simulation truth, expose it through command/result/evidence surfaces, and let products project that truth without mutating it.")
    lines.append("")
    lines.append("The current repo already establishes the strongest version of that principle through canon, glossary, README, and queue state. The conversation corpus adds historical design intent around world scale, Workbench, setup/launcher, release identity, provider/content boundaries, and future UI/editor experiences. Those claims remain advisory until reconciled and promoted.")
    lines.append("")
    lines.append("## 3. What Dominium Is Trying To Be")
    lines.append("")
    lines.append("Repo-established truth: Dominium is the official game/product/domain layer on top of Domino, the reusable deterministic substrate. It is concerned with invention, production, logistics, economics, settlement, trust, communication, and institutional power emerging from lawful simulation.")
    lines.append("")
    lines.append("Conversation-derived intent: the archive repeatedly extends that picture toward a broad universe-scale simulation platform, with real-world defaults, arbitrary authored packs, robust tooling, deterministic evidence, long-term portability, and a Workbench that makes the project inspectable and operable.")
    lines.append("")
    lines.append("## 4. Core Mental Model")
    lines.append("")
    lines.append("The current README gives the clearest spine: intent -> command -> capability/refusal check -> service or deterministic process -> result/document/snapshot -> diagnostics/evidence -> view/action model -> projection -> shell. The conversations mostly orbit that same model, even when they discuss UI, renderer, platform, setup, or release packaging.")
    lines.append("")
    lines.append("## 5. Engine / Game / Runtime / Product Boundaries")
    lines.append("")
    lines.append("Repo truth keeps Engine, Game, Client, Server, Workbench, setup, launcher, tools, contracts, and content in separate roles. Conversation-derived material reinforces the boundary: renderer and UI project state, clients issue intents, server/game/engine law remains authoritative, and tools validate or inspect rather than silently mutate truth.")
    lines.append("")
    lines.append(f"Representative sources: {topic_refs(conversations, 'architecture', 8)}.")
    lines.append("")
    lines.append("## 6. Determinism, Replay, And Provenance")
    lines.append("")
    lines.append("The canon makes determinism primary: ordering, reductions, RNG streams, replay, hash partitions, and provenance are non-negotiable. The corpus adds historical emphasis on deterministic world scale, portable builds, replay proofs, verification artifacts, and avoiding hidden fallback behavior.")
    lines.append("")
    lines.append(f"Representative sources: {topic_refs(conversations, 'determinism', 8)}.")
    lines.append("")
    lines.append("## 7. Law, Authority, Refusal, And Capability Model")
    lines.append("")
    lines.append("Current repo truth says authority permits attempts, law decides accept/refuse/transform, and refusals must be deterministic and auditable. Conversations often use different local language, but the recurring direction is aligned: no convenience bypass, no generated output as truth, and no old prompt as authority.")
    lines.append("")
    lines.append(f"Representative sources: {topic_refs(conversations, 'governance', 8)}.")
    lines.append("")
    lines.append("## 8. World, Reality, Scale, And Refinement Model")
    lines.append("")
    lines.append("Conversation-derived intent is expansive: worlds, planets, celestial systems, universe explorer concepts, chronology, spatial refinement, simulation domains, macro/micro transitions, and real-world defaults recur across the archive. This is a design-intent signal, not current implementation authority.")
    lines.append("")
    lines.append(f"Representative sources: {topic_refs(conversations, 'worldgen', 8)}.")
    lines.append("")
    lines.append("## 9. Timekeeping, Chronology, And 2038 Resilience")
    lines.append("")
    lines.append("Time appears as both a simulation domain and a platform durability concern. The archive repeatedly points to chronology, calendars, celestial alignment, 2038 resilience, and timestamp policy. Current promotion must verify all such claims against current contracts and language/platform baselines.")
    lines.append("")
    lines.append(f"Representative sources: {topic_refs(conversations, 'timekeeping', 8)}.")
    lines.append("")
    lines.append("## 10. Civilization, Institutions, Economy, Logistics")
    lines.append("")
    lines.append("The corpus frames Dominium around emergent production, logistics, economics, settlement, communication, trust, institutions, and power. These are project identity themes; they are not authorization to open gameplay or runtime work while the current queue blocks it.")
    lines.append("")
    lines.append(f"Representative sources: {topic_refs(conversations, 'simulation', 8)}.")
    lines.append("")
    lines.append("## 11. UI, Renderer, Workbench, And Tools")
    lines.append("")
    lines.append("The conversations strongly prefer a rich Workbench and eventual editor/operator surfaces. Current authority is narrower: broad Workbench UI, renderer implementation, and native GUI remain blocked. Therefore synthesis may describe intent, but follow-up tasks must stay contract/planning scoped until the queue opens implementation scope.")
    lines.append("")
    lines.append(f"Representative sources: {topic_refs(conversations, 'workbench', 8)}.")
    lines.append("")
    lines.append("## 12. AIDE, Codex, Governance, And Patch Workflow")
    lines.append("")
    lines.append("The archive treats AIDE/Codex/XStack as repo-control and patch-execution aids. Current repo truth agrees that they do not replace canon, contracts, review gates, or validation. Their correct role is bounded evidence-producing work, not direct semantic authority.")
    lines.append("")
    lines.append(f"Representative sources: {topic_refs(conversations, 'xstack_aide', 8)}.")
    lines.append("")
    lines.append("## 13. Release, Setup, Launcher, Platform, Portability")
    lines.append("")
    lines.append("Conversations cover setup, launcher, release identity, versioning, portability, platform support, and public distribution. Current queue still blocks release publication, so these remain planning and audit material unless a later reviewed task opens the scope.")
    lines.append("")
    lines.append(f"Representative sources: {topic_refs(conversations, 'release', 8)}.")
    lines.append("")
    lines.append("## 14. Content, Packs, Modding, Providers")
    lines.append("")
    lines.append("The corpus repeatedly returns to pack-driven composition, authored content, providers, binary/content boundaries, and modding. Canon requires pack-driven integration and explicit refusal for missing packs. Current queue blocks package runtime and provider runtime, so promotion must be careful.")
    lines.append("")
    lines.append(f"Representative sources: {topic_refs(conversations, 'content', 8)}.")
    lines.append("")
    lines.append("## 15. What Was Decided Across Conversations")
    lines.append("")
    lines.append("The strongest recurring conversation-level decisions are advisory: keep simulation truth deterministic, separate rendering from authority, keep Workbench a projection/inspection/control surface rather than truth owner, preserve source provenance, and avoid direct promotion from old chats. These are valuable because they align with current repo doctrine, but alignment is not the same as promotion.")
    lines.append("")
    lines.append("## 16. What Is Still Unresolved")
    lines.append("")
    for item in metrics["decision_candidates"]:
        lines.append(f"- {item['title']}: {item['why']} Source: [{item['source']}]({item['source']}).")
    lines.append("")
    lines.append("## 17. Contradictions And Drift")
    lines.append("")
    lines.append("The audit layer contains review triggers, not resolved contradictions. The main risk classes are conversation claims against current queue restrictions, stale external/platform claims, old docs/baseline drift, and conversation-vs-conversation disagreements.")
    lines.append("")
    for class_name, count in metrics["contradiction_counts"].items():
        lines.append(f"- `{class_name}`: `{count}` findings.")
    lines.append("")
    lines.append("## 18. Stale Claims And Verification Queue")
    lines.append("")
    lines.append("External platform, SDK, renderer, language baseline, release, provider, package runtime, and implementation claims must be rechecked. The synthesis should use those old claims to identify questions, not to assert current facts.")
    lines.append("")
    lines.append("## 19. Promotion Candidates")
    lines.append("")
    lines.append(f"The raw queue contains `{len(metrics['promotions'])}` generated candidates in [PROMOTION_QUEUE.md](../_promotion/PROMOTION_QUEUE.md). Acceptance review found the queue useful but noisy. It should be triaged before any candidate patch work.")
    lines.append("")
    lines.append("## 20. Recommended Reconciliation Roadmap")
    lines.append("")
    lines.append("1. Keep this synthesis advisory and archive-scoped.")
    lines.append("2. Build a claim review matrix against canon, glossary, AGENTS, current queue, contracts, schema law, and targeted current docs.")
    lines.append("3. Triage promotion candidates into serious, historical, stale, noisy, rejected, and needs-user-decision groups.")
    lines.append("4. Patch live docs only through narrow promotion tasks with named source claims and validation.")
    lines.append("")
    lines.append("## 21. Appendices")
    lines.append("")
    lines.append(render_current_repo_truth_block(metrics))
    lines.append("")
    lines.append("### Topic Coverage")
    lines.append("")
    lines.append(render_topic_overview(metrics))
    return "\n".join(lines) + "\n"


def render_executive_brief(metrics: dict) -> str:
    return synthesis_header("executive_brief_generated") + f"""# Executive Brief v0

The conversation archive now supports a derived project picture: Dominium is a deterministic, contract-governed simulation game and operating environment on top of Domino. The old conversations consistently point toward a broad product: simulation engine, official game/domain layer, Workbench, setup/launcher, content packs, release identity, portability, and repo governance.

This brief is not authority. Current truth remains in [README.md](../../../../README.md), [constitution_v1.md](../../../canon/constitution_v1.md), [glossary_v1.md](../../../canon/glossary_v1.md), [AGENTS.md](../../../../AGENTS.md), contracts, schema law, and current queue state.

## Current Signal

- Source conversations: `{metrics['manifest']['summary']['conversation_count']}`
- Source files: `{metrics['manifest']['summary']['source_file_count']}`
- Acceptance result: `{metrics['acceptance_result']}`
- Promotion candidates: `{len(metrics['promotions'])}`
- Audit findings: `{len(metrics['findings'])}`
- Blocked current queue scopes: `{', '.join(sorted(metrics['blocked_constraints']))}`

## Main Takeaway

The archive is ready for understanding and synthesis. It is not ready for direct promotion. The next review surface should compare the synthesis against current repo authority and reduce the raw promotion queue into a smaller decision backlog.
"""


def render_full_project_picture(metrics: dict) -> str:
    lines = [synthesis_header("full_project_picture_generated"), "# Full Project Picture v0", ""]
    lines.append("This map combines current repo orientation with conversation-derived design intent. When they differ, current repo authority wins.")
    lines.append("")
    lines.append("## Product Identity")
    lines.append("")
    lines.append("Domino is the deterministic substrate. Dominium is the official game, product, and domain layer. Workbench is a governed validation and inspection environment. Setup and launcher compose product instances. Tools validate, generate, audit, and migrate. Contracts and schema law define public identity and compatibility meaning.")
    lines.append("")
    lines.append("## Boundary Map")
    lines.append("")
    lines.append("| Surface | Current Role | Conversation-Derived Intent | Current Caution |")
    lines.append("| --- | --- | --- | --- |")
    lines.append("| Engine / Domino | Deterministic substrate | Reusable law-bound simulation foundation | Do not collapse into product UI |")
    lines.append("| Game / Dominium | Domain rules and official product meaning | Invention, logistics, institutions, world systems | Gameplay remains blocked by current queue |")
    lines.append("| Client / Renderer | Presentation and intent issuing | Rich visualization and projection | Renderer implementation is blocked |")
    lines.append("| Server | Authoritative multiplayer validation | Law and authority keeper | Must preserve deterministic proof |")
    lines.append("| Workbench | Validation and inspection surface | Rich operator and authoring future | Broad Workbench UI is blocked |")
    lines.append("| Setup / Launcher | Product composition and local orchestration | Install, repair, profiles, instances | Runtime package behavior remains constrained |")
    lines.append("| Content / Packs | Authored payload and pack-driven composition | Mods, providers, data-driven expansion | Provider/package runtime blocked |")
    lines.append("| AIDE / Codex / XStack | Repo-control and patch workflow aids | Evidence-producing governance layer | No authority replacement |")
    lines.append("")
    lines.append("## Topic Map")
    lines.append("")
    lines.append(render_topic_overview(metrics))
    lines.append("")
    lines.append("## Blocked Versus Open")
    lines.append("")
    lines.append("Open for derived archive work: reading, synthesis, crosswalks, contradiction review, promotion triage, and narrow docs-only planning. Blocked by current queue: broad Workbench UI, runtime module loader, provider runtime, package runtime, gameplay, renderer implementation, native GUI, and release publication.")
    return "\n".join(lines) + "\n"


def render_what_needs_decision(metrics: dict) -> str:
    lines = [synthesis_header("what_needs_decision_generated"), "# What Needs Decision v0", ""]
    lines.append("These are not decisions. They are review questions created by reading the conversation corpus after acceptance.")
    lines.append("")
    lines.append("| Decision Area | Why It Matters | Source | Current Disposition |")
    lines.append("| --- | --- | --- | --- |")
    for item in metrics["decision_candidates"]:
        lines.append(f"| {item['title']} | {item['why']} | [{item['source']}]({item['source']}) | `needs_user_or_repo_review` |")
    lines.append("")
    lines.append("## User-Level Questions")
    lines.append("")
    lines.append("- Which promotion candidates should become serious doc-update proposals?")
    lines.append("- Which conversation themes are only historical and should be preserved without promotion?")
    lines.append("- Which blocked queue areas should remain blocked even if old conversations discuss them as next work?")
    lines.append("- Which product names and boundaries should be considered stable enough for a current-doc crosswalk?")
    lines.append("- Which world/time/civilization ambitions are near-term planning versus long-term vision?")
    return "\n".join(lines) + "\n"


def render_contradictions_to_reconcile(metrics: dict) -> str:
    lines = [synthesis_header("contradictions_to_reconcile_generated"), "# Contradictions To Reconcile v0", ""]
    lines.append("This document summarizes contradiction classes that should feed the reconciliation crosswalk. It does not resolve them.")
    lines.append("")
    lines.append("## Counts By Class")
    lines.append("")
    for class_name, count in metrics["contradiction_counts"].items():
        lines.append(f"- `{class_name}`: `{count}`")
    lines.append("")
    lines.append("## Highest-Priority Classes")
    lines.append("")
    lines.append("- `conversation_vs_current_queue`: old work suggestions that touch currently blocked scope.")
    lines.append("- `conversation_vs_docs`: old baseline or architecture statements that may drift from current README/canon.")
    lines.append("- `stale_external_claim`: external platform, SDK, language, renderer, or runtime claims needing current verification.")
    lines.append("- `conversation_vs_conversation`: disagreements among old conversations that need review before promotion.")
    lines.append("")
    lines.append("## Sample Findings")
    lines.append("")
    for finding in metrics["findings"][:30]:
        lines.append(f"- `{finding.finding_id}` `{finding.class_name}` `{finding.source_conversation}`: {finding.claim}")
    lines.append("")
    lines.append("## Reconciliation Rule")
    lines.append("")
    lines.append("Resolve nothing by convenience. Check canon, glossary, AGENTS, authority order, current queue, contracts/schema law, and targeted current docs before promoting any claim.")
    return "\n".join(lines) + "\n"


def validate_outputs(repo_root: Path) -> List[str]:
    errors: List[str] = []
    root = repo_root / CORPUS_ROOT
    manifest_path = root / "_intake" / "corpus_manifest.json"
    if not manifest_path.exists():
        errors.append("missing _intake/corpus_manifest.json")
        return errors
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"manifest JSON parse failed: {exc}")
        return errors
    required_docs = [
        root / "README.md",
        root / "INDEX.md",
        root / "_intake" / "CORPUS_MANIFEST.md",
        root / "_intake" / "PACKAGE_COMPLETENESS.md",
        root / "_intake" / "SOURCE_PROVENANCE.md",
        root / "_reader" / "conversation_reader_index.md",
        root / "_audit" / "CONTRADICTION_MATRIX.md",
        root / "_promotion" / "PROMOTION_QUEUE.md",
        root / "_wiki" / "index.md",
    ]
    acceptance_docs = [
        root / "_audit" / "INTAKE_ACCEPTANCE_REVIEW.md",
        root / "_audit" / "READER_QUALITY_REVIEW.md",
        root / "_audit" / "PROMOTION_QUEUE_QUALITY_REVIEW.md",
        root / "_audit" / "LINK_INTEGRITY_REVIEW.md",
    ]
    if any(doc.exists() for doc in acceptance_docs):
        required_docs.extend(acceptance_docs)
    synthesis_docs = [
        root / "_synthesis" / "PROJECT_SYNTHESIS_BOOK_v0.md",
        root / "_synthesis" / "EXECUTIVE_BRIEF_v0.md",
        root / "_synthesis" / "FULL_PROJECT_PICTURE_v0.md",
        root / "_synthesis" / "WHAT_NEEDS_DECISION_v0.md",
        root / "_synthesis" / "CONTRADICTIONS_TO_RECONCILE_v0.md",
    ]
    if any(doc.exists() for doc in synthesis_docs):
        required_docs.extend(synthesis_docs)
    if not (root / "_intake" / "SHA256SUMS.txt").exists():
        errors.append("missing generated doc: docs/archive/conversations/_intake/SHA256SUMS.txt")
    for doc in required_docs:
        if not doc.exists():
            errors.append(f"missing generated doc: {normalize_rel(doc, repo_root)}")
        else:
            text = doc.read_text(encoding="utf-8")
            for field_name in ["Status:", "Last Reviewed:", "Stability:", "Result:", "Binding Sources:"]:
                if field_name not in text[:500]:
                    errors.append(f"missing header field {field_name} in {normalize_rel(doc, repo_root)}")
    for conv in manifest.get("conversations", []):
        source_path = repo_root / conv["path"]
        if not source_path.exists():
            errors.append(f"missing source folder: {conv['path']}")
        reader = root / "_reader" / "by_chat" / f"{conv['slug']}.md"
        if not reader.exists():
            errors.append(f"missing reader page: {normalize_rel(reader, repo_root)}")
        for file_entry in conv.get("files", []):
            file_path = repo_root / file_entry["path"]
            if not file_path.exists():
                errors.append(f"missing source file: {file_entry['path']}")
            elif sha256_file(file_path) != file_entry["sha256"]:
                errors.append(f"sha mismatch: {file_entry['path']}")
    return errors


def write_all(repo_root: Path, phases: Sequence[str]) -> List[str]:
    changed: List[str] = []
    if "phase1" in phases:
        changed.extend(write_phase1(repo_root))
    if "phase2" in phases:
        changed.extend(write_phase2(repo_root))
    if "phase3" in phases:
        changed.extend(write_phase3(repo_root))
    if "phase4" in phases:
        changed.extend(write_phase4(repo_root))
    if "acceptance" in phases:
        changed.extend(write_acceptance(repo_root))
    if "synthesis" in phases:
        changed.extend(write_synthesis(repo_root))
    return sorted(set(changed), key=sort_key)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build or validate conversation corpus outputs.")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument(
        "command",
        choices=["inventory", "readers", "audit", "wiki", "acceptance", "synthesis", "all", "validate"],
        help="Operation to run.",
    )
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    if args.command == "inventory":
        changed = write_all(repo_root, ["phase1"])
        print(json.dumps({"changed": changed, "phase": "inventory"}, indent=2, sort_keys=True))
        return 0
    if args.command == "readers":
        changed = write_all(repo_root, ["phase2"])
        print(json.dumps({"changed": changed, "phase": "readers"}, indent=2, sort_keys=True))
        return 0
    if args.command == "audit":
        changed = write_all(repo_root, ["phase3"])
        print(json.dumps({"changed": changed, "phase": "audit"}, indent=2, sort_keys=True))
        return 0
    if args.command == "wiki":
        changed = write_all(repo_root, ["phase4"])
        print(json.dumps({"changed": changed, "phase": "wiki"}, indent=2, sort_keys=True))
        return 0
    if args.command == "acceptance":
        changed = write_all(repo_root, ["acceptance"])
        print(json.dumps({"changed": changed, "phase": "acceptance"}, indent=2, sort_keys=True))
        return 0
    if args.command == "synthesis":
        changed = write_all(repo_root, ["synthesis"])
        print(json.dumps({"changed": changed, "phase": "synthesis"}, indent=2, sort_keys=True))
        return 0
    if args.command == "all":
        changed = write_all(repo_root, ["phase1", "phase2", "phase3", "phase4"])
        print(json.dumps({"changed": changed, "phase": "all"}, indent=2, sort_keys=True))
        return 0
    if args.command == "validate":
        errors = validate_outputs(repo_root)
        if errors:
            print(json.dumps({"result": "fail", "errors": errors}, indent=2, sort_keys=True))
            return 1
        print(json.dumps({"result": "pass"}, indent=2, sort_keys=True))
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
