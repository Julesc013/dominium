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
MANAGED_DIRS = {"_intake", "_reader", "_wiki", "_audit", "_promotion", "__unsorted"}
HEADER_BINDING = (
    "`docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, "
    "`AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, "
    "`docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`"
)

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
        primary = link(c.primary_source) if c.primary_source else "none"
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
        root / "_intake" / "SHA256SUMS.txt",
        root / "_reader" / "conversation_reader_index.md",
        root / "_audit" / "CONTRADICTION_MATRIX.md",
        root / "_promotion" / "PROMOTION_QUEUE.md",
        root / "_wiki" / "index.md",
    ]
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
    return sorted(set(changed), key=sort_key)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build or validate conversation corpus outputs.")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument(
        "command",
        choices=["inventory", "readers", "audit", "wiki", "all", "validate"],
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
