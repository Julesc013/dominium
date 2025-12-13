Determinism Baseline
--------------------
- World hashing uses a 64-bit FNV-1a hash over world metadata (seed/size/vertical bounds/versions), instance TLV payloads, and all chunks serialized in coordinate-sorted order. Padding and pointers are ignored; only serialized values are hashed.
- Replay contexts carry a determinism mode (off/record/playback/assert-only) and store the last world hash seen. In assert-only mode the engine aborts when two consecutive ticks produce different hashes.
- CLI flags `--deterministic-test`, `--record-replay=<path>`, `--play-replay=<path>`, and `--devmode` drive determinism features; devmode enables assertions by default.
- Input streams are expected to be canonicalized before entering the replay buffer; ordering and timestamps must be stable and free of platform-specific noise.
- Tick ordering is stable: subsystems tick in registration order, then dsim systems, once per fixed tick; hashes are computed after the tick.
- Replay payloads remain TLV; platform/OS state is never hashed or recorded.
