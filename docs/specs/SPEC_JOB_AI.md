--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# SPEC_JOB_AI — Deterministic Job Planning (JOB/AI)

This spec defines deterministic job planning and assignment rules for the JOB
layer. It is intentionally semantic-light: it covers ordering, tie-breaks, and
bounded work, not gameplay heuristics.

## Scope
Applies to:
- the job planner tick (`d_job_planner_tick`)
- deterministic eligibility checks derived from content template requirements
- deterministic tie-break rules and truncation/cap behavior

## Planner inputs
- Jobs: `d_job_record` (`source/domino/job/d_job.h`)
- Templates: `d_proto_job_template` (`content/d_content.h`)
- Agents (legacy): `d_agent_state` (`source/domino/ai/d_agent.h`)

The refactor agent pipeline (`dg_agent_*`) is specified separately
(`docs/SPEC_AGENT.md`) and is not interchangeable with the legacy `d_agent_*`
IDs or storage.

## Canonical ordering and assignment
Planner ordering is authoritative:
- Jobs are considered in ascending `d_job_id`.
- Agents are considered in ascending `d_agent_id`.
- For each pending job, the planner assigns the **first eligible** agent in
  that canonical agent order.

Eligibility requirements (current plumbing):
- the agent has no current job assignment
- the agent satisfies `D_TLV_JOB_REQ_AGENT_TAGS` from the template requirements
  blob (`source/domino/content/d_content_extra.h`)

Tie-break rules:
- Any ambiguous choice MUST be resolved by stable numeric IDs (never pointer
  identity or hash iteration order).

## Bounded work and deterministic truncation
Planner work MUST be bounded.

If a fixed cap is used (e.g. max jobs or max agents processed per tick), the
cap MUST apply deterministic truncation:
- collect IDs
- sort canonically
- process the first `cap` entries in that order

## Forbidden behaviors
- Randomized selection (unless derived from explicit deterministic seed context).
- Wall-clock time or OS scheduling as a planning input.
- Unordered iteration (hash maps, pointer identity ordering).
- Dynamic allocation in hot deterministic loops without bounded capacity planning.

## Source of truth vs derived cache
**Source of truth:**
- job records and their committed assignment state

**Derived cache:**
- planner intermediate lists (eligible sets, candidate lists)

## Implementation pointers
- `source/domino/job/d_job_planner.h`, `source/domino/job/d_job_planner.c`
- Shared TLV tags: `source/domino/content/d_content_extra.h`

## Related specs
- `docs/SPEC_DETERMINISM.md`
- `docs/SPEC_JOBS.md`
- `docs/SPEC_AGENT.md`
