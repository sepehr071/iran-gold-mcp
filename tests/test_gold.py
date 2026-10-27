import httpx
import pytest
from conftest import fixture

from iran_gold_mcp import http

pytestmark = pytest.mark.anyio

P = "/api/v1/public"
PLATFORM_ROUTES = {
    f"{P}/milli-price/external": "price.json",
    "/api/v1/prices": "wallgold.json",
    "/api/v1/exchange/buy-sell-price/": "melligold.json",
    "/loan/api/v1/User/Collateral/GetGoldlPrice": "daric.json",
}


async def test_all_tools_are_read_only(client):
    tools = (await client.list_tools()).tools
    assert {t.name for t in tools} == {"gold_prices", "gold_milli_history", "gold_milli_stats"}
    for t in tools:
        assert t.annotations.read_only_hint is True, t.name
        assert t.description and t.title, t.name


async def test_prices_compare_platforms_in_toman_per_gram(client, api):
    for path, name in PLATFORM_ROUTES.items():
        api[path] = fixture(name)
    r = (await client.call_tool("gold_prices", {})).structured_content
    by = {row["platform"]: row for row in r["prices"]}
    assert by["milli"]["buy"] == by["milli"]["sell"] == 26_890_000  # 268,900 Rial/mg
    assert (by["wallgold"]["buy"], by["melligold"]["buy"]) == (26_220_000, 26_258_490)
    assert (by["daric"]["buy"], by["daric"]["sell"]) == (26_342_055, 26_233_555)  # ask, bid
    assert [row["platform"] for row in r["prices"]] == ["wallgold", "melligold", "daric", "milli"]
    assert (r["best_to_buy"], r["best_to_sell"]) == ("wallgold", "milli")
    assert "failed" not in r


async def test_prices_survive_one_platform_failing(client, api):
    for path, name in PLATFORM_ROUTES.items():
        api[path] = fixture(name)
    api["/api/v1/prices"] = lambda r: httpx.Response(403)
    api["/loan/api/v1/User/Collateral/GetGoldlPrice"] = lambda r: httpx.Response(200, json={"Data": None})
    r = (await client.call_tool("gold_prices", {})).structured_content
    assert {row["platform"] for row in r["prices"]} == {"milli", "melligold"}
    assert "403" in r["failed"]["wallgold"] and "Daric returned no price" in r["failed"]["daric"]


async def test_prices_error_when_no_platform_answers(client, api):
    r = await client.call_tool("gold_prices", {})
    assert r.is_error and "No platform answered" in r.content[0].text


async def test_price_history_thins_and_summarises(client, api):
    api[f"{P}/milli-price/widget/external"] = fixture("widget.json")
    r = (await client.call_tool("gold_milli_history", {"period": "WEEKLY", "points": 5})).structured_content
    assert len(r["points"]) == 5 and r["low"] <= r["last"] <= r["high"]
    assert r["points"][0]["price"] == r["first"]


async def test_price_history_rejects_bad_period(client, api):
    api[f"{P}/milli-price/widget/external"] = fixture("widget.json")
    assert (await client.call_tool("gold_milli_history", {"period": "YEARLY"})).is_error


async def test_platform_stats(client, api):
    api[f"{P}/milli-overall-report"] = fixture("report.json")
    r = (await client.call_tool("gold_milli_stats", {})).structured_content
    assert r["users"] == 27_000_000 and r["branches_and_representatives"] == 16


async def test_cookie_redirect_is_retried(client, api):
    calls = []

    def handler(request):
        calls.append(1)
        if len(calls) == 1:
            return httpx.Response(307, headers={"location": str(request.url)})
        return httpx.Response(200, json=fixture("report.json"))

    api[f"{P}/milli-overall-report"] = handler
    r = await client.call_tool("gold_milli_stats", {})
    assert not r.is_error and len(calls) == 2


async def test_http_error_is_tool_error(client, api):
    api[f"{P}/milli-overall-report"] = lambda r: httpx.Response(403)
    r = await client.call_tool("gold_milli_stats", {})
    assert r.is_error and "403" in r.content[0].text


@pytest.mark.parametrize(
    "tool, path, body",
    [
        ("gold_milli_history", "milli-price/widget/external", {"code": 0, "data": {"prices": None}}),
        (
            "gold_milli_history",
            "milli-price/widget/external",
            {"code": 0, "data": {"prices": {"DAILY": [{"value": 1}]}}},
        ),
    ],
)
async def test_malformed_reply_gives_clear_error(client, api, tool, path, body):
    api[f"{P}/{path}"] = lambda r: httpx.Response(200, json=body)
    r = await client.call_tool(tool, {})
    assert r.is_error and "Milli.gold returned no" in r.content[0].text


async def test_week_stats_include_day_peak_and_live_price(client, api):
    day = [{"timestamp": 2000, "value": 130}, {"timestamp": 3000, "value": 110}]
    week = [{"timestamp": 1000, "value": 100}, {"timestamp": 2500, "value": 120}]
    api[f"{P}/milli-price/widget/external"] = lambda r: httpx.Response(
        200, json={"code": 0, "data": {"prices": {"DAILY": day, "WEEKLY": week}}}
    )
    api[f"{P}/milli-price/external"] = lambda r: httpx.Response(200, json={"code": 0, "data": {"price18": 150}})
    r = (await client.call_tool("gold_milli_history", {"period": "WEEKLY"})).structured_content
    assert (r["first"], r["last"], r["high"], r["low"], r["change_percent"]) == (100, 150, 150, 100, 50.0)
    api[f"{P}/milli-price/external"] = lambda r: httpx.Response(500)
    http._cache.clear()
    r = (await client.call_tool("gold_milli_history", {"period": "WEEKLY"})).structured_content
    assert r["high"] == 130 and r["last"] == 110
