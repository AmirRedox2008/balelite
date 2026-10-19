# Changelog

## 1.0.0 — initial public release

BaleLite is a from-scratch Bot API framework for the **Bale messenger**
(`tapi.bale.ai`). It is the Bale twin of GramLite: the same layered
architecture, rebuilt against Bale's documented method surface.

### Added
- **Sync `Bot` + async `AsyncBot`** sharing types, filters and FSM; async runs
  on `aiohttp`, sync on `requests`.
- **Core API surface verified against docs.bale.ai**: messaging
  (`send_message`, `edit_message_*`, `forward_message`, `copy_message`,
  `delete_message`, `send_chat_action`), media (`send_photo/video/audio/voice/
  document/animation`, `send_media_group`), location & contact, chat info,
  moderation (`ban/unban/promote_chat_member`, `set_chat_title/description`,
  invite links), pins (`pin/unpin_chat_message`, `unpin_all_chat_messages`),
  sticker sets, webhooks (`set_webhook` with `secret_token`,
  `delete_webhook`, `get_webhook_info`), `get_file` + direct downloads.
- **Bale payments, first-class**: `sendInvoice` (with `LabeledPrice` accepting
  tuples/dicts/objects), `createInvoiceLink`, `answerPreCheckoutQuery`,
  `inquireTransaction`, and the Bale-specific `askReview`.
- **Handlers**: decorator registration with first-match-wins routing over the
  six documented update kinds; filters `commands`, `regexp`, `content_types`,
  `chat_types`, `func`, `custom_filter`, `state`, `pass_args`.
- **FSM**: `State`/`StateGroup` with `MemoryStorage`, `JSONFileStorage`,
  `RedisStorage` (optional extra).
- **Middleware** for sync and async bots with short-circuit semantics, plus a
  global `@bot.exception_handler`.
- **Robust transport**: automatic retry on 429/5xx with `retry_after`
  awareness, typed error hierarchy (`BaleError` base).
- **Utilities**: long-message splitting, HTML/Markdown escaping,
  `ble.ir` deep links, threaded dispatch, infinity polling with back-off.
- **Docs**: bilingual README (English + full Persian), architecture notes,
  seven runnable examples including a complete payments shop.
- **Tests**: 143 offline tests (no token/network), GitHub Actions CI for
  Python 3.10–3.13.

### Not included (by design)
Methods that Telegram documents but Bale does not (inline mode, polls, dice,
`setMyCommands`, sticker *sending*, venue, video notes, profile photos,
`restrictChatMember`, join-request handling) are intentionally absent — the
library mirrors Bale's documented surface exactly.
