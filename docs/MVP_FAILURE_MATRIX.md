# MVP Failure and Acceptance Matrix

This document turns the current product discussion into observable MVP behavior.

It is intentionally implementation-neutral. A green unit-test suite is not sufficient if these end-to-end behaviors do not hold.

## Closed decisions

| Scenario | Expected behavior |
|---|---|
| Remaining quota crosses 30% / 20% / 10% | Send a deduplicated Telegram warning. Recovery/quota reset re-arms thresholds. |
| Countable quota approaches exhaustion | Do not consume the quota to zero. Preserve at least 5 request-equivalents as a hard floor; a configured higher reserve may apply. |
| Shared quota domain | Reserve and exhaustion are evaluated at the shared domain, not independently per model/capability. |
| HTTP 429 / provider throttling | Mark affected resource/domain degraded or cooldown as appropriate and route to another eligible resource. |
| Provider 5xx / connection failure / timeout | Use bounded retry/fallback within the request deadline; do not retry forever. |
| Credential/auth failure | Mark the credential unavailable, alert, and do not hammer the same rejected credential. |
| Model retired/unavailable | Remove/disable it from eligibility, alert, and route to another compatible model if available. |
| Several remote routes fail but an allowed local model is available | Local capacity is a valid fallback route. Exact ranking/trigger threshold remains configurable. |
| All free eligible capacity is unavailable and paid is forbidden | Return a stable terminal capacity/policy error. Never spend implicitly. |
| Paid capacity | May be used only when explicitly allowed by request/profile/policy. |
| Preferred quality unavailable, degradation forbidden | Return unavailability/error; do not silently substitute a weaker route. |
| Preferred quality unavailable, degradation allowed | Use only a compatible permitted weaker route and expose the degradation in metadata. |
| Model output quality | Gateway does not decide domain truth/quality. Client projects validate business semantics. |
| Gateway restart during a logical request | The old transport may die. Client retries with the same request ID; Gateway deduplicates, resumes safely or returns stored terminal state. |
| Duplicate delivery of same logical request | Must not cause uncontrolled duplicate upstream/paid/quota-consuming calls. |
| Lower-priority OSINT reaches protected JH reserve | Defer/reject/checkpoint OSINT. JH remains eligible for its protected reserve. |
| Predictably too-large OSINT batch | Perform admission/pre-flight capacity check where data permits; do not knowingly start a run that must violate reserve floors. |
| Partial outage | Some capacity/routes are unavailable but at least some permitted requests remain serviceable. |
| Full outage for a request | No eligible route exists for that request under its hard policy, even if Gateway itself is still running. |
| Telegram unavailable | Routing continues. Telegram is not a routing dependency. |
| Routing diagnostics | Every request has a trace/correlation ID and route decision metadata; Telegram may expose a read-only trace view. |

## Still open

These are not implementation bugs. They are product/architecture decisions still requiring an explicit answer.

1. **Deadline / latency policy**
   - What SLO/deadline classes should exist for interactive requests, Job Hunter matching/apply, and OSINT batch work?
   - How much Gateway overhead is acceptable before provider latency is counted?

2. **Retry budget**
   - Exact retry count per error class.
   - Backoff/jitter rules.
   - After how many repeated failures should one incident alert be raised?

3. **Cancellation semantics**
   - If the client disconnects/cancels while the provider call is already running, should Gateway try to cancel upstream immediately?
   - If upstream cannot be cancelled, should the result be stored for a later retry with the same request ID or discarded?

4. **Durable-state retention**
   - How long should completed request/idempotency records live?
   - How long should detailed routing logs live?
   - Which state is durable across restart versus reconstructable?

5. **Reserve formula above the minimum floor**
   - The hard rule is: do not consume countable quota below 5 request-equivalents.
   - Should critical workloads also reserve a percentage such as 10% / 20% / 25% per quota domain?
   - Should reserve floors differ by project/workload priority?

6. **Local fallback ordering**
   - Local models are eligible first-class capacity.
   - Should JH prefer several remote fallbacks before local, prefer local earlier for cheap workloads, or decide entirely by workload policy/latency?

7. **Security / credentials**
   - Exact Gateway client authentication mechanism.
   - Credential storage/encryption model.
   - Rotation/revocation workflow.

8. **Persistence technology**
   - The product semantics require durable quota/cooldown/idempotency state.
   - SQLite, another database, or another mechanism is not yet frozen.

9. **Quota discovery**
   - Which providers expose authoritative remaining quota?
   - Where must Gateway estimate remaining capacity from observed usage/errors?

10. **Deployment topology**
    - Where the standalone Gateway runs relative to Job Hunter, OSINT and local model nodes.
    - How remote/local node reachability and health are represented.

## MVP release gate

The MVP is not accepted merely because internal tests are green.

At minimum, a Job Hunter shadow integration must demonstrate that:

1. multiple real workload classes route through Gateway;
2. one provider can be intentionally made unavailable;
3. Gateway falls back to another permitted route, including local capacity when policy selects it;
4. paid capacity is not used without explicit permission;
5. a lower-priority batch workload cannot consume protected Job Hunter reserve;
6. a restart/retry with the same request identity does not create uncontrolled duplicate provider work;
7. terminal capacity failure is returned as infrastructure failure, not converted into a valid-looking Job Hunter business decision.

That is the MVP equivalent of "the tractor actually moves".
