# Migration from Job Hunter

This document owns the migration work that previously lived implicitly inside Job Hunter's LLM fallback implementation and emergency Ollama notes.

The migration must happen **after** AI Gateway has an accepted interface and verified replacement behavior. Job Hunter's current fallback chain remains production behavior until then.

## Current Job Hunter responsibilities to move

Today Job Hunter owns reusable infrastructure that should eventually belong to AI Gateway:

- provider/account registry;
- provider ordering;
- model aliases and logical-to-concrete model mapping;
- multiple accounts for the same provider;
- retryable provider error classification;
- rate-limit and quota failover;
- model-unavailable failover;
- provider/network timeout handling;
- per-requested-model fallback TTL/cooldown;
- local / LAN Ollama compatibility slots;
- provider-specific timeout behavior;
- provider/model usage metadata;
- provider-specific headers and compatibility details.

## Required behavior to preserve

Migration must preserve these business semantics:

1. A retryable provider failure moves to another eligible resource.
2. Exhaustion of all LLM resources is distinguishable from a legitimate model decision.
3. Job Hunter matcher infrastructure failure remains a deferred/unscored outcome rather than a fabricated score.
4. Vision workloads are never routed through text-only fallback capacity.
5. Client cancellation/deadline behavior is not swallowed by gateway retries.
6. Provider/model metadata remains observable.
7. Local emergency capacity can be disabled without changing application code.
8. Credentials and full candidate data are not exposed through ordinary analytics.

## Job Hunter migration sequence

### Phase 1. Contract

Define and validate the Gateway request/response contract against representative Job Hunter workloads.

No Job Hunter production behavior changes yet.

### Phase 2. Shadow / compatibility integration

Add a Gateway integration path while retaining the existing Job Hunter fallback implementation as the rollback path.

Compare:

- selected workload capability;
- success/failure classification;
- latency;
- routing/fallback behavior;
- model/provider metadata.

### Phase 3. Gateway becomes routing owner

Move provider/account/model routing policy out of Job Hunter.

Job Hunter should retain only:

- task-specific prompts;
- domain validation;
- business-safe failure semantics;
- task-specific requested quality/capability policy.

### Phase 4. Remove Job Hunter routing compatibility code

After replacement behavior is verified, remove Gateway-owned compatibility logic from Job Hunter, including the temporary LAN Ollama routing path.

The cleanup includes the current Gateway-owned concerns in Job Hunter's LLM client:

- emergency slot-specific model binding;
- slot-specific timeouts and direct transport;
- model-aware provider deduplication used only for emergency slots;
- Gateway-replaced model mapping/capability/timeout logic;
- temporary Ollama quality-journal hooks if Gateway provides their replacement.

Job Hunter-specific analytics and business-domain failure handling remain until explicitly replaced.

## Acceptance criteria for migration

Migration is complete only when:

- Job Hunter no longer needs provider credentials for normal LLM routing;
- adding/removing a supported provider does not require Job Hunter code changes;
- current retry/fallback scenarios have equivalent or safer outcomes through Gateway;
- local model fallback works through Gateway rather than Job Hunter-specific slots;
- no weaker model can silently bypass Job Hunter's business safety semantics;
- rollback has been tested before the old routing code is deleted.
