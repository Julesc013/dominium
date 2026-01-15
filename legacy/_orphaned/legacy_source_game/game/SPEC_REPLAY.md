# Replay Spec (DMRP)

Status: v3
Version: 4

This document defines the Dominium replay container `DMRP`.

## Endianness
- All numeric fields in the `DMRP` header and records are little-endian.
- The endian marker is `0x0000FFFE` (u32_le).

## File header (DMRP v4)

| Offset | Size | Field | Meaning |
|---:|---:|---|---|
| 0 | 4 | `magic` | ASCII `"DMRP"` |
| 4 | 4 | `version` | container version (`4`) |
| 8 | 4 | `endian` | `0x0000FFFE` (little-endian marker) |
| 12 | 4 | `ups` | updates per second |
| 16 | 8 | `seed` | world seed |
| 24 | 4 | `feature_epoch` | feature epoch (`u32_le`) |
| 28 | 4 | `content_tlv_len` | bytes of content identity TLV |
| 32 | N | `content_tlv` | content identity TLV bytes |
| 32+N | 4 | `identity_tlv_len` | bytes of identity TLV (v2+) |
| 36+N | M | `identity_tlv` | identity TLV bytes (v2+) |
| 36+N+M | 4 | `macro_economy_version` | macro economy schema version (v4+) |
| 40+N+M | 4 | `macro_economy_len` | bytes of macro economy blob (v4+) |
| 44+N+M | K | `macro_economy_blob` | macro economy bytes (v4+) |
| 44+N+M+K | 4 | `macro_events_version` | macro events schema version (v4+) |
| 48+N+M+K | 4 | `macro_events_len` | bytes of macro events blob (v4+) |
| 52+N+M+K | L | `macro_events_blob` | macro events bytes (v4+) |

Immediately after `macro_events_blob` comes the record stream.

## Content identity TLV

Format and tags match `SPEC_SAVE.md` (`PACKSET_ID`, `PACK_HASH`, `MOD_HASH`,
`INSTANCE_ID`).

## Record stream

Each record:
```
tick u64
msg_kind u32
size u32
payload[size]
```

### Record semantics
- `tick`: simulation tick to inject before stepping.
- `msg_kind`: `D_NET_MSG_CMD` (u32) for lockstep command packets.
- `payload`: exact bytes consumed by `d_net_receive_packet` for
  `D_NET_MSG_CMD` packets.
- Macro economy/events are loaded from header blobs (v4+) and are not
  represented as record stream entries.
- Orbit maneuvers and warp-factor changes are recorded as command packets;
  replay does not store a separate orbit-state chunk in v3+.
- Construction placement/removal commands are recorded as command packets.
- Station/route/transfer commands are recorded as command packets.

## Load policy

- Unknown record kinds may be skipped by size.
- Malformed lengths are fatal.
- Content identity mismatch rejects playback by default.
- `--replay-strict-content=0` allows mismatched content (non-default).

## Compatibility promise

`DMRP` is versioned; breaking changes require incrementing the container
version. Readers should accept older versions with explicit migrations and
never silently coerce newer data.
