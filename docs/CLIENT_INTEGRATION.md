# Client Integration Contract

This document defines the intended onboarding contract for any project that wants to use AI Gateway.

It is deliberately project-agnostic. A coding agent should be able to read this file and integrate a new client without studying Job Hunter or Relocation / OSINT internals.

## Goal

A client project should never need to know:

- which providers exist;
- which API keys exist;
- which account currently has quota;
- which concrete model should be used;
- how provider-specific fallback works.

The client describes the workload. AI Gateway selects and operates the model route.

## Intended integration flow

A new project should require only:

1. add the Gateway connector/SDK;
2. configure Gateway endpoint and project identity;
3. define workload profiles or pass workload descriptors;
4. replace direct provider calls with connector calls.

No ordinary integration should require a Gateway source-code change.

## Minimal client configuration

Conceptually:

```env
AI_GATEWAY_URL=http://gateway-host:port
AI_GATEWAY_PROJECT=my-project
AI_GATEWAY_TOKEN=...
```

Provider credentials must remain on the Gateway side.

## Workload descriptor

Each request should describe the task rather than naming a concrete model.

Illustrative shape:

```yaml
task:
  id: extract_facts
  category: extraction
  quality: balanced
  capabilities:
    - text
    - structured_json
  cost_policy: free_first
  paid_allowed: false
  degradation: compatible_only
  deadline_ms: 30000
```

The exact wire format is an architecture decision, but these semantics are part of the product contract.

## Named workload profiles

Projects should be able to define stable local names for recurring tasks.

Example:

```yaml
project: my-project

workloads:
  summarize:
    category: summarization
    quality: cheap
    capabilities: [text]
    cost_policy: free_first

  extract_json:
    category: extraction
    quality: balanced
    capabilities: [text, structured_json]
    cost_policy: free_first

  final_decision:
    category: judgement
    quality: critical
    capabilities: [text, reasoning, structured_json]
    paid_allowed: true
    degradation: no_weaker_model
```

The project calls `summarize`, `extract_json` or `final_decision`; it does not encode provider/model identifiers.

Workload profiles may be stored client-side, Gateway-side, or both. The architecture must preserve the same logical contract.

## Generic workloads for fast onboarding

A new project should not be forced to invent a complete taxonomy before its first call.

The Gateway should provide reusable generic workload categories such as:

- chat / general text;
- summarization;
- extraction;
- classification;
- judgement / reasoning;
- coding;
- vision;
- structured generation.

Projects can start with generic categories and introduce project-specific workload profiles only where needed.

## Request contract

A connector request should be able to include:

- project identity;
- workload/profile identity;
- messages or prompt;
- required capabilities;
- quality tier;
- cost policy;
- paid allowed yes/no;
- degradation policy;
- deadline/timeout;
- response format or JSON schema;
- optional diversity/anti-affinity group;
- optional caller trace/correlation ID.

## Response contract

A successful response should provide:

- generated content or structured result;
- actual provider identity;
- actual model identity;
- logical workload/profile;
- whether fallback occurred;
- latency metadata;
- token usage when available;
- cost metadata when available;
- trace/correlation ID.

The connector may expose a simplified response by default, but routing provenance must be obtainable for diagnostics and OSINT independence checks.

## Error contract

Client code should receive stable Gateway-level error classes instead of provider-specific exceptions.

Examples:

- `NoEligibleModel`
- `CapacityExhausted`
- `DeadlineExceeded`
- `PolicyRejected`
- `StructuredOutputFailed`
- `GatewayUnavailable`

Exact names may change during API design; the requirement is a stable provider-independent error taxonomy.

## OpenAI compatibility

An OpenAI-compatible endpoint is desirable for easy adoption, but compatibility alone is not enough because routing needs workload metadata.

The architecture may support both:

1. OpenAI-compatible requests for simple/drop-in use;
2. the Gateway connector/SDK for full workload, policy and diversity controls.

Projects that need only generic text generation should have a low-friction path. Projects that need safety-critical routing should use the richer contract.

## Connector responsibilities

The connector should be thin.

It should **not**:

- contain provider API keys;
- know the current provider list;
- duplicate model rankings;
- implement its own fallback chain;
- infer business decisions from provider errors.

Its job is transport and stable contract handling.

## Acceptance test for a future project

A completely new repository should be considered easy to onboard if a coding agent can:

1. read this integration contract;
2. add the connector;
3. define one or more workload profiles;
4. replace direct LLM calls;
5. run without knowing concrete provider/model names.

If that requires copying code from Job Hunter or OSINT, the connector contract has failed.
