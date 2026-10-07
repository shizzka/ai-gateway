# AI Gateway

Русская версия README.

English version: [README.md](README.md)

Общий LLM-gateway для личных проектов и автоматизации.

> Статус: **сбор требований / product discovery**. Production-реализации пока нет.

AI Gateway должен дать таким проектам, как [Job Hunter](https://github.com/shizzka/job-hunter), [Relocation / OSINT](https://github.com/shizzka/relocation-osint) и любым будущим инструментам один стабильный интерфейс к нескольким LLM-провайдерам, аккаунтам и локальным моделям.

Клиентские проекты не должны знать, какой конкретно provider, account или model нужно использовать сейчас. Gateway должен скрывать роутинг, квоты, временные отказы, смену моделей и fallback-логику.

## Основные принципы

- **Free-first:** по умолчанию использовать бесплатную ёмкость, если она подходит для задачи.
- **Task-oriented routing:** проект описывает задачу и требования, а не выбирает конкретного провайдера или модель.
- **Graceful degradation:** проблемы провайдера не должны молча превращаться в плохое бизнес-решение.
- **Provider independence:** приложения не должны хранить собственные цепочки provider/account fallback.
- **Наблюдаемость:** должно быть понятно, куда ушёл запрос, почему был выбран этот маршрут, были ли fallback'и, сколько заняло времени и сколько это стоило.
- **Локальные модели как полноценный ресурс:** Ollama/локальные OpenAI-compatible модели участвуют в общем пуле на тех же принципах, что и облачные.
- **Универсальное подключение:** новый проект должен подключаться через общий connector/SDK без копирования provider-логики из существующих проектов.

## Первые потребители

- [Job Hunter](https://github.com/shizzka/job-hunter)
- [Relocation / OSINT](https://github.com/shizzka/relocation-osint)
- будущие личные проекты

## Как это должно выглядеть для проекта

Проект не должен писать:

```text
use model X
if 429 → model Y
if quota exhausted → provider Z
```

Вместо этого он описывает workload:

```text
task = extraction
quality = balanced
structured_json = required
paid_allowed = false
```

А Gateway уже решает:

```text
workload
  ↓
Task Profile / routing requirements
  ↓
Model Registry
  ↓
health + quota + cost + quality + latency
  ↓
provider + account + model
```

Для известных сценариев вроде Job Hunter matcher или OSINT judge workload задаётся явно.

Для свободных пользовательских запросов в будущем может использоваться небольшой Task Profiler, который классифицирует запрос и формирует Task Profile. Эта идея пока относится к design notes, а не к обязательному MVP.

## Документация

- [Бизнес-требования](docs/BUSINESS_REQUIREMENTS.md)
- [Требования к роутингу](docs/ROUTING_REQUIREMENTS.md)
- [Контракт подключения нового проекта](docs/CLIENT_INTEGRATION.md)
- [Design notes / идеи](docs/DESIGN_NOTES.md)
- [Telegram control plane / мониторинг](docs/TELEGRAM_CONTROL_PLANE.md)
- [Миграция Job Hunter](docs/MIGRATION_FROM_JOB_HUNTER.md)
- [Миграция Relocation / OSINT](docs/MIGRATION_FROM_RELOCATION_OSINT.md)

## Для нового проекта

Не нужно копировать provider-код из Job Hunter или OSINT.

Начинать нужно с [Client integration contract](docs/CLIENT_INTEGRATION.md).

Идеальный сценарий подключения:

1. добавить общий connector/SDK;
2. указать адрес Gateway и identity проекта;
3. описать workload profiles или передавать task requirements;
4. заменить прямые вызовы LLM на вызовы Gateway;
5. не хранить в проекте provider API keys, model rankings и fallback chain.

Если coding agent для подключения нового проекта вынужден читать внутренности Job Hunter или копировать его `llm_client.py`, значит интеграционный контракт спроектирован плохо.

## Текущая граница проекта

Сейчас репозиторий содержит **требования, идеи и планы миграции**.

Пока намеренно не зафиксированы:

- точный API;
- HTTP service vs SDK;
- формат model registry;
- способ хранения quota/cooldown state;
- конкретный алгоритм выбора модели;
- deployment topology.

Сначала фиксируем продуктовую модель и границы ответственности. Потом уже строим очередной сервис, который неизбежно захочет стать платформой.
