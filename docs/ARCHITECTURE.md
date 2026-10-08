# Architecture

> Status: initial architecture decisions. Subject to validation during MVP implementation.

## 1. Deployment lifecycle

### Phase A — development and early validation

AI Gateway initially runs on the Lenovo development host.

Reasoning:

- development happens on this machine;
- local iteration and debugging are simpler;
- there is no need to introduce deployment complexity before routing behavior is stable.

During this phase the Gateway must still be implemented as a portable standalone service. It must not depend on Lenovo-specific assumptions in client code.

### Phase B — stable service deployment

After the Gateway is reasonably stable, it should be deployable without client changes to an always-on host such as:

- NanoPi;
- VPS;
- another suitable always-on Linux host.

Deployment location is therefore an operational choice, not part of the client contract.

## 2. Service boundary

AI Gateway is a standalone service.

Client projects must not embed Gateway routing logic as an in-process library.

The preferred integration model is:

```text
client project
    ↓ simple connector / HTTP contract
AI Gateway service
    ↓
providers / local nodes / search resources
```

A client-side connector may be implemented as a very small adapter or helper, but it must contain no provider selection, quota balancing, fallback policy or credential pool logic.

## 3. Initial priority model

Job Hunter is the highest-priority production consumer during the initial rollout.

Initial policy:

- **P0** — Job Hunter runtime and other explicitly critical production workloads;
- **P1** — normal interactive workloads;
- **P2** — long-running batch workloads such as Relocation / OSINT.

The names are provisional. The invariant from BR-22 is not: lower-priority workloads must not consume protected higher-priority reserve.

OSINT may wait for many hours when necessary. Speed is secondary to correctness, resumability and preservation of critical capacity.

## 4. Job Hunter safety during Gateway development

During Gateway development and early migration, Job Hunter retains an emergency local-model fallback hosted on a separate laptop.

That fallback is expected to remain online during the risky integration period so Gateway development cannot turn a routing bug into a complete Job Hunter outage.

This fallback is transitional. It should not become a permanent source of duplicated routing policy.

Migration should therefore proceed in stages:

1. existing Job Hunter routing remains available;
2. Gateway is introduced in shadow/compatibility mode;
3. the separate local fallback remains available as an emergency path;
4. Gateway behavior is validated under provider exhaustion and failure scenarios;
5. Gateway becomes routing owner only after those scenarios pass;
6. duplicated client-side routing is removed later.

## 5. Paid-capacity policy

Initial default policy:

- Job Hunter: paid capacity disabled by default;
- OSINT researcher/scout: paid capacity disabled;
- OSINT judge: paid capacity may be enabled explicitly with a hard cost ceiling;
- no workload may silently escalate from free to paid capacity.

Paid access is a hard policy constraint, not a routing preference.

## 6. Initial runtime shape

A reasonable MVP shape is:

```text
                    ┌────────────────────┐
                    │    Job Hunter P0   │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │    AI Gateway      │
                    │ standalone service │
                    │                    │
                    │ router             │
                    │ quota manager      │
                    │ reserve manager    │
                    │ circuit breakers   │
                    │ persistent state   │
                    │ observability      │
                    └──────┬───────┬─────┘
                           │       │
             ┌─────────────┘       └──────────────┐
             ▼                                    ▼
      cloud/free providers                local compute nodes
                                               │
                                               ├─ Lenovo-hosted models when applicable
                                               └─ separate laptop emergency model

                    ┌────────────────────┐
                    │   OSINT batch P2   │
                    └─────────┬──────────┘
                              │
                              └────→ same Gateway
```

Search routing may later add one or more SearXNG/search nodes behind the same resource-management principles.

## 7. Architecture decisions intentionally deferred

The following are not yet frozen:

- exact HTTP API shape;
- implementation language/framework;
- SQLite vs PostgreSQL vs another persistence layer;
- whether an external queue/Valkey is needed for MVP;
- exact scheduler algorithm;
- exact reserve-floor representation;
- deployment packaging;
- authentication mechanism;
- search-node topology.

These should be decided from the simplest implementation that satisfies the accepted requirements and migration tests.
