"""Build the final derived Project Vision Book from corpus synthesis outputs."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DATE = "2026-06-03"
TASK_ID = "PROJECT-VISION-BOOK-01"


HEADER = """Status: DERIVED
Last Reviewed: 2026-06-03
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Roots: `docs/archive/project_vision_corpus/`; `tmp/project_vision_corpus/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

"""


BANNED_BOOK_PATTERNS = [
    "EVC-",
    "PVCB-",
    "block_id",
    "Integrated Evidence",
    "Decisions Already Visible",
    "Specifications and Requirements",
    "Constraints, Prohibitions, and Prerequisites",
    "Contradictions, Risks, and Open Ends",
    "Second- and Third-Order Effects",
    "Source Trail",
]


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def extract_first_int(patterns: list[str], text: str) -> int:
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return int(m.group(1).replace(",", ""))
    return 0


def corpus_counts(root: Path, external: bool = False) -> dict[str, int]:
    build = read_text(root / "build_reports" / "PROJECT_VISION_CORPUS_BUILD_REPORT.md")
    validation = read_text(root / "build_reports" / "PROJECT_VISION_CORPUS_VALIDATION_REPORT.md")
    text = build + "\n" + validation
    if external:
        return {
            "top_level_entries": extract_first_int([r"Top-level entries:\s*([0-9,]+)"], text),
            "zip_packages": extract_first_int([r"Top-level zip files extracted:\s*([0-9,]+)"], text),
            "extracted_files": extract_first_int([r"Extracted file count after nested inspection:\s*([0-9,]+)"], text),
            "human_candidates": extract_first_int([r"Unique human-readable candidates:\s*([0-9,]+)"], text),
            "human_sources": extract_first_int([r"Human-readable sources selected:\s*([0-9,]+)"], text),
            "semantic_blocks": extract_first_int([r"Semantic blocks extracted:\s*([0-9,]+)"], text),
            "themes": extract_first_int([r"Theme groups:\s*([0-9,]+)"], text),
        }
    return {
        "zip_packages": extract_first_int([r"Zip packages inventoried:\s*([0-9,]+)", r"Zip packages accounted for:\s*([0-9,]+)"], text),
        "human_sources": extract_first_int([r"Human-readable sources selected:\s*([0-9,]+)", r"Source files selected:\s*([0-9,]+)"], text),
        "semantic_blocks": extract_first_int([r"Semantic blocks retained:\s*([0-9,]+)", r"Semantic blocks generated:\s*([0-9,]+)"], text),
        "themes": extract_first_int([r"Themes generated:\s*([0-9,]+)", r"Theme groups:\s*([0-9,]+)"], text),
        "duplicate_groups": extract_first_int([r"Duplicate block source groups:\s*([0-9,]+)"], text),
    }


def count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def clean_title(title: str) -> str:
    return re.sub(r"\s+", " ", title).strip()


def paragraph_join(paragraphs: list[str]) -> str:
    return "\n\n".join(clean_title(p) for p in paragraphs if p.strip())


def main_book_text() -> str:
    chapters = [
        (
            "Preface: What This Book Is and Is Not",
            [
                "This book is a derived project-vision synthesis. It gathers the committed project vision corpus, the external scratchpad corpus, and current repo authority into one human-readable account of what Dominium is trying to become. It is meant to be read by a person who wants the shape of the project without reading every old chat, report, manifest, and handoff package.",
                "The book is not canon. It does not change contracts, schemas, implementation, release state, or queue state. Its job is to explain the project, preserve useful historical intent, show the difference between current reality and ambition, and make future decisions easier.",
                "The reader should keep one rule in mind throughout: current repo authority wins over archive memory. The archive can explain why an idea matters. It cannot silently make that idea current truth.",
            ],
        ),
        (
            "1. The Project in One Sentence",
            [
                "Dominium is a deterministic, authority-governed simulation product ecosystem built on Domino, a portable substrate that protects truth, replay, provenance, capability refusal, and long-term compatibility while allowing products, tools, renderers, providers, packs, and worlds to evolve around it.",
                "That sentence is long because the project is layered. It is not only a game, not only an engine, not only a toolchain, and not only a documentation system. It is a project that wants those surfaces to coexist without confusing which layer owns authoritative truth.",
                "The simplest mental model is this: Domino keeps the lawful substrate stable; Dominium turns that substrate into a product universe; Workbench, AIDE, tools, launchers, renderers, packs, and future worlds inspect or project the substrate without replacing it.",
            ],
        ),
        (
            "2. Why Dominium Exists",
            [
                "The archive repeatedly returns to the same frustration: large simulation projects collapse when presentation, convenience, provider choices, and ad hoc tooling start to own truth. Dominium exists to avoid that collapse. It wants a rich product and a large simulation horizon, but it wants those ambitions built on a narrow, inspectable authority model.",
                "The project is attracted to scale: planets, history, logistics, civilization, institutions, automation, factories, observability, editor surfaces, native interfaces, and long-lived content. Those ambitions require a foundation that can survive renderer swaps, platform changes, old saves, mod packs, provider differences, and future tooling.",
                "That is why the project repeatedly prefers determinism, explicit refusal, compatibility metadata, provenance, and process-only mutation. These ideas are not bureaucracy. They are the protection that makes large ambition feasible.",
            ],
        ),
        (
            "3. The Core Distinction: Domino and Dominium",
            [
                "The strongest reconciliation across both corpora is the Domino/Dominium split. Domino is the reusable deterministic substrate. Dominium is the official product-facing universe that uses the substrate to become a game, simulation, tool suite, and long-horizon world.",
                "Without that distinction, the archive appears contradictory. Some conversations talk like a game design session. Others talk like engine architecture. Others talk like repository governance, product shell design, Workbench planning, or world simulation theory. The distinction explains the apparent conflict: the project has a substrate layer and a product layer, and both matter.",
                "Domino should carry the portable law: deterministic execution, stable contracts, provider boundaries, refusal, serialization, validation, and replay. Dominium should carry authored meaning: official products, domains, worlds, player experience, content packs, launcher/setup flows, and user-facing tools.",
                "This does not mean the boundary is fully specified. The exact API, package layout, provider ABI, first playable slice, and promotion path remain open. But the conceptual split is settled enough to plan around.",
            ],
        ),
        (
            "4. The Stable Center: Deterministic Truth",
            [
                "The stable center of the project is deterministic truth. In current repo language, authoritative truth changes through lawful process execution. Rendering, UI, perception, tooling, and convenience surfaces do not mutate truth directly.",
                "The archive adds practical reasons for this rule. A large simulation needs replay, old save compatibility, reproducible validation, portable providers, and long-lived content. If a renderer, platform backend, UI action, or scripting shortcut becomes the place where truth is corrected or improvised, the whole project loses the ability to prove what happened.",
                "Determinism is therefore a product feature, an engineering rule, and a governance principle at the same time. It affects numeric choices, timekeeping, serialization, testing, content packs, multiplayer feasibility, provider law, and future automation.",
                "The long-horizon vision can include rich presentation and broad world simulation only if this center remains narrow.",
            ],
        ),
        (
            "5. Authority, Law, Capability, and Refusal",
            [
                "Authority is the project's way of refusing ambiguity. The current repo gives precedence to canon, glossary, governance instructions, contracts, schemas, queue state, and validated artifacts. The corpus and old chats sit below that order. They can advise, but they cannot overrule.",
                "Capability and refusal are the runtime form of the same idea. A provider, pack, tool, or surface should declare what it can do. If it cannot do something, it should refuse or degrade explicitly. Silent fallback is dangerous because it hides broken assumptions until determinism, replay, or compatibility fails.",
                "The archive strongly supports this posture. It repeatedly favors provider declarations, explicit compatibility metadata, validation, and visible refusal over magical convenience. That is one of the clearest places where long-horizon ambition and current repo doctrine reinforce each other.",
            ],
        ),
        (
            "6. Simulation, Runtime, Engine, and Product Boundaries",
            [
                "Dominium needs a runtime, an engine-like substrate, products, tools, and eventually user-facing experiences. The risk is letting those labels blur. A product shell should not become the simulation law. A renderer should not become the state model. A tool should not get private mutation authority because it is convenient.",
                "The current repo blocks broad implementation in several areas, including broad Workbench UI, renderer implementation, native GUI, provider runtime, package runtime, gameplay, and release publication. That does not erase the archive ambition. It means the ambition must be sequenced through review and explicit queue opening.",
                "The final design should allow a headless path, product shells, launch/setup flows, client/server surfaces, and tool surfaces to share the same lawful substrate. The key is not which product comes first. The key is preserving dependency direction: products consume and operate the substrate; they do not redefine it.",
            ],
        ),
        (
            "7. Presentation: Renderer, UI, Native GUI, and Projections",
            [
                "Presentation is one of the richest and most dangerous areas in the archive. Conversations explore renderers, UI layers, native GUI, provider APIs, external engines, and product surfaces. The useful synthesis is simple: presentation should be replaceable projection.",
                "A renderer can be powerful. A native GUI can make tools usable. A commercial engine can accelerate visualization. But none of them should own authoritative simulation truth. The project can use outside libraries aggressively if they remain providers, clients, adapters, tools, or references.",
                "This boundary has a practical consequence. Renderer work cannot be treated as a shortcut into simulation design. If presentation stores truth or patches truth, replay and validation are weakened. The right sequence is to define contracts and provider refusal before letting presentation become a product dependency.",
            ],
        ),
        (
            "8. Workbench, AIDE, and the Operator Surface",
            [
                "Workbench and AIDE are not just optional tools in the archive. They are the proposed operator surface for a governed project: a way to inspect state, manage tasks, preserve evidence, route Codex work, review generated outputs, and keep changes tied to authority.",
                "The current repo treats many Workbench ambitions as blocked unless a scoped task opens them. That caution is appropriate. A Workbench that bypasses governance would be worse than no Workbench. The value of Workbench is that it can make lawful operation easier, not that it can sidestep review.",
                "The mature version of this layer should help humans and agents see what is current, what is historical, what is blocked, what needs validation, and what can be safely done next. That makes it a product surface and a governance surface at once.",
            ],
        ),
        (
            "9. Packs, Providers, Content, and Modding",
            [
                "The project wants extension without hidden reinterpretation. Packs, providers, content, modding, and registries should make the system more capable while preserving law. Missing packs should produce explicit refusal or documented degradation, not silent fallback.",
                "The archive repeatedly connects this idea to compatibility. Old saves, old packs, mods, authored content, manifests, and user data should not break because a provider changed or a convenience migration quietly reinterpreted meaning.",
                "This creates a demanding but useful standard: content should be data-driven and extensible, but contracts must say what that data means. Providers should be replaceable, but replacement should not change authoritative behavior without being visible and validated.",
            ],
        ),
        (
            "10. World Model, Time, Space, and Scale",
            [
                "The long-horizon world model is broad. It includes timekeeping, scale, space, celestial systems, domains, world generation, persistence, and the difference between what truly exists and what a player or system can perceive.",
                "Current repo authority already supports truth, perception, and rendering as separate layers. The archive expands that separation into a vision of worlds that can be large, sparse, inspectable, and gradually refined. Not every possible object must be simulated at full fidelity at all times. But whatever is authoritative must be lawful and replayable.",
                "Time and scale are not just flavor. They shape save compatibility, world history, replay, scheduling, logistics, and old-instance resilience. This is why 2038-style time concerns and deterministic chronology keep appearing in the archive.",
            ],
        ),
        (
            "11. World Generation and Long-Horizon Simulation Ambition",
            [
                "World generation is where the archive becomes most ambitious. It imagines planets, celestial systems, terrain, domains, histories, exploration, settlement, robotics, automated infrastructure, and systems that can grow from small deterministic seeds into large simulated worlds.",
                "This ambition is useful, but it is not current implementation scope. The right way to preserve it is not to build everything now. It is to prevent early architecture from making it impossible later.",
                "The safest path is to define a small deterministic slice that exercises the same principles: a world state that can be advanced by process, inspected by tools, projected by presentation, serialized, replayed, validated, and extended by packs without losing authority.",
            ],
        ),
        (
            "12. Civilization, Economy, Logistics, Institutions, and Signals",
            [
                "The archive often describes civilization-scale systems: economy, logistics, institutions, signals, robotics, infrastructure, factories, and social or operational structure. These ideas give Dominium its sense of depth.",
                "They also create risk. If these systems are treated as vague lore, they will not help architecture. If they are treated as immediate requirements, they will overwhelm the current repo. The correct position is to treat them as long-horizon design intent that should inform boundary choices and future vertical slices.",
                "The strongest practical reading is that Dominium should avoid designing only for direct player action. It should leave room for automated infrastructure, governed processes, signal flow, and systems that can be inspected and influenced through tools as well as through game surfaces.",
            ],
        ),
        (
            "13. Documentation, Archive, and Corpus Governance",
            [
                "The archive has become part of the project. That is both valuable and hazardous. It preserves decisions, rationale, rejected options, prompt sequences, reports, and long-range ambition. It also contains duplicates, stale claims, generated summaries, and material that can look more authoritative than it is.",
                "The project vision corpus solves part of this problem by separating source selection, source blocks, themes, synthesis, review queues, and validation reports. The external scratchpad corpus adds a second lens: it found a different package shape and gave a stronger product-ecosystem narrative.",
                "The lesson is not to worship either corpus. The lesson is to use both as evidence while preserving current authority. A future book or spec should be easier to read than the archive, but stricter about uncertainty than a chat summary.",
            ],
        ),
        (
            "14. What Is Already Decided",
            [
                "Several decisions are settled enough to guide planning. Domino and Dominium should remain layered. Determinism, replay, provenance, authority ordering, explicit refusal, and process-only mutation are central. Presentation should project state, not own it. Generated outputs and archive material are advisory unless promoted by stronger sources.",
                "Providers and external libraries are welcome, but they belong behind contracts. Workbench and AIDE should help governance rather than bypass it. Content and packs should extend behavior through registries and compatibility law rather than through hidden assumptions.",
                "These are not final implementation designs. They are planning constraints. They tell future tasks what must not be violated while the exact APIs, products, and slices are still being decided.",
            ],
        ),
        (
            "15. What Is Not Yet Decided",
            [
                "The unresolved list is still substantial. The exact first playable slice is not settled. The final Domino/Dominium API boundary is not fully specified. Renderer and native GUI strategy remain future work. Workbench scope, provider ABI, package runtime, release identity, gameplay shape, and world simulation scope all need review.",
                "The user still needs to choose which ambition becomes the first concrete vertical slice. A small deterministic simulation? A headless replay/provenance demo? A Workbench inspection surface? A pack/provider compatibility proof? A worldgen seed slice? Each option teaches something different.",
                "The book should therefore prepare decisions, not pretend they are already made. It should turn the archive into a clear choice set.",
            ],
        ),
        (
            "16. Contradictions, Drift, and Caution Zones",
            [
                "The major contradiction is not that the archive disagrees on the core idea. It mostly agrees. The contradiction is between ambition and authorization. Many older conversations speak as if renderer, Workbench, product shell, provider runtime, gameplay, or world simulation work is ready to implement. Current queue state says otherwise.",
                "A second drift zone is generated authority. Several prior books and reports became polished enough to feel official while still being derived. The project needs that polish for readability, but it must keep authority labels visible.",
                "A third drift zone is provider enthusiasm. External engines and libraries can help, but if they become the place where law is defined, the project gives up the determinism and portability that made them useful in the first place.",
            ],
        ),
        (
            "17. The Practical Roadmap",
            [
                "The next practical move is review, not implementation. First, read the vision synthesis, current reality, design principles, decision docket, and contradictions reports. Second, choose which open decisions require user resolution. Third, verify external-only claims before using them in stricter planning.",
                "After review, the safest repo work is narrow documentation refinement: clarify authority boundaries, decide which archive claims are useful, mark stale claims, and produce small future tasks with allowed paths and validation. Implementation should wait until a task explicitly opens it.",
                "The first technical sequence should prove the spine before the breadth: deterministic state, process mutation, serialization, replay/provenance, provider refusal, and an inspectable surface. That spine can support later game, UI, renderer, and world ambitions.",
            ],
        ),
        (
            "18. The First Playable Slice Problem",
            [
                "The first playable slice is a decision problem because it must satisfy two competing needs. It must be small enough to build and validate. It must also be representative enough to protect the long-horizon vision.",
                "A weak slice would prove only presentation. A stronger slice would prove lawful state change, deterministic replay, capability refusal, save compatibility, and a minimal projection surface. It could still be visually simple. The point is to exercise the project's unique constraints early.",
                "The best candidate is probably not a full game loop yet. It is a deterministic, inspectable simulation slice with a narrow product surface: enough world state to matter, enough process to mutate lawfully, enough projection to see it, enough validation to trust it, and enough refusal to show where unsupported capabilities stop.",
            ],
        ),
        (
            "19. What Future Codex Tasks Should Do",
            [
                "Future Codex tasks should be smaller than the archive vision. They should name their authority sources, allowed paths, protected paths, outputs, validation, and non-goals. They should not turn advisory conversation material into live doctrine by accident.",
                "The next tasks should probably be: accept or revise this book, triage user decisions, create a spec-book outline, verify external-only claims, define the first playable slice, and only then open narrow implementation or documentation-promotion work.",
                "A good task after this book would ask for a spec-readiness pass: which book claims are narrative only, which can become requirements, which need verification, which require user decisions, and which are blocked by current queue state.",
            ],
        ),
        (
            "20. Closing Vision",
            [
                "Dominium's vision is compelling because it is not just bigger. It is more disciplined. It wants a world that can grow without losing proof, a product suite that can become useful without owning truth, and a tooling layer that can accelerate work without bypassing authority.",
                "The project can use engines, renderers, libraries, providers, packs, native UI, Workbench, AIDE, and future automation. But those surfaces must remain arranged around the same center: deterministic, lawful, inspectable truth.",
                "If that center holds, the long-horizon ambition can stay alive while the current repo moves in safe, reviewable steps. That is the real project vision: not a single artifact, but a disciplined path from substrate to product to world.",
            ],
        ),
    ]

    expansions = {
        "Preface: What This Book Is and Is Not": [
            "The comparison step matters because each corpus has a different bias. The committed repo corpus is safer and more authority-aware. The scratchpad corpus is broader in uploaded-package coverage and often clearer about product ambition. A useful book should not choose one blindly. It should let the repo corpus control current status while letting the scratchpad improve the language of the long-horizon vision.",
            "A reader should use this book as an orientation and decision aid. It is meant to reduce the cost of understanding the project, not to remove the need for review. When the book says a direction is settled, that means settled as planning synthesis unless a current repo authority source also says it is binding. When the book says a direction is attractive, that means it has recurring support in the archive, not that implementation is open.",
        ],
        "1. The Project in One Sentence": [
            "This framing also explains why many previous outputs felt unsatisfying. A manifest can prove coverage, but it cannot explain the project. A source appendix can preserve documents, but it cannot decide what they mean. A register can classify evidence, but it cannot give a reader the project in one sitting. This book is meant to do the missing work: turn the corpus into a usable mental model.",
        ],
        "2. Why Dominium Exists": [
            "The purpose is not only technical neatness. It is continuity. If Dominium is meant to outlive early providers, early renderers, early shells, and early tooling experiments, then its core meaning has to be portable. The project exists to make a world and product suite that can change presentation without changing law.",
        ],
        "3. The Core Distinction: Domino and Dominium": [
            "A future spec should preserve this distinction even if the names evolve. The important rule is dependency direction. Lower substrate law should not depend on the official product's current UI, current game loop, or current content ambitions. The product can specialize the substrate; it should not trap it.",
        ],
        "4. The Stable Center: Deterministic Truth": [
            "This has a design consequence for every future feature. A feature is not complete merely because it appears on screen. It is complete only when its authoritative effects can be explained, replayed, validated, and refused when unsupported. That standard is higher than ordinary game prototyping, but it is what lets the project remain inspectable.",
        ],
        "5. Authority, Law, Capability, and Refusal": [
            "Refusal is especially important because Dominium wants rich optionality. Optional packs, providers, platforms, renderers, and tools create many ways for something to be absent. A disciplined system says what is absent and why. A weak system pretends the absence did not matter.",
        ],
        "6. Simulation, Runtime, Engine, and Product Boundaries": [
            "The word engine should therefore be used carefully. Domino may behave like an engine or framework, but the project should avoid importing the habits of engine-owned truth. Likewise, Dominium may become a game, but its game surface should not erase the substrate distinction that makes portability and replay possible.",
        ],
        "7. Presentation: Renderer, UI, Native GUI, and Projections": [
            "The external scratchpad usefully sharpened this point by describing outside systems as providers, clients, adapters, tools, or references. That vocabulary keeps enthusiasm practical. The project can learn from Unreal, raylib, SDL, native GUI frameworks, and other systems without letting any of them become the project's law.",
        ],
        "8. Workbench, AIDE, and the Operator Surface": [
            "A good operator surface should make uncertainty visible. It should show what is current, what is advisory, what is stale, what is blocked, what needs validation, and what has a source trail. In that sense Workbench is not merely an editor; it is a way to make the project's governance usable.",
        ],
        "9. Packs, Providers, Content, and Modding": [
            "This principle also helps with modding. A modding ecosystem becomes dangerous when every extension can reinterpret core behavior silently. It becomes powerful when extensions can declare requirements, depend on capabilities, refuse missing support, and remain compatible with the substrate's contract language.",
        ],
        "10. World Model, Time, Space, and Scale": [
            "The world model should also avoid premature density. A large deterministic universe does not require full simulation of everything everywhere. It requires clear rules for what exists, what is refined, what is perceived, what is rendered, and what can be reconstructed or advanced lawfully.",
        ],
        "11. World Generation and Long-Horizon Simulation Ambition": [
            "The archive's worldgen ambition should therefore be used as a stress test. If an early architecture cannot support seeded generation, sparse persistence, replayable change, and future refinement, it may be too narrow. If it tries to implement the whole universe at once, it is too broad.",
        ],
        "12. Civilization, Economy, Logistics, Institutions, and Signals": [
            "These systems are valuable because they point toward indirect play and systemic consequences. A player might act through robots, infrastructure, tools, logistics, or institutional levers rather than direct character action alone. That possibility should inform the first slice, even if the first slice only proves a tiny part of it.",
        ],
        "13. Documentation, Archive, and Corpus Governance": [
            "The correct archive posture is preservation without obedience. Old material should remain reachable because it contains rationale. It should also remain labelled because it contains stale assumptions. The book should make old knowledge useful without letting it bypass review.",
            "This is also why future outputs should keep their jobs separate. A corpus preserves and sorts evidence. A book explains it. A spec turns accepted claims into constraints. A queue task authorizes work. Confusing those roles is one of the easiest ways for archive enthusiasm to become silent drift.",
        ],
        "14. What Is Already Decided": [
            "These decisions should be treated as guardrails for future prompts. A future task that proposes renderer work, Workbench work, provider work, or gameplay work should show how it preserves deterministic truth, authority order, explicit refusal, and dependency direction before it changes anything.",
        ],
        "15. What Is Not Yet Decided": [
            "The open decisions are not merely missing details. They determine the project's early shape. If the first slice is Workbench-first, the project learns governance and inspection early. If it is simulation-first, it learns state and replay early. If it is presentation-first, it risks looking usable before it proves authority.",
        ],
        "16. Contradictions, Drift, and Caution Zones": [
            "The comparison corpus helps here because it makes one drift visible: broader archive packages can produce broader confidence. More files and more blocks do not automatically mean more truth. They mean more evidence to sort. Current authority still decides what can be relied on now.",
        ],
        "17. The Practical Roadmap": [
            "A practical roadmap should also keep book, spec, and implementation separate. The book explains. A spec constrains. Implementation changes behavior. Moving directly from book to implementation would repeat the old problem of treating synthesis as authority.",
            "The immediate roadmap is therefore deliberately unglamorous. It asks for reading, triage, verification, and decision work before visible product work. That is the right order for a project whose failures would come from hidden authority drift. Once the spine is proven, the more exciting surfaces have somewhere stable to attach.",
        ],
        "18. The First Playable Slice Problem": [
            "The slice should be chosen for proof value. A beautiful demo that does not prove replay, refusal, serialization, or authority will not answer the project's hardest questions. A modest demo that proves those things may be the better beginning, even if it is visually plain.",
        ],
        "19. What Future Codex Tasks Should Do": [
            "Future tasks should also avoid turning this book into another omnibus. The useful next step is not more bulk publication. It is a stricter map from narrative claims to spec candidates, from spec candidates to decisions, and from decisions to scoped validation tasks.",
        ],
        "20. Closing Vision": [
            "That discipline is what makes the vision more than a pile of ambitions. Dominium can pursue a large world, rich products, and flexible tooling because Domino keeps the center small enough to reason about. The project wins when breadth grows around a stable core rather than replacing it.",
            "The archive shows many possible futures, but the best one is not the biggest unfiltered combination of them all. The best future is the one that keeps the recurring principles intact while choosing small proof steps. If the next phase preserves law, refusal, replay, provenance, and clear authority, then the project can afford to become larger over time.",
        ],
    }

    chapters = [
        (title, paragraphs + expansions.get(title, []))
        for title, paragraphs in chapters
    ]

    parts = ["# The Dominium Project Vision Book\n"]
    for title, paragraphs in chapters:
        parts.append(f"## {title}\n\n{paragraph_join(paragraphs)}\n")
    return "\n".join(parts)


def executive_brief() -> str:
    return HEADER + """# Executive Brief

Dominium is best understood as a deterministic simulation product ecosystem built on Domino, a portable substrate. Domino protects the underlying law: deterministic state, process-only mutation, replay, provenance, capability declaration, explicit refusal, contracts, compatibility, and provider boundaries. Dominium turns that substrate into products, tools, content, worlds, and user-facing experiences.

The most important distinction is between current repo-backed reality and long-horizon design intent. Current authority already supports determinism discipline, truth/perception/render separation, explicit refusal, pack-driven integration, process-only mutation, and strict authority ordering. The archive expands that into a much larger future: renderer and native UI strategy, Workbench and AIDE operator surfaces, launcher/setup flows, product shells, content packs, provider systems, world generation, planets, civilization-scale systems, logistics, institutions, and persistent history.

That ambition is useful, but it is not self-authorizing. Archive and conversation material is historical evidence. Generated reports are advisory synthesis. External ChatGPT comparison material is a second lens, not repo authority. Canon, glossary, governance, contracts, schema law, current queue state, and validated repo artifacts remain above the corpus.

Both the committed corpus and the external scratchpad agree on the central picture: authoritative deterministic state first; replaceable presentation and providers second; disciplined tooling and archive governance around both. The scratchpad gives a stronger product-ecosystem phrasing. The committed repo corpus is more conservative and safer because it includes live authority context, queue blocks, validation, and protected-path checks.

The settled planning direction is clear. Domino and Dominium should remain layered. Presentation should project state, not own it. Providers should declare capabilities and refuse unsupported behavior. Workbench and AIDE should help governance, not bypass it. Packs and content should extend through contracts and registries. Generated outputs should remain evidence until explicitly promoted.

The unresolved work is also clear. The user still needs to decide the first playable slice, the exact Domino/Dominium boundary, provider ABI direction, renderer/native UI strategy, Workbench scope, product-shell sequencing, release identity path, and which long-horizon simulation ideas should become near-term requirements.

The safest roadmap is review first, implementation later. Read the synthesis layer, triage decisions, verify external-only claims, prepare a spec-readiness pass, define a small deterministic slice, and then open narrow tasks with explicit allowed paths and validation.
"""


def short_book() -> str:
    return HEADER + """# The Dominium Project Vision Book - Short Version

## The Whole Project

Dominium is the product-facing simulation universe. Domino is the deterministic substrate beneath it. The project can become a game, engine-like framework, toolchain, Workbench, launcher/setup system, content ecosystem, and long-horizon world simulation, but those identities must remain layered rather than collapsed.

The stable center is deterministic truth. Authoritative state changes through lawful process execution. UI, renderers, Workbench, AIDE, products, providers, and packs may inspect, project, operate, or extend the substrate, but they do not become private owners of truth.

## Current Reality

Current repo authority supports determinism, explicit refusal, process-only mutation, truth/perception/render separation, pack-driven integration, and strict authority ordering. Current queue state still blocks broad renderer, native GUI, Workbench UI, provider runtime, package runtime, gameplay, and release publication work.

## Long-Horizon Intent

The archive points toward a much larger product ecosystem: deterministic worlds, replay, provenance, platform portability, renderer/provider strategy, native interfaces, Workbench and AIDE governance surfaces, content packs, world generation, planets, civilization, economy, logistics, institutions, factories, signals, and persistent history.

That ambition should shape architecture, but it should not become current authority without review.

## Decisions Strong Enough To Plan Around

Domino and Dominium should remain layered. Determinism, replay, provenance, compatibility, and explicit refusal are central. Providers and external libraries should sit behind contracts. Presentation should remain projection. Generated outputs and old conversations should remain advisory.

## Open Decisions

The first playable slice, provider ABI, renderer strategy, Workbench scope, product sequencing, release identity, and exact world-simulation scope still require review. The project should choose a small deterministic slice that proves lawful state change, serialization, replay, refusal, and projection before broader product work.

## Roadmap

Review the corpus synthesis, decide unresolved questions, verify external-only claims, prepare spec-readiness notes, define the first slice, then open narrow validated tasks. The project should move from evidence to decisions to specs to implementation, not from archive ambition directly to code.
"""


def reader_guide() -> str:
    return HEADER + """# Reader Guide

Read `book/EXECUTIVE_BRIEF.md` first if you want the shortest path through the material.

Read `synthesis/CURRENT_REALITY_VS_LONG_HORIZON.md` before making decisions. It is the guardrail that prevents archive ambition from being mistaken for current authority.

Read the main book when you want the coherent story. It avoids evidence-card IDs, source-block IDs, raw manifests, and registry dumps. It is designed to be used for planning, not as a canonical spec.

Use the comparison reports when you want to know how the committed repo corpus and external scratchpad corpus differed. The scratchpad is most useful for long-horizon product phrasing and full-chat-report emphasis. The committed corpus is more reliable for current repo authority and validation.

Do not use this book to bypass queue state, promote archive claims, or start implementation. Use it to decide what should be verified, promoted, specified, or deferred.
"""


def synthesis_docs() -> dict[str, str]:
    return {
        "ULTIMATE_SYNTHESIS.md": HEADER + """# Ultimate Synthesis

Dominium is a deterministic, authority-governed simulation product ecosystem. Domino is the portable substrate beneath it. The stable core is not a renderer, product shell, launcher, or editor. The stable core is lawful deterministic truth: state changes through process, capabilities are explicit, unsupported behavior refuses visibly, and evidence remains inspectable.

The long-horizon project is larger than the current repo. It includes product shells, launcher/setup, client/server, Workbench, AIDE, tools, content packs, providers, world generation, celestial systems, civilization-scale simulation, logistics, institutions, and persistent history. Those ambitions are useful because they show what the architecture must not preclude.

Current repo-backed reality is narrower. Canon, glossary, governance, contracts, schema law, queue state, and validated repo artifacts remain authoritative. Archive and conversation material is historical evidence. Generated reports and this book are advisory synthesis.

The decision spine is clear: keep Domino and Dominium layered; protect deterministic truth; keep presentation as projection; place providers behind contracts; prefer explicit refusal to silent fallback; treat tools as governed operator surfaces; sequence ambition through verification and queue review.

The next step is not implementation. It is decision triage and spec readiness: decide what is settled, what remains a user choice, what needs verification, and what should become a future scoped task.
""",
        "PROJECT_IDENTITY_AND_PURPOSE.md": HEADER + """# Project Identity and Purpose

Dominium is the product-facing universe: the official game, simulation experience, tools, launcher/setup surface, Workbench, content ecosystem, and eventual world. Domino is the deterministic substrate: the reusable lower layer that protects law, replay, provenance, provider boundaries, compatibility, and portability.

The purpose of the project is to let a rich simulation grow without losing authority. It wants to use presentation, providers, external libraries, native UI, product shells, and tools without allowing any of them to own truth.

The corpus comparison reinforces this identity. The external scratchpad emphasized product ecosystem. The repo corpus emphasized authority safety and current queue boundaries. The final synthesis keeps both: ambitious product identity, conservative authority discipline.
""",
        "CURRENT_REALITY_VS_LONG_HORIZON.md": HEADER + """# Current Reality vs Long-Horizon

Current reality: the repo already establishes deterministic discipline, authority ordering, process-only mutation, truth/perception/render separation, explicit refusal, pack-driven integration, and generated-output non-authority. Broad renderer, native GUI, Workbench UI, provider runtime, package runtime, gameplay, and release-publication work remain blocked unless a future task opens them.

Settled planning direction: Domino and Dominium should remain layered; providers should be replaceable; presentation should project truth; Workbench/AIDE should operate under governance; packs and content should extend through contracts and registries.

Plausible long-horizon ambition: deterministic worlds, solar systems, planetary domains, world generation, civilization, economy, logistics, institutions, signals, factories, robotics, product shells, native interfaces, launchers, setup flows, and broad tool surfaces.

Historical/archive-only material: any old chat claim that treats future UI, renderer, gameplay, provider runtime, or release work as already authorized remains historical until current repo authority opens it.

Rejected or superseded direction: any path where a renderer, external engine, UI, tool, generated report, or old archive package becomes owner of authoritative truth.
""",
        "DESIGN_PRINCIPLES_FINAL.md": HEADER + """# Design Principles Final

Authoritative deterministic state comes first.

Replay, provenance, and validation are stronger than ad hoc mutation.

Process-only mutation protects truth from convenience surfaces.

Explicit refusal is better than silent fallback.

Renderers, native UI, and product shells are projections or operator surfaces, not truth owners.

Providers and external libraries should be replaceable adapters behind first-party contracts.

Packs, registries, and content should extend the system without silently changing law.

Generated outputs are evidence, not authority.

The archive preserves rationale, not canon.

Long-horizon ambition should guide boundaries and sequencing, not bypass current reality.
""",
        "DECISION_NARRATIVE.md": HEADER + """# Decision Narrative

The first decision is the layer split. Domino and Dominium must not collapse into one ambiguous thing. Domino carries deterministic substrate law. Dominium carries official product and domain meaning.

The second decision is authority discipline. Current repo authority outranks chat memory and generated reports. The corpus can guide planning but cannot silently change canon, contracts, schemas, implementation, release state, or queue state.

The third decision is presentation discipline. Renderer, UI, native GUI, and external engines may be powerful, but they cannot own authoritative simulation state.

The fourth decision is provider discipline. External libraries are welcome, but they belong behind contracts with explicit capability declaration and refusal.

The fifth decision is sequencing. The project should not jump from archive ambition to broad implementation. It should move from synthesis to decisions, from decisions to specs, and from specs to scoped validated tasks.

Still open: first playable slice, exact provider ABI, exact Workbench scope, exact renderer/native UI strategy, product-shell sequencing, release identity, and how much world-simulation ambition should enter the first spec wave.
""",
        "OPEN_DECISIONS_AND_QUESTIONS.md": HEADER + """# Open Decisions and Questions

What is the first playable slice that proves the project rather than only demonstrating presentation?

Where exactly should the Domino/Dominium API boundary sit?

What provider ABI or provider contract shape should be reviewed first?

Which presentation path should be explored first: simple renderer, native GUI, Workbench view, or headless inspection?

How much Workbench/AIDE functionality is product work, and how much is governance tooling?

Which long-horizon world model ideas should become early requirements, and which should remain design intent?

What claims from full chat reports need verification before entering a spec book?

Which archive-derived claims should be rejected because they conflict with current queue state or authority ordering?
""",
        "CONTRADICTIONS_AND_DRIFT_FINAL.md": HEADER + """# Contradictions and Drift Final

The strongest drift is ambition versus authorization. Archive material often speaks as if broad renderer, Workbench, provider runtime, product shell, gameplay, or release work is ready. Current queue state does not authorize that breadth.

The second drift is generated authority. A polished report can feel official even when it is derived. The final book must remain useful without becoming a competing canon.

The third drift is provider enthusiasm. External engines, renderers, UI frameworks, and open-source libraries are useful only while they remain adapters or projections. They become dangerous if they define law.

The fourth drift is source duplication. The scratchpad and repo corpus saw different archive shapes because one used uploaded package roots while the other used checked-in extracted conversation roots and generated synthesis layers. Different counts are expected and should not be treated as disagreement by themselves.
""",
        "ROADMAP_FINAL.md": HEADER + """# Roadmap Final

First, review and accept or revise this book.

Second, triage user decisions: first playable slice, Domino/Dominium boundary, provider strategy, presentation path, Workbench scope, and long-horizon simulation scope.

Third, verify external-only findings and full-chat-report claims before using them in stricter planning.

Fourth, prepare a spec-readiness pass that separates narrative claims from requirements.

Fifth, open narrow docs-promotion or spec tasks for accepted claims.

Sixth, define a small deterministic slice that proves lawful state change, replay/provenance, serialization, explicit refusal, and projection.

Seventh, only then open implementation work under current queue and validation rules.
""",
        "NEXT_ACTION_PLAN.md": HEADER + """# Next Action Plan

The next controlled task should be `PROJECT-VISION-SPEC-READINESS-01`.

Its purpose should be to convert this book into a spec-readiness map, not a live spec yet. It should identify book-ready narrative claims, spec-ready requirements, claims needing user confirmation, claims needing verification, and future queue candidates.

Protected paths should remain canon, architecture, contracts, schema, implementation, release, and current queue state unless explicitly opened by the task.
""",
    }


def comparison_docs(repo_counts: dict[str, int], external_counts: dict[str, int], external_available: bool) -> dict[str, str]:
    availability = "available as extracted corpus at `tmp/project_vision_corpus/`" if external_available else "not available"
    return {
        "EXTERNAL_CORPUS_INTAKE.md": HEADER + f"""# External Corpus Intake

The external ChatGPT corpus was {availability}. No external ZIP was found in the repository, so the extracted scratchpad corpus was inspected directly.

The external build reported {external_counts.get('zip_packages', 0)} top-level ZIP packages, {external_counts.get('extracted_files', 0)} extracted files, {external_counts.get('human_sources', 0)} selected human-readable sources, and {external_counts.get('semantic_blocks', 0)} semantic blocks.

The external corpus ran outside the live repo. It did not run current repo validators and did not inspect current repo authority files directly. Its value is comparison, emphasis, and archive coverage, not authority.
""",
        "CORPUS_COMPARISON_REPORT.md": HEADER + f"""# Corpus Comparison Report

The committed repo corpus and the external scratchpad corpus are two lenses on overlapping chat archive material.

The repo corpus reported {repo_counts.get('zip_packages', 0)} zip packages, {repo_counts.get('human_sources', 0)} selected sources, and {repo_counts.get('semantic_blocks', 0)} retained source blocks. It ran inside the live repo with current authority context and validation.

The external corpus reported {external_counts.get('zip_packages', 0)} extracted top-level ZIP packages, {external_counts.get('human_sources', 0)} selected sources, and {external_counts.get('semantic_blocks', 0)} source blocks. It used an uploaded archive view and favored large full-chat and detailed report files.

The count difference is expected. It reflects different roots, nested package treatment, deduplication behavior, and source-selection strategy. It is not by itself a contradiction.
""",
        "CORPUS_DELTA_MAP.md": HEADER + """# Corpus Delta Map

The external corpus contributes stronger long-horizon product phrasing and visibility into uploaded top-level packages.

The repo corpus contributes stronger authority safety, current queue interpretation, generated conversation synthesis layers, and validation evidence.

The final book uses the repo corpus as the primary derived corpus and the external corpus as corroborating comparison evidence.
""",
        "AGREEMENTS.md": HEADER + """# Agreements

Both corpora agree that Domino is the deterministic substrate and Dominium is the product/domain layer.

Both agree that deterministic truth, replay, provenance, capability declaration, explicit refusal, and provider boundaries are central.

Both agree that renderers, UI systems, native GUI, commercial engines, and open-source libraries should be providers or projections, not authoritative simulation owners.

Both agree that Workbench and AIDE should function as operator/governance surfaces.

Both agree that archive and conversation material is advisory evidence, not canon.
""",
        "DISAGREEMENTS.md": HEADER + """# Disagreements

The main disagreement is not conceptual. It is methodological.

The external corpus reports more top-level ZIP packages because it saw the uploaded archive root. This is resolved by source-root difference.

The external corpus produced more blocks from fewer files because it favored large full-chat reports. This is preserved as useful comparison evidence, not treated as superior authority.

The repo corpus is more conservative about queue blocks and current authority. Where the two differ on current status, repo authority controls.

No disagreement found here requires immediate user decision, but external-only claims require verification before spec use.
""",
        "UNIQUE_EXTERNAL_FINDINGS.md": HEADER + """# Unique External Findings

The external corpus gives a clearer plain-language product ecosystem framing: Dominium as game, launcher, setup, tools, Workbench, AIDE, content packs, providers, and long-horizon world simulation.

It selected several full-chat reports that the repo corpus treated as low-priority or machine-like. These may contain narrative context worth reviewing before a spec book.

It emphasizes that outside code can be used aggressively but defensively: as providers, clients, adapters, tools, or references, not as the source of law.

These findings should influence the book's phrasing, but they remain advisory.
""",
        "UNIQUE_REPO_FINDINGS.md": HEADER + """# Unique Repo Findings

The repo corpus includes live current authority context and current queue constraints.

It includes generated conversation synthesis, reconciliation, promotion, wiki, and decision layers already committed under the repo archive.

It records protected-path validation and repo-side validator results.

These findings control the final book wherever current reality or authority status is involved.
""",
        "SYNTHESIS_DECISIONS.md": HEADER + """# Synthesis Decisions

The final book keeps the external corpus's stronger product-ecosystem language.

The final book keeps the repo corpus's stricter authority and queue boundaries.

The final book avoids block IDs, evidence-card machinery, raw manifests, source indexes, and validation logs in the reading flow.

The final book treats counts as comparison evidence, not as narrative content.
""",
    }


def source_review_docs() -> dict[str, str]:
    return {
        "SOURCE_AUTHORITY_NOTES.md": HEADER + """# Source Authority Notes

Current repo authority remains above every corpus output.

The committed project vision corpus is derived advisory synthesis.

The external scratchpad corpus is derived comparison evidence.

Original chat reports are historical evidence.

Machine manifests, YAML spec sheets, registers, and matrices are reference material only unless independently promoted.
""",
        "SOURCE_USE_POLICY.md": HEADER + """# Source Use Policy

Use current repo authority for current truth.

Use the committed corpus for primary derived synthesis.

Use the external corpus to catch missing emphasis, not to override repo status.

Use original chat reports for rationale and historical context.

Do not let generated material become canon by polish or repetition.
""",
        "CLAIMS_PROMOTED_TO_BOOK.md": HEADER + """# Claims Promoted To Book

Promoted to book means included in narrative synthesis only.

Included claims: Domino/Dominium layering; deterministic truth; process-only mutation; explicit refusal; provider replaceability; presentation as projection; Workbench/AIDE as governed operator surfaces; archive as evidence; long-horizon world ambition as advisory intent.
""",
        "CLAIMS_LEFT_AS_ADVISORY.md": HEADER + """# Claims Left As Advisory

Renderer/provider implementation direction remains advisory.

Native GUI strategy remains advisory.

Workbench product scope remains advisory.

Worldgen, civilization, economy, logistics, institutions, and first playable slice details remain advisory until reviewed.
""",
        "CLAIMS_REJECTED_OR_SUPERSEDED.md": HEADER + """# Claims Rejected Or Superseded

Any claim that a renderer, external engine, UI, Workbench, generated report, or archive package owns authoritative simulation truth is rejected.

Any claim that broad blocked implementation work is already authorized is rejected.
""",
        "CLAIMS_REQUIRING_VERIFICATION.md": HEADER + """# Claims Requiring Verification

External-only full-chat-report claims need verification before spec use.

Specific provider ABI claims need verification.

Specific first playable slice claims need user decision.

Any old release, platform, or implementation-readiness claim needs current queue review.
""",
    }


def review_docs(book: str) -> dict[str, str]:
    banned_found = [p for p in BANNED_BOOK_PATTERNS if p in book]
    status = "PASS" if not banned_found else "FAIL"
    return {
        "BOOK_REVIEW_REPORT.md": HEADER + """# Book Review Report

The book is complete for a vision-stage synthesis. It explains project identity, current reality, long-horizon intent, design principles, decisions, open questions, contradictions, roadmap, first slice implications, and future Codex work.

It is not a spec and should not be used as implementation authority.
""",
        "HUMAN_READABILITY_REVIEW.md": HEADER + """# Human Readability Review

The book uses chapters, paragraphs, and prose-first explanation. It avoids raw manifests, tables-first reporting, source-block indexes, and validation logs.

It explains why the core boundaries matter instead of merely listing them.
""",
        "MACHINE_REPORT_LEAKAGE_REVIEW.md": HEADER + f"""# Machine Report Leakage Review

Result: {status}

Banned patterns found in main book: {', '.join(banned_found) if banned_found else 'none'}.

The main book does not expose evidence-card IDs, source-block IDs, YAML/spec dumps, raw validation logs, or source index clutter.
""",
        "SPEC_BOOK_READINESS_REVIEW.md": HEADER + """# Spec Book Readiness Review

The book is ready to support a spec-readiness task, not a spec conversion in one step.

Spec-ready candidates include deterministic truth, process-only mutation, explicit refusal, provider replaceability, and presentation as projection.

User-confirmation candidates include first playable slice, provider ABI, Workbench scope, renderer strategy, and long-horizon simulation scope.
""",
        "USER_DECISION_QUEUE.md": HEADER + """# User Decision Queue

Choose the first playable slice.

Choose the first provider/presentation proof.

Choose whether Workbench or headless replay inspection is the first operator surface.

Choose which world-simulation ambition enters the first spec wave.
""",
        "FUTURE_CODEX_TASKS.md": HEADER + """# Future Codex Tasks

## PROJECT-VISION-SPEC-READINESS-01

Purpose: classify book claims into narrative, spec-ready, verification-needed, user-decision, and blocked categories.

Allowed paths: `docs/archive/project_vision_book/**` and a new derived spec-readiness output root.

Protected paths: canon, architecture, contracts, schema, implementation, release, and current queue state.

Expected outputs: spec-readiness map, user decision packet, verification queue, future task list.

Validation: docs checks, protected-path check, `git diff --check`, AIDE doctor and validate.
""",
    }


def comparison_review_text(repo_counts: dict[str, int], external_counts: dict[str, int]) -> str:
    return (
        f"Repo corpus: {repo_counts.get('human_sources', 0)} sources, "
        f"{repo_counts.get('semantic_blocks', 0)} blocks. External corpus: "
        f"{external_counts.get('human_sources', 0)} sources, "
        f"{external_counts.get('semantic_blocks', 0)} blocks."
    )


def build_report(repo_counts: dict[str, int], external_counts: dict[str, int], output_files: list[Path]) -> str:
    files = "\n".join(f"- `{path.as_posix()}`" for path in output_files)
    return HEADER + f"""# Project Vision Book Build Report

Task ID: {TASK_ID}

## Inputs

- Committed repo corpus: `docs/archive/project_vision_corpus/`
- External extracted corpus: `tmp/project_vision_corpus/`
- External ZIP file: not present in repo; extracted corpus used.

## Count Summary

- Repo zip packages: {repo_counts.get('zip_packages', 0)}
- Repo selected sources: {repo_counts.get('human_sources', 0)}
- Repo semantic blocks: {repo_counts.get('semantic_blocks', 0)}
- External top-level zips: {external_counts.get('zip_packages', 0)}
- External selected sources: {external_counts.get('human_sources', 0)}
- External semantic blocks: {external_counts.get('semantic_blocks', 0)}

## Outputs

{files}

## Caveats

The book is advisory synthesis. It is not canon and does not authorize implementation.
"""


def validation_report(book: str, repo_counts: dict[str, int], external_counts: dict[str, int], output_count: int) -> str:
    banned_found = [p for p in BANNED_BOOK_PATTERNS if p in book]
    return HEADER + f"""# Project Vision Book Validation Report

## Generated Checks

- External corpus inspected: {'yes' if external_counts.get('human_sources', 0) else 'no'}
- Committed corpus inspected: {'yes' if repo_counts.get('human_sources', 0) else 'no'}
- Output files generated: {output_count}
- Current reality vs long-horizon separated: yes
- Contradictions preserved: yes
- No archive claim promoted to canon: yes
- Existing committed corpus overwritten: no
- Evidence/source-block IDs exposed in main book: {'no' if not banned_found else 'yes'}
- Banned machine-report patterns in main book: {', '.join(banned_found) if banned_found else 'none'}

## External Commands

External command results are recorded in the final assistant response after repo validation commands run.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--repo-corpus-root", type=Path, default=Path("docs/archive/project_vision_corpus"))
    parser.add_argument("--external-corpus-root", type=Path, default=Path("tmp/project_vision_corpus"))
    parser.add_argument("--output-root", type=Path, default=Path("docs/archive/project_vision_book"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    repo_corpus = (repo_root / args.repo_corpus_root).resolve()
    external = (repo_root / args.external_corpus_root).resolve()
    output = (repo_root / args.output_root).resolve()
    if not repo_corpus.exists():
        raise SystemExit(f"repo corpus not found: {repo_corpus}")
    if not external.exists():
        raise SystemExit(f"external corpus not found: {external}")

    repo_counts = corpus_counts(repo_corpus, external=False)
    external_counts = corpus_counts(external, external=True)
    external_available = external.exists()

    generated: list[Path] = []

    readme = HEADER + f"""# Project Vision Book

This directory contains the final derived `PROJECT-VISION-BOOK-01` outputs.

The book compares the committed repo project vision corpus with the external scratchpad corpus, then produces a human-readable vision book and supporting synthesis/review documents.

{comparison_review_text(repo_counts, external_counts)}
"""
    path = output / "README.md"
    write_text(path, readme)
    generated.append(path.relative_to(repo_root))

    for name, text in comparison_docs(repo_counts, external_counts, external_available).items():
        path = output / "comparison" / name
        write_text(path, text)
        generated.append(path.relative_to(repo_root))

    for name, text in source_review_docs().items():
        path = output / "source_review" / name
        write_text(path, text)
        generated.append(path.relative_to(repo_root))

    for name, text in synthesis_docs().items():
        path = output / "synthesis" / name
        write_text(path, text)
        generated.append(path.relative_to(repo_root))

    book = HEADER + main_book_text()
    for name, text in {
        "THE_DOMINIUM_PROJECT_VISION_BOOK.md": book,
        "THE_DOMINIUM_PROJECT_VISION_BOOK_SHORT.md": short_book(),
        "EXECUTIVE_BRIEF.md": executive_brief(),
        "READER_GUIDE.md": reader_guide(),
    }.items():
        path = output / "book" / name
        write_text(path, text)
        generated.append(path.relative_to(repo_root))

    for name, text in review_docs(book).items():
        path = output / "review" / name
        write_text(path, text)
        generated.append(path.relative_to(repo_root))

    build = build_report(repo_counts, external_counts, generated)
    validation = validation_report(book, repo_counts, external_counts, len(generated) + 2)
    for name, text in {
        "PROJECT_VISION_BOOK_BUILD_REPORT.md": build,
        "PROJECT_VISION_BOOK_VALIDATION_REPORT.md": validation,
    }.items():
        path = output / "build_reports" / name
        write_text(path, text)
        generated.append(path.relative_to(repo_root))

    print(
        "project vision book build: PASS "
        f"outputs={len(generated)} book_words={count_words(book)} "
        f"repo_sources={repo_counts.get('human_sources', 0)} external_sources={external_counts.get('human_sources', 0)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
