import pytest

pytestmark = [pytest.mark.live, pytest.mark.anyio]


async def test_live_prices(client):
    r = (await client.call_tool("gold_prices", {})).structured_content
    assert not r.get("failed"), r.get("failed")
    for row in r["prices"]:
        # 18k gold sits within a few percent across platforms; a unit slip would be off by 10x or more
        assert 0.8 < row["buy"] / r["prices"][0]["buy"] < 1.25, row
        assert row["sell"] <= row["buy"] * 1.02, row


async def test_live_history(client):
    for period in ("DAILY", "WEEKLY", "MONTHLY"):
        r = (await client.call_tool("gold_milli_history", {"period": period, "points": 10})).structured_content
        assert len(r["points"]) == 10 and r["low"] <= r["high"]


async def test_live_stats(client):
    r = (await client.call_tool("gold_milli_stats", {})).structured_content
    assert r["users"] > 1_000_000
