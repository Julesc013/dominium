# Setup2 Security Model

## Trust boundaries
- Kernel is pure orchestration: no OS APIs, no filesystem, no network.
- Services perform all side effects behind explicit facades.
- Frontends only emit requests and call kernel/services.

## Data integrity
- All contracts are TLV with checksums and skip-unknown support.
- Audit and journal files are required for forensic recovery.

## Sandboxing
- Fake services enforce sandbox roots and path traversal rejection.
- Real services must validate paths and avoid escaping roots.

## Offline-first
- No network access is required for install, repair, or verify.
- Offline policy flag is enforced in planning and execution.
