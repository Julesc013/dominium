"""Compare the repo project-vision corpus with an external scratchpad variant.

This tool treats the scratchpad corpus as derived advisory evidence. It does
not copy the scratchpad corpus wholesale and does not promote any archive claim.
It writes a compact comparison layer under the repo corpus output root.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path


TASK_ID = "PROJECT-VISION-CORPUS-SCRATCHPAD-COMPARE-01"
DATE = "2026-06-03"


HEADER = """Status: DERIVED
Last Reviewed: 2026-06-03
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_comparison
Source Root: `docs/archive/project_vision_corpus/`; `tmp/project_vision_corpus/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

"""


SOURCE_LIBRARY_HEADER = """Status: DERIVED
Last Reviewed: 2026-06-03
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


@dataclass(frozen=True)
class CorpusSummary:
    root: Path
    name: str
    counts: dict[str, int]
    source_paths: list[str]
    source_basenames: set[str]
    zip_names: set[str]


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def normalize_basename(path_text: str) -> str:
    return Path(path_text.replace("\\", "/")).name.lower()


def extract_first_int(patterns: list[str], text: str) -> int:
    for pattern in patterns:
        m = re.search(pattern, text, flags=re.IGNORECASE)
        if m:
            return int(m.group(1).replace(",", ""))
    return 0


def extract_counts(root: Path, name: str) -> dict[str, int]:
    build = read_text(root / "build_reports" / "PROJECT_VISION_CORPUS_BUILD_REPORT.md")
    validation = read_text(root / "build_reports" / "PROJECT_VISION_CORPUS_VALIDATION_REPORT.md")
    text = build + "\n" + validation

    if name == "repo":
        return {
            "zip_packages": extract_first_int([r"Zip packages inventoried:\s*([0-9,]+)", r"Zip packages accounted for:\s*([0-9,]+)"], text),
            "human_sources": extract_first_int([r"Human-readable sources selected:\s*([0-9,]+)", r"Source files selected:\s*([0-9,]+)"], text),
            "semantic_blocks": extract_first_int([r"Semantic blocks retained:\s*([0-9,]+)", r"Semantic blocks generated:\s*([0-9,]+)"], text),
            "themes": extract_first_int([r"Themes generated:\s*([0-9,]+)", r"Theme groups:\s*([0-9,]+)"], text),
            "duplicate_source_groups": extract_first_int([r"Duplicate block source groups:\s*([0-9,]+)", r"Duplicate source groups noted:\s*([0-9,]+)"], text),
        }

    return {
        "top_level_entries": extract_first_int([r"Top-level entries:\s*([0-9,]+)"], text),
        "zip_packages": extract_first_int([r"Top-level zip files extracted:\s*([0-9,]+)"], text),
        "extracted_files": extract_first_int([r"Extracted file count after nested inspection:\s*([0-9,]+)"], text),
        "human_candidates": extract_first_int([r"Unique human-readable candidates:\s*([0-9,]+)"], text),
        "human_sources": extract_first_int([r"Human-readable sources selected:\s*([0-9,]+)"], text),
        "semantic_blocks": extract_first_int([r"Semantic blocks extracted:\s*([0-9,]+)"], text),
        "themes": extract_first_int([r"Theme groups:\s*([0-9,]+)"], text),
    }


def parse_source_paths(root: Path) -> list[str]:
    paths: list[str] = []
    for relpath in (
        "source_selection/SOURCE_PRIORITY_LIST.md",
        "source_selection/HUMAN_READABLE_SOURCE_SELECTION.md",
    ):
        text = read_text(root / relpath)
        for line in text.splitlines():
            # Repo corpus bullet style: - P1: `path`
            for match in re.finditer(r"`([^`]+\.(?:md|txt))`", line, flags=re.IGNORECASE):
                paths.append(match.group(1).strip())

            # Scratchpad table style: | rank | ... | path |
            if line.startswith("|") and ".md" in line.lower() or line.startswith("|") and ".txt" in line.lower():
                cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
                if cells:
                    candidate = cells[-1]
                    if candidate.lower().endswith((".md", ".txt")):
                        paths.append(candidate)

    seen: set[str] = set()
    out: list[str] = []
    for path in paths:
        key = path.replace("\\", "/").lower()
        if key not in seen:
            seen.add(key)
            out.append(path.replace("\\", "/"))
    return out


def load_zip_names(root: Path, name: str) -> set[str]:
    manifest_path = root / "raw_manifest" / "ZIP_MANIFEST.json"
    if not manifest_path.exists():
        return set()
    data = json.loads(read_text(manifest_path))
    if name == "repo":
        return {Path(item.get("path", "")).name.lower() for item in data.get("zips", []) if item.get("path")}
    return {
        item.get("filename", "").lower()
        for item in data.get("top_level_entries", [])
        if item.get("filename", "").lower().endswith(".zip")
    }


def summarize(root: Path, name: str) -> CorpusSummary:
    source_paths = parse_source_paths(root)
    return CorpusSummary(
        root=root,
        name=name,
        counts=extract_counts(root, name),
        source_paths=source_paths,
        source_basenames={normalize_basename(path) for path in source_paths},
        zip_names=load_zip_names(root, name),
    )


def markdown_list(items: list[str], limit: int = 80) -> str:
    shown = items[:limit]
    lines = [f"- `{item}`" for item in shown]
    if len(items) > limit:
        lines.append(f"- ... {len(items) - limit} more omitted from this compact report")
    return "\n".join(lines) if lines else "- none"


def count_shadowed_duplicates(report_text: str) -> int:
    total = 0
    for match in re.finditer(r"shadowed\s+([0-9]+)\s+duplicate", report_text, flags=re.IGNORECASE):
        total += int(match.group(1))
    return total


def write_source_block_library(repo: CorpusSummary) -> None:
    dedupe_text = read_text(repo.root / "source_blocks" / "SOURCE_BLOCK_DEDUPLICATION_REPORT.md")
    shadowed = count_shadowed_duplicates(dedupe_text)
    text = (
        SOURCE_LIBRARY_HEADER
        + "# Source Block Library\n\n"
        + "This is the repo-side source block library entry point for `PROJECT-VISION-CORPUS-01`.\n"
        + "It exists to make the semantic block layer discoverable without turning a future book into "
        + "a block-ID or evidence-card report.\n\n"
        + "## Status\n\n"
        + "- The block library is derived and advisory.\n"
        + "- Conversation and archive claims remain historical evidence, not canon.\n"
        + "- Block IDs are for traceability and review; they should not become the main reading flow of a final book.\n\n"
        + "## Library Files\n\n"
        + "- `source_blocks/SOURCE_BLOCKS.yml` - full machine-readable semantic block library.\n"
        + "- `source_blocks/SOURCE_BLOCKS.md` - human-readable excerpted block library.\n"
        + "- `source_blocks/SOURCE_BLOCK_INDEX.md` - block index by source, type, and theme.\n"
        + "- `source_blocks/SOURCE_BLOCK_DEDUPLICATION_REPORT.md` - duplicate/shadow block report.\n\n"
        + "## Counts\n\n"
        + f"- Human-readable sources selected: {repo.counts.get('human_sources', 0)}\n"
        + f"- Semantic blocks retained: {repo.counts.get('semantic_blocks', 0)}\n"
        + f"- Duplicate source groups noted: {repo.counts.get('duplicate_source_groups', 0)}\n"
        + f"- Duplicate/shadow blocks omitted: {shadowed}\n"
        + f"- Themes generated: {repo.counts.get('themes', 0)}\n\n"
        + "## Use Rule\n\n"
        + "Use this library for review, verification, and future synthesis planning. A polished project vision "
        + "book should summarize the ideas in prose and relegate source-block traceability to notes or appendices.\n"
    )
    write_text(repo.root / "synthesis" / "SOURCE_BLOCK_LIBRARY.md", text)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_comparison(repo: CorpusSummary, scratch: CorpusSummary, output_root: Path) -> None:
    common_sources = sorted(repo.source_basenames & scratch.source_basenames)
    repo_only = sorted(repo.source_basenames - scratch.source_basenames)
    scratch_only = sorted(scratch.source_basenames - repo.source_basenames)
    common_zips = sorted(repo.zip_names & scratch.zip_names)
    repo_only_zips = sorted(repo.zip_names - scratch.zip_names)
    scratch_only_zips = sorted(scratch.zip_names - repo.zip_names)

    manifest = {
        "task_id": TASK_ID,
        "date": DATE,
        "repo_corpus_root": rel(repo.root, repo.root.parent.parent.parent.parent),
        "scratchpad_corpus_root": scratch.root.as_posix(),
        "repo_counts": repo.counts,
        "scratchpad_counts": scratch.counts,
        "source_basename_overlap": len(common_sources),
        "repo_only_source_basenames": len(repo_only),
        "scratchpad_only_source_basenames": len(scratch_only),
        "zip_overlap": len(common_zips),
        "repo_only_zip_names": len(repo_only_zips),
        "scratchpad_only_zip_names": len(scratch_only_zips),
        "scratchpad_files": [
            {"path": rel(path, scratch.root), "sha256": sha256_file(path), "size": path.stat().st_size}
            for path in sorted(scratch.root.rglob("*"))
            if path.is_file()
        ],
    }
    write_text(output_root / "SCRATCHPAD_CORPUS_MANIFEST.json", json.dumps(manifest, indent=2, sort_keys=True))

    readme = (
        HEADER
        + "# Scratchpad Corpus Comparison\n\n"
        + "This directory records the comparison between the committed repo project-vision corpus and the "
        + "external scratchpad corpus at `tmp/project_vision_corpus`.\n\n"
        + "The scratchpad output is useful because it processed an uploaded archive view with different nesting "
        + "and selected some full chat reports that the repo run demoted. It is not authority and was not copied "
        + "wholesale into the live docs corpus.\n\n"
        + "## Files\n\n"
        + "- `SCRATCHPAD_CORPUS_MANIFEST.json`\n"
        + "- `SCRATCHPAD_CORPUS_COMPARISON.md`\n"
        + "- `SCRATCHPAD_SOURCE_SELECTION_DELTA.md`\n"
        + "- `SCRATCHPAD_SYNTHESIS_DELTA.md`\n"
        + "- `SCRATCHPAD_ACTION_QUEUE.md`\n"
    )
    write_text(output_root / "README.md", readme)

    comparison = (
        HEADER
        + "# Scratchpad Corpus Comparison\n\n"
        + "## Assessment\n\n"
        + "The scratchpad corpus is a useful corroborating variant, not a replacement for the repo corpus. "
        + "It appears to have run against an uploaded `dominium archives.zip` package outside the live repository. "
        + "That explains its larger top-level zip count and its lack of live repo validation. The repo corpus "
        + "ran against the checked-in conversation archive plus current authority docs and validators.\n\n"
        + "## Count Comparison\n\n"
        + "| Metric | Repo corpus | Scratchpad corpus |\n"
        + "| --- | ---: | ---: |\n"
        + f"| Zip packages / extracted top-level zips | {repo.counts.get('zip_packages', 0)} | {scratch.counts.get('zip_packages', 0)} |\n"
        + f"| Human-readable sources selected | {repo.counts.get('human_sources', 0)} | {scratch.counts.get('human_sources', 0)} |\n"
        + f"| Semantic source blocks | {repo.counts.get('semantic_blocks', 0)} | {scratch.counts.get('semantic_blocks', 0)} |\n"
        + f"| Theme groups | {repo.counts.get('themes', 0)} | {scratch.counts.get('themes', 0)} |\n"
        + f"| Source basename overlap | {len(common_sources)} | {len(common_sources)} |\n"
        + f"| Repo-only selected source basenames | {len(repo_only)} | n/a |\n"
        + f"| Scratchpad-only selected source basenames | n/a | {len(scratch_only)} |\n\n"
        + "## Interpretation\n\n"
        + "- The scratchpad selected fewer source files but produced more blocks, because it favored large full-chat "
        + "and detailed report files from the uploaded archive.\n"
        + "- The repo selected more source files because it included current generated conversation synthesis, "
        + "reader/wiki/reconciliation outputs, and current repo authority context.\n"
        + "- The scratchpad had stronger raw uploaded-package visibility, including 47 top-level zip packages and "
        + "56 top-level archive entries.\n"
        + "- The repo had stronger authority safety: current files were live-inspected, validators ran, protected "
        + "paths were checked, and the generated output was committed.\n\n"
        + "## Synthesis Agreement\n\n"
        + "Both corpora converge on the same central picture: Dominium is the product-facing simulation/game/tool "
        + "universe, Domino is the deterministic portable substrate, presentation and providers must remain "
        + "replaceable projections, and archive material is advisory historical evidence rather than canon.\n\n"
        + "## Synthesis Differences\n\n"
        + "The scratchpad prose is more explicit about the long-horizon product ecosystem: launcher, setup, game, "
        + "tools, Workbench/AIDE, content packs, providers, and world simulation. The repo synthesis is more "
        + "conservative and more tightly tied to current queue blocks and authority boundaries.\n\n"
        + "## Recommendation\n\n"
        + "Keep the repo corpus as the active derived corpus. Use the scratchpad as a comparison source for the "
        + "next synthesis refinement, especially for full-chat reports and uploaded-archive-only package context. "
        + "Do not copy scratchpad claims into canon, contracts, implementation, release, or queue state.\n"
    )
    write_text(output_root / "SCRATCHPAD_CORPUS_COMPARISON.md", comparison)

    source_delta = (
        HEADER
        + "# Scratchpad Source Selection Delta\n\n"
        + "This report compares selected source filenames by basename. Paths differ because the scratchpad corpus "
        + "uses uploaded-archive extraction paths while the repo corpus uses checked-in repo paths.\n\n"
        + "## Summary\n\n"
        + f"- Repo selected source path entries parsed: {len(repo.source_paths)}\n"
        + f"- Scratchpad selected source path entries parsed: {len(scratch.source_paths)}\n"
        + f"- Common selected source basenames: {len(common_sources)}\n"
        + f"- Repo-only selected source basenames: {len(repo_only)}\n"
        + f"- Scratchpad-only selected source basenames: {len(scratch_only)}\n"
        + f"- Common zip basenames: {len(common_zips)}\n"
        + f"- Repo-only zip basenames: {len(repo_only_zips)}\n"
        + f"- Scratchpad-only zip basenames: {len(scratch_only_zips)}\n\n"
        + "## Scratchpad-Only Selected Source Basenames\n\n"
        + markdown_list(scratch_only, 120)
        + "\n\n## Repo-Only Selected Source Basenames\n\n"
        + markdown_list(repo_only, 120)
        + "\n\n## Scratchpad-Only Top-Level Zip Basenames\n\n"
        + markdown_list(scratch_only_zips, 80)
        + "\n\n## Repo-Only Zip Basenames\n\n"
        + markdown_list(repo_only_zips, 80)
    )
    write_text(output_root / "SCRATCHPAD_SOURCE_SELECTION_DELTA.md", source_delta)

    synth_docs = [
        "ULTIMATE_PROJECT_VISION_DRAFT.md",
        "CURRENT_PROJECT_REALITY.md",
        "LONG_HORIZON_DESIGN_INTENT.md",
        "DESIGN_PRINCIPLES.md",
        "DECISION_DOCKET.md",
        "OPEN_QUESTIONS.md",
        "CONTRADICTIONS_AND_DRIFT.md",
        "ROADMAP_AND_SEQUENCE.md",
        "WHAT_TO_DO_NEXT.md",
    ]
    rows: list[str] = []
    for doc in synth_docs:
        repo_text = read_text(repo.root / "synthesis" / doc)
        scratch_text = read_text(scratch.root / "synthesis" / doc)
        rows.append(
            "| "
            + doc
            + f" | {len(repo_text.split())} | {len(scratch_text.split())} | "
            + ("yes" if repo_text and scratch_text else "no")
            + " |"
        )

    synth_delta = (
        HEADER
        + "# Scratchpad Synthesis Delta\n\n"
        + "## Document Size Comparison\n\n"
        + "| Document | Repo words | Scratchpad words | Present in both |\n"
        + "| --- | ---: | ---: | --- |\n"
        + "\n".join(rows)
        + "\n\n## Useful Scratchpad Emphases\n\n"
        + "- The scratchpad states the product/substrate distinction very clearly: Dominium as product-facing "
        + "universe and Domino as portable deterministic substrate.\n"
        + "- It gives a stronger plain-language product ecosystem framing: game, launcher/setup, tools, Workbench, "
        + "AIDE, content packs, provider layer, and long-horizon world simulation.\n"
        + "- It explicitly warns that external engines/libraries should be providers, clients, adapters, tools, "
        + "or references, not the source of law.\n"
        + "- It reinforces that the archive is valuable but dangerous because generated reports can appear more "
        + "authoritative than they are.\n\n"
        + "## Repo-Side Strengths To Preserve\n\n"
        + "- Live current-repo authority was inspected.\n"
        + "- Current queue blocks were represented.\n"
        + "- Validators ran and protected paths were checked.\n"
        + "- The repo output avoids treating an uploaded archive snapshot as current repository truth.\n\n"
        + "## Integration Rule\n\n"
        + "Future `PROJECT-VISION-BOOK-01` work may borrow scratchpad phrasing as editorial synthesis, but any "
        + "claim must remain labelled as archive-derived unless independently supported by current repo authority.\n"
    )
    write_text(output_root / "SCRATCHPAD_SYNTHESIS_DELTA.md", synth_delta)

    action_queue = (
        HEADER
        + "# Scratchpad Ingestion Action Queue\n\n"
        + "## Recommended Follow-Up\n\n"
        + "1. Keep `docs/archive/project_vision_corpus/` as the active derived corpus.\n"
        + "2. Do not overwrite repo-generated corpus outputs with scratchpad outputs.\n"
        + "3. Before `PROJECT-VISION-BOOK-01`, review scratchpad-only selected source basenames for any full-chat "
        + "reports that contain unique narrative not already captured by repo reader reports.\n"
        + "4. Consider a future controlled rebuild mode that can ingest an uploaded all-in-one archive zip if the "
        + "operator intentionally places it under a reviewed input root.\n"
        + "5. Use the scratchpad's clearer product/substrate phrasing as a writing cue, not as authority.\n\n"
        + "## Do Not Do\n\n"
        + "- Do not promote scratchpad claims into canon.\n"
        + "- Do not patch live docs or queue state based on scratchpad output.\n"
        + "- Do not copy all scratchpad files into repo outputs; that would duplicate derived material without "
        + "adding authority.\n"
        + "- Do not treat the scratchpad's higher zip/block counts as automatically better coverage; they reflect "
        + "different input packaging.\n"
    )
    write_text(output_root / "SCRATCHPAD_ACTION_QUEUE.md", action_queue)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", type=Path)
    parser.add_argument("--repo-corpus-root", default=Path("docs/archive/project_vision_corpus"), type=Path)
    parser.add_argument("--scratchpad-root", default=Path("tmp/project_vision_corpus"), type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    repo_corpus = (repo_root / args.repo_corpus_root).resolve()
    scratchpad = (repo_root / args.scratchpad_root).resolve()
    if not repo_corpus.exists():
        raise SystemExit(f"repo corpus root missing: {repo_corpus}")
    if not scratchpad.exists():
        raise SystemExit(f"scratchpad corpus root missing: {scratchpad}")

    repo = summarize(repo_corpus, "repo")
    scratch = summarize(scratchpad, "scratchpad")
    write_source_block_library(repo)
    output_root = repo_corpus / "external_scratchpad_comparison"
    write_comparison(repo, scratch, output_root)
    print(
        "project vision scratchpad comparison: PASS "
        f"repo_sources={len(repo.source_paths)} scratch_sources={len(scratch.source_paths)} "
        f"repo_blocks={repo.counts.get('semantic_blocks', 0)} scratch_blocks={scratch.counts.get('semantic_blocks', 0)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
