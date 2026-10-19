# 🟢 BaleLite

**A lightweight Bale Bot API framework written completely from scratch — sync + async, FSM, middleware, payments.**

> 🇮🇷 **مستندات کامل فارسی:** [README_FA.md](README_FA.md) — راهنمای گام‌به‌گام با نمونه‌کدهای آماده

> BaleLite is not a wrapper around `python-bale-bot` or a port of pyTelegramBotAPI.
> Every layer — HTTP transport, retry policy, type parsing, router, filters, FSM,
> middleware — is implemented in ~3,400 lines of typed, tested Python with only
> `requests` as the runtime dependency. The method surface is **verified against
> the official Bale Bot API docs** (`tapi.bale.ai` / docs.bale.ai).

![CI](https://github.com/AmirRedox2008/balelite/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-143%20offline-brightgreen)

---

## Why BaleLite

Bale's Bot API is modelled on the Telegram Bot API, but it is **not identical**:
no inline mode, no polls, different deep links (`ble.ir`), webhook ports limited
to 443/88, and a built-in payment gateway. BaleLite is built for that reality —
every method it exposes is documented by Bale, and nothing else is advertised.

| | BaleLite | python-bale-bot |
|---|---|---|
| Core dependency | `requests` only | `aiohttp` + `websockets` |
| Sync **and** async APIs | ✅ shared types/filters | ❌ async only |
| Programming model | decorators (`@bot.message_handler`) | event listeners (`@bot.on(...)`) |
| FSM (states) | ✅ 3 storages built-in | ❌ roll your own |
| Middleware | ✅ sync + async | ❌ |
| Payments (sendInvoice, pre-checkout) | ✅ | ✅ |
| License | MIT | GPL-2.0 |
| Code size to read end-to-end | ~3.4k lines | ~10k lines |

And if you already know pyTelegramBotAPI or have a Telegram bot, the code looks
familiar on purpose — see [Porting a Telegram bot to Bale](#porting-a-telegram-bot-to-bale).

## Features

- 🔌 **Full Bot API client** — long polling, webhooks, file upload/download,
  automatic retries and Flood Control (429) handling
- 🎯 **Decorator handlers** — `@bot.message_handler`, `@bot.callback_query_handler`,
  `@bot.pre_checkout_query_handler` and more
- 🧲 **Composable filters** — `commands`, `regexp`, `content_types`, `chat_types`,
  `state`, `AdminFilter`, custom filters
- 🧠 **Built-in FSM** — memory, JSON-file and Redis storages
- 🧱 **Middleware** — chain runs before every handler (logging, anti-flood, bans…)
- 💳 **Bale payments** — `sendInvoice`, `createInvoiceLink`, pre-checkout flow,
  `inquireTransaction`, plus the Bale-specific `askReview`
- ⚡ **Async twin** — same API surface, `aiohttp` under the hood
- 🧵 **Threaded dispatch** — one flag (`threaded=True`), handlers run in parallel
- 🛠 **Utilities** — long-message splitting, HTML/Markdown escaping, `ble.ir` deep links
- 🧪 **143 offline tests** — no token, no internet, no mocks leaking into CI
- 📦 **Packaging** — `pyproject.toml`, full type hints, `py.typed`, GitHub Actions CI

## Installation

```bash
pip install balelite            # sync only (requests)
pip install "balelite[async]"   # + async support (aiohttp)
pip install "balelite[redis]"   # + Redis FSM storage

# from source
git clone https://github.com/your-username/balelite
cd balelite && pip install -e .
```

Python 3.10+ required. Optional extras: `aiohttp` (async), `redis` (FSM), `flask`/`fastapi` (webhooks).

## Quick start — first bot in 10 lines

Get a token from **@BotFather inside the Bale app**, then:

```python
from balelite import Bot

bot = Bot("YOUR-BOT-TOKEN")

@bot.message_handler(commands=["start", "help"])
def welcome(message):
    bot.reply_to(message, "سلام! من یک ربات بله‌ام 🤖")

bot.infinity_polling()
```

Run it: `python examples/echo_bot.py`

## Handlers & filters

```python
@bot.message_handler(commands=["help"])                 # /help, /help@mybot
@bot.message_handler(func=lambda m: "👋" in (m.text or ""))
def hi(message): ...

@bot.message_handler(regexp=r"^\d+$", chat_types=["private"])   # digits only, DMs only
def digits(message): ...

@bot.callback_query_handler(regexp=r"^page:")           # inline keyboard presses
def pager(call):
    bot.answer_callback_query(call.id, text=f"{call.data}")
```

Content types: `text`, `audio`, `document`, `animation`, `photo`, `sticker`,
`video`, `video_note`, `voice`, `location`, `contact`, `new_chat_members`,
`left_chat_member`, `invoice`, `successful_payment` — or `["all"]`.

## Inline keyboards & callbacks

```python
from balelite import InlineKeyboardButton, InlineKeyboardMarkup

menu = InlineKeyboardMarkup().row(
    InlineKeyboardButton("Buy ☕️", callback_data="buy:coffee"),
    InlineKeyboardButton("Site 🌐", url="https://example.com"),
)
bot.send_message(chat_id, "Choose:", reply_markup=menu)
```

## FSM — multi-step forms

```python
from balelite import StateGroup

class Form(StateGroup):
    name, age = State(), State()

@bot.message_handler(commands=["form"])
def ask_name(message):
    bot.set_state(message.from_user.id, Form.name, message.chat.id)
    bot.reply_to(message, "اسمت چیه؟")

@bot.message_handler(state=Form.name)
def ask_age(message):
    bot.update_state_data(message.from_user.id, message.chat.id, name=message.text)
    bot.set_state(message.from_user.id, Form.age, message.chat.id)
    bot.reply_to(message, "چند سالته؟")

@bot.message_handler(state=Form.age)
def done(message):
    data = bot.get_state_data(message.from_user.id, message.chat.id)
    bot.reset_state(message.from_user.id, message.chat.id)
    bot.reply_to(message, f"خوش اومدی {data['name']} عزیز!")
```

## Payments — Bale's killer feature

```python
@bot.callback_query_handler(regexp=r"^buy:")
def on_buy(call):
    bot.send_invoice(
        call.message.chat.id, "Coffee", "A nice cup", "order:coffee:1",
        provider_token="PROVIDER-TOKEN", currency="IRR",
        prices=[("Coffee", 25_000)],           # (label, amount) tuples work
    )

@bot.pre_checkout_query_handler()              # answer within 10 seconds!
def on_checkout(query):
    bot.answer_pre_checkout_query(query.id, ok=True)

@bot.message_handler(content_types=["successful_payment"])
def on_paid(message):
    bot.reply_to(message, f"پرداخت شد: {message.successful_payment.total_amount:,} IRR 🎉")
    bot.ask_review(message.chat.id)            # Bale-specific: ask for a rating
```

Full shop example: [`examples/payments_bot.py`](examples/payments_bot.py).

## Middleware & error handling

```python
@bot.register_middleware(update_types=["message"])
def anti_flood(message, next_):
    if is_spammer(message.from_user.id):
        return                    # drop — handler never runs
    next_()

@bot.exception_handler
def on_error(payload, exception):
    logging.exception("Handler crashed: %s", exception)
```

Errors: `BaleError` → `NetworkError`, `ApiHTTPError`, `ApiBaleError`
(`InvalidTokenError`, `BotBlockedError`, `RateLimitError` with `retry_after`).

## Async bot — same surface

```python
from balelite import AsyncBot

bot = AsyncBot("YOUR-BOT-TOKEN")

@bot.message_handler(commands=["start"])
async def start(message):
    await bot.send_message(message.chat.id, "async! ⚡️")

bot.polling()   # or: asyncio.run(bot.infinity_polling())
```

## Webhooks

Bale accepts webhooks on ports **443 and 88 only**; put Flask/FastAPI behind a
reverse proxy:

```python
bot.set_webhook("https://example.com/webhook", secret_token="s3cret")

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != "s3cret":
        return "forbidden", 403
    bot.process_webhook_update(request.get_json(force=True))
    return "ok", 200
```

## Porting a Telegram bot to Bale

| Telegram habit | Bale reality | BaleLite |
|---|---|---|
| `api.telegram.org` | `tapi.bale.ai` | handled for you |
| `t.me/bot?start=x` links | `ble.ir/bot?start=x` | `create_deep_link()` |
| inline mode (`@bot query`) | ❌ not supported | not exposed |
| polls, dice, stickers-send, venue, video notes | ❌ not documented | not exposed |
| `setMyCommands`, profile photos, `restrictChatMember` | ❌ not documented | not exposed |
| webhook ports 443, 80, 88, 8443 | only **443** and **88** | documented + validated |
| payments via Telegram Stars/PSP | built-in wallet (`sendInvoice`) | ✅ full flow |

The rule: **if it's in BaleLite, it's in Bale's docs.** That makes porting a
matter of changing the import and the token.

## Utility helpers

```python
from balelite import create_deep_link, escape_html, split_text

create_deep_link("mybot", "ref42")   # https://ble.ir/mybot?start=ref42
```

## Running the tests

```bash
pip install -e ".[dev]"
python -m pytest -q     # 143 passed — fully offline
```

## Project structure

```
balelite/
├── src/balelite/
│   ├── api_client.py     # HTTP transport, retries, 429 handling
│   ├── bot.py            # sync Bot: 60+ methods, FSM, middleware, polling
│   ├── async_bot.py      # AsyncBot: same surface on aiohttp
│   ├── handlers.py       # router, filters, decorators
│   ├── fsm.py            # StateGroup + 3 storages
│   ├── middleware.py     # sync/async chains
│   ├── polling.py        # blocking & infinity loops
│   ├── types.py          # Update/Message/Invoice/keyboards…
│   ├── utils.py          # splitting, escaping, deep links
│   └── exceptions.py     # BaleError hierarchy
├── examples/             # echo, async, FSM, keyboards, middleware, webhook, payments
├── tests/                # 143 offline tests
└── .github/workflows/    # CI: 3.10 → 3.13
```

## License

MIT — see [LICENSE](LICENSE). Built as a from-scratch demonstration that a
framework's core is smaller than it looks — and as a companion to
[GramLite](https://github.com/your-username/gramlite), the Telegram twin.
