## 7. Determinism, Replay, Provenance, And Validation

Determinism is the project's engineering spine. Identical canonical inputs should produce identical authoritative outputs, and evidence must make that fact reviewable.

This chapter is part of the synthesized reader, not a source-file transcript. It is written to preserve the meaning that recurs across current docs, archive material, and conversation synthesis while keeping the authority boundary visible.

**Current repo-backed picture.** Current governance requires named RNG streams, deterministic ordering, deterministic reductions, replay-hash equivalence where applicable, and validation before success is claimed. Validation reports are evidence, not replacement authority.

The practical consequence is that this topic should be read through the current authority model first. If a current source and an archive source appear to disagree, the archive source becomes review evidence rather than a shortcut around current doctrine.

**Historical and advisory context.** Conversation material extends this concern into long-term portability, world scale, release trust, and tool-assisted inspection. It treats evidence as a first-class product surface.

That historical context is still useful. It shows why the topic kept returning, which boundaries people were worried about, and what kind of future work the project repeatedly imagined. The book preserves that context so it can be reviewed instead of rediscovered or silently re-invented.

**What remains unresolved.** Full validation depth and release/trust proof remain visible debt outside narrow docs publication tasks. Generated books should report validation honestly and avoid implying runtime progress.

**What not to assume.** Do not treat historical breadth as current permission. Do not infer implementation readiness from a polished description. Do not treat this book, the source reader, or any generated corpus report as a promotion into canon, contracts, schema, implementation, release state, or queue state.

**Review questions.**

- Which parts of this topic are already current repo truth?
- Which parts are merely consistent with current docs but not formalized?
- Which parts are blocked by queue state or need explicit human decision?
- Which source paths should be inspected before any later docs-only promotion?

**How to use this chapter.** Read this chapter as orientation, not as promotion. If later work wants to change canon, contracts, architecture, schema, implementation, release state, or queue state, it needs a separate scoped promotion task with explicit validation.

**Source trail:**

- `README.md`
- `AGENTS.md`
- `docs/architecture/INVARIANTS.md`
- `docs/repo/FOUNDATION_LOCK.md`
