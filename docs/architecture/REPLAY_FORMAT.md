Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Replay Format (REPLAY1)





Status: binding.


Scope: replay container layout and required chunks.





## Container: replay.dm


Chunked binary format:


```


REPLAY_HEADER


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


- EVENT_LOG





### Optional chunks


- REPLAY_STREAM


- ENGINE_STATE (debug)


- GAME_STATE (debug)


- TOOL_ANNOTATIONS





## Rules


- Unknown chunks MUST be preserved.


- Replays are deterministic and replay-safe.


- No absolute paths inside chunks.


- Replays may reference a save by hash.





## See also


- `docs/architecture/LOCKFILES.md`


- `schema/save_and_replay.schema`
