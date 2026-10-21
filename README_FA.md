# 📚 بله‌لایت (BaleLite) — مستندات کامل فارسی

> **بله‌لایت** یک فریم‌ورک کامل و سبک برای ساخت ربات پیام‌رسان **بله** است که **از صفر** و بدون استفاده از کتابخانه‌های آماده مثل python-bale-bot نوشته شده است. تمام لایه‌ها — از کلاینت HTTP گرفته تا سیستم هندلر، ماشین حالت، میان‌افزار و **پرداخت درون‌چتی** — در همین پروژه پیاده‌سازی شده‌اند.
>
> این مستندات مرجع کامل استفاده از کتابخانه است. نسخه انگلیسی: [README.md](README.md) | معماری داخلی: [ARCHITECTURE.md](ARCHITECTURE.md)
>
> ⚠️ **دقت مهم:** لیست متدهای این کتابخانه دقیقاً با مستندات رسمی بله (docs.bale.ai) تطبیق داده شده است. هر متدی که بله پشتیبانی نمی‌کند (inline mode، نظرسنجی و…) اصلاً در کتابخانه وجود ندارد — پس با سورس غیرواقعی مواجه نیستید.

---

## 📖 فهرست مطالب

1. [ویژگی‌ها](#-ویژگیها)
2. [تفاوت‌های بله با تلگرام](#-تفاوتهای-بله-با-تلگرام)
3. [نصب](#-نصب)
4. [دریافت توکن از BotFather در بله](#-دریافت-توکن-از-botfather-در-بله)
5. [شروع سریع — اولین ربات در ۱۰ خط](#-شروع-سریع)
6. [هندلرها و فیلترها](#-هندلرها-و-فیلترها)
7. [کیبوردها (دکمه‌های شیشه‌ای و معمولی)](#-کیبوردها)
8. [ماشین حالت (FSM) — فرم‌های چندمرحله‌ای](#-ماشین-حالت-fsm)
9. [میان‌افزار (Middleware)](#-میانافزار-middleware)
10. [مدیریت خطاها](#-مدیریت-خطاها)
11. [کار با فایل‌ها (ارسال و دانلود)](#-کار-با-فایلها)
12. [💳 پرداخت در بله — ویژگی امضای این کتابخانه](#-پرداخت-در-بله)
13. [نسخه Async](#-نسخه-async)
14. [وبهوک (Webhook)](#-وبهوک-webhook)
15. [مرجع متدهای پرکاربرد](#-مرجع-متدهای-پرکاربرد)
16. [ابزارهای کمکی](#-ابزارهای-کمکی)
17. [مهاجرت ربات تلگرامی به بله](#-مهاجرت-ربات-تلگرامی-به-بله)
18. [اجرای تست‌ها](#-اجرای-تستها)
19. [ساختار پروژه](#-ساختار-پروژه)
20. [انتشار در گیت‌هاب و رزومه](#-انتشار-در-گیتهاست-و-رزومه)

---

## ✨ ویژگی‌ها

- 🔌 **کلاینت کامل Bot API بله** — لانگ‌پولینگ، وبهوک، آپلود/دانلود فایل، تلاش مجدد خودکار و مدیریت Flood Control (429)
- 🎯 **هندلرهای دکوریتوری** — `@bot.message_handler`، `@bot.callback_query_handler`، `@bot.pre_checkout_query_handler` و…
- 🧲 **فیلترهای قدرتمند و قابل ترکیب** — `commands`، `regexp`، `content_types`، `chat_types`، `state` و فیلتر سفارشی
- 🧠 **ماشین حالت (FSM) داخلی** — با سه ذخیره‌ساز: حافظه، فایل JSON و Redis
- 🧱 **میان‌افزار** — زنجیره‌ای، قبل از همه هندلرها (لاگ، ضد اسپم، بن و…)
- 💳 **پرداخت کامل بله** — `sendInvoice`، `createInvoiceLink`، `inquireTransaction` و متد اختصاصی `askReview`
- ⚡ **نسخه Async** — همان API در حالت غیرهمزمان با aiohttp
- 🚦 **مدیریت خودکار محدودیت نرخ** — استثنای `RateLimitError` همراه با `retry_after`
- 🧵 **Dispatch چندنخی** — اجرای موازی هندلرها با یک پارامتر
- 🛠 **ابزارهای کمکی** — تقسیم پیام بلند، escape کردن HTML/Markdown، دیپ‌لینک `ble.ir`
- 🧪 **۱۴۳ تست خودکار آفلاین** — بدون نیاز به اینترنت و توکن
- 📦 **بسته‌بندی استاندارد** — `pyproject.toml`، تایپ‌هینت کامل، CI آماده (پایتون ۳.۱۰ تا ۳.۱۳)

---

## 🆚 تفاوت‌های بله با تلگرام

چون API بله بر پایه API تلگرام ساخته شده، خیلی‌ها فکر می‌کنند «همه‌چیز مثل تلگرام است». نیست! این جدول واقعیت است:

| موضوع | تلگرام | بله |
|---|---|---|
| آدرس API | `api.telegram.org` | `tapi.bale.ai` |
| دیپ‌لینک ربات | `t.me/bot?start=x` | `ble.ir/bot?start=x` |
| Inline mode (`@bot query`) | ✅ | ❌ وجود ندارد |
| نظرسنجی (Poll) و تاس (Dice) | ✅ | ❌ در مستندات نیست |
| `setMyCommands`، عکس پروفایل، `restrictChatMember` | ✅ | ❌ در مستندات نیست |
| پورت‌های مجاز وبهوک | 443، 80، 88، 8443 | فقط **443** و **88** |
| نگهداری آپدیت‌ها | ۲۴ ساعت | ۲۴ ساعت / حداکثر ۲۰۰۰ پیام |
| پرداخت | از طریق درگاه واسط | 💳 کیف پول داخلی بله |

بله‌لایت این واقعیت را جدی گرفته: **فقط متدهایی که بله مستند کرده در کتابخانه هستند.**

---

## 📦 نصب

```bash
pip install balelite            # فقط نسخه sync (با requests)
pip install "balelite[async]"   # + پشتیبانی async (با aiohttp)
pip install "balelite[redis]"   # + ذخیره‌ساز Redis برای FSM
```

نصب از سورس (برای توسعه):

```bash
git clone https://github.com/your-username/balelite
cd balelite
pip install -e ".[dev]"
```

---

## 🎫 دریافت توکن از BotFather در بله

1. اپلیکیشن بله را باز کنید و به ربات **[@BotFather](https://ble.ir/BotFather)** پیام دهید.
2. دستور `/newbot` را بزنید و طبق راهنمایی، **نام** و **یوزرنیم** (باید به `bot` تمام شود) ربات را انتخاب کنید.
3. توکن چیزی شبیه `12345678:AAEhBOweik6ad9r_QXMENQjcrGbqCr4K-4s` دریافت می‌کنید.
4. ⚠️ توکن را مثل رمز عبور نگه دارید — هر کسی که توکن را داشته باشد، ربات شماست!

> نکته: برای دریافت توکن پرداخت (provider token)، از همان BotFather بخش Payments را دنبال کنید یا با پشتیبانی توسعه‌دهندگان بله (گروه dev.bale.ai) هماهنگ شوید.

---

## 🚀 شروع سریع

اولین ربات — فقط ۱۰ خط:

```python
from balelite import Bot

bot = Bot("YOUR-BOT-TOKEN")

@bot.message_handler(commands=["start", "help"])
def welcome(message):
    bot.reply_to(message, "سلام! من یک ربات بله‌ام 🤖")

@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.send_message(message.chat.id, f"گفتی: {message.text}")

bot.infinity_polling()
```

اجرا:

```bash
python examples/echo_bot.py
```

همین! از این به بعد تا وقتی اسکریپت باز است، ربات به هر پیام جواب می‌دهد. (`Ctrl+C` برای توقف)

---

## 🎯 هندلرها و فیلترها

هر نوع رویداد یک دکوریتور دارد و هر دکوریتور چندین فیلتر قابل ترکیب می‌پذیرد:

```python
# دستورها — /help و /help@mybot هر دو می‌آیند
@bot.message_handler(commands=["help"])
def help_cmd(message):
    bot.reply_to(message, "راهنما: ...")

# عبارت باقاعده — فقط پیام‌های عددی در چت خصوصی
@bot.message_handler(regexp=r"^\d+$", chat_types=["private"])
def digits(message):
    bot.reply_to(message, "عدد گرفتم!")

# دکمه‌های شیشه‌ای — فشار callback با regexp روی data
@bot.callback_query_handler(regexp=r"^page:")
def pager(call):
    bot.answer_callback_query(call.id, text=f"صفحه {call.data.split(':')[1]}")

# پیام‌های ویرایش‌شده
@bot.edited_message_handler(content_types=["text"])
def edited(message):
    bot.reply_to(message, "ویرایشش کردی،ها! 👀")

# پست‌های کانال
@bot.channel_post_handler()
def posts(message):
    ...

# فیلتر تابعی و pass_args
@bot.message_handler(commands=["ban"], pass_args=True, custom_filter=AdminFilter())
def ban(message):
    target_id = int(message.args[0])
    bot.ban_chat_member(message.chat.id, target_id)
```

**فیلترهای موجود:**

| فیلتر | مثال | توضیح |
|---|---|---|
| `commands` | `commands=["start"]` | دستورهای مجاز (با `/`) |
| `regexp` | `regexp=r"^\d+$"` | الگوی regex روی متن پیام یا `callback_data` |
| `content_types` | `content_types=["photo"]` | نوع محتوا؛ `["all"]` برای همه |
| `chat_types` | `chat_types=["private"]` | `private`، `group`، `supergroup`، `channel` |
| `func` | `func=lambda m: ...` | هر شرط دلخواه پایتونی |
| `custom_filter` | `custom_filter=AdminFilter()` | فیلتر سفارشی (کلاس `BaseFilter`) |
| `state` | `state=Form.name` | فقط وقتی کاربر در آن حالت FSM است |
| `pass_args` | `pass_args=True` | آرگومان‌های بعد از دستور در `message.args` |

**انواع محتوا:** `text`، `audio`، `document`، `animation`، `photo`، `sticker`، `video`، `video_note`، `voice`، `location`، `contact`، `new_chat_members`، `left_chat_member`، `invoice`، `successful_payment` — و `["all"]`.

**دکوراتورهای موجود:** `message_handler`، `edited_message_handler`، `channel_post_handler`، `edited_channel_post_handler`، `callback_query_handler`، `pre_checkout_query_handler` — همین‌ها؛ چون آپدیت‌های بله فقط همین شش نوع را شامل می‌شوند.

---

## ⌨️ کیبوردها

```python
from balelite import (
    InlineKeyboardButton, InlineKeyboardMarkup,     # دکمه شیشه‌ای (زیر پیام)
    KeyboardButton, ReplyKeyboardMarkup,            # کیبورد معمولی (جای تایپ)
    ReplyKeyboardRemove, ForceReply,
)

# کیبورد شیشه‌ای — callback_data یا url
menu = InlineKeyboardMarkup(row_width=2)
menu.add(
    InlineKeyboardButton("خرید ☕️", callback_data="buy:coffee"),
    InlineKeyboardButton("کیک 🍰", callback_data="buy:cake"),
    InlineKeyboardButton("سایت 🌐", url="https://example.com"),
)
bot.send_message(chat_id, "یک گزینه انتخاب کن:", reply_markup=menu)

# کیبورد معمولی — دکمه می‌تواند متن بفرستد یا شماره/لوکیشن بگیرد
kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb.add(KeyboardButton("📊 آمار"), KeyboardButton("🔔 اعلان‌ها"))
kb.row(KeyboardButton("📱 اشتراک شماره", request_contact=True))
bot.send_message(chat_id, "از منو انتخاب کن:", reply_markup=kb)

# حذف کیبورد یا اجبار به ریپلای
bot.send_message(chat_id, "کیبورد پاک شد.", reply_markup=ReplyKeyboardRemove())
bot.send_message(chat_id, "جواب بده:", reply_markup=ForceReply())
```

---

## 🧠 ماشین حالت (FSM)

برای فرم‌های چندمرحله‌ای (ثبت‌نام، سفارش و…):

```python
from balelite import Bot, StateGroup, JSONFileStorage

bot = Bot("TOKEN", storage=JSONFileStorage("states.json"))  # یا MemoryStorage (پیش‌فرض)

class Form(StateGroup):
    name = State()
    age = State()

@bot.message_handler(commands=["form"])
def start_form(message):
    bot.set_state(message.from_user.id, Form.name, message.chat.id)
    bot.reply_to(message, "اسمت چیه؟")

@bot.message_handler(state=Form.name)
def get_name(message):
    bot.update_state_data(message.from_user.id, message.chat.id, name=message.text)
    bot.set_state(message.from_user.id, Form.age, message.chat.id)
    bot.reply_to(message, "قشنگ! چند سالته؟")

@bot.message_handler(state=Form.age)
def get_age(message):
    data = bot.get_state_data(message.from_user.id, message.chat.id)
    bot.reset_state(message.from_user.id, message.chat.id)
    bot.reply_to(message, f"خوش اومدی {data['name']} عزیز! {message.text} ساله شدی 😄")
```

- `state="*"` یعنی در هر حالتی؛ `state=None` یعنی وقتی در هیچ حالتی نیست.
- سه ذخیره‌ساز: `MemoryStorage` (پیش‌فرض)، `JSONFileStorage("file.json")`، `RedisStorage` (با اکسترای `[redis]`).

---

## 🧱 میان‌افزار (Middleware)

تابعی که **قبل از همه هندلرها** اجرا می‌شود — برای لاگ، ضد اسپم، کنترل دسترسی:

```python
@bot.register_middleware(update_types=["message"])
def anti_flood(message, next_):
    if is_spammer(message.from_user.id):
        return  # پیام دور ریخته می‌شود — هندلر اجرا نمی‌شود
    next_()     # حتماً صدا بزن تا زنجیره ادامه پیدا کند
```

اگر `next_()` را صدا نزنی، بقیه زنجیره (از جمله هندلرها) اجرا نمی‌شوند — این ساده‌ترین راه بستن دسترسی است. میان‌افزار async هم دقیقاً همین شکل را دارد.

---

## 🚨 مدیریت خطاها

سلسله‌مراتب استثناها:

```
BaleError                    پایه همه خطاها
├── NetworkError                 درخواست اصلاً به بله نرسید
├── ApiHTTPError                 جواب غیر JSON (مثلاً صفحه 502)
└── ApiBaleError             بله گفت {"ok": false, ...}
    ├── InvalidTokenError        401/404 — توکن غلط یا باطل
    ├── BotBlockedError          403 — کاربر ربات را بلاک کرده
    └── RateLimitError           429 — همراه با retry_after
```

```python
from balelite import RateLimitError, BaleError

@bot.message_handler(func=lambda m: True)
def safe_echo(message):
    try:
        bot.send_message(message.chat.id, message.text)
    except RateLimitError as e:
        import time; time.sleep(e.retry_after)
        bot.send_message(message.chat.id, message.text)
    except BaleError as e:
        logging.exception("خطای API: %s", e)

# یا یک هندلر سراسری برای همه خطاهای هندلرها:
@bot.exception_handler
def on_error(payload, exception):
    logging.exception("کرش داخل هندلر: %s", exception)
```

---

## 📁 کار با فایل‌ها

چهار شکل ورودی برای همه متدهای رسانه‌ای (ارسال) پذیرفته است:

```python
bot.send_photo(chat_id, "FILE_ID")                          # 1) file_id
bot.send_photo(chat_id, "https://example.com/pic.jpg")      # 2) URL عمومی
bot.send_photo(chat_id, open("pic.jpg", "rb"))              # 3) فایل‌آبجکت
bot.send_photo(chat_id, "/home/me/pic.jpg", caption="سلام") # 4) مسیر فایل

# آلبوم (۲ تا ۱۰ عکس/ویدیو):
from balelite import InputMediaPhoto, InputMediaVideo
bot.send_media_group(chat_id, [InputMediaPhoto("P1"), InputMediaVideo("V1")])

# دانلود فایل:
file = bot.get_file(file_id)                       # متادیتا
url = bot.download_file_url(file)                  # لینک مستقیم tapi.bale.ai/file/...
data = bot.download_file(file)                     # بایت‌های فایل
```

---

## 💳 پرداخت در بله

ویژگی امضای بله نسبت به بقیه پیام‌رسان‌ها: **کیف پول داخلی**. کاربر بدون خروج از چت پرداخت می‌کند و جریان کامل در باله‌لایت پشتیبانی می‌شود:

```
sendInvoice (نمایش فاکتور) → pre_checkout_query (تأیید ظرف ۱۰ ثانیه!)
→ successful_payment (پول رسید) → askReview (درخواست امتیاز — مخصوص بله)
```

```python
from balelite import InlineKeyboardButton, InlineKeyboardMarkup

MENU = InlineKeyboardMarkup().row(
    InlineKeyboardButton("☕️ قهوه — ۲۵,۰۰۰ ریال", callback_data="buy:coffee"),
)

@bot.message_handler(commands=["shop"])
def shop(message):
    bot.send_message(message.chat.id, "فروشگاه:", reply_markup=MENU)

@bot.callback_query_handler(regexp=r"^buy:")
def on_buy(call):
    bot.send_invoice(
        call.message.chat.id,
        title="قهوه",
        description="یک فنجان قهوه تازه",
        payload="order:coffee:1",            # شناسه سفارش شما — موقع پرداخت برمی‌گردد
        provider_token="YOUR-PROVIDER-TOKEN",
        currency="IRR",
        prices=[("قهوه", 25_000)],           # تاپل (برچسب، مبلغ) هم قبول است
    )
    bot.answer_callback_query(call.id, text="فاکتور ارسال شد")

@bot.pre_checkout_query_handler()            # ⚠️ حتماً ظرف ۱۰ ثانیه جواب بدهید
def on_checkout(query):
    bot.answer_pre_checkout_query(query.id, ok=True)

@bot.message_handler(content_types=["successful_payment"])
def on_paid(message):
    p = message.successful_payment
    bot.reply_to(message, f"✅ پرداخت شد: {p.total_amount:,} {p.currency}\nسفارش: {p.invoice_payload}")
    bot.ask_review(message.chat.id)          # از کاربر امتیاز بخواهید 💯
```

نمونه کامل: [`examples/payments_bot.py`](examples/payments_bot.py)

- قیمت‌ها را `LabeledPrice`، تاپل `(برچسب, مبلغ)` یا دیکشنری بدهید — همه پذیرفته می‌شوند.
- لینک پرداخت خارج از چت هم می‌توانید بسازید: `bot.create_invoice_link(...)`.
- وضعیت تراکنش: `bot.inquire_transaction(order_id="...")`.

---

## ⚡ نسخه Async

همان API، فقط `await` دار:

```python
import asyncio
from balelite import AsyncBot

bot = AsyncBot("YOUR-BOT-TOKEN")

@bot.message_handler(commands=["start"])
async def start(message):
    await bot.send_message(message.chat.id, "سلام از نسخه async! ⚡️")

@bot.message_handler(func=lambda m: True)
async def echo(message):
    await bot.send_message(message.chat.id, message.text)

bot.polling()          # یا: asyncio.run(bot.infinity_polling())
```

نیاز به `pip install "balelite[async]"` دارد. نوع‌ها و فیلترها دقیقاً مشترک هستند — فقط هندلرها `async def` می‌شوند.

---

## 🪝 وبهوک (Webhook)

به‌جای polling، خود بله پیام‌ها را به سرور شما POST می‌کند:

```python
from flask import Flask, request

app = Flask(__name__)
bot = Bot("TOKEN")

@app.route("/webhook", methods=["POST"])
def webhook():
    token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if token != "my-secret":
        return "forbidden", 403
    bot.process_webhook_update(request.get_json(force=True))
    return "ok", 200

if __name__ == "__main__":
    bot.set_webhook("https://example.com/webhook", secret_token="my-secret")
    app.run(host="0.0.0.0", port=8443)   # فقط با ریورس‌پروکسی روی 443/88
```

⚠️ **بله فقط پورت‌های 443 و 88 را قبول می‌کند** — پس Flask را پشت nginx/caddy بگذارید. برای حذف وبهوک: `bot.delete_webhook()` و برای وضعیت: `bot.get_webhook_info()`.

---

## 📇 مرجع متدهای پرکاربرد

فقط متدهایی که در مستندات رسمی بله آمده‌اند (حروف CamalCase همان نام API است):

| دسته | متدها |
|---|---|
| پیام | `send_message`، `reply_to`، `send_long_message`، `edit_message_text`، `edit_message_caption`، `edit_message_reply_markup`، `delete_message`، `forward_message`، `copy_message`، `send_chat_action` |
| رسانه | `send_photo`، `send_video`، `send_audio`، `send_voice`، `send_document`، `send_animation`، `send_media_group` |
| مکان/مخاطب | `send_location`، `send_contact` |
| کیبورد/سنجاق | `pin_chat_message`، `unpin_chat_message`، `unpin_all_chat_messages` |
| تعامل | `answer_callback_query`، `set_webhook`، `delete_webhook`، `get_webhook_info` |
| چت و ادمین | `get_chat`، `get_chat_member`، `get_chat_member_count`، `get_chat_administrators`، `ban_chat_member`، `unban_chat_member`، `promote_chat_member`، `set_chat_title`، `set_chat_description`، `leave_chat` |
| لینک دعوت | `export_chat_invite_link`، `create_chat_invite_link`، `revoke_chat_invite_link` |
| فایل | `get_file`، `download_file`، `download_file_url` |
| استیکر | `upload_sticker_file`، `create_new_sticker_set`، `add_sticker_to_set` |
| 💳 پرداخت | `send_invoice`، `create_invoice_link`، `answer_pre_checkout_query`، `inquire_transaction` |
| ویژه بله | `ask_review` |
| FSM | `set_state`، `get_state`، `reset_state`، `get_state_data`، `update_state_data`، `clear_state_data` |

---

## 🛠 ابزارهای کمکی

```python
from balelite import create_deep_link, escape_html, escape_markdown, split_text

create_deep_link("mybot", "ref42")       # https://ble.ir/mybot?start=ref42
escape_html("<b>سلام</b>")               # &lt;b&gt;سلام&lt;/b&gt;
split_text("متن خیلی طولانی ...", 4096)  # تقسیم هوشمند در پاراگراف/خط/کلمه
```

`send_long_message(chat_id, text)` هم خودکار پیام‌های بلندتر از ۴۰۹۶ کاراکتر را می‌شکند و چند پیام می‌فرستد.

---

## 🔁 مهاجرت ربات تلگرامی به بله

اگر با pyTelegramBotAPI یا گرام‌لایت ربات تلگرامی نوشته‌اید، مهاجرت معمولاً فقط تغییر ایمپورت و توکن است:

```diff
- import telebot
- bot = telebot.TeleBot("TOKEN")
+ from balelite import Bot
+ bot = Bot("TOKEN-BOTFATHER-BALE")

- @bot.message_handler(commands=["start"])
+ @bot.message_handler(commands=["start"])
  def start(message): ...          # بدون تغییر!
```

چک‌لیست تفاوت‌ها:
- ❌ `answer_inline_query`، `send_poll`، `send_dice`، `send_sticker`، `send_venue`، `send_video_note`، `set_my_commands`، `restrict_chat_member`، `get_user_profile_photos` — در بله نیستند؛ حذفشان کنید.
- 🔗 لینک‌های `t.me` را با `create_deep_link` بسازید (خروجی `ble.ir`).
- 🪝 پورت وبهوک را به 443/88 تغییر دهید.
- 💳 اگر درگاه پرداخت داشتید، با `send_invoice` بله جایگزین کنید.

---

## 🧪 اجرای تست‌ها

```bash
pip install -e ".[dev]"
python -m pytest -q
# 143 passed, 1 skipped — کاملاً آفلاین، بدون توکن و اینترنت
```

تست آپشنال Redis فقط وقتی Redis نصب/در دسترس باشد اجرا می‌شود.

---

## 🗂 ساختار پروژه

```
balelite/
├── src/balelite/
│   ├── api_client.py     # ترنسپورت HTTP، retry، مدیریت 429
│   ├── bot.py            # Bot همگام: ۶۰+ متد، FSM، میان‌افزار، polling
│   ├── async_bot.py      # AsyncBot: همان سطح API روی aiohttp
│   ├── handlers.py       # روتر، فیلترها، دکوراتورها
│   ├── fsm.py            # StateGroup + سه ذخیره‌ساز
│   ├── middleware.py     # زنجیره sync/async
│   ├── polling.py        # حلقه‌های blocking و infinity
│   ├── types.py          # Update/Message/Invoice/کیبوردها...
│   ├── utils.py          # تقسیم متن، escape، دیپ‌لینک
│   └── exceptions.py     # سلسله‌مراتب BaleError
├── examples/             # echo، async، FSM، کیبورد، میان‌افزار، وبهوک، پرداخت
├── tests/                # ۱۴۳ تست آفلاین
└── .github/workflows/    # CI: پایتون ۳.۱۰ تا ۳.۱۳
```

---
