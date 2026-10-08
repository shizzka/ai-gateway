"""AI Gateway MVP — ядро: hard filter → ранжирование → fallback."""
from __future__ import annotations

import os
import sqlite3
import time
from dataclasses import dataclass, field

import httpx
import yaml

TIERS = {"cheap": 0, "balanced": 1, "critical": 2}
SAFE_FOR_PII = {"trusted", "local"}
FREE_BONUS = 3  # мягкое предпочтение free/local; hard-ограничения его не обходят


@dataclass
class Provider:
    name: str
    base_url: str
    quota_domain: str
    key_env: str | None = None
    data_policy: str = "trains_on_data"


@dataclass
class Model:
    id: str
    provider: str
    served_model: str
    cost: str  # free | paid | local
    caps: set
    context: int
    tier: str
    family: str
    suitability: dict = field(default_factory=dict)


@dataclass
class Workload:
    category: str = "general_text"
    quality: str = "balanced"
    need: set = field(default_factory=set)
    paid_allowed: bool = False
    degrade_ok: bool = True
    data: str = "normal"  # normal | pii
    min_context: int = 0


class NoRoute(Exception):
    def __init__(self, attempts):
        self.attempts = attempts


class Upstream(Exception):
    def __init__(self, status, text):
        self.status, self.text = status, text


class Registry:
    def __init__(self, path: str = "registry.yaml"):
        with open(path, encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        self.providers = {n: Provider(name=n, **p) for n, p in raw["providers"].items()}
        self.models = [Model(**{**m, "caps": set(m["caps"])}) for m in raw["models"]]
        self.workloads = {
            n: Workload(**{**w, "need": set(w.get("need", []))})
            for n, w in raw["workloads"].items()
        }


class State:
    """Cooldown-ы и лог запросов. Переживает рестарт."""

    def __init__(self, path: str = "gateway.db"):
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.executescript(
            "CREATE TABLE IF NOT EXISTS cooldown(scope TEXT PRIMARY KEY, until REAL, reason TEXT);"
            "CREATE TABLE IF NOT EXISTS log(ts REAL, project TEXT, workload TEXT,"
            " model TEXT, status INT, latency REAL);"
        )

    def cool(self, scope: str, seconds: float, reason: str):
        self.db.execute(
            "INSERT OR REPLACE INTO cooldown VALUES(?,?,?)",
            (scope, time.time() + seconds, reason),
        )
        self.db.commit()

    def is_cool(self, scope: str) -> bool:
        row = self.db.execute("SELECT until FROM cooldown WHERE scope=?", (scope,)).fetchone()
        return bool(row and row[0] > time.time())

    def log(self, project, workload, model, status, latency):
        self.db.execute(
            "INSERT INTO log VALUES(?,?,?,?,?,?)",
            (time.time(), project, workload, model, status, latency),
        )
        self.db.commit()


def classify(status: int, retry_after: float | None):
    """-> (retryable, scope, seconds). 599 = сетевая ошибка."""
    if status == 429:
        return True, "domain", retry_after or 300  # квота общая на весь аккаунт
    if status in (401, 403):
        return True, "domain", 3600
    if status in (404, 410):
        return True, "model", 86400  # модель снята
    if status == 408 or status >= 500:
        return True, "model", 120
    return False, "", 0


def score(m: Model, wl: Workload) -> float:
    s = m.suitability.get(wl.category, 5)
    if m.cost in ("free", "local"):
        s += FREE_BONUS
    s -= 100 * max(0, TIERS[wl.quality] - TIERS[m.tier])  # деградация — только если разрешена
    return s


def candidates(reg: Registry, state: State, wl: Workload, avoid_families=frozenset()):
    out = []
    for m in reg.models:
        p = reg.providers[m.provider]
        if not wl.need <= m.caps:
            continue
        if m.context < wl.min_context:
            continue
        if m.cost == "paid" and not wl.paid_allowed:
            continue
        if wl.data == "pii" and p.data_policy not in SAFE_FOR_PII:
            continue
        if not wl.degrade_ok and TIERS[m.tier] < TIERS[wl.quality]:
            continue
        if m.family in avoid_families:
            continue
        if state.is_cool(f"domain:{p.quota_domain}") or state.is_cool(f"model:{m.id}"):
            continue
        out.append(m)
    return sorted(out, key=lambda m: score(m, wl), reverse=True)


async def route_chat(reg, state, wl, body, project="?", workload="?", avoid_families=frozenset()):
    attempts, tried = [], set()
    async with httpx.AsyncClient(timeout=60) as client:
        while True:
            cands = [m for m in candidates(reg, state, wl, avoid_families) if m.id not in tried]
            if not cands:
                raise NoRoute(attempts)  # честный отказ, а не «выдуманный» ответ
            m = cands[0]
            tried.add(m.id)
            p = reg.providers[m.provider]
            key = os.environ.get(p.key_env, "") if p.key_env else ""
            headers = {"Authorization": f"Bearer {key}"} if key else {}

            t0, r = time.time(), None
            try:
                r = await client.post(
                    f"{p.base_url}/chat/completions",
                    json={**body, "model": m.served_model},
                    headers=headers,
                )
                status = r.status_code
            except httpx.HTTPError:
                status = 599
            state.log(project, workload, m.id, status, time.time() - t0)

            if status == 200:
                meta = {
                    "provider": p.name,
                    "model": m.id,
                    "served_model": m.served_model,
                    "family": m.family,
                    "degraded": TIERS[m.tier] < TIERS[wl.quality],
                    "attempts": attempts,
                }
                return r.json(), meta

            ra = r.headers.get("retry-after") if r is not None else None
            retry, scope, secs = classify(status, float(ra) if ra and ra.isdigit() else None)
            attempts.append({"model": m.id, "status": status})
            if not retry:
                raise Upstream(status, r.text[:500] if r is not None else "")
            target = p.quota_domain if scope == "domain" else m.id
            state.cool(f"{scope}:{target}", secs, str(status))
