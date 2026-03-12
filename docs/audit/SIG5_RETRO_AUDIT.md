Status: AUDIT
Scope: SIG-5 trust graph and belief dynamics
Date: 2026-03-03
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# SIG5 Retro Audit

## Audit Scope
- `src/signals/transport/transport_engine.py`
- `src/signals/addressing/address_engine.py`
- `src/signals/aggregation/aggregation_engine.py`
- `src/inspection/inspection_engine.py`
- `data/registries/trust_policy.json`
- `tools/xstack/sessionx/process_runtime.py`

## Findings

### F1 - Trust is currently receipt-local, not graph-based
- Current message delivery writes `trust_weight` directly into `knowledge_receipt` rows.
- There is no canonical trust-edge model (`from_subject_id -> to_subject_id`) in signals runtime.
- Impact: acceptance/propagation cannot use stable relationship history.

### F2 - Verification state is stored but lacks explicit trust update process
- `verification_state` appears on receipts, but there is no `process.trust_update` path.
- Trust adaptation is therefore static unless callers manually patch receipt rows.
- Impact: belief evolution is under-specified and difficult to audit.

### F3 - Acceptance semantics are implicit
- Inbox inspection aggregates trust and verification metadata, but no canonical threshold policy is evaluated at receipt.
- There is no explicit accepted/untrusted receipt state derived from policy.
- Impact: downstream systems cannot reliably differentiate actionable vs. untrusted knowledge.

### F4 - No dedicated verification result artifact/row in signals
- Message transport and quality layers log delivery/loss/corruption events.
- There is no first-class verification result row for belief updates.
- Impact: trust updates and misinformation handling are not event-explicit.

### F5 - Global trust policy exists for SecureX, not subject-level belief trust
- `data/registries/trust_policy.json` governs platform/package trust boundaries.
- This does not cover subject-to-subject belief trust edges for SIG message semantics.
- Impact: runtime trust graph must remain separate from install/runtime security trust policy.

## Ad-Hoc / Bypass Scan
- No direct omniscient truth-to-receipt mutation found in audited SIG transport paths.
- No explicit `admin` bypass for receipt creation was found in audited signal functions.
- Acceptance logic is currently absent rather than bypassed.

## Migration Plan
1. Add canonical SIG-5 trust/belief schemas and registries.
2. Implement deterministic trust engine:
   - trust edge normalization
   - trust update and decay processes
   - verification result rows
3. Integrate trust lookup into receipt weighting at delivery time.
4. Add deterministic acceptance policy evaluation at receipt creation.
5. Add explicit verification process helper that consumes evidence artifacts/certificates and emits verification results.
6. Add trust and inbox-acceptance inspection sections.
7. Add RepoX/AuditX checks for omniscient trust updates and unlogged trust changes.
8. Add TestX coverage for deterministic trust updates, acceptance, and verification coupling.
