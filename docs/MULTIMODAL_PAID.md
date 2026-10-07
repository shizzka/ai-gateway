# Multimodal and Paid Capacity Requirements

This document captures product requirements for paid image-generation capacity and other future non-text model types.

It is not a commitment to any specific provider.

## Why this belongs in AI Gateway

AI Gateway must not assume that every routed resource is a text LLM.

A future client may request:

- text generation;
- image generation;
- image editing;
- image-to-image transformation;
- vision analysis;
- video generation;
- audio generation or transcription.

The same infrastructure concerns still apply:

- provider/account pool;
- capability matching;
- quota and health state;
- budget policy;
- cost tracking;
- fallback;
- observability;
- Telegram monitoring.

## First image-generation use case

An existing/legacy Telegram image-generation bot is a candidate future client.

A previously used provider appears to be **LaoZhang API**, which exposed several image models including Gemini/Nano Banana-family routes.

This provider should be treated as a candidate paid adapter, not as a permanent architectural dependency.

## Provider/model churn

Image providers change model IDs, aliases and pricing frequently.

Therefore client projects must not hardcode:

- provider names;
- model IDs;
- provider endpoints;
- per-image prices;
- retirement/replacement mappings.

The Gateway model registry owns these details.

## Image workload descriptor

A generation request may need additional routing dimensions beyond text workloads:

- modality: image_generation / image_edit;
- quality target;
- resolution or minimum resolution;
- aspect ratio;
- number of images;
- reference-image support;
- number of reference images;
- text rendering/layout fidelity;
- identity/style consistency;
- latency class;
- synchronous vs queueable/batch;
- maximum cost per request;
- maximum cost per output asset;
- paid allowed;
- provider/model restrictions only when explicitly required.

Example product-level profile:

```yaml
task: generate_image
modality: image_generation
quality_target: normal
resolution: 2K
aspect_ratio: 16:9
paid_allowed: true
max_cost_usd: 0.10
latency: interactive
```

The concrete provider/model is selected by Gateway.

## Paid routing is not a boolean only

`paid_allowed=true` is insufficient for safe routing.

Paid workloads should be able to define hard budget limits such as:

- max cost per request;
- max cost per generated asset;
- daily project budget;
- monthly project budget;
- per-workload budget;
- optional manual approval threshold.

A route that exceeds a hard budget constraint is not eligible.

## Price-aware routing

The Gateway resource registry should support price metadata appropriate to each modality.

For image generation this may include:

- fixed price per image;
- price by output resolution;
- price by execution mode (interactive/batch/flex);
- input/reference-image charges;
- token-based thinking/text charges when applicable;
- provider-specific billing semantics.

Price metadata must be versioned or timestamped because provider pricing changes.

For providers whose exact billing cannot be predicted before the call, Gateway should store an estimate and reconcile with reported usage/billing metadata when available.

## Cost policy examples

### Cheap interactive image

```text
quality_target = normal
resolution = 1K
paid_allowed = true
max_cost_per_asset = low
prefer = cheapest compatible route
```

### Final/high-fidelity asset

```text
quality_target = high
resolution = 4K
reference_images = required
paid_allowed = true
max_cost_per_asset = higher
prefer = quality over cost within budget
```

### Batch/queueable generation

```text
latency = non_interactive
paid_allowed = true
prefer = discounted batch/flex capacity
```

## Billing edge cases

The Gateway must account for provider-specific charging behavior.

Examples:

- successful HTTP response without a usable image may still be billed;
- reference-image input may have separate cost;
- thinking/text tokens may add to image-output cost;
- retries can create duplicate charges;
- async/batch jobs may be billed differently from interactive calls.

A failed validation after a provider reports a billable success must still be recorded as cost incurred.

## Image quality routing

Image quality must be workload-specific.

A cheap model may be sufficient for:

- drafts;
- simple illustrations;
- high-volume social assets.

A stronger model may be required for:

- complex text inside images;
- dense layout;
- identity/style consistency;
- multiple references;
- final production assets.

As with text routing, this suitability belongs in Gateway model-registry metadata and can evolve without client releases.

## Observability

For each image request, record when available:

- project/workload;
- requested image constraints;
- actual provider/model;
- resolution/aspect ratio;
- reference count;
- latency;
- estimated cost;
- actual cost if available;
- retries/fallbacks;
- output count;
- validation status;
- trace ID.

Do not store image bytes in ordinary request logs.

## Telegram integration

Telegram control-plane alerts should support multimodal paid capacity:

- low provider balance;
- image-provider authentication failure;
- model retired/unavailable;
- price metadata stale or changed;
- paid image call executed;
- request blocked by max-cost policy;
- daily/monthly image budget threshold crossed;
- high failed/billed-image rate.

Optional policy: require manual Telegram approval when an individual image request or batch exceeds a configured cost threshold.

## Current candidate: LaoZhang

Historical project documentation referenced:

- LaoZhang API;
- Gemini/Nano Banana image generation;
- a balance endpoint;
- multiple image model routes.

Before implementation:

1. verify current API documentation and supported model list;
2. verify current prices;
3. verify billing behavior for failed/empty responses;
4. verify terms and account limits;
5. add it as a normal paid provider adapter;
6. do not encode LaoZhang-specific behavior in the client connector.

## Migration / test value

The legacy image bot is useful as a fourth integration test because it exercises:

- non-text modality;
- paid-by-default workloads;
- per-asset cost ceilings;
- model selection by image features;
- binary outputs;
- long-running requests;
- provider-specific response formats.

If the bot requires Gateway core changes that are specific to the bot rather than to image-generation capabilities, the abstraction should be reconsidered.
