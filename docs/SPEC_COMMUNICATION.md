# SPEC_COMMUNICATION — Communication & Information Logistics Canon

Status: draft
Version: 1

## Purpose
Define the canonical Communication & Information Logistics system: a deterministic,
event-driven mechanism by which information and commands are transmitted, delayed,
degraded, intercepted, or lost — identically across singleplayer, lockstep, and
server-auth modes.

This spec is documentation-only. It introduces no runtime logic.

## Core axioms (locked)
1) Communication is event-driven, not continuous.
2) All messages have a send tick and an arrival tick.
3) Communication never alters authoritative world state.
4) Messages produce InfoRecords or CommandIntents only on delivery.
5) Latency, bandwidth, and fidelity are explicit.
6) Effect fields may degrade communication deterministically.
7) No actor receives information before arrival.
8) Communication is auditable and replayable.
9) Lockstep and server-auth use the SAME semantics.
10) Removing a comm channel removes future deliveries.

## Definitions

### Message
A payload transmitted between actors or systems. Contains:
- message_id (deterministic)
- sender
- receiver (or scope)
- payload type
- payload digest
- send_tick (ACT)
- arrival_tick (ACT)
- channel_id

### Communication channel
A deterministic transmission medium. Declares:
- latency function
- bandwidth limits
- fidelity constraints
- susceptibility to effect fields
- operating cost

### Payload types
At minimum:
- Info payloads (InfoRecords or summaries)
- Command payloads (CommandIntents)
- Acknowledgements
- Administrative / governance messages

### Delivery event
A scheduled event at arrival_tick that:
- validates the message
- applies degradation
- produces InfoRecords or queues commands

## Communication pipeline (mandatory)

ASCII diagram:

  [ Sender ]
      |
      v  (enqueue)
  [ Message Creation ]
      |
      v  (schedule)
  [ Communication Channel ]
      |
      v  (effect fields applied)
  [ Delivery Event (arrival_tick) ]
      |
      v
  [ InfoRecord Creation OR Command Queue ]

No step may be skipped or merged.

## Engine vs game responsibilities

Engine (Domino, C89/C90) MAY:
- provide deterministic scheduling primitives
- provide canonical ACT timestamps
- provide math helpers for latency computation

Engine MUST NOT:
- store messages
- deliver messages
- know about actors or belief

Game (Dominium, C++98) MUST:
- create and enqueue messages
- compute arrival_tick deterministically
- schedule delivery events
- apply effect-field degradation
- generate InfoRecords or CommandIntents on delivery

## Latency and bandwidth (mandatory)
Latency is a deterministic function of:
- channel properties
- distance/topology
- effect fields

Bandwidth is:
- max payloads per interval
- overflow behavior (queueing, delay)

Latency and bandwidth MUST be explicit, inspectable, and replayable.

## Fidelity and degradation
Payload fidelity degrades deterministically via:
- truncation
- summarization
- resolution downgrade

Effect fields (radiation, jamming, distance) modify delivery.
UNKNOWN is produced on insufficient fidelity.

No randomness. No silent corruption.

## Lockstep vs server-auth semantics

LOCKSTEP:
- each peer enqueues identical messages
- each peer computes identical arrival_tick
- delivery events processed locally
- peers synchronize send-intents and message digests

SERVER-AUTH:
- server computes messages and arrival
- server processes delivery events
- clients receive delivered InfoRecords/commands and may verify digests

Behavior MUST be identical; only execution placement differs.

## Communication scopes
- point-to-point
- broadcast (with scope)
- multicast (group)
- hierarchical (command chains)

Each scope must be deterministic, respect channel constraints, and integrate with
governance and authority.

## Domains that must use communication
- sensor output propagation
- command and control
- economic information (prices, contracts)
- legal notices
- diplomatic messages
- emergency alerts
- UI updates via epistemic layer

## Prohibitions (enforced)
- instant message delivery
- "global chat" without infrastructure
- UI-driven knowledge injection
- random packet loss
- per-frame comm updates
- implicit synchronization between actors

## Worked examples

### Delayed command
A command message sent at tick T arrives at tick T+K based on channel latency.
It is queued only on delivery, not at send time.

### Degraded sensor report
A sensor report is truncated by bandwidth limits; resolution tier downgrades to
COARSE. The receiver stores the degraded InfoRecord with provenance.

### Jammed channel
An effect field marks the channel as jammed; delivery produces UNKNOWN and a
recorded failure reason. No implicit retries.

### Economic price latency
Market quotes sent on cadence N ticks arrive later and decay deterministically.
Newer quotes do not delete older records; both remain in belief stores.

## Integration references
- Information model: `docs/SPEC_INFORMATION_MODEL.md`
- Sensors: `docs/SPEC_SENSORS.md`
- Effect fields: `docs/SPEC_EFFECT_FIELDS.md`

## Test and validation requirements (spec-only)
Implementations must provide:
- deterministic arrival tests
- bandwidth saturation tests
- effect-field degradation tests
- message removal tests (channel removed -> no deliveries)
- lockstep/server-auth equivalence tests
