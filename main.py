"""OpenAI-совместимый вход. Клиент меняет только base_url и добавляет заголовки:
  X-GW-Project, X-GW-Workload (имя профиля из registry.yaml), X-GW-Diversity-Group (опц.)
Запуск: uvicorn main:app --port 8800
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from router import NoRoute, Registry, State, Upstream, route_chat

reg, state = Registry("registry.yaml"), State()
groups: dict[str, set] = {}  # diversity_group -> уже использованные семейства (in-memory, MVP)
app = FastAPI()


def err(status: int, type_: str, **extra):
    return JSONResponse(status_code=status, content={"error": {"type": type_, **extra}})


@app.post("/v1/chat/completions")
async def chat(req: Request):
    body, h = await req.json(), req.headers
    if body.get("stream"):
        return err(400, "streaming_not_supported")  # MVP

    name = h.get("x-gw-workload", "")
    if name not in reg.workloads:  # неизвестный профиль — ошибка, а не тихий дефолт
        return err(400, "unknown_workload", workload=name)
    wl, project, group = reg.workloads[name], h.get("x-gw-project", "unknown"), h.get("x-gw-diversity-group")

    try:
        data, meta = await route_chat(
            reg, state, wl, body, project, name,
            avoid_families=frozenset(groups.get(group, set())) if group else frozenset(),
        )
    except NoRoute as e:
        return err(503, "gateway_unavailable", attempts=e.attempts)
    except Upstream as e:
        return err(502, "upstream_error", status=e.status, detail=e.text)

    if group:
        groups.setdefault(group, set()).add(meta["family"])
    data["x_gateway"] = meta  # served_model + degraded — клиент видит, что реально отработало
    return data


@app.get("/health")
async def health():
    return {"ok": True}
