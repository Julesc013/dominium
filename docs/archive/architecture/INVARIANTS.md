# ARCHIVED — OUTDATED

This document is archived and superseded by `docs/architecture/INVARIANTS.md`.
Reason: EG-H canon designates `docs/architecture/` as the authoritative source and
this file may conflict or duplicate canonical invariants.
Status: archived for historical reference only.

# Architectural Invariants

Status: canonical.
Scope: binding rules for engine, game, tools, and content.
Authority: canonical. All other docs MUST defer to this file for invariants.

Each invariant is mandatory. Each includes a rationale and a forbidden outcome.
Any change to these invariants SHALL be treated as an explicit breaking
revision.

## Content and boot
- Executables MUST be content-agnostic. Rationale: portability and auditability
  require behavior to be defined by external content. Forbids: embedding
  gameplay meaning or assets in binaries.
- Engine and game MUST boot with zero assets present. Rationale: headless,
  server, and CI operation must not depend on content. Forbids: any boot path
  that requires packs or assets.
- All content MUST be external and optional via packs. Rationale: content must
  be replaceable without binary changes. Forbids: hard-coded content or
  mandatory asset bundles.
- Capability-driven resolution MUST be used; file paths MUST NOT be
  authoritative. Rationale: capabilities are stable, inspectable contracts.
  Forbids: selecting behavior by filesystem layout or path heuristics.
- Headless, CI, and server-only operation MUST be first-class. Rationale:
  authoritative simulation must run without presentation. Forbids: requiring
  UI, GPU, or audio to execute core logic.

## Authority and processes
- There MUST be a single authoritative source of truth; implicit god mode MUST
  NOT exist. Rationale: authority must be explicit and auditable. Forbids:
  hidden admin bypass or implicit superuser powers.
- All authoritative state changes MUST occur via declared processes invoked by
  explicit events. Rationale: determinism requires ordered, declared changes.
  Forbids: ad-hoc mutation, background scans, or implicit state edits.
- Conservation, causality, and provenance MUST be enforced. Rationale:
  simulation integrity depends on traceable state transitions. Forbids:
  creation, destruction, or teleportation without declared process and record.
- Renderer, platform, client, and server components MUST be non-authoritative.
  Rationale: presentation and transport cannot define truth. Forbids:
  authoritative state mutation from these components.
- Unknown and latent state MUST be first-class. Rationale: systems must
  represent partial knowledge without fabrication. Forbids: assuming complete
  knowledge or inventing missing state.

## Determinism, truth, and compatibility
- Authoritative simulation MUST be deterministic and replayable. Rationale:
  reproducibility and auditability require identical outcomes. Forbids:
  nondeterministic sources that change authoritative results.
- Truth and perception MUST be distinct. Rationale: authoritative state and
  derived views serve different contracts. Forbids: conflating subjective views
  with authoritative truth.
- Compatibility MUST NOT break silently. Rationale: archival integrity requires
  explicit outcomes. Forbids: loading incompatible saves, replays, mods, or
  packs without refusal or declared mode.
- Degradation MUST be explicit and MUST NOT change authoritative outcomes.
  Rationale: compatibility requires stable truth. Forbids: implicit fallback
  that alters simulation results.

## References (detailed enforcement)
- `docs/architectureitecture/INVARIANTS.md`
- `docs/architectureitecture/TERMINOLOGY.md`
- `docs/architectureitecture/COMPATIBILITY_PHILOSOPHY.md`
- `docs/content/UPS_OVERVIEW.md`
- `docs/audit/PROMPT_G_REPORT.md`
