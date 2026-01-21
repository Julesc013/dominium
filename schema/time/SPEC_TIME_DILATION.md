# SPEC TIME DILATION (TIME2)

Status: draft.
Version: 1.0
Scope: deterministic time dilation for perception only.

## Definition
Perceived time is a function of ACT:

perceived_time(t) = f(ACT(t))

Where f is:
- deterministic
- continuous
- monotonic

## Allowed Effects
- slow perception (dilation_factor < 1)
- accelerate perception (dilation_factor > 1)
- buffered perception (see TIME2 buffers)

## Forbidden Effects
- altering authoritative schedules
- changing event ordering
- changing outcomes

## Integration Points
- Observer clocks (TIME2)
- Law/capability gates for dilation limits
