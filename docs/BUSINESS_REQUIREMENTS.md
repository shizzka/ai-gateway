# Business Requirements

## 1. Purpose

AI Gateway provides client applications with a single stable interface to LLM capacity while hiding provider-specific accounts, models, quotas, failures and routing rules.

The business goal is to reduce dependency on any single provider and to maximize useful work from free or low-cost capacity without allowing infrastructure failures or weak fallback models to silently damage application decisions.

## 2. Problem

Current projects may need to know:

- which LLM providers are configured;
- which account/key should be used;
- which concrete model exists today;
- which provider currently has quota;
- how a provider reports rate limits or unavailable models;
- when to retry, cool down or fail over;
- whether a local model may substitute for a cloud model.

This logic is reusable infrastructure and should not be duplicated inside each client project.

## 3. Product boundary

Client applications should describe **what they need**, not **where to get it**.

A client request should be expressible in terms such as:

- task / workload class;
- required capabilities;
- quality tier;
- latency or timeout constraints;
- whether paid capacity is allowed;
- whether degradation to a weaker model is allowed.

Provider names, API keys, account rotation and concrete model mappings are owned by AI Gateway.

## 4. Initial consumers

The initial target consumers are:

1. **Job Hunter**
   - vacancy matching;
   - cover letters;
   - screening questions;
   - structured fact extraction;
   - chat responses;
   - vision tasks where required.

2. **Relocation / OSINT workflows** — a first-class Gateway consumer, not a secondary compatibility case:
   - independent fact discovery;
   - extraction and summarization;
   - parallel/cross-checking work by multiple distinct model identities;
   - free-first researcher/scout calls;
   - a separately governed higher-quality judge call where paid usage may be explicitly allowed.

3. **Future personal automation projects**
   - must be able to reuse the same gateway without copying provider logic.

## 5. Core business requirements

### BR-01. Single client interface

All client projects use one gateway interface instead of integrating provider-specific fallback chains independently.

### BR-02. Provider and account pool

The gateway manages multiple providers and multiple accounts/credentials per provider.

Each provider/account may have its own:

- available models;
- limits and quotas;
- health state;
- latency profile;
- capabilities;
- cost policy.

### BR-03. Free-first routing

Free capacity is preferred by default when it satisfies the request.

Paid capacity must not be used implicitly. Paid usage requires an explicit client or policy allowance.

### BR-04. Task-oriented routing

Clients request workload requirements rather than hardcoding concrete models.

Initial logical quality tiers:

- **cheap** — low-cost / high-volume tasks where weaker models are acceptable;
- **balanced** — normal production tasks requiring reasonable quality;
- **critical** — tasks where answer quality is more important than saving free quota.

The exact names and number of tiers may change during architecture design.

### BR-05. Capability-aware routing

The gateway must distinguish model capabilities such as:

- text;
- structured JSON output;
- vision;
- coding;
- long context;
- stronger reasoning;
- low-latency execution.

A provider/model must not be selected for a request it cannot satisfy.

### BR-06. Automatic failover

Retryable infrastructure failures must trigger routing to another suitable resource when policy permits.

Examples include:

- rate limit / HTTP 429;
- quota exhaustion;
- provider timeout;
- connection failure;
- HTTP 5xx;
- retired or unavailable model;
- provider-side model permission failure.

### BR-07. Cooldown and quota awareness

Resources that are temporarily unavailable must not be retried blindly on every request.

The gateway should maintain operational state such as:

- healthy;
- degraded;
- cooldown;
- exhausted;
- disabled.

### BR-08. Graceful degradation

If the preferred quality tier is unavailable, the gateway must follow an explicit degradation policy.

Depending on the workload, it may:

- use a weaker compatible model;
- wait for another eligible resource;
- use paid capacity if explicitly allowed;
- return a clear temporary-unavailability result.

A weaker model must not be silently substituted for a critical workload where such degradation is forbidden.

### BR-09. Local models as first-class capacity

Local OpenAI-compatible / Ollama-style models participate in the same routing system as remote providers.

They may differ in:

- latency;
- quality;
- context size;
- hardware availability;
- vision support;
- effective monetary cost.

They must not require special-case logic in client applications.

### BR-10. Observability

For each request the system should make it possible to determine:

- calling project;
- workload type / quality tier;
- requested capabilities;
- selected provider/account/model;
- fallback attempts;
- latency;
- token usage when available;
- monetary cost when available;
- final success or failure class.

Full prompt/response logging is not required by default and may contain sensitive data.

### BR-11. Separation of availability and quality

Operational availability and model answer quality are different concerns.

A model may be:

- highly available but poor for a workload;
- high quality but slow or quota-constrained.

Routing policy should eventually be able to consider both without reducing them to one opaque score.

### BR-12. Provider churn isolation

Provider model renames, retirements and alias changes should be handled inside the gateway.

Client applications should not require a release merely because a provider changed a model identifier.

### BR-13. Safe failure semantics

Infrastructure failure must not be converted into a valid-looking business result.

Example: if every matcher-capable model is unavailable, Job Hunter should receive an unavailable/deferred outcome rather than a fabricated low relevance score.

### BR-14. Diversity / anti-affinity for independent research

OSINT workflows must be able to request multiple calls that are intentionally independent.

The Gateway must support a routing constraint that prevents related researcher/scout calls from accidentally resolving to the same effective model identity when diversity is required.

Effective identity should be based on the actual served provider/model combination rather than only the logical model name requested by the client.

This requirement does **not** imply that the Gateway itself must perform OSINT consensus or judging. It means the client can ask the Gateway for genuinely distinct model capacity.

### BR-15. Role-specific budget policy

Different roles inside one workflow may have different cost permissions.

Example for Relocation / OSINT:

- researcher/scout calls: free-only by default;
- reserve researcher capacity: free-only unless explicitly changed;
- final judge: may use a paid high-quality model when that workload policy explicitly allows it.

Paid permission for one role must not implicitly enable paid capacity for other roles in the same project.

## 6. Policy requirements

The gateway should support at least these policy dimensions:

- quality tier;
- required capabilities;
- paid allowed: yes/no;
- weaker-model degradation allowed: yes/no;
- timeout/deadline;
- project/workload identity for analytics and policy;
- role-specific budget / paid policy;
- optional diversity or anti-affinity group for independent multi-model work.

Policies may later be configured centrally per project and task.

## 7. MVP scope

The first useful version should focus on:

- one client API;
- provider/account registry;
- logical model/capability mapping;
- free-first ordered routing;
- retryable-error classification;
- cooldown after rate-limit/quota/provider failures;
- explicit degradation policy;
- local model support;
- routing/usage analytics;
- clear terminal error when no eligible resource remains.

## 8. Explicit non-goals for MVP

The MVP does **not** require:

- an LLM judging the confidence of every other LLM response;
- ML-based routing;
- self-learning routing policy;
- automatic production benchmarking on every call;
- consensus voting for ordinary requests;
- autonomous purchasing or enabling of paid capacity;
- a complex web UI;
- replacing task-specific validation inside client projects.

These can be reconsidered only when measured need appears.

## 9. Success criteria

The product is successful when:

1. Job Hunter can remove provider/account fallback logic from its codebase without losing current resilience.
2. Another project can use the same gateway without importing Job Hunter-specific code.
3. Exhaustion or failure of one free provider does not normally fail a request while another eligible resource exists.
4. Paid capacity is never consumed unless policy explicitly allows it.
5. Routing decisions and failures can be diagnosed from metadata.
6. A client can request a workload by capability/quality policy without naming a specific provider account.
7. Gateway failure cannot silently masquerade as a valid domain decision.
8. Relocation / OSINT can run its researcher/scout and judge roles through the same Gateway while preserving free-only scout policy, explicit judge budget policy and required model diversity.

## 10. Open product questions

These remain intentionally unresolved:

- exact public API shape;
- HTTP service vs embedded client library vs both;
- persistence mechanism for quota/cooldown state;
- how provider quotas are discovered versus inferred from errors;
- whether quality tiers are global or task-specific;
- how model quality is measured and updated;
- exact boundary between higher-level OSINT orchestration and Gateway diversity enforcement; the current requirement is that orchestration may remain in OSINT while Gateway can enforce requested model anti-affinity;
- deployment topology for local and remote clients;
- credential storage model;
- whether budget ceilings should be global, per project or per workload.

These questions belong to architecture/design after business requirements are accepted.
