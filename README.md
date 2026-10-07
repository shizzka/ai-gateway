# AI Gateway

Shared LLM gateway for personal automation projects.

> Status: **requirements / product discovery**. There is no production implementation yet.

AI Gateway is intended to provide projects such as [Job Hunter](https://github.com/shizzka/job-hunter) and relocation/OSINT tooling with one stable interface to multiple LLM providers, accounts and local models.

The gateway should hide provider-specific routing, quotas, temporary outages and model churn from client applications.

## Product principles

- **Free-first:** prefer zero-cost capacity when it is suitable for the task.
- **Task-oriented routing:** clients request capabilities and quality level, not a specific provider account.
- **Graceful degradation:** provider failures must not silently become bad business decisions.
- **Provider independence:** applications should not contain provider/account fallback chains.
- **Observable decisions:** routing, fallback, latency, usage and cost must be explainable.
- **Local models are first-class providers:** local Ollama-compatible capacity participates in the same routing model as cloud providers.

## Initial consumers

- Job Hunter
- [Relocation / OSINT](https://github.com/shizzka/relocation-osint)
- future personal automation projects

## Documents

- [Business requirements](docs/BUSINESS_REQUIREMENTS.md)
- [Migration from Job Hunter](docs/MIGRATION_FROM_JOB_HUNTER.md)
- [Migration from Relocation / OSINT](docs/MIGRATION_FROM_RELOCATION_OSINT.md)

## Current scope

This repository currently owns **requirements and migration planning only**. Implementation choices, API contracts and deployment architecture are intentionally not frozen yet.
