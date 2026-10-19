"""Bale payments — sendInvoice + pre-checkout + successful payment.

Bale has a built-in payment gateway (wallet), so a bot can sell goods
without any third-party PSP. The flow:

    1. user taps the "Pay" button        -> sendInvoice(...) shows the invoice
    2. Bale sends a pre_checkout_query   -> answer within 10 seconds!
    3. user confirms the payment         -> message.successful_payment arrives
    4. (optional) askReview              -> ask the user to rate the bot

Run:  python examples/payments_bot.py
"""

import logging

from balelite import Bot, InlineKeyboardButton, InlineKeyboardMarkup

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

bot = Bot("YOUR-BOT-TOKEN")

# In Bale you receive the payment token from @BotFather (My Bots -> Payments)
# or the merchant panel; paste it here:
PROVIDER_TOKEN = "YOUR-PROVIDER-TOKEN"

MENU = InlineKeyboardMarkup().row(
    InlineKeyboardButton("☕️ Coffee — 25,000 IRR", callback_data="buy:coffee"),
    InlineKeyboardButton("🍰 Cake — 90,000 IRR", callback_data="buy:cake"),
)

ITEMS = {
    "coffee": {"title": "Coffee", "amount": 25_000},
    "cake": {"title": "Cake", "amount": 90_000},
}


@bot.message_handler(commands=["start", "menu"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🛒 <b>Welcome to the demo shop!</b>\nPick an item to pay inside Bale:",
        reply_markup=MENU,
    )


@bot.callback_query_handler(regexp=r"^buy:")
def on_buy(call):
    item = ITEMS[call.data.split(":")[1]]
    # 1) show the invoice — prices accept (label, amount) tuples
    bot.send_invoice(
        call.message.chat.id,
        title=item["title"],
        description="Demo order — delivered by a smile",
        payload=f"order:{call.data}",          # echoed back on success
        provider_token=PROVIDER_TOKEN,
        currency="IRR",
        prices=[(item["title"], item["amount"])],
    )
    bot.answer_callback_query(call.id, text="Invoice sent — pay in chat")


# 2) MUST be answered within 10 seconds, or the payment is cancelled
@bot.pre_checkout_query_handler()
def on_pre_checkout(query):
    ok = query.total_amount > 0  # your own validation goes here
    bot.answer_pre_checkout_query(
        query.id, ok=ok,
        error_message=None if ok else "Order is no longer available.",
    )


# 3) money arrived — deliver the goods
@bot.message_handler(content_types=["successful_payment"])
def on_paid(message):
    payment = message.successful_payment
    bot.send_message(
        message.chat.id,
        f"✅ Payment received: <b>{payment.total_amount:,} {payment.currency}</b>\n"
        f"payload: <code>{payment.invoice_payload}</code>\nThank you! 🎉",
    )
    # 4) Bale-specific: kindly ask for a rating
    bot.ask_review(message.chat.id)


if __name__ == "__main__":
    bot.infinity_polling()
