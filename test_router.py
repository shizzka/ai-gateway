"""Инварианты, которые нельзя сломать при правках. Запуск: pytest -q"""
import asyncio

import httpx
import pytest

import router
from router import NoRoute, Registry, State, candidates, route_chat

reg = Registry("registry.yaml")


@pytest.fixture
def state():
    return State(":memory:")


def ids(ms):
    return [m.id for m in ms]


def test_pii_never_goes_to_training_providers(state):
    wl = reg.workloads["jh.vacancy_match"]
    for m in candidates(reg, state, wl):
        assert reg.providers[m.provider].data_policy in router.SAFE_FOR_PII


def test_paid_forbidden_unless_allowed(state):
    assert all(m.cost != "paid" for m in candidates(reg, state, reg.workloads["osint.scout"]))
    assert "paid-judge" in ids(candidates(reg, state, reg.workloads["osint.judge"]))


def test_no_degrade_means_no_weaker_tier(state):
    wl = reg.workloads["osint.judge"]
    assert all(router.TIERS[m.tier] >= router.TIERS[wl.quality] for m in candidates(reg, state, wl))


def test_quota_domain_cooldown_blocks_whole_account(state):
    wl = reg.workloads["osint.scout"]
    assert "ollama-big" in ids(candidates(reg, state, wl))
    state.cool("domain:ollama-acct-1", 60, "429")
    assert "ollama-big" not in ids(candidates(reg, state, wl))


def test_anti_affinity_excludes_family(state):
    wl = reg.workloads["osint.scout"]
    got = candidates(reg, state, wl, avoid_families=frozenset({"gpt-oss"}))
    assert all(m.family != "gpt-oss" for m in got)


def test_429_triggers_fallback_then_no_route(state, monkeypatch):
    calls = []

    class FakeClient:
        def __init__(self, *a, **k): ...
        async def __aenter__(self): return self
        async def __aexit__(self, *a): ...
        async def post(self, url, json=None, headers=None):
            calls.append(json["model"])
            return httpx.Response(429, request=httpx.Request("POST", url))

    monkeypatch.setattr(router.httpx, "AsyncClient", FakeClient)
    wl = reg.workloads["osint.scout"]
    with pytest.raises(NoRoute) as e:
        asyncio.run(route_chat(reg, state, wl, {"messages": []}))
    assert len(e.value.attempts) == len(set(calls)) >= 1  # каждая модель — максимум раз
    assert candidates(reg, state, wl) == []              # все домены ушли в cooldown
