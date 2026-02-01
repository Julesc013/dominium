Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Runtime Loop Contract

All product entrypoints follow the same loop phases when running an interactive
mode. CLI-only commands execute the init/probe/work/shutdown phases without a
long-running loop.

## Loop phases (ordered)
1) init
2) capability probe
3) enter loop
   - poll platform events
   - process input queue
   - advance application clock (if permitted)
   - perform application work
   - emit outputs/logs
4) shutdown request handling
5) orderly shutdown (reverse of init)
6) exit

## No reentrancy
Platform backends only enqueue events. Application logic consumes the queue at
deterministic points inside the loop.

## Loop ownership
Each executable owns exactly one primary loop. No background loops mutate
observable state.

## Current implementations
- Client windowed + TUI loops: `client/app/main_client.c`
- Tools TUI loop: `tools/tools_host_main.c`
- Server/launcher/setup CLI commands: init/probe/work/shutdown without a loop