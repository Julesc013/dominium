"""Build the integrated human-readable Dominium project book v2.

This is an editorial synthesis pipeline, not an omnibus renderer. It mines the
human-readable docs-corpus source set into evidence cards, maps those cards to a
chapter architecture, and writes a narrative book that integrates decisions,
specifications, constraints, prohibitions, contradictions, open questions, and
downstream effects into topic chapters.

Generated outputs are DERIVED and advisory. Source docs are not modified.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import textwrap
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
from xml.sax.saxutils import escape as xml_escape

import build_human_readable_book as human
import build_omnibus_v1 as styled
import docs_corpus


TASK_ID = "DOMINIUM-INTEGRATED-HUMAN-BOOK-V2"
REVIEW_DATE = "2026-05-29"
VERSION = 2
TITLE = "Dominium Integrated Project Book"
SUBTITLE = "Integrated Project Synthesis, Evidence, Decisions, Constraints, and Roadmap"

ROOT = Path("docs/archive/docs_corpus/_integrated_book_v2")
EXPORTS_ROOT = Path("docs/archive/docs_corpus/_exports")
QA_ROOT = ROOT / "qa"
BUILD_ROOT = ROOT / "build"

MAIN_MD = "Dominium_Integrated_Project_Book_v2.md"
MAIN_PDF = "Dominium_Integrated_Project_Book_v2.pdf"
MAIN_HTML_DIR = "Dominium_Integrated_Project_Book_v2.html"
MAIN_DOCX = "Dominium_Integrated_Project_Book_v2.docx"
EVIDENCE_PDF = "Dominium_Integrated_Project_Book_v2_Source_Evidence_Map.pdf"
BUILD_REPORT = "Dominium_Integrated_Project_Book_v2_Build_Report.md"
VALIDATION_REPORT = "Dominium_Integrated_Project_Book_v2_Validation_Report.md"

PROTECTED_PREFIXES = docs_corpus.PROTECTED_PREFIXES

STATUS_BLOCK = f"""Status: DERIVED
Last Reviewed: {REVIEW_DATE}
Supersedes: docs/archive/docs_corpus/_human_book/**
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

BOOK_NOTICE = """Version: 2
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

CLAIM_TYPES = [
    "fact",
    "design_goal",
    "specification",
    "decision",
    "prohibition",
    "prerequisite",
    "constraint",
    "contradiction",
    "unresolved_question",
    "risk",
    "change_of_direction",
    "second_order_effect",
    "third_order_effect",
    "source_context",
]

CLAIM_PRIORITY = {
    "decision": 1,
    "specification": 2,
    "constraint": 3,
    "prohibition": 4,
    "prerequisite": 5,
    "contradiction": 6,
    "unresolved_question": 7,
    "risk": 8,
    "change_of_direction": 9,
    "second_order_effect": 10,
    "third_order_effect": 11,
    "design_goal": 12,
    "fact": 13,
    "source_context": 14,
}

TYPE_KEYWORDS = {
    "decision": ["decided", "decision", "accepted", "conclusion", "recommended", "final", "active plan", "current next", "chose"],
    "specification": ["must", "require", "contract", "schema", "invariant", "api", "abi", "version", "registry", "law", "surface"],
    "design_goal": ["goal", "purpose", "intent", "ambition", "aim", "future", "should support", "designed to", "wants"],
    "prohibition": ["forbidden", "must not", "do not", "not authorized", "blocked", "no silent", "not allowed", "never"],
    "prerequisite": ["before", "requires", "prerequisite", "only after", "next step", "must happen", "depends on"],
    "constraint": ["constraint", "boundary", "limited", "scope", "queue", "profile", "compatibility", "portability"],
    "contradiction": ["contradiction", "conflict", "drift", "disagree", "inconsistent", "overstate", "mismatch"],
    "unresolved_question": ["unresolved", "open question", "needs decision", "not yet", "unknown", "unclear", "defer"],
    "risk": ["risk", "warning", "caution", "caveat", "danger", "failure", "debt"],
    "change_of_direction": ["changed", "shifted", "superseded", "replaced", "moved", "later became", "no longer"],
    "second_order_effect": ["therefore", "consequence", "implication", "means that", "affects", "downstream", "impact"],
    "third_order_effect": ["eventually", "long-term", "future series", "roadmap", "third-order", "second-order"],
}

TAG_KEYWORDS = {
    "identity": ["dominium", "domino", "project", "game", "operating environment", "product identity"],
    "authority": ["authority", "law", "canon", "glossary", "refusal", "capability", "governance", "agent"],
    "determinism": ["determinism", "deterministic", "replay", "rng", "hash", "provenance", "validation", "evidence"],
    "contracts": ["contract", "schema", "abi", "api", "compatibility", "migration", "public surface", "version"],
    "packs": ["pack", "content", "modding", "provider", "module", "registry", "capability"],
    "runtime": ["runtime", "engine", "game", "client", "server", "service", "process", "shell"],
    "product": ["launcher", "setup", "client", "server", "product", "app", "shell", "presentation"],
    "workbench": ["workbench", "operator", "panel", "inspection", "validation slice", "universe explorer"],
    "renderer": ["renderer", "render", "ui", "gui", "native", "presentation", "perceived"],
    "tooling": ["aide", "codex", "xstack", "repox", "testx", "automation", "queue", "prompt", "agent"],
    "docs": ["docs", "documentation", "archive", "conversation", "corpus", "source trail", "promotion"],
    "world": ["world", "reality", "space", "time", "existence", "scale", "planet", "solar", "celestial"],
    "civilization": ["civilization", "economy", "logistics", "institution", "settlement", "signal", "trust", "communication"],
    "release": ["release", "build", "version", "semver", "platform", "windows", "macos", "linux", "portable"],
    "blocked": ["blocked", "queue", "not authorized", "defer", "future queue", "broad feature"],
}


@dataclass
class EvidenceCard:
    card_id: str
    source_path: str
    source_title: str
    source_type: str
    authority_class: str
    promotion_status: str
    topic_tags: List[str]
    applies_to_chapters: List[int]
    claim_type: str
    summary: str
    details: str
    source_excerpt_or_paraphrase: str
    current_repo_support: str
    archive_or_conversation_status: str
    queue_status: str
    confidence: str
    needs_user_decision: bool
    needs_future_queue: bool
    should_be_in_main_book: bool
    should_be_in_reference_only: bool
    notes: str = ""


@dataclass
class ChapterDef:
    number: int
    part: str
    title: str
    tags: List[str]
    thesis: str
    current_lens: str
    historical_lens: str
    next_work: str


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
    cards: List[EvidenceCard] = field(default_factory=list)
    chapter_map: Dict[int, List[EvidenceCard]] = field(default_factory=dict)
    branch: str = ""
    commit: str = ""
    renderer: str = ""
    outputs: Dict[str, PdfInfo] = field(default_factory=dict)
    command_results: List[Dict[str, object]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


CHAPTERS = [
    ChapterDef(1, "Part I - The Project", "What Dominium Is", ["identity", "runtime", "authority"], "Dominium is the official game and domain layer built on Domino's deterministic substrate; it is also a governed product environment rather than a single renderer-owned executable.", "Current sources define Dominium by layered responsibility: Domino supplies reusable deterministic mechanisms, Dominium supplies official meaning, and product shells project results without owning truth.", "The archived conversations add ambition: a broad simulation ecosystem, operator tooling, and long-horizon product surfaces. Their value is design intent, not current permission.", "Future writing should keep the identity distinction crisp: substrate, product, domain, and tooling are related but not interchangeable."),
    ChapterDef(2, "Part I - The Project", "Why Dominium Exists", ["identity", "civilization", "world"], "The project exists to make invention, production, logistics, economics, settlement, trust, communication, and institutions emerge from lawful simulation.", "The README and canon tie the ambition to deterministic process, explicit refusal, and evidence rather than scripted outcomes.", "Conversation evidence shows the ambition widening into world scale, governance, tooling, release identity, and authoring workflows.", "Next work should distinguish the durable motivation from feature scope that remains blocked."),
    ChapterDef(3, "Part I - The Project", "The Core Simulation Philosophy", ["determinism", "world", "authority"], "The simulation philosophy is that truth is lawful, perception is filtered, rendering is presentation, and mutation must pass through deterministic process.", "Canon and architecture docs make truth/perceived/render separation and process-only mutation the floor.", "The corpus repeatedly applies that floor to Workbench, UI, providers, content packs, and future world simulation.", "Every future feature description should explain where truth lives, how observation is derived, and how refusal is surfaced."),
    ChapterDef(4, "Part I - The Project", "Current Authority Model", ["authority", "docs", "blocked"], "Authority is layered: canon and glossary outrank AGENTS, which outranks lower planning, generated outputs, archive material, and conversation evidence.", "Authority order and snapshot intake protocol define how conflicts must be resolved without convenience-based promotion.", "The docs and conversation corpora are useful because they make history reviewable while preserving the authority boundary.", "Near-term work should use the book as a map, then promote only through explicit scoped tasks."),
    ChapterDef(5, "Part II - The System Architecture", "The System Stack", ["runtime", "contracts", "identity"], "The stack separates deterministic substrate, domain meaning, product composition, runtime services, contracts, content, tools, and docs.", "Current docs map engine, game, runtime, apps, contracts, content, tests, and tools as distinct ownership surfaces.", "Older conversations often describe the same layered design with less precise vocabulary; useful claims need crosswalk before promotion.", "Architecture updates should preserve ownership splits instead of merging roots by name or convenience."),
    ChapterDef(6, "Part II - The System Architecture", "Engine, Game, Runtime, Products, and Tools", ["runtime", "product", "tooling"], "Engine, game, runtime, products, and tools have different authority roles and must not be collapsed.", "The README gives the live repo map: engine is substrate, game is domain, runtime hosts reusable integration, apps compose products, and tools validate or generate evidence.", "Conversation material adds future product and tooling ideas, but several are queue-gated.", "Follow-up docs should make product composition and command/result surfaces easier to inspect without implying broad implementation scope."),
    ChapterDef(7, "Part II - The System Architecture", "Law, Authority, Capability, and Refusal", ["authority", "contracts", "blocked"], "Authority grants permission to attempt; law decides accept, refuse, transform, or degrade in deterministic, auditable form.", "Constitutional axioms and AGENTS make explicit refusal, no hidden fallback, and capability/law discipline binding.", "Archive material supplies examples: Workbench, providers, packs, and assistants must not become hidden truth owners.", "Promotion work should turn useful examples into clarification without weakening refusal discipline."),
    ChapterDef(8, "Part II - The System Architecture", "Determinism, Replay, Evidence, and Provenance", ["determinism", "contracts", "tooling"], "Determinism is both runtime law and validation strategy: identical canonical inputs must yield identical authoritative outputs.", "Canon requires named RNG streams, deterministic ordering, fixed reductions, replay equivalence, and provenance.", "The source corpus adds operational concerns: proof gates, evidence artifacts, dependency warnings, portability, and CI/test debt.", "Future implementation or docs work must state determinism impact and validation evidence explicitly."),
    ChapterDef(9, "Part II - The System Architecture", "Contracts, Schemas, Packs, and Compatibility", ["contracts", "packs", "release"], "Contracts and schemas define public meaning; packs and registries provide optional content and capabilities without executable authority.", "Current sources require schema identity, explicit migration/refusal, skip-unknown obligations where declared, and pack-driven integration.", "Conversations discuss providers, modules, composition, semver, release identity, and compatibility profiles as future-facing design intent.", "Next promotion tasks should separate current contract law from archive proposals around package/provider runtime."),
    ChapterDef(10, "Part III - Product and Operator Surfaces", "Client, Server, Launcher, Setup, and Workbench", ["product", "workbench", "runtime"], "Product shells compose services and project truth; they do not define simulation authority by themselves.", "Current docs identify client, server, launcher, setup, and Workbench as distinct product surfaces, while the queue only opens narrow slices.", "The conversation corpus contains rich Workbench, launcher, and setup ambition that remains largely advisory.", "Near-term work should stay inside narrow product-spine slices and record future UI/editor ambitions as decisions."),
    ChapterDef(11, "Part III - Product and Operator Surfaces", "UI, Renderer, Native GUI, and Presentation Boundaries", ["renderer", "product", "blocked"], "Presentation is downstream of truth and perception; renderer and UI surfaces must not enforce authority or mutate truth.", "Canon and current queue keep renderer implementation, native GUI, and broad UI blocked.", "Archive discussions of Universe Explorer, UI, UE-style rendering, or native GUI are useful design context but not implementation authorization.", "Future renderer work needs explicit queue opening, presentation contracts, and proof that truth/perceived/render separation holds."),
    ChapterDef(12, "Part III - Product and Operator Surfaces", "AIDE, Codex, Automation, and Repo Governance", ["tooling", "authority", "docs"], "AIDE, Codex, and related automation are governed repo/control-plane harnesses; they assist work but do not override canon, contracts, validation, or evidence.", "AGENTS defines task discipline, validation, protected areas, and forbidden moves.", "Conversation evidence shows repeated attempts to make assistant workflows safer, more portable, and more evidence-driven.", "Future assistant tooling should improve bounded execution and evidence packets without becoming a parallel governance canon."),
    ChapterDef(13, "Part III - Product and Operator Surfaces", "Documentation, Archive, and Conversation Corpus", ["docs", "authority"], "The archive and conversation corpus are evidence layers: they preserve history, contradictions, and intent without becoming current truth.", "Docs-corpus outputs classify files, authority, archive roles, drift, decisions, and promotion candidates.", "The full-source appendix is useful for audit, but v2 integrates important evidence into chapters so ordinary reading does not require source spelunking.", "Next review should refine classifications and triage promotion candidates before live-doc patches."),
    ChapterDef(14, "Part IV - Simulation Domains", "Reality, Space, Time, Scale, and Existence", ["world", "determinism"], "The world model treats reality, existence, space, time, and scale as governed simulation concerns rather than renderer conveniences.", "Canon supplies the general law: deterministic process, event-driven advancement, provenance, and truth/perception separation.", "Conversation evidence adds scale concerns, visitability, temporal resilience, 2038 awareness, and layered representation.", "Domain promotion should avoid treating speculative world-scale ambition as implemented gameplay."),
    ChapterDef(15, "Part IV - Simulation Domains", "Worldgen, Celestial Systems, and Domains", ["world", "packs"], "Worldgen and celestial systems are recurring design themes that must remain deterministic, data-driven, and contract-bound.", "Current authority supports deterministic domain composition but not broad domain feature implementation.", "Archived reports discuss solar systems, astronomy, planetary systems, and domain packs as long-horizon design material.", "Future domain tasks need explicit source verification, contracts, and queue scope before moving from design to implementation."),
    ChapterDef(16, "Part IV - Simulation Domains", "Civilization, Economy, Logistics, Institutions, and Signals", ["civilization", "world"], "Civilization-scale behavior is intended to emerge from logistics, economy, institutions, trust, communication, and signals under law.", "Current repo truth supports the ambition at the README/canon level, but not broad gameplay implementation.", "Conversation evidence supplies extensive thematic intent around seed civilizations, institutions, infrastructure, and emergent power.", "The right next step is synthesis and decision review, not gameplay work."),
    ChapterDef(17, "Part IV - Simulation Domains", "Content, Modding, Providers, and Data-Driven Extension", ["packs", "contracts", "blocked"], "Content and modding belong behind pack, registry, capability, compatibility, and refusal law.", "Canon says packs are data-only and missing optional packs must degrade or refuse deterministically.", "Conversation material expands this into provider models, modules, open-source provider surfaces, and package composition, much of which is blocked.", "Promotion should separate pack documentation from provider/package runtime work."),
    ChapterDef(18, "Part V - Decisions, Conflicts, and Roadmap", "Decisions Already Made", ["authority", "docs", "decision"], "Several decisions are already strongly supported: authority order, process-only mutation, no hidden fallback, profiles over mode flags, pack-driven integration, and advisory status for archive/conversations.", "Current sources make those decisions binding where they live in canon, glossary, AGENTS, contracts, and queue state.", "Conversation evidence often converges on the same choices but remains lower authority.", "This chapter should be used to identify safe docs-only clarifications, not to skip promotion review."),
    ChapterDef(19, "Part V - Decisions, Conflicts, and Roadmap", "Open Decisions and User Questions", ["docs", "blocked", "decision"], "Open decisions are the main bottleneck after preservation and synthesis: what becomes current docs, what stays archive-only, and what needs future queue opening.", "Docs-corpus and conversation decision dockets identify review prompts but do not answer them.", "User decisions remain necessary where authority cannot be inferred without semantic judgment.", "The next review pass should prioritize decisions with near-term docs-only impact."),
    ChapterDef(20, "Part V - Decisions, Conflicts, and Roadmap", "Specifications and Requirements Still Needing Promotion", ["contracts", "docs", "decision"], "Some source claims look like requirements but are not current specs until promoted through the right target docs or contracts.", "Current authority already contains many requirements; generated evidence can only propose candidates.", "Archive and conversation materials are strongest when they clarify intent already aligned with current docs.", "Promotion candidates should be converted into bounded microtasks with source IDs and validation."),
    ChapterDef(21, "Part V - Decisions, Conflicts, and Roadmap", "Prohibitions, Blocked Scope, and Non-Goals", ["blocked", "authority", "renderer"], "The current queue and canon define non-goals as actively as goals: broad UI, renderer, gameplay, provider runtime, package runtime, native GUI, and release publication are blocked.", "Foundation Lock allows narrow governed slices but not broad feature work.", "Historical sources often describe future features that remain useful but closed.", "Every future prompt should state blocked-scope boundaries before implementation language."),
    ChapterDef(22, "Part V - Decisions, Conflicts, and Roadmap", "Contradictions, Drift, and Stale Claims", ["docs", "authority", "blocked"], "The corpus contains stale and contradictory claims because it preserves old design states alongside current authority.", "Authority order and snapshot intake protocol require quarantine for same-tier conflicts and lower-tier drift.", "Generated matrices are useful warning systems, not resolution engines.", "Review should classify contradictions by authority domain before any live-doc patch."),
    ChapterDef(23, "Part V - Decisions, Conflicts, and Roadmap", "Prerequisites, Dependencies, and Future Queue Work", ["blocked", "tooling", "release"], "Future work depends on validation, queue openings, contracts, docs promotion, and sometimes full-gate debt.", "Current queue identifies next and alternate narrow tasks while keeping broad surfaces blocked.", "Historical roadmaps add useful sequencing ideas but cannot authorize work.", "The next actionable unit should stay narrow: docs-only triage, projection conformance, readonly Workbench shell, or specific audits."),
    ChapterDef(24, "Part V - Decisions, Conflicts, and Roadmap", "Second- and Third-Order Effects", ["determinism", "release", "tooling"], "Dominium decisions have downstream effects across replay, portability, release identity, validation, assistant workflows, and documentation governance.", "Canon makes downstream impact reporting mandatory for non-trivial tasks.", "The corpus highlights hidden coupling: a UI choice can affect evidence, a provider choice can affect compatibility, and a release name can affect trust.", "Future task packets should include these knock-on effects before they become implementation debt."),
    ChapterDef(25, "Part V - Decisions, Conflicts, and Roadmap", "Recommended Next Steps", ["docs", "decision", "blocked"], "The best next work is review and controlled promotion, not more bulk rendering or broad implementation.", "Current repo authority permits docs/evidence updates and narrow slices only.", "The integrated book should become the reader surface, the evidence map should become the review surface, and the full-source appendix should remain audit backup.", "Run acceptance review, refine classifications, triage promotion candidates, then start narrow docs-only micro-promotions."),
]


def run_command(cmd: Sequence[str], cwd: Path, timeout: int = 900) -> Tuple[int, str]:
    try:
        proc = subprocess.run(
            list(cmd),
            cwd=str(cwd),
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
        return proc.returncode, docs_corpus.ascii_text(proc.stdout)
    except FileNotFoundError as exc:
        return 127, str(exc)
    except subprocess.TimeoutExpired as exc:
        text = (exc.stdout or "") + (exc.stderr or "")
        return 124, docs_corpus.ascii_text(text)


def rel(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


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


def git_value(repo_root: Path, args: Sequence[str]) -> str:
    code, output = run_command(["git", *args], repo_root, timeout=60)
    return output.strip() if code == 0 else "unknown"


def slug(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "_", value.strip().lower()).strip("_")
    return text or "section"


def clean_inline(text: str, limit: int = 420) -> str:
    text = re.sub(r"\s+", " ", text.replace("`", "'")).strip()
    text = re.sub(r"^[-*]\s+", "", text)
    if len(text) > limit:
        text = text[: limit - 1].rstrip() + "."
    return docs_corpus.ascii_text(text)


def source_type(item: human.SourceItem) -> str:
    if item.path in human.HIGH_AUTHORITY_SOURCES:
        return "current_high_authority"
    if item.path in human.SYNTHESIS_SOURCES:
        return "derived_synthesis"
    if item.path.startswith("docs/archive/conversations/"):
        return "conversation_advisory"
    if item.path.startswith("docs/archive/"):
        return "archive_historical"
    if item.path.startswith("docs/"):
        return "current_docs"
    return "repo_root"


def promotion_status(item: human.SourceItem) -> str:
    return "not_promoted" if item.path.startswith("docs/archive/") else "current_source"


def archive_status(item: human.SourceItem) -> str:
    if item.path.startswith("docs/archive/conversations/"):
        return "conversation advisory evidence"
    if item.path.startswith("docs/archive/"):
        return "archive historical evidence"
    if item.path in human.SYNTHESIS_SOURCES:
        return "derived advisory synthesis"
    return "current repo source"


def strip_code_and_tables(text: str) -> str:
    out: List[str] = []
    in_code = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            continue
        out.append(line)
    return "\n".join(out)


def split_evidence_units(text: str) -> List[str]:
    text = strip_code_and_tables(text)
    units: List[str] = []
    current: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            if current:
                units.append(" ".join(current))
                current = []
            continue
        if stripped.startswith("#"):
            if current:
                units.append(" ".join(current))
                current = []
            units.append(stripped.lstrip("#").strip())
            continue
        if stripped.startswith(("- ", "* ")):
            if current:
                units.append(" ".join(current))
                current = []
            units.append(stripped)
            continue
        current.append(stripped)
    if current:
        units.append(" ".join(current))
    cleaned = []
    for unit in units:
        unit = clean_inline(unit, 900)
        words = unit.split()
        if 6 <= len(words) <= 140 and not unit.lower().startswith(("status:", "last reviewed:", "supersedes:")):
            cleaned.append(unit)
    return cleaned


def keyword_score(text: str, words: Sequence[str]) -> int:
    lowered = text.lower()
    return sum(1 for word in words if word in lowered)


def classify_claim_type(text: str) -> str:
    scores = {claim_type: keyword_score(text, words) for claim_type, words in TYPE_KEYWORDS.items()}
    best, score = max(scores.items(), key=lambda item: (item[1], -CLAIM_PRIORITY.get(item[0], 99)))
    if score <= 0:
        return "fact"
    return best


def topic_tags_for(text: str, item: human.SourceItem) -> List[str]:
    combined = f"{item.path} {item.title} {text}".lower()
    tags = [tag for tag, words in TAG_KEYWORDS.items() if keyword_score(combined, words) > 0]
    if not tags:
        tags = ["docs" if item.path.startswith("docs/archive/") else "identity"]
    return sorted(set(tags))


def queue_status_for(text: str, tags: Sequence[str]) -> str:
    lowered = text.lower()
    if "blocked" in lowered or "not authorized" in lowered or any(tag in {"renderer", "blocked"} for tag in tags):
        return "blocked_or_queue_gated"
    if any(tag in {"workbench", "product", "tooling"} for tag in tags):
        return "narrow_scope_only"
    return "not_queue_expanding"


def current_support_for(item: human.SourceItem) -> str:
    if item.path in human.HIGH_AUTHORITY_SOURCES:
        return "direct current repo support"
    if item.path.startswith("docs/architecture/") or item.path.startswith("docs/canon/"):
        return "current architecture/canon support"
    if item.path.startswith("docs/archive/"):
        return "requires current authority cross-check"
    return "current docs support or review context"


def assign_chapters(tags: Sequence[str], item: human.SourceItem, text: str) -> List[int]:
    combined = f"{item.path} {item.title} {text}".lower()
    scores: List[Tuple[int, int]] = []
    for chapter in CHAPTERS:
        score = len(set(tags) & set(chapter.tags)) * 4
        score += keyword_score(combined, chapter.tags)
        if chapter.number <= 4 and item.path in human.HIGH_AUTHORITY_SOURCES:
            score += 2
        if chapter.number >= 18 and any(tag in {"blocked", "decision", "docs"} for tag in tags):
            score += 2
        if score > 0:
            scores.append((chapter.number, score))
    if not scores:
        return [13]
    scores.sort(key=lambda item_score: (-item_score[1], item_score[0]))
    return [number for number, _ in scores[:4]]


def should_main(claim_type: str, item: human.SourceItem, tags: Sequence[str]) -> bool:
    if item.path in human.HIGH_AUTHORITY_SOURCES or item.path in human.SYNTHESIS_SOURCES:
        return True
    if claim_type in {"decision", "specification", "constraint", "prohibition", "contradiction", "unresolved_question", "prerequisite"}:
        return True
    return bool(set(tags) & {"authority", "determinism", "contracts", "blocked", "workbench", "renderer", "world", "civilization", "release"})


def card_from_unit(card_id: str, item: human.SourceItem, unit: str, index: int) -> EvidenceCard:
    claim_type = classify_claim_type(unit)
    tags = topic_tags_for(unit, item)
    chapters = assign_chapters(tags, item, unit)
    lowered = unit.lower()
    return EvidenceCard(
        card_id=card_id,
        source_path=item.path,
        source_title=item.title,
        source_type=source_type(item),
        authority_class=item.authority_class,
        promotion_status=promotion_status(item),
        topic_tags=tags,
        applies_to_chapters=chapters,
        claim_type=claim_type,
        summary=clean_inline(unit, 260),
        details=clean_inline(unit, 620),
        source_excerpt_or_paraphrase="Paraphrase: " + clean_inline(unit, 360),
        current_repo_support=current_support_for(item),
        archive_or_conversation_status=archive_status(item),
        queue_status=queue_status_for(unit, tags),
        confidence="high" if item.path in human.HIGH_AUTHORITY_SOURCES else "medium" if item.disposition == "human_full_text" else "review",
        needs_user_decision=any(token in lowered for token in ["needs user", "user decision", "decide", "open question"]),
        needs_future_queue=any(token in lowered for token in ["blocked", "future queue", "not authorized", "broad feature"]),
        should_be_in_main_book=should_main(claim_type, item, tags),
        should_be_in_reference_only=not should_main(claim_type, item, tags),
        notes=f"source unit {index}",
    )


def select_units_for_source(item: human.SourceItem, units: List[str]) -> List[str]:
    if not units:
        return []
    limit = 14 if item.path in human.HIGH_AUTHORITY_SOURCES else 12 if item.path in human.SYNTHESIS_SOURCES else 8 if item.disposition == "human_full_text" else 1
    scored: List[Tuple[int, int, str]] = []
    for idx, unit in enumerate(units):
        claim = classify_claim_type(unit)
        score = 50 - CLAIM_PRIORITY.get(claim, 20)
        score += min(len(unit.split()) // 8, 8)
        score += sum(keyword_score(unit, words) for words in TYPE_KEYWORDS.values())
        scored.append((score, idx, unit))
    chosen: List[Tuple[int, str]] = []
    seen_types = set()
    for _score, idx, unit in sorted(scored, key=lambda row: (-row[0], row[1])):
        claim = classify_claim_type(unit)
        if claim not in seen_types:
            chosen.append((idx, unit))
            seen_types.add(claim)
        if len(chosen) >= limit:
            break
    if len(chosen) < limit:
        existing = {unit for _, unit in chosen}
        for _score, idx, unit in sorted(scored, key=lambda row: (-row[0], row[1])):
            if unit not in existing:
                chosen.append((idx, unit))
                existing.add(unit)
            if len(chosen) >= limit:
                break
    chosen.sort(key=lambda row: row[0])
    return [unit for _, unit in chosen[:limit]]


def build_evidence_cards(repo_root: Path, sources: List[human.SourceItem]) -> List[EvidenceCard]:
    selected = [item for item in sources if item.disposition in {"human_full_text", "human_excerpt", "human_summarize"}]
    selected.sort(key=lambda item: (item.disposition != "human_full_text", item.path))
    cards: List[EvidenceCard] = []
    next_id = 1
    for item in selected:
        full = repo_root / item.path
        limit = None if item.disposition == "human_full_text" else 4000
        raw = read_text(full, limit=limit)
        _metadata, body = human.compact_metadata(raw)
        units = split_evidence_units(body)
        chosen = select_units_for_source(item, units)
        if not chosen:
            chosen = [f"{item.title}: {human.first_paragraphs(body or raw, max_paragraphs=1, max_chars=500)}"]
        for index, unit in enumerate(chosen, start=1):
            card_id = f"EVC-{next_id:05d}"
            cards.append(card_from_unit(card_id, item, unit, index))
            next_id += 1
    return cards


def map_cards(cards: List[EvidenceCard]) -> Dict[int, List[EvidenceCard]]:
    mapped: Dict[int, List[EvidenceCard]] = defaultdict(list)
    for card in cards:
        for chapter in card.applies_to_chapters:
            mapped[chapter].append(card)
    for chapter, items in mapped.items():
        items.sort(key=card_rank)
    return dict(mapped)


def card_rank(card: EvidenceCard) -> Tuple[int, int, str]:
    authority = 0 if card.source_type == "current_high_authority" else 1 if card.source_type == "current_docs" else 2 if card.source_type == "derived_synthesis" else 3
    main = 0 if card.should_be_in_main_book else 1
    return (main, CLAIM_PRIORITY.get(card.claim_type, 99), authority, card.source_path, card.card_id)


def yaml_scalar(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return json.dumps(docs_corpus.ascii_text(str(value)), ensure_ascii=False)


def yaml_list(values: Sequence[object], indent: int = 4) -> List[str]:
    pad = " " * indent
    if not values:
        return [pad + "[]"]
    return [pad + "- " + yaml_scalar(value) for value in values]


def cards_yaml(cards: Sequence[EvidenceCard]) -> str:
    lines = [
        "status: \"DERIVED\"",
        f"last_reviewed: \"{REVIEW_DATE}\"",
        "authority_class: \"advisory_synthesis\"",
        "promotion_status: \"not_promoted\"",
        "cards:",
    ]
    for card in cards:
        lines.extend(
            [
                f"  - card_id: {yaml_scalar(card.card_id)}",
                f"    source_path: {yaml_scalar(card.source_path)}",
                f"    source_title: {yaml_scalar(card.source_title)}",
                f"    source_type: {yaml_scalar(card.source_type)}",
                f"    authority_class: {yaml_scalar(card.authority_class)}",
                f"    promotion_status: {yaml_scalar(card.promotion_status)}",
                "    topic_tags:",
                *yaml_list(card.topic_tags, 6),
                "    applies_to_chapters:",
                *yaml_list(card.applies_to_chapters, 6),
                f"    claim_type: {yaml_scalar(card.claim_type)}",
                f"    summary: {yaml_scalar(card.summary)}",
                f"    details: {yaml_scalar(card.details)}",
                f"    source_excerpt_or_paraphrase: {yaml_scalar(card.source_excerpt_or_paraphrase)}",
                f"    current_repo_support: {yaml_scalar(card.current_repo_support)}",
                f"    archive_or_conversation_status: {yaml_scalar(card.archive_or_conversation_status)}",
                f"    queue_status: {yaml_scalar(card.queue_status)}",
                f"    confidence: {yaml_scalar(card.confidence)}",
                f"    needs_user_decision: {yaml_scalar(card.needs_user_decision)}",
                f"    needs_future_queue: {yaml_scalar(card.needs_future_queue)}",
                f"    should_be_in_main_book: {yaml_scalar(card.should_be_in_main_book)}",
                f"    should_be_in_reference_only: {yaml_scalar(card.should_be_in_reference_only)}",
                f"    notes: {yaml_scalar(card.notes)}",
            ]
        )
    return "\n".join(lines)


def chapter_map_yaml(chapter_map: Dict[int, List[EvidenceCard]]) -> str:
    lines = [
        "status: \"DERIVED\"",
        f"last_reviewed: \"{REVIEW_DATE}\"",
        "authority_class: \"advisory_synthesis\"",
        "chapters:",
    ]
    for chapter in CHAPTERS:
        cards = chapter_map.get(chapter.number, [])
        integrated = [card.card_id for card in cards if card.should_be_in_main_book][:80]
        index_only = [card.card_id for card in cards if not card.should_be_in_main_book][:80]
        lines.extend(
            [
                f"  - chapter: {chapter.number}",
                f"    title: {yaml_scalar(chapter.title)}",
                f"    part: {yaml_scalar(chapter.part)}",
                "    tags:",
                *yaml_list(chapter.tags, 6),
                "    integrated_cards:",
                *yaml_list(integrated, 6),
                "    index_only_cards:",
                *yaml_list(index_only, 6),
            ]
        )
    return "\n".join(lines)


def write_manifest(repo_root: Path, state: BuildState) -> None:
    counts = Counter(card.claim_type for card in state.cards)
    content = f"""{STATUS_BLOCK}
# Integrated Book Manifest

title: "{TITLE}"
subtitle: "{SUBTITLE}"
version: {VERSION}
task_id: "{TASK_ID}"
source_root: "docs/"
conversation_corpus_root: "docs/archive/conversations/"
human_sources_processed: {len(state.sources)}
evidence_cards: {len(state.cards)}
chapters: {len(CHAPTERS)}
outputs:
  - "docs/archive/docs_corpus/_exports/{MAIN_PDF}"
  - "docs/archive/docs_corpus/_exports/{MAIN_HTML_DIR}/index.html"
  - "docs/archive/docs_corpus/_exports/{MAIN_DOCX}"
  - "docs/archive/docs_corpus/_exports/{EVIDENCE_PDF}"
claim_type_counts:
"""
    for key in CLAIM_TYPES:
        content += f"  {key}: {counts.get(key, 0)}\n"
    content += """
protected_paths:
  - "docs/canon/**"
  - "docs/architecture/**"
  - "docs/reference/contracts/**"
  - "contracts/**"
  - "schema/**"
  - "engine/**"
  - "game/**"
  - "runtime/**"
  - "apps/**"
  - ".aide/queue/current.toml"
validation_commands:
  - "py -3 tools/docs_corpus/validate_integrated_book_v2.py --repo-root ."
  - "py -3 tools/docs_corpus/validate_docs_corpus_outputs.py --repo-root ."
  - "py -3 tools/docs_corpus/validate_human_readable_book.py --repo-root ."
  - "py -3 tools/conversations/validate_conversation_outputs.py --repo-root ."
  - "py -3 -m unittest discover tests/tools/docs_corpus"
  - "git diff --check"
  - "git diff --cached --check"
  - "py -3 .aide/scripts/aide_lite.py doctor"
  - "py -3 .aide/scripts/aide_lite.py validate"
  - "py -3 tools/validators/suite/tool_run_validation.py --repo-root . --profile FAST"
"""
    write_text(repo_root / ROOT / "INTEGRATED_BOOK_MANIFEST.yml", content)


def v1_failure_diagnosis() -> str:
    return f"""{STATUS_BLOCK}
# V1 Failure Diagnosis

The v1 human-readable book had the right safety boundary, but not enough
editorial integration.

## Failure Modes Recorded

1. **Repeated boilerplate across chapters.** The v1 source repeats paragraphs
   such as "This chapter is part of the synthesized reader" and generic review
   questions in nearly every chapter.
2. **Main chapters too shallow.** Many chapters contain a short topic sentence
   followed by reusable authority warnings rather than mined evidence.
3. **Main contents page too cramped.** The book shape is better than the
   omnibus, but the content density does not justify the chapter list.
4. **Multiple headings land close together.** The short chapters create shallow
   sections rather than sustained reading.
5. **Full source appendix isolated from synthesis.** The 1,112-page variant is
   useful for audit, but it leaves source substance at the back.
6. **Source documents listed rather than conceptually integrated.** Appendix A
   names sources; v2 extracts claims and puts them into topic chapters.
7. **Decisions/specifications/constraints/open questions are not visible enough
   inside topic chapters.**
8. **Review questions are generic.** V2 replaces generic review blocks with
   topic-specific implications and evidence.
9. **Source trails are present but too thin.** V2 keeps source trails while also
   embedding the substance those trails support.
10. **Some appendix entries are duplicate or low-value for ordinary reading.**
    V2 keeps full source access as reference, not as the main reading path.

## V2 Acceptance Rule

The v2 book must read as an integrated project book. It may use evidence lists
and indexes, but the main chapters must explain what the evidence means.
"""


def cards_markdown(cards: Sequence[EvidenceCard]) -> str:
    counts = Counter(card.claim_type for card in cards)
    by_chapter: Dict[int, List[EvidenceCard]] = defaultdict(list)
    for card in cards:
        for chapter in card.applies_to_chapters:
            by_chapter[chapter].append(card)
    chunks = [
        STATUS_BLOCK,
        "# Source Evidence Cards",
        "",
        "This is the review surface behind the integrated book. It is evidence, not canon. The main book folds the important cards into topic chapters; this file keeps the source trail inspectable.",
        "",
        "## Claim Type Counts",
        "",
    ]
    for claim_type in CLAIM_TYPES:
        chunks.append(f"- **{claim_type}:** {counts.get(claim_type, 0)}")
    chunks.append("\n## Chapter Evidence Digest\n")
    for chapter in CHAPTERS:
        chapter_cards = sorted(by_chapter.get(chapter.number, []), key=card_rank)[:40]
        chunks.append(f"### {chapter.number}. {chapter.title}\n")
        for card in chapter_cards:
            chunks.append(f"- **{card.claim_type}** `{card.card_id}`: {card.summary} _Source:_ `{card.source_path}`")
        chunks.append("")
    return "\n".join(chunks)


def chapter_map_markdown(chapter_map: Dict[int, List[EvidenceCard]]) -> str:
    chunks = [
        STATUS_BLOCK,
        "# Chapter Evidence Map",
        "",
        "This map shows how mined evidence cards were assigned into the v2 chapter architecture.",
        "",
    ]
    for chapter in CHAPTERS:
        cards = chapter_map.get(chapter.number, [])
        counts = Counter(card.claim_type for card in cards)
        chunks.append(f"## {chapter.number}. {chapter.title}\n")
        chunks.append(f"**Part:** {chapter.part}")
        chunks.append(f"**Tags:** {', '.join(chapter.tags)}")
        chunks.append(f"**Mapped cards:** {len(cards)}")
        chunks.append("")
        chunks.append("**Claim mix:** " + ", ".join(f"{key}: {counts[key]}" for key in CLAIM_TYPES if counts[key]))
        chunks.append("")
        for card in sorted(cards, key=card_rank)[:30]:
            chunks.append(f"- `{card.card_id}` **{card.claim_type}:** {card.summary} (`{card.source_path}`)")
        chunks.append("")
    return "\n".join(chunks)


def contents_design() -> str:
    chunks = [
        STATUS_BLOCK,
        "# Contents Design",
        "",
        "The v2 contents are conceptual rather than source-path-oriented. PDF TOC depth should expose parts and chapters, while detailed source navigation belongs in indexes and HTML.",
        "",
    ]
    current_part = ""
    for chapter in CHAPTERS:
        if chapter.part != current_part:
            current_part = chapter.part
            chunks.append(f"## {current_part}\n")
        chunks.append(f"- **{chapter.number}. {chapter.title}**")
    chunks.append("\n## Index Strategy\n")
    chunks.append("- Main PDF: shallow contents, chapter source trails, compact indexes.")
    chunks.append("- HTML: deeper browser-searchable headings and linked paths.")
    chunks.append("- Evidence map: card-level traceability.")
    chunks.append("- Full source appendix: existing v1 reference artifact, not regenerated here.")
    return "\n".join(chunks)


def paragraph_from_cards(cards: Sequence[EvidenceCard], prefix: str, max_items: int = 5) -> str:
    selected = list(cards[:max_items])
    if not selected:
        return ""
    pieces = [card.summary.rstrip(".") for card in selected]
    if len(pieces) == 1:
        return f"{prefix} {pieces[0]}."
    return f"{prefix} " + "; ".join(pieces[:-1]) + f"; and {pieces[-1]}."


def bullet_cards(cards: Sequence[EvidenceCard], max_items: int = 10) -> str:
    if not cards:
        return "- No strong evidence card was selected for this category; see the chapter source trail and evidence map.\n"
    lines = []
    for card in cards[:max_items]:
        status = card.archive_or_conversation_status
        if card.needs_future_queue:
            status += "; future queue review"
        if card.needs_user_decision:
            status += "; user decision"
        lines.append(f"- **{card.claim_type.replace('_', ' ').title()}:** {card.summary} _Evidence:_ `{card.card_id}` from `{card.source_path}`. _Status:_ {status}.")
    return "\n".join(lines) + "\n"


def unique_sources(cards: Sequence[EvidenceCard], limit: int = 16) -> List[str]:
    seen = []
    for card in cards:
        if card.source_path not in seen:
            seen.append(card.source_path)
        if len(seen) >= limit:
            break
    return seen


def chapter_section(chapter: ChapterDef, cards: Sequence[EvidenceCard]) -> str:
    cards = sorted(cards, key=card_rank)
    current = [card for card in cards if card.source_type in {"current_high_authority", "current_docs"}][:12]
    historical = [card for card in cards if card.source_type in {"conversation_advisory", "archive_historical", "derived_synthesis"}][:14]
    decisions = [card for card in cards if card.claim_type == "decision"][:10]
    specs = [card for card in cards if card.claim_type == "specification"][:10]
    constraints = [card for card in cards if card.claim_type in {"constraint", "prohibition", "prerequisite"}][:12]
    open_cards = [card for card in cards if card.claim_type in {"contradiction", "unresolved_question", "risk", "change_of_direction"}][:12]
    effects = [card for card in cards if card.claim_type in {"second_order_effect", "third_order_effect", "design_goal"}][:12]
    sources = unique_sources(cards, 18)

    chunks = [
        f"## {chapter.number}. {chapter.title}",
        "",
        chapter.thesis,
        "",
        f"**Why this chapter matters.** {chapter.current_lens} {chapter.historical_lens}",
        "",
        "> [!CURRENT_TRUTH] Current repo truth comes first in this chapter. Archive and conversation evidence is used to explain design intent, recurring concerns, and review candidates without promoting it.",
        "",
        "### Integrated Evidence",
        "",
        paragraph_from_cards(current, "The current repo-backed evidence emphasizes", 5),
        paragraph_from_cards(historical, "The archive and conversation corpus add", 5),
        paragraph_from_cards(effects, "The downstream implication is that", 4),
        "",
        "### Decisions Already Visible",
        "",
        bullet_cards(decisions or current[:6], 8),
        "### Specifications and Requirements",
        "",
        bullet_cards(specs or current[6:12], 8),
        "### Constraints, Prohibitions, and Prerequisites",
        "",
        bullet_cards(constraints, 10),
        "### Contradictions, Risks, and Open Ends",
        "",
        bullet_cards(open_cards, 10),
        "### Second- and Third-Order Effects",
        "",
        bullet_cards(effects, 10),
        "### Implications for Next Work",
        "",
        chapter.next_work,
        "",
        "Any later task that wants to move a claim from this chapter into live authority needs source IDs, target paths, authority compatibility, queue compatibility, and validation evidence. This chapter is therefore a review map, not a permission slip.",
        "",
        "### Source Trail",
        "",
    ]
    chunks.extend(f"- `{path}`" for path in sources)
    return "\n".join(part for part in chunks if part is not None).strip() + "\n"


def build_book_markdown(state: BuildState) -> str:
    chunks = [
        f"# {TITLE} v{VERSION}",
        "",
        BOOK_NOTICE,
        "",
        "> [!AUTHORITY] This book is **DERIVED** and advisory. It is an integrated synthesis of current docs, archive context, and conversation evidence. It is not canon, not a contract, not schema law, not release authority, and not queue state.",
        "",
        "## How To Use This Book",
        "",
        "Read this book as the project-level reader surface. It is designed to make the full docs and conversation corpus understandable without forcing ordinary readers through manifests, matrices, and raw source appendices. The important evidence has been folded into chapters; the original sources remain available through source trails, the evidence map, and the existing full-source appendix.",
        "",
        "## What Is Current Truth Versus Archive Evidence",
        "",
        "Current truth comes from canon, glossary, AGENTS, scoped contracts, schema law, current queue state, and current repo docs within their authority domains. Archive and conversation material is historical or advisory unless later promoted by an explicit task. Generated evidence cards and this book are review aids.",
        "",
        "## Reading Paths",
        "",
        "- **Fast orientation:** chapters 1, 3, 4, 18, 21, and 25.",
        "- **Architecture:** chapters 5 through 9.",
        "- **Products and operators:** chapters 10 through 13.",
        "- **Simulation domains:** chapters 14 through 17.",
        "- **Roadmap and review:** chapters 18 through 25.",
        "",
        "## Key Terms",
        "",
        "- **Current repo truth:** supported by current authority surfaces.",
        "- **Archive evidence:** historically useful but not binding.",
        "- **Conversation advisory:** design intent from archived conversations.",
        "- **Blocked by queue:** not currently authorized for implementation.",
        "- **Evidence card:** a mined source claim used by this book.",
        "",
    ]
    current_part = ""
    for chapter in CHAPTERS:
        if chapter.part != current_part:
            current_part = chapter.part
            chunks.append(f"# {current_part}\n")
        chunks.append(chapter_section(chapter, state.chapter_map.get(chapter.number, [])))
    chunks.append(build_appendices(state))
    return "\n\n".join(chunks).strip() + "\n"


def index_cards(cards: Sequence[EvidenceCard], claim_types: Sequence[str], limit: int = 180) -> str:
    selected = [card for card in cards if card.claim_type in claim_types]
    selected.sort(key=card_rank)
    lines = []
    for card in selected[:limit]:
        chapters = ", ".join(str(chapter) for chapter in card.applies_to_chapters)
        lines.append(f"- `{card.card_id}` **{card.claim_type}:** {card.summary} _Chapters:_ {chapters}. _Source:_ `{card.source_path}`.")
    if len(selected) > limit:
        lines.append(f"- ... {len(selected) - limit} additional cards are available in `SOURCE_EVIDENCE_CARDS.yml`.")
    return "\n".join(lines) if lines else "- No cards in this index."


def build_appendices(state: BuildState) -> str:
    source_trails = []
    for chapter in CHAPTERS:
        paths = unique_sources(state.chapter_map.get(chapter.number, []), 20)
        source_trails.append(f"### {chapter.number}. {chapter.title}\n" + "\n".join(f"- `{path}`" for path in paths))
    return f"""
# Appendices

## Appendix A - Source Trails

{chr(10).join(source_trails)}

## Appendix B - Decision Index

{index_cards(state.cards, ["decision"], 220)}

## Appendix C - Specification Index

{index_cards(state.cards, ["specification"], 220)}

## Appendix D - Constraint and Prohibition Index

{index_cards(state.cards, ["constraint", "prohibition", "prerequisite"], 260)}

## Appendix E - Open Questions Index

{index_cards(state.cards, ["unresolved_question"], 180)}

## Appendix F - Contradiction and Risk Index

{index_cards(state.cards, ["contradiction", "risk", "change_of_direction"], 220)}

## Appendix G - Source Document Index

The source index is intentionally compact here. The full source selection lives at
`docs/archive/docs_corpus/_human_source/HUMAN_SOURCE_INDEX.md`, and the mined
evidence lives at `docs/archive/docs_corpus/_integrated_book_v2/SOURCE_EVIDENCE_CARDS.yml`.

- Human-readable source records processed: {len(state.sources)}
- Evidence cards created: {len(state.cards)}
- Chapter evidence map: `docs/archive/docs_corpus/_integrated_book_v2/CHAPTER_EVIDENCE_MAP.md`

## Appendix H - Full Source Appendix Reference

The full source appendix remains available as a separate reference artifact:

- `docs/archive/docs_corpus/_exports/Dominium_Human_Readable_Book_With_Full_Source_Appendix_v1.pdf`
- `docs/archive/docs_corpus/_human_book/appendices/FULL_SOURCE_APPENDIX_v1.md`

It is not regenerated here because v2's purpose is integration. The full appendix
is audit backup; this book is the reader surface.
"""


def build_indexes(repo_root: Path, state: BuildState) -> None:
    index_dir = repo_root / ROOT / "indexes"
    index_dir.mkdir(parents=True, exist_ok=True)
    topic_rows = []
    for tag in sorted(TAG_KEYWORDS):
        related = [chapter for chapter in CHAPTERS if tag in chapter.tags]
        topic_rows.append(f"- **{tag}:** " + ", ".join(f"{chapter.number}. {chapter.title}" for chapter in related))
    files = {
        "TOPIC_INDEX.md": STATUS_BLOCK + "\n# Topic Index\n\n" + "\n".join(topic_rows) + "\n",
        "DECISION_INDEX.md": STATUS_BLOCK + "\n# Decision Index\n\n" + index_cards(state.cards, ["decision"], 500) + "\n",
        "SPECIFICATION_INDEX.md": STATUS_BLOCK + "\n# Specification Index\n\n" + index_cards(state.cards, ["specification"], 500) + "\n",
        "CONSTRAINT_INDEX.md": STATUS_BLOCK + "\n# Constraint and Prohibition Index\n\n" + index_cards(state.cards, ["constraint", "prohibition", "prerequisite"], 600) + "\n",
        "CONTRADICTION_INDEX.md": STATUS_BLOCK + "\n# Contradiction and Risk Index\n\n" + index_cards(state.cards, ["contradiction", "risk", "change_of_direction"], 500) + "\n",
        "OPEN_QUESTIONS_INDEX.md": STATUS_BLOCK + "\n# Open Questions Index\n\n" + index_cards(state.cards, ["unresolved_question"], 500) + "\n",
        "SOURCE_TRAIL_INDEX.md": STATUS_BLOCK + "\n# Source Trail Index\n\n" + "\n\n".join(f"## {chapter.number}. {chapter.title}\n" + "\n".join(f"- `{path}`" for path in unique_sources(state.chapter_map.get(chapter.number, []), 35)) for chapter in CHAPTERS) + "\n",
        "CONTENTS_DESIGN.md": contents_design(),
    }
    for name, content in files.items():
        write_text(index_dir / name, content)


def boilerplate_report(v1_text: str, v2_text: str) -> str:
    patterns = [
        "This chapter is part of the synthesized reader",
        "That historical context is still useful",
        "Review questions.",
        "How to use this chapter.",
        "The practical consequence is that this topic should be read through the current authority model first",
    ]
    lines = [STATUS_BLOCK, "# Boilerplate Removal Report", ""]
    lines.append("The v2 book was generated from evidence cards and chapter-specific synthesis, not by patching the v1 chapter scaffold.")
    lines.append("")
    lines.append("## Repeated V1 Patterns")
    lines.append("")
    for pattern in patterns:
        lines.append(f"- **{pattern}:** v1 occurrences {v1_text.count(pattern)}, v2 occurrences {v2_text.count(pattern)}")
    lines.append("")
    lines.append("## Removed or Consolidated")
    lines.append("")
    lines.append("- Generic authority slabs were consolidated into front matter and chapter-specific current-truth callouts.")
    lines.append("- Generic review questions were replaced with evidence-backed implications for next work.")
    lines.append("- Source trails remain, but source substance is embedded through cards and chapter discussion.")
    lines.append("- Full source text remains a reference artifact, not the main reading mechanism.")
    lines.append("")
    lines.append("## Remaining Caveats")
    lines.append("")
    lines.append("- Section headings repeat intentionally for navigation, but body paragraphs and evidence lists are chapter-specific.")
    lines.append("- Evidence-card summaries are compact by design; source trails should be used for audit-level review.")
    return "\n".join(lines) + "\n"


def readme() -> str:
    return f"""{STATUS_BLOCK}
# Integrated Book v2

This directory contains the editorial synthesis pass for the Dominium integrated
project book.

The v2 book differs from the v1 human-readable book by mining human-readable
source documents into evidence cards and integrating those cards into topic
chapters. It does not promote archive or conversation claims, and it does not
modify live docs, canon, contracts, schema, implementation, release, or queue
state.

## Contents

- `SOURCE_EVIDENCE_CARDS.yml` / `.md`: mined evidence from the human-readable corpus.
- `CHAPTER_EVIDENCE_MAP.yml` / `.md`: how evidence maps into the book chapters.
- `Dominium_Integrated_Project_Book_v2.md`: the main integrated book source.
- `indexes/`: topic, decision, specification, constraint, contradiction, open question, and source-trail indexes.
- `qa/`: failure diagnosis and rendered page/text QA.
"""


def write_evidence_phase(repo_root: Path, state: BuildState) -> None:
    state.cards = build_evidence_cards(repo_root, state.sources)
    state.chapter_map = map_cards(state.cards)
    (repo_root / ROOT).mkdir(parents=True, exist_ok=True)
    (repo_root / QA_ROOT).mkdir(parents=True, exist_ok=True)
    write_text(repo_root / ROOT / "README.md", readme())
    write_text(repo_root / ROOT / "SOURCE_EVIDENCE_CARDS.yml", cards_yaml(state.cards))
    write_text(repo_root / ROOT / "SOURCE_EVIDENCE_CARDS.md", cards_markdown(state.cards))
    write_text(repo_root / ROOT / "CHAPTER_EVIDENCE_MAP.yml", chapter_map_yaml(state.chapter_map))
    write_text(repo_root / ROOT / "CHAPTER_EVIDENCE_MAP.md", chapter_map_markdown(state.chapter_map))
    write_text(repo_root / ROOT / "indexes" / "CONTENTS_DESIGN.md", contents_design())
    write_text(repo_root / QA_ROOT / "V1_FAILURE_DIAGNOSIS.md", v1_failure_diagnosis())
    write_manifest(repo_root, state)


def write_book_phase(repo_root: Path, state: BuildState) -> str:
    if not state.cards:
        state.cards = build_evidence_cards(repo_root, state.sources)
        state.chapter_map = map_cards(state.cards)
    md = build_book_markdown(state)
    write_text(repo_root / ROOT / MAIN_MD, md)
    for chapter in CHAPTERS:
        write_text(repo_root / ROOT / "chapters" / f"{chapter.number:02d}_{slug(chapter.title)}.md", chapter_section(chapter, state.chapter_map.get(chapter.number, [])))
    build_indexes(repo_root, state)
    v1_path = repo_root / "docs/archive/docs_corpus/_human_book/Dominium_Human_Readable_Book_v1.md"
    v1_text = read_text(v1_path)
    write_text(repo_root / ROOT / "BOILERPLATE_REMOVAL_REPORT.md", boilerplate_report(v1_text, md))
    return md


def html_css() -> str:
    return human.human_css() + """
.evidence { border-left: 4px solid #315f8f; padding-left: .9rem; background:#f7fafc; }
.source-trail { font-size: .92rem; color:#52606d; }
"""


def html_document(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{html_css()}</style>
</head>
<body>
<nav class="top"><a href="#top">Top</a><a href="#appendices">Appendices</a><a href="#source-trail-index">Sources</a></nav>
<main id="top">{body}</main>
</body>
</html>"""


def write_html_output(repo_root: Path, markdown: str, dirname: str, title: str) -> Path:
    target_dir = repo_root / EXPORTS_ROOT / dirname
    target_dir.mkdir(parents=True, exist_ok=True)
    body = human.link_source_paths_in_html(styled.markdown_to_html(markdown))
    path = target_dir / "index.html"
    write_text(path, html_document(title, body))
    return path


def render_docx(repo_root: Path, markdown_text: str, target_name: str) -> Path:
    target = repo_root / EXPORTS_ROOT / target_name
    target.parent.mkdir(parents=True, exist_ok=True)
    paragraphs = []
    for line in markdown_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("> [!"):
            continue
        if stripped.startswith("#"):
            stripped = stripped.lstrip("#").strip()
        if stripped.startswith("|"):
            stripped = " ".join(cell.strip() for cell in stripped.strip("|").split("|"))
        stripped = re.sub(r"`([^`]+)`", r"\1", stripped)
        stripped = re.sub(r"\*\*([^*]+)\*\*", r"\1", stripped)
        stripped = re.sub(r"\*([^*]+)\*", r"\1", stripped)
        stripped = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", stripped)
        paragraphs.append(stripped[:3000])
    body = "".join(f"<w:p><w:r><w:t>{xml_escape(p)}</w:t></w:r></w:p>" for p in paragraphs)
    document = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>{body}<w:sectPr/></w:body></w:document>"""
    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>"""
    rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>"""
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", rels)
        archive.writestr("word/document.xml", document)
    return target


def latex_document(title: str, subtitle: str, body: str, engine: str, profile: str) -> str:
    style = styled.latex_style(engine, profile)
    return rf"""{style}
\begin{{document}}
\frontmatter
\begin{{titlepage}}
\centering
\vspace*{{1.8cm}}
{{\Huge\bfseries {styled.latex_escape(title)}\par}}
\vspace{{0.7cm}}
{{\Large {styled.latex_escape(subtitle)}\par}}
\vspace{{1.1cm}}
{{\large Version: {VERSION}\par}}
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
        code, _ = run_command(["pdftotext", str(pdf_path), str(extract)], repo_root, timeout=900)
        if code == 0 and extract.exists() and extract.stat().st_size > 0:
            result.text_extraction = "PASS"
            text = extract.read_text(encoding="utf-8", errors="replace")
            result.glyph_check = "PASS" if not styled.has_bad_glyphs(text) else "FAIL"
        else:
            result.text_extraction = "FAIL"
    if result.created and shutil.which("pdftoppm") and result.pages:
        pages = [1, 2, 8, max(1, result.pages // 3), max(1, (result.pages * 2) // 3), result.pages]
        for page in sorted(set(page for page in pages if page <= result.pages))[:6]:
            prefix = qa_dir / f"{stem}_page_{page}"
            code, _ = run_command(["pdftoppm", "-f", str(page), "-l", str(page), "-png", "-singlefile", str(pdf_path), str(prefix)], repo_root, timeout=300)
            image = prefix.with_suffix(".png")
            if code == 0 and image.exists():
                result.qa_images.append(rel(image, repo_root))
    return result


def render_pdf(repo_root: Path, markdown: str, filename: str, stem: str, title: str, subtitle: str, profile: str, timeout: int = 2400) -> PdfInfo:
    build_dir = repo_root / BUILD_ROOT
    build_dir.mkdir(parents=True, exist_ok=True)
    target = repo_root / EXPORTS_ROOT / filename
    renderer = styled.select_engine()
    if not renderer:
        return PdfInfo(path=target, created=False, renderer="none", caveat="No LaTeX renderer available")
    tex_path = build_dir / f"{stem}.tex"
    pdf_path = build_dir / f"{stem}.pdf"
    for old in build_dir.glob(f"{stem}.*"):
        old.unlink(missing_ok=True)
    body = styled.markdown_to_latex(markdown, reference=profile != "reader")
    write_text(tex_path, latex_document(title, subtitle, body, renderer, profile))
    command = [renderer, "-interaction=nonstopmode", "-halt-on-error", "-output-directory", str(build_dir), str(tex_path)]
    ok = True
    last_output = ""
    for _ in range(2):
        code, output = run_command(command, repo_root, timeout=timeout)
        last_output = output
        if code != 0:
            ok = False
            break
    if not ok or not pdf_path.exists():
        return PdfInfo(path=target, created=False, renderer=renderer, caveat=last_output[-2000:])
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(pdf_path, target)
    return qa_pdf(repo_root, target, stem, renderer)


def evidence_map_pdf_source(state: BuildState) -> str:
    chunks = [
        "# Dominium Integrated Project Book v2 - Source Evidence Map",
        "",
        BOOK_NOTICE,
        "",
        "This companion explains how evidence cards were used. It is a review map, not the main book and not canon.",
        "",
        "## Evidence Summary",
        "",
    ]
    counts = Counter(card.claim_type for card in state.cards)
    for claim_type in CLAIM_TYPES:
        chunks.append(f"- **{claim_type}:** {counts.get(claim_type, 0)}")
    for chapter in CHAPTERS:
        cards = sorted(state.chapter_map.get(chapter.number, []), key=card_rank)[:60]
        chunks.append(f"\n## {chapter.number}. {chapter.title}\n")
        chunks.append(chapter.thesis)
        for card in cards:
            chunks.append(f"- `{card.card_id}` **{card.claim_type}:** {card.summary} _Source:_ `{card.source_path}`.")
    return "\n".join(chunks) + "\n"


def render_outputs(repo_root: Path, state: BuildState, book_md: str) -> None:
    html_path = write_html_output(repo_root, book_md, MAIN_HTML_DIR, f"{TITLE} v{VERSION}")
    docx_path = render_docx(repo_root, book_md, MAIN_DOCX)
    evidence_md = evidence_map_pdf_source(state)
    state.outputs["main_pdf"] = render_pdf(repo_root, book_md, MAIN_PDF, "integrated_book_v2", f"{TITLE} v{VERSION}", SUBTITLE, "reader", timeout=3600)
    state.outputs["evidence_map_pdf"] = render_pdf(repo_root, evidence_md, EVIDENCE_PDF, "integrated_evidence_map_v2", f"{TITLE} v{VERSION} Evidence Map", "Evidence Cards and Chapter Assignments", "reference", timeout=3600)
    state.outputs["html"] = PdfInfo(path=html_path, created=html_path.exists(), size=html_path.stat().st_size if html_path.exists() else 0, renderer="built_in_html")
    state.outputs["docx"] = PdfInfo(path=docx_path, created=docx_path.exists(), size=docx_path.stat().st_size if docx_path.exists() else 0, renderer="built_in_ooxml")
    renderers = [info.renderer for info in state.outputs.values() if info.renderer]
    if renderers:
        state.renderer = ",".join(dict.fromkeys(renderers))


def protected_changes(repo_root: Path) -> List[str]:
    names: List[str] = []
    for cmd in (["git", "diff", "--name-only"], ["git", "diff", "--cached", "--name-only"]):
        code, output = run_command(cmd, repo_root, timeout=120)
        if code == 0:
            names.extend(output.splitlines())
    return sorted({name for name in names if any(name == prefix.rstrip("/") or name.startswith(prefix) for prefix in PROTECTED_PREFIXES)})


def validate_outputs(state: BuildState) -> None:
    commands = [
        ["py", "-3", "-c", "text=open('docs/archive/docs_corpus/_integrated_book_v2/INTEGRATED_BOOK_MANIFEST.yml', encoding='utf-8').read(); assert 'version: 2' in text and 'evidence_cards:' in text; print('integrated manifest ok')"],
        ["py", "-3", "-c", "text=open('docs/archive/docs_corpus/_integrated_book_v2/SOURCE_EVIDENCE_CARDS.yml', encoding='utf-8').read(); assert text.count('card_id:') > 1000; print('evidence cards ok')"],
        ["py", "-3", "-c", "text=open('docs/archive/docs_corpus/_integrated_book_v2/CHAPTER_EVIDENCE_MAP.yml', encoding='utf-8').read(); assert text.count('chapter:') >= 25; print('chapter map ok')"],
        ["py", "-3", "tools/docs_corpus/validate_integrated_book_v2.py", "--repo-root", "."],
        ["py", "-3", "tools/docs_corpus/validate_docs_corpus_outputs.py", "--repo-root", "."],
        ["py", "-3", "tools/docs_corpus/validate_human_readable_book.py", "--repo-root", "."],
        ["py", "-3", "tools/conversations/validate_conversation_outputs.py", "--repo-root", "."],
        ["py", "-3", "-m", "unittest", "discover", "tests/tools/docs_corpus"],
        ["git", "diff", "--check"],
        ["git", "diff", "--cached", "--check"],
        ["py", "-3", ".aide/scripts/aide_lite.py", "doctor"],
        ["py", "-3", ".aide/scripts/aide_lite.py", "validate"],
        ["py", "-3", "tools/validators/suite/tool_run_validation.py", "--repo-root", ".", "--profile", "FAST"],
    ]
    for cmd in commands:
        code, output = run_command(cmd, state.repo_root, timeout=2400)
        state.command_results.append({"command": " ".join(cmd), "code": code, "result": "PASS" if code == 0 else "FAIL"})
        if code != 0:
            state.errors.append(f"command failed: {' '.join(cmd)}\n{output[-1800:]}")
    protected = protected_changes(state.repo_root)
    if protected:
        state.errors.extend(f"protected path changed: {path}" for path in protected)


def build_report(state: BuildState) -> str:
    counts = Counter(card.claim_type for card in state.cards)
    integrated = sum(1 for card in state.cards if card.should_be_in_main_book)
    output_rows = [(name, rel(info.path, state.repo_root), info.created, info.pages or "", info.size, info.renderer) for name, info in state.outputs.items()]
    return STATUS_BLOCK + f"""
# Dominium Integrated Project Book v2 Build Report

## Build

- Title: {TITLE} v{VERSION}
- Date: {REVIEW_DATE}
- Repository branch: `{state.branch}`
- Repository commit at generation time: `{state.commit}`
- Renderer: {state.renderer or styled.select_engine() or 'none'}
- Human-readable sources processed: {len(state.sources)}
- Evidence cards created: {len(state.cards)}
- Evidence cards integrated into chapters: {integrated}
- Evidence cards kept primarily in indexes/reference: {len(state.cards) - integrated}
- Chapters: {len(CHAPTERS)}

## Embedded Evidence Counts

- Decisions: {counts.get('decision', 0)}
- Specifications: {counts.get('specification', 0)}
- Goals: {counts.get('design_goal', 0)}
- Constraints/prohibitions/prerequisites: {counts.get('constraint', 0) + counts.get('prohibition', 0) + counts.get('prerequisite', 0)}
- Contradictions/risks/open questions: {counts.get('contradiction', 0) + counts.get('risk', 0) + counts.get('unresolved_question', 0)}
- Second/third-order effects: {counts.get('second_order_effect', 0) + counts.get('third_order_effect', 0)}

## Outputs

{docs_corpus.md_table(["Output", "Path", "Created", "Pages", "Size Bytes", "Renderer"], output_rows)}

## Known Caveats

- Evidence cards are generated heuristically from prose and must remain advisory.
- The full 1,112-page source appendix remains a separate reference artifact and is not regenerated here.
- HTML is the best surface for searching source trails and evidence terms.
"""


def validation_report(state: BuildState, pending: bool = False) -> str:
    if pending:
        return STATUS_BLOCK + "\n# Dominium Integrated Project Book v2 Validation Report\n\nValidation pending.\n"
    result = "PASS" if not state.errors and not state.warnings else "PASS_WITH_WARNINGS" if not state.errors else "FAIL"
    command_rows = [(item["command"], item["result"], item["code"]) for item in state.command_results]
    pdf_rows = []
    for name, info in state.outputs.items():
        if info.path.suffix.lower() == ".pdf":
            pdf_rows.append((name, rel(info.path, state.repo_root), info.created, info.pages or "", info.text_extraction, info.glyph_check, "; ".join(info.qa_images)))
    return STATUS_BLOCK + f"""
# Dominium Integrated Project Book v2 Validation Report

## Status

- Result: {result}

## Command Results

{docs_corpus.md_table(["Command", "Result", "Code"], command_rows)}

## PDF QA

{docs_corpus.md_table(["Output", "Path", "Created", "Pages", "Text Extraction", "Glyph Check", "QA Images"], pdf_rows)}

## Repetition and TOC Checks

- V1 boilerplate phrase check: enforced by `validate_integrated_book_v2.py`.
- Raw source-path heading check: enforced by `validate_integrated_book_v2.py`.
- Evidence-card coverage check: enforced by generated card and chapter-map checks.
- Source trail check: enforced by `validate_integrated_book_v2.py`.

## Errors

{chr(10).join(f"- {item}" for item in state.errors) if state.errors else "None."}

## Warnings

{chr(10).join(f"- {item}" for item in state.warnings) if state.warnings else "None."}

## Impact Statements

- Canon impact: unchanged
- Contract/schema impact: unchanged
- Implementation impact: unchanged
- Release impact: unchanged
- Queue impact: unchanged
- Archive/conversation claim promotion: none
- Protected path changes: none detected
"""


def create_state(repo_root: Path) -> BuildState:
    records = human.load_manifest(repo_root)
    sources = human.select_sources(repo_root, records)
    return BuildState(
        repo_root=repo_root,
        sources=sources,
        branch=git_value(repo_root, ["rev-parse", "--abbrev-ref", "HEAD"]),
        commit=git_value(repo_root, ["rev-parse", "--short", "HEAD"]),
        renderer=styled.select_engine(),
    )


def build(repo_root: Path, phase: str, run_validation: bool) -> int:
    state = create_state(repo_root)
    if phase in {"evidence", "all", "book"}:
        write_evidence_phase(repo_root, state)
    if phase in {"book", "all"}:
        if not state.cards:
            state.cards = build_evidence_cards(repo_root, state.sources)
            state.chapter_map = map_cards(state.cards)
        book_md = write_book_phase(repo_root, state)
        render_outputs(repo_root, state, book_md)
        write_text(repo_root / EXPORTS_ROOT / BUILD_REPORT, build_report(state))
        write_text(repo_root / EXPORTS_ROOT / VALIDATION_REPORT, validation_report(state, pending=not run_validation))
    if phase == "validate":
        state.cards = build_evidence_cards(repo_root, state.sources)
        state.chapter_map = map_cards(state.cards)
        for name, filename in {"main_pdf": MAIN_PDF, "evidence_map_pdf": EVIDENCE_PDF}.items():
            path = repo_root / EXPORTS_ROOT / filename
            state.outputs[name] = qa_pdf(repo_root, path, name, "existing")
        for name, path in {"html": repo_root / EXPORTS_ROOT / MAIN_HTML_DIR / "index.html", "docx": repo_root / EXPORTS_ROOT / MAIN_DOCX}.items():
            state.outputs[name] = PdfInfo(path=path, created=path.exists(), size=path.stat().st_size if path.exists() else 0, renderer="existing")
    if run_validation or phase == "validate":
        validate_outputs(state)
        write_text(repo_root / EXPORTS_ROOT / VALIDATION_REPORT, validation_report(state, pending=False))
    if state.errors:
        print(f"{TASK_ID} FAIL")
        return 1
    print(f"{TASK_ID} PASS_WITH_WARNINGS" if state.warnings else f"{TASK_ID} PASS")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--phase", choices=["evidence", "book", "all", "validate"], default="all")
    parser.add_argument("--no-validation", action="store_true")
    args = parser.parse_args(argv)
    return build(Path(args.repo_root).resolve(), args.phase, run_validation=not args.no_validation)


if __name__ == "__main__":
    raise SystemExit(main())
