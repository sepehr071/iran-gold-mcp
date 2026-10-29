<!-- mcp-name: io.github.sepehr071/iran-gold-mcp -->

<div align="center">

<img src="https://raw.githubusercontent.com/sepehr071/iran-gold-mcp/main/.github/banner.png" alt="iran-gold-mcp: compare live 18k gold prices on Milli.gold, Wallgold, Melligold, Daric and Taline from Claude, Cursor or Copilot" width="100%">

# iran-gold-mcp: live gold prices from Iranian gold platforms for AI agents

**Compare the 18k gold price on Milli.gold, Wallgold, Melligold, Daric and Taline from your AI agent.**<br>
An unofficial, read-only MCP server for Iranian online platforms that sell 18k melted gold (طلای آب&zwnj;شده):<br>
live buy and sell price per gram on each platform, the cheapest place to buy, the best place to sell, and Milli.gold's price history.

[![PyPI](https://img.shields.io/pypi/v/iran-gold-mcp?color=2563eb)](https://pypi.org/project/iran-gold-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/iran-gold-mcp)](https://pypi.org/project/iran-gold-mcp/)
[![CI](https://github.com/sepehr071/iran-gold-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/sepehr071/iran-gold-mcp/actions/workflows/ci.yml)
[![MCP Registry](https://img.shields.io/badge/MCP_Registry-io.github.sepehr071%2Firan--gold--mcp-7c3aed)](https://registry.modelcontextprotocol.io/?q=iran-gold-mcp)
[![License: MIT](https://img.shields.io/badge/license-MIT-16a34a)](https://github.com/sepehr071/iran-gold-mcp/blob/main/LICENSE)

[![Install in Cursor](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/en/install-mcp?name=iran-gold&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJpcmFuLWdvbGQtbWNwIl19)
[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_iran--gold--mcp-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://vscode.dev/redirect/mcp/install?name=iran-gold&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22iran-gold-mcp%22%5D%7D)

[For AI agents](#for-ai-agents) · [Quick start](#quick-start) · [Tools](#tools) · [Good to know](#good-to-know) · [FAQ](#faq) · [فارسی](#فارسی)

</div>

---

## For AI agents

- **What:** unofficial MCP server (model context protocol) for the public prices of five Iranian online gold platforms: milli.gold, wallgold.ir, melligold.com, daric.gold and taline.ir.
- **Install:** `uvx iran-gold-mcp` or `claude mcp add iran-gold -- uvx iran-gold-mcp`. Transport: stdio. Needs [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python 3.10+).
- **Auth:** none, no API key or account. Optional `IRAN_GOLD_MCP_PROXY` (HTTP proxy URL, or a comma-separated list); system proxy settings are ignored.
- **Access:** read-only, so no confirmation is needed before calling any tool. It cannot log in, trade or read a wallet.
- **Tools:** 3, all prefixed `gold_`. Typical sequence: `gold_prices` -> `gold_milli_history`.
- **Use when:** the user asks what 18k melted gold costs per gram on these platforms, where it is cheapest to buy or best to sell, or how the Milli.gold price moved over a day, week or month.
- **Do not use when:** the user wants to buy or sell gold, or wants dollar, coin or crypto prices (see [tgju-mcp](https://github.com/sepehr071/tgju-mcp)).
- **Output:** compact JSON. `gold_prices` is **Toman per gram** of 18k gold; `gold_milli_history` is Rial per milligram. Times are Tehran time.

## Why

Every Iranian gold platform quotes its own price, in its own unit: Milli.gold in Rial per milligram, the others in
Toman per gram, Daric as an order book with a separate bid and ask, and Taline only on its homepage. `iran-gold-mcp` reads all five at
once,
converts them to Toman per gram and sorts them:

> **You:** Where is 18k gold cheapest to buy right now?
>
> **Agent:** *calls* `gold_prices()`
>
> Milli.gold is cheapest at 25,935,000 Toman per gram, then Wallgold (26,078,000), Melligold (26,133,565), Daric
> (26,209,064) and Taline (26,262,300). Platform fees are not included.

<sub>Real prices from 2026-10-27; they change all the time.</sub>

Example prompts:

- "Compare the 18k gold price per gram on Milli, Wallgold, Melligold, Daric and Taline."
- "Where should I sell 2 grams of melted gold right now?"
- "Show me Milli.gold's gold price for the last month. What were the high and the low?"
- <span dir="rtl">قیمت طلای آب&zwnj;شده الان در کدام سایت ارزان&zwnj;تر است؟</span>
- <span dir="rtl">قیمت هر گرم طلای ۱۸ عیار در میلی، وال&zwnj;گلد، ملی&zwnj;گلد، داریک و طلاین را مقایسه کن.</span>

## Quick start

You need [uv](https://docs.astral.sh/uv/getting-started/installation/). No API key or account.

<details open>
<summary><b>Claude Code</b></summary>

```bash
claude mcp add iran-gold -- uvx iran-gold-mcp
```
</details>

<details>
<summary><b>Claude Desktop</b></summary>

Settings → Developer → Edit Config, then add:

```json
{
  "mcpServers": {
    "iran-gold": { "command": "uvx", "args": ["iran-gold-mcp"] }
  }
}
```
</details>

<details>
<summary><b>Cursor</b></summary>

Click **Install in Cursor** above, or add the Claude Desktop block to `~/.cursor/mcp.json`.
</details>

<details>
<summary><b>VS Code (Copilot agent mode)</b></summary>

Click **Install in VS Code** above, or add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "iran-gold": { "type": "stdio", "command": "uvx", "args": ["iran-gold-mcp"] }
  }
}
```
</details>

<details>
<summary><b>Codex CLI</b></summary>

```bash
codex mcp add iran-gold -- uvx iran-gold-mcp
```
</details>

<details>
<summary><b>Anything else</b></summary>

It's a standard stdio MCP server: run `uvx iran-gold-mcp`, or `pip install iran-gold-mcp` and run `iran-gold-mcp`.
</details>

## Tools

All 3 tools are read-only and return compact JSON.

| Tool | What it does |
|---|---|
| `gold_prices` | Compares the live 18k gold buy and sell price per gram (Toman) on Milli.gold, Wallgold, Melligold, Daric and Taline, cheapest first, with `best_to_buy` and `best_to_sell`. A platform that does not answer is listed under `failed`; the rest still return |
| `gold_milli_history` | Gets the Milli.gold 18k gold price series for a day, week or month (`period`: `DAILY`, `WEEKLY`, `MONTHLY`; `points`: 2-50, default 24) with first, last, high, low and change percent |
| `gold_milli_stats` | Gets Milli.gold's headline numbers: users, trade transactions, gold traded (kg), user balances (kg), burned gold (kg), branches and representatives |

## Good to know

- **Buy and sell.** `buy` is what you pay per gram on that platform, `sell` what you get when you sell. Milli.gold, Wallgold and Melligold often show one price for both; Daric is an order book, so `buy` is the best ask and `sell` the best bid.
- **Fees are not included.** Platforms charge a trading fee (often around 0.5 %) on top of the price.
- **Platform prices, not market quotes.** Each number is that platform's own price for 18k melted gold, so expect small differences from tgju and from each other.
- **Units.** Milli.gold quotes Rial per milligram; `gold_prices` converts it (x100 = Toman per gram). `gold_milli_history` keeps Rial per milligram.
- **Tehran time.** `as_of` and history `time` values are Tehran time (UTC+3:30).
- **15 s cache.** Repeated calls within 15 seconds reuse the answer.
- **Taline needs an Iranian connection.** Taline puts its price only on its homepage and only for visitors from Iran;
  elsewhere it is listed under `failed`. Outside Iran set `IRAN_GOLD_MCP_PROXY` to an Iranian HTTP proxy.

## FAQ

<details>
<summary><b>Is there an API for Iranian gold platform prices?</b></summary>

Not an official one. `iran-gold-mcp` calls the public, login-free price endpoints that the platforms' own websites use.
</details>

<details>
<summary><b>How is it different from milligold-mcp and tgju-mcp?</b></summary>

[milligold-mcp](https://github.com/sepehr071/milligold-mcp) covers Milli.gold only. `iran-gold-mcp` covers Milli.gold
plus Wallgold, Melligold, Daric and Taline and compares them. [tgju-mcp](https://github.com/sepehr071/tgju-mcp) gives
market-wide rates for dollar, coins, gold and crypto.
</details>

<details>
<summary><b>Can it buy or sell gold for me?</b></summary>

No, and that's deliberate. It has no login and only reads public data.
</details>

<details>
<summary><b>Do I need an Iranian IP or a proxy?</b></summary>

Not by default. If requests are blocked from your network, set `IRAN_GOLD_MCP_PROXY` to an HTTP proxy. System proxy variables are ignored on purpose.
</details>

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `IRAN_GOLD_MCP_PROXY` | unset | Optional HTTP proxy URL for the platform requests. A comma-separated list is used one at a time: the next proxy takes over when one is blocked or cannot connect. System proxy settings are ignored |

<a id="فارسی"></a>

## فارسی: سرور MCP قیمت طلای آب&zwnj;شده

<div dir="rtl">

**iran-gold-mcp** یک سرور MCP غیررسمی و فقط&zwnj;خواندنی است که قیمت لحظه&zwnj;ای طلای ۱۸ عیار آب&zwnj;شده را از پلتفرم&zwnj;های آنلاین [میلی](https://milli.gold)، [وال&zwnj;گلد](https://wallgold.ir)، [ملی&zwnj;گلد](https://melligold.com)، [داریک](https://daric.gold) و [طلاین](https://taline.ir) می&zwnj;خواند و مقایسه می&zwnj;کند.

- قیمت خرید و فروش هر گرم (تومان) در هر پلتفرم، از ارزان&zwnj;ترین به گران&zwnj;ترین، با بهترین جا برای خرید و فروش.
- تاریخچه قیمت میلی در روز، هفته و ماه گذشته و آمار پلتفرم میلی.
- فقط خواندنی است: خرید و فروش نمی&zwnj;کند و وارد حساب نمی&zwnj;شود. کارمزد پلتفرم&zwnj;ها در قیمت&zwnj;ها حساب نشده است.
- طلاین قیمت را فقط به بازدیدکننده&zwnj;های داخل ایران نشان می&zwnj;دهد؛ بیرون از ایران `IRAN_GOLD_MCP_PROXY` را روی یک پراکسی ایرانی بگذارید.

</div>

```bash
claude mcp add iran-gold -- uvx iran-gold-mcp
```

## Development

```bash
git clone https://github.com/sepehr071/iran-gold-mcp && cd iran-gold-mcp
uv sync
uv run ruff check . && uv run ruff format --check .
uv run python -m pytest -q          # offline unit tests
uv run python -m pytest -m live -q  # calls the real platforms
uv build
```

## Related servers

- [milligold-mcp](https://github.com/sepehr071/milligold-mcp) for Milli.gold only
- [tgju-mcp](https://github.com/sepehr071/tgju-mcp) for dollar, euro, gold, coin, crypto and commodity prices from tgju.org
- [iran-mcp](https://github.com/sepehr071/iran-mcp): catalog of all Iranian-service MCP servers
- [mcpfarsi.ir](https://mcpfarsi.ir/): Persian marketplace of MCP servers for Iranian services

## Disclaimer

Unofficial and not affiliated with or endorsed by Milli.gold, Wallgold, Melligold, Daric or Taline. It is read-only and uses
public endpoints that can change without notice. Prices are informational and not financial advice.

## Author

<a href="https://www.linkedin.com/in/sepehr-radmard"><img src="https://raw.githubusercontent.com/sepehr071/iran-mcp/main/assets/author-banner.png" alt="Sepehr Radmard: open-source MCP servers for the Iranian web. LinkedIn: linkedin.com/in/sepehr-radmard" width="100%"></a>

Built and maintained by **Sepehr Radmard** (سپهر رادمرد). Connect on [LinkedIn](https://www.linkedin.com/in/sepehr-radmard) or follow [@sepehr071 on GitHub](https://github.com/sepehr071) for more MCP servers for Iranian websites, all listed in [iran-mcp](https://github.com/sepehr071/iran-mcp).

## License

[MIT](https://github.com/sepehr071/iran-gold-mcp/blob/main/LICENSE)
