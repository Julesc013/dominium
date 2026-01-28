# Dominium Documentation

Status: current.
Scope: high-level orientation and map.

Dominium (game) and Domino (engine) form a deterministic simulation kernel with
external perception layers. Executables are content-agnostic; all meaning comes
from packs resolved through the Universal Pack System (UPS). Authority is
capability- and law-gated using explicit authority tokens. Boot is guaranteed
with zero assets or packs installed.

## Core mental model
- The simulation kernel is the source of truth; perception layers are derived.
- Objective snapshots record authoritative state; subjective snapshots record
  views.
- Packs provide capabilities, data, and assets; executables do not embed
  content.
- Determinism and replay-first design are mandatory.

## What it is not
- Not a general-purpose graphics/physics engine.
- Not a modes-based game with hidden exceptions.
- Not a global-scan sandbox; work is event-driven.
- Not an asset-dependent runtime.

## Where to start
- `docs/architectureitecture/MENTAL_MODEL.md` (canonical framing)
- `docs/architectureitecture/INVARIANTS.md` (non-negotiable rules)
- `docs/architectureitecture/TERMINOLOGY.md` (canonical terms and aliases)
- `docs/architectureitecture/COMPATIBILITY_PHILOSOPHY.md` (saves/mods/packs)
- `docs/architectureitecture/NON_GOALS.md` (explicit non-goals)
- `docs/architecture/WHAT_THIS_IS.md` and `docs/architecture/WHAT_THIS_IS_NOT.md` (binding canon)

## Structure
- `docs/architecture/` binding architecture canon and laws
- `docs/specs/` subsystem specs (normative unless marked)
- `docs/app/` product boundaries and runtime contracts
- `docs/policies/` enforcement policies
- `docs/platform/` platform runtime and adapters
- `docs/render/` renderer interfaces and backends
- `docs/build/` build and packaging
- `docs/ci/` CI and enforcement
- `docs/guides/` authoring and workflows

## Archival notes
Historical and audit documents are moved to `docs/architectureive/` with headers that
state why they are archived and what replaces them.
