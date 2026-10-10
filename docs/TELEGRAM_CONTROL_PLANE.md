# Telegram Control Plane Requirements

Telegram is an operational control plane for AI Gateway.

It is not part of model routing itself and must not become a hard dependency for request processing. If Telegram is unavailable, Gateway routing must continue to work.

## Goals

Telegram should make it possible to:

- notice provider/account/model failures before client projects start failing;
- inspect current Gateway capacity from a phone;
- understand why a route is degraded;
- manually refresh or test provider state;
- receive budget/quota warnings;
- inspect recent routing activity during early operation;
- perform a small set of explicitly safe administrative actions.

## Alert classes

### Quota and rate-limit alerts

Notify when:

- an account/provider reports quota exhaustion;
- remaining quota crosses configured warning thresholds where quota data is available; initial default warning levels are 30%, 20% and 10% remaining;
- repeated rate limits push a resource into cooldown;
- all free capacity for a workload class is exhausted;
- paid fallback becomes the only eligible route;
- a paid route is blocked because policy forbids spending.

Where providers do not expose quota APIs, Gateway may report inferred state based on observed errors and cooldown history. The message must distinguish measured quota from inferred exhaustion.

Quota threshold alerts must be deduplicated: crossing a threshold should produce one alert for that depletion cycle, not one message per request while the account remains below the threshold. Recovery or quota reset should re-arm the thresholds. Alerts should also show any protected reserve floor so an operator can distinguish total remaining quota from quota still available to lower-priority workloads.

### Credential / authentication alerts

Notify when:

- API key/token is rejected;
- token or credential is known to expire soon;
- refresh/renewal fails;
- permissions no longer allow a required model;
- provider account becomes unauthorized.

Secrets must never be included in Telegram messages.

### Model lifecycle alerts

Notify when:

- a configured model disappears or returns model-not-found/retired;
- an alias no longer resolves;
- a model becomes unavailable for the current account;
- a replacement/fallback mapping becomes active;
- no compatible model remains for a required capability.

Future enhancement: notify about significant quality regression if benchmark/validator data indicates that a model no longer meets its assigned routing tier.

### Provider and node health alerts

Notify on meaningful state transitions:

- provider healthy → degraded;
- degraded → unavailable;
- unavailable/cooldown → recovered;
- local/edge node online → offline;
- edge node offline → recovered;
- Task Profiler unavailable when free-form routing depends on it.

Recovery notifications are important. An alerting system that only screams and never says "fixed" becomes background wallpaper.

### Budget alerts

Notify when:

- daily/monthly/project budget crosses warning thresholds;
- a paid call is actually used;
- paid usage is attempted but blocked;
- a workload unexpectedly starts consuming paid capacity;
- cost metadata is unavailable for a paid route.

### Routing quality / reliability alerts

Notify when configurable thresholds are exceeded:

- high provider error rate;
- high fallback rate;
- structured-output validation failures;
- deadline/timeout rate;
- unusually high latency;
- required OSINT diversity/anti-affinity cannot be satisfied;
- a workload repeatedly degrades below its preferred quality target.

These should be aggregated to avoid one Telegram message per failed request.

## Notification behavior

Telegram alerts must support:

- severity levels, for example info / warning / critical;
- deduplication;
- cooldown/grouping for repeated identical incidents;
- first-failure and recovery messages;
- incident correlation ID where useful;
- project/workload/provider/model context;
- no prompt/body content by default.

A flood of 429 messages is not observability. It is a denial-of-service attack performed by our own bot.

## Manual commands

Exact command names are an implementation detail, but the control plane should provide equivalents of:

### Overall status

- Gateway health;
- number of healthy/degraded/cooldown/exhausted resources;
- free capacity availability;
- paid capacity availability;
- local/edge node status;
- current incident summary.

Example intent: `/status`.

### Providers and accounts

Inspect:

- provider/account state;
- cooldown reason and remaining time;
- last successful call;
- last error class;
- currently available capabilities/models.

Example intents:

- `/providers`
- `/provider <name>`
- `/accounts`

### Models

Inspect:

- active model registry;
- capabilities;
- routing tier/suitability;
- provider availability;
- models currently disabled/retired/unavailable.

Example intents:

- `/models`
- `/model <name>`

### Quota

Manually request the freshest quota/limit information available.

Example intents:

- `/quota`
- `/quota <provider/account>`

The response must state whether quota is:

- provider-reported;
- locally estimated;
- inferred from failures;
- unknown.

### Budgets and cost

Inspect:

- project/workload budget limits;
- current spend;
- paid calls today/month;
- most expensive recent routes.

Example intents:

- `/budget`
- `/cost`

### Recent routing activity

During initial rollout, provide a compact recent request log.

Useful fields:

- timestamp;
- project;
- workload;
- route selected;
- actual provider/model;
- latency;
- fallback count;
- token usage when available;
- cost when available;
- final status/error class;
- request/trace ID.

Example intents:

- `/recent`
- `/errors`

Prompt and response bodies should not be included by default.


### Request trace inspection

A read-only trace lookup should make it possible to answer "why did this request use that route?" without reading raw log files.

Given a request/trace ID, the control plane should show a compact decision trail such as:

- workload/profile and hard requirements;
- candidates rejected by policy/capability/quota/cooldown;
- selected provider/account/model;
- fallback attempts;
- requested vs served quality tier;
- whether degradation was used;
- terminal status/error class.

Example intent: `/trace <id>`.

Prompt/response bodies remain hidden by default.

### Manual health check

Allow explicit test/refresh operations:

- refresh provider/account state;
- probe a provider/model;
- test a local edge node;
- re-check quota when supported;
- refresh model inventory where supported.

Example intents:

- `/check <resource>`
- `/refresh quota <resource>`
- `/refresh models <provider>`

Checks must be bounded and must not accidentally spend meaningful paid budget.

### Administrative overrides

Potentially useful actions:

- temporarily disable a provider/account/model;
- re-enable it;
- clear or shorten cooldown;
- force a resource into maintenance mode;
- reload routing/model registry configuration.

These are write operations and need stricter controls than read-only status commands.

## Security

Telegram must not become an accidental root shell for Gateway.

Requirements:

- explicit Telegram user/chat allowlist;
- read-only commands by default;
- mutating operations require explicit confirmation;
- high-impact actions may require a second confirmation step;
- never print API keys, bearer tokens or raw auth headers;
- redact sensitive provider errors;
- audit all administrative actions;
- Gateway API and routing must continue if Telegram is unavailable.

## Request logging during early rollout

A temporary richer request journal may be useful while routing policies are being tuned.

Default log metadata may include:

- request/trace ID;
- timestamp;
- project;
- declared workload;
- generated Task Profile where applicable;
- requested capabilities;
- selected and fallback routes;
- actual provider/model/account identity;
- latency;
- token usage;
- cost;
- validator result;
- terminal error class.

Full prompt/response logging must be opt-in because client requests may contain:

- resumes and personal candidate data;
- recruiter messages;
- OSINT research content;
- private project data.

If full-content logging is enabled:

- keep it outside the repository;
- use explicit retention/rotation;
- restrict filesystem permissions;
- redact known secrets best-effort;
- allow logging to be disabled per project/workload;
- Telegram should show only metadata unless the operator explicitly requests a specific trace and policy allows content display.

## Digests

Useful optional summaries:

### Daily digest

- provider/account health;
- quota/cooldown incidents;
- calls by project/workload;
- free vs paid usage;
- estimated cost;
- fallback rate;
- top errors;
- edge-node uptime;
- unusual routing changes.

### Incident digest

When a noisy incident ends, send one summary:

- start/end time;
- affected provider/model;
- number of failed/fallback requests;
- projects affected;
- whether paid fallback was used;
- final recovery state.

## Priority

### MVP / early rollout

High value:

- critical quota/auth/model/provider alerts;
- recovery alerts;
- `status`;
- provider/account/model health;
- manual quota refresh;
- recent metadata-only request log;
- errors/fallback inspection;
- paid-call notification;
- alert deduplication.

### Later

- remote administrative overrides;
- configuration reload;
- richer cost reports;
- quality-regression alerts;
- daily/incident digests;
- selective trace-content inspection.

The first version should prefer visibility over remote control. It is much safer to learn what the Gateway is doing before giving Telegram buttons that can rearrange production routing.
