"""Echo bot — the "Hello, world" of Bale bots, BaleLite edition.

Run:  python examples/echo_bot.py
"""

import logging

from balelite import Bot

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

bot = Bot("YOUR-BOT-TOKEN")  # get a token from @BotFather inside the Bale app


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(message, "Howdy! I am an echo bot built with BaleLite. Send me anything.")


@bot.message_handler(func=lambda message: True, content_types=["all"])
def echo_all(message):
    bot.reply_to(message, message.text or f"(got a {message.content_type})")


if __name__ == "__main__":
    bot.infinity_polling()
