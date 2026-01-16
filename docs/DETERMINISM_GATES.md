# Determinism Gates (DET0)

This document defines merge-blocking determinism gates.
Every gate listed here is mandatory and MUST block merges on failure.

## Gate DET-G1: Step vs batch equivalence

**Requirement**
Stepping N ticks one-by-one MUST match batching to the same ACT target.

**Test inputs**
- Minimal Earth-only
- Warp scenario

**Expected outputs**
- All SIM_* partitions match at each checkpoint tick.

**Failure artifacts**
- Desync bundle with partition hashes and event queue snapshot.

## Gate DET-G2: Replay equivalence

**Requirement**
Recorded commands and events MUST reproduce identical partition hashes.

**Test inputs**
- Sol-only scenario
- Market contract scenario

**Expected outputs**
- All SIM_* partitions match at each replay checkpoint.

**Failure artifacts**
- Desync bundle plus replay log and hash diff report.

## Gate DET-G3: Lockstep parity

**Requirement**
Two peers running lockstep MUST converge to identical partition hashes.

**Test inputs**
- Sol-only scenario (local MP lockstep)

**Expected outputs**
- All SIM_* partitions match across peers at every checkpoint.

**Failure artifacts**
- Desync bundle from both peers with hash diffs.

## Gate DET-G4: Server-auth parity

**Requirement**
Server-auth authoritative state MUST match expected partition hashes.

**Test inputs**
- Market contract scenario
- Info/comm scenario

**Expected outputs**
- Server SIM_* partitions match canonical expected hashes.

**Failure artifacts**
- Desync bundle with server partition hashes and input log.

## Gate DET-G5: No float, OS time, or nondeterministic RNG in authoritative dirs

**Requirement**
Authoritative directories MUST NOT use floating point, OS time APIs, or nondeterministic RNG.

**Test inputs**
- Static scan across authoritative directories.

**Expected outputs**
- Zero violations in authoritative directories.

**Failure artifacts**
- Scan report listing file:line violations.

## Gate DET-G6: Canonical ordering

**Requirement**
Container iteration order MUST be deterministic under permuted insertions.

**Test inputs**
- Deterministic ordering fixture that permutes insert order across runs.

**Expected outputs**
- All SIM_* partitions match across permutations.

**Failure artifacts**
- Desync bundle with ordering trace and hash diffs.

## Global prohibitions

- No determinism gate may be downgraded or disabled without explicit governance approval.
- No flake tolerance is allowed for determinism failures.
- Partial-state comparison is FORBIDDEN unless the partition is defined in
  `docs/DETERMINISM_HASH_PARTITIONS.md`.
