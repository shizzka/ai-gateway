# Routing Requirements

This document describes how AI Gateway should decide which model receives a task.

It defines product-level routing behavior, not an implementation algorithm.

## Core rule

The client says **what the task requires**.

The Gateway decides **which currently available model/provider/account should execute it**.

Model selection must not be hardcoded in client projects.

## Inputs to routing

Routing should consider three groups of information.

### 1. Workload requirements

Examples:

- task category;
- quality tier;
- text / vision / coding;
- structured JSON support;
- reasoning strength;
- minimum context requirement;
- latency/deadline;
- degradation policy;
- cost policy;
- diversity constraints.

### 2. Model suitability metadata

The Gateway maintains a model registry.

A model entry may include:

- provider/model identity;
- supported capabilities;
- context limits;
- structured-output reliability;
- workload suitability such as extraction, classification, coding, reasoning or vision;
- quality tier(s);
- expected latency class;
- cost class;
- whether the model is free, paid or locally hosted;
- known restrictions.

Suitability is Gateway-owned configuration/data, not client code.

### 3. Runtime state

Routing must also account for current operational state:

- provider/account health;
- active cooldowns;
- quota exhaustion;
- recent rate limits;
- model retirement/unavailability;
- observed latency;
- optional recent reliability metrics.

## Selection process

Conceptually, routing occurs in this order:

1. **Hard filtering**
   - remove models missing required capabilities;
   - remove models forbidden by cost policy;
   - remove models that cannot satisfy context/format requirements;
   - remove unavailable/cooldown resources when appropriate;
   - enforce diversity/anti-affinity constraints.

2. **Suitability ranking**
   - prefer models rated stronger for the requested workload;
   - consider requested quality tier;
   - consider free-first policy;
   - consider latency preference;
   - consider operational reliability.

3. **Selection**
   - choose the highest-ranked currently eligible route.

4. **Fallback**
   - on retryable infrastructure failure, repeat selection from remaining compatible routes;
   - never relax a hard constraint silently.

## Hard vs soft requirements

This distinction is mandatory.

Examples of hard requirements:

- vision required;
- structured JSON required;
- paid forbidden;
- actual model must differ from other members of an anti-affinity group;
- no weaker-model degradation.

Examples of soft preferences:

- fastest available;
- prefer free;
- prefer stronger reasoning;
- prefer local;
- prefer lower recent failure rate.

A soft preference may be relaxed. A hard requirement may not.

## Task categories

The Gateway should support generic categories to avoid project-specific code.

Initial examples:

- general_text;
- summarization;
- extraction;
- classification;
- judgement;
- reasoning;
- coding;
- vision;
- structured_generation.

Projects may define named workloads that map onto these categories plus policy.

Example:

```text
Job Hunter vacancy_match
→ category=classification/judgement
→ quality=balanced
→ structured_json=true
→ paid=false

OSINT scout
→ category=research synthesis
→ quality=balanced
→ structured_json=true
→ free_only
→ diversity_group=research-run-123

OSINT judge
→ category=judgement
→ quality=critical
→ reasoning=true
→ paid_allowed=true
→ no_weaker_model
```

The exact category vocabulary can evolve. Client projects must not depend on a particular concrete model for a category.

## How the Gateway "knows" which model is good at which task

This must be explicit data, not mystical prompt intuition.

The Gateway should maintain model suitability metadata derived from:

- known model capabilities;
- controlled benchmarks;
- project-specific observed quality;
- manual overrides where needed;
- provider documentation;
- production reliability metrics.

A future model can therefore be added by updating its registry/rating data rather than changing every client.

The MVP may begin with manually maintained suitability tiers. More automated benchmarking can come later.

## Avoid per-request LLM classification by default

The Gateway should not need another LLM call merely to decide where to send an LLM call.

For ordinary use:

- the project/connector supplies the workload descriptor;
- named workload profiles provide defaults;
- the router uses registry data.

Prompt-based automatic task inference may exist later as an optional convenience fallback, but it must not be the safety-critical routing mechanism.

## Dynamic model changes

If model A disappears tomorrow and model B becomes the best free extraction model, client projects should not change.

Only Gateway routing data/policy changes.

This is one of the central reasons the Gateway exists.

## Quality feedback loop

The architecture should allow routing suitability to evolve over time.

Potential future signals:

- schema validation success;
- task-specific validator success;
- user/project acceptance;
- hallucination or grounding failures;
- latency;
- retry rate;
- cost.

The MVP does not need autonomous learning, but routing data must be replaceable without client releases.

## Safety

The Gateway selects compute capacity, not domain truth.

A stronger model choice does not replace:

- Job Hunter grounding and safety guards;
- OSINT source/citation validation;
- project-specific validators.

Routing and domain validation remain separate responsibilities.
