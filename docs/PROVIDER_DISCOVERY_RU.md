# Provider Discovery: РФ-оплата, крипта и web search

> Срез рынка на **2026-10-08**. Это discovery-заметки, а не гарантированный прайс или одобренный production allowlist.
>
> Цены, модели, способы оплаты и условия free/trial меняются. Перед подключением провайдера Gateway должен перепроверять актуальные условия.

## Почему это отдельное требование

Для пользователя из РФ недостаточно знать, что модель дешёвая.

Paid route практически бесполезен, если баланс нельзя пополнить доступным способом.

Поэтому в provider registry нужно учитывать не только цену и capabilities, но и:

- `payment_reachable`;
- способы оплаты;
- минимальное пополнение;
- валюту баланса;
- free/trial ограничения;
- trust class канала;
- дату последней проверки цены/оплаты;
- web-search capability отдельно от обычного LLM.

## Кандидаты

### APIrf

Ссылки:
- https://apirf.ru/
- https://apirf.ru/modeli
- https://apirf.ru/ceny
- https://apirf.ru/faq
- https://apirf.ru/oferta

Оплата, публично заявленная на 2026-10-08:

- карта РФ / ЮKassa;
- Telegram Stars;
- **TON**;
- счёт для юрлиц.

Есть guest account / промо-доступ без обычной регистрации.

Примеры публичных цен:

- DeepSeek V4 Pro: **3.32 ₽ input / 8.29 ₽ output за 1M**;
- Gemini 3.1 Pro: **1.99 ₽ / 12 ₽ за 1M**;
- GPT-5.6 Luna: **1.66 ₽ / 4.98 ₽ за 1M**;
- GPT-5.6 Sol: **18 ₽ / 113 ₽ за 1M**;
- Nano Banana 2: **1.33 ₽ за кадр 1K**;
- Nano Banana Pro: **1.99 ₽ за кадр 1K**.

Плюсы:

- очень низкие цены;
- удобная оплата из РФ;
- TON;
- text + image + video;
- OpenAI-compatible text API.

Риски / что проверить:

- цена на часть моделей аномально низкая относительно official API;
- проверить фактическую model identity и качество на golden benchmark;
- проверить реальный context window;
- проверить structured output / tools / vision;
- не использовать критичный judge route до прохождения benchmark;
- постоянного публичного server-side web search API на момент проверки не найдено.

Предварительная роль:

- дешёвый paid pool;
- image-generation provider;
- после benchmark — candidate judge/fallback route.

### Clavis.to

Ссылки:
- https://clavis.to/
- https://clavis.to/news/free-pool-1-free-models

Оплата:

- карта РФ;
- СБП;
- USDT;
- BTC;
- **TON**.

Есть постоянный `free-pool-1`:

- 0 ₽ за input/output;
- нужен баланс от 1 ₽;
- до 25 запросов в сутки на аккаунт;
- без SLA / зависит от доступной ёмкости пула.

В free pool публично заявлены несколько моделей, включая DeepSeek V4 Flash.

Плюсы:

- настоящий free pool;
- РФ-оплата + TON;
- один OpenAI-compatible API;
- text + multimedia.

Риски / что проверить:

- free pool нельзя считать guaranteed capacity;
- не подтверждён отдельный server-side web-search endpoint;
- модели free pool должны проходить capability/quality benchmark перед назначением workload.

Предварительная роль:

- бесплатные scouts;
- дешёвые fallback workload;
- non-critical experimentation.

### TokVenta

Ссылки:
- https://tokventa.tech/
- https://tokventa.tech/pricing
- https://tokventa.tech/providers/deepseek
- https://tokventa.tech/models/deepseek-v4-pro

Оплата:

- CryptoBot;
- **TON**;
- USDT;
- BTC;
- ETH и другие поддержанные CryptoBot валюты;
- прямой USDT TRC-20.

На 2026-10-08 карта РФ / СБП публично обозначены как недоступные.

Пример:

- DeepSeek V4 Pro: **2.25 ₽ input / 6.75 ₽ output за 1M**.

Плюсы:

- крайне дешёвые reasoning/Asian-model routes;
- TON;
- OpenAI-compatible API.

Риски / что проверить:

- model fidelity / actual served model;
- reliability;
- context limits;
- отдельный web-search endpoint публично не подтверждён.

Предварительная роль:

- candidate cheap judge;
- дешёвый reasoning pool;
- только после benchmark для critical workloads.

### ForgetAPI

Ссылки:
- https://forgetapi.ru/
- https://forgetapi.ru/api-neyrosetey-oplata-kartoy

Оплата:

- карта РФ через ЮKassa;
- USDT TRC-20;
- USDT TON;
- BTC;
- **TON**.

Заявлено 140+ моделей и OpenAI-compatible API.

Плюсы:

- удобная доступность из РФ;
- TON и карта РФ;
- широкий каталог;
- budget/key controls.

Риски / что проверить:

- отдельный public server-side web-search endpoint не подтверждён;
- цены на часть моделей не настолько агрессивны, как у APIrf/TokVenta.

Предварительная роль:

- универсальный резервный paid provider;
- дополнительная независимость от одного агрегатора.

### MegaAPI

Ссылки:
- https://megaapi.ru/
- https://megaapi.ru/docs
- https://megaapi.ru/docs/models
- https://megaapi.ru/docs/quickstart

Оплата:

- карта РФ;
- СБП;
- crypto;
- USDT, включая TON-network через CryptoBot.

Публично заявлено:

- 200+ моделей;
- text / vision / image / audio / video;
- **real-time web search через Grok**.

Пример:

- Grok 4.6: **$2.40 input / $7.20 output за 1M**.

Плюсы:

- мультимодальный каталог;
- доступная оплата;
- web-grounded Grok route.

Риски:

- web search здесь следует считать `web_grounding`, пока не доказано, что API возвращает полноценные structured search results + provenance;
- заметно дороже самых дешёвых text-агрегаторов.

Предварительная роль:

- дополнительный grounded research lane;
- multimedia fallback.

### AltRouter

Ссылки:
- https://altrouter.ai/
- https://altrouter.ai/docs/api-reference/
- https://altrouter.ai/docs/limits/

Оплата:

- карта РФ;
- СБП;
- крипта (публично явно указаны USDT/BTC);
- welcome credit $1 после подтверждения Telegram;
- минимальное пополнение публично указано от $15.

API поддерживает:

```json
{
  "web_search": true
}
```

для GPT-5.x и большинства Gemini там, где соответствующий route это поддерживает.

Пример цены:

- Gemini 3.8 Flash: примерно **$0.64 input / $3.19 output за 1M** на момент проверки.

Отдельный публичный surcharge «за один web search» в документации не найден.
Ответ API возвращает `usage.cost`, поэтому фактическую стоимость нужно измерить живым benchmark.

Плюсы:

- server-side fresh web grounding;
- карта РФ / СБП / crypto;
- широкий LLM + image/video каталог;
- фактический cost в response metadata.

Риски / что проверить:

- возвращаются ли достаточные citation/source URL metadata;
- является ли web search отдельной billable component;
- насколько стабильно grounding работает на OSINT запросах;
- `web_search=true` не следует автоматически считать заменой Search Gateway.

Предварительная роль:

- **web_grounding provider**;
- дополнительный OSINT lane;
- не `web_retrieval`, пока provenance не подтверждён.

### LaoZhang

Исторически использовался в старом image-generation tooling.

Интересен как image/video/LLM aggregator, но для наших требований ещё нужно отдельно подтвердить:

- доступность оплаты из РФ;
- crypto / TON;
- актуальные модели;
- актуальные тарифы.

До этого `payment_reachable = unknown`.

## Важное разделение: web_grounding vs web_retrieval

`web_grounding`:

- модель сама делает поиск;
- возвращает итоговый grounded answer;
- может не отдавать полноценный список поисковой выдачи;
- кандидаты: AltRouter, MegaAPI/Grok.

`web_retrieval`:

- возвращает search results;
- URL;
- title/snippet;
- provider metadata;
- provenance;
- позволяет Evidence Store независимо обработать документы.

Для Relocation OSINT полноценный `web_retrieval` остаётся предпочтительным базовым слоем.

## Новые поля Provider Registry

Кандидаты для будущей схемы:

```yaml
provider:
  payment_reachable: true
  payment_methods:
    - ru_card
    - sbp
    - ton
    - usdt
  minimum_topup: null
  trust_class: unverified_discount
  capabilities:
    - text
    - vision
    - image_generation
    - web_grounding
  price_last_verified_at: 2026-10-08
  terms_last_verified_at: 2026-10-08
```

Возможные `trust_class`:

- official;
- verified_discount;
- unverified_discount;
- free_pool;
- trial.

## Правило для critical workloads

Сверхнизкая цена не должна автоматически выигрывать routing.

Для OSINT judge и других critical workload:

1. provider/model route проходит golden benchmark;
2. проверяется context behavior;
3. проверяется structured output;
4. проверяется consistency на известных trap cases;
5. только после этого route может перейти из `unverified_discount` в `verified_discount`.

