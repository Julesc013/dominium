# Save Format (SAVE1)

Status: binding.
Scope: save container layout and required chunks.

## Container: save.dm
Chunked binary format:
```
SAVE_HEADER
CHUNK_TABLE
CHUNK[n]:
  type_id
  version
  flags
  sizes
  checksum
COMMIT_RECORD
```

### Mandatory chunks
- WORLDDEF
- ENGINE_STATE
- GAME_STATE

### Optional chunks
- MOD_STATE:<ns>
- EVENT_LOG
- REPLAY_STREAM
- TOOL_ANNOTATIONS

## Rules
- Unknown chunks MUST be preserved.
- Chunk types are namespaced and versioned.
- No absolute paths inside chunks.
- Saves embed WorldDefinition by value.

## See also
- `docs/architecture/SAVE_PIPELINE.md`
- `docs/architecture/LOCKFILES.md`
