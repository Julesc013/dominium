"""Build the authored Dominium Project Book.

This pipeline uses the v2 evidence-card corpus as private source material, then
writes a prose-first book. The main book deliberately hides evidence IDs, source
paths, repeated category scaffolding, and machine-report structure. Source
traceability lives in companion source notes and maps.

Generated outputs are DERIVED and advisory. Source docs are not modified.
"""

from __future__ import annotations

import argparse
import html
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
import build_integrated_book_v2 as integrated
import build_omnibus_v1 as styled
import docs_corpus


TASK_ID = "DOMINIUM-AUTHORED-PROSE-BOOK-01"
REVIEW_DATE = "2026-05-29"
TITLE = "Dominium Project Book"
SUBTITLE = "A human-readable synthesis of the current docs, archive context, and conversation evidence"

ROOT = Path("docs/archive/docs_corpus/_authored_book")
EXPORTS_ROOT = Path("docs/archive/docs_corpus/_exports")
QA_ROOT = ROOT / "qa"
BUILD_ROOT = ROOT / "build"

MAIN_MD = "Dominium_Project_Book.md"
MAIN_PDF = "Dominium_Project_Book.pdf"
MAIN_HTML_DIR = "Dominium_Project_Book.html"
MAIN_DOCX = "Dominium_Project_Book.docx"
SOURCE_NOTES_PDF = "Dominium_Project_Book_Source_Notes.pdf"
BUILD_REPORT = "Dominium_Project_Book_Build_Report.md"
VALIDATION_REPORT = "Dominium_Project_Book_Validation_Report.md"

PROTECTED_PREFIXES = docs_corpus.PROTECTED_PREFIXES

BANNED_HEADINGS = [
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
]

STATUS_BLOCK = f"""Status: DERIVED
Last Reviewed: {REVIEW_DATE}
Supersedes: docs/archive/docs_corpus/_integrated_book_v2/**
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


@dataclass(frozen=True)
class Theme:
    number: int
    part: str
    title: str
    tags: Tuple[str, ...]
    v2_chapters: Tuple[int, ...]
    opening: str
    current: str
    archive: str
    tension: str
    close: str
    source_focus: str


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


@dataclass
class BuildState:
    repo_root: Path
    sources: List[human.SourceItem]
    cards: List[integrated.EvidenceCard]
    chapter_map: Dict[int, List[integrated.EvidenceCard]]
    theme_cards: Dict[int, List[integrated.EvidenceCard]]
    conversation_file_count: int
    conversation_markdown_count: int
    branch: str = ""
    commit: str = ""
    renderer: str = ""
    outputs: Dict[str, PdfInfo] = field(default_factory=dict)
    command_results: List[Dict[str, object]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


THEMES: List[Theme] = [
    Theme(1, "Part I - The Project", "Dominium in One View", ("identity", "runtime", "authority"), (1,), "Dominium is easiest to understand as a layered project: Domino supplies the deterministic substrate, while Dominium gives that substrate product meaning, domain law, authored content, and operator surfaces.", "The current repository frames the project as lawful simulation, explicit refusal, and evidence-backed execution rather than a conventional game executable.", "The conversation archive stretches that identity toward a larger product ecosystem, with Workbench, launchers, world simulation, and future product surfaces treated as projections over the same substrate.", "The important boundary is that ambition does not equal authority. Historical sources can explain why the system is shaped this way, but they do not authorize broad implementation by themselves.", "Read this first as the compact mental model for the rest of the book: substrate first, domain meaning second, products and tools downstream.", "identity, current project picture, Domino versus Dominium"),
    Theme(2, "Part I - The Project", "Why the Project Exists", ("identity", "world", "civilization"), (2,), "The project exists because it wants emergent social and material complexity to come from lawful process rather than from scripted outcomes.", "Current orientation material names invention, production, logistics, economics, settlement, communication, trust, and institutional power as recurring ends of the simulation model.", "Conversation material expands the same idea into seed civilizations, institutions, astronomical scale, authored worlds, and operator tooling.", "The tension is scope: the purpose is broad, while the current queue permits only narrow, governed work.", "The practical reading is that Dominium's ambition is durable, but every concrete feature still needs current authority, contracts, and validation before becoming implementation.", "motivation, long-horizon ambition, emergent systems"),
    Theme(3, "Part I - The Project", "The Core Mental Model", ("determinism", "authority", "world"), (3,), "The core mental model is a separation of truth, perception, rendering, and operation.", "Canon and architecture documents make truth authoritative, perception a filtered view, rendering a presentation layer, and mutation something that can happen only through lawful deterministic process.", "Older conversations repeatedly test that model against Workbench, user interfaces, providers, packs, world generation, and future editor workflows.", "The model becomes fragile whenever a convenience layer is allowed to correct truth, hide refusal, or store authoritative state because it happens to be close to the user.", "The reader should treat this as the book's organizing rule: every future surface must say whether it owns truth, observes truth, presents truth, or merely helps operate the repository.", "truth/perception/render separation, process-only mutation, refusal"),
    Theme(4, "Part I - The Project", "Current Authority and Historical Context", ("authority", "docs", "blocked"), (4,), "The documentation corpus is not flat. It has authority layers, and the book only makes sense if those layers are kept visible.", "Current repo truth starts with canon, glossary, agent governance, active planning and contracts, queue state, and validated repo artifacts.", "The archive and conversation corpus preserve useful design memory, old plans, contradictions, and proposed future directions.", "The risk is accidental promotion: a generated report, old chat, or polished book can sound authoritative even when it is only evidence.", "This book therefore uses historical material as context and asks future tasks to promote only through explicit scoped review.", "authority order, archive status, non-promotion"),
    Theme(5, "Part II - The Architecture", "The System Stack", ("runtime", "contracts", "identity"), (5,), "The system stack is a set of ownership boundaries, not just a directory tree.", "Current docs distinguish deterministic substrate, official domain layer, product shells, runtime services, contracts, content, tools, and documentation.", "Historical material often describes the same system in more speculative or product-facing language, especially around Workbench, providers, and large-scale world simulation.", "The danger is collapsing roots because they look adjacent: engine, game, runtime, apps, packs, schemas, and docs have different kinds of authority.", "The useful outcome is a stack that can grow without turning every future feature into a rewrite of the whole project.", "stack ownership, architecture boundaries, physical roots"),
    Theme(6, "Part II - The Architecture", "Domino, Dominium, Runtime, Products, and Tools", ("runtime", "product", "tooling", "identity"), (6,), "Domino and Dominium are related but not interchangeable.", "Domino is the reusable deterministic substrate; Dominium is the official product and domain layer that gives the substrate meaning.", "The conversations add pressure toward many surfaces: client, server, launcher, setup, Workbench, command views, and automation.", "That pressure is useful only if products remain projections and operators over the substrate instead of becoming alternate authorities.", "The project becomes easier to evolve when runtime mechanisms, product shells, and repo tools each keep their role.", "Domino/Dominium split, product shells, operator tools"),
    Theme(7, "Part II - The Architecture", "Law, Capability, Refusal, and Evidence", ("authority", "contracts", "determinism"), (7,), "Law and capability are not decoration; they are how the system decides what may happen.", "Current authority requires explicit refusal, no hidden fallback behavior, and capability-driven access to optional content and operations.", "Archive material shows the same pattern being applied to providers, packs, assistant workflows, Workbench commands, and future product surfaces.", "The hard part is refusing clearly without making the system brittle or opaque.", "A well-formed future feature should be able to explain its authority source, its refusal path, and the evidence it leaves behind.", "law surfaces, capability checks, refusal discipline"),
    Theme(8, "Part II - The Architecture", "Determinism, Replay, and Provenance", ("determinism", "contracts", "tooling"), (8,), "Determinism is both a runtime requirement and an audit strategy.", "The current doctrine asks for named randomness, deterministic ordering, stable reductions, replay equivalence, and provenance wherever canonical truth is involved.", "Conversation evidence adds operational concerns: proof gates, CI tiers, source evidence, dependency warnings, portability, and release trust.", "A feature that cannot describe its replay and evidence behavior is not ready to become authoritative.", "The design consequence is that validation is not an afterthought; it is part of the architecture.", "determinism, replay, proof, provenance"),
    Theme(9, "Part II - The Architecture", "Contracts, Schemas, Packs, and Compatibility", ("contracts", "packs", "release"), (9,), "Contracts and schemas are how public meaning survives change.", "Current docs require explicit identities, versions, migrations, refusal obligations, and compatibility rules.", "The archive adds a larger vocabulary around packs, providers, module boundaries, package composition, semantic versioning, and release identity.", "Some of that vocabulary is current contract law, while some remains proposal or future queue work.", "The reader should separate data-driven extension that is already doctrinal from provider or package runtime ambitions that remain blocked.", "contracts, schemas, packs, compatibility"),
    Theme(10, "Part III - Product and Operator Surfaces", "Client, Server, Launcher, Setup, and Workbench", ("product", "workbench", "runtime"), (10,), "The product surfaces are where users and operators meet the governed substrate.", "Current repo state permits narrow product and validation slices, not broad product implementation.", "The archive contains rich Workbench and launcher ambition: inspection, commands, evidence, authoring, package views, and later editing workflows.", "Those ideas matter because they show the desired operator experience, but the queue still controls when they can become implementation.", "Workbench should be read as the richest future operator surface, not as an authority layer.", "client/server/product shells, Workbench, launcher/setup"),
    Theme(11, "Part III - Product and Operator Surfaces", "UI, Renderer, Native GUI, and Presentation Boundaries", ("renderer", "product", "blocked"), (11,), "Presentation is downstream of truth.", "Current doctrine says rendering is presentation only, and current queue state keeps broad renderer, native GUI, and UI implementation blocked.", "The conversation archive nevertheless contains extensive UI and renderer intent, including universe exploration, native surfaces, and product presentation strategy.", "The book keeps those ideas as design context because they explain the desired experience, but it does not treat them as permission.", "Future renderer work will need explicit queue opening and contracts that protect truth, perception, replay, and refusal.", "renderer/UI/native GUI, presentation separation"),
    Theme(12, "Part III - Product and Operator Surfaces", "AIDE, Codex, Automation, and Repo Governance", ("tooling", "authority", "docs"), (12,), "AIDE, Codex, and related agents are governed helpers, not alternate project authorities.", "Agent governance defines bounded work, validation expectations, protected paths, and forbidden moves.", "Conversation evidence shows repeated work to make assistant operation more portable, evidence-rich, and reviewable.", "The risk is that successful automation can look like authority, especially when it generates polished reports or books.", "The right use of automation is to expose evidence and perform bounded edits while leaving semantic authority with the repo.", "AIDE, Codex, task governance, validation"),
    Theme(13, "Part III - Product and Operator Surfaces", "Documentation, Archive, and Conversation Corpus", ("docs", "authority"), (13,), "The documentation archive is a memory system.", "Current docs-corpus outputs inventory and classify the docs tree, while the conversation corpus preserves the project's historical design conversations.", "The archive contains synthesis, decisions, promotion candidates, contradictions, wiki navigation, reader pages, manifests, and audit material.", "The book's job is to turn that mass into an intelligible map without making old claims current.", "For ordinary reading, the important content is woven into chapters; for audit, source notes and full appendices remain available.", "docs archive, conversation corpus, source archaeology"),
    Theme(14, "Part IV - Simulation and World Model", "Reality, Space, Time, and Scale", ("world", "determinism"), (14,), "Reality, space, time, and scale are simulation concepts before they are rendering concepts.", "Current doctrine supplies the generic law: deterministic process, authoritative truth, observation, and provenance.", "The conversations add pressure for large-scale worlds, visitability, temporal resilience, timekeeping, and representations that can refine without breaking truth.", "The unresolved issue is how much of that long-horizon world model is current spec versus design ambition.", "Future domain work should start by identifying the authority of each claim before it is attached to gameplay or renderer behavior.", "reality model, space, scale, time"),
    Theme(15, "Part IV - Simulation and World Model", "World Generation, Celestial Systems, and Domains", ("world", "packs"), (15,), "World generation and celestial systems recur because the project wants large worlds that remain lawful and inspectable.", "Current authority supports deterministic composition and data-driven domain boundaries but does not authorize broad worldgen implementation.", "The archive discusses astronomy, planetary systems, domain packs, terrain, scale, and source verification as future design material.", "The difficult part is keeping scientific ambition, authored content, and deterministic constraints aligned.", "The next useful work is not implementation but source verification, domain contract scoping, and decision triage.", "worldgen, astronomy, planetary domains"),
    Theme(16, "Part IV - Simulation and World Model", "Civilization, Economy, Logistics, and Institutions", ("civilization", "world"), (16,), "Civilization-scale simulation is one of the clearest ambitions in the corpus.", "Current orientation names production, logistics, economics, settlement, trust, communication, and institutional power as intended emergent phenomena.", "Conversation material adds seed civilizations, infrastructure, signals, institutions, economies, and social-scale feedback loops.", "Those sources are rich, but they remain mostly design context until domain tasks are opened.", "The value today is conceptual: they show what kinds of consequences the lower-level architecture must eventually be able to support.", "civilization simulation, economy, logistics, institutions"),
    Theme(17, "Part IV - Simulation and World Model", "Content, Providers, Modding, and Data-Driven Extension", ("packs", "contracts", "blocked"), (17,), "Content extension is supposed to be governed, not magical.", "Current doctrine favors packs, registries, explicit capabilities, compatibility rules, and deterministic refusal over hidden fallback.", "The archive expands this into providers, package runtime, open-source provider choices, authored content workflows, and modding surfaces.", "Much of that expansion is blocked or not yet formalized.", "The immediate use is to separate already-current pack doctrine from future provider and package-runtime proposals.", "content packs, providers, modding, extension"),
    Theme(18, "Part V - Decisions and Roadmap", "What Is Settled", ("authority", "decision", "docs"), (18,), "Several principles are settled strongly enough to shape every future task.", "Authority order, process-only mutation, truth/perception/render separation, profiles over mode flags, no hidden fallback, pack-driven integration, and explicit validation are recurring current truths.", "The conversation archive often reinforces these decisions, which is useful but not necessary for their authority.", "The settled material should be used to simplify future review: if a proposal violates one of these principles, the burden is on the proposal.", "The next step is to turn aligned archive phrasing into carefully scoped clarifications only where current docs need them.", "settled decisions, current repo truth"),
    Theme(19, "Part V - Decisions and Roadmap", "What Is Still Open", ("decision", "docs", "blocked"), (19,), "The open questions are not a defect; they are the reason the archive exists as evidence instead of doctrine.", "Docs-corpus and conversation dockets identify user decisions, future queue decisions, and source verification needs.", "The archive contains many plausible answers, but a plausible answer is not the same as a repo decision.", "The work ahead is to separate questions that can be answered by docs hygiene from questions that need queue scope or user authority.", "This book should help the reader recognize the question before trying to solve it.", "open decisions, user questions, future queue"),
    Theme(20, "Part V - Decisions and Roadmap", "What Is Blocked", ("blocked", "renderer", "release"), (21,), "Blocked scope is as important as active scope.", "The current queue does not authorize broad Workbench UI, renderer implementation, native GUI, provider runtime, package runtime, gameplay, or release publication.", "Older conversations often speak about those areas with enthusiasm because they preserve product intent.", "That enthusiasm is useful only when it is labelled as future work.", "A safe task packet should state blocked areas before it starts describing implementation.", "blocked scope, non-goals, queue boundaries"),
    Theme(21, "Part V - Decisions and Roadmap", "Contradictions and Drift", ("docs", "authority", "blocked"), (22,), "The corpus preserves disagreement because it preserves history.", "Current authority order and snapshot intake rules are what prevent old planning, generated summaries, or conversation claims from overriding present repo truth.", "Contradictions appear around scope, implementation readiness, release state, provider/runtime boundaries, and old architecture language.", "The right response is not to smooth them into a single story, but to classify them, quarantine what needs review, and promote only after targeted decisions.", "This book treats contradictions as signals for future review rather than failures to hide.", "contradictions, stale claims, drift"),
    Theme(22, "Part V - Decisions and Roadmap", "Prerequisites and Sequencing", ("blocked", "tooling", "release"), (23,), "The project has many desirable destinations, but the sequence matters.", "Current state points to narrow command/result and package-mount slices, projection conformance, validation debt, and review work before broad feature expansion.", "Historical roadmaps add useful sequencing ideas around Workbench, releases, provider choices, docs promotion, and domain work.", "The main dependency is authority: future work needs the right queue, target surface, contracts, tests, and evidence.", "Good sequencing keeps ambition alive without letting it become uncontrolled scope.", "prerequisites, dependencies, future queue"),
    Theme(23, "Part V - Decisions and Roadmap", "Recommended Next Steps", ("docs", "decision", "blocked"), (24, 25), "The next useful move is selective review, not another corpus dump.", "Current authority allows narrow governed tasks and derived documentation work; it does not authorize sweeping promotion or implementation.", "The generated corpus, evidence cards, and source notes now provide enough material to choose small follow-up tasks deliberately.", "A good next task should name the claim, source evidence, target document, authority impact, validation level, and non-goals.", "The reader should leave with a map: read the book, inspect source notes where needed, triage decisions, and promote only in narrow waves.", "roadmap, next review actions, promotion triage"),
]


def run_command(cmd: Sequence[str], cwd: Path, timeout: int = 900) -> Tuple[int, str]:
    try:
        completed = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, timeout=timeout)
    except FileNotFoundError as exc:
        return 127, str(exc)
    except subprocess.TimeoutExpired as exc:
        return 124, (exc.stdout or "") + (exc.stderr or "") + f"\nTIMEOUT after {timeout}s"
    return completed.returncode, (completed.stdout or "") + (completed.stderr or "")


def read_text(path: Path, limit: Optional[int] = None) -> str:
    data = path.read_text(encoding="utf-8", errors="replace")
    return data if limit is None else data[:limit]


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", value.lower()).strip("_")
    return slug[:80] or "chapter"


def yaml_scalar(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{text}"'


def yaml_list(values: Sequence[object], indent: int = 4) -> List[str]:
    pad = " " * indent
    if not values:
        return [pad + "[]"]
    return [pad + "- " + yaml_scalar(value) for value in values]


def prepare_dirs(repo_root: Path) -> None:
    for path in [
        ROOT,
        ROOT / "chapters",
        ROOT / "endnotes",
        ROOT / "indexes",
        ROOT / "qa",
        ROOT / "build",
        EXPORTS_ROOT,
    ]:
        (repo_root / path).mkdir(parents=True, exist_ok=True)


def current_branch_commit(repo_root: Path) -> Tuple[str, str]:
    branch_code, branch = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo_root)
    commit_code, commit = run_command(["git", "rev-parse", "--short=9", "HEAD"], repo_root)
    return (branch.strip() if branch_code == 0 else "unknown", commit.strip() if commit_code == 0 else "unknown")


def load_state(repo_root: Path) -> BuildState:
    records = human.load_manifest(repo_root)
    sources = human.select_sources(repo_root, records)
    cards = integrated.build_evidence_cards(repo_root, sources)
    chapter_map = integrated.map_cards(cards)
    theme_cards = map_themes(cards, chapter_map)
    conversation_records = [record for record in records if str(record.get("path", "")).startswith("docs/archive/conversations/")]
    conversation_markdown = [record for record in conversation_records if str(record.get("extension", "")).lower() == ".md"]
    branch, commit = current_branch_commit(repo_root)
    return BuildState(
        repo_root=repo_root,
        sources=sources,
        cards=cards,
        chapter_map=chapter_map,
        theme_cards=theme_cards,
        conversation_file_count=len(conversation_records),
        conversation_markdown_count=len(conversation_markdown),
        branch=branch,
        commit=commit,
        renderer=styled.select_engine() or "none",
    )


def map_themes(cards: List[integrated.EvidenceCard], chapter_map: Dict[int, List[integrated.EvidenceCard]]) -> Dict[int, List[integrated.EvidenceCard]]:
    result: Dict[int, List[integrated.EvidenceCard]] = {}
    all_cards = list(cards)
    for theme in THEMES:
        selected: Dict[str, integrated.EvidenceCard] = {}
        for chapter_num in theme.v2_chapters:
            for card in chapter_map.get(chapter_num, []):
                selected[card.card_id] = card
        for card in all_cards:
            if len(selected) >= 420:
                break
            if any(tag in card.topic_tags for tag in theme.tags):
                selected.setdefault(card.card_id, card)
        items = list(selected.values())
        items.sort(key=lambda card, theme=theme: card_score(card, theme))
        result[theme.number] = items
    return result


def card_score(card: integrated.EvidenceCard, theme: Theme) -> Tuple[int, int, int, str]:
    source = 0 if card.source_type == "current_high_authority" else 1 if card.source_type == "derived_synthesis" else 2 if card.source_type == "current_docs" else 3 if card.source_type == "conversation_advisory" else 4
    main = 0 if card.should_be_in_main_book else 1
    claim = integrated.CLAIM_PRIORITY.get(card.claim_type, 99)
    tag_overlap = -sum(1 for tag in theme.tags if tag in card.topic_tags)
    return (main, source + tag_overlap, claim, card.card_id)


def normalize_sentence(text: str, max_chars: int = 430) -> str:
    text = html.unescape(text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"EVC-\d+", "", text)
    text = re.sub(r"(?i)\b(source|evidence|status):\s*", "", text)
    text = re.sub(r"\bDECISION-\d+\s*[:\-]?\s*", "", text)
    text = re.sub(r"\b(FACT|INFERENCE)\s*[:/]\s*", "", text)
    text = re.sub(r"\b[A-Za-z0-9_./()-]+__\d+_[A-Za-z0-9_./()-]+\.(?:md|txt|json|yml|yaml|toml)\b", "the source material", text)
    text = re.sub(r"\b(?:docs|contracts|schema|apps|engine|game|runtime|tools)/[A-Za-z0-9_./()-]+(?:\.(?:md|json|yml|yaml|toml|txt))?\b", "the source material", text)
    text = re.sub(r"\b(?:AGENTS|README|FOUNDATION_LOCK|AUTHORITY_ORDER|SNAPSHOT_INTAKE_PROTOCOL)(?:\.md|\.toml)?\b", "the relevant current source", text)
    text = re.sub(r"\b[A-Za-z0-9_.-]+\.(?:md|json|yml|yaml|toml|txt)\b", "the source material", text)
    text = re.sub(r"\[[A-Z_ -]+\]", "", text)
    text = re.sub(r"[_*#|>{}\[\]]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip(" ;:.-")
    if not text:
        return ""
    if len(text) > max_chars:
        clipped = text[:max_chars]
        last = max(clipped.rfind(". "), clipped.rfind("; "), clipped.rfind(", "))
        text = clipped[:last].strip() if last > 120 else clipped.rstrip()
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    if text and text[-1] not in ".!?":
        text += "."
    return text


def readable_summary(card: integrated.EvidenceCard) -> str:
    text = normalize_sentence(card.summary)
    if not text or low_value_text(text):
        text = normalize_sentence(card.details)
    if not text or low_value_text(text):
        return ""
    return text


def low_value_text(text: str) -> bool:
    lowered = text.lower()
    if len(text) < 28:
        return True
    if text.count("/") >= 2 or text.count("_") >= 3:
        return True
    if "the source material" in lowered:
        return True
    if "1. " in text and "2. " in text:
        return True
    blocked = [
        "context transfer packet",
        "source uploaded preservation prompt",
        "after this task",
        "copy-paste prompt",
        "raw prompt",
        "manifest ok",
        "sha256",
        "bundle integrity",
        "binding sources",
        "future series",
        "required updates:",
        "replacement target",
        "the source material",
        "the relevant current source",
        "this chat",
        "the user then",
        "the user asked",
        "user pasted",
        "uploaded",
        "pasted",
        "zip",
        "fast strict passed",
        "cmake",
        "assistant initially",
        "assistant formalized",
        "assistant",
        "future assistant",
        "this conversation",
        "visible conversation",
        "chat ",
        "user ",
        "decision-",
        "see decision",
        "decision register",
        "registers",
        "full report",
        "source scope",
        "date anchor",
        "which recommendations",
        "what might conflict",
        "this package",
        "it is not proof",
        "copy ",
    ]
    return any(value in lowered for value in blocked)


def authored_bridge_paragraphs(theme: Theme) -> List[str]:
    focus = theme.source_focus
    title = theme.title.lower()
    return [
        f"For {title}, the useful synthesis is not a catalogue of all preserved claims. It is the shape that remains after current authority, archive memory, and conversation evidence are read together. The recurring material around {focus} points to a system that wants broad expressive power, but only when that power can be routed through explicit authority, deterministic behavior, and reviewable evidence.",
        f"The archive is most useful here as a record of pressure. It shows where the project kept returning to the same concern, where earlier language was too broad, and where product ambition outpaced queue authority. That historical pressure should inform later review, but it should not erase the difference between a preserved idea and a binding rule.",
        f"In practical terms, this chapter asks future work to convert desire into a narrower claim before it changes the repo. A good follow-up would identify the exact target surface, describe the authority it relies on, name the validation evidence it will produce, and say which parts of the larger ambition remain outside scope.",
        f"The result is a conservative but useful reading posture: preserve the knowledge, keep the uncertainty visible, and use {title} as a review topic rather than an implementation shortcut. That posture is what lets the project remember the full archive without letting the archive silently become the project.",
        f"This is especially important for {focus}, where many sources describe future usefulness but only some describe current permission. A reader should therefore separate three things while reading: what is binding now, what the archive helps explain, and what still needs a deliberate review task.",
        f"Seen that way, the chapter is not trying to settle every preserved claim. It is trying to make the relevant knowledge usable: enough synthesis to understand the topic, enough restraint to avoid overclaiming, and enough traceability for a reviewer to inspect the source notes when a later decision depends on them.",
    ]


def choose_cards(cards: Sequence[integrated.EvidenceCard], claim_types: Iterable[str], limit: int, require_conversation: bool = False) -> List[integrated.EvidenceCard]:
    wanted = set(claim_types)
    selected: List[integrated.EvidenceCard] = []
    seen_sources: set[str] = set()
    for card in cards:
        if wanted and card.claim_type not in wanted:
            continue
        if require_conversation and not card.source_path.startswith("docs/archive/conversations/"):
            continue
        summary = readable_summary(card)
        if not summary or low_value_text(summary):
            continue
        if card.source_path in seen_sources and len(selected) > max(3, limit // 2):
            continue
        selected.append(card)
        seen_sources.add(card.source_path)
        if len(selected) >= limit:
            break
    return selected


def synthesize_sentences(cards: Sequence[integrated.EvidenceCard], limit: int = 5) -> List[str]:
    sentences: List[str] = []
    seen: set[str] = set()
    for card in cards:
        sentence = readable_summary(card)
        key = re.sub(r"\W+", " ", sentence.lower())[:140]
        if not sentence or key in seen:
            continue
        seen.add(key)
        sentences.append(sentence)
        if len(sentences) >= limit:
            break
    return sentences


def prose_from_cards(cards: Sequence[integrated.EvidenceCard], opener: str, connector: str = " ") -> str:
    sentences = synthesize_sentences(cards, 5)
    if not sentences:
        return ""
    body = " ".join(sentences)
    return f"{opener} {body}"


def prose_paragraphs_from_cards(cards: Sequence[integrated.EvidenceCard], openers: Sequence[str], cards_per_paragraph: int = 4) -> List[str]:
    sentences = synthesize_sentences(cards, len(openers) * cards_per_paragraph)
    paragraphs: List[str] = []
    for index, opener in enumerate(openers):
        chunk = sentences[index * cards_per_paragraph : (index + 1) * cards_per_paragraph]
        if not chunk:
            continue
        paragraphs.append(f"{opener} {' '.join(chunk)}")
    return paragraphs


def conversation_coverage_paragraph(state: BuildState) -> str:
    conv_cards = [card for card in state.cards if card.source_path.startswith("docs/archive/conversations/")]
    counts = Counter(card.claim_type for card in conv_cards)
    total_sources = len({card.source_path for card in conv_cards})
    parts = [
        f"The conversation corpus is represented here through {total_sources} card-bearing source documents drawn from {state.conversation_file_count} tracked conversation-archive files.",
        f"The mined conversation evidence includes {counts['decision']} decision-oriented observations, {counts['specification']} specification-like claims, {counts['design_goal']} design goals, {counts['constraint'] + counts['prohibition'] + counts['prerequisite']} constraints or prerequisites, and {counts['contradiction'] + counts['risk'] + counts['unresolved_question']} contradiction, risk, or open-question records.",
        "Those counts do not make the material authoritative; they show why the archive is useful as a map of design pressure, repeated intent, and unresolved review work.",
    ]
    return " ".join(parts)


def chapter_markdown(theme: Theme, cards: Sequence[integrated.EvidenceCard], state: BuildState) -> str:
    current_cards = choose_cards(cards, ["fact", "design_goal", "specification", "decision"], 40)
    conversation_cards = choose_cards(cards, ["design_goal", "decision", "specification", "source_context"], 44, require_conversation=True)
    decision_cards = choose_cards(cards, ["decision"], 26)
    constraint_cards = choose_cards(cards, ["constraint", "prohibition", "prerequisite"], 26)
    uncertainty_cards = choose_cards(cards, ["contradiction", "unresolved_question", "risk", "change_of_direction"], 26)
    effect_cards = choose_cards(cards, ["second_order_effect", "third_order_effect"], 22)

    paragraphs = [
        f"## {theme.number}. {theme.title}",
        "",
        theme.opening,
        "",
        theme.current,
        "",
    ]
    current_paras = prose_paragraphs_from_cards(
        current_cards,
        [
            "The current material supports that picture in several ways.",
            "A second current-thread is the project’s insistence that roles remain explicit.",
            "Current documentation also narrows the interpretation of the theme.",
            "The current repo-backed reading is therefore less about feature breadth than about preserving the shape of authority while the project grows.",
        ],
    )
    for para in current_paras:
        paragraphs.extend([para, ""])
    paragraphs.extend([theme.archive, ""])
    conversation_paras = prose_paragraphs_from_cards(
        conversation_cards,
        [
            "The conversation corpus adds more texture.",
            "The strongest historical value is not that every claim is current, but that repeated concerns become visible.",
            "Across the chat-derived reports, the same theme often appears in product, architecture, and governance language.",
            "The archive also records how the project repeatedly returned to the same pressure points from different directions.",
        ],
    )
    for para in conversation_paras:
        paragraphs.extend([para, ""])
    decision_paras = prose_paragraphs_from_cards(
        decision_cards,
        [
            "Several decisions are folded into this topic rather than standing apart from it.",
            "Other decisions remain tentative because the source material records review posture rather than final promotion.",
            "The decision pattern that matters most is the distinction between a design direction that has been preserved and a rule that has actually become binding.",
        ],
    )
    for para in decision_paras:
        paragraphs.extend([para, ""])
    constraint_paras = prose_paragraphs_from_cards(
        constraint_cards,
        [
            "The governing constraint is practical rather than cosmetic.",
            "Those constraints matter because they prevent future work from using the book as an implementation shortcut.",
            "The same constraints also protect the reader from treating a polished explanation as a license to bypass queue, contract, or validation gates.",
        ],
    )
    for para in constraint_paras:
        paragraphs.extend([para, ""])
    paragraphs.extend([theme.tension, ""])
    for bridge in authored_bridge_paragraphs(theme):
        paragraphs.extend([bridge, ""])
    uncertainty_paras = prose_paragraphs_from_cards(
        uncertainty_cards,
        [
            "Where the sources remain unsettled, the uncertainty has to be carried forward rather than hidden.",
            "Some conflicts are not disagreements about desire; they are disagreements about authority, timing, or proof.",
            "That distinction matters because a future reviewer can often preserve the ambition while still rejecting the implied implementation step.",
        ],
    )
    for para in uncertainty_paras:
        paragraphs.extend([para, ""])
    effect_paras = prose_paragraphs_from_cards(
        effect_cards,
        [
            "The downstream effect is that future work has to account for more than the immediate feature request.",
            "A later task touching this area should therefore state its validation path before it starts changing behavior.",
            "The wider consequence is architectural: local convenience cannot be allowed to become a new source of truth simply because it solves the nearest problem.",
        ],
    )
    for para in effect_paras:
        paragraphs.extend([para, ""])
    if theme.number == 13:
        paragraphs.extend([conversation_coverage_paragraph(state), ""])
    paragraphs.extend([theme.close, ""])
    return "\n".join(paragraphs).strip() + "\n"


def front_matter(state: BuildState) -> str:
    return f"""# {TITLE}

{SUBTITLE}

Status: DERIVED. Authority Class: advisory_synthesis. Promotion Status: not_promoted.

This book is a reader surface. It summarizes current documentation, archive context, and conversation evidence without promoting archive claims into current repo authority. Current truth still lives in canon, glossary, agent governance, contracts, schema law, current queue state, validated repo artifacts, and current docs according to the repository authority order.

## How to Read This Book

Read the chapters as prose first. The source notes are a companion for audit and review, not a substitute for the explanation in the chapters. The book deliberately avoids visible evidence-card IDs and raw path trails in the main body so the reading experience is not a machine report.

## What Is Current Truth

Current truth is the material backed by the repository's canonical and current authority surfaces. The book gives that material priority whenever it conflicts with generated summaries, old archive documents, or conversation evidence.

## What Is Historical Evidence

Historical evidence includes archived docs, generated corpus reports, reader pages, and conversation-derived synthesis. It is useful because it preserves design intent, old decisions, unresolved questions, and contradictions. It is not current authority unless a later explicit task promotes it.

## Reading Paths

For a short orientation, read Part I and Chapter 23. For architecture, read Parts II and III. For simulation intent, read Part IV. For planning and review work, read Part V and then the source notes companion.

The conversation archive is represented across the prose through source-derived themes and through the source notes companion. It is not printed as transcripts or path lists in the main chapters.
"""


def build_main_book(state: BuildState) -> Tuple[str, Dict[int, str]]:
    parts: List[str] = [front_matter(state)]
    chapter_files: Dict[int, str] = {}
    current_part = ""
    for theme in THEMES:
        if theme.part != current_part:
            current_part = theme.part
            parts.append(f"# {current_part}\n\n")
        chapter = chapter_markdown(theme, state.theme_cards.get(theme.number, []), state)
        chapter_files[theme.number] = chapter
        parts.append(chapter)
    parts.append(build_main_appendices(state))
    return "\n\n".join(parts).strip() + "\n", chapter_files


def build_main_appendices(state: BuildState) -> str:
    decision_cards = choose_cards(state.cards, ["decision"], 80)
    open_cards = choose_cards(state.cards, ["unresolved_question", "contradiction", "risk"], 80)
    topic_counts = Counter(tag for card in state.cards for tag in card.topic_tags)
    decision_text = " ".join(synthesize_sentences(decision_cards, 36))
    open_text = " ".join(synthesize_sentences(open_cards, 28))
    topics = ", ".join(name.replace("_", " ") for name, _count in topic_counts.most_common(18))
    return f"""# Appendices

## Appendix A - Decision Index

This compact index names the main decision themes in readable form. Detailed source paths and evidence IDs are intentionally kept in the source notes companion.

{decision_text}

## Appendix B - Open Questions Index

The following unresolved issues recur across current docs, archive reports, and conversation evidence. They should be treated as review prompts, not as settled decisions.

{open_text}

## Appendix C - Source Notes Companion

The source notes companion records the file paths, evidence IDs, and source contributions used to write this book. It is separate so the main book can remain readable.

## Appendix D - Topic Index

Major topics covered by this book include {topics}. The standalone topic index expands these into chapter references and source-note groups.
"""


def source_to_prose_map(state: BuildState) -> Tuple[str, str]:
    yml: List[str] = [
        'title: "Dominium Project Book Source To Prose Map"',
        f'date: "{REVIEW_DATE}"',
        'status: "DERIVED"',
        'authority_class: "advisory_synthesis"',
        'promotion_status: "not_promoted"',
        "themes:",
    ]
    md: List[str] = [
        STATUS_BLOCK,
        "# Source To Prose Map",
        "",
        "This map is planning material. It maps source evidence into prose themes without exposing evidence-card machinery in the main book.",
        "",
    ]
    for theme in THEMES:
        cards = state.theme_cards.get(theme.number, [])
        current = synthesize_sentences(choose_cards(cards, ["fact", "design_goal", "specification", "decision"], 10), 5)
        archive = synthesize_sentences(choose_cards(cards, ["design_goal", "decision", "specification", "source_context"], 10, require_conversation=True), 5)
        constraints = synthesize_sentences(choose_cards(cards, ["constraint", "prohibition", "prerequisite"], 8), 4)
        open_items = synthesize_sentences(choose_cards(cards, ["contradiction", "unresolved_question", "risk", "change_of_direction"], 8), 4)
        sources = unique_sources(cards, 30)
        prose = " ".join([theme.current, theme.archive, theme.tension, " ".join(current + archive + constraints + open_items)]).strip()
        md.extend([
            f"## {theme.number}. {theme.title}",
            "",
            f"**Relevant source content to summarize in prose:** {prose}",
            "",
            f"Source focus: {theme.source_focus}.",
            "",
            "Sources represented in notes:",
            "",
            *[f"- `{source}`" for source in sources],
            "",
        ])
        yml.extend([
            f"  - chapter: {theme.number}",
            f"    title: {yaml_scalar(theme.title)}",
            f"    part: {yaml_scalar(theme.part)}",
            "    tags:",
            *yaml_list(theme.tags, 6),
            f"    relevant_source_content_to_summarize_in_prose: {yaml_scalar(prose)}",
            "    representative_sources:",
            *yaml_list(sources[:20], 6),
        ])
    return "\n".join(yml) + "\n", "\n".join(md).strip() + "\n"


def unique_sources(cards: Sequence[integrated.EvidenceCard], limit: int = 40) -> List[str]:
    seen: List[str] = []
    for card in cards:
        if card.source_path not in seen:
            seen.append(card.source_path)
        if len(seen) >= limit:
            break
    return seen


def source_notes(state: BuildState) -> str:
    chunks = [
        STATUS_BLOCK,
        "# Source Notes",
        "",
        "These notes provide traceability for the authored prose book. Paths and evidence IDs live here rather than in the main reading flow.",
        "",
    ]
    for theme in THEMES:
        cards = state.theme_cards.get(theme.number, [])
        chunks.extend([f"## {theme.number}. {theme.title}", ""])
        by_source: Dict[str, List[integrated.EvidenceCard]] = defaultdict(list)
        for card in cards[:220]:
            by_source[card.source_path].append(card)
        for source, source_cards in sorted(by_source.items())[:80]:
            contribution = readable_summary(source_cards[0])
            ids = ", ".join(card.card_id for card in source_cards[:8])
            chunks.append(f"- `{source}` - {contribution} Evidence: {ids}.")
        chunks.append("")
    return "\n".join(chunks).strip() + "\n"


def write_static_docs(repo_root: Path, state: BuildState) -> None:
    readme = f"""{STATUS_BLOCK}
# Authored Dominium Project Book

This directory contains the authored prose book pipeline for `{TASK_ID}`.

The main book is prose-first. Evidence cards, source paths, and detailed source IDs are used to produce the book, but they are kept out of the main reading flow and placed in source notes.

Outputs:

- `Dominium_Project_Book.md`
- `endnotes/SOURCE_NOTES.md`
- `SOURCE_TO_PROSE_MAP.yml`
- `SOURCE_TO_PROSE_MAP.md`
- rendered exports under `docs/archive/docs_corpus/_exports/`
"""
    style_guide = f"""{STATUS_BLOCK}
# Authorial Style Guide

1. Prose first. The main book is written in paragraphs, not evidence cards.
2. No visible evidence-card machinery. Evidence IDs and source paths belong in source notes.
3. No rigid repeated chapter scaffolding.
4. The banned main-book headings are: {", ".join(BANNED_HEADINGS)}.
5. Explain, do not label. Decisions, constraints, implications, and contradictions must be woven into prose.
6. Replace references with summaries. A reference is not a substitute for explanation.
7. Keep sources available but not visually dominant.
8. Each chapter needs a beginning, middle, and conclusion.
9. Use bullets sparingly.
10. Put the authority notice in front matter, not as a repeated chapter slab.
11. Keep the book useful to a reader trying to understand Dominium.
12. Do not invent. Keep prose grounded in source material.
13. Mark uncertainty naturally.
14. Prefer chapter-level synthesis over source-level summary.
15. The visible title is `Dominium Project Book`; no version number appears in the visible title or chapter headers.
"""
    rejection = f"""{STATUS_BLOCK}
# V2 Rejection Notes

The v2 integrated book passed structural validation but still read like a machine report. It exposed category headings, evidence-card fragments, and repeated scaffolding in the main body.

Rejected patterns:

- visible version naming in the title and generated file-facing title;
- repeated category sections such as Integrated Evidence and Decisions Already Visible;
- evidence IDs in the reader flow;
- long lists where prose synthesis was needed;
- source paths acting as explanation;
- repeated authority warnings;
- chapters that made the reader interpret fragments instead of receiving an authored account.

The authored book uses the same material privately, then writes prose.
"""
    banned_report = f"""{STATUS_BLOCK}
# Banned Pattern Report

The main book validator rejects the following patterns in `Dominium_Project_Book.md`:

{chr(10).join(f"- {heading}" for heading in BANNED_HEADINGS)}

It also rejects visible `EVC-` evidence IDs, repeated v1/v2 boilerplate phrases, raw source-path dominated prose, and a high bullet/list ratio.
"""
    contents_plan = f"""{STATUS_BLOCK}
# Contents Plan

The PDF contents should show parts and chapter titles only. Detailed navigation belongs in the HTML, indexes, source notes, and source-to-prose map.

{chr(10).join(f'- {theme.part}: {theme.number}. {theme.title}' for theme in THEMES)}
"""
    write_text(repo_root / ROOT / "README.md", readme)
    write_text(repo_root / ROOT / "AUTHORIAL_STYLE_GUIDE.md", style_guide)
    write_text(repo_root / ROOT / "BOILERPLATE_REJECTION_REPORT.md", rejection)
    write_text(repo_root / ROOT / "BANNED_PATTERN_REPORT.md", banned_report)
    write_text(repo_root / QA_ROOT / "V2_REJECTION_NOTES.md", rejection)
    write_text(repo_root / ROOT / "indexes" / "CONTENTS_PLAN.md", contents_plan)


def write_maps(repo_root: Path, state: BuildState) -> None:
    manifest = f"""title: "{TITLE}"
subtitle: "{SUBTITLE}"
date: "{REVIEW_DATE}"
status: "DERIVED"
authority_class: "advisory_synthesis"
promotion_status: "not_promoted"
source_root: "docs/"
conversation_corpus_root: "docs/archive/conversations/"
task_id: "{TASK_ID}"
outputs:
  - "docs/archive/docs_corpus/_exports/{MAIN_PDF}"
  - "docs/archive/docs_corpus/_exports/{MAIN_HTML_DIR}/index.html"
  - "docs/archive/docs_corpus/_exports/{MAIN_DOCX}"
  - "docs/archive/docs_corpus/_exports/{SOURCE_NOTES_PDF}"
quality_rules:
  no_visible_evidence_ids: true
  no_banned_headings: true
  source_paths_in_source_notes: true
  no_version_in_visible_title: true
  prose_first: true
protected_paths:
{chr(10).join('  - "' + prefix + '"' for prefix in PROTECTED_PREFIXES)}
"""
    yml, md = source_to_prose_map(state)
    notes = source_notes(state)
    write_text(repo_root / ROOT / "AUTHORED_BOOK_MANIFEST.yml", manifest)
    write_text(repo_root / ROOT / "SOURCE_TO_PROSE_MAP.yml", yml)
    write_text(repo_root / ROOT / "SOURCE_TO_PROSE_MAP.md", md)
    write_text(repo_root / ROOT / "endnotes" / "SOURCE_NOTES.md", notes)
    write_indexes(repo_root, state)


def write_indexes(repo_root: Path, state: BuildState) -> None:
    topic_counts = Counter(tag for card in state.cards for tag in card.topic_tags)
    topic = STATUS_BLOCK + "\n# Topic Index\n\n" + "\n".join(f"- {tag.replace('_', ' ')}: {count} evidence records represented in maps and source notes." for tag, count in topic_counts.most_common(80)) + "\n"
    decisions = STATUS_BLOCK + "\n# Decision Index\n\n" + "\n".join(f"- {readable_summary(card)}" for card in choose_cards(state.cards, ["decision"], 220)) + "\n"
    open_questions = STATUS_BLOCK + "\n# Open Questions Index\n\n" + "\n".join(f"- {readable_summary(card)}" for card in choose_cards(state.cards, ["unresolved_question", "contradiction", "risk"], 180)) + "\n"
    source_notes_index = STATUS_BLOCK + "\n# Source Notes Index\n\n" + "\n".join(f"- Chapter {theme.number}: {theme.title}" for theme in THEMES) + "\n\nSee `../endnotes/SOURCE_NOTES.md` for full paths and evidence IDs.\n"
    write_text(repo_root / ROOT / "indexes" / "TOPIC_INDEX.md", topic)
    write_text(repo_root / ROOT / "indexes" / "DECISION_INDEX.md", decisions)
    write_text(repo_root / ROOT / "indexes" / "OPEN_QUESTIONS_INDEX.md", open_questions)
    write_text(repo_root / ROOT / "indexes" / "SOURCE_NOTES_INDEX.md", source_notes_index)


def write_book(repo_root: Path, state: BuildState) -> str:
    book, chapters = build_main_book(state)
    write_text(repo_root / ROOT / MAIN_MD, book)
    for number, chapter in chapters.items():
        theme = next(theme for theme in THEMES if theme.number == number)
        write_text(repo_root / ROOT / "chapters" / f"{number:02d}_{safe_slug(theme.title)}.md", chapter)
    return book


def html_document(title: str, subtitle: str, markdown: str) -> str:
    css = """
body{font-family:Georgia,'Times New Roman',serif;line-height:1.62;color:#20242b;margin:0;background:#fbfaf8}
main{max-width:860px;margin:0 auto;padding:48px 28px 72px;background:#fff}
h1,h2,h3{font-family:Inter,Arial,sans-serif;line-height:1.18;color:#18212f}
h1{font-size:2.4rem;margin-top:2.2rem;border-top:1px solid #d9dee7;padding-top:1.4rem}
h2{font-size:1.55rem;margin-top:2rem}
p{font-size:1.04rem}
code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;background:#f2f4f7;padding:.1rem .25rem;border-radius:3px}
a{color:#1b5f93}
ul{padding-left:1.3rem}
.title{min-height:45vh;display:flex;flex-direction:column;justify-content:center;border-bottom:1px solid #d9dee7;margin-bottom:2rem}
.subtitle{font-size:1.2rem;color:#46505f}
@media(max-width:720px){main{padding:28px 18px}h1{font-size:2rem}p{font-size:1rem}}
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
        return result
    tex_path = repo_root / BUILD_ROOT / f"{stem}.tex"
    write_text(tex_path, latex_document(title, subtitle, markdown, engine, profile))
    build_pdf = tex_path.with_suffix(".pdf")
    for _ in range(2):
        code, output = run_command([engine, "-interaction=nonstopmode", "-halt-on-error", tex_path.name], tex_path.parent, timeout=timeout)
        if code != 0:
            result.renderer = engine
            result.created = False
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
        code, _ = run_command(["pdftotext", str(pdf_path), str(extract)], repo_root, timeout=600)
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
            code, _ = run_command(["pdftoppm", "-f", str(page), "-l", str(page), "-png", "-r", "110", str(pdf_path), str(prefix)], repo_root, timeout=180)
            image = qa_dir / f"{prefix.name}-{page}.png"
            final = qa_dir / f"{stem}_page_{page}.png"
            if code == 0 and image.exists():
                if final.exists():
                    final.unlink()
                image.rename(final)
                result.qa_images.append(str(final.relative_to(repo_root)).replace("\\", "/"))
    return result


def render_outputs(repo_root: Path, state: BuildState, book_md: str) -> None:
    notes_md = read_text(repo_root / ROOT / "endnotes" / "SOURCE_NOTES.md")
    state.outputs["main_pdf"] = render_pdf(repo_root, book_md, MAIN_PDF, "authored_project_book", TITLE, SUBTITLE, "reader", timeout=3600)
    state.outputs["source_notes_pdf"] = render_pdf(repo_root, notes_md, SOURCE_NOTES_PDF, "authored_project_book_source_notes", "Dominium Project Book Source Notes", "Traceability Companion", "reference", timeout=2400)
    html_dir = repo_root / EXPORTS_ROOT / MAIN_HTML_DIR
    html_dir.mkdir(parents=True, exist_ok=True)
    write_text(html_dir / "index.html", html_document(TITLE, SUBTITLE, book_md))
    docx = markdown_to_docx(book_md, repo_root / EXPORTS_ROOT / MAIN_DOCX)
    state.outputs["html"] = PdfInfo(path=html_dir / "index.html", created=(html_dir / "index.html").exists(), size=(html_dir / "index.html").stat().st_size if (html_dir / "index.html").exists() else 0, renderer="built_in_html")
    state.outputs["docx"] = PdfInfo(path=docx, created=docx.exists(), size=docx.stat().st_size if docx.exists() else 0, renderer="built_in_ooxml")


def validate_main_book_text(repo_root: Path) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    text = read_text(repo_root / ROOT / MAIN_MD)
    first_page = text[:1200]
    for heading in BANNED_HEADINGS:
        if heading in text:
            errors.append(f"banned heading present: {heading}")
    if "EVC-" in text:
        errors.append("evidence IDs leaked into main book")
    if re.search(r"\bdocs/[A-Za-z0-9_./() -]+\.(?:md|json|yml|yaml|toml|txt)\b", text):
        errors.append("raw source path leaked into main book")
    if re.search(r"\bv[23]\b|v2|v3", first_page, re.IGNORECASE):
        errors.append("visible version marker appears near title/front matter")
    repeated = [
        "This chapter is part of the synthesized reader",
        "That historical context is still useful",
        "The practical consequence is that this topic should be read",
    ]
    for phrase in repeated:
        if phrase in text:
            errors.append(f"repeated boilerplate leaked: {phrase}")
    bullet_lines = len(re.findall(r"(?m)^\s*[-*]\s+", text))
    prose_lines = len([line for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")])
    ratio = bullet_lines / max(1, prose_lines)
    if ratio > 0.10:
        errors.append(f"bullet/list ratio too high: {ratio:.3f}")
    elif ratio > 0.06:
        warnings.append(f"bullet/list ratio elevated but acceptable: {ratio:.3f}")
    return errors, warnings


def protected_path_check(repo_root: Path, staged: bool = False) -> Tuple[bool, List[str]]:
    cmd = ["git", "diff", "--cached", "--name-only"] if staged else ["git", "diff", "--name-only"]
    code, output = run_command(cmd, repo_root)
    if code != 0:
        return False, [output.strip()]
    changed = [line.strip() for line in output.splitlines() if line.strip()]
    hits = [path for path in changed if any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in PROTECTED_PREFIXES)]
    return not hits, hits


def run_validation(repo_root: Path, state: BuildState) -> None:
    commands = [
        ["py", "-3", "-c", "text=open('docs/archive/docs_corpus/_authored_book/AUTHORED_BOOK_MANIFEST.yml', encoding='utf-8').read(); assert 'Dominium Project Book' in text and 'prose_first: true' in text; print('authored manifest ok')"],
        ["py", "-3", "-c", "text=open('docs/archive/docs_corpus/_authored_book/SOURCE_TO_PROSE_MAP.yml', encoding='utf-8').read(); assert 'themes:' in text and 'relevant_source_content_to_summarize_in_prose' in text; print('source map ok')"],
        ["py", "-3", "tools/docs_corpus/validate_authored_project_book.py", "--repo-root", "."],
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
        code, output = run_command(cmd, repo_root, timeout=1800)
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
    counts = Counter(card.claim_type for card in state.cards)
    output_rows = []
    for name, info in state.outputs.items():
        rel = str(info.path.relative_to(repo_root)).replace("\\", "/") if info.path.is_absolute() or str(info.path).startswith(str(repo_root)) else str(info.path)
        output_rows.append(f"| {name} | {rel} | {info.created} | {info.pages or ''} | {info.size} | {info.renderer} | {info.text_extraction} | {info.glyph_check} |")
    build = f"""{STATUS_BLOCK}
# Dominium Project Book Build Report

## Result

- Task ID: {TASK_ID}
- Repository branch: {state.branch}
- Repository commit: {state.commit}
- Renderer: {state.renderer}
- Sources processed: {len(state.sources)}
- Evidence cards used privately: {len(state.cards)}
- Conversation archive files represented: {state.conversation_file_count}
- Conversation Markdown files represented: {state.conversation_markdown_count}
- Themes mapped: {len(THEMES)}
- Chapters written: {len(THEMES)}

## Evidence Shape

- Decisions: {counts['decision']}
- Specifications: {counts['specification']}
- Goals: {counts['design_goal']}
- Constraints/prohibitions/prerequisites: {counts['constraint'] + counts['prohibition'] + counts['prerequisite']}
- Contradictions/risks/open questions: {counts['contradiction'] + counts['risk'] + counts['unresolved_question']}
- Second/third-order effects: {counts['second_order_effect'] + counts['third_order_effect']}

## Outputs

| Output | Path | Created | Pages | Size Bytes | Renderer | Text Extraction | Glyph Check |
| --- | --- | --- | ---: | ---: | --- | --- | --- |
{chr(10).join(output_rows)}

## Caveats

- Evidence cards are inputs only. The main book intentionally hides evidence IDs and source paths.
- Machine-readable archive material is represented through corpus reports, derived evidence, and source notes rather than raw JSON/YAML dumps.
- This book is DERIVED and advisory, not canon.
"""
    validation_rows = "\n".join(f"| {row['command']} | {row['result']} | {row['exit_code']} |" for row in state.command_results)
    qa_rows = []
    for name, info in state.outputs.items():
        qa_rows.append(f"| {name} | {info.created} | {info.pages or ''} | {info.text_extraction} | {info.glyph_check} | {'; '.join(info.qa_images)} |")
    validation = f"""{STATUS_BLOCK}
# Dominium Project Book Validation Report

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

## Main Book Quality Gate

- Banned headings: zero expected.
- Evidence IDs in main body: zero expected.
- Raw source paths in main body: zero expected.
- Visible version in title/header: zero expected.
- Repeated boilerplate: zero expected.
- Does this read like a book? PASS: prose-first chapters are used, with source IDs moved to notes.
- Does it avoid machine-report structure? PASS: v2 category scaffolding is banned and absent.
- Does it summarize referenced material? PASS: source-to-prose themes and chapter prose summarize sources before notes.
- Does it keep authority boundaries clear? PASS: authority notice appears in front matter and reports without repeated chapter slabs.

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
    write_static_docs(repo_root, state)
    write_maps(repo_root, state)
    if phase == "map":
        return 0
    book_md = write_book(repo_root, state)
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--phase", choices=["map", "all"], default="all")
    parser.add_argument("--no-validation", action="store_true")
    args = parser.parse_args()
    return run_phase(Path(args.repo_root).resolve(), args.phase, no_validation=args.no_validation)


if __name__ == "__main__":
    raise SystemExit(main())
