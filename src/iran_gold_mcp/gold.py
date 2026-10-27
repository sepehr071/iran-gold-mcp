"""Gold tools: live 18k prices across platforms, Milli.gold price history and platform statistics."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Literal

from pydantic import Field

from .http import DARIC, MELLIGOLD, MILLI, WALLGOLD, ApiError, fetch
from .registry import tool

TEHRAN = timezone(timedelta(hours=3, minutes=30))  # no DST since 2022


def _data(body: Any, what: str) -> dict[str, Any]:
    data = body.get("data") if isinstance(body, dict) else None
    if not isinstance(body, dict) or body.get("code") != 0 or not isinstance(data, dict):
        raise ApiError(f"Milli.gold returned no {what}.")
    return data


def _toman(v: Any, site: str) -> int:
    """A positive Toman-per-gram price from a number or numeric string; anything else is a bad reply."""
    try:
        n = int(float(v))
    except (TypeError, ValueError):
        n = 0
    if n <= 0:
        raise ApiError(f"{site} returned no price.")
    return n


def _get(body: Any, key: str) -> Any:
    return body.get(key) if isinstance(body, dict) else None


async def _milli() -> tuple[int, int]:
    d = _data(await fetch(f"{MILLI}/milli-price/external"), "price")
    p = _toman(d.get("price18"), "Milli.gold") * 100  # Rial per mg -> Toman per gram
    return p, p  # one price for buying and selling


async def _wallgold() -> tuple[int, int]:
    rows = _get(await fetch(f"{WALLGOLD}/prices"), "result")
    rows = rows if isinstance(rows, list) else []
    side = {r.get("side"): r.get("price") for r in rows if isinstance(r, dict) and r.get("symbol") == "GLD_18C_750TMN"}
    return _toman(side.get("buy"), "Wallgold"), _toman(side.get("sell"), "Wallgold")


async def _melligold() -> tuple[int, int]:
    d = _get(await fetch(f"{MELLIGOLD}/buy-sell-price/", {"symbol": "XAU18", "format": "json"}), "data")
    return _toman(_get(d, "price_buy"), "Melligold"), _toman(_get(d, "price_sell"), "Melligold")


async def _daric() -> tuple[int, int]:
    d = _get(await fetch(f"{DARIC}/loan/api/v1/User/Collateral/GetGoldlPrice"), "Data")
    # Order book: the user buys at the best ask (BestSellPrice) and sells at the best bid (BestBuyPrice).
    return _toman(_get(d, "BestSellPrice"), "Daric"), _toman(_get(d, "BestBuyPrice"), "Daric")


PLATFORMS = {
    "milli": ("Milli.gold", "https://milli.gold", _milli),
    "wallgold": ("Wallgold", "https://wallgold.ir", _wallgold),
    "melligold": ("Melligold", "https://melligold.com", _melligold),
    "daric": ("Daric", "https://daric.gold", _daric),
}


@tool("Live gold prices on Iranian platforms")
async def gold_prices() -> dict[str, Any]:
    """Compare the live 18k melted-gold price on Milli.gold, Wallgold, Melligold and Daric, in Toman per gram.

    `buy` is what you pay per gram on that platform, `sell` what you get back when you sell. Rows are sorted
    cheapest to buy first; `best_to_buy` and `best_to_sell` name the winners. A platform that did not answer is
    listed under `failed` and the rest still return. Platform fees (often ~0.5 %) are not included. For the
    Milli.gold trend over a day, week or month use gold_milli_history.
    """
    results = await asyncio.gather(*(get() for _, _, get in PLATFORMS.values()), return_exceptions=True)
    rows, failed = [], {}
    for (key, (name, url, _)), res in zip(PLATFORMS.items(), results, strict=True):
        if isinstance(res, ApiError):
            failed[key] = str(res)
        elif isinstance(res, BaseException):
            raise res
        else:
            buy, sell = res
            rows.append({"platform": key, "name": name, "url": url, "buy": buy, "sell": sell, "spread": buy - sell})
    if not rows:
        raise ApiError("No platform answered: " + "; ".join(failed.values()))
    rows.sort(key=lambda r: r["buy"])
    return {
        "as_of": datetime.now(TEHRAN).strftime("%Y-%m-%d %H:%M"),
        "unit": "toman_per_gram",
        "karat": 18,
        "best_to_buy": rows[0]["platform"],
        "best_to_sell": max(rows, key=lambda r: r["sell"])["platform"],
        "prices": rows,
        **({"failed": failed} if failed else {}),
    }


@tool("Milli.gold price history")
async def gold_milli_history(
    period: Annotated[
        Literal["DAILY", "WEEKLY", "MONTHLY"],
        Field(description="Window: DAILY = last ~24 h (15-min points), WEEKLY = last week, MONTHLY = last ~month."),
    ] = "DAILY",
    points: Annotated[int, Field(description="Max points to return, evenly spaced (2-50).", ge=2, le=50)] = 24,
) -> dict[str, Any]:
    """Get the Milli.gold 18k gold price series for a day, week or month, with high, low and change.

    Prices are Rial per milligram (x100 = Toman per gram); `time` is Tehran time. Points are thinned evenly to
    `points`. For today's price on every platform use gold_prices.
    """
    prices = _data(await fetch(f"{MILLI}/milli-price/widget/external"), "price history").get("prices")
    series = prices.get(period) if isinstance(prices, dict) else None
    if not series or not all(isinstance(p, dict) and p.get("timestamp") and p.get("value") for p in series):
        raise ApiError(f"Milli.gold returned no {period} history.")
    series = sorted(series, key=lambda p: p["timestamp"])
    # Like the site: stats span every series from this window's start (the day's peak counts in the week) plus the live price.
    every = [
        p
        for v in prices.values()
        if isinstance(v, list)
        for p in v
        if isinstance(p, dict) and p.get("value") and p.get("timestamp", 0) >= series[0]["timestamp"]
    ]
    values = [p["value"] for p in sorted(every, key=lambda p: p["timestamp"])]
    try:
        values.append(_data(await fetch(f"{MILLI}/milli-price/external"), "price")["price18"])
    except (ApiError, KeyError):
        pass  # live price is a refinement; the series alone is still valid
    step = (len(series) - 1) / (points - 1)
    picked = [series[round(i * step)] for i in range(min(points, len(series)))] if len(series) > points else series
    first, last = values[0], values[-1]
    return {
        "period": period,
        "unit": "rial_per_mg",
        "first": first,
        "last": last,
        "high": max(values),
        "low": min(values),
        "change_percent": round((last - first) / first * 100, 2),
        "points": [
            {
                "time": datetime.fromtimestamp(p["timestamp"] / 1000, TEHRAN).strftime("%Y-%m-%d %H:%M"),
                "price": p["value"],
            }
            for p in picked
        ],
    }


@tool("Milli.gold platform statistics")
async def gold_milli_stats() -> dict[str, Any]:
    """Get Milli.gold's headline numbers: users, trades, gold traded, gold held and branches.

    Figures are rounded totals the company publishes; weights are in kilograms. For prices use gold_prices.
    """
    d = _data(await fetch(f"{MILLI}/milli-overall-report"), "statistics")
    return {
        "users": d.get("overallNumberOfUsers"),
        "trade_transactions": d.get("overallNumberOfTradeTransactions"),
        "traded_gold_kg": d.get("overallTradedMilliTurnoverInKg"),
        "user_balances_kg": d.get("overallUsersMilliBalanceInKg"),
        "burned_kg": d.get("overallBurnedMilliAmountInKg"),
        "branches_and_representatives": d.get("numberOfBranchesAndRepresentatives"),
    }
