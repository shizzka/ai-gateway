# Business Requirements

## 1. Purpose

AI Gateway provides client applications with a single stable interface to LLM capacity while hiding provider-specific accounts, models, quotas, failures and routing rules.

The primary business goal is to aggregate fragmented free capacity across providers, accounts and local models into one usable pool, reducing dependence on any single provider and avoiding routine paid API spend. Low-cost paid capacity is a controlled reserve, not the default economic model. Infrastructure failures or weak fallback models must not silently damage application decisions.

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

### BR-16. Task-to-model routing

The Gateway must own the decision of which currently available model is suitable for a workload.

Client projects must not maintain lists such as "use model X for matching, model Y for JSON, model Z for reasoning".

A request must carry a workload descriptor with enough information to route safely. The descriptor may include:

- task category / semantic role;
- hard capabilities such as text, vision, coding or structured JSON;
- quality tier;
- context-size requirement;
- latency preference or deadline;
- cost policy;
- degradation policy;
- diversity / anti-affinity constraints;
- response-format requirements.

The Gateway then:

1. filters out models that do not satisfy hard requirements;
2. considers current health, quota and cooldown state;
3. ranks eligible models for the requested workload;
4. chooses a route according to cost/quality/latency policy;
5. falls back only to models still compatible with the workload contract.

The task-to-model mapping must be data/configuration driven. Adding a new model, retiring a model, or changing which model is preferred for a task must not require client-project code changes.

### BR-17. Universal project connector

A new project must be able to use AI Gateway through a simple connector / stable service contract rather than implementing provider logic. The Gateway must remain a standalone service; client projects must not embed its routing engine as an in-process library.

The connector is responsible for:

- Gateway endpoint/auth configuration;
- serializing the workload descriptor;
- sending prompts/messages and optional structured-output schema;
- propagating deadlines/cancellation;
- returning the model response plus safe routing metadata;
- exposing stable Gateway error classes;
- hiding provider credentials and provider-specific SDKs from the client project.

Onboarding a new project must not require modifying Gateway source code for ordinary workloads.

The intended developer experience is:

1. configure a small project-side connector against the Gateway endpoint;
2. configure the project identity;
3. define named workload profiles or pass a declarative workload descriptor;
4. replace direct provider calls with connector calls;
5. receive routing automatically.

A language-specific helper/SDK may exist as an optional convenience, but it must not be required to preserve routing behavior and must not contain Gateway-owned policy.

A dedicated integration contract must be sufficient for a coding agent to add Gateway access to a new project without reading Job Hunter or Relocation / OSINT internals.

### BR-18. Telegram operational control plane

AI Gateway should expose an optional Telegram control plane for operational visibility.

The Telegram layer must support alerting and inspection for:

- quota/rate-limit exhaustion and recovery;
- credential/authentication failures;
- model retirement/unavailability;
- provider/account/local-node health transitions;
- paid fallback usage and budget warnings;
- elevated fallback/error/timeout rates;
- recent routing activity during early rollout.

It should also provide safe read-only commands for status, providers/accounts/models, quota, budgets and recent errors.

Telegram must not be a hard dependency for routing. Gateway must continue operating when Telegram is unavailable.

Administrative write actions may be added later, with explicit allowlists, confirmation and audit logging.

See [Telegram control plane requirements](TELEGRAM_CONTROL_PLANE.md).

### BR-19. Multimodal and per-asset paid routing

AI Gateway must not assume that every routed workload is text-only.

Future clients must be able to request non-text workloads such as image generation/editing through the same provider/account/budget infrastructure.

For paid multimodal workloads, `paid_allowed=true` is not sufficient by itself. The Gateway must support hard cost constraints such as maximum cost per request/asset and project/workload budgets.

Model routing for image generation must consider modality-specific requirements such as resolution, aspect ratio, reference-image support, layout/text fidelity, latency and batch/interactive execution mode.

Provider/model/pricing churn must remain Gateway-owned rather than client-owned.

See [Multimodal and paid capacity requirements](MULTIMODAL_PAID.md).

### BR-20. Free capacity aggregation is a primary product objective

The Gateway exists in large part because individual free tiers are too small, unreliable or fragmented to support the client workloads by themselves.

Free/trial/local capacity is therefore not merely an optimization. It is a first-class production resource pool.

The Gateway must be able to:

- combine legitimate free quotas from different providers and configured accounts;
- track remaining quota independently per resource;
- spread workload across free resources before paid capacity is considered;
- predict whether the remaining free pool can finish a run;
- stop or checkpoint long-running jobs before exhausting every reserve at once;
- distinguish renewable free quota, one-time trial credit and local compute;
- expose pool-level remaining capacity to clients and Telegram monitoring.

Paid capacity must remain opt-in per workload/project and should normally act as a deliberately bounded reserve.

For Search/OSINT workloads this principle applies to search capacity as well as LLM capacity. Search providers that cannot be practically paid for from the user's available payment methods should be treated as free/trial-only resources, not as assumed paid fallback.

### BR-21. Shared quota domains and cross-capability exhaustion

Provider capabilities must not be assumed to have independent quotas.

A single provider account may expose multiple capabilities such as:

- text generation;
- vision;
- web search;
- image generation.

Those capabilities may consume the same underlying account-level quota or may trigger account-wide throttling.

Observed example: exhausting the Ollama account's web-search quota can cause subsequent LLM generation calls on the same account to return HTTP 429 as well. In practice, search exhaustion can therefore invalidate the entire account for other workloads.

The Gateway / shared resource-balancing layer must model quota ownership explicitly:

- provider-level;
- account-level;
- capability-level;
- model-level;
- shared quota domain spanning several capabilities.

A resource that shares a quota domain with critical capacity must not be consumed independently by another project without considering the blast radius.

Search/LLM routing must therefore coordinate reservations and reserve floors for shared accounts.

Example:

```text
ollama-account-1
  quota_domain = account
  capabilities = [llm, web_search]

OSINT web search consumes account quota
→ remaining shared capacity decreases
→ Job Hunter LLM capacity on the same account also decreases
```

Capacity planning and Telegram status must expose this relationship rather than showing search and LLM quotas as unrelated pools.

### BR-22. Critical capacity reservation and workload priority

The Gateway must support protected capacity for critical workloads so that long-running or low-priority consumers cannot exhaust resources required by higher-priority clients.

Workloads may be assigned priority classes or equivalent policy semantics. An initial model may be:

- **P0** — critical interactive/production workloads such as Job Hunter runtime;
- **P1** — normal interactive Gateway workloads;
- **P2** — long-running batch workloads such as Relocation / OSINT research.

The exact class names are an implementation detail, but the protection invariant is mandatory:

> A lower-priority workload must not consume a resource below the reserve floor required by a higher-priority workload.

The Gateway must therefore support:

- reserve floors per provider/account/shared quota domain;
- project/workload-specific access to those reserves;
- refusal, queueing or checkpointing of lower-priority work when only protected capacity remains;
- routing decisions that consider both current quota and protected quota;
- persistent accounting so a restart does not forget consumed capacity or temporarily expose protected reserve;
- observability showing protected, available and exhausted capacity separately.

Example:

```text
ollama-account-1
  quota_domain = account
  protected_for_P0 = 25%

OSINT / P2 may consume only unprotected capacity.
When the remaining quota reaches the P0 floor:
→ OSINT is deferred/checkpointed
→ Job Hunter remains eligible to use the protected reserve
```

This requirement applies across shared capabilities. If web search and LLM generation share one account-level quota domain, a low-priority search workload must not exhaust capacity reserved for a critical LLM workload.


### BR-23. Request identity, retry and restart safety

Gateway restarts and client retries must not create uncontrolled duplicate provider calls.

Requests that may be retried by a client must carry a stable request identity / idempotency key. The Gateway must retain enough durable request state to distinguish:

- a new request;
- an in-progress request being retried after transport failure;
- a completed request whose result can be returned again;
- a terminally failed request.

A process restart is not expected to preserve an existing HTTP/TCP connection. The recovery contract is instead:

1. the client retries with the same request identity;
2. the Gateway recognizes the request after restart;
3. the Gateway either resumes safe processing or returns the already stored terminal result;
4. the Gateway must not silently create duplicate paid or quota-consuming provider work.

Internal provider retries and fallbacks must be bounded by the request deadline and retry policy.

Repeated systemic failures must become observable incidents rather than infinite retry loops.

### BR-24. Route degradation is not answer-quality judgement

The Gateway is responsible for selecting compute capacity, not deciding whether the semantic answer is "good enough" for a client domain.

For Gateway purposes, degradation means that the actual served route is weaker or less preferred than the requested route/profile, for example:

- a lower quality tier;
- a slower route;
- local fallback instead of preferred cloud capacity;
- another explicitly permitted compatible substitute.

Such degradation may happen only when policy permits it and must be exposed in routing metadata.

The Gateway must not convert model output into a domain decision about vacancy relevance, OSINT truth, cover-letter quality or similar client semantics. Domain validation remains the client's responsibility.

### BR-25. Admission control for large batch workloads

Large, predictable batch workloads should not begin consuming capacity blindly when the Gateway can already determine that available unprotected capacity is insufficient.

Where quota/capacity information is available, the Gateway should support pre-flight admission checks for high-volume workloads such as Relocation / OSINT.

A batch may be:

- admitted;
- admitted with an explicit capacity warning;
- deferred;
- rejected until quota recovers;
- checkpointed before protected reserve is reached.

The admission decision must account for shared quota domains and higher-priority reserve floors.

This requirement does not require perfect forecasting. It requires avoiding obviously doomed runs when current capacity already proves they cannot finish safely.

## 6. Policy requirements

The gateway should support at least these policy dimensions:

- quality tier;
- required capabilities;
- paid allowed: yes/no;
- weaker-model degradation allowed: yes/no;
- timeout/deadline;
- project/workload identity for analytics and policy;
- role-specific budget / paid policy;
- optional diversity or anti-affinity group for independent multi-model work;
- generic task category and/or project-defined named workload profile;
- response format / structured-output requirements;
- workload priority / criticality;
- protected reserve floor and reserve-access policy;
- stable request identity / idempotency policy for retriable calls;
- retry budget / backoff policy;
- batch admission policy.

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
- clear terminal error when no eligible resource remains;
- reusable client connector/SDK;
- declarative workload descriptors;
- model registry containing routing capabilities and workload suitability metadata;
- stable request identity and restart-safe retry semantics;
- protected reserve enforcement for lower-priority batch work;
- an MVP failure/acceptance matrix covering provider failure, quota exhaustion, restart and policy refusal.

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
9. A new project can integrate by following one standalone integration document and using the reusable connector, without copying provider/model routing code.
10. Client projects can request a task by workload requirements while Gateway selects the concrete model dynamically.
11. Relocation / OSINT can exhaust all capacity available to its policy without consuming protected Job Hunter reserve; Job Hunter requests remain routable while that protected capacity exists.
12. Retrying the same request after a Gateway restart does not create uncontrolled duplicate provider work.
13. If a weaker route is used under an allowed degradation policy, the client can see that degradation in routing metadata.
14. A large batch can be deferred before it predictably consumes protected capacity needed by a higher-priority workload.

## 10. Open product questions

These remain intentionally unresolved:

- exact public API / transport shape for the standalone Gateway service;
- persistence mechanism for quota/cooldown state and durable idempotency records;
- how provider quotas are discovered versus inferred from errors;
- whether quality tiers are global or task-specific;
- how model quality is measured and updated;
- exact boundary between higher-level OSINT orchestration and Gateway diversity enforcement; the current requirement is that orchestration may remain in OSINT while Gateway can enforce requested model anti-affinity;
- deployment topology for local and remote clients;
- credential storage model;
- whether budget ceilings should be global, per project or per workload;
- exact per-workload deadlines and latency SLOs;
- exact retry counts, backoff rules and incident thresholds;
- cancellation semantics when the client disconnects while an upstream provider call is already running;
- retention TTL for completed request/idempotency records;
- exact reserve formula above the mandatory minimum floor for countable quotas.

These questions belong to architecture/design after business requirements are accepted.
