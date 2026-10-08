# AI Gateway

Русская версия: [README.ru.md](README.ru.md)

Shared LLM gateway for personal automation projects.

> Status: **requirements / product discovery + thin MVP skeleton**. The implementation is intentionally minimal and not production-ready.

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
- legacy Telegram image bot / image-generation clients
- future personal automation projects

## Documents

- [Business requirements](docs/BUSINESS_REQUIREMENTS.md)
- [Routing requirements](docs/ROUTING_REQUIREMENTS.md)
- [Client integration contract](docs/CLIENT_INTEGRATION.md)
- [Design notes / ideas](docs/DESIGN_NOTES.md)
- [Telegram control plane](docs/TELEGRAM_CONTROL_PLANE.md)
- [Multimodal and paid capacity](docs/MULTIMODAL_PAID.md)
- [Provider discovery: RU payments / crypto / search](docs/PROVIDER_DISCOVERY_RU.md)
- [Migration from Job Hunter](docs/MIGRATION_FROM_JOB_HUNTER.md)
- [Migration from Relocation / OSINT](docs/MIGRATION_FROM_RELOCATION_OSINT.md)

## For a new project

Do not copy provider code from existing consumers.

A new project should start from [Client integration contract](docs/CLIENT_INTEGRATION.md): add the reusable connector/SDK, identify the project, describe workload requirements, and let AI Gateway choose the concrete provider/model route.


## Thin MVP skeleton

The repository now contains a deliberately small runnable Gateway skeleton:

- OpenAI-compatible `POST /v1/chat/completions`;
- FastAPI HTTP service;
- YAML provider/model/workload registry;
- SQLite cooldown and request log state;
- hard capability/cost/PII filtering;
- simple suitability ranking;
- fallback on retryable upstream failures;
- shared `quota_domain` cooldown;
- model-family anti-affinity;
- typed unavailable/upstream errors;
- basic invariant tests.

This is a validation scaffold, not the final architecture.

Run locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
uvicorn main:app --host 127.0.0.1 --port 8800
```

Configure provider credentials through the environment variables referenced by `registry.yaml`. The registry currently contains example provider/model entries and must be reviewed before real traffic is enabled.

Initial client integration should be Job Hunter behind a feature flag / shadow path. Relocation / OSINT integration comes later.

## Current scope

This repository currently owns **requirements and migration planning only**. Implementation choices, API contracts and deployment architecture are intentionally not frozen yet.
