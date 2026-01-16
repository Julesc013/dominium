# ARCH_SPEC_OWNERSHIP — Spec Responsibility Model

Status: draft
Version: 1

## Purpose
This document defines how specification ownership is declared and enforced.
It makes responsibilities explicit so engine and game remain separable.

## Ownership model
- Engine owns deterministic primitives and invariants only.
- Game owns rules, policy, meaning, and validation.
- Tools own authoring, inspection, and diagnostics.
- Schema owns canonical formats and migrations.

## Why the split exists
- Engine must be reusable outside Dominium.
- Game logic must remain deterministic and replay-safe.
- Tools must not become runtime authorities.
- Schema must remain canonical and shared across products.

## How to read specs
Every SPEC_* document starts with an OWNERSHIP & RESPONSIBILITY block.
Use it to determine:
- Who implements the spec.
- Where code lives in the repo.
- Allowed and forbidden dependency directions.

## Required ownership declaration
All new or updated specs MUST include the ownership block at the top with:
- ENGINE
- GAME
- TOOLS
- SCHEMA
- FORBIDDEN
- DEPENDENCIES

## Enforcement hooks
Boundary checks live in CMake and scripts:
- `scripts/verify_includes_sanity.py`
- `scripts/verify_cmake_no_global_includes.py`
