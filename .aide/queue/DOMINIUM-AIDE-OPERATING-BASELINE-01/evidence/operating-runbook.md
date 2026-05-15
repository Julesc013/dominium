# Dominium AIDE Operating Runbook

Status: needs_review

## How To Start A New Dominium AIDE Task

1. Confirm repo identity with `git remote -v`, `git rev-parse --show-toplevel`, and `git status --short`.
2. Read the latest relevant queue packet and `.aide/context/latest-task-packet.md`.
3. Check `AGENTS.md` and doctrine refs by path, not pasted doctrine.
4. Run `doctor`, `validate`, and a task packet/estimate when available.

## How To Handle Vague Prompts

Compile intent before action. Do not execute raw user intent directly. If the prompt lacks bounded paths, write a plan/evidence packet rather than touching product or doctrine files.

## How To Validate Before And After

Minimum baseline:

- `doctor`
- `validate`
- `test` or `selftest`; if these fail on generated review-packet reference hygiene, run the Q53R repair task before claiming readiness
- relevant domain validate command
- `verify`
- `git diff --check`
- `.aide.local/` ignore check
- targeted secret scan

Use the Python 3.14 executable if `py -3` remains inaccessible.

## How To Handle Repeated Or Out-Of-Order Prompts

Repo state, queue status, branch role, and evidence outrank chat order. If a prior queue phase is dirty or uncommitted, record it before advancing.

## How To Preserve Doctrine

Reference doctrine by path. Do not inline or rewrite canon, glossary, `AGENTS.md`, specs, data, or planning doctrine unless the active task explicitly targets doctrine with review.

## How To Preserve Existing Tools

XStack/AuditX/RepoX/TestX and validators are preserve-first. Do not execute, rename, migrate, or retire them until wrapper contracts and migration evidence exist.

## How To Handle Root Recycling

Root recycling is no-apply by default:

`inventory -> classify -> plan -> salvage map -> move map -> alias plan -> reference rewrite plan -> reviewed apply`

Q52 approved no moves, deletes, aliases, shims, or rewrites.

## What Not To Do

- Do not modify product roots.
- Do not rewrite doctrine.
- Do not run unknown tools.
- Do not mutate branches, remotes, tags, CI, GitHub, or releases.
- Do not call providers/models/network.
- Do not commit `.aide.local/`, secrets, raw prompts, or raw responses.

## Current Next Task

Immediate repair: `Q53R Dominium Baseline Commit Finalization`.

Global next after repair: `Q54 Eureka Fresh Upgrade Preflight`.
