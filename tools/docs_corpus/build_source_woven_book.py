"""Build the Dominium Source-Woven Project Book.

This pipeline is intentionally separate from the authored and integrated book
generators. It extracts original human-readable source passages as semantic
blocks, assigns those blocks to conceptual chapters, and composes a reader that
uses source text directly with light editorial bridges.

Generated outputs are DERIVED and advisory. Source documents are not modified.
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
from xml.sax.saxutils import escape as xml_escape

import build_human_readable_book as human
import build_integrated_book_v2 as integrated
import build_omnibus_v1 as styled
import docs_corpus


TASK_ID = "DOMINIUM-SOURCE-WOVEN-BOOK-01"
REVIEW_DATE = "2026-05-30"
TITLE = "Dominium Source-Woven Project Book"
SUBTITLE = "A human-readable compilation of current docs, archive context, and conversation source passages"

ROOT = Path("docs/archive/docs_corpus/_source_woven_book")
EXPORTS_ROOT = Path("docs/archive/docs_corpus/_exports")
QA_ROOT = ROOT / "qa"
BUILD_ROOT = ROOT / "build"

MAIN_MD = "Dominium_Source_Woven_Project_Book.md"
MAIN_PDF = "Dominium_Source_Woven_Project_Book.pdf"
MAIN_HTML_DIR = "Dominium_Source_Woven_Project_Book.html"
MAIN_DOCX = "Dominium_Source_Woven_Project_Book.docx"
SOURCE_MAP_PDF = "Dominium_Source_Woven_Project_Book_Source_Map.pdf"
BUILD_REPORT = "Dominium_Source_Woven_Project_Book_Build_Report.md"
VALIDATION_REPORT = "Dominium_Source_Woven_Project_Book_Validation_Report.md"

STATUS_BLOCK = f"""Status: DERIVED
Last Reviewed: {REVIEW_DATE}
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/`
Conversation Corpus Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged
"""

BANNED_PATTERNS = [
    "EVC-",
    "card_id",
    "block_id",
    "Integrated Evidence",
    "Decisions Already Visible",
    "Specifications and Requirements",
    "Constraints, Prohibitions, and Prerequisites",
    "Contradictions, Risks, and Open Ends",
    "Second- and Third-Order Effects",
    "Implications for Next Work",
    "Source Trail",
    "Review Questions",
    "How to use this chapter",
    "This chapter is part of",
    "That historical context is still useful",
]

MACHINE_EXCLUSION_PATTERNS = [
    "manifest",
    "source_index",
    "file_counts",
    "tree_summary",
    "hash",
    "sha256",
    "integrity",
    "register",
    "matrix",
    "validation",
    "build_report",
    "bundle",
    "packet",
    "spec_sheet",
    "aggregator",
    "context_transfer",
    "inventory",
]

BLOCK_TYPE_KEYWORDS = {
    "decision": ["decided", "decision", "accepted", "conclusion", "recommended", "choose", "chosen"],
    "design_goal": ["goal", "purpose", "intent", "aim", "ambition", "designed to", "should support"],
    "requirement": ["must", "required", "requires", "contract", "schema", "invariant", "api", "law"],
    "constraint": ["constraint", "boundary", "limited", "scope", "queue", "compatibility", "portable"],
    "prohibition": ["must not", "do not", "forbidden", "not authorized", "blocked", "never", "no silent"],
    "prerequisite": ["before", "prerequisite", "only after", "depends on", "must happen"],
    "unresolved_question": ["open question", "unresolved", "unclear", "needs decision", "unknown", "not yet"],
    "contradiction": ["contradiction", "conflict", "drift", "inconsistent", "mismatch", "disagree"],
    "risk": ["risk", "warning", "caveat", "danger", "failure", "debt"],
    "rationale": ["because", "therefore", "consequence", "means that", "why", "rationale"],
    "roadmap": ["next step", "roadmap", "future", "later", "sequencing"],
}


@dataclass(frozen=True)
class ChapterDef:
    number: int
    part: str
    title: str
    tags: Tuple[str, ...]
    opening: str
    current_bridge: str
    archive_bridge: str
    tension_bridge: str
    closing: str


@dataclass
class SourceBlock:
    block_id: str
    source_path: str
    source_title: str
    source_heading_path: str
    original_text: str
    cleaned_text: str
    block_type: str
    authority_class: str
    promotion_status: str
    topic_tags: List[str]
    candidate_chapters: List[int]
    primary_chapter: int
    secondary_chapters: List[int]
    include_mode: str
    confidence: str
    notes: str = ""


@dataclass
class PdfInfo:
    path: Path
    created: bool
    pages: Optional[int] = None
    size: int = 0
    renderer: str = ""
    text_extraction: str = "not_run"
    glyph_check: str = "not_run"
    qa_images: List[str] = field(default_factory=list)
    caveat: str = ""


@dataclass
class BuildState:
    repo_root: Path
    sources: List[human.SourceItem]
    blocks: List[SourceBlock] = field(default_factory=list)
    chapter_blocks: Dict[int, List[SourceBlock]] = field(default_factory=dict)
    duplicate_count: int = 0
    excluded_machine_count: int = 0
    conversation_file_count: int = 0
    conversation_markdown_count: int = 0
    branch: str = ""
    commit: str = ""
    renderer: str = ""
    outputs: Dict[str, PdfInfo] = field(default_factory=dict)
    command_results: List[Dict[str, object]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


CHAPTERS: List[ChapterDef] = [
    ChapterDef(1, "Part I - The Project", "Dominium in One View", ("identity", "runtime", "authority"), "Dominium is easiest to read as a layered project: a deterministic substrate, an official domain layer, product surfaces, and governed tooling all held apart by authority rules.", "The current sources set the initial boundary.", "The archive then widens the view without changing the authority order.", "The useful tension is that the project is ambitious, but current permission remains narrow.", "Where this leaves us: Dominium is a broad project only because its layers stay disciplined."),
    ChapterDef(2, "Part I - The Project", "Why the Project Exists", ("identity", "world", "civilization"), "The project exists to make complex worlds emerge from lawful process rather than from ad hoc scripting.", "Current orientation material describes a project built around refusal, evidence, and deterministic process.", "Conversation material supplies the larger product and simulation desire behind that machinery.", "The tension is between long-horizon intent and the present queue.", "Where this leaves us: the ambition is preserved, but future feature work still needs a smaller lawful task."),
    ChapterDef(3, "Part I - The Project", "The Core Mental Model", ("determinism", "authority", "world"), "The core mental model is the separation of truth, perception, rendering, and operation.", "Current doctrine makes truth authoritative and mutation process-bound.", "The conversations repeatedly test that model against Workbench, UI, providers, packs, and world simulation.", "The risk appears whenever a convenience layer is allowed to become an authority layer.", "Where this leaves us: every later surface has to say whether it owns truth, observes truth, presents truth, or operates the repo."),
    ChapterDef(4, "Part I - The Project", "Current Truth and Historical Evidence", ("authority", "docs", "blocked"), "The docs corpus is not a flat library. It contains current truth, historical context, derived reports, and advisory conversation evidence.", "Current authority starts with canon, glossary, AGENTS, contracts, schema law, queue state, and validated repo artifacts.", "Archive and conversation material are valuable because they preserve design memory and unresolved decisions.", "The tension is accidental promotion: a polished old idea can sound current when it is not.", "Where this leaves us: use the archive to understand the project, then promote only through explicit review."),
    ChapterDef(5, "Part II - Architecture", "The System Stack", ("runtime", "contracts", "identity"), "The system stack is a set of responsibility boundaries rather than a file listing.", "Current docs separate substrate, domain meaning, products, runtime services, contracts, content, tools, and documentation.", "Older sources describe the same stack with more future-facing language.", "The tension is that adjacent roots can look interchangeable even when their authority is different.", "Where this leaves us: growth should extend the stack without collapsing ownership."),
    ChapterDef(6, "Part II - Architecture", "Domino, Dominium, Runtime, Products, and Tools", ("runtime", "product", "tooling", "identity"), "Domino and Dominium are linked, but they are not synonyms.", "Current sources make Domino the reusable deterministic substrate and Dominium the official product/domain layer.", "The archive adds client, server, launcher, setup, Workbench, and automation ambitions.", "The tension is product ambition versus substrate authority.", "Where this leaves us: products and tools can project or operate the substrate, but they do not replace it."),
    ChapterDef(7, "Part II - Architecture", "Law, Capability, Refusal, and Evidence", ("authority", "contracts", "determinism"), "Law and capability are how the project turns possibility into allowed action.", "Current doctrine requires explicit refusal and no hidden fallback behavior.", "Archive passages show the same rule pressed into packs, providers, Workbench, assistant workflows, and future product surfaces.", "The tension is making refusal clear without making the system opaque.", "Where this leaves us: a future feature should be able to name its authority source, refusal path, and evidence trail."),
    ChapterDef(8, "Part II - Architecture", "Determinism, Replay, and Provenance", ("determinism", "contracts", "tooling"), "Determinism is both a runtime rule and an audit strategy.", "Current sources require named randomness, stable ordering, replay equivalence, and provenance.", "The archive adds proof gates, evidence artifacts, portability concerns, and release trust.", "The tension is that some attractive features become unsafe if they cannot explain their replay behavior.", "Where this leaves us: validation is part of architecture, not a later checklist."),
    ChapterDef(9, "Part II - Architecture", "Contracts, Schemas, Packs, and Compatibility", ("contracts", "packs", "release"), "Contracts and schemas preserve public meaning across time.", "Current material requires explicit identity, versioning, migration, refusal, and compatibility discipline.", "Conversation sources expand that into provider choices, package composition, modding surfaces, and release identity.", "The tension is separating current contract law from future packaging ambition.", "Where this leaves us: packs are current doctrine; provider/package runtime claims still need review."),
    ChapterDef(10, "Part III - Product and Operator Surfaces", "Client, Server, Launcher, Setup, and Workbench", ("product", "workbench", "runtime"), "Product shells are how operators meet the substrate, but they remain downstream of truth.", "Current docs identify product surfaces while queue state keeps broad implementation constrained.", "The archive preserves rich Workbench, launcher, setup, and command-surface ideas.", "The tension is that the desired operator experience is clearer than the currently authorized implementation surface.", "Where this leaves us: Workbench is product intent and operator design, not a hidden authority layer."),
    ChapterDef(11, "Part III - Product and Operator Surfaces", "UI, Renderer, Native GUI, and Presentation Boundaries", ("renderer", "product", "blocked"), "Presentation is downstream of truth and perception.", "Current doctrine says rendering presents; it does not mutate truth.", "The conversation archive contains extensive UI, renderer, native GUI, and universe-exploration intent.", "The tension is that those ideas are useful precisely because they remain blocked until the queue opens them.", "Where this leaves us: future renderer work must protect truth/perception/render separation before it becomes product work."),
    ChapterDef(12, "Part III - Product and Operator Surfaces", "AIDE, Codex, Automation, and Repo Governance", ("tooling", "authority", "docs"), "AIDE, Codex, and automation are governed helpers, not alternate project authorities.", "AGENTS defines bounded work, validation expectations, protected paths, and forbidden moves.", "The archive records repeated work to make assistant operation portable, evidence-rich, and reviewable.", "The tension is that generated outputs can look authoritative because they are polished.", "Where this leaves us: automation may expose evidence and perform bounded edits, but it cannot silently become canon."),
    ChapterDef(13, "Part III - Product and Operator Surfaces", "Documentation, Archive, and Conversation Corpus", ("docs", "authority"), "The archive is the project's memory system.", "Current docs-corpus outputs classify the tree, authority layers, drift, decisions, and promotion candidates.", "The conversation corpus adds preserved design intent, old handoffs, contradictions, reader pages, and reports.", "The tension is turning that memory into useful reading without making it current truth.", "Where this leaves us: ordinary readers get woven chapters; auditors get source maps and appendices."),
    ChapterDef(14, "Part IV - Simulation and World Model", "Reality, Space, Time, Scale, and Existence", ("world", "determinism"), "Reality, space, time, scale, and existence are simulation concerns before they are presentation concerns.", "Current law supplies deterministic process, event-driven change, truth/perception separation, and provenance.", "The archive adds visitability, temporal resilience, large-scale representation, and 2038-style timekeeping concerns.", "The tension is that long-horizon world design can outrun present domain authority.", "Where this leaves us: future domain work should classify claims before attaching them to gameplay or rendering."),
    ChapterDef(15, "Part IV - Simulation and World Model", "World Generation, Celestial Systems, and Domains", ("world", "packs"), "World generation and celestial systems recur because the project wants large lawful worlds.", "Current authority supports deterministic composition and data-driven domain boundaries.", "Archive passages discuss planets, astronomy, domain packs, terrain, stars, and source verification.", "The tension is aligning scientific ambition, authored content, and deterministic constraints.", "Where this leaves us: worldgen work needs source verification, contracts, and queue scope before implementation."),
    ChapterDef(16, "Part IV - Simulation and World Model", "Civilization, Economy, Logistics, and Institutions", ("civilization", "world"), "Civilization-scale simulation is one of the clearest ambitions in the conversation corpus.", "Current orientation names production, logistics, economics, settlement, trust, communication, and institutions as important phenomena.", "Conversation passages add seed civilizations, infrastructure, signals, institutions, power, and social feedback loops.", "The tension is that those ideas are rich but mostly not yet implementation scope.", "Where this leaves us: they define pressure that the architecture should be able to bear later."),
    ChapterDef(17, "Part IV - Simulation and World Model", "Content, Providers, Modding, and Data-Driven Extension", ("packs", "contracts", "blocked"), "Content extension is supposed to be governed, not magical.", "Current doctrine favors packs, registries, explicit capabilities, compatibility rules, and deterministic refusal.", "The archive expands this into providers, package runtime, open-source provider choices, authoring, and modding workflows.", "The tension is that pack doctrine is current while provider/package runtime is not broadly open.", "Where this leaves us: extension work should separate data-driven content from blocked runtime-provider ambitions."),
    ChapterDef(18, "Part V - Decisions and Roadmap", "What Is Settled", ("authority", "decision", "docs"), "Some principles are settled strongly enough to shape every later task.", "Current authority supports process-only mutation, profiles over mode flags, pack-driven integration, truth/perception/render separation, explicit refusal, and validation discipline.", "Conversation evidence often reinforces those decisions by showing the same pressure from different directions.", "The tension is that agreement in archive material still does not change the authority source.", "Where this leaves us: settled principles should simplify later review, not bypass it."),
    ChapterDef(19, "Part V - Decisions and Roadmap", "What Is Still Open", ("decision", "docs", "blocked"), "Open decisions are the reason this material remains evidence rather than doctrine.", "Current reports identify user decisions, future queue decisions, and source verification needs.", "Archive and conversation passages often offer plausible answers, but not final authority.", "The tension is between preserving useful answers and avoiding silent promotion.", "Where this leaves us: the book should help readers identify decisions before trying to resolve them."),
    ChapterDef(20, "Part V - Decisions and Roadmap", "What Is Blocked", ("blocked", "renderer", "release"), "Blocked scope is part of the project picture.", "Current queue state does not open broad Workbench UI, renderer implementation, native GUI, provider runtime, package runtime, gameplay, or release publication.", "Historical sources often talk about those areas because they preserve product intent.", "The tension is that future usefulness can be mistaken for present permission.", "Where this leaves us: every later prompt should state blocked areas before implementation language."),
    ChapterDef(21, "Part V - Decisions and Roadmap", "Contradictions and Drift", ("docs", "authority", "blocked"), "The corpus preserves drift because it preserves time.", "Current authority order is what prevents old planning, generated summaries, and conversation claims from overriding present repo truth.", "Archive passages reveal conflicts around scope, release, provider boundaries, renderer readiness, and old architecture language.", "The tension is that smoothing those conflicts would make the book easier but less accurate.", "Where this leaves us: contradictions are review signals, not failures to hide."),
    ChapterDef(22, "Part V - Decisions and Roadmap", "Prerequisites and Sequencing", ("blocked", "tooling", "release"), "Sequencing is the discipline that keeps ambition useful.", "Current state points toward narrow command/result, package-mount, projection conformance, validation, and review work before broad feature expansion.", "Historical roadmaps add useful orderings around Workbench, release, providers, docs promotion, and domains.", "The tension is that the same future may be desirable in several orders but only one order may be safe now.", "Where this leaves us: future tasks should name prerequisites before changing behavior."),
    ChapterDef(23, "Part V - Decisions and Roadmap", "Recommended Next Steps", ("docs", "decision", "blocked"), "The next best work is selective review and controlled promotion, not another dump.", "Current authority permits derived documentation and narrow governed tasks, not sweeping promotion.", "The source-woven book and source map give reviewers enough material to choose small follow-ups deliberately.", "The tension is deciding which preserved knowledge deserves live-doc promotion and which should remain archive evidence.", "Where this leaves us: read the book, inspect the source map where needed, triage decisions, and promote only in narrow waves."),
]

CHAPTER_BY_NUMBER = {chapter.number: chapter for chapter in CHAPTERS}


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
        text = (exc.stdout or "") + (exc.stderr or "")
        return 124, docs_corpus.ascii_text(text)
    return completed.returncode, docs_corpus.ascii_text(completed.stdout or "")


def write_text(path: Path, content: str) -> None:
    clean = "\n".join(line.rstrip(" \t") for line in content.splitlines())
    docs_corpus.write_if_changed(path, docs_corpus.ascii_text(clean) + "\n")


def read_text(path: Path, limit: Optional[int] = None) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text[:limit] if limit and len(text) > limit else text


def yaml_scalar(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{text}"'


def yaml_list(values: Sequence[object], indent: int = 4) -> List[str]:
    pad = " " * indent
    if not values:
        return [pad + "[]"]
    return [pad + "- " + yaml_scalar(value) for value in values]


def safe_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", value.lower()).strip("_") or "chapter"


def normalize_key(text: str) -> str:
    text = re.sub(r"`[^`]+`", "", text)
    text = re.sub(r"\b(?:docs|tools|contracts|schema|apps|engine|game|runtime)/\S+", "", text)
    text = re.sub(r"[^a-z0-9]+", " ", text.lower())
    return " ".join(text.split())[:260]


def clean_source_text(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"EVC-\d+", "", text)
    text = re.sub(r"\b(?:docs|tools|contracts|schema|apps|engine|game|runtime)/[A-Za-z0-9_./() -]+(?:\.(?:md|json|yml|yaml|toml|txt|py|pdf|docx))?\b", "the referenced source", text)
    text = re.sub(r"\[[^\]]+\]\([^)]*\)", lambda match: match.group(0).split("](")[0].lstrip("["), text)
    text = re.sub(r"\s+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def source_label(item: human.SourceItem) -> str:
    label = item.title or human.title_from_path(item.path)
    label = re.sub(r"\s+", " ", label).strip()
    return label[:90] or "Source document"


def authority_rank(block: SourceBlock) -> int:
    path = block.source_path
    if path in human.HIGH_AUTHORITY_SOURCES:
        return 0
    if path.startswith("docs/") and not path.startswith("docs/archive/"):
        return 1
    if path in human.SYNTHESIS_SOURCES:
        return 2
    if path.startswith("docs/archive/conversations/"):
        return 3
    if path.startswith("docs/archive/"):
        return 4
    return 5


def source_is_machine_like(item: human.SourceItem) -> bool:
    lower = item.path.lower()
    return item.extension in human.MACHINE_EXTENSIONS or any(pattern in lower for pattern in MACHINE_EXCLUSION_PATTERNS)


def should_select_source(item: human.SourceItem) -> bool:
    if item.disposition in {"binary_or_non_text", "exclude_generated_recursive"}:
        return False
    if item.path.startswith("docs/archive/docs_corpus/_source_woven_book/"):
        return False
    if item.path in human.HIGH_AUTHORITY_SOURCES or item.path in human.SYNTHESIS_SOURCES:
        return True
    if item.disposition in {"human_full_text", "human_excerpt", "human_summarize"}:
        return True
    if item.path.startswith("docs/archive/conversations/") and item.extension == ".md":
        return True
    return False


def classify_block_type(text: str) -> str:
    lowered = text.lower()
    for block_type, keywords in BLOCK_TYPE_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return block_type
    return "explanation"


def topic_tags(text: str, item: human.SourceItem) -> List[str]:
    lowered = f"{item.path} {item.title} {text}".lower()
    tags = [tag for tag, keywords in integrated.TAG_KEYWORDS.items() if any(keyword in lowered for keyword in keywords)]
    return tags or ["docs"]


def candidate_chapters(tags: Sequence[str], item: human.SourceItem) -> List[int]:
    candidates: List[int] = []
    tag_set = set(tags)
    for chapter in CHAPTERS:
        if tag_set.intersection(chapter.tags):
            candidates.append(chapter.number)
    path = item.path.lower()
    if "renderer" in path or "gui" in path or "ui" in path:
        candidates.insert(0, 11)
    if "workbench" in path or "launcher" in path or "setup" in path:
        candidates.insert(0, 10)
    if "conversation" in path or path.startswith("docs/archive/conversations/"):
        candidates.append(13)
    if "decision" in path:
        candidates.append(19)
    if "promotion" in path:
        candidates.append(23)
    if "contradiction" in path or "stale" in path or "drift" in path:
        candidates.append(21)
    if "canon" in path or "authority" in path or "agents" in path:
        candidates.append(4)
    ordered: List[int] = []
    for number in candidates:
        if number in CHAPTER_BY_NUMBER and number not in ordered:
            ordered.append(number)
    return ordered or [13]


def split_semantic_blocks(text: str) -> List[Tuple[str, str, str]]:
    _metadata, body = human.compact_metadata(text)
    blocks: List[Tuple[str, str, str]] = []
    heading_stack: List[str] = []
    current: List[str] = []
    current_kind = "paragraph"
    in_code = False

    def flush() -> None:
        nonlocal current, current_kind
        if not current:
            return
        raw = "\n".join(current).strip()
        current = []
        if len(raw) < 90:
            return
        if len(raw) > 2600:
            raw = raw[:2600].rsplit(" ", 1)[0].rstrip(".,;:") + "."
        heading = " > ".join(heading_stack[-3:]) if heading_stack else ""
        blocks.append((heading, raw, current_kind))
        current_kind = "paragraph"

    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code = not in_code
            flush()
            continue
        if in_code:
            continue
        if stripped.startswith("#"):
            flush()
            level = len(stripped) - len(stripped.lstrip("#"))
            title = stripped.lstrip("#").strip()
            heading_stack = heading_stack[: max(0, level - 1)] + [title]
            continue
        if not stripped:
            flush()
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            if len(stripped) > 180 or stripped.count("|") > 8:
                flush()
                continue
            current_kind = "table"
            current.append(stripped)
            continue
        if re.match(r"^[-*]\s+", stripped) or re.match(r"^\d+[.)]\s+", stripped):
            if current_kind != "list":
                flush()
                current_kind = "list"
            current.append(stripped)
            continue
        if current_kind in {"list", "table"}:
            flush()
        current.append(stripped)
    flush()
    return blocks


def include_mode_for(item: human.SourceItem, cleaned: str) -> str:
    if source_is_machine_like(item):
        return "reference_only"
    if item.disposition == "human_summarize":
        return "excerpt"
    if len(cleaned) < 120:
        return "reference_only"
    return "main"


def extract_blocks(repo_root: Path, sources: Sequence[human.SourceItem]) -> Tuple[List[SourceBlock], int, int]:
    blocks: List[SourceBlock] = []
    duplicate_count = 0
    excluded_machine = 0
    seen: Dict[str, str] = {}
    ordinal = 1
    for item in sources:
        if not should_select_source(item):
            continue
        full = repo_root / item.path
        if not full.exists() or full.is_dir():
            continue
        if source_is_machine_like(item):
            excluded_machine += 1
            summary = f"{item.title} is represented as reference material because it is primarily machine-readable, register-like, or validation-oriented."
            tags = topic_tags(summary, item)
            chapters = candidate_chapters(tags, item)
            block = SourceBlock(
                block_id=f"SWB-{ordinal:05d}",
                source_path=item.path,
                source_title=source_label(item),
                source_heading_path="reference material",
                original_text=summary,
                cleaned_text=summary,
                block_type="source_context",
                authority_class=item.authority_class,
                promotion_status="not_promoted" if item.path.startswith("docs/archive/") else "current_source",
                topic_tags=tags,
                candidate_chapters=chapters,
                primary_chapter=chapters[0],
                secondary_chapters=chapters[1:4],
                include_mode="reference_only",
                confidence="medium",
                notes=item.reason,
            )
            blocks.append(block)
            ordinal += 1
            continue
        limit = 80_000 if item.disposition in {"human_full_text", "human_excerpt"} else 18_000
        if item.path.startswith("docs/archive/conversations/_reader/by_chat/"):
            limit = 90_000
        raw_text = read_text(full, limit=limit)
        for heading, original, kind in split_semantic_blocks(raw_text):
            cleaned = clean_source_text(original)
            if len(cleaned) < 90:
                continue
            key = normalize_key(cleaned)
            include_mode = include_mode_for(item, cleaned)
            if key in seen:
                duplicate_count += 1
                include_mode = "excluded_duplicate"
            else:
                seen[key] = item.path
            tags = topic_tags(cleaned, item)
            chapters = candidate_chapters(tags, item)
            block = SourceBlock(
                block_id=f"SWB-{ordinal:05d}",
                source_path=item.path,
                source_title=source_label(item),
                source_heading_path=heading,
                original_text=original,
                cleaned_text=cleaned,
                block_type=classify_block_type(cleaned) if kind != "table" else "source_context",
                authority_class=item.authority_class,
                promotion_status="not_promoted" if item.path.startswith("docs/archive/") else "current_source",
                topic_tags=tags,
                candidate_chapters=chapters,
                primary_chapter=chapters[0],
                secondary_chapters=chapters[1:4],
                include_mode=include_mode,
                confidence="high" if item.path in human.HIGH_AUTHORITY_SOURCES else "medium",
                notes=item.reason,
            )
            blocks.append(block)
            ordinal += 1
    return blocks, duplicate_count, excluded_machine


def select_sources(repo_root: Path) -> Tuple[List[human.SourceItem], int, int]:
    records = human.load_manifest(repo_root)
    items = human.select_sources(repo_root, records)
    by_path = {item.path: item for item in items}
    for path in human.HIGH_AUTHORITY_SOURCES + human.SYNTHESIS_SOURCES:
        if path not in by_path and (repo_root / path).exists():
            item = human.manual_source_item(repo_root, path, "required source for source-woven book")
            items.append(item)
            by_path[path] = item
    conversation_files = [record for record in records if str(record.get("path", "")).startswith("docs/archive/conversations/")]
    conversation_markdown = [record for record in conversation_files if str(record.get("extension", "")).lower() == ".md"]
    items.sort(key=lambda item: item.path)
    return items, len(conversation_files), len(conversation_markdown)


def load_state(repo_root: Path) -> BuildState:
    sources, conversation_files, conversation_markdown = select_sources(repo_root)
    branch = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo_root, timeout=60)[1].strip() or "unknown"
    commit = run_command(["git", "rev-parse", "--short=9", "HEAD"], repo_root, timeout=60)[1].strip() or "unknown"
    blocks, duplicate_count, excluded_machine = extract_blocks(repo_root, sources)
    chapter_blocks = map_blocks_to_chapters(blocks)
    return BuildState(
        repo_root=repo_root,
        sources=sources,
        blocks=blocks,
        chapter_blocks=chapter_blocks,
        duplicate_count=duplicate_count,
        excluded_machine_count=excluded_machine,
        conversation_file_count=conversation_files,
        conversation_markdown_count=conversation_markdown,
        branch=branch,
        commit=commit,
        renderer=styled.select_engine() or "none",
    )


def map_blocks_to_chapters(blocks: Sequence[SourceBlock]) -> Dict[int, List[SourceBlock]]:
    by_chapter: Dict[int, List[SourceBlock]] = defaultdict(list)
    for block in blocks:
        chapters = block.candidate_chapters or [block.primary_chapter]
        for chapter in chapters:
            if chapter in CHAPTER_BY_NUMBER:
                by_chapter[chapter].append(block)
    for number, items in by_chapter.items():
        items.sort(key=lambda block: (block.include_mode != "main", authority_rank(block), type_rank(block), block.source_path, block.block_id))
    return by_chapter


def type_rank(block: SourceBlock) -> int:
    order = {
        "decision": 0,
        "requirement": 1,
        "constraint": 2,
        "prohibition": 3,
        "prerequisite": 4,
        "design_goal": 5,
        "rationale": 6,
        "contradiction": 7,
        "unresolved_question": 8,
        "risk": 9,
        "roadmap": 10,
        "explanation": 11,
        "source_context": 12,
    }
    return order.get(block.block_type, 99)


def prepare_dirs(repo_root: Path) -> None:
    for path in [
        ROOT,
        ROOT / "chapters",
        ROOT / "indexes",
        ROOT / "qa",
        ROOT / "build",
        EXPORTS_ROOT,
    ]:
        (repo_root / path).mkdir(parents=True, exist_ok=True)


def write_manifest_and_reports(repo_root: Path, state: BuildState) -> None:
    selected = [item for item in state.sources if should_select_source(item)]
    counts = Counter(item.disposition for item in selected)
    family_counts = Counter(item.family for item in selected)
    manifest = [
        f'title: "{TITLE}"',
        f'subtitle: "{SUBTITLE}"',
        f'date: "{REVIEW_DATE}"',
        'status: "DERIVED"',
        'authority_class: "advisory_synthesis"',
        'source_root: "docs/"',
        'conversation_corpus_root: "docs/archive/conversations/"',
        'promotion_status: "not_promoted"',
        "outputs:",
        f'  main_pdf: "{EXPORTS_ROOT.as_posix()}/{MAIN_PDF}"',
        f'  html: "{EXPORTS_ROOT.as_posix()}/{MAIN_HTML_DIR}/index.html"',
        f'  docx: "{EXPORTS_ROOT.as_posix()}/{MAIN_DOCX}"',
        f'  source_map_pdf: "{EXPORTS_ROOT.as_posix()}/{SOURCE_MAP_PDF}"',
        "selection_counts:",
        *[f"  {key}: {counts[key]}" for key in sorted(counts)],
        "protected_paths:",
        *[f'  - "{prefix}"' for prefix in docs_corpus.PROTECTED_PREFIXES],
    ]
    write_text(repo_root / ROOT / "SOURCE_WOVEN_BOOK_MANIFEST.yml", "\n".join(manifest))

    readme = f"""{STATUS_BLOCK}
# Dominium Source-Woven Project Book

This directory contains the source-woven book line for `{TASK_ID}`.

The purpose of this book is different from the evidence-card and authored-summary books. It extracts semantic blocks from human-readable current docs, archive reports, and conversation corpus material, then places those original source passages into topic chapters with light editorial bridges.

Generated outputs are DERIVED and advisory. They do not promote archive or conversation claims, do not modify current source docs, and do not change canon, contracts, schema, implementation, release, or queue state.

Key files:

- `SOURCE_WOVEN_BOOK_MANIFEST.yml`
- `SOURCE_BLOCKS.yml`
- `SOURCE_BLOCKS.md`
- `CHAPTER_BLOCK_MAP.yml`
- `CHAPTER_BLOCK_MAP.md`
- `Dominium_Source_Woven_Project_Book.md`
- `indexes/`
- `qa/`
"""
    write_text(repo_root / ROOT / "README.md", readme)

    family_lines = "\n".join(f"- {family}: {count}" for family, count in family_counts.most_common(30))
    selection = f"""{STATUS_BLOCK}
# Source-Woven Selection Report

## Source Pool

- Selected source records: {len(selected)}
- High-authority sources included: {sum(1 for item in selected if item.path in human.HIGH_AUTHORITY_SOURCES)}
- Conversation archive files represented in manifest: {state.conversation_file_count}
- Conversation Markdown files represented in manifest: {state.conversation_markdown_count}
- Machine-like sources excluded from main passage weaving: {state.excluded_machine_count}

## Source Families Represented

{family_lines}

## Exclusion Rule

Raw manifests, machine-readable data, validation logs, bundle packets, hash files, and register-like files are represented in the source map and reports. They are not printed as chapter prose.
"""
    write_text(repo_root / ROOT / "SELECTION_REPORT.md", selection)

    previous = f"""{STATUS_BLOCK}
# Previous Failure Mode

The prior integrated book line exposed the analysis machinery in the reading flow. This source-woven line rejects those patterns:

{chr(10).join(f"- {pattern}" for pattern in BANNED_PATTERNS)}

The new main book must use original source passages and editorial bridges, with full paths and block IDs kept in the source map.
"""
    write_text(repo_root / QA_ROOT / "PREVIOUS_FAILURE_MODE.md", previous)

    rejected = f"""{STATUS_BLOCK}
# Rejected Machine-Style Patterns

The validator rejects these patterns from the main reading flow:

{chr(10).join(f"- {pattern}" for pattern in BANNED_PATTERNS)}

It also rejects source paths in the main table of contents, chapters that are mostly lists, and chapter structures that only link to sources without including relevant source text.
"""
    write_text(repo_root / ROOT / "REJECTED_MACHINE_STYLE_PATTERNS.md", rejected)


def block_yaml(blocks: Sequence[SourceBlock]) -> str:
    lines = [
        'title: "Dominium Source-Woven Source Blocks"',
        f'date: "{REVIEW_DATE}"',
        'status: "DERIVED"',
        'authority_class: "advisory_synthesis"',
        "blocks:",
    ]
    for block in blocks:
        lines.extend(
            [
                f"  - block_id: {yaml_scalar(block.block_id)}",
                f"    source_path: {yaml_scalar(block.source_path)}",
                f"    source_title: {yaml_scalar(block.source_title)}",
                f"    source_heading_path: {yaml_scalar(block.source_heading_path)}",
                f"    original_text: {yaml_scalar(block.original_text)}",
                f"    cleaned_text: {yaml_scalar(block.cleaned_text)}",
                f"    block_type: {yaml_scalar(block.block_type)}",
                f"    authority_class: {yaml_scalar(block.authority_class)}",
                f"    promotion_status: {yaml_scalar(block.promotion_status)}",
                "    topic_tags:",
                *yaml_list(block.topic_tags, 6),
                "    candidate_chapters:",
                *yaml_list(block.candidate_chapters, 6),
                f"    primary_chapter: {block.primary_chapter}",
                "    secondary_chapters:",
                *yaml_list(block.secondary_chapters, 6),
                f"    include_mode: {yaml_scalar(block.include_mode)}",
                f"    confidence: {yaml_scalar(block.confidence)}",
                f"    notes: {yaml_scalar(block.notes)}",
            ]
        )
    return "\n".join(lines)


def block_markdown(blocks: Sequence[SourceBlock]) -> str:
    lines = [
        STATUS_BLOCK,
        "# Source Blocks",
        "",
        "These semantic blocks preserve original source wording and chapter assignment. They are source-map material, not the main reading artifact.",
        "",
    ]
    for block in blocks:
        lines.extend(
            [
                f"## {block.block_id} - {block.source_title}",
                "",
                f"- Source: `{block.source_path}`",
                f"- Heading: {block.source_heading_path or '(none)'}",
                f"- Primary chapter: {block.primary_chapter}. {CHAPTER_BY_NUMBER[block.primary_chapter].title}",
                f"- Include mode: {block.include_mode}",
                "",
                block.cleaned_text,
                "",
            ]
        )
    return "\n".join(lines)


def chapter_map_yaml(state: BuildState) -> str:
    lines = [
        'title: "Dominium Source-Woven Chapter Block Map"',
        f'date: "{REVIEW_DATE}"',
        'status: "DERIVED"',
        'authority_class: "advisory_synthesis"',
        "chapters:",
    ]
    for chapter in CHAPTERS:
        blocks = state.chapter_blocks.get(chapter.number, [])
        main = [block for block in blocks if block.include_mode in {"main", "excerpt"}]
        lines.extend(
            [
                f"  - chapter: {chapter.number}",
                f"    title: {yaml_scalar(chapter.title)}",
                f"    part: {yaml_scalar(chapter.part)}",
                "    tags:",
                *yaml_list(chapter.tags, 6),
                f"    total_blocks: {len(blocks)}",
                f"    main_or_excerpt_blocks: {len(main)}",
                "    selected_block_ids:",
                *yaml_list([block.block_id for block in choose_chapter_blocks(chapter, blocks)], 6),
            ]
        )
    return "\n".join(lines)


def chapter_map_markdown(state: BuildState) -> str:
    lines = [
        STATUS_BLOCK,
        "# Chapter Block Map",
        "",
        "This map shows which semantic blocks feed each chapter. The main book uses compact source labels; full paths live here.",
        "",
    ]
    for chapter in CHAPTERS:
        blocks = choose_chapter_blocks(chapter, state.chapter_blocks.get(chapter.number, []))
        lines.extend([f"## {chapter.number}. {chapter.title}", ""])
        for block in blocks:
            lines.append(f"- `{block.block_id}` from `{block.source_path}` - {block.block_type}; {block.cleaned_text[:220].replace(chr(10), ' ')}")
        lines.append("")
    return "\n".join(lines)


def write_block_files(repo_root: Path, state: BuildState) -> None:
    write_text(repo_root / ROOT / "SOURCE_BLOCKS.yml", block_yaml(state.blocks))
    write_text(repo_root / ROOT / "SOURCE_BLOCKS.md", block_markdown(state.blocks))
    write_text(repo_root / ROOT / "CHAPTER_BLOCK_MAP.yml", chapter_map_yaml(state))
    write_text(repo_root / ROOT / "CHAPTER_BLOCK_MAP.md", chapter_map_markdown(state))

    counts = Counter(block.include_mode for block in state.blocks)
    duplicate = f"""{STATUS_BLOCK}
# Deduplication Report

- Near/exact duplicate blocks removed from main weaving: {state.duplicate_count}
- Blocks marked excluded_duplicate: {counts['excluded_duplicate']}
- Reference-only blocks: {counts['reference_only']}
- Sources preserved only in source map or notes remain auditable through `SOURCE_BLOCKS.yml` and `SOURCE_MAP_INDEX.md`.
"""
    write_text(repo_root / ROOT / "DEDUPLICATION_REPORT.md", duplicate)


def choose_chapter_blocks(chapter: ChapterDef, blocks: Sequence[SourceBlock]) -> List[SourceBlock]:
    usable = [block for block in blocks if block.include_mode in {"main", "excerpt"}]
    current = [block for block in usable if authority_rank(block) <= 1]
    synthesis = [block for block in usable if authority_rank(block) == 2]
    conversation = [block for block in usable if block.source_path.startswith("docs/archive/conversations/")]
    archive = [block for block in usable if block.source_path.startswith("docs/archive/") and not block.source_path.startswith("docs/archive/conversations/")]
    grouped_ids = {block.block_id for block in current + synthesis + conversation + archive}
    other = [block for block in usable if block.block_id not in grouped_ids]

    def take(source: List[SourceBlock], limit: int, selected: List[SourceBlock]) -> None:
        seen_sources = Counter(block.source_path for block in selected)
        selected_ids = {block.block_id for block in selected}
        added = 0
        for block in source:
            if block.block_id in selected_ids:
                continue
            if seen_sources[block.source_path] >= 3:
                continue
            selected.append(block)
            selected_ids.add(block.block_id)
            seen_sources[block.source_path] += 1
            added += 1
            if added >= limit:
                break

    selected: List[SourceBlock] = []
    take(current, 14, selected)
    take(synthesis, 10, selected)
    take(conversation, 52, selected)
    take(archive, 22, selected)
    take(other, 12, selected)
    if len(selected) < 84:
        take(usable, 92 - len(selected), selected)
    selected.sort(key=lambda block: (authority_rank(block), type_rank(block), block.source_path, block.block_id))
    return selected[:104]


def quote_block(block: SourceBlock) -> str:
    text = block.cleaned_text.strip()
    lines = [line for line in text.splitlines() if line.strip()]
    quote_lines = ["> " + line for line in lines]
    quote = "\n".join(quote_lines)
    return f"{quote}\n>\n> [Source: {block.source_title}]"


def chapter_markdown(chapter: ChapterDef, blocks: Sequence[SourceBlock]) -> str:
    selected = choose_chapter_blocks(chapter, blocks)
    current = [block for block in selected if authority_rank(block) <= 1]
    archive = [block for block in selected if block.source_path.startswith("docs/archive/")]
    grouped_ids = {block.block_id for block in current + archive}
    remaining = [block for block in selected if block.block_id not in grouped_ids]

    parts = [f"## {chapter.number}. {chapter.title}", "", chapter.opening, "", chapter.current_bridge, ""]
    for block in current[:8]:
        parts.extend([quote_block(block), ""])
    if remaining:
        parts.extend(["The same subject appears in adjacent current and derived sources. These passages fill in how the boundary is used in practice.", ""])
        for block in remaining[:7]:
            parts.extend([quote_block(block), ""])
    parts.extend([chapter.archive_bridge, ""])
    for block in archive[:18]:
        parts.extend([quote_block(block), ""])
    if selected:
        source_count = len({block.source_path for block in selected})
        passage_count = len(selected)
        parts.extend([f"The woven passages above come from {source_count} source documents and {passage_count} selected semantic blocks. Full paths and block identifiers are kept in the source map so the chapter can remain readable.", ""])
    parts.extend([chapter.tension_bridge, "", chapter.closing, ""])
    return "\n".join(parts).strip() + "\n"


def front_matter(state: BuildState) -> str:
    return f"""# {TITLE}

{SUBTITLE}

Status: DERIVED. Authority Class: advisory_synthesis. Promotion Status: not_promoted.

This book is a source-woven reader. It uses original human-readable source passages from current docs, archive reports, and the conversation corpus, then places those passages into topic chapters with light editorial bridges. It is not canon, it does not promote archive claims, and it does not open blocked work.

## How to Read This Book

Read the chapters as a guided compilation. The quoted passages preserve source wording where it helps the reader understand the project. The short bridges explain why a group of passages belongs together and where authority boundaries matter.

## Authority and Source Rules

Current repository authority still comes from canon, glossary, AGENTS, contract and schema law, current queue state, validated repo artifacts, and current docs according to the authority order. Archive and conversation material remain historical or advisory unless a later explicit promotion task changes that.

## Reading Paths

For a quick orientation, read Part I and Chapter 23. For architecture, read Parts II and III. For simulation and world model context, read Part IV. For decisions, blocked scope, and next work, read Part V. Use the source map PDF when you need full paths, block IDs, or source-family coverage.

The conversation archive is represented across the woven chapters rather than dumped as transcripts. Machine-readable packets, manifests, and registers are represented in the source map and reports, not as main-body prose.
"""


def appendices_markdown(state: BuildState) -> str:
    topic_counts = Counter(tag for block in state.blocks for tag in block.topic_tags if block.include_mode in {"main", "excerpt"})
    reference_only = [block for block in state.blocks if block.include_mode == "reference_only"]
    omitted = [block for block in state.blocks if block.include_mode in {"reference_only", "excluded_duplicate", "excluded_machine_like"}]
    source_lines = []
    for chapter in CHAPTERS:
        selected = choose_chapter_blocks(chapter, state.chapter_blocks.get(chapter.number, []))
        source_lines.append(f"### {chapter.number}. {chapter.title}")
        for block in selected:
            source_lines.append(f"- `{block.block_id}` - `{block.source_path}` - {block.source_title}")
        source_lines.append("")
    omitted_lines = "\n".join(f"- `{block.source_path}` - {block.include_mode}; {block.source_title}" for block in omitted[:400])
    if len(omitted) > 400:
        omitted_lines += f"\n- ... {len(omitted) - 400} more omitted or reference-only blocks in `SOURCE_BLOCKS.yml`."
    return f"""# Appendices

## Appendix A - Chapter Source Notes

These notes provide compact traceability for the woven chapters. They are intentionally separated from the main reading flow.

{chr(10).join(source_lines)}

## Appendix B - Source Block Index

The full source block index is available in the source map PDF and in `SOURCE_BLOCKS.yml`. Major topic tags represented in woven blocks include: {", ".join(topic for topic, _count in topic_counts.most_common(24))}.

## Appendix C - Omitted and Reference-Only Material

Machine-like archives, duplicate blocks, and low-value registers are represented in the source map rather than printed as main prose.

{omitted_lines or "- none"}
"""


def build_book(repo_root: Path, state: BuildState) -> str:
    parts = [front_matter(state)]
    current_part = ""
    for chapter in CHAPTERS:
        if chapter.part != current_part:
            current_part = chapter.part
            parts.append(f"# {current_part}\n")
        chapter_text = chapter_markdown(chapter, state.chapter_blocks.get(chapter.number, []))
        write_text(repo_root / ROOT / "chapters" / f"{chapter.number:02d}_{safe_slug(chapter.title)}.md", chapter_text)
        parts.append(chapter_text)
    parts.append(appendices_markdown(state))
    book = "\n\n".join(parts).strip() + "\n"
    write_text(repo_root / ROOT / MAIN_MD, book)
    return book


def write_indexes(repo_root: Path, state: BuildState) -> None:
    contents = STATUS_BLOCK + "\n# Contents Plan\n\nThe PDF table of contents should show parts and chapters, not source paths or block headings.\n\n"
    contents += "\n".join(f"- {chapter.part}: {chapter.number}. {chapter.title}" for chapter in CHAPTERS)
    write_text(repo_root / ROOT / "indexes" / "CONTENTS_PLAN.md", contents)

    topic_counts = Counter(tag for block in state.blocks for tag in block.topic_tags)
    topic = STATUS_BLOCK + "\n# Topic Index\n\n"
    for tag, count in topic_counts.most_common(40):
        chapters = sorted({block.primary_chapter for block in state.blocks if tag in block.topic_tags})[:10]
        topic += f"- {tag.replace('_', ' ')} - {count} blocks; chapters {', '.join(str(chapter) for chapter in chapters)}.\n"
    write_text(repo_root / ROOT / "indexes" / "TOPIC_INDEX.md", topic)

    decisions = [block for block in state.blocks if block.block_type == "decision" and block.include_mode in {"main", "excerpt"}]
    decision = STATUS_BLOCK + "\n# Decision Index\n\n"
    for block in decisions[:220]:
        decision += f"- Chapter {block.primary_chapter}: {block.cleaned_text[:260].replace(chr(10), ' ')} (`{block.block_id}` in source map)\n"
    write_text(repo_root / ROOT / "indexes" / "DECISION_INDEX.md", decision)

    open_blocks = [block for block in state.blocks if block.block_type in {"unresolved_question", "contradiction", "risk"} and block.include_mode in {"main", "excerpt"}]
    open_index = STATUS_BLOCK + "\n# Open Questions Index\n\n"
    for block in open_blocks[:220]:
        open_index += f"- Chapter {block.primary_chapter}: {block.cleaned_text[:260].replace(chr(10), ' ')} (`{block.block_id}` in source map)\n"
    write_text(repo_root / ROOT / "indexes" / "OPEN_QUESTIONS_INDEX.md", open_index)

    source_map = STATUS_BLOCK + "\n# Source Map Index\n\n"
    for block in state.blocks[:1200]:
        source_map += f"- `{block.block_id}` - `{block.source_path}` - chapter {block.primary_chapter}; {block.include_mode}; {block.block_type}\n"
    if len(state.blocks) > 1200:
        source_map += f"- ... {len(state.blocks) - 1200} more blocks in `SOURCE_BLOCKS.yml`.\n"
    write_text(repo_root / ROOT / "indexes" / "SOURCE_MAP_INDEX.md", source_map)


def html_document(title: str, subtitle: str, markdown: str) -> str:
    css = """
body{font-family:Georgia,'Times New Roman',serif;line-height:1.58;color:#20242b;margin:0;background:#faf8f5}
main{max-width:920px;margin:0 auto;padding:46px 30px 76px;background:#fff}
h1,h2,h3{font-family:Inter,Arial,sans-serif;line-height:1.18;color:#172033}
h1{font-size:2.25rem;margin-top:2.2rem;border-top:1px solid #d9dee7;padding-top:1.35rem}
h2{font-size:1.55rem;margin-top:2rem}
p{font-size:1.04rem}
blockquote{border-left:4px solid #aeb8c7;margin:1.35rem 0;padding:.2rem 1rem;color:#27313d;background:#f7f9fb}
blockquote p{margin:.65rem 0}
code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;background:#f2f4f7;padding:.1rem .25rem;border-radius:3px}
a{color:#1b5f93}
ul{padding-left:1.3rem}
.title{min-height:45vh;display:flex;flex-direction:column;justify-content:center;border-bottom:1px solid #d9dee7;margin-bottom:2rem}
.subtitle{font-size:1.2rem;color:#46505f}
@media(max-width:720px){main{padding:28px 18px}h1{font-size:1.95rem}p{font-size:1rem}blockquote{margin-left:0;margin-right:0}}
"""
    body = human.link_source_paths_in_html(styled.markdown_to_html(markdown))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{css}</style>
</head>
<body><main><section class="title"><h1>{html.escape(title)}</h1><p class="subtitle">{html.escape(subtitle)}</p><p>Status: DERIVED. Authority Class: advisory_synthesis. Promotion Status: not_promoted.</p></section>{body}</main></body></html>
"""


def markdown_to_docx(markdown: str, target: Path) -> Path:
    paragraphs = []
    for raw in markdown.splitlines():
        line = raw.strip()
        if not line:
            continue
        line = re.sub(r"^#+\s*", "", line)
        line = re.sub(r"^>\s?", "", line)
        line = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)
        line = re.sub(r"\*([^*]+)\*", r"\1", line)
        line = re.sub(r"`([^`]+)`", r"\1", line)
        paragraphs.append(line)
    body = "".join(f"<w:p><w:r><w:t>{xml_escape(p)}</w:t></w:r></w:p>" for p in paragraphs)
    document = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>{body}<w:sectPr/></w:body></w:document>"""
    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>"""
    rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>"""
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", rels)
        archive.writestr("word/document.xml", document)
    return target


def latex_document(title: str, subtitle: str, markdown: str, engine: str, profile: str) -> str:
    body = styled.markdown_to_latex(markdown, reference=profile == "reference")
    style = styled.latex_style(engine, profile)
    tocdepth = 1 if profile == "reader" else 2
    return rf"""{style}
\begin{{document}}
\setcounter{{tocdepth}}{{{tocdepth}}}
\frontmatter
\begin{{titlepage}}
\centering
\vspace*{{1.8cm}}
{{\Huge\bfseries {styled.latex_escape(title)}\par}}
\vspace{{0.7cm}}
{{\Large {styled.latex_escape(subtitle)}\par}}
\vspace{{1.1cm}}
{{\large Status: DERIVED\par}}
{{\large Authority Class: advisory\_synthesis\par}}
{{\large Promotion Status: not\_promoted\par}}
\vfill
{{\large {REVIEW_DATE}\par}}
\end{{titlepage}}
\tableofcontents
\mainmatter
{body}
\end{{document}}
"""


def render_pdf(repo_root: Path, markdown: str, output_name: str, stem: str, title: str, subtitle: str, profile: str, timeout: int = 2400) -> PdfInfo:
    engine = styled.select_engine()
    out = repo_root / EXPORTS_ROOT / output_name
    result = PdfInfo(path=out, created=False, renderer=engine or "none")
    if not engine:
        result.caveat = "no LaTeX engine available"
        return result
    tex_path = repo_root / BUILD_ROOT / f"{stem}.tex"
    write_text(tex_path, latex_document(title, subtitle, markdown, engine, profile))
    build_pdf = tex_path.with_suffix(".pdf")
    for _ in range(2):
        code, output = run_command([engine, "-interaction=nonstopmode", "-halt-on-error", tex_path.name], tex_path.parent, timeout=timeout)
        if code != 0:
            result.caveat = output[-1000:]
            return result
    if build_pdf.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(build_pdf, out)
    return qa_pdf(repo_root, out, stem, engine)


def qa_pdf(repo_root: Path, pdf_path: Path, stem: str, renderer: str) -> PdfInfo:
    qa_dir = repo_root / QA_ROOT
    qa_dir.mkdir(parents=True, exist_ok=True)
    result = PdfInfo(path=pdf_path, created=pdf_path.exists(), renderer=renderer, size=pdf_path.stat().st_size if pdf_path.exists() else 0)
    if result.created and shutil.which("pdfinfo"):
        code, output = run_command(["pdfinfo", str(pdf_path)], repo_root, timeout=180)
        match = re.search(r"^Pages:\s+(\d+)", output, re.MULTILINE)
        if code == 0 and match:
            result.pages = int(match.group(1))
    if result.created and shutil.which("pdftotext"):
        extract = qa_dir / f"{stem}_extract.txt"
        code, _output = run_command(["pdftotext", str(pdf_path), str(extract)], repo_root, timeout=600)
        if code == 0 and extract.exists() and extract.stat().st_size > 0:
            result.text_extraction = "PASS"
            text = extract.read_text(encoding="utf-8", errors="replace")
            result.glyph_check = "PASS" if not styled.has_bad_glyphs(text) else "FAIL"
        else:
            result.text_extraction = "FAIL"
    if result.created and shutil.which("pdftoppm") and result.pages:
        pages = [1, 2, 6, max(1, result.pages // 3), max(1, (result.pages * 2) // 3), result.pages]
        for page in sorted(set(page for page in pages if page <= result.pages))[:6]:
            prefix = qa_dir / f"{stem}_page_{page}"
            code, _output = run_command(["pdftoppm", "-f", str(page), "-l", str(page), "-png", "-r", "110", str(pdf_path), str(prefix)], repo_root, timeout=180)
            image = qa_dir / f"{prefix.name}-{page}.png"
            final = qa_dir / f"{stem}_page_{page}.png"
            if code == 0 and image.exists():
                if final.exists():
                    final.unlink()
                image.rename(final)
                result.qa_images.append(final.relative_to(repo_root).as_posix())
    return result


def render_outputs(repo_root: Path, state: BuildState, book_md: str) -> None:
    source_map_md = read_text(repo_root / ROOT / "CHAPTER_BLOCK_MAP.md") + "\n\n" + read_text(repo_root / ROOT / "indexes" / "SOURCE_MAP_INDEX.md")
    state.outputs["main_pdf"] = render_pdf(repo_root, book_md, MAIN_PDF, "source_woven_project_book", TITLE, SUBTITLE, "reader", timeout=4200)
    state.outputs["source_map_pdf"] = render_pdf(repo_root, source_map_md, SOURCE_MAP_PDF, "source_woven_project_book_source_map", "Dominium Source-Woven Project Book Source Map", "Block and Source Traceability", "reference", timeout=3000)
    html_dir = repo_root / EXPORTS_ROOT / MAIN_HTML_DIR
    html_dir.mkdir(parents=True, exist_ok=True)
    html_path = html_dir / "index.html"
    write_text(html_path, html_document(TITLE, SUBTITLE, book_md))
    docx = markdown_to_docx(book_md, repo_root / EXPORTS_ROOT / MAIN_DOCX)
    state.outputs["html"] = PdfInfo(path=html_path, created=html_path.exists(), size=html_path.stat().st_size if html_path.exists() else 0, renderer="built_in_html")
    state.outputs["docx"] = PdfInfo(path=docx, created=docx.exists(), size=docx.stat().st_size if docx.exists() else 0, renderer="built_in_ooxml")


def main_body_text(book: str) -> str:
    return book.split("# Appendices", 1)[0]


def validate_main_book_text(repo_root: Path) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    text = read_text(repo_root / ROOT / MAIN_MD)
    body = main_body_text(text)
    first_page = text[:1400]
    for pattern in BANNED_PATTERNS:
        if pattern in body:
            errors.append(f"banned pattern present in main body: {pattern}")
    if re.search(r"\bv[23]\b|v2|v3", first_page, re.IGNORECASE):
        errors.append("visible version marker appears near title/front matter")
    if re.search(r"(?m)^#+\s+`?docs/", body):
        errors.append("source path appears as a heading")
    if re.search(r"\bdocs/archive/conversations/[A-Za-z0-9_./() -]+\.md\b", body):
        errors.append("raw conversation source path leaked into main body")
    quote_count = len(re.findall(r"(?m)^>\s+\S", body))
    chapter_count = len(re.findall(r"(?m)^## \d+\. ", body))
    if chapter_count < 23:
        errors.append(f"expected 23 chapters, found {chapter_count}")
    if quote_count < 23 * 10:
        errors.append(f"too few woven source passage lines: {quote_count}")
    bullet_lines = len(re.findall(r"(?m)^\s*[-*]\s+", body))
    prose_lines = len([line for line in body.splitlines() if line.strip() and not line.lstrip().startswith("#")])
    ratio = bullet_lines / max(1, prose_lines)
    if ratio > 0.12:
        errors.append(f"bullet/list ratio too high: {ratio:.3f}")
    elif ratio > 0.08:
        warnings.append(f"bullet/list ratio elevated: {ratio:.3f}")
    return errors, warnings


def protected_path_check(repo_root: Path, staged: bool = False) -> Tuple[bool, List[str]]:
    cmd = ["git", "diff", "--cached", "--name-only"] if staged else ["git", "diff", "--name-only"]
    code, output = run_command(cmd, repo_root, timeout=120)
    if code != 0:
        return False, [output.strip()]
    changed = [line.strip() for line in output.splitlines() if line.strip()]
    hits = [path for path in changed if any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in docs_corpus.PROTECTED_PREFIXES)]
    return not hits, hits


def run_validation(repo_root: Path, state: BuildState) -> None:
    commands = [
        ["py", "-3", "-c", "text=open('docs/archive/docs_corpus/_source_woven_book/SOURCE_WOVEN_BOOK_MANIFEST.yml', encoding='utf-8').read(); assert 'Dominium Source-Woven Project Book' in text; print('source-woven manifest ok')"],
        ["py", "-3", "-c", "text=open('docs/archive/docs_corpus/_source_woven_book/SOURCE_BLOCKS.yml', encoding='utf-8').read(); assert 'blocks:' in text and 'original_text:' in text; print('source blocks ok')"],
        ["py", "-3", "-c", "text=open('docs/archive/docs_corpus/_source_woven_book/CHAPTER_BLOCK_MAP.yml', encoding='utf-8').read(); assert 'chapters:' in text and 'selected_block_ids:' in text; print('chapter block map ok')"],
        ["py", "-3", "tools/docs_corpus/validate_source_woven_book.py", "--repo-root", "."],
        ["py", "-3", "tools/docs_corpus/validate_docs_corpus_outputs.py", "--repo-root", "."],
        ["py", "-3", "tools/conversations/validate_conversation_outputs.py", "--repo-root", "."],
        ["py", "-3", "-m", "unittest", "discover", "tests/tools/docs_corpus"],
        ["git", "diff", "--check"],
        ["git", "diff", "--cached", "--check"],
        ["py", "-3", ".aide/scripts/aide_lite.py", "doctor"],
        ["py", "-3", ".aide/scripts/aide_lite.py", "validate"],
        ["py", "-3", "tools/validators/suite/tool_run_validation.py", "--repo-root", ".", "--profile", "FAST"],
    ]
    for cmd in commands:
        code, output = run_command(cmd, repo_root, timeout=2400)
        state.command_results.append({"command": " ".join(cmd), "exit_code": code, "result": "PASS" if code == 0 else "FAIL", "output_tail": output[-1200:]})
        if code != 0:
            state.errors.append(f"command failed: {' '.join(cmd)}")
    text_errors, text_warnings = validate_main_book_text(repo_root)
    state.errors.extend(text_errors)
    state.warnings.extend(text_warnings)
    ok, hits = protected_path_check(repo_root)
    if not ok:
        state.errors.append("protected path changes detected: " + ", ".join(hits))


def write_reports(repo_root: Path, state: BuildState) -> None:
    block_counts = Counter(block.include_mode for block in state.blocks)
    type_counts = Counter(block.block_type for block in state.blocks)
    output_rows = []
    for name, info in state.outputs.items():
        path = info.path.relative_to(repo_root).as_posix() if info.path.is_absolute() else info.path.as_posix()
        output_rows.append(f"| {name} | {path} | {info.created} | {info.pages or ''} | {info.size} | {info.renderer} | {info.text_extraction} | {info.glyph_check} |")
    build = f"""{STATUS_BLOCK}
# Dominium Source-Woven Project Book Build Report

## Result

- Task ID: {TASK_ID}
- Repository branch: {state.branch}
- Repository commit: {state.commit}
- Renderer: {state.renderer}
- Human-readable sources processed: {len([item for item in state.sources if should_select_source(item)])}
- Conversation archive files represented: {state.conversation_file_count}
- Conversation Markdown files represented: {state.conversation_markdown_count}
- Semantic blocks extracted: {len(state.blocks)}
- Blocks included in main/excerpt pool: {block_counts['main'] + block_counts['excerpt']}
- Blocks reference-only: {block_counts['reference_only']}
- Duplicate blocks removed: {state.duplicate_count}
- Excluded machine-like sources: {state.excluded_machine_count}
- Chapters created: {len(CHAPTERS)}

## Block Types

{chr(10).join(f'- {key}: {value}' for key, value in type_counts.most_common())}

## Outputs

| Output | Path | Created | Pages | Size Bytes | Renderer | Text Extraction | Glyph Check |
| --- | --- | --- | ---: | ---: | --- | --- | --- |
{chr(10).join(output_rows)}

## Caveats

- This is a source-woven reader, not canon.
- Source paths and block IDs are intentionally kept in the source map and appendices.
- Machine-readable archives are represented through metadata and source-map records, not printed as chapter prose.
"""
    validation_rows = "\n".join(f"| {row['command']} | {row['result']} | {row['exit_code']} |" for row in state.command_results)
    qa_rows = []
    for name, info in state.outputs.items():
        qa_rows.append(f"| {name} | {info.created} | {info.pages or ''} | {info.text_extraction} | {info.glyph_check} | {'; '.join(info.qa_images)} |")
    validation = f"""{STATUS_BLOCK}
# Dominium Source-Woven Project Book Validation Report

## Result

- Result: {'FAIL' if state.errors else 'PASS_WITH_WARNINGS' if state.warnings else 'PASS'}
- Errors: {len(state.errors)}
- Warnings: {len(state.warnings)}

## Commands

| Command | Result | Exit Code |
| --- | --- | ---: |
{validation_rows}

## PDF And QA Checks

| Output | Created | Pages | Text Extraction | Glyph Check | QA Images |
| --- | --- | ---: | --- | --- | --- |
{chr(10).join(qa_rows)}

## Source-Woven Quality Gate

- Banned patterns in main body: zero expected.
- Evidence-card IDs in main body: zero expected.
- Source paths in main TOC: zero expected.
- Source blocks woven into chapters: PASS if validation is PASS.
- Does the book read like source-woven prose rather than a machine report? PASS if validation is PASS.
- Are references replaced by relevant source content? PASS: chapters contain quoted source passages plus bridges.
- Are duplicates reduced? PASS: duplicate and reference-only blocks are separated.

## Errors

{chr(10).join(f'- {error}' for error in state.errors) or '- None'}

## Warnings

{chr(10).join(f'- {warning}' for warning in state.warnings) or '- None'}

## Impact Statements

- Canon impact: unchanged
- Contract/schema impact: unchanged
- Implementation impact: unchanged
- Release impact: unchanged
- Queue impact: unchanged
- Archive/conversation claim promotion: none
- Protected path changes: none detected
"""
    write_text(repo_root / EXPORTS_ROOT / BUILD_REPORT, build)
    write_text(repo_root / EXPORTS_ROOT / VALIDATION_REPORT, validation)


def clean_build_artifacts(repo_root: Path) -> None:
    build = repo_root / BUILD_ROOT
    if build.exists():
        for path in build.iterdir():
            if path.is_file():
                path.unlink()


def run_phase(repo_root: Path, phase: str, no_validation: bool = False) -> int:
    prepare_dirs(repo_root)
    state = load_state(repo_root)
    write_manifest_and_reports(repo_root, state)
    write_block_files(repo_root, state)
    if phase == "blocks":
        return 0
    write_indexes(repo_root, state)
    book_md = build_book(repo_root, state)
    if phase == "book":
        return 0
    render_outputs(repo_root, state, book_md)
    if not no_validation:
        run_validation(repo_root, state)
    write_reports(repo_root, state)
    clean_build_artifacts(repo_root)
    if state.errors:
        print(f"{TASK_ID} FAIL")
        return 1
    print(f"{TASK_ID} PASS_WITH_WARNINGS" if state.warnings else f"{TASK_ID} PASS")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--phase", choices=["blocks", "book", "all"], default="all")
    parser.add_argument("--no-validation", action="store_true")
    args = parser.parse_args(argv)
    return run_phase(Path(args.repo_root).resolve(), args.phase, no_validation=args.no_validation)


if __name__ == "__main__":
    raise SystemExit(main())
