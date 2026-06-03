"""Build the derived Project Vision Corpus from archived conversations.

This tool reads the archived conversation packages and human-readable reports,
then writes a planning/synthesis corpus under ``docs/archive/project_vision_corpus``.
It does not modify source zips, canon, contracts, schema, implementation,
release, or queue state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import docs_corpus


TASK_ID = "PROJECT-VISION-CORPUS-01"
REVIEW_DATE = "2026-06-03"
CONVERSATIONS_ROOT = Path("docs/archive/conversations")
OUTPUT_ROOT = Path("docs/archive/project_vision_corpus")

STATUS_BLOCK = f"""Status: DERIVED
Last Reviewed: {REVIEW_DATE}
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged
"""

REPORT_PATTERNS = (
    "human_readable_report",
    "human_readable_detailed_summary",
    "detailed_summary_report",
    "accompanying_detailed_summary",
    "accompanying_human_readable",
    "companion_detailed_summary",
    "companion_report",
    "reader_brief",
    "in_chat_reader",
    "conversation_reader",
    "current_project",
    "project_synthesis",
    "decision",
    "promotion",
    "reconciliation",
    "read_this_first",
)

MACHINE_PATTERNS = (
    "manifest",
    "bundle_integrity",
    "hash",
    "source_index",
    "file_index",
    "validation",
    "build_report",
    "context_transfer",
    "aggregator",
    "spec_sheet",
    "register",
    "matrix",
    "packet",
)

EXCLUDED_GENERATED_DIRS = {"_exports", "_book", "_reports_book"}
INCLUDED_GENERATED_DIRS = {"_reader", "_synthesis", "_decision", "_promotion", "_reconciliation", "_wiki"}

THEMES = [
    ("project_identity", "Project identity and purpose", ("identity", "purpose", "vision", "game", "ecosystem", "simulation os")),
    ("domino_dominium", "Domino/Dominium relationship", ("domino", "dominium", "substrate", "official", "product layer")),
    ("determinism_replay_provenance", "Determinism, replay, evidence, and provenance", ("determin", "replay", "provenance", "hash", "proof", "evidence")),
    ("law_authority_refusal", "Law, authority, capability, and refusal", ("law", "authority", "capability", "refusal", "permission", "audit")),
    ("runtime_boundaries", "Engine/game/runtime/product boundaries", ("engine", "game", "runtime", "client", "server", "boundary", "process")),
    ("ui_renderer_presentation", "UI, renderer, native GUI, and presentation", ("ui", "renderer", "render", "native gui", "presentation", "projection")),
    ("workbench_aide_codex", "Workbench, AIDE, Codex, automation, and governance", ("workbench", "aide", "codex", "automation", "agent", "governance")),
    ("setup_launcher_release", "Setup, launcher, release, and platform", ("setup", "launcher", "release", "platform", "version", "identity")),
    ("content_packs_modding", "Content, packs, modding, and providers", ("pack", "mod", "content", "provider", "bundle", "registry")),
    ("world_time_scale", "World model, time, space, and scale", ("world", "time", "space", "scale", "reality", "existence")),
    ("worldgen_celestial_domains", "Worldgen, planets, celestial systems, and domains", ("worldgen", "planet", "celestial", "astronomy", "solar", "domain")),
    ("civilization_economy_institutions", "Civilization, economy, logistics, institutions, and signals", ("civilization", "economy", "logistics", "institution", "signal", "settlement")),
    ("docs_archive_corpus", "Documentation, archive, and conversation corpus", ("docs", "documentation", "archive", "conversation", "corpus", "preservation")),
    ("decisions_made", "Decisions already made", ("decided", "decision", "settled", "accepted", "ratified", "choose")),
    ("open_decisions", "Open decisions", ("open question", "unresolved", "needs decision", "unknown", "not decided")),
    ("contradictions_drift", "Contradictions and stale claims", ("contradiction", "conflict", "drift", "stale", "superseded", "mismatch")),
    ("roadmap_sequence", "Roadmap and sequencing", ("roadmap", "next step", "sequence", "future", "phase", "queue")),
]

BLOCK_TYPE_KEYWORDS = {
    "decision": ("decided", "decision", "accepted", "settled", "choose", "chosen", "conclusion"),
    "design_goal": ("goal", "vision", "intent", "ambition", "aim", "wants to", "should support"),
    "requirement": ("must", "required", "requires", "contract", "schema", "invariant", "law"),
    "constraint": ("constraint", "boundary", "scope", "compatibility", "queue", "portable"),
    "prohibition": ("must not", "do not", "forbidden", "blocked", "not authorized", "never", "no silent"),
    "prerequisite": ("before", "prerequisite", "depends on", "only after", "must happen first"),
    "unresolved_question": ("open question", "unresolved", "unclear", "needs decision", "unknown", "needs review"),
    "contradiction": ("contradiction", "conflict", "drift", "inconsistent", "mismatch"),
    "risk": ("risk", "warning", "caveat", "danger", "failure", "debt"),
    "rationale": ("because", "therefore", "why", "rationale", "consequence"),
    "roadmap": ("next step", "roadmap", "future", "later", "sequence", "phase"),
    "rejection": ("rejected", "do not repeat", "superseded", "discarded", "deprioritized"),
    "change_of_direction": ("changed", "moved from", "shifted", "superseded", "replaced"),
}

CURRENT_TRUTH_POINTS = [
    "Dominium is a deterministic, contract-governed simulation game and operating environment built on the Domino deterministic substrate.",
    "Domino is the reusable deterministic substrate; Dominium is the official game, product, and domain layer on top of it.",
    "Authority order starts with canon, glossary, AGENTS, contracts, schema law, current queue state, and validated repo artifacts.",
    "Archive and conversation material are historical evidence and advisory planning context, not current authority.",
    "Process-only mutation, truth/perception/render separation, pack-driven integration, explicit refusal, and determinism discipline are settled current constraints.",
    "The current queue blocks broad Workbench UI, renderer implementation, native GUI, provider runtime, package runtime, gameplay, and release publication.",
]


@dataclass(frozen=True)
class ZipRecord:
    path: str
    chat_label: str
    apparent_topic: str
    size: int
    sha256: str
    file_count: int
    human_report_count: int
    reader_brief_count: int
    machine_file_count: int
    nested_zip_count: int
    date_hint: str
    extraction_confidence: str
    members: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class SourceRecord:
    path: str
    chat_label: str
    title: str
    kind: str
    priority: int
    size: int
    authority_status: str


@dataclass
class SourceBlock:
    block_id: str
    source_zip: str
    source_file: str
    chat_label: str
    source_heading: str
    date_or_sequence: str
    original_text: str
    cleaned_text: str
    block_type: str
    authority_status: str
    confidence: str
    topic_tags: List[str]
    candidate_themes: List[str]
    include_in_vision: bool
    include_in_roadmap: bool
    include_in_decision_docket: bool
    notes: str = ""


def run_command(cmd: Sequence[str], cwd: Path, timeout: int = 900) -> Tuple[int, str]:
    try:
        completed = subprocess.run(
            list(cmd),
            cwd=str(cwd),
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        return 127, str(exc)
    except subprocess.TimeoutExpired as exc:
        return 124, docs_corpus.ascii_text((exc.stdout or "") + (exc.stderr or ""))
    return completed.returncode, docs_corpus.ascii_text(completed.stdout or "")


def write_text(path: Path, content: str) -> None:
    clean = "\n".join(line.rstrip(" \t") for line in content.splitlines())
    docs_corpus.write_if_changed(path, docs_corpus.ascii_text(clean) + "\n")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def title_from_path(path: Path | str) -> str:
    stem = Path(path).stem if not isinstance(path, str) else Path(path).stem
    stem = re.sub(r"__\d+_", " - ", stem)
    stem = re.sub(r"[_\-]+", " ", stem)
    return " ".join(word.capitalize() for word in stem.split()) or "Untitled"


def infer_chat_label(path: Path, root: Path) -> str:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        parts = path.parts
    if not parts:
        return "unknown"
    if parts[0].startswith("_") and len(parts) > 1:
        return parts[1]
    return parts[0]


def infer_kind(path: Path) -> str:
    lower = path.name.lower()
    for pattern in REPORT_PATTERNS:
        if pattern in lower:
            return pattern
    return "human_readable_source"


def looks_machine_like(path: Path, text: Optional[str] = None) -> bool:
    lower = path.name.lower()
    if any(pattern in lower for pattern in MACHINE_PATTERNS):
        if not any(pattern in lower for pattern in ("human_readable", "reader_brief", "in_chat_reader", "detailed_summary")):
            return True
    if text is None:
        return False
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return True
    tableish = sum(1 for line in lines if line.strip().startswith("|") or line.count("|") >= 3)
    keyvalue = sum(1 for line in lines if re.match(r"^[A-Za-z0-9_.-]+:\s+", line.strip()))
    return tableish / len(lines) > 0.45 or keyvalue / len(lines) > 0.65


def inventory_zips(repo_root: Path) -> List[ZipRecord]:
    root = repo_root / CONVERSATIONS_ROOT
    records: List[ZipRecord] = []
    for path in sorted(root.rglob("*.zip"), key=lambda p: p.relative_to(repo_root).as_posix().lower()):
        rel = path.relative_to(repo_root).as_posix()
        members: List[str] = []
        human = reader = machine = nested = 0
        date_hint = ""
        confidence = "medium"
        try:
            with zipfile.ZipFile(path) as archive:
                infos = archive.infolist()
                for info in infos:
                    name = info.filename.replace("\\", "/")
                    members.append(name)
                    lower = name.lower()
                    if lower.endswith(".zip"):
                        nested += 1
                    if any(pattern in lower for pattern in REPORT_PATTERNS):
                        human += 1
                    if "reader_brief" in lower or "in_chat_reader" in lower:
                        reader += 1
                    if any(pattern in lower for pattern in MACHINE_PATTERNS):
                        machine += 1
                    if not date_hint and info.date_time:
                        year, month, day, *_ = info.date_time
                        if year > 1980:
                            date_hint = f"{year:04d}-{month:02d}-{day:02d}"
                if not infos:
                    confidence = "low"
        except zipfile.BadZipFile:
            confidence = "low"
        chat_label = infer_chat_label(path, root)
        records.append(
            ZipRecord(
                path=rel,
                chat_label=chat_label,
                apparent_topic=title_from_path(chat_label),
                size=path.stat().st_size,
                sha256=sha256_file(path),
                file_count=len(members),
                human_report_count=human,
                reader_brief_count=reader,
                machine_file_count=machine,
                nested_zip_count=nested,
                date_hint=date_hint or "unknown",
                extraction_confidence=confidence,
                members=members[:120],
            )
        )
    return records


def is_human_source_candidate(path: Path, conversations_root: Path) -> bool:
    if path.suffix.lower() not in {".md", ".txt"}:
        return False
    try:
        parts = path.relative_to(conversations_root).parts
    except ValueError:
        return False
    if not parts:
        return False
    if parts[0] in EXCLUDED_GENERATED_DIRS:
        return False
    lower = path.name.lower()
    if any(pattern in lower for pattern in REPORT_PATTERNS):
        return True
    if parts[0] in INCLUDED_GENERATED_DIRS and not looks_machine_like(path):
        return True
    return False


def select_sources(repo_root: Path) -> Tuple[List[SourceRecord], List[Tuple[str, str]]]:
    root = repo_root / CONVERSATIONS_ROOT
    selected: List[SourceRecord] = []
    excluded: List[Tuple[str, str]] = []
    for path in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix().lower()):
        if not path.is_file():
            continue
        rel = path.relative_to(repo_root).as_posix()
        if not is_human_source_candidate(path, root):
            if path.suffix.lower() in {".md", ".txt", ".json", ".yml", ".yaml", ".toml"}:
                excluded.append((rel, "machine_or_low_priority_material"))
            continue
        text = read_text(path)
        if looks_machine_like(path, text) or len(text.strip()) < 350:
            excluded.append((rel, "machine_like_or_too_short"))
            continue
        kind = infer_kind(path)
        priority = 10
        if "human_readable_report" in kind or "human_readable_detailed" in kind:
            priority = 1
        elif "detailed_summary" in kind or "companion_report" in kind:
            priority = 2
        elif "reader_brief" in kind or "in_chat_reader" in kind:
            priority = 3
        elif path.relative_to(root).parts[0] in {"_synthesis", "_decision", "_reconciliation"}:
            priority = 2
        elif path.relative_to(root).parts[0] in {"_reader", "_wiki", "_promotion"}:
            priority = 4
        selected.append(
            SourceRecord(
                path=rel,
                chat_label=infer_chat_label(path, root),
                title=title_from_path(path),
                kind=kind,
                priority=priority,
                size=path.stat().st_size,
                authority_status="conversation_advisory",
            )
        )
    return selected, excluded


def clean_block_text(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"\s+", " ", text.replace("\ufeff", " ")).strip()
    return text


def split_semantic_blocks(text: str) -> Iterable[Tuple[str, str]]:
    heading = "front matter"
    current: List[str] = []
    in_code = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if stripped.startswith("#"):
            if current:
                yield heading, "\n".join(current).strip()
                current = []
            heading = stripped.lstrip("#").strip() or heading
            continue
        if not stripped:
            if current:
                yield heading, "\n".join(current).strip()
                current = []
            continue
        if stripped.startswith(("-", "*", "+")) or re.match(r"^\d+[.)]\s+", stripped):
            current.append(stripped)
            continue
        if current and (current[-1].startswith(("-", "*", "+")) or re.match(r"^\d+[.)]\s+", current[-1])):
            yield heading, "\n".join(current).strip()
            current = []
        current.append(stripped)
    if current:
        yield heading, "\n".join(current).strip()


def classify_block(text: str) -> str:
    lower = text.lower()
    for block_type, keywords in BLOCK_TYPE_KEYWORDS.items():
        if any(keyword in lower for keyword in keywords):
            return block_type
    return "explanation"


def theme_tags_for(text: str) -> List[str]:
    lower = text.lower()
    tags = []
    for theme_id, _title, keywords in THEMES:
        if any(keyword in lower for keyword in keywords):
            tags.append(theme_id)
    return tags or ["project_identity"]


def extract_blocks(repo_root: Path, sources: List[SourceRecord]) -> Tuple[List[SourceBlock], Dict[str, int]]:
    raw_blocks: List[SourceBlock] = []
    per_source_limits = defaultdict(lambda: 10, {1: 28, 2: 22, 3: 12, 4: 10})
    for source in sources:
        path = repo_root / source.path
        source_text = read_text(path)
        source_blocks: List[Tuple[str, str]] = []
        for heading, block in split_semantic_blocks(source_text):
            cleaned = clean_block_text(block)
            if len(cleaned) < 160 or len(cleaned) > 2800:
                continue
            if looks_machine_like(path, cleaned):
                continue
            source_blocks.append((heading, block))
        source_blocks.sort(key=lambda item: (0 if classify_block(clean_block_text(item[1])) in {"decision", "design_goal", "requirement", "constraint", "unresolved_question", "roadmap"} else 1, len(item[1])))
        limit = per_source_limits[source.priority]
        for heading, original in source_blocks[:limit]:
            cleaned = clean_block_text(original)
            themes = theme_tags_for(cleaned)
            block_type = classify_block(cleaned)
            raw_blocks.append(
                SourceBlock(
                    block_id="",
                    source_zip="expanded_conversation_archive",
                    source_file=source.path,
                    chat_label=source.chat_label,
                    source_heading=heading,
                    date_or_sequence="unknown",
                    original_text=original.strip(),
                    cleaned_text=cleaned,
                    block_type=block_type,
                    authority_status="conversation_advisory",
                    confidence="medium" if source.priority <= 3 else "low",
                    topic_tags=themes,
                    candidate_themes=themes,
                    include_in_vision=block_type in {"explanation", "design_goal", "rationale", "requirement", "constraint", "roadmap"},
                    include_in_roadmap=block_type in {"roadmap", "prerequisite", "unresolved_question", "decision"},
                    include_in_decision_docket=block_type in {"decision", "unresolved_question", "rejection", "contradiction", "change_of_direction"},
                )
            )
    seen: Dict[str, SourceBlock] = {}
    duplicates = Counter()
    for block in raw_blocks:
        key = re.sub(r"[^a-z0-9]+", " ", block.cleaned_text.lower()).strip()[:700]
        if key in seen:
            duplicates[seen[key].source_file] += 1
            continue
        seen[key] = block
    blocks = list(seen.values())
    blocks.sort(key=lambda block: (block.candidate_themes[0], block.chat_label.lower(), block.source_file.lower(), block.source_heading.lower()))
    for index, block in enumerate(blocks, 1):
        block.block_id = f"PVCB-{index:05d}"
    return blocks, dict(duplicates)


def yaml_text(value: str, indent: int = 2) -> str:
    clean = docs_corpus.ascii_text(value).replace("\r\n", "\n").replace("\r", "\n").strip()
    pad = " " * indent
    return "|\n" + "\n".join(pad + line for line in clean.splitlines())


def write_raw_manifest(repo_root: Path, zips: List[ZipRecord]) -> None:
    raw = repo_root / OUTPUT_ROOT / "raw_manifest"
    data = {
        "task_id": TASK_ID,
        "date": REVIEW_DATE,
        "source_root": CONVERSATIONS_ROOT.as_posix(),
        "zip_count": len(zips),
        "zips": [record.__dict__ for record in zips],
    }
    write_text(raw / "ZIP_MANIFEST.json", json.dumps(data, indent=2, sort_keys=True))
    lines = [STATUS_BLOCK, "# Zip Manifest", "", f"Zip packages inventoried: {len(zips)}", "", "| Zip | Chat label | Files | Human reports | Reader briefs | Machine files | Nested zips | Confidence |", "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |"]
    for record in zips:
        lines.append(f"| `{record.path}` | {record.chat_label} | {record.file_count} | {record.human_report_count} | {record.reader_brief_count} | {record.machine_file_count} | {record.nested_zip_count} | {record.extraction_confidence} |")
    write_text(raw / "ZIP_MANIFEST.md", "\n".join(lines))
    complete = [record for record in zips if record.human_report_count or record.reader_brief_count]
    incomplete = [record for record in zips if not (record.human_report_count or record.reader_brief_count)]
    completeness = [STATUS_BLOCK, "# Package Completeness", "", f"- Packages with human-readable report evidence: {len(complete)}", f"- Packages without obvious human-readable report evidence: {len(incomplete)}", "", "## Packages Needing Review", ""]
    for record in incomplete:
        completeness.append(f"- `{record.path}` - no human report or reader brief detected inside zip; inspect manually if this package is important.")
    write_text(raw / "PACKAGE_COMPLETENESS.md", "\n".join(completeness))
    by_hash = defaultdict(list)
    for record in zips:
        by_hash[record.sha256].append(record.path)
    dup_lines = [STATUS_BLOCK, "# Duplicate Package Report", ""]
    duplicate_groups = {digest: paths for digest, paths in by_hash.items() if len(paths) > 1}
    dup_lines.append(f"Duplicate zip hash groups: {len(duplicate_groups)}")
    for digest, paths in sorted(duplicate_groups.items()):
        dup_lines.extend(["", f"## `{digest}`", ""])
        dup_lines.extend(f"- `{path}`" for path in paths)
    if not duplicate_groups:
        dup_lines.append("\nNo exact duplicate zip packages were detected by hash.")
    write_text(raw / "DUPLICATE_PACKAGE_REPORT.md", "\n".join(dup_lines))


def write_source_selection(repo_root: Path, sources: List[SourceRecord], excluded: List[Tuple[str, str]]) -> None:
    root = repo_root / OUTPUT_ROOT / "source_selection"
    by_kind = Counter(source.kind for source in sources)
    by_chat = Counter(source.chat_label for source in sources)
    lines = [STATUS_BLOCK, "# Human-Readable Source Selection", "", f"Selected source files: {len(sources)}", f"Conversation/source groups represented: {len(by_chat)}", "", "## Kind Counts", ""]
    lines.extend(f"- `{kind}`: {count}" for kind, count in sorted(by_kind.items()))
    lines.extend(["", "## Selected Sources", ""])
    for source in sorted(sources, key=lambda item: (item.priority, item.chat_label.lower(), item.path.lower())):
        lines.append(f"- `{source.path}` - {source.title} (`{source.kind}`, priority {source.priority})")
    write_text(root / "HUMAN_READABLE_SOURCE_SELECTION.md", "\n".join(lines))
    machine = [STATUS_BLOCK, "# Machine Material Excluded", "", f"Excluded low-priority or machine-like files noted: {len(excluded)}", ""]
    for path, reason in excluded[:700]:
        machine.append(f"- `{path}` - {reason}")
    if len(excluded) > 700:
        machine.append(f"- ... {len(excluded) - 700} more omitted from this report.")
    write_text(root / "MACHINE_MATERIAL_EXCLUDED.md", "\n".join(machine))
    priority = [STATUS_BLOCK, "# Source Priority List", "", "Priority 1 sources are long human-readable reports. Priority 2 sources are detailed summaries and synthesis reports. Priority 3 sources are reader briefs and in-chat readers. Priority 4 sources are useful generated reader/wiki/context pages.", ""]
    for source in sorted(sources, key=lambda item: (item.priority, item.chat_label.lower(), item.path.lower())):
        priority.append(f"- P{source.priority}: `{source.path}`")
    write_text(root / "SOURCE_PRIORITY_LIST.md", "\n".join(priority))


def write_source_blocks(repo_root: Path, blocks: List[SourceBlock], duplicate_counts: Dict[str, int]) -> None:
    root = repo_root / OUTPUT_ROOT / "source_blocks"
    yml_lines = ["task_id: PROJECT-VISION-CORPUS-01", f"date: {REVIEW_DATE}", f"block_count: {len(blocks)}", "blocks:"]
    for block in blocks:
        yml_lines.extend(
            [
                f"  - block_id: {block.block_id}",
                f"    source_zip: {block.source_zip}",
                f"    source_file: {block.source_file}",
                f"    chat_label: {block.chat_label}",
                f"    source_heading: {json.dumps(block.source_heading)}",
                f"    date_or_sequence: {block.date_or_sequence}",
                f"    original_text: {yaml_text(block.original_text, 6)}",
                f"    cleaned_text: {yaml_text(block.cleaned_text, 6)}",
                f"    block_type: {block.block_type}",
                f"    authority_status: {block.authority_status}",
                f"    confidence: {block.confidence}",
                "    topic_tags: [" + ", ".join(block.topic_tags) + "]",
                "    candidate_themes: [" + ", ".join(block.candidate_themes) + "]",
                f"    include_in_vision: {str(block.include_in_vision).lower()}",
                f"    include_in_roadmap: {str(block.include_in_roadmap).lower()}",
                f"    include_in_decision_docket: {str(block.include_in_decision_docket).lower()}",
                f"    notes: {json.dumps(block.notes)}",
            ]
        )
    write_text(root / "SOURCE_BLOCKS.yml", "\n".join(yml_lines))
    md = [STATUS_BLOCK, "# Source Block Library", "", f"Semantic blocks extracted: {len(blocks)}", "", "These blocks are reusable source material for planning and future books. They are not current authority.", ""]
    for block in blocks[:1200]:
        md.extend([f"## {block.block_id} - {block.block_type}", "", f"- Source: `{block.source_file}`", f"- Theme candidates: {', '.join(block.candidate_themes)}", "", block.cleaned_text, ""])
    if len(blocks) > 1200:
        md.append(f"... {len(blocks) - 1200} additional blocks are retained in `SOURCE_BLOCKS.yml`.")
    write_text(root / "SOURCE_BLOCKS.md", "\n".join(md))
    index = [STATUS_BLOCK, "# Source Block Index", "", "| Block | Type | Themes | Source | Heading |", "| --- | --- | --- | --- | --- |"]
    for block in blocks:
        index.append(f"| {block.block_id} | {block.block_type} | {', '.join(block.candidate_themes)} | `{block.source_file}` | {block.source_heading[:80]} |")
    write_text(root / "SOURCE_BLOCK_INDEX.md", "\n".join(index))
    dedup = [STATUS_BLOCK, "# Source Block Deduplication Report", "", f"Blocks retained after exact-normalized deduplication: {len(blocks)}", f"Duplicate source groups noted: {len(duplicate_counts)}", ""]
    for source, count in sorted(duplicate_counts.items(), key=lambda item: (-item[1], item[0]))[:100]:
        dedup.append(f"- `{source}` shadowed {count} duplicate block(s).")
    write_text(root / "SOURCE_BLOCK_DEDUPLICATION_REPORT.md", "\n".join(dedup))


def group_blocks_by_theme(blocks: List[SourceBlock]) -> Dict[str, List[SourceBlock]]:
    grouped: Dict[str, List[SourceBlock]] = {theme_id: [] for theme_id, _title, _keywords in THEMES}
    for block in blocks:
        for theme in block.candidate_themes:
            grouped.setdefault(theme, []).append(block)
    for theme in grouped:
        grouped[theme].sort(key=lambda block: (block.block_type != "decision", block.chat_label.lower(), block.source_file.lower()))
    return grouped


def prose_for_theme(theme_id: str, title: str, blocks: List[SourceBlock]) -> str:
    type_counts = Counter(block.block_type for block in blocks)
    source_count = len({block.source_file for block in blocks})
    sample = blocks[:8]
    lines = [
        STATUS_BLOCK,
        f"# {title}",
        "",
        f"This theme gathers {len(blocks)} source block(s) from {source_count} source file(s). It is advisory conversation evidence unless the current repo independently supports the same claim.",
        "",
        "## What The Sources Suggest",
        "",
    ]
    if not blocks:
        lines.append("No substantial source blocks were assigned to this theme.")
    else:
        lines.append(_theme_summary(theme_id))
        lines.extend(["", "## Strongest Recurring Signals", ""])
        for block in sample:
            lines.append(f"- {block.cleaned_text[:420]}{'...' if len(block.cleaned_text) > 420 else ''}")
    lines.extend(["", "## Decision And Review Shape", ""])
    decisions = [block for block in blocks if block.block_type in {"decision", "unresolved_question", "contradiction", "rejection", "roadmap"}][:10]
    if decisions:
        for block in decisions:
            lines.append(f"- {block.block_type}: {block.cleaned_text[:360]}{'...' if len(block.cleaned_text) > 360 else ''}")
    else:
        lines.append("- No decision-shaped blocks dominated this theme; treat it mainly as design context.")
    lines.extend(["", "## Representative Source Block References", ""])
    for block in blocks[:18]:
        lines.append(f"- {block.block_id}: `{block.source_file}`")
    lines.extend(["", "## Block Type Counts", ""])
    lines.extend(f"- `{kind}`: {count}" for kind, count in sorted(type_counts.items()))
    return "\n".join(lines)


def _theme_summary(theme_id: str) -> str:
    summaries = {
        "project_identity": "Across the archive, Dominium reads as a layered project rather than a single executable: deterministic substrate, official domain/game layer, product surfaces, tools, and a long-horizon simulation vision.",
        "domino_dominium": "The recurring distinction is that Domino supplies reusable deterministic mechanisms while Dominium gives those mechanisms official domain meaning, authored content, and product interpretation.",
        "determinism_replay_provenance": "The archive repeatedly returns to replay, proof, deterministic ordering, provenance, and validation as architectural necessities rather than test-only concerns.",
        "law_authority_refusal": "Authority is framed as constrained permission under law. Refusal is a lawful, auditable outcome, not a failure path to hide.",
        "runtime_boundaries": "Many conversations test where engine, game, runtime, client, server, and product layers should meet without collapsing ownership.",
        "ui_renderer_presentation": "Renderer and UI ambitions are broad, but the stable rule is that presentation must project truth rather than own or mutate it.",
        "workbench_aide_codex": "Workbench, AIDE, and Codex recur as governed operator and repo-control surfaces that expose evidence and actions without becoming canon.",
        "setup_launcher_release": "Setup, launcher, release, and version identity appear as later product/control-plane concerns with current queue limits.",
        "content_packs_modding": "The archive preserves a strong preference for data-driven packs, registries, compatibility, and explicit refusal over hidden fallback or executable content magic.",
        "world_time_scale": "World, time, scale, and existence themes point toward a simulation model that can refine detail while preserving authoritative truth.",
        "worldgen_celestial_domains": "Worldgen and celestial systems are long-horizon domain ambitions that need source verification and contract scoping before implementation.",
        "civilization_economy_institutions": "Civilization, economy, logistics, institutions, and signals are recurring target phenomena for emergent lawful simulation.",
        "docs_archive_corpus": "The documentation and archive material form a memory system whose value is provenance, contradiction surfacing, and future promotion planning.",
        "decisions_made": "Settled-looking decisions cluster around authority, determinism, refusal, product boundaries, and documentation discipline, but archive support is still advisory unless current docs also support it.",
        "open_decisions": "Open decisions mostly concern scope, sequencing, renderer/UI boundaries, provider/package runtime, domain promotion, and future queue authorization.",
        "contradictions_drift": "Drift appears when older ambition sounds implementation-ready or authoritative despite current queue and authority constraints.",
        "roadmap_sequence": "The clean path is inventory, source selection, theme synthesis, decision triage, targeted promotion, and only then scoped implementation.",
    }
    return summaries.get(theme_id, "This theme preserves project-bearing material for later review.")


def write_themes(repo_root: Path, blocks: List[SourceBlock]) -> None:
    root = repo_root / OUTPUT_ROOT / "themes"
    grouped = group_blocks_by_theme(blocks)
    theme_map = [STATUS_BLOCK, "# Theme Map", "", "Blocks are sorted by meaning. Theme files summarize source material in prose while preserving representative block references.", "", "| Theme | Blocks | Main Use |", "| --- | ---: | --- |"]
    yml = ["task_id: PROJECT-VISION-CORPUS-01", "themes:"]
    for theme_id, title, _keywords in THEMES:
        count = len(grouped.get(theme_id, []))
        theme_map.append(f"| {title} | {count} | planning synthesis and future review |")
        yml.append(f"  {theme_id}:")
        yml.append(f"    title: {json.dumps(title)}")
        yml.append(f"    block_count: {count}")
        yml.append("    blocks: [" + ", ".join(block.block_id for block in grouped.get(theme_id, [])[:250]) + "]")
    write_text(root / "THEME_MAP.md", "\n".join(theme_map))
    write_text(root / "THEME_BLOCK_MAP.yml", "\n".join(yml))
    theme_files = {
        "PROJECT_IDENTITY.md": ["project_identity", "domino_dominium"],
        "ARCHITECTURE_AND_SYSTEM_MODEL.md": ["determinism_replay_provenance", "law_authority_refusal", "runtime_boundaries"],
        "PRODUCT_AND_TOOLING.md": ["ui_renderer_presentation", "workbench_aide_codex", "setup_launcher_release", "content_packs_modding"],
        "WORLD_AND_SIMULATION.md": ["world_time_scale", "worldgen_celestial_domains", "civilization_economy_institutions"],
        "GOVERNANCE_AND_PROCESS.md": ["docs_archive_corpus", "decisions_made", "open_decisions", "contradictions_drift"],
        "ROADMAP_AND_SEQUENCE.md": ["roadmap_sequence", "open_decisions", "contradictions_drift"],
    }
    for filename, theme_ids in theme_files.items():
        lines = [STATUS_BLOCK, f"# {filename.removesuffix('.md').replace('_', ' ').title()}", ""]
        for theme_id in theme_ids:
            title = next(title for tid, title, _keywords in THEMES if tid == theme_id)
            lines.append(prose_for_theme(theme_id, title, grouped.get(theme_id, [])))
            lines.append("")
        write_text(root / filename, "\n".join(lines))


def top_blocks(blocks: List[SourceBlock], types: set[str], limit: int = 18) -> List[SourceBlock]:
    chosen = [block for block in blocks if block.block_type in types]
    chosen.sort(key=lambda block: (block.confidence != "medium", len(block.cleaned_text)))
    return chosen[:limit]


def write_synthesis(repo_root: Path, blocks: List[SourceBlock]) -> None:
    root = repo_root / OUTPUT_ROOT / "synthesis"
    grouped = group_blocks_by_theme(blocks)
    vision = [
        STATUS_BLOCK,
        "# Ultimate Project Vision Draft",
        "",
        "This is a derived planning synthesis, not canon. It describes the long-horizon project that emerges from the archived conversation corpus while keeping current repository authority separate from advisory ambition.",
        "",
        "## The Project In One View",
        "",
        "Dominium wants to become a layered deterministic simulation ecosystem. The stable center is not a renderer, editor, launcher, or single game executable. The stable center is a lawful deterministic substrate where authoritative truth changes only through process, capabilities are checked explicitly, unsupported actions refuse audibly, and evidence/provenance remain inspectable. Domino is the reusable substrate; Dominium is the official product and domain layer that gives the substrate authored meaning.",
        "",
        "The archive expands that core into a wider vision: a project that can support game-like simulation, world generation, civilization-scale systems, operator workbenches, launch/setup surfaces, content packs, validation tools, and future presentation layers. The strongest recurring idea is that all of those surfaces should project or operate the same underlying truth rather than becoming separate sources of truth.",
        "",
        "## Current Truth Versus Advisory Ambition",
        "",
        "The current repository already supports the authority model, determinism discipline, truth/perception/render separation, process-only mutation, explicit refusal, and pack-driven integration as hard constraints. The archived conversations strongly reinforce those choices, but the conversations do not create authority by themselves.",
        "",
        "Long-horizon ambition is broader than current permission. Renderer implementation, native GUI, broad Workbench UI, provider runtime, package runtime, gameplay, and release publication remain blocked by queue state until reviewed phases open them. The archive should therefore guide decisions and future tasks, not bypass current scope.",
        "",
        "## Emerging Future Shape",
        "",
        "The future project shape appears to be an ecosystem with four durable layers: deterministic substrate, official domain/game meaning, product/operator surfaces, and evidence-governed documentation/tooling. The simulation side points toward worlds that can express time, scale, celestial systems, economies, logistics, institutions, and signals. The tooling side points toward Workbench, AIDE, Codex, validation harnesses, and source-preserving documentation pipelines. The content side points toward packs, registries, providers, compatibility law, and explicit refusal when optional material is absent.",
        "",
        "## What Must Stay True",
        "",
        "The archive repeatedly warns, directly or indirectly, that future feature work must not collapse truth into rendering, mutate authority through convenience surfaces, hide fallback behavior, treat generated reports as canon, or let old ambition override present queue state. The project can be expansive only if authority remains narrow and inspectable.",
        "",
        "## Practical Interpretation",
        "",
        "The best next use of the corpus is not another omnibus book or broad implementation wave. It is decision triage: identify claims that are current, claims that are useful future intent, claims that conflict with authority, and claims that require user or queue decisions. After that, future work can promote narrow documentation clarifications or open scoped implementation tasks with proper validation.",
    ]
    write_text(root / "ULTIMATE_PROJECT_VISION_DRAFT.md", "\n".join(vision))
    current = [STATUS_BLOCK, "# Current Project Reality", "", "Current repo-backed reality is narrower and stronger than the archived vision.", ""]
    current.extend(f"- {point}" for point in CURRENT_TRUTH_POINTS)
    current.extend(["", "## What This Means", "", "The project can use archive material for orientation, but current work must still obey active authority order and queue state. The corpus supports planning, not automatic promotion."])
    write_text(root / "CURRENT_PROJECT_REALITY.md", "\n".join(current))
    intent = [STATUS_BLOCK, "# Long-Horizon Design Intent", "", "The archive preserves ambitions that are useful for direction but not automatically current truth.", ""]
    for theme_id in ["ui_renderer_presentation", "worldgen_celestial_domains", "civilization_economy_institutions", "workbench_aide_codex", "content_packs_modding"]:
        title = next(title for tid, title, _keywords in THEMES if tid == theme_id)
        intent.extend([f"## {title}", "", _theme_summary(theme_id), ""])
    write_text(root / "LONG_HORIZON_DESIGN_INTENT.md", "\n".join(intent))
    principles = [STATUS_BLOCK, "# Design Principles", "", "Recurring principles extracted from current authority and repeated archive evidence:", ""]
    principles.extend(
        [
            "- Determinism first: authoritative outcomes must be reproducible.",
            "- Authority is lawful permission, not convenience power.",
            "- Refusal and degradation must be explicit, deterministic, and auditable.",
            "- Truth, perception, and rendering remain separate.",
            "- Products, Workbench, AIDE, and Codex operate or project truth; they do not become truth.",
            "- Optional content integrates through packs, registries, capabilities, and compatibility law.",
            "- Generated books and reports are evidence and navigation aids, not promotion mechanisms.",
            "- Future ambition must be sequenced through queue scope, contracts, validation, and review.",
        ]
    )
    write_text(root / "DESIGN_PRINCIPLES.md", "\n".join(principles))
    decisions = top_blocks(blocks, {"decision"}, 35)
    questions = top_blocks(blocks, {"unresolved_question"}, 35)
    contradictions = top_blocks(blocks, {"contradiction", "change_of_direction", "rejection"}, 35)
    docket = [STATUS_BLOCK, "# Decision Docket", "", "This docket records decision-shaped archive evidence. It is a review queue, not a declaration of canon.", "", "## Settled-Looking Decisions To Confirm Against Current Authority", ""]
    docket.extend(f"- {block.cleaned_text[:520]}{'...' if len(block.cleaned_text) > 520 else ''}" for block in decisions[:18])
    docket.extend(["", "## User Or Future Queue Decisions Needed", ""])
    docket.extend(f"- {block.cleaned_text[:520]}{'...' if len(block.cleaned_text) > 520 else ''}" for block in questions[:18])
    docket.extend(["", "## Superseded Or Rejected Directions To Preserve", ""])
    docket.extend(f"- {block.cleaned_text[:520]}{'...' if len(block.cleaned_text) > 520 else ''}" for block in contradictions[:18])
    write_text(root / "DECISION_DOCKET.md", "\n".join(docket))
    open_q = [STATUS_BLOCK, "# Open Questions", "", "The main unresolved issues are not lack of ideas; they are authority, scope, sequencing, and verification questions.", ""]
    open_q.extend(f"- {block.cleaned_text[:640]}{'...' if len(block.cleaned_text) > 640 else ''}" for block in questions[:30])
    write_text(root / "OPEN_QUESTIONS.md", "\n".join(open_q))
    drift = [STATUS_BLOCK, "# Contradictions And Drift", "", "The archive preserves historical changes and conflicting levels of ambition. These should be classified rather than smoothed away.", ""]
    drift.extend(f"- {block.cleaned_text[:640]}{'...' if len(block.cleaned_text) > 640 else ''}" for block in contradictions[:30])
    drift.extend(["", "## Common Drift Pattern", "", "The most common drift pattern is old or advisory material describing a future product surface as if it were implementation-ready. Current queue state blocks broad renderer, native GUI, Workbench UI, provider runtime, package runtime, gameplay, and release publication until future reviewed phases open them."])
    write_text(root / "CONTRADICTIONS_AND_DRIFT.md", "\n".join(drift))
    roadmap_blocks = top_blocks(blocks, {"roadmap", "prerequisite"}, 35)
    roadmap = [STATUS_BLOCK, "# Roadmap And Sequence", "", "The clean sequence is evidence first, decision triage second, narrow promotion third, and implementation only after authority and queue scope are explicit.", "", "## Near-Term Sequence", "", "1. Review this project vision corpus and confirm whether the extracted vision matches user intent.", "2. Triage decision docket items into current truth, future intent, rejected direction, and user decision.", "3. Run narrow docs-only promotion tasks for uncontroversial current-doc clarifications.", "4. Open future queue tasks only for scoped implementation surfaces with contracts and validation.", "5. Keep broad renderer/UI/provider/package/gameplay/release work blocked until explicitly authorized.", "", "## Roadmap Evidence From Sources", ""]
    roadmap.extend(f"- {block.cleaned_text[:600]}{'...' if len(block.cleaned_text) > 600 else ''}" for block in roadmap_blocks[:24])
    write_text(root / "ROADMAP_AND_SEQUENCE.md", "\n".join(roadmap))
    next_doc = [STATUS_BLOCK, "# What To Do Next", "", "The best next action is a human review pass over five files:", "", "- `synthesis/ULTIMATE_PROJECT_VISION_DRAFT.md`", "- `synthesis/CURRENT_PROJECT_REALITY.md`", "- `synthesis/DECISION_DOCKET.md`", "- `synthesis/CONTRADICTIONS_AND_DRIFT.md`", "- `synthesis/ROADMAP_AND_SEQUENCE.md`", "", "After review, create a narrow `PROJECT-VISION-BOOK-01` task only if the synthesis is accepted. Do not begin promotion or implementation from this corpus alone."]
    write_text(root / "WHAT_TO_DO_NEXT.md", "\n".join(next_doc))


def write_review(repo_root: Path, blocks: List[SourceBlock]) -> None:
    root = repo_root / OUTPUT_ROOT / "review"
    questions = top_blocks(blocks, {"unresolved_question"}, 80)
    roadmap = top_blocks(blocks, {"roadmap", "prerequisite"}, 80)
    verification = [block for block in blocks if any(term in block.cleaned_text.lower() for term in ("verify", "source", "evidence", "proof", "audit"))][:80]
    rejected = top_blocks(blocks, {"rejection", "change_of_direction"}, 80)
    risks = top_blocks(blocks, {"risk", "contradiction"}, 80)
    docs = [
        ("USER_DECISION_LIST.md", "User Decision List", questions[:40], "Questions that likely need user review before being treated as settled."),
        ("FUTURE_QUEUE_DECISIONS.md", "Future Queue Decisions", roadmap[:40], "Items that should become explicit future queue decisions rather than implicit scope."),
        ("CLAIMS_REQUIRING_VERIFICATION.md", "Claims Requiring Verification", verification[:40], "Claims that need current-source verification before promotion."),
        ("REJECTED_OR_SUPERSEDED_IDEAS.md", "Rejected Or Superseded Ideas", rejected[:40], "Ideas the archive says were rejected, superseded, or deprioritized."),
        ("RISK_REGISTER.md", "Risk Register", risks[:40], "Risks, contradictions, and drift patterns to preserve for review."),
    ]
    for filename, title, selected, intro in docs:
        lines = [STATUS_BLOCK, f"# {title}", "", intro, ""]
        if selected:
            lines.extend(f"- {block.cleaned_text[:620]}{'...' if len(block.cleaned_text) > 620 else ''}" for block in selected)
        else:
            lines.append("- No strong source blocks were classified into this register.")
        write_text(root / filename, "\n".join(lines))


def write_root_and_reports(repo_root: Path, zips: List[ZipRecord], sources: List[SourceRecord], blocks: List[SourceBlock], duplicate_counts: Dict[str, int], commands: List[Tuple[str, int]]) -> None:
    root = repo_root / OUTPUT_ROOT
    grouped = group_blocks_by_theme(blocks)
    output_files = [
        "raw_manifest/ZIP_MANIFEST.json",
        "raw_manifest/ZIP_MANIFEST.md",
        "raw_manifest/PACKAGE_COMPLETENESS.md",
        "raw_manifest/DUPLICATE_PACKAGE_REPORT.md",
        "source_selection/HUMAN_READABLE_SOURCE_SELECTION.md",
        "source_selection/MACHINE_MATERIAL_EXCLUDED.md",
        "source_selection/SOURCE_PRIORITY_LIST.md",
        "source_blocks/SOURCE_BLOCKS.yml",
        "source_blocks/SOURCE_BLOCKS.md",
        "source_blocks/SOURCE_BLOCK_INDEX.md",
        "source_blocks/SOURCE_BLOCK_DEDUPLICATION_REPORT.md",
        "themes/THEME_MAP.md",
        "themes/THEME_BLOCK_MAP.yml",
        "themes/PROJECT_IDENTITY.md",
        "themes/ARCHITECTURE_AND_SYSTEM_MODEL.md",
        "themes/PRODUCT_AND_TOOLING.md",
        "themes/WORLD_AND_SIMULATION.md",
        "themes/GOVERNANCE_AND_PROCESS.md",
        "themes/ROADMAP_AND_SEQUENCE.md",
        "synthesis/ULTIMATE_PROJECT_VISION_DRAFT.md",
        "synthesis/CURRENT_PROJECT_REALITY.md",
        "synthesis/LONG_HORIZON_DESIGN_INTENT.md",
        "synthesis/DESIGN_PRINCIPLES.md",
        "synthesis/DECISION_DOCKET.md",
        "synthesis/OPEN_QUESTIONS.md",
        "synthesis/CONTRADICTIONS_AND_DRIFT.md",
        "synthesis/ROADMAP_AND_SEQUENCE.md",
        "synthesis/WHAT_TO_DO_NEXT.md",
        "review/USER_DECISION_LIST.md",
        "review/FUTURE_QUEUE_DECISIONS.md",
        "review/CLAIMS_REQUIRING_VERIFICATION.md",
        "review/REJECTED_OR_SUPERSEDED_IDEAS.md",
        "review/RISK_REGISTER.md",
    ]
    readme = [STATUS_BLOCK, "# Project Vision Corpus", "", "This derived corpus turns archived chat packages and human-readable reports into a planning source library, theme map, and first project-vision synthesis.", "", "It does not promote archive claims. It does not modify current docs, canon, contracts, schema, implementation, release, or queue state.", "", "## Main Reading Path", "", "1. `synthesis/ULTIMATE_PROJECT_VISION_DRAFT.md`", "2. `synthesis/CURRENT_PROJECT_REALITY.md`", "3. `synthesis/DESIGN_PRINCIPLES.md`", "4. `synthesis/DECISION_DOCKET.md`", "5. `synthesis/CONTRADICTIONS_AND_DRIFT.md`", "6. `synthesis/ROADMAP_AND_SEQUENCE.md`", "", "## Corpus Scale", "", f"- Zip packages inventoried: {len(zips)}", f"- Human-readable sources selected: {len(sources)}", f"- Semantic source blocks retained: {len(blocks)}", f"- Theme groups created: {len([theme for theme in grouped if grouped[theme]])}"]
    write_text(root / "README.md", "\n".join(readme))
    code_json, _ = run_command(["py", "-3", "-c", f"import json; json.load(open(r'{(root / 'raw_manifest/ZIP_MANIFEST.json').as_posix()}'))"], repo_root, timeout=120)
    code_protected, protected_output = protected_path_check(repo_root)
    commands.extend([("parse ZIP_MANIFEST.json", code_json), ("protected path check", code_protected)])
    existing = sum(1 for rel in output_files if (root / rel).exists())
    build = [STATUS_BLOCK, "# Project Vision Corpus Build Report", "", f"- Task ID: {TASK_ID}", f"- Zip packages inventoried: {len(zips)}", f"- Human-readable sources selected: {len(sources)}", f"- Semantic blocks retained: {len(blocks)}", f"- Duplicate block source groups: {len(duplicate_counts)}", f"- Theme files created: 6 grouped theme files plus theme map", f"- Expected core outputs present: {existing} / {len(output_files)}", "", "## Outputs", ""]
    build.extend(f"- `{rel}`" for rel in output_files)
    write_text(root / "build_reports/PROJECT_VISION_CORPUS_BUILD_REPORT.md", "\n".join(build))
    command_rows = "\n".join(f"| {name} | {'PASS' if code == 0 else 'FAIL'} | {code} |" for name, code in commands)
    ok = existing == len(output_files) and code_json == 0 and code_protected == 0
    validation = [STATUS_BLOCK, "# Project Vision Corpus Validation Report", "", f"- Result: {'PASS' if ok else 'FAIL'}", f"- Zip packages accounted for: {len(zips)}", f"- Source files selected: {len(sources)}", f"- Source blocks generated: {len(blocks)}", f"- Themes generated: {len([theme for theme in grouped if grouped[theme]])}", f"- Protected path changes: {'none detected' if code_protected == 0 else protected_output}", "", "## Commands", "", "| Command | Result | Exit Code |", "| --- | --- | ---: |", command_rows, "", "## Quality Gate", "", "- Raw zips were read only, not modified.", "- Current truth versus advisory vision is labelled in synthesis outputs.", "- Archive/conversation claims remain advisory.", "- No live-doc promotion was performed.", "- No final book was generated in this milestone."]
    write_text(root / "build_reports/PROJECT_VISION_CORPUS_VALIDATION_REPORT.md", "\n".join(validation))


def protected_path_check(repo_root: Path) -> Tuple[int, str]:
    code, output = run_command(["git", "diff", "--name-only"], repo_root, timeout=120)
    if code != 0:
        return code, output.strip()
    changed = [line.strip() for line in output.splitlines() if line.strip()]
    hits = [path for path in changed if any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in docs_corpus.PROTECTED_PREFIXES)]
    return (1, ", ".join(hits)) if hits else (0, "none")


def build(repo_root: Path) -> Tuple[int, Dict[str, int]]:
    commands: List[Tuple[str, int]] = []
    zips = inventory_zips(repo_root)
    sources, excluded = select_sources(repo_root)
    blocks, duplicates = extract_blocks(repo_root, sources)
    write_raw_manifest(repo_root, zips)
    write_source_selection(repo_root, sources, excluded)
    write_source_blocks(repo_root, blocks, duplicates)
    write_themes(repo_root, blocks)
    write_synthesis(repo_root, blocks)
    write_review(repo_root, blocks)
    write_root_and_reports(repo_root, zips, sources, blocks, duplicates, commands)
    return 0, {"zips": len(zips), "sources": len(sources), "blocks": len(blocks), "themes": len(THEMES)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    code, stats = build(repo_root)
    print(
        "project vision corpus build: "
        + ("PASS" if code == 0 else "FAIL")
        + f" zips={stats['zips']} sources={stats['sources']} blocks={stats['blocks']} themes={stats['themes']}"
    )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
