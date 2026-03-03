# Information Grammar Constitution

Status: CANONICAL
Last Updated: 2026-03-03
Scope: META-INFO artifact family constraints used across transport, trust, and inspection layers.

## 1) Purpose

Define canonical artifact-family semantics for information-bearing outputs so domains do not create bespoke message/report/knowledge systems.

## 2) Core Artifact Families

- `OBSERVATION`: measured or sensed state snapshots.
- `RECORD`: factual event/provenance records.
- `REPORT`: deterministic aggregation/summarization artifacts.
- `MESSAGE`: transport envelope content payloads.
- `CREDENTIAL`: identity/certification/security artifacts.
- `BELIEF`: interpreted knowledge state derived from receipts and policy.

## 3) Constitutive Model Integration (META-MODEL)

Derived outputs produced by constitutive response evaluation must map to existing META-INFO families:

- direct measurements and derived scalar/vector outputs -> `OBSERVATION`
- scheduled or institutional summaries -> `REPORT`
- audit/provenance traces for model evaluation decisions -> `RECORD`

Constitutive models do not create a new information ontology.

## 4) Determinism And Epistemics

- knowledge acquisition remains receipt-driven and policy-gated
- no direct truth mutation from message transport or report generation
- all artifact generation remains deterministic and replay-safe

## 5) Electrical Domain Mapping (ELEC-0)

Electrical information outputs map to existing families only:

- instrument readings, meter samples, and derived PF/loss summaries -> `OBSERVATION`
- breaker trips, overload/protection outcomes, and fault traces -> `RECORD`
- compliance packs, standards audits, and grid status bulletins -> `REPORT`

No electrical-specific information ontology is introduced.

## 6) Non-Goals

- no runtime semantic changes in META-MODEL-0
- no new artifact family additions in this phase
