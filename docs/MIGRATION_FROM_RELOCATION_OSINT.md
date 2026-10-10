# Migration from Relocation / OSINT

Relocation / OSINT is a first-class AI Gateway consumer.

Today the project already owns provider-routing concerns that should eventually move behind the Gateway boundary. The OSINT pipeline itself should keep orchestration, evidence handling, validation, scoring and judging semantics.

## Current Relocation / OSINT responsibilities to move

The current project owns reusable provider infrastructure including:

- provider/account discovery from shared credential files;
- multiple accounts per provider;
- scout model configuration;
- free OpenRouter reserve capacity;
- Gemini account fallback;
- model aliasing;
- provider-specific request compatibility;
- rate-limit classification and retry/fallback behavior;
- actual served provider/model provenance;
- separate judge provider/model selection.

These concerns should become Gateway-owned after migration.

## OSINT responsibilities that remain outside the Gateway

The Gateway must **not** absorb domain orchestration merely because it can route models.

Relocation / OSINT should continue to own:

- research task decomposition;
- source collection and evidence packs;
- citation validation;
- scoring schema;
- disagreement analysis;
- report caching;
- researcher/scout orchestration;
- judge prompt and verdict semantics;
- final relocation decision logic.

## Required behavior to preserve

### Independent researchers

The current workflow intentionally compares multiple researchers.

Migration must preserve effective model diversity. If three logical scout roles are requested as independent, the Gateway must not silently route all three to the same actual provider/model identity.

The OSINT layer should be able to request an anti-affinity/diversity group and inspect the actual served identities.

### Free-first scouts

Researcher/scout calls are free-first and should remain free-only by default.

Fallback between free providers/accounts is allowed when capability requirements remain satisfied.

### Separately governed judge

The final judge is a different workload from research scouts.

The Gateway must allow the judge role to have an explicitly different policy, for example:

- higher quality tier;
- stronger reasoning;
- paid capacity allowed;
- no weak-model degradation;
- longer deadline.

Permission to spend money on the judge must not enable paid scout calls.

### Provenance

The OSINT project currently reasons about independent model count using actual provenance.

Gateway responses must expose enough metadata to identify the effective provider/model used for each call so OSINT can verify independence and audit results.

### Safe exhaustion and pause/resume

If required independent researchers cannot be obtained, the Gateway must return a clear capacity/policy failure rather than pretending the requested diversity requirement was met.

If the judge has no eligible model under its budget/capability policy, judging must fail explicitly.

For long sequential research runs, Relocation / OSINT should continue consuming free capacity only while it remains outside protected reserve floors.

When Gateway reports that the free boundary has been reached:

1. OSINT checkpoints completed work;
2. the run enters a paused/waiting state rather than discarding progress;
3. the operator may grant a scoped paid allowance such as USD 2 for that run;
4. OSINT resumes using Gateway while that allowance remains;
5. when the allowance is exhausted, Gateway stops paid routing and OSINT checkpoints/pauses again.

OSINT owns pause/resume/checkpoint orchestration. Gateway owns capacity, pricing metadata and enforcement of the spending envelope.

## Migration sequence

### Phase 1. Define Gateway workload contracts

Define representative policies for at least:

- OSINT scout/researcher;
- OSINT final judge.

No production routing changes yet.

### Phase 2. Preserve diversity semantics

Validate that the Gateway can satisfy a group of independent scout calls using distinct effective model identities when requested.

Verify the returned provenance against the current OSINT independence checks.

### Phase 3. Shadow current provider routing

Route representative requests through Gateway while keeping the current provider implementation as a rollback/reference path.

Compare:

- actual model/provider identity;
- rate-limit/fallback behavior;
- JSON compatibility;
- latency;
- failure classification;
- scout free-only policy;
- judge paid-policy enforcement.

### Phase 4. Gateway becomes provider owner

Move provider/account/model selection out of Relocation / OSINT.

The OSINT project should retain only logical workload policy, for example:

- scout: balanced, structured JSON, free-only, diversity required;
- judge: critical, structured JSON, stronger reasoning, paid allowed.

### Phase 5. Remove duplicated provider infrastructure

After acceptance criteria pass, remove Gateway-owned routing/account/model compatibility logic from the OSINT repository.

## Acceptance criteria

Migration is complete only when:

1. Relocation / OSINT no longer needs provider-specific account rotation for normal LLM calls.
2. Three requested independent researchers cannot silently collapse to one effective model identity.
3. Scout calls remain free-only unless their policy explicitly changes.
4. Judge paid permission is isolated from scout policy.
5. Actual provider/model provenance remains available for audit and independent-model counting.
6. Provider rate limits or model retirement can be handled without changing OSINT domain code.
7. Evidence, citation, scoring and judging logic remain owned by the OSINT project.
8. A rollback path has been verified before deleting the old provider implementation.
9. An OSINT run can pause at the free-capacity boundary, resume with a bounded paid allowance, and pause again when that allowance is exhausted without losing completed research.
