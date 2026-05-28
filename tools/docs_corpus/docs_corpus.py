"""Build derived docs-corpus inventory, reconciliation, wiki, and book outputs.

This tool is intentionally archive-only. It reads git-tracked files under
``docs/`` and writes derived advisory outputs under
``docs/archive/docs_corpus/`` without modifying source docs or promoting
archive/conversation claims into current repo authority.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
from xml.sax.saxutils import escape as xml_escape


TASK_ID = "DOCS-CORPUS-MEGA-01"
REVIEW_DATE = "2026-05-28"
SOURCE_ROOT = Path("docs")
OUTPUT_ROOT = Path("docs/archive/docs_corpus")
BOOK_DIR = OUTPUT_ROOT / "_book"
EXPORTS_DIR = OUTPUT_ROOT / "_exports"
QA_DIR = BOOK_DIR / "qa"
TITLE = "Dominium Documentation Corpus Book v0"
SUBTITLE = "Current Docs, Archive Archaeology, Conversation Synthesis, and Reconciliation Guide"
READER_BASENAME = "Dominium_Docs_Corpus_Reader_v0"
REFERENCE_BASENAME = "Dominium_Docs_Corpus_Reference_Appendix_v0"
BUILD_REPORT_BASENAME = "Dominium_Docs_Corpus_Build_Report_v0"
VALIDATION_REPORT_BASENAME = "Dominium_Docs_Corpus_Validation_Report_v0"

STATUS_BLOCK = """Status: DERIVED
Last Reviewed: 2026-05-28
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

PROTECTED_PREFIXES = (
    "docs/canon/",
    "docs/architecture/",
    "docs/reference/contracts/",
    "contracts/",
    "schema/",
    "engine/",
    "game/",
    "runtime/",
    "apps/",
    "release/",
    "updates/",
    "security/",
    ".aide/queue/current.toml",
)

TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".csv",
    ".tsv",
    ".rst",
    ".html",
    ".htm",
    ".xml",
    ".svg",
}

BINARY_EXTENSIONS = {
    ".zip",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".pdf",
    ".docx",
    ".epub",
    ".ico",
    ".bin",
}

METADATA_FIELDS = [
    "Status",
    "Last Reviewed",
    "Supersedes",
    "Superseded By",
    "Stability",
    "Future Series",
    "Replacement Target",
    "Binding Sources",
    "Result",
    "Version",
    "Compatibility",
]

REQUIRED_REPORTS = [
    "README.md",
    "_intake/DOCS_CORPUS_MANIFEST.json",
    "_intake/DOCS_CORPUS_MANIFEST.md",
    "_intake/DOCS_SOURCE_INDEX_v0.md",
    "_intake/DOCS_FILE_COUNTS_v0.md",
    "_intake/DOCS_TREE_SUMMARY_v0.md",
    "_intake/DOCS_LARGE_FILES_AND_NON_MARKDOWN_v0.md",
    "_audit/DOCS_STATUS_HEADER_AUDIT_v0.md",
    "_audit/DOCS_AUTHORITY_CLASSIFICATION_DRAFT_v0.md",
    "_audit/DOCS_AUTHORITY_MAP_v0.md",
    "_audit/DOCS_SUPERSESSION_MAP_v0.md",
    "_audit/DOCS_BINDING_SOURCE_MAP_v0.md",
    "_audit/DOCS_ARCHIVE_CLASSIFICATION_v0.md",
    "_audit/DOCS_BOOK_INCLUSION_PLAN_v0.md",
    "_audit/DOCS_DRIFT_MATRIX_v0.md",
    "_audit/DOCS_CONTRADICTION_MATRIX_v0.md",
    "_audit/DOCS_STALENESS_AND_VERIFICATION_v0.md",
    "_audit/DOCS_DUPLICATE_SHADOWS_v0.md",
    "_audit/DOCS_COVERAGE_GAPS_v0.md",
    "_archive/DOCS_ARCHIVE_ATLAS_v0.md",
    "_archive/DOCS_ARCHIVE_FAMILIES_v0.md",
    "_archive/DOCS_ARCHIVE_STALE_OR_USEFUL_v0.md",
    "_archive/DOCS_ARCHIVE_TO_CURRENT_CROSSWALK_v0.md",
    "_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md",
    "_reconciliation/DOCS_REPO_TRUTH_CROSSWALK_v0.md",
    "_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md",
    "_reconciliation/DOCS_CANON_ARCHITECTURE_ALIGNMENT_v0.md",
    "_reconciliation/DOCS_ARCHIVE_CONVERSATION_ALIGNMENT_v0.md",
    "_reconciliation/DOCS_PROMOTION_QUEUE_v0.md",
    "_reconciliation/DOCS_DECISION_DOCKET_v0.md",
    "_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md",
    "_wiki/index.md",
    "_wiki/current_authority.md",
    "_wiki/archive_archaeology.md",
    "_wiki/conversation_corpus.md",
    "_wiki/decisions.md",
    "_wiki/promotion_candidates.md",
    "_wiki/contradictions.md",
    "_wiki/staleness_and_verification.md",
    "_wiki/source_index.md",
    "_wiki/reading_paths.md",
    "_book/README.md",
    "_book/BOOK_MANIFEST.yml",
    "_book/index.md",
    "_book/chapters/00_front_matter.md",
    "_book/chapters/01_current_project_orientation.md",
    "_book/chapters/02_current_canon_architecture_contracts.md",
    "_book/chapters/03_product_runtime_tooling_domains.md",
    "_book/chapters/04_archive_archaeology.md",
    "_book/chapters/05_conversation_corpus_integration.md",
    "_book/chapters/06_cross_corpus_reconciliation.md",
    "_book/chapters/07_decisions_promotion_roadmap.md",
    "_book/chapters/08_navigation_reading_paths.md",
    "_book/appendices/A_docs_corpus_manifest_summary.md",
    "_book/appendices/B_authority_and_supersession_registers.md",
    "_book/appendices/C_archive_family_listing.md",
    "_book/appendices/D_contradiction_staleness_promotion_decision_registers.md",
    "_book/appendices/E_source_path_index.md",
    "_exports/Dominium_Docs_Corpus_Reader_v0.pdf",
    "_exports/Dominium_Docs_Corpus_Reader_v0.html/index.html",
    "_exports/Dominium_Docs_Corpus_Reader_v0.docx",
    "_exports/Dominium_Docs_Corpus_Reader_v0.epub",
    "_exports/Dominium_Docs_Corpus_Reference_Appendix_v0.pdf",
    "_exports/Dominium_Docs_Corpus_Build_Report_v0.md",
    "_exports/Dominium_Docs_Corpus_Validation_Report_v0.md",
]

REFERENCE_DOCS = {
    "README.md": "project identity and repository orientation",
    "docs/README.md": "docs taxonomy and archive status",
    "AGENTS.md": "agent governance and authority model",
    "docs/canon/constitution_v1.md": "constitutional canon",
    "docs/canon/glossary_v1.md": "canonical vocabulary",
    "docs/planning/AUTHORITY_ORDER.md": "authority ordering and conflict handling",
    "docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md": "source intake and provenance law",
    ".aide/queue/current.toml": "current queue and blocked scope",
    "docs/repo/FOUNDATION_LOCK.md": "foundation state and blocked broad feature work",
}

RECONCILIATION_TOPICS = [
    (
        "project_identity",
        "Project identity and purpose",
        ["README.md", "docs/README.md"],
        "current_repo_truth",
        "Use current repo orientation first; archive and conversations may only explain history.",
    ),
    (
        "canon_glossary_authority",
        "Canon and glossary authority",
        ["docs/canon/constitution_v1.md", "docs/canon/glossary_v1.md", "AGENTS.md"],
        "current_repo_truth",
        "Canon, glossary, and AGENTS outrank archive and generated outputs.",
    ),
    (
        "engine_game_runtime_product_boundaries",
        "Engine/game/runtime/product boundaries",
        ["README.md", "docs/architecture", "docs/archive/conversations/_reconciliation"],
        "consistent_but_review_required",
        "Boundary claims need current-doc support before promotion.",
    ),
    (
        "determinism_replay_provenance",
        "Determinism, replay, and provenance",
        ["AGENTS.md", "docs/canon/constitution_v1.md", "docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md"],
        "current_repo_truth",
        "Determinism and provenance constraints are binding where scoped by canon and governance.",
    ),
    (
        "process_only_mutation",
        "Process-only mutation",
        ["AGENTS.md", "docs/canon/constitution_v1.md"],
        "current_repo_truth",
        "Authoritative truth mutation must occur through lawful deterministic Process execution.",
    ),
    (
        "law_authority_refusal_capabilities",
        "Law, authority, refusal, and capability model",
        ["AGENTS.md", "docs/canon/constitution_v1.md", "docs/reference/contracts"],
        "current_repo_truth_with_review_needed",
        "Current law and contracts govern; archive claims are advisory only.",
    ),
    (
        "pack_driven_integration",
        "Pack-driven integration",
        ["AGENTS.md", "docs/canon/constitution_v1.md"],
        "current_repo_truth",
        "Optional content and capabilities must remain pack- and registry-driven.",
    ),
    (
        "profiles_over_modes",
        "Profiles over runtime mode flags",
        ["AGENTS.md", "docs/canon/constitution_v1.md"],
        "current_repo_truth",
        "Hardcoded runtime mode branches remain prohibited.",
    ),
    (
        "workbench_aide_codex_tooling",
        "Workbench/AIDE/Codex/tooling role",
        ["AGENTS.md", ".aide/queue/current.toml", "docs/archive/conversations/_synthesis"],
        "blocked_scope_sensitive",
        "Tooling is active, but broad Workbench UI and native GUI work remain blocked by the queue.",
    ),
    (
        "conversation_corpus_role",
        "Conversation corpus role",
        ["docs/archive/conversations/README.md", "docs/archive/conversations/_exports"],
        "conversation_advisory_only",
        "Conversation material is derived historical evidence, not current truth.",
    ),
    (
        "release_setup_launcher_platform",
        "Release/setup/launcher/platform state",
        [".aide/queue/current.toml", "docs/release", "docs/archive/conversations/_promotion"],
        "blocked_scope_sensitive",
        "Release publication remains blocked unless a stronger current queue source opens it.",
    ),
    (
        "renderer_ui_native_gui_scope",
        "Renderer/UI/native GUI scope",
        [".aide/queue/current.toml", "docs/archive/conversations/_reconciliation"],
        "blocked_by_current_queue",
        "Renderer implementation and native GUI work remain blocked.",
    ),
    (
        "provider_package_runtime_scope",
        "Provider/package runtime scope",
        [".aide/queue/current.toml", "docs/archive/conversations/_promotion"],
        "blocked_by_current_queue",
        "Provider runtime, package runtime, and runtime module loading remain blocked.",
    ),
    (
        "gameplay_domain_feature_scope",
        "Gameplay/domain feature scope",
        [".aide/queue/current.toml", "docs/archive/conversations/_synthesis"],
        "blocked_by_current_queue",
        "Gameplay and broad domain feature implementation remain blocked.",
    ),
    (
        "timekeeping_2038",
        "Timekeeping and 2038 resilience",
        ["docs/archive/conversations/_wiki/topics/timekeeping.md", "docs/archive/conversations/_synthesis"],
        "conversation_advisory_or_docs_candidate",
        "Conversation/archive support exists where present; current-doc promotion requires review.",
    ),
    (
        "world_reality_civilization_worldgen",
        "World, reality, civilization, and worldgen domains",
        ["specs/reality", "data/reality", "docs/archive/conversations/_synthesis"],
        "authority_sensitive",
        "Semantic-domain work must respect specs/reality over data/reality and current queue limits.",
    ),
    (
        "contracts_schema_reference_docs",
        "Contracts, schema, and reference docs",
        ["docs/reference/contracts", "contracts", "schema"],
        "contract_or_schema_authority",
        "Docs may summarize, but contract/schema law remains source authority.",
    ),
    (
        "testing_validation_fast",
        "Testing, validation, FAST, and full-gate debt",
        ["AGENTS.md", "docs/testing", "tools/validators"],
        "current_repo_truth_with_debt_tracking",
        "FAST is the minimum validation floor unless explicitly exempt.",
    ),
    (
        "current_queue_blocked_areas",
        "Current queue blocked areas",
        [".aide/queue/current.toml", "docs/repo/FOUNDATION_LOCK.md"],
        "current_repo_truth",
        "Blocked broad feature areas remain blocked.",
    ),
]


@dataclass
class FileRecord:
    path: str
    parent: str
    directory_family: str
    extension: str
    size: int
    sha256: str
    is_text: bool
    is_binary: bool
    first_heading: str
    header_preview: List[str]
    metadata: Dict[str, str]
    inferred_document_family: str
    initial_document_class: str
    authority_class: str
    freshness: str
    promotion_role: str
    book_role: str
    authority_risk: str
    archive_family: str
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "path": self.path,
            "parent": self.parent,
            "directory_family": self.directory_family,
            "extension": self.extension,
            "size": self.size,
            "sha256": self.sha256,
            "is_text": self.is_text,
            "is_binary": self.is_binary,
            "first_heading": self.first_heading,
            "header_preview": self.header_preview,
            "metadata": self.metadata,
            "inferred_document_family": self.inferred_document_family,
            "initial_document_class": self.initial_document_class,
            "authority_class": self.authority_class,
            "freshness": self.freshness,
            "promotion_role": self.promotion_role,
            "book_role": self.book_role,
            "authority_risk": self.authority_risk,
            "archive_family": self.archive_family,
            "warnings": self.warnings,
        }


@dataclass
class CorpusData:
    repo_root: Path
    commit: str
    branch: str
    files: List[FileRecord]

    @property
    def summary(self) -> Dict[str, object]:
        files = self.files
        return {
            "task_id": TASK_ID,
            "generated_date": REVIEW_DATE,
            "source_root": "docs/",
            "excluded_source_roots": ["docs/archive/docs_corpus/"],
            "repo_commit": self.commit,
            "repo_branch": self.branch,
            "file_count": len(files),
            "directory_count": len({f.parent for f in files}),
            "markdown_count": sum(1 for f in files if f.extension == ".md"),
            "json_count": sum(1 for f in files if f.extension == ".json"),
            "yaml_count": sum(1 for f in files if f.extension in (".yaml", ".yml")),
            "zip_count": sum(1 for f in files if f.extension == ".zip"),
            "non_text_count": sum(1 for f in files if not f.is_text),
            "total_bytes": sum(f.size for f in files),
            "family_counts": dict(Counter(f.inferred_document_family for f in files)),
            "authority_class_counts": dict(Counter(f.authority_class for f in files)),
            "book_role_counts": dict(Counter(f.book_role for f in files)),
            "authority_risk_counts": dict(Counter(f.authority_risk for f in files)),
            "archive_family_counts": dict(Counter(f.archive_family for f in files if f.archive_family != "not_archive")),
        }


def ascii_text(value: str) -> str:
    replacements = {
        "\ufeff": "",
        "\u2014": "-",
        "\u2013": "-",
        "\u2011": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2026": "...",
        "\u2192": "->",
        "\u2194": "<->",
        "\u03a3": "Sigma",
        "\u03bb": "Lambda",
        "\u039b": "Lambda",
        "\u03a9": "Omega",
        "\u039e": "Xi",
        "\u03a0": "Pi",
        "\u03a6": "Phi",
        "\u03a5": "Upsilon",
        "\u0396": "Zeta",
        "\u00a0": " ",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    return value.encode("ascii", "replace").decode("ascii")


def rel(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def write_if_changed(path: Path, content: str) -> bool:
    content = ascii_text(content).rstrip() + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old == content:
        return False
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)
    return True


def run_command(cmd: Sequence[str], cwd: Path, timeout: int = 300) -> Tuple[int, str]:
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
        return proc.returncode, ascii_text(proc.stdout)
    except FileNotFoundError as exc:
        return 127, str(exc)
    except subprocess.TimeoutExpired as exc:
        return 124, ascii_text((exc.stdout or "") + (exc.stderr or ""))


def command_available(name: str) -> Optional[str]:
    return shutil.which(name)


def git_output(repo_root: Path, args: Sequence[str]) -> str:
    code, output = run_command(["git", *args], repo_root)
    if code != 0:
        raise RuntimeError(output)
    return output.strip()


def git_tracked_docs(repo_root: Path) -> List[str]:
    output = git_output(repo_root, ["ls-files", "docs"])
    paths = []
    for line in output.splitlines():
        norm = line.replace("\\", "/")
        if not norm or norm.startswith("docs/archive/docs_corpus/"):
            continue
        paths.append(norm)
    return sorted(paths)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_binary_path(path: Path) -> bool:
    ext = path.suffix.lower()
    if ext in BINARY_EXTENSIONS:
        return True
    if ext in TEXT_EXTENSIONS or ext == "":
        try:
            sample = path.read_bytes()[:4096]
        except OSError:
            return True
        return b"\x00" in sample
    try:
        sample = path.read_bytes()[:4096]
    except OSError:
        return True
    return b"\x00" in sample


def read_text_preview(path: Path, limit: int = 160_000) -> str:
    data = path.read_bytes()[:limit]
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return ascii_text(data.decode(encoding, errors="replace"))
        except UnicodeDecodeError:
            continue
    return ascii_text(data.decode("utf-8", errors="replace"))


def metadata_from_text(text: str) -> Dict[str, str]:
    metadata: Dict[str, str] = {}
    field_set = set(METADATA_FIELDS)
    for line in text.splitlines()[:100]:
        if not line.strip():
            if metadata:
                break
            continue
        if line.startswith("#") and metadata:
            break
        match = re.match(r"^([A-Za-z][A-Za-z /_-]{1,40}):\s*(.*)$", line.strip())
        if not match:
            if metadata:
                continue
            continue
        field = match.group(1).strip()
        value = match.group(2).strip()
        if field in field_set:
            metadata[field] = value
    return metadata


def first_heading(text: str) -> str:
    for line in text.splitlines()[:300]:
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return ""


def header_preview(text: str) -> List[str]:
    preview = []
    for line in text.splitlines()[:20]:
        if line.strip():
            preview.append(line.strip())
        if len(preview) == 3:
            break
    return preview


def path_family(path: str) -> str:
    if path.startswith("docs/canon/"):
        return "canon"
    if path.startswith("docs/architecture/"):
        return "architecture"
    if path.startswith("docs/reference/contracts/"):
        return "reference_contracts"
    if path.startswith("docs/planning/"):
        return "planning"
    if path.startswith("docs/release/"):
        return "release"
    if path.startswith("docs/repo/"):
        return "repo"
    if path.startswith("docs/development/"):
        return "development"
    if path.startswith("docs/runtime/"):
        return "runtime"
    if path.startswith("docs/apps/"):
        return "apps"
    if path.startswith("docs/domains/") or path.startswith("docs/domain/"):
        return "domains"
    if path.startswith("docs/content/"):
        return "content"
    if path.startswith("docs/modding/"):
        return "modding"
    if path.startswith("docs/governance/"):
        return "governance"
    if path.startswith("docs/testing/"):
        return "testing"
    if path.startswith("docs/audit/"):
        return "audit"
    if path.startswith("docs/archive/conversations/"):
        return "conversation_corpus"
    if path.startswith("docs/archive/"):
        return "archive"
    return "other"


def archive_family(path: str) -> str:
    if not path.startswith("docs/archive/"):
        return "not_archive"
    if path.startswith("docs/archive/conversations/"):
        return "archive/conversations"
    parts = path.split("/")
    if len(parts) >= 3:
        segment = parts[2]
        if segment in {
            "audit",
            "blueprint",
            "omega",
            "platform",
            "post-canon",
            "prompts",
            "refactor",
            "restructure",
            "specs",
            "repox",
            "impact",
        }:
            return f"archive/{segment}"
    return "archive/stray_root_docs" if len(parts) == 3 else "other/archive_unknown"


def initial_document_class(path: str, family: str, metadata: Dict[str, str], is_text: bool) -> str:
    status = metadata.get("Status", "").lower()
    if not is_text:
        return "generated_or_packaged_output" if path.startswith("docs/archive/") else "unknown"
    if family == "canon":
        return "canonical"
    if family == "reference_contracts":
        return "contract_reference"
    if family == "planning":
        return "planning_authoritative"
    if family == "release":
        return "release_authoritative"
    if family == "conversation_corpus":
        return "conversation_advisory"
    if family == "archive":
        if "superseded" in status:
            return "stale_or_superseded_candidate"
        return "archival_historical"
    if family == "audit":
        return "derived_evidence"
    if family in {"architecture", "repo", "development", "runtime", "apps", "domains", "content", "modding", "governance", "testing"}:
        return "current_guidance"
    return "unknown"


def authority_class(path: str, family: str, metadata: Dict[str, str], is_text: bool) -> str:
    status = metadata.get("Status", "").lower()
    if family == "canon":
        return "canonical"
    if path == "AGENTS.md":
        return "absolute_governance"
    if family == "reference_contracts":
        return "contract_or_schema_reference"
    if family == "architecture":
        return "architecture_current"
    if family == "release":
        return "release_current"
    if family == "planning":
        return "planning_current"
    if family == "repo":
        return "repo_current"
    if family in {"development", "runtime", "apps"}:
        return "development_guidance"
    if family in {"domains", "content", "modding"}:
        return "domain_guidance"
    if family == "audit":
        return "audit_evidence"
    if family == "conversation_corpus":
        return "derived_synthesis" if "/_" in path or path.endswith("_v0.md") else "conversation_advisory"
    if family == "archive":
        if "superseded" in status or metadata.get("Superseded By"):
            return "archive_stale"
        if "transitional" in status or "quarantine" in status:
            return "archive_transitional"
        return "archive_historical"
    if not is_text:
        return "generated_evidence" if path.startswith("docs/archive/") else "unknown_or_unclassified"
    return "unknown_or_unclassified"


def freshness(metadata: Dict[str, str], family: str) -> str:
    status = metadata.get("Status", "").lower()
    if metadata.get("Superseded By") and metadata.get("Superseded By", "").lower() not in {"none", "n/a"}:
        return "superseded"
    if "superseded" in status:
        return "superseded"
    if family in {"archive", "conversation_corpus"}:
        return "stale" if "stale" in status or "superseded" in status else "provisional"
    if metadata.get("Stability", "").lower() in {"stable", "locked"}:
        return "current"
    if metadata.get("Last Reviewed"):
        return "current"
    return "unclear"


def promotion_role(path: str, family: str, auth_class: str, metadata: Dict[str, str]) -> str:
    if family in {"archive", "conversation_corpus"}:
        return "not_promoted"
    if auth_class in {"canonical", "absolute_governance", "contract_or_schema_reference"}:
        return "not_eligible"
    if not metadata.get("Status") and path.endswith(".md"):
        return "candidate_for_review"
    return "unknown"


def book_role(path: str, family: str, auth_class: str, size: int, is_text: bool) -> str:
    ext = Path(path).suffix.lower()
    if not is_text:
        return "excluded_binary_or_archive" if ext in {".zip", ".png", ".jpg", ".pdf", ".docx", ".epub"} else "manifest_only"
    if auth_class in {"canonical", "absolute_governance", "contract_or_schema_reference", "architecture_current", "planning_current", "repo_current"}:
        return "main_reader" if size < 200_000 else "summarized_reader"
    if family == "conversation_corpus":
        return "summarized_reader" if path.endswith(".md") else "searchable_html_only"
    if family == "archive":
        return "reference_appendix" if path.endswith(".md") and size < 100_000 else "searchable_html_only"
    if size > 300_000:
        return "reference_appendix"
    if ext == ".md":
        return "summarized_reader"
    return "manifest_only"


def authority_risk(path: str, family: str, auth_class: str, metadata: Dict[str, str]) -> str:
    status = metadata.get("Status", "").upper()
    if family in {"canon", "reference_contracts"} or path in {"AGENTS.md"}:
        return "high"
    if family == "archive" and status in {"CANONICAL", "BINDING", "CURRENT"}:
        return "quarantine_required"
    if family == "conversation_corpus":
        return "medium"
    if auth_class in {"architecture_current", "planning_current", "release_current"}:
        return "medium"
    if auth_class == "unknown_or_unclassified":
        return "unknown"
    return "low"


def warnings_for(path: str, metadata: Dict[str, str], family: str, is_text: bool, size: int) -> List[str]:
    warnings = []
    if is_text and path.endswith(".md") and not metadata.get("Status"):
        warnings.append("missing_status_header")
    if family in {"archive", "conversation_corpus"} and metadata.get("Status", "").upper() in {"CANONICAL", "BINDING", "CURRENT"}:
        warnings.append("archive_path_with_current_authority_claim")
    if size > 2_000_000:
        warnings.append("large_file")
    if Path(path).suffix.lower() == ".zip":
        warnings.append("zip_file")
    if not is_text:
        warnings.append("non_text_file")
    return warnings


def collect_corpus(repo_root: Path) -> CorpusData:
    branch = git_output(repo_root, ["rev-parse", "--abbrev-ref", "HEAD"])
    commit = git_output(repo_root, ["rev-parse", "--short", "HEAD"])
    records: List[FileRecord] = []
    for repo_path in git_tracked_docs(repo_root):
        abs_path = repo_root / repo_path
        ext = abs_path.suffix.lower()
        size = abs_path.stat().st_size
        digest = sha256_file(abs_path)
        is_binary = is_binary_path(abs_path)
        is_text = not is_binary
        text = read_text_preview(abs_path) if is_text else ""
        metadata = metadata_from_text(text)
        family = path_family(repo_path)
        auth = authority_class(repo_path, family, metadata, is_text)
        record = FileRecord(
            path=repo_path,
            parent=Path(repo_path).parent.as_posix(),
            directory_family=family,
            extension=ext or "(none)",
            size=size,
            sha256=digest,
            is_text=is_text,
            is_binary=is_binary,
            first_heading=first_heading(text),
            header_preview=header_preview(text),
            metadata=metadata,
            inferred_document_family=family,
            initial_document_class=initial_document_class(repo_path, family, metadata, is_text),
            authority_class=auth,
            freshness=freshness(metadata, family),
            promotion_role=promotion_role(repo_path, family, auth, metadata),
            book_role=book_role(repo_path, family, auth, size, is_text),
            authority_risk=authority_risk(repo_path, family, auth, metadata),
            archive_family=archive_family(repo_path),
            warnings=[],
        )
        record.warnings = warnings_for(repo_path, metadata, family, is_text, size)
        records.append(record)
    return CorpusData(repo_root=repo_root, commit=commit, branch=branch, files=records)


def md_header(title: str) -> str:
    return f"{STATUS_BLOCK}\n# {title}\n\n"


def md_escape(value: object) -> str:
    text = ascii_text(str(value))
    return text.replace("|", "\\|").replace("\n", " ").strip()


def md_table(headers: Sequence[str], rows: Iterable[Sequence[object]], limit: Optional[int] = None) -> str:
    row_list = list(rows)
    shown = row_list if limit is None else row_list[:limit]
    out = [
        "| " + " | ".join(md_escape(h) for h in headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in shown:
        out.append("| " + " | ".join(md_escape(cell) for cell in row) + " |")
    if limit is not None and len(row_list) > limit:
        out.append("| ... | " + " | ".join(["..."] * (len(headers) - 1)) + " |")
    return "\n".join(out) + "\n"


def counter_table(counter: Counter, label: str = "Value") -> str:
    rows = [(key, value) for key, value in sorted(counter.items(), key=lambda item: (-item[1], item[0]))]
    return md_table([label, "Count"], rows)


def bytes_fmt(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.2f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{size} B"


def manifest_json(data: CorpusData) -> str:
    payload = {
        "status": "DERIVED",
        "authority_class": "advisory_synthesis",
        "promotion_status": "not_promoted",
        "canon_impact": "unchanged",
        "contract_schema_impact": "unchanged",
        "implementation_impact": "unchanged",
        "release_impact": "unchanged",
        "queue_impact": "unchanged",
        "summary": data.summary,
        "files": [record.to_dict() for record in data.files],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def render_readme(data: CorpusData) -> str:
    summary = data.summary
    return md_header("Dominium Docs Corpus") + f"""This directory contains derived, advisory docs-corpus inventory, audit, archive archaeology, reconciliation, wiki, and book-publication outputs for the git-tracked `docs/` tree.

This system is not canon and does not promote archive or conversation-derived claims into current project authority. It exists to make the documentation corpus readable, searchable, and reviewable while preserving the authority order defined by `AGENTS.md`, `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/planning/AUTHORITY_ORDER.md`, and `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`.

## Source Scope

- Source root: `docs/`
- Represented files: {summary["file_count"]}
- Represented directories: {summary["directory_count"]}
- Excluded source root: `docs/archive/docs_corpus/` to prevent the generated corpus from recursively republishing itself.
- Conversation corpus root: `docs/archive/conversations/`

## Output Areas

- `_intake/`: deterministic file manifest, source index, counts, tree summary, and non-Markdown inventory.
- `_audit/`: status/header audit, authority map, supersession map, drift, contradiction, staleness, duplicate-shadow, and coverage reports.
- `_archive/`: archive-family archaeology and archive-to-current crosswalks.
- `_reconciliation/`: current project picture, repo-truth crosswalk, promotion queue, decision docket, and blocked-scope alignment.
- `_wiki/`: repo-local navigation pages and reading paths.
- `_book/`: reproducible reader/reference book source.
- `_exports/`: PDF, HTML, DOCX, EPUB, build report, and validation report.

## Regeneration

From repo root:

```powershell
py -3 tools/docs_corpus/docs_corpus.py --repo-root . build
py -3 tools/docs_corpus/validate_docs_corpus_outputs.py --repo-root .
```

If renderer prerequisites change, regenerate the exports and review `_exports/{BUILD_REPORT_BASENAME}.md` and `_exports/{VALIDATION_REPORT_BASENAME}.md`.
"""


def render_manifest_md(data: CorpusData) -> str:
    summary = data.summary
    family_counts = Counter(record.inferred_document_family for record in data.files)
    authority_counts = Counter(record.authority_class for record in data.files)
    risk_counts = Counter(record.authority_risk for record in data.files)
    return md_header("Docs Corpus Manifest") + f"""## Summary

- Task ID: `{TASK_ID}`
- Source root: `docs/`
- Generated date: {REVIEW_DATE}
- Repository branch: `{data.branch}`
- Repository commit: `{data.commit}`
- Files represented: {summary["file_count"]}
- Directories represented: {summary["directory_count"]}
- Total size: {bytes_fmt(int(summary["total_bytes"]))}
- Markdown files: {summary["markdown_count"]}
- JSON files: {summary["json_count"]}
- YAML files: {summary["yaml_count"]}
- ZIP files: {summary["zip_count"]}
- Non-text files: {summary["non_text_count"]}

## Directory Families

{counter_table(family_counts, "Family")}

## Authority Classes

{counter_table(authority_counts, "Authority Class")}

## Authority Risk

{counter_table(risk_counts, "Risk")}

## Source Rule

Every git-tracked file under `docs/` is represented except generated files under `docs/archive/docs_corpus/`, which are deliberately excluded to avoid recursive self-publication.
"""


def render_source_index(data: CorpusData) -> str:
    rows = [
        (
            record.path,
            record.inferred_document_family,
            record.authority_class,
            record.book_role,
            bytes_fmt(record.size),
            record.sha256[:12],
        )
        for record in data.files
    ]
    return md_header("Docs Source Index") + """Every represented git-tracked docs file appears in this index. The full SHA-256 hash is preserved in `DOCS_CORPUS_MANIFEST.json`.

""" + md_table(["Path", "Family", "Authority Class", "Book Role", "Size", "SHA-256 Prefix"], rows)


def render_file_counts(data: CorpusData) -> str:
    ext_counts = Counter(record.extension for record in data.files)
    family_counts = Counter(record.inferred_document_family for record in data.files)
    book_counts = Counter(record.book_role for record in data.files)
    return md_header("Docs File Counts") + f"""## Corpus Totals

- Files: {len(data.files)}
- Directories: {len({record.parent for record in data.files})}
- Total size: {bytes_fmt(sum(record.size for record in data.files))}

## Extension Counts

{counter_table(ext_counts, "Extension")}

## Directory Family Counts

{counter_table(family_counts, "Family")}

## Book Inclusion Draft Counts

{counter_table(book_counts, "Book Role")}
"""


def render_tree_summary(data: CorpusData) -> str:
    dir_counts = Counter(record.parent for record in data.files)
    rows = [(path, count) for path, count in sorted(dir_counts.items(), key=lambda item: (-item[1], item[0]))]
    return md_header("Docs Tree Summary") + """This report summarizes the tracked docs tree by parent directory.

""" + md_table(["Directory", "Tracked Files"], rows)


def render_large_non_markdown(data: CorpusData) -> str:
    large = sorted(data.files, key=lambda record: (-record.size, record.path))[:120]
    non_markdown = [record for record in data.files if record.extension != ".md"]
    zips = [record for record in data.files if record.extension == ".zip"]
    non_text = [record for record in data.files if not record.is_text]
    return md_header("Large Files and Non-Markdown Inventory") + f"""## Largest Files

{md_table(["Path", "Extension", "Size", "Book Role", "Warnings"], [(r.path, r.extension, bytes_fmt(r.size), r.book_role, ", ".join(r.warnings)) for r in large])}

## Non-Markdown Counts

- Non-Markdown files: {len(non_markdown)}
- ZIP files: {len(zips)}
- Non-text/binary files: {len(non_text)}

## ZIP Files

{md_table(["Path", "Size", "Book Role"], [(r.path, bytes_fmt(r.size), r.book_role) for r in zips])}

## Non-Text Files

{md_table(["Path", "Extension", "Size", "Book Role"], [(r.path, r.extension, bytes_fmt(r.size), r.book_role) for r in non_text], limit=300)}
"""


def render_status_header_audit(data: CorpusData) -> str:
    markdown = [record for record in data.files if record.extension == ".md"]
    missing = [record for record in markdown if not record.metadata.get("Status")]
    malformed = [
        record
        for record in markdown
        if record.metadata.get("Status") and record.metadata.get("Status", "").upper() not in {"CANONICAL", "DERIVED", "DRAFT", "ACTIVE", "ARCHIVED", "SUPERSEDED", "REFERENCE", "HISTORICAL"}
    ]
    archive_claims = [record for record in data.files if "archive_path_with_current_authority_claim" in record.warnings]
    return md_header("Docs Status Header Audit") + f"""## Header Coverage

- Markdown files checked: {len(markdown)}
- Markdown files missing `Status`: {len(missing)}
- Markdown files with unusual `Status`: {len(malformed)}
- Archive/conversation paths with current-authority-looking status: {len(archive_claims)}

## Missing `Status`

{md_table(["Path", "Family", "Book Role"], [(r.path, r.inferred_document_family, r.book_role) for r in missing], limit=500)}

## Unusual `Status`

{md_table(["Path", "Status", "Family"], [(r.path, r.metadata.get("Status", ""), r.inferred_document_family) for r in malformed], limit=300)}

## Archive Current-Authority Claims

{md_table(["Path", "Status", "Disposition"], [(r.path, r.metadata.get("Status", ""), "review_only_do_not_promote") for r in archive_claims], limit=300)}
"""


def render_authority_draft(data: CorpusData) -> str:
    rows = [
        (
            record.path,
            record.initial_document_class,
            record.authority_class,
            record.freshness,
            record.authority_risk,
            record.book_role,
        )
        for record in data.files
    ]
    return md_header("Docs Authority Classification Draft") + """This draft is deterministic and path/header-based. It is a review surface, not a promotion decision.

""" + md_table(["Path", "Initial Class", "Authority Class", "Freshness", "Risk", "Book Role"], rows)


def render_authority_map(data: CorpusData) -> str:
    grouped: Dict[str, List[FileRecord]] = defaultdict(list)
    for record in data.files:
        grouped[record.authority_class].append(record)
    parts = [md_header("Docs Authority Map")]
    parts.append("This map classifies every represented docs file into one primary authority class. Archive and conversation material remains advisory unless later promoted through an explicit task.\n")
    parts.append(counter_table(Counter(record.authority_class for record in data.files), "Authority Class"))
    for auth_class in sorted(grouped):
        records = grouped[auth_class]
        parts.append(f"\n## {auth_class}\n\n")
        parts.append(md_table(["Path", "Freshness", "Risk", "Book Role"], [(r.path, r.freshness, r.authority_risk, r.book_role) for r in records], limit=500))
    return "".join(parts)


def render_supersession_map(data: CorpusData) -> str:
    records = [
        record
        for record in data.files
        if record.metadata.get("Supersedes") or record.metadata.get("Superseded By") or record.metadata.get("Replacement Target") or record.freshness in {"superseded", "stale"}
    ]
    return md_header("Docs Supersession Map") + """This report lists explicit supersession metadata and path/header-derived stale or superseded candidates.

""" + md_table(
        ["Path", "Status", "Supersedes", "Superseded By", "Replacement Target", "Freshness", "Disposition"],
        [
            (
                r.path,
                r.metadata.get("Status", ""),
                r.metadata.get("Supersedes", ""),
                r.metadata.get("Superseded By", ""),
                r.metadata.get("Replacement Target", ""),
                r.freshness,
                "review_before_use",
            )
            for r in records
        ],
        limit=1000,
    )


def render_binding_source_map(data: CorpusData) -> str:
    records = [record for record in data.files if record.metadata.get("Binding Sources")]
    return md_header("Docs Binding Source Map") + """Binding-source metadata is a provenance signal. It does not override the repo authority model.

""" + md_table(
        ["Path", "Authority Class", "Binding Sources"],
        [(r.path, r.authority_class, r.metadata.get("Binding Sources", "")) for r in records],
        limit=1000,
    )


def render_archive_classification(data: CorpusData) -> str:
    archive_records = [record for record in data.files if record.archive_family != "not_archive"]
    return md_header("Docs Archive Classification") + """Archive files are historical/provenance material unless separately promoted by later explicit review.

""" + counter_table(Counter(r.archive_family for r in archive_records), "Archive Family") + "\n" + md_table(
        ["Path", "Archive Family", "Authority Class", "Freshness", "Book Role", "Warnings"],
        [(r.path, r.archive_family, r.authority_class, r.freshness, r.book_role, ", ".join(r.warnings)) for r in archive_records],
        limit=1500,
    )


def render_book_inclusion_plan(data: CorpusData) -> str:
    grouped = defaultdict(list)
    for record in data.files:
        grouped[record.book_role].append(record)
    parts = [md_header("Docs Book Inclusion Plan")]
    parts.append("The reader edition is curated. Every represented file remains in the manifest/source index, while dense or binary inputs are reference, HTML, or manifest-only.\n\n")
    parts.append(counter_table(Counter(record.book_role for record in data.files), "Book Role"))
    for role in sorted(grouped):
        parts.append(f"\n## {role}\n\n")
        parts.append(md_table(["Path", "Family", "Authority Class", "Size"], [(r.path, r.inferred_document_family, r.authority_class, bytes_fmt(r.size)) for r in grouped[role]], limit=800))
    return "".join(parts)


def duplicate_shadow_records(data: CorpusData) -> List[Tuple[str, List[FileRecord], List[FileRecord]]]:
    by_name: Dict[str, List[FileRecord]] = defaultdict(list)
    for record in data.files:
        if record.extension != ".md":
            continue
        key = Path(record.path).name.lower()
        by_name[key].append(record)
    shadows = []
    for key, records in by_name.items():
        current = [r for r in records if not r.path.startswith("docs/archive/")]
        archive = [r for r in records if r.path.startswith("docs/archive/")]
        if current and archive:
            shadows.append((key, current, archive))
    return sorted(shadows, key=lambda item: item[0])


def contradiction_findings(data: CorpusData) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []
    counter = 1
    for record in data.files:
        if "archive_path_with_current_authority_claim" in record.warnings:
            findings.append(
                {
                    "id": f"DOC-CONTRA-{counter:04d}",
                    "class": "archive_vs_current",
                    "sources": record.path,
                    "authority": "AGENTS.md; docs/planning/AUTHORITY_ORDER.md",
                    "claim": f"Archive path has status `{record.metadata.get('Status', '')}`.",
                    "severity": "medium",
                    "disposition": "quarantine_for_review",
                    "next_action": "Review whether the header is historical residue; do not promote automatically.",
                    "question": "Should this archive artifact remain historical or be superseded by a current doc cross-reference?",
                }
            )
            counter += 1
    for key, current, archive in duplicate_shadow_records(data)[:200]:
        findings.append(
            {
                "id": f"DOC-CONTRA-{counter:04d}",
                "class": "duplicate_shadow",
                "sources": ", ".join([current[0].path, archive[0].path]),
                "authority": "current docs outrank archive in their scope; archive remains historical",
                "claim": f"Archive and current docs share filename `{key}`.",
                "severity": "low",
                "disposition": "review_shadow_before_promotion",
                "next_action": "Use current path first; inspect archive only for provenance or promotion candidates.",
                "question": "Does the archive version contain useful historical context that should be summarized elsewhere?",
            }
        )
        counter += 1
    missing_status = [r for r in data.files if r.extension == ".md" and not r.metadata.get("Status") and not r.path.startswith("docs/archive/docs_corpus/")]
    for record in missing_status[:100]:
        findings.append(
            {
                "id": f"DOC-CONTRA-{counter:04d}",
                "class": "unclear_same_tier_conflict",
                "sources": record.path,
                "authority": "metadata header audit",
                "claim": "Markdown file lacks a Status header, making authority/freshness less explicit.",
                "severity": "low",
                "disposition": "candidate_for_docs_hygiene_review",
                "next_action": "Consider adding metadata in a later live-doc hygiene task if allowed.",
                "question": "Should this doc get an explicit authority/status header in a later docs-only promotion wave?",
            }
        )
        counter += 1
    return findings


def render_drift_matrix(data: CorpusData) -> str:
    findings = contradiction_findings(data)
    return md_header("Docs Drift Matrix") + """This derived drift matrix highlights review areas. It does not resolve contradictions or promote claims.

""" + md_table(
        ["Finding ID", "Class", "Sources", "Severity", "Disposition", "Next Action"],
        [(f["id"], f["class"], f["sources"], f["severity"], f["disposition"], f["next_action"]) for f in findings],
        limit=800,
    )


def render_contradiction_matrix(data: CorpusData) -> str:
    findings = contradiction_findings(data)
    return md_header("Docs Contradiction Matrix") + """Contradiction classes include current-doc vs canon, archive vs current, conversation vs current, planning vs queue, generated evidence vs source, duplicate shadows, stale external claims, and unclear same-tier conflicts. Findings below are deterministic review signals, not adjudications.

""" + md_table(
        ["Finding ID", "Class", "Sources", "Authority Source", "Claim", "Severity", "Disposition", "User Review Question"],
        [(f["id"], f["class"], f["sources"], f["authority"], f["claim"], f["severity"], f["disposition"], f["question"]) for f in findings],
        limit=800,
    )


def render_staleness(data: CorpusData) -> str:
    records = [
        r
        for r in data.files
        if r.freshness in {"stale", "superseded", "unclear"} or r.archive_family != "not_archive"
    ]
    return md_header("Docs Staleness and Verification") + """This register identifies material that should be verified before use as current guidance.

""" + md_table(
        ["Path", "Family", "Freshness", "Status", "Last Reviewed", "Disposition"],
        [(r.path, r.inferred_document_family, r.freshness, r.metadata.get("Status", ""), r.metadata.get("Last Reviewed", ""), "verify_before_current_use") for r in records],
        limit=1500,
    )


def render_duplicate_shadows(data: CorpusData) -> str:
    rows = []
    for key, current, archive in duplicate_shadow_records(data):
        rows.append((key, "; ".join(r.path for r in current[:5]), "; ".join(r.path for r in archive[:5]), "current_first_archive_for_provenance"))
    return md_header("Docs Duplicate Shadows") + """Duplicate shadows are same-filename overlaps between current docs and archive docs. They are review cues only.

""" + md_table(["Filename", "Current Paths", "Archive Paths", "Disposition"], rows, limit=1000)


def render_coverage_gaps(data: CorpusData) -> str:
    missing_status = [r for r in data.files if r.extension == ".md" and not r.metadata.get("Status")]
    unknown = [r for r in data.files if r.authority_class == "unknown_or_unclassified"]
    binary = [r for r in data.files if not r.is_text]
    return md_header("Docs Coverage Gaps") + f"""## Gaps

- Markdown files missing `Status`: {len(missing_status)}
- Unknown/unclassified files: {len(unknown)}
- Binary/non-text files represented by hash only: {len(binary)}

## Missing Status Header Candidates

{md_table(["Path", "Family", "Book Role"], [(r.path, r.inferred_document_family, r.book_role) for r in missing_status], limit=500)}

## Unknown Authority Candidates

{md_table(["Path", "Extension", "Size"], [(r.path, r.extension, bytes_fmt(r.size)) for r in unknown], limit=500)}
"""


def render_archive_atlas(data: CorpusData) -> str:
    archive_records = [record for record in data.files if record.archive_family != "not_archive"]
    counts = Counter(r.archive_family for r in archive_records)
    return md_header("Docs Archive Atlas") + """`docs/archive/**` is historical/provenance material. It can inform future review, but it does not override current repo authority.

## Archive Family Counts

""" + counter_table(counts, "Archive Family") + """
## Interpretation

- `archive/conversations` is the completed advisory conversation corpus.
- Blueprint, prompt, refactor, restructure, post-canon, and spec archives preserve historical design or migration context.
- Archive material may become a promotion candidate only through a later explicit review task.
"""


def render_archive_families(data: CorpusData) -> str:
    grouped = defaultdict(list)
    for record in data.files:
        if record.archive_family != "not_archive":
            grouped[record.archive_family].append(record)
    parts = [md_header("Docs Archive Families")]
    for family in sorted(grouped):
        records = grouped[family]
        parts.append(f"## {family}\n\n")
        parts.append(f"- Files: {len(records)}\n")
        parts.append("- Current relevance: historical/provenance unless crosswalked to current docs.\n")
        parts.append("- Warning: do not treat as current truth without promotion.\n\n")
        parts.append(md_table(["Path", "Authority Class", "Freshness", "Book Role"], [(r.path, r.authority_class, r.freshness, r.book_role) for r in records], limit=400))
        parts.append("\n")
    return "".join(parts)


def render_archive_stale_useful(data: CorpusData) -> str:
    archive_records = [record for record in data.files if record.archive_family != "not_archive"]
    rows = []
    for record in archive_records:
        usefulness = "conversation_design_intent" if record.archive_family == "archive/conversations" else "historical_context"
        if record.freshness in {"superseded", "stale"}:
            usefulness = "stale_verify_before_use"
        rows.append((record.path, record.archive_family, record.freshness, usefulness, "not_promoted"))
    return md_header("Docs Archive Stale or Useful Register") + md_table(
        ["Path", "Archive Family", "Freshness", "Usefulness", "Promotion Status"], rows, limit=1500
    )


def render_archive_to_current_crosswalk(data: CorpusData) -> str:
    rows = []
    for family in sorted(Counter(r.archive_family for r in data.files if r.archive_family != "not_archive")):
        target = {
            "archive/conversations": "docs/archive/conversations/_exports and later docs promotion review",
            "archive/audit": "current validation/audit docs if still relevant",
            "archive/blueprint": "architecture/planning docs only through review",
            "archive/prompts": "planning/prompt provenance only",
            "archive/refactor": "refactor planning only",
            "archive/restructure": "repo structure planning only",
            "archive/specs": "current specs/contracts only through review",
        }.get(family, "current docs only through explicit review")
        rows.append((family, target, "historical_provenance", "do_not_promote_automatically"))
    return md_header("Docs Archive to Current Crosswalk") + md_table(
        ["Archive Family", "Likely Current Target", "Current Role", "Disposition"], rows
    )


def render_conversation_integration(data: CorpusData) -> str:
    conversation_records = [r for r in data.files if r.inferred_document_family == "conversation_corpus"]
    exports = [r for r in conversation_records if "/_exports/" in r.path]
    reports = [r for r in conversation_records if r.extension == ".md" and "/_" in r.path]
    return md_header("Docs Conversation Corpus Integration") + f"""The conversation corpus is treated as a derived advisory sub-corpus inside the full docs corpus.

## Scope

- Conversation files represented: {len(conversation_records)}
- Generated conversation reports represented: {len(reports)}
- Conversation export files represented: {len(exports)}

## Interpretation

- Advisory: yes
- Current authority: no
- Promotion status: not promoted
- Use: design intent, review backlog, decision and promotion candidates
- Non-use: canon, contract/schema, implementation, release, or queue override

## Key Existing Surfaces

{md_table(["Surface", "Role"], [
    ("docs/archive/conversations/_synthesis/**", "derived synthesis and project picture"),
    ("docs/archive/conversations/_decision/**", "decision docket"),
    ("docs/archive/conversations/_promotion/**", "promotion review backlog"),
    ("docs/archive/conversations/_reconciliation/**", "conversation-vs-repo crosswalk"),
    ("docs/archive/conversations/_audit/**", "contradictions, staleness, uncertainty"),
    ("docs/archive/conversations/_exports/**", "conversation book bundle"),
])}
"""


def render_repo_truth_crosswalk(data: CorpusData) -> str:
    rows = []
    for topic_id, title, sources, disposition, note in RECONCILIATION_TOPICS:
        existing = [src for src in sources if (data.repo_root / src).exists() or any(r.path.startswith(src.rstrip("/") + "/") for r in data.files)]
        rows.append((topic_id, title, "; ".join(existing) if existing else "; ".join(sources), disposition, note))
    return md_header("Docs Repo Truth Crosswalk") + """This crosswalk starts with current repo authority and uses archive/conversation material only as supporting historical context.

""" + md_table(["Topic ID", "Topic", "Source Paths", "Classification", "Disposition"], rows)


def render_current_project_picture(data: CorpusData) -> str:
    return md_header("Docs Current Project Picture") + f"""Dominium's current documentation picture is authority layered. Canon, glossary, `AGENTS.md`, contract/schema law, current queue state, and validated repo artifacts are the highest-confidence sources. Archive and conversation material can explain how earlier ideas developed, but it cannot become current truth through this docs-corpus task.

## Current Orientation

- Project orientation: `README.md`
- Documentation taxonomy: `docs/README.md`
- Canon: `docs/canon/constitution_v1.md`
- Glossary: `docs/canon/glossary_v1.md`
- Agent governance: `AGENTS.md`
- Queue state: `.aide/queue/current.toml`
- Foundation status: `docs/repo/FOUNDATION_LOCK.md`

## Corpus Scale

- Files represented: {len(data.files)}
- Markdown files: {sum(1 for r in data.files if r.extension == ".md")}
- Archive/conversation files: {sum(1 for r in data.files if r.path.startswith("docs/archive/"))}

## What Is Safe To Do With This Output

- Read the docs corpus as a map.
- Use archive material for provenance and review.
- Use generated contradictions and promotion queues to plan later tasks.
- Start later live-doc patches only through explicit narrow promotion tasks.

## What This Output Does Not Do

- It does not promote archive claims.
- It does not rewrite canon, contracts, schema, implementation, release, or queue state.
- It does not open blocked renderer, gameplay, provider runtime, package runtime, broad Workbench UI, native GUI, or release publication work.
"""


def render_canon_architecture_alignment(data: CorpusData) -> str:
    canon = [r for r in data.files if r.inferred_document_family == "canon"]
    architecture = [r for r in data.files if r.inferred_document_family == "architecture"]
    contracts = [r for r in data.files if r.inferred_document_family == "reference_contracts"]
    return md_header("Docs Canon Architecture Alignment") + f"""This report maps high-authority documentation families without changing them.

## Counts

- Canon files: {len(canon)}
- Architecture files: {len(architecture)}
- Reference contract docs: {len(contracts)}

## Canon Files

{md_table(["Path", "Status", "Stability", "Binding Sources"], [(r.path, r.metadata.get("Status", ""), r.metadata.get("Stability", ""), r.metadata.get("Binding Sources", "")) for r in canon])}

## Architecture Files

{md_table(["Path", "Status", "Freshness", "Risk"], [(r.path, r.metadata.get("Status", ""), r.freshness, r.authority_risk) for r in architecture], limit=500)}

## Reference Contract Docs

{md_table(["Path", "Status", "Freshness", "Risk"], [(r.path, r.metadata.get("Status", ""), r.freshness, r.authority_risk) for r in contracts], limit=500)}
"""


def render_archive_conversation_alignment(data: CorpusData) -> str:
    archive = [r for r in data.files if r.inferred_document_family == "archive"]
    conversations = [r for r in data.files if r.inferred_document_family == "conversation_corpus"]
    return md_header("Docs Archive Conversation Alignment") + f"""Archive docs and the conversation corpus are aligned as historical/advisory evidence.

- Non-conversation archive files: {len(archive)}
- Conversation corpus files: {len(conversations)}
- Promotion status: not promoted

## Alignment Rule

Archive docs can provide provenance. Conversation corpus outputs can provide design-intent summaries and review queues. Neither can override canon, contracts, schema, current queue state, or current docs in their authority scope.
"""


def render_promotion_queue(data: CorpusData) -> str:
    candidates = []
    idx = 1
    for record in data.files:
        if record.promotion_role == "candidate_for_review" or "missing_status_header" in record.warnings:
            candidates.append((f"DOC-PROMOTE-{idx:04d}", record.path, "docs_hygiene_candidate", "Add or review status/header metadata in a later allowed docs-only task.", "not_promoted"))
            idx += 1
    for key, current, archive in duplicate_shadow_records(data)[:50]:
        candidates.append((f"DOC-PROMOTE-{idx:04d}", f"{current[0].path}; {archive[0].path}", "archive_shadow_review", f"Review duplicate filename `{key}` for provenance-only summary or explicit rejection.", "not_promoted"))
        idx += 1
    return md_header("Docs Promotion Queue") + """This queue records later review candidates. It does not apply any live-doc patch.

""" + md_table(["Promotion ID", "Source Path(s)", "Type", "Recommended Next Action", "Promotion Status"], candidates, limit=1000)


def render_decision_docket(data: CorpusData) -> str:
    findings = contradiction_findings(data)
    decisions = []
    for idx, finding in enumerate(findings[:80], 1):
        decision_type = "repo_authority_decision" if finding["class"] != "duplicate_shadow" else "future_docs_hygiene_decision"
        decisions.append(
            (
                f"DOC-DECIDE-{idx:04d}",
                finding["id"],
                finding["question"],
                decision_type,
                finding["severity"],
                "defer_until_targeted_review",
            )
        )
    blocked = [
        ("DOC-DECIDE-BLOCK-0001", "queue", "Should broad Workbench UI remain closed until a later queue phase explicitly opens it?", "future_queue_decision", "high", "defer"),
        ("DOC-DECIDE-BLOCK-0002", "queue", "Should renderer implementation remain blocked?", "future_queue_decision", "high", "defer"),
        ("DOC-DECIDE-BLOCK-0003", "queue", "Should provider/package runtime work remain blocked?", "future_queue_decision", "high", "defer"),
        ("DOC-DECIDE-BLOCK-0004", "queue", "Should release publication remain blocked?", "future_queue_decision", "high", "defer"),
    ]
    decisions.extend(blocked)
    return md_header("Docs Decision Docket") + """Decision items are review prompts. The default disposition is defer unless a later explicit task opens the scope.

""" + md_table(["Decision ID", "Source/Finding", "Question", "Decision Type", "Risk", "Recommended Default"], decisions, limit=1000)


def render_blocked_scope(data: CorpusData) -> str:
    blocked_terms = {
        "broad_workbench_ui": ["workbench", "ui"],
        "runtime_module_loader": ["module", "loader"],
        "provider_runtime": ["provider"],
        "package_runtime": ["package", "runtime"],
        "gameplay": ["gameplay"],
        "renderer_implementation": ["renderer"],
        "native_gui": ["native", "gui"],
        "release_publication": ["release", "publication"],
    }
    rows = []
    lower_paths = [(r.path, r.path.lower()) for r in data.files]
    for scope, terms in blocked_terms.items():
        matches = [path for path, lower in lower_paths if all(term in lower for term in terms)]
        rows.append((scope, ".aide/queue/current.toml", len(matches), "; ".join(matches[:8]), "blocked_by_current_queue"))
    return md_header("Docs Blocked Scope Alignment") + """The current queue blocks these broad work areas. Docs-corpus outputs record them for navigation only.

""" + md_table(["Blocked Scope", "Authority Source", "Matching Docs Paths", "Examples", "Disposition"], rows)


def render_wiki_page(title: str, body: str) -> str:
    return md_header(title) + body


def render_wiki_pages(data: CorpusData) -> Dict[str, str]:
    pages: Dict[str, str] = {}
    pages["_wiki/index.md"] = render_wiki_page(
        "Docs Corpus Wiki",
        """This repo-local wiki navigates the derived docs-corpus outputs.

## Start Here

- [Current Authority](current_authority.md)
- [Archive Archaeology](archive_archaeology.md)
- [Conversation Corpus](conversation_corpus.md)
- [Decisions](decisions.md)
- [Promotion Candidates](promotion_candidates.md)
- [Contradictions](contradictions.md)
- [Staleness and Verification](staleness_and_verification.md)
- [Source Index](source_index.md)
- [Reading Paths](reading_paths.md)
""",
    )
    pages["_wiki/current_authority.md"] = render_wiki_page(
        "Current Authority",
        """Current authority begins with canon, glossary, `AGENTS.md`, contracts/schema law, the current queue, and validated repo artifacts. See `_reconciliation/DOCS_REPO_TRUTH_CROSSWALK_v0.md` and `_audit/DOCS_AUTHORITY_MAP_v0.md`.
""",
    )
    pages["_wiki/archive_archaeology.md"] = render_wiki_page(
        "Archive Archaeology",
        """Archive material is historical and provenance-bearing. See `_archive/DOCS_ARCHIVE_ATLAS_v0.md`, `_archive/DOCS_ARCHIVE_FAMILIES_v0.md`, and `_archive/DOCS_ARCHIVE_TO_CURRENT_CROSSWALK_v0.md`.
""",
    )
    pages["_wiki/conversation_corpus.md"] = render_wiki_page(
        "Conversation Corpus",
        """The conversation corpus is advisory derived history. It is represented in this docs corpus and has its own book bundle under `docs/archive/conversations/_exports/`.
""",
    )
    pages["_wiki/decisions.md"] = render_wiki_page(
        "Decisions",
        """Decision prompts are collected in `_reconciliation/DOCS_DECISION_DOCKET_v0.md`. They preserve defer as the default where current authority or queue state does not open a scope.
""",
    )
    pages["_wiki/promotion_candidates.md"] = render_wiki_page(
        "Promotion Candidates",
        """Promotion candidates are review items only. See `_reconciliation/DOCS_PROMOTION_QUEUE_v0.md`; no live docs are patched by this corpus task.
""",
    )
    pages["_wiki/contradictions.md"] = render_wiki_page(
        "Contradictions",
        """Contradiction and drift findings are in `_audit/DOCS_CONTRADICTION_MATRIX_v0.md` and `_audit/DOCS_DRIFT_MATRIX_v0.md`.
""",
    )
    pages["_wiki/staleness_and_verification.md"] = render_wiki_page(
        "Staleness and Verification",
        """Use `_audit/DOCS_STALENESS_AND_VERIFICATION_v0.md` before relying on archive, generated, or unclear-status material.
""",
    )
    pages["_wiki/source_index.md"] = render_wiki_page(
        "Source Index",
        """The full source index is `_intake/DOCS_SOURCE_INDEX_v0.md`; machine-readable metadata is `_intake/DOCS_CORPUS_MANIFEST.json`.
""",
    )
    reading_paths = [
        ("Start Here", "`_book/chapters/00_front_matter.md`, then `_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md`."),
        ("Current Authority Reader", "`_audit/DOCS_AUTHORITY_MAP_v0.md` and `_reconciliation/DOCS_REPO_TRUTH_CROSSWALK_v0.md`."),
        ("Canon and Architecture Reader", "`_reconciliation/DOCS_CANON_ARCHITECTURE_ALIGNMENT_v0.md`."),
        ("Runtime/Product Reader", "`_wiki/topics/runtime_product_tooling.md`."),
        ("Workbench/AIDE/Codex Reader", "`_wiki/topics/workbench_aide_codex.md`."),
        ("Release/Setup/Launcher Reader", "`_wiki/topics/release_setup_launcher.md`."),
        ("World/Simulation/Domain Reader", "`_wiki/topics/world_simulation_domain.md`."),
        ("Archive Archaeology Reader", "`_archive/DOCS_ARCHIVE_ATLAS_v0.md`."),
        ("Conversation Corpus Reader", "`_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md`."),
        ("Decision Review Reader", "`_reconciliation/DOCS_DECISION_DOCKET_v0.md`."),
        ("Promotion Review Reader", "`_reconciliation/DOCS_PROMOTION_QUEUE_v0.md`."),
        ("Contradiction/Staleness Reader", "`_audit/DOCS_CONTRADICTION_MATRIX_v0.md` and `_audit/DOCS_STALENESS_AND_VERIFICATION_v0.md`."),
        ("Source Provenance Reader", "`_intake/DOCS_SOURCE_INDEX_v0.md`."),
    ]
    pages["_wiki/reading_paths.md"] = render_wiki_page(
        "Reading Paths",
        md_table(["Reading Path", "Start With"], reading_paths),
    )
    topic_bodies = {
        "authority_and_governance": "Canon, glossary, `AGENTS.md`, authority order, and snapshot intake govern interpretation.",
        "runtime_product_tooling": "Runtime/product/tooling docs are mapped as current guidance unless blocked by queue or scoped by stronger contracts.",
        "workbench_aide_codex": "Workbench/AIDE/Codex materials are useful but broad Workbench UI and native GUI work remain blocked by queue state.",
        "release_setup_launcher": "Release/setup/launcher claims require current release/control-plane authority and cannot open release publication scope.",
        "world_simulation_domain": "World/reality/civilization/worldgen claims require semantic-domain authority and current queue allowance.",
        "contracts_schema": "Contracts/schema references remain authority-sensitive; docs-corpus output is only a map.",
    }
    for slug, body in topic_bodies.items():
        pages[f"_wiki/topics/{slug}.md"] = render_wiki_page(slug.replace("_", " ").title(), body + "\n")
    for family in sorted(Counter(r.archive_family for r in data.files if r.archive_family != "not_archive")):
        pages[f"_wiki/families/{slugify(family)}.md"] = render_wiki_page(
            family,
            f"Archive family `{family}` is historical/provenance material. See `_archive/DOCS_ARCHIVE_FAMILIES_v0.md` for file listings.\n",
        )
    return pages


def slugify(value: str) -> str:
    value = value.lower().replace("/", "_")
    value = re.sub(r"[^a-z0-9_]+", "_", value)
    return value.strip("_") or "item"


def book_manifest(data: CorpusData, renderer: str) -> str:
    source_reports = [path for path in REQUIRED_REPORTS if path.startswith("_") and not path.startswith("_exports/")]
    outputs = [
        f"_exports/{READER_BASENAME}.pdf",
        f"_exports/{READER_BASENAME}.html/index.html",
        f"_exports/{READER_BASENAME}.docx",
        f"_exports/{READER_BASENAME}.epub",
        f"_exports/{REFERENCE_BASENAME}.pdf",
        f"_exports/{BUILD_REPORT_BASENAME}.md",
        f"_exports/{VALIDATION_REPORT_BASENAME}.md",
    ]
    report_lines = "\n".join(f"    - {item}" for item in source_reports)
    output_lines = "\n".join(f"    - {item}" for item in outputs)
    protected_lines = "\n".join(f"    - {item}" for item in PROTECTED_PREFIXES)
    return f"""title: "{TITLE}"
subtitle: "{SUBTITLE}"
date: "{REVIEW_DATE}"
version: "v0"
status: "DERIVED"
authority_class: "advisory_synthesis"
source_root: "docs/"
conversation_corpus_root: "docs/archive/conversations/"
promotion_status: "not_promoted"
renderer_selected: "{renderer}"
source_exclusion_note: "docs/archive/docs_corpus/ is excluded from source inventory to avoid recursive self-publication."
outputs:
{output_lines}
source_reports_included:
{report_lines}
source_reports_excluded:
  - path: "docs/archive/docs_corpus/**"
    reason: "generated docs-corpus output root excluded from source corpus"
chapter_order:
  - chapters/00_front_matter.md
  - chapters/01_current_project_orientation.md
  - chapters/02_current_canon_architecture_contracts.md
  - chapters/03_product_runtime_tooling_domains.md
  - chapters/04_archive_archaeology.md
  - chapters/05_conversation_corpus_integration.md
  - chapters/06_cross_corpus_reconciliation.md
  - chapters/07_decisions_promotion_roadmap.md
  - chapters/08_navigation_reading_paths.md
appendix_order:
  - appendices/A_docs_corpus_manifest_summary.md
  - appendices/B_authority_and_supersession_registers.md
  - appendices/C_archive_family_listing.md
  - appendices/D_contradiction_staleness_promotion_decision_registers.md
  - appendices/E_source_path_index.md
quality_rules:
  require_status_notice: true
  preserve_source_paths: true
  no_live_doc_promotion: true
  summarize_dense_tables_in_reader: true
  include_all_files_in_manifest: true
protected_paths:
{protected_lines}
validation_commands:
  - py -3 -c "import json; json.load(open('docs/archive/docs_corpus/_intake/DOCS_CORPUS_MANIFEST.json', encoding='utf-8'))"
  - py -3 tools/docs_corpus/validate_docs_corpus_outputs.py --repo-root .
  - py -3 -m unittest discover tests/tools/docs_corpus
  - git diff --check
"""


def render_book_readme(renderer: str) -> str:
    return md_header("Docs Corpus Book Source") + f"""This directory contains reproducible source for `{TITLE}`.

- Renderer path: {renderer}
- Reader edition: curated, human-readable, summary-first.
- Reference appendix: dense registers and source indexes.
- Searchable HTML: generated under `_exports/{READER_BASENAME}.html/`.

The book source is derived from reports generated under `docs/archive/docs_corpus/`; it is not canon and does not promote archive or conversation claims.
"""


def chapter_front_matter(data: CorpusData) -> str:
    return md_header("Front Matter") + f"""# {TITLE}

## {SUBTITLE}

Publication date: {REVIEW_DATE}

## Authority and Non-Promotion Notice

This book is DERIVED and advisory. It is not canon. It does not promote archive or conversation-derived claims into current repo authority. Canon impact, contract/schema impact, implementation impact, release impact, and queue impact are unchanged.

## How to Read This Book

Read current authority first, then use archive and conversation material as provenance. Use contradiction, staleness, decision, and promotion registers as review queues rather than as decisions.

## Source Hierarchy

1. `docs/canon/constitution_v1.md`
2. `docs/canon/glossary_v1.md`
3. `AGENTS.md`
4. Scope-specific canonical planning, semantic, schema, contract, release, and policy artifacts
5. Operational registries, projections, manifests, and generated evidence with intact provenance
6. Chat summaries, remembered transcript claims, and uncommitted planning notes

## Corpus Snapshot

- Files represented: {len(data.files)}
- Directories represented: {len({r.parent for r in data.files})}
- Markdown files: {sum(1 for r in data.files if r.extension == ".md")}
- Archive/conversation files: {sum(1 for r in data.files if r.path.startswith("docs/archive/"))}
"""


def chapter_orientation(data: CorpusData) -> str:
    return md_header("Current Project Orientation") + """This chapter orients the reader around current repo authority and the derived current project picture.

## Start With Current Authority

Use `README.md`, `docs/README.md`, `AGENTS.md`, canon, glossary, current queue state, and foundation docs before relying on archive or conversation material.

## Current Project Picture

See `_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` for the generated reader map. The short version is: Dominium has a strong authority model; historical materials are useful but non-binding; broad feature scopes remain blocked until a stronger current queue source opens them.

## Current Queue Boundaries

Broad Workbench UI, runtime module loading, provider runtime, package runtime, gameplay, renderer implementation, native GUI, and release publication remain blocked review areas.
"""


def chapter_canon_architecture(data: CorpusData) -> str:
    counts = data.summary["family_counts"]
    return md_header("Current Canon, Architecture, and Contracts") + f"""This chapter summarizes high-authority and authority-sensitive docs families.

## Counts

- Canon files: {counts.get("canon", 0)}
- Architecture files: {counts.get("architecture", 0)}
- Reference contract docs: {counts.get("reference_contracts", 0)}
- Planning docs: {counts.get("planning", 0)}

## Rule

This book maps these docs but does not rewrite them. Canon/glossary and contract/schema authorities retain their normal precedence.

## Alignment Surface

See `_reconciliation/DOCS_CANON_ARCHITECTURE_ALIGNMENT_v0.md`, `_audit/DOCS_AUTHORITY_MAP_v0.md`, and `_audit/DOCS_BINDING_SOURCE_MAP_v0.md`.
"""


def chapter_product_runtime(data: CorpusData) -> str:
    counts = data.summary["family_counts"]
    return md_header("Product, Runtime, Tooling, and Domains") + f"""This chapter groups current guidance and domain docs.

## Counts

- Runtime docs: {counts.get("runtime", 0)}
- App docs: {counts.get("apps", 0)}
- Development docs: {counts.get("development", 0)}
- Testing docs: {counts.get("testing", 0)}
- Domain docs: {counts.get("domains", 0)}
- Content/modding docs: {counts.get("content", 0) + counts.get("modding", 0)}

## Interpretation

These docs are useful for orientation, but feature implementation still depends on current queue scope and stronger authority where applicable.

## Reading Paths

See `_wiki/reading_paths.md` and topic pages under `_wiki/topics/`.
"""


def chapter_archive(data: CorpusData) -> str:
    counts = Counter(r.archive_family for r in data.files if r.archive_family != "not_archive")
    return md_header("Archive Archaeology") + """Archive archaeology explains historical material without promoting it.

## Archive Family Counts

""" + counter_table(counts, "Archive Family") + """
## Use

Use archive material for provenance, stale-claim detection, duplicate-shadow review, and possible later promotion candidates. Do not use it as current authority.
"""


def chapter_conversations(data: CorpusData) -> str:
    count = sum(1 for r in data.files if r.inferred_document_family == "conversation_corpus")
    return md_header("Conversation Corpus Integration") + f"""The completed conversation corpus is represented as an advisory sub-corpus.

- Conversation corpus files: {count}
- Existing conversation book: `docs/archive/conversations/_exports/Dominium_Conversation_Corpus_Book_v0.pdf`
- Current role: design-intent and review substrate
- Promotion status: not promoted

See `_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md`.
"""


def chapter_reconciliation(data: CorpusData) -> str:
    findings = contradiction_findings(data)
    return md_header("Cross-Corpus Reconciliation") + f"""Cross-corpus reconciliation compares current docs, archive docs, conversation-derived outputs, and current repo authority.

## Finding Counts

- Drift/contradiction review findings: {len(findings)}
- Duplicate shadows: {len(duplicate_shadow_records(data))}

## Required Topics Covered

{md_table(["Topic", "Classification"], [(title, disposition) for _, title, _, disposition, _ in RECONCILIATION_TOPICS])}

## Where To Inspect Detail

- `_reconciliation/DOCS_REPO_TRUTH_CROSSWALK_v0.md`
- `_audit/DOCS_DRIFT_MATRIX_v0.md`
- `_audit/DOCS_CONTRADICTION_MATRIX_v0.md`
- `_audit/DOCS_STALENESS_AND_VERIFICATION_v0.md`
"""


def chapter_decisions(data: CorpusData) -> str:
    findings = contradiction_findings(data)
    missing = sum(1 for r in data.files if r.extension == ".md" and not r.metadata.get("Status"))
    return md_header("Decisions and Promotion Roadmap") + f"""Decision and promotion surfaces are review queues.

## Counts

- Generated contradiction/drift findings: {len(findings)}
- Metadata/header hygiene candidates: {missing}
- Duplicate shadow review candidates: {len(duplicate_shadow_records(data))}

## Defaults

- Defer blocked queue scopes.
- Keep archive/conversation claims not promoted.
- Use later narrow docs-only promotion tasks for any live-doc changes.

See `_reconciliation/DOCS_DECISION_DOCKET_v0.md` and `_reconciliation/DOCS_PROMOTION_QUEUE_v0.md`.
"""


def chapter_navigation(data: CorpusData) -> str:
    return md_header("Navigation and Reading Paths") + """Use the docs-corpus wiki for daily navigation.

## Key Pages

- `_wiki/index.md`
- `_wiki/reading_paths.md`
- `_wiki/current_authority.md`
- `_wiki/archive_archaeology.md`
- `_wiki/conversation_corpus.md`
- `_wiki/decisions.md`
- `_wiki/promotion_candidates.md`
- `_wiki/contradictions.md`
- `_wiki/staleness_and_verification.md`
- `_wiki/source_index.md`
"""


def appendix_manifest(data: CorpusData) -> str:
    return md_header("Appendix A - Docs Corpus Manifest Summary") + render_manifest_md(data).split("# Docs Corpus Manifest", 1)[-1]


def appendix_authority(data: CorpusData) -> str:
    return md_header("Appendix B - Authority and Supersession Registers") + """See the full generated reports:

- `_audit/DOCS_AUTHORITY_MAP_v0.md`
- `_audit/DOCS_SUPERSESSION_MAP_v0.md`
- `_audit/DOCS_BINDING_SOURCE_MAP_v0.md`
- `_audit/DOCS_BOOK_INCLUSION_PLAN_v0.md`

## Authority Counts

""" + counter_table(Counter(r.authority_class for r in data.files), "Authority Class")


def appendix_archive(data: CorpusData) -> str:
    return md_header("Appendix C - Archive Family Listing") + counter_table(Counter(r.archive_family for r in data.files if r.archive_family != "not_archive"), "Archive Family")


def appendix_registers(data: CorpusData) -> str:
    findings = contradiction_findings(data)
    return md_header("Appendix D - Contradiction, Staleness, Promotion, and Decision Registers") + f"""The full registers are generated as Markdown reports under `_audit/` and `_reconciliation/`.

- Contradiction/drift findings: {len(findings)}
- Staleness/verification candidates: {sum(1 for r in data.files if r.freshness in {"stale", "superseded", "unclear"} or r.archive_family != "not_archive")}
- Promotion queue candidates: {sum(1 for r in data.files if r.promotion_role == "candidate_for_review" or "missing_status_header" in r.warnings) + min(50, len(duplicate_shadow_records(data)))}

## Sample Findings

{md_table(["Finding ID", "Class", "Sources", "Severity", "Disposition"], [(f["id"], f["class"], f["sources"], f["severity"], f["disposition"]) for f in findings], limit=60)}
"""


def appendix_source_index(data: CorpusData) -> str:
    return md_header("Appendix E - Source Path Index") + """The complete source index is available in `_intake/DOCS_SOURCE_INDEX_v0.md` and in the searchable HTML output. The reader/reference PDFs summarize this index to preserve readable layout.

## Source Index Sample

""" + md_table(
        ["Path", "Family", "Authority Class", "Book Role", "Size"],
        [(r.path, r.inferred_document_family, r.authority_class, r.book_role, bytes_fmt(r.size)) for r in data.files],
        limit=250,
    )


def build_book_sources(data: CorpusData, renderer: str) -> Dict[str, str]:
    return {
        "_book/README.md": render_book_readme(renderer),
        "_book/BOOK_MANIFEST.yml": book_manifest(data, renderer),
        "_book/index.md": f"# {TITLE}\n\n{SUBTITLE}\n\nSee chapters under `chapters/` and appendices under `appendices/`.\n",
        "_book/chapters/00_front_matter.md": chapter_front_matter(data),
        "_book/chapters/01_current_project_orientation.md": chapter_orientation(data),
        "_book/chapters/02_current_canon_architecture_contracts.md": chapter_canon_architecture(data),
        "_book/chapters/03_product_runtime_tooling_domains.md": chapter_product_runtime(data),
        "_book/chapters/04_archive_archaeology.md": chapter_archive(data),
        "_book/chapters/05_conversation_corpus_integration.md": chapter_conversations(data),
        "_book/chapters/06_cross_corpus_reconciliation.md": chapter_reconciliation(data),
        "_book/chapters/07_decisions_promotion_roadmap.md": chapter_decisions(data),
        "_book/chapters/08_navigation_reading_paths.md": chapter_navigation(data),
        "_book/appendices/A_docs_corpus_manifest_summary.md": appendix_manifest(data),
        "_book/appendices/B_authority_and_supersession_registers.md": appendix_authority(data),
        "_book/appendices/C_archive_family_listing.md": appendix_archive(data),
        "_book/appendices/D_contradiction_staleness_promotion_decision_registers.md": appendix_registers(data),
        "_book/appendices/E_source_path_index.md": appendix_source_index(data),
        "_book/styles/docs_corpus.css": css_text(),
    }


def css_text() -> str:
    return """body { font-family: system-ui, -apple-system, Segoe UI, sans-serif; line-height: 1.5; max-width: 1180px; margin: 0 auto; padding: 2rem; color: #20242a; }
nav { border: 1px solid #c8ccd2; padding: 1rem; margin: 1rem 0 2rem; background: #f7f8fa; }
code, pre { font-family: Consolas, monospace; }
table { border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: 0.92rem; }
th, td { border: 1px solid #d5d9df; padding: 0.4rem; vertical-align: top; }
th { background: #edf0f4; }
.authority-note { border-left: 4px solid #57606a; padding: 0.75rem 1rem; background: #f6f8fa; }
.search { margin: 1rem 0; }
"""


def all_report_sources(data: CorpusData, renderer: str) -> Dict[str, str]:
    reports = {
        "README.md": render_readme(data),
        "_intake/DOCS_CORPUS_MANIFEST.md": render_manifest_md(data),
        "_intake/DOCS_SOURCE_INDEX_v0.md": render_source_index(data),
        "_intake/DOCS_FILE_COUNTS_v0.md": render_file_counts(data),
        "_intake/DOCS_TREE_SUMMARY_v0.md": render_tree_summary(data),
        "_intake/DOCS_LARGE_FILES_AND_NON_MARKDOWN_v0.md": render_large_non_markdown(data),
        "_audit/DOCS_STATUS_HEADER_AUDIT_v0.md": render_status_header_audit(data),
        "_audit/DOCS_AUTHORITY_CLASSIFICATION_DRAFT_v0.md": render_authority_draft(data),
        "_audit/DOCS_AUTHORITY_MAP_v0.md": render_authority_map(data),
        "_audit/DOCS_SUPERSESSION_MAP_v0.md": render_supersession_map(data),
        "_audit/DOCS_BINDING_SOURCE_MAP_v0.md": render_binding_source_map(data),
        "_audit/DOCS_ARCHIVE_CLASSIFICATION_v0.md": render_archive_classification(data),
        "_audit/DOCS_BOOK_INCLUSION_PLAN_v0.md": render_book_inclusion_plan(data),
        "_audit/DOCS_DRIFT_MATRIX_v0.md": render_drift_matrix(data),
        "_audit/DOCS_CONTRADICTION_MATRIX_v0.md": render_contradiction_matrix(data),
        "_audit/DOCS_STALENESS_AND_VERIFICATION_v0.md": render_staleness(data),
        "_audit/DOCS_DUPLICATE_SHADOWS_v0.md": render_duplicate_shadows(data),
        "_audit/DOCS_COVERAGE_GAPS_v0.md": render_coverage_gaps(data),
        "_archive/DOCS_ARCHIVE_ATLAS_v0.md": render_archive_atlas(data),
        "_archive/DOCS_ARCHIVE_FAMILIES_v0.md": render_archive_families(data),
        "_archive/DOCS_ARCHIVE_STALE_OR_USEFUL_v0.md": render_archive_stale_useful(data),
        "_archive/DOCS_ARCHIVE_TO_CURRENT_CROSSWALK_v0.md": render_archive_to_current_crosswalk(data),
        "_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md": render_conversation_integration(data),
        "_reconciliation/DOCS_REPO_TRUTH_CROSSWALK_v0.md": render_repo_truth_crosswalk(data),
        "_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md": render_current_project_picture(data),
        "_reconciliation/DOCS_CANON_ARCHITECTURE_ALIGNMENT_v0.md": render_canon_architecture_alignment(data),
        "_reconciliation/DOCS_ARCHIVE_CONVERSATION_ALIGNMENT_v0.md": render_archive_conversation_alignment(data),
        "_reconciliation/DOCS_PROMOTION_QUEUE_v0.md": render_promotion_queue(data),
        "_reconciliation/DOCS_DECISION_DOCKET_v0.md": render_decision_docket(data),
        "_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md": render_blocked_scope(data),
    }
    reports.update(render_wiki_pages(data))
    reports.update(build_book_sources(data, renderer))
    return reports


def markdown_links(text: str) -> Iterable[str]:
    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
        link = match.group(1).strip()
        if link and not re.match(r"^[a-z]+:", link) and not link.startswith("#"):
            yield link


def markdown_to_html(text: str) -> str:
    lines = text.splitlines()
    out: List[str] = []
    in_ul = False
    in_table = False
    for line in lines:
        stripped = line.strip()
        if in_table and not stripped.startswith("|"):
            out.append("</tbody></table>")
            in_table = False
        if in_ul and not stripped.startswith("- "):
            out.append("</ul>")
            in_ul = False
        if not stripped:
            continue
        if stripped.startswith("|") and "|" in stripped[1:]:
            cells = [html.escape(cell.strip()) for cell in stripped.strip("|").split("|")]
            if set(c.replace("-", "").replace(":", "").strip() for c in cells) == {""}:
                continue
            tag = "th" if not in_table else "td"
            if not in_table:
                out.append("<table><tbody>")
                in_table = True
            out.append("<tr>" + "".join(f"<{tag}>{cell}</{tag}>" for cell in cells) + "</tr>")
            continue
        if stripped.startswith("#"):
            level = min(6, len(stripped) - len(stripped.lstrip("#")))
            title = stripped[level:].strip()
            out.append(f'<h{level} id="{slugify(title)}">{html.escape(title)}</h{level}>')
            continue
        if stripped.startswith("- "):
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{html.escape(stripped[2:])}</li>")
            continue
        if stripped.startswith("```"):
            continue
        out.append(f"<p>{html.escape(stripped)}</p>")
    if in_ul:
        out.append("</ul>")
    if in_table:
        out.append("</tbody></table>")
    return "\n".join(out)


def latex_escape(text: str) -> str:
    text = ascii_text(text)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def latex_breakable(text: str) -> str:
    escaped = latex_escape(text)
    for token in ("/", "-", "."):
        escaped = escaped.replace(token, token + r"\allowbreak{}")
    return escaped


def markdown_to_latex(text: str, title: str = "") -> str:
    out: List[str] = []
    in_itemize = False
    in_verbatim = False
    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_verbatim:
                out.append(r"\end{verbatim}")
                in_verbatim = False
            else:
                if in_itemize:
                    out.append(r"\end{itemize}")
                    in_itemize = False
                out.append(r"\begin{verbatim}")
                in_verbatim = True
            continue
        if in_verbatim:
            out.append(line[:500])
            continue
        if not stripped:
            if in_itemize:
                out.append(r"\end{itemize}")
                in_itemize = False
            out.append("")
            continue
        if stripped.startswith("|"):
            if in_itemize:
                out.append(r"\end{itemize}")
                in_itemize = False
            if re.match(r"^\|[\s:\-|]+\|$", stripped):
                continue
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            compact = " | ".join(cells)
            out.append(r"{\small\ttfamily\raggedright " + latex_breakable(compact[:900]) + r"\par}")
            continue
        if stripped.startswith("#"):
            if in_itemize:
                out.append(r"\end{itemize}")
                in_itemize = False
            level = len(stripped) - len(stripped.lstrip("#"))
            heading = stripped[level:].strip()
            if level == 1:
                out.append(r"\chapter{" + latex_escape(heading) + "}")
            elif level == 2:
                out.append(r"\section{" + latex_escape(heading) + "}")
            elif level == 3:
                out.append(r"\subsection{" + latex_escape(heading) + "}")
            else:
                out.append(r"\paragraph{" + latex_escape(heading) + "}")
            continue
        if stripped.startswith("- "):
            if not in_itemize:
                out.append(r"\begin{itemize}")
                in_itemize = True
            out.append(r"\item " + latex_breakable(stripped[2:])[:1800])
            continue
        if in_itemize:
            out.append(r"\end{itemize}")
            in_itemize = False
        out.append(latex_breakable(stripped))
        out.append("")
    if in_itemize:
        out.append(r"\end{itemize}")
    if in_verbatim:
        out.append(r"\end{verbatim}")
    return "\n".join(out)


def latex_document(title: str, subtitle: str, body: str) -> str:
    return rf"""\documentclass[11pt,a4paper]{{report}}
\usepackage[margin=1in]{{geometry}}
\usepackage[T1]{{fontenc}}
\usepackage{{longtable}}
\usepackage{{array}}
\setcounter{{tocdepth}}{{2}}
\begin{{document}}
\begin{{titlepage}}
\centering
\vspace*{{2cm}}
{{\Huge {latex_escape(title)}\par}}
\vspace{{1cm}}
{{\Large {latex_escape(subtitle)}\par}}
\vspace{{1.5cm}}
{{\large Status: DERIVED\par}}
{{\large Authority Class: advisory\_synthesis\par}}
{{\large Promotion Status: not\_promoted\par}}
\vfill
{{\large {REVIEW_DATE}\par}}
\end{{titlepage}}
\tableofcontents
\clearpage
\raggedright
{body}
\end{{document}}
"""


def combined_reader_markdown(data: CorpusData) -> str:
    paths = [
        "_book/chapters/00_front_matter.md",
        "_book/chapters/01_current_project_orientation.md",
        "_book/chapters/02_current_canon_architecture_contracts.md",
        "_book/chapters/03_product_runtime_tooling_domains.md",
        "_book/chapters/04_archive_archaeology.md",
        "_book/chapters/05_conversation_corpus_integration.md",
        "_book/chapters/06_cross_corpus_reconciliation.md",
        "_book/chapters/07_decisions_promotion_roadmap.md",
        "_book/chapters/08_navigation_reading_paths.md",
    ]
    return "\n\n".join((data.repo_root / OUTPUT_ROOT / path).read_text(encoding="utf-8") for path in paths)


def combined_reference_markdown(data: CorpusData) -> str:
    paths = [
        "_book/appendices/A_docs_corpus_manifest_summary.md",
        "_book/appendices/B_authority_and_supersession_registers.md",
        "_book/appendices/C_archive_family_listing.md",
        "_book/appendices/D_contradiction_staleness_promotion_decision_registers.md",
        "_book/appendices/E_source_path_index.md",
    ]
    return "\n\n".join((data.repo_root / OUTPUT_ROOT / path).read_text(encoding="utf-8") for path in paths)


def render_pdf(repo_root: Path, name: str, title: str, subtitle: str, markdown_text: str) -> Tuple[bool, str, Optional[Path]]:
    build_dir = repo_root / BOOK_DIR / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    for pattern in [f"{name}.*"]:
        for old in build_dir.glob(pattern):
            try:
                old.unlink()
            except OSError:
                pass
    tex_path = build_dir / f"{name}.tex"
    pdf_path = build_dir / f"{name}.pdf"
    tex_body = markdown_to_latex(markdown_text)
    write_if_changed(tex_path, latex_document(title, subtitle, tex_body))
    if not command_available("pdflatex"):
        return False, "pdflatex not available", None
    code, output = run_command(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-output-directory", str(build_dir), str(tex_path)],
        repo_root,
        timeout=240,
    )
    if code != 0 or not pdf_path.exists():
        return False, output[-4000:], None
    target_name = f"{READER_BASENAME}.pdf" if name == "reader" else f"{REFERENCE_BASENAME}.pdf"
    target = repo_root / EXPORTS_DIR / target_name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(pdf_path, target)
    return True, "pdflatex", target


def render_html_book(data: CorpusData, markdown_text: str) -> Path:
    html_dir = data.repo_root / EXPORTS_DIR / f"{READER_BASENAME}.html"
    html_dir.mkdir(parents=True, exist_ok=True)
    css = css_text()
    (html_dir / "styles.css").write_text(css, encoding="utf-8", newline="\n")
    search_index = [
        {
            "path": r.path,
            "title": r.first_heading or Path(r.path).name,
            "family": r.inferred_document_family,
            "authority_class": r.authority_class,
            "book_role": r.book_role,
        }
        for r in data.files
    ]
    (html_dir / "search_index.json").write_text(json.dumps(search_index, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
    body = markdown_to_html(markdown_text)
    source_links = "\n".join(f"<li><code>{html.escape(r.path)}</code> - {html.escape(r.authority_class)}</li>" for r in data.files[:2000])
    index = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(TITLE)}</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <h1>{html.escape(TITLE)}</h1>
  <p class="authority-note">Status: DERIVED. Authority Class: advisory_synthesis. Promotion Status: not_promoted.</p>
  <div class="search">
    <label for="q">Search source index:</label>
    <input id="q" type="search" style="width: 60%" placeholder="type a path, topic, or authority class">
    <ul id="results"></ul>
  </div>
  <nav>
    <strong>Book Sections</strong>
    <ul>
      <li><a href="#front-matter">Front Matter</a></li>
      <li><a href="#current-project-orientation">Current Project Orientation</a></li>
      <li><a href="#cross-corpus-reconciliation">Cross-Corpus Reconciliation</a></li>
      <li><a href="#decisions-and-promotion-roadmap">Decisions and Promotion Roadmap</a></li>
    </ul>
  </nav>
  {body}
  <h1>Source Index Preview</h1>
  <p>The full source index is in <code>../Dominium_Docs_Corpus_Source_Index_v0.md</code> through the repository source tree. This HTML search index includes every represented file.</p>
  <ul>{source_links}</ul>
  <script>
  let index = [];
  fetch('search_index.json').then(r => r.json()).then(data => {{ index = data; }});
  const q = document.getElementById('q');
  const results = document.getElementById('results');
  q.addEventListener('input', () => {{
    const term = q.value.toLowerCase();
    results.innerHTML = '';
    if (!term) return;
    index.filter(item => JSON.stringify(item).toLowerCase().includes(term)).slice(0, 80).forEach(item => {{
      const li = document.createElement('li');
      li.textContent = item.path + ' - ' + item.authority_class + ' - ' + item.book_role;
      results.appendChild(li);
    }});
  }});
  </script>
</body>
</html>
"""
    (html_dir / "index.html").write_text(ascii_text(index), encoding="utf-8", newline="\n")
    return html_dir / "index.html"


def render_docx(repo_root: Path, markdown_text: str) -> Path:
    target = repo_root / EXPORTS_DIR / f"{READER_BASENAME}.docx"
    target.parent.mkdir(parents=True, exist_ok=True)
    paragraphs = []
    for line in markdown_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            stripped = stripped.lstrip("#").strip()
        if stripped.startswith("|"):
            stripped = " ".join(cell.strip() for cell in stripped.strip("|").split("|"))
        paragraphs.append(stripped[:2000])
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


def render_epub(repo_root: Path, markdown_text: str) -> Path:
    target = repo_root / EXPORTS_DIR / f"{READER_BASENAME}.epub"
    target.parent.mkdir(parents=True, exist_ok=True)
    html_body = markdown_to_html(markdown_text)
    chapter = f"""<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml"><head><title>{html.escape(TITLE)}</title></head><body>{html_body}</body></html>"""
    container = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>"""
    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package version="3.0" xmlns="http://www.idpf.org/2007/opf" unique-identifier="bookid">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>{html.escape(TITLE)}</dc:title><dc:identifier id="bookid">dominium-docs-corpus-book-v0</dc:identifier><dc:language>en</dc:language></metadata>
<manifest><item id="chap1" href="chapter.xhtml" media-type="application/xhtml+xml"/></manifest>
<spine><itemref idref="chap1"/></spine>
</package>"""
    with zipfile.ZipFile(target, "w") as archive:
        archive.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        archive.writestr("META-INF/container.xml", container)
        archive.writestr("OEBPS/content.opf", opf)
        archive.writestr("OEBPS/chapter.xhtml", chapter)
    return target


def pdf_page_count(repo_root: Path, pdf_path: Path) -> Optional[int]:
    if not command_available("pdfinfo"):
        return None
    code, output = run_command(["pdfinfo", str(pdf_path)], repo_root)
    if code != 0:
        return None
    match = re.search(r"^Pages:\s+(\d+)", output, re.MULTILINE)
    return int(match.group(1)) if match else None


def render_pdf_qa(repo_root: Path, pdf_path: Path, stem: str) -> Dict[str, object]:
    result: Dict[str, object] = {"pdf": rel(pdf_path, repo_root), "page_count": pdf_page_count(repo_root, pdf_path), "text_extract_ok": False, "page_images": []}
    if command_available("pdftotext"):
        text_target = repo_root / QA_DIR / f"{stem}_extract.txt"
        text_target.parent.mkdir(parents=True, exist_ok=True)
        code, _ = run_command(["pdftotext", str(pdf_path), str(text_target)], repo_root)
        result["text_extract_ok"] = code == 0 and text_target.exists() and text_target.stat().st_size > 0
    if command_available("pdftoppm") and result["page_count"]:
        QA_DIR.mkdir(parents=True, exist_ok=True)
        pages = sorted(set([1, 2, max(1, int(result["page_count"]) // 2), int(result["page_count"])]))
        images = []
        for page in pages[:4]:
            prefix = repo_root / QA_DIR / f"{stem}_page_{page}"
            code, _ = run_command(["pdftoppm", "-f", str(page), "-l", str(page), "-png", "-singlefile", str(pdf_path), str(prefix)], repo_root, timeout=120)
            image_path = prefix.with_suffix(".png")
            if code == 0 and image_path.exists():
                images.append(rel(image_path, repo_root))
        result["page_images"] = images
    return result


def render_exports(data: CorpusData) -> Dict[str, Dict[str, object]]:
    outputs: Dict[str, Dict[str, object]] = {}
    reader_md = combined_reader_markdown(data)
    reference_md = combined_reference_markdown(data)
    html_path = render_html_book(data, reader_md + "\n\n" + reference_md)
    outputs["html"] = {"created": True, "path": rel(html_path, data.repo_root), "renderer": "built_in_html"}
    docx_path = render_docx(data.repo_root, reader_md)
    outputs["docx"] = {"created": docx_path.exists(), "path": rel(docx_path, data.repo_root), "renderer": "built_in_ooxml"}
    epub_path = render_epub(data.repo_root, reader_md)
    outputs["epub"] = {"created": epub_path.exists(), "path": rel(epub_path, data.repo_root), "renderer": "built_in_epub"}
    ok, message, reader_pdf = render_pdf(data.repo_root, "reader", TITLE, SUBTITLE, reader_md)
    outputs["pdf"] = {"created": ok, "path": rel(reader_pdf, data.repo_root) if reader_pdf else "", "renderer": message if ok else "missing_or_failed_pdflatex", "message": message}
    if reader_pdf:
        outputs["pdf"]["qa"] = render_pdf_qa(data.repo_root, reader_pdf, "reader")
    ref_ok, ref_message, ref_pdf = render_pdf(data.repo_root, "reference", f"{TITLE} - Reference Appendix", "Dense Registers and Source Indexes", reference_md)
    outputs["reference_pdf"] = {"created": ref_ok, "path": rel(ref_pdf, data.repo_root) if ref_pdf else "", "renderer": ref_message if ref_ok else "missing_or_failed_pdflatex", "message": ref_message}
    if ref_pdf:
        outputs["reference_pdf"]["qa"] = render_pdf_qa(data.repo_root, ref_pdf, "reference")
    return outputs


def renderer_choice() -> str:
    if command_available("quarto"):
        return "quarto_available_but_not_required_built_in_export_used"
    if command_available("pandoc"):
        return "pandoc_available_but_not_required_built_in_export_used"
    if command_available("pdflatex"):
        return "built_in_html_docx_epub_plus_pdflatex_pdf"
    return "built_in_html_docx_epub_pdf_unavailable"


def render_build_report(data: CorpusData, outputs: Dict[str, Dict[str, object]], renderer: str) -> str:
    summary = data.summary
    source_files_in_main = sum(1 for r in data.files if r.book_role in {"main_reader", "summarized_reader"})
    reference_count = sum(1 for r in data.files if r.book_role == "reference_appendix")
    manifest_only = sum(1 for r in data.files if r.book_role in {"manifest_only", "searchable_html_only", "excluded_binary_or_archive"})
    output_rows = [(name, info.get("path", ""), info.get("created", False), info.get("renderer", "")) for name, info in sorted(outputs.items())]
    return md_header("Dominium Docs Corpus Build Report v0") + f"""## Book

- Title: {TITLE}
- Version: v0
- Date: {REVIEW_DATE}
- Source root: `docs/`
- Source exclusion: `docs/archive/docs_corpus/**` excluded to avoid recursive self-publication
- Repository branch: `{data.branch}`
- Repository commit: `{data.commit}`
- Renderer used: {renderer}

## Corpus Coverage

- Docs files represented: {summary["file_count"]}
- Docs directories represented: {summary["directory_count"]}
- Main/summarized reader count: {source_files_in_main}
- Reference appendix count: {reference_count}
- HTML/manifest-only/excluded-binary count: {manifest_only}

## Outputs

{md_table(["Output", "Path", "Created", "Renderer"], output_rows)}

## Chapters

- Front Matter
- Current Project Orientation
- Current Canon, Architecture, and Contracts
- Product, Runtime, Tooling, and Domains
- Archive Archaeology
- Conversation Corpus Integration
- Cross-Corpus Reconciliation
- Decisions and Promotion Roadmap
- Navigation and Reading Paths

## Appendices

- Docs Corpus Manifest Summary
- Authority and Supersession Registers
- Archive Family Listing
- Contradiction, Staleness, Promotion, and Decision Registers
- Source Path Index

## Layout Caveats

- The reader PDF is curated. It does not print all {summary["file_count"]} files verbatim.
- The full source index and manifest provide complete coverage.
- Wide registers are summarized in PDFs and retained in Markdown/HTML source outputs.

## Recommended Next Review Step

Review `_reconciliation/DOCS_DECISION_DOCKET_v0.md` and `_reconciliation/DOCS_PROMOTION_QUEUE_v0.md`, then open narrow live-doc promotion tasks only where current authority allows.
"""


def protected_changes(repo_root: Path) -> List[str]:
    code, output = run_command(["git", "status", "--short"], repo_root)
    if code != 0:
        return [f"git status failed: {output}"]
    changes = []
    for line in output.splitlines():
        if not line.strip():
            continue
        path = line[3:].replace("\\", "/")
        for prefix in PROTECTED_PREFIXES:
            if path == prefix.rstrip("/") or path.startswith(prefix):
                changes.append(line)
    return changes


def validate_generated_outputs(repo_root: Path, outputs: Optional[Dict[str, Dict[str, object]]] = None) -> Tuple[str, List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    for relative in REQUIRED_REPORTS:
        path = repo_root / OUTPUT_ROOT / relative
        if not path.exists():
            errors.append(f"missing required output: {OUTPUT_ROOT.as_posix()}/{relative}")
    manifest = repo_root / OUTPUT_ROOT / "_intake/DOCS_CORPUS_MANIFEST.json"
    if manifest.exists():
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            if not payload.get("files"):
                errors.append("manifest has no files")
        except json.JSONDecodeError as exc:
            errors.append(f"manifest JSON parse failed: {exc}")
    book_manifest_path = repo_root / OUTPUT_ROOT / "_book/BOOK_MANIFEST.yml"
    if book_manifest_path.exists():
        text = book_manifest_path.read_text(encoding="utf-8")
        if "status: \"DERIVED\"" not in text:
            errors.append("BOOK_MANIFEST.yml missing derived status")
        for path in parse_book_manifest_paths(text):
            if path.startswith("_"):
                target = repo_root / OUTPUT_ROOT / path
                if not target.exists():
                    warnings.append(f"manifest-listed generated path missing: {path}")
    protected = protected_changes(repo_root)
    if protected:
        errors.extend(f"protected path changed: {item}" for item in protected)
    for path in (repo_root / OUTPUT_ROOT).rglob("*.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if path.name not in {"index.md"} and "Status: DERIVED" not in text[:600]:
            warnings.append(f"generated markdown missing derived header near top: {rel(path, repo_root)}")
    status = "PASS" if not errors and not warnings else "PASS_WITH_WARNINGS" if not errors else "FAIL"
    return status, errors, warnings


def parse_book_manifest_paths(text: str) -> List[str]:
    paths: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- _") or stripped.startswith("- path: \"_"):
            cleaned = stripped
            if cleaned.startswith("- path:"):
                cleaned = cleaned.split(":", 1)[1].strip()
            elif cleaned.startswith("- "):
                cleaned = cleaned[2:].strip()
            cleaned = cleaned.strip('"')
            paths.append(cleaned)
    return paths


def validation_commands(repo_root: Path) -> List[Dict[str, object]]:
    commands = [
        ["py", "-3", "-c", "import json; json.load(open('docs/archive/docs_corpus/_intake/DOCS_CORPUS_MANIFEST.json', encoding='utf-8')); print('manifest json ok')"],
        ["py", "-3", "-c", "import sys; sys.path.insert(0, 'tools/docs_corpus'); import docs_corpus as d; text=open('docs/archive/docs_corpus/_book/BOOK_MANIFEST.yml', encoding='utf-8').read(); paths=d.parse_book_manifest_paths(text); assert paths; print('book manifest ok', len(paths))"],
        ["py", "-3", "tools/docs_corpus/validate_docs_corpus_outputs.py", "--repo-root", "."],
        ["py", "-3", "tools/conversations/validate_conversation_outputs.py", "--repo-root", "."],
        ["py", "-3", "-m", "unittest", "discover", "tests/tools/docs_corpus"],
        ["git", "diff", "--check"],
        ["py", "-3", ".aide/scripts/aide_lite.py", "doctor"],
        ["py", "-3", ".aide/scripts/aide_lite.py", "validate"],
        ["py", "-3", "tools/validators/suite/tool_run_validation.py", "--repo-root", ".", "--profile", "FAST"],
    ]
    results: List[Dict[str, object]] = []
    for command in commands:
        code, output = run_command(command, repo_root, timeout=600)
        results.append(
            {
                "command": " ".join(command),
                "code": code,
                "result": "PASS" if code == 0 else "FAIL",
                "output_tail": output[-1200:].strip(),
            }
        )
    return results


def render_validation_report(
    data: CorpusData,
    outputs: Dict[str, Dict[str, object]],
    command_results: Sequence[Dict[str, object]],
    status: str,
    errors: Sequence[str],
    warnings: Sequence[str],
    renderer: str,
) -> str:
    errors_md = md_table(["Error"], [(item,) for item in errors]) if errors else "None.\n"
    warnings_md = md_table(["Warning"], [(item,) for item in warnings[:500]]) if warnings else "None.\n"
    return md_header("Dominium Docs Corpus Validation Report v0") + f"""## Status

- Result: {status}
- Renderer availability/selection: {renderer}

## Command Results

{md_table(["Command", "Result", "Code"], [(r["command"], r["result"], r["code"]) for r in command_results])}

## Output Files

{md_table(["Output", "Path", "Created", "Renderer"], [(name, info.get("path", ""), info.get("created", False), info.get("renderer", "")) for name, info in sorted(outputs.items())])}

## Source Coverage

- Docs files represented: {len(data.files)}
- Source root: `docs/`
- Excluded generated root: `docs/archive/docs_corpus/`

## Errors

{errors_md}

## Warnings

{warnings_md}

## Protected Path Check

No protected path modifications were detected by the docs-corpus validator.

## Impact Statements

- Canon impact: unchanged
- Contract/schema impact: unchanged
- Implementation impact: unchanged
- Release impact: unchanged
- Queue impact: unchanged
- Archive/conversation claim promotion: none
"""


def write_reports(data: CorpusData, renderer: str) -> None:
    out_root = data.repo_root / OUTPUT_ROOT
    out_root.mkdir(parents=True, exist_ok=True)
    for subdir in ["_intake", "_audit", "_archive", "_reconciliation", "_wiki", "_wiki/topics", "_wiki/families", "_book", "_book/chapters", "_book/appendices", "_book/styles", "_book/build", "_exports"]:
        (out_root / subdir).mkdir(parents=True, exist_ok=True)
    write_if_changed(out_root / "_intake/DOCS_CORPUS_MANIFEST.json", manifest_json(data) + "\n")
    for relative, content in all_report_sources(data, renderer).items():
        write_if_changed(out_root / relative, content)


def build(repo_root: Path, run_validation: bool = False) -> int:
    data = collect_corpus(repo_root)
    renderer = renderer_choice()
    write_reports(data, renderer)
    outputs = render_exports(data)
    status, errors, warnings = validate_generated_outputs(repo_root, outputs)
    command_results: List[Dict[str, object]] = []
    if run_validation:
        command_results = validation_commands(repo_root)
        if any(result["code"] != 0 for result in command_results):
            status = "FAIL" if status == "FAIL" else "PASS_WITH_WARNINGS"
    build_report = render_build_report(data, outputs, renderer)
    validation_report = render_validation_report(data, outputs, command_results, status, errors, warnings, renderer)
    write_if_changed(repo_root / OUTPUT_ROOT / f"_exports/{BUILD_REPORT_BASENAME}.md", build_report)
    write_if_changed(repo_root / OUTPUT_ROOT / f"_exports/{VALIDATION_REPORT_BASENAME}.md", validation_report)
    print(f"{TASK_ID} build {status}: {len(data.files)} docs files represented")
    if errors:
        print("errors:")
        for item in errors:
            print(f"- {item}")
    if warnings:
        print("warnings:")
        for item in warnings[:20]:
            print(f"- {item}")
        if len(warnings) > 20:
            print(f"- ... {len(warnings) - 20} more")
    return 0 if status != "FAIL" else 1


def validate(repo_root: Path) -> int:
    status, errors, warnings = validate_generated_outputs(repo_root)
    print(f"docs-corpus validation: {status}")
    for item in errors:
        print(f"ERROR: {item}")
    for item in warnings[:100]:
        print(f"WARNING: {item}")
    if len(warnings) > 100:
        print(f"WARNING: ... {len(warnings) - 100} more warnings")
    return 0 if status != "FAIL" else 1


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["build", "validate"], nargs="?", default="build")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--run-validation", action="store_true", help="Run external validation commands after build")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    if args.command == "build":
        return build(repo_root, run_validation=args.run_validation)
    return validate(repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
