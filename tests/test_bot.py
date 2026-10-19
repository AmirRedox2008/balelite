"""Tests for the Bot facade: method/params mapping and response parsing."""

from __future__ import annotations

import io
import json

from balelite.bot import Bot
from balelite.types import (
    File, InlineKeyboardButton, InlineKeyboardMarkup, Message, User,
)

from conftest import CALLBACK_UPDATE_JSON, COMMAND_MESSAGE_JSON, TOKEN, RecordingClient, UPDATE_JSON


def test_send_message_maps_params_and_parses(bot, recording_client):
    bot.client.result = COMMAND_MESSAGE_JSON
    message = bot.send_message(42, "hello", parse_mode="HTML")
    assert isinstance(message, Message)
    assert message.message_id == 7
    call = recording_client.calls[0]
    assert call["method"] == "sendMessage"
    assert call["params"]["chat_id"] == 42
    assert call["params"]["text"] == "hello"
    assert call["params"]["parse_mode"] == "HTML"


def test_reply_to_uses_chat_id_and_reply_id(bot, recording_client):
    message = Message.de_json(COMMAND_MESSAGE_JSON)
    bot.reply_to(message, "hi")
    params = recording_client.calls[0]["params"]
    assert params["chat_id"] == message.chat.id
    assert params["reply_to_message_id"] == message.message_id


def test_get_me_returns_user(bot):
    bot.client.result = {"id": 1, "is_bot": True, "first_name": "BaleLite Bot"}
    me = bot.get_me()
    assert isinstance(me, User)
    assert me.is_bot is True


def test_get_updates_returns_updates(bot, recording_client):
    bot.client.result = [UPDATE_JSON]
    updates = bot.get_updates(offset=None, timeout=5, allowed_updates=["message"])
    assert updates[0].update_id == 100
    params = recording_client.calls[0]["params"]
    assert params["timeout"] == 5
    assert json.loads(params["allowed_updates"]) == ["message"]


def test_edit_message_text_returns_message(bot):
    bot.client.result = COMMAND_MESSAGE_JSON
    assert isinstance(bot.edit_message_text("new", chat_id=1, message_id=7), Message)


def test_edit_message_text_inline_returns_bool(bot):
    bot.client.result = True
    assert bot.edit_message_text("new", inline_message_id="abc") is True


def test_delete_and_forward_return_types(bot, recording_client):
    bot.client.result = True
    assert bot.delete_message(1, 7) is True
    bot.client.result = {"message_id": 99}
    forwarded = bot.forward_message(2, 1, 7)
    assert forwarded.message_id == 99
    assert recording_client.calls[-1]["method"] == "forwardMessage"


def test_send_media_with_string_file_id(bot, recording_client):
    bot.client.result = COMMAND_MESSAGE_JSON
    message = bot.send_photo(42, "FID-123")
    assert isinstance(message, Message)
    assert recording_client.calls[0]["files"] is None
    assert recording_client.calls[0]["params"]["photo"] == "FID-123"


def test_send_media_with_file_like(bot, recording_client):
    bot.client.result = COMMAND_MESSAGE_JSON
    payload = io.BytesIO(b"fake-png-bytes")
    bot.send_photo(42, payload, caption="a photo")
    files = recording_client.calls[0]["files"]
    assert files is not None
    name, content = files["photo"]
    assert name == "upload"
    assert content == b"fake-png-bytes"
    assert "photo" not in recording_client.calls[0]["params"]


def test_send_media_with_path(bot, recording_client, tmp_path):
    bot.client.result = COMMAND_MESSAGE_JSON
    photo = tmp_path / "pic.png"
    photo.write_bytes(b"png")
    bot.send_photo(42, photo)
    name, content = recording_client.calls[0]["files"]["photo"]
    assert name == "pic.png"
    assert content == b"png"


def test_send_media_all_kinds_map_to_methods(bot, recording_client):
    bot.client.result = COMMAND_MESSAGE_JSON
    bot.send_document(1, "d")
    bot.send_video(1, "v")
    bot.send_audio(1, "a")
    bot.send_voice(1, "vo")
    methods = [call["method"] for call in recording_client.calls]
    assert methods == ["sendDocument", "sendVideo", "sendAudio", "sendVoice"]


def test_reply_markup_is_passed_for_serialisation(bot, recording_client):
    bot.client.result = COMMAND_MESSAGE_JSON
    markup = InlineKeyboardMarkup().row(InlineKeyboardButton("hi", callback_data="hi"))
    bot.send_message(1, "choose", reply_markup=markup)
    assert recording_client.calls[0]["params"]["reply_markup"] is markup


def test_answer_callback_query(bot, recording_client):
    bot.client.result = True
    assert bot.answer_callback_query("cbq-1", text="Done!") is True
    params = recording_client.calls[0]["params"]
    assert params["callback_query_id"] == "cbq-1"


def test_get_file_and_download_url(bot, recording_client):
    bot.client.result = {"file_id": "x", "file_unique_id": "y", "file_path": "docs/a.txt"}
    file = bot.get_file("x")
    assert isinstance(file, File)
    assert bot.download_file_url(file).endswith(f"/file/bot{TOKEN}/docs/a.txt")


def test_token_property(bot):
    assert bot.token == TOKEN


def test_decorators_register_and_route(recording_client):
    bot = Bot(token=TOKEN, client=recording_client)
    received = []

    @bot.message_handler(commands=["start"])
    def start_handler(message):
        received.append(message)

    @bot.callback_query_handler(func=lambda c: True)
    def callback_handler(call):
        received.append(call)

    bot.process_new_updates([UPDATE_JSON, CALLBACK_UPDATE_JSON])
    assert len(received) == 2
    assert received[0].text == "/start@mybot hello"
    assert received[1].data == "buy:3"


# ---------------------------------------------------------------------------
# v2 — new API methods
# ---------------------------------------------------------------------------
def test_send_invoice_maps_params(bot, recording_client):
    bot.client.result = COMMAND_MESSAGE_JSON
    bot.send_invoice(
        42, "Coffee", "A nice cup", "order-1", "PROVIDER-TOKEN",
        prices=[("Coffee", 25000)], need_phone_number=True,
    )
    call = recording_client.calls[0]
    assert call["method"] == "sendInvoice"
    assert call["params"]["prices"] == [{"label": "Coffee", "amount": 25000}]
    assert call["params"]["currency"] == "IRR"
    assert call["params"]["need_phone_number"] is True


def test_send_invoice_forwards_extra_kwargs(bot, recording_client):
    bot.client.result = COMMAND_MESSAGE_JSON
    bot.send_invoice(1, "T", "D", "p", "tok", prices=[], max_tip_amount=500)
    assert recording_client.calls[0]["params"]["max_tip_amount"] == 500


def test_create_invoice_link_and_inquire_transaction(bot, recording_client):
    bot.client.result = "https://ble.ir/pay/abc"
    assert bot.create_invoice_link("T", "D", "p", "tok", prices=[("x", 1)]) == "https://ble.ir/pay/abc"
    assert recording_client.calls[0]["method"] == "createInvoiceLink"
    bot.client.result = {"status": "paid", "amount": 25000}
    txn = bot.inquire_transaction(order_id="order-1")
    assert recording_client.calls[1]["method"] == "inquireTransaction"
    assert txn.status == "paid"


def test_ask_review_maps_method(bot, recording_client):
    bot.client.result = True
    assert bot.ask_review(42) is True
    assert recording_client.calls[0]["method"] == "askReview"
    assert recording_client.calls[0]["params"]["chat_id"] == 42


def test_send_animation_field_names(bot, recording_client):
    bot.client.result = COMMAND_MESSAGE_JSON
    bot.send_animation(1, "GIF-1")
    calls = recording_client.calls
    assert calls[0]["method"] == "sendAnimation" and calls[0]["params"]["animation"] == "GIF-1"


def test_send_media_group_serialises_media(bot, recording_client):
    from balelite.types import InputMediaPhoto, InputMediaVideo
    bot.client.result = [COMMAND_MESSAGE_JSON, COMMAND_MESSAGE_JSON]
    messages = bot.send_media_group(1, [InputMediaPhoto("P1"), InputMediaVideo("V1")])
    assert len(messages) == 2
    call = recording_client.calls[0]
    assert call["method"] == "sendMediaGroup"
    assert call["params"]["media"][0] == {"type": "photo", "media": "P1"}


def test_edit_message_caption_and_markup(bot, recording_client):
    bot.client.result = True
    assert bot.edit_message_caption(chat_id=1, message_id=7, caption="new") is True
    assert recording_client.calls[0]["method"] == "editMessageCaption"
    assert bot.edit_message_reply_markup(chat_id=1, message_id=7) is True


def test_pin_unpin_and_unpin_all(bot, recording_client):
    bot.client.result = True
    bot.pin_chat_message(1, 7)
    bot.unpin_chat_message(1, 7)
    bot.unpin_all_chat_messages(1)
    assert [c["method"] for c in recording_client.calls] == [
        "pinChatMessage", "unpinChatMessage", "unpinAllChatMessages",
    ]


def test_chat_admin_surface(bot, recording_client):
    bot.client.result = 17
    assert bot.get_chat_member_count(-100) == 17
    bot.client.result = {"status": "member", "user": {"id": 1, "is_bot": False, "first_name": "A"}}
    assert bot.get_chat_member(-100, 1).status == "member"
    bot.client.result = True
    bot.set_chat_title(-100, "New")
    bot.promote_chat_member(-100, 5, can_delete_messages=True)
    bot.ban_chat_member(-100, 5, revoke_messages=True)
    bot.unban_chat_member(-100, 5)
    methods = [c["method"] for c in recording_client.calls]
    assert methods == [
        "getChatMembersCount", "getChatMember", "setChatTitle",
        "promoteChatMember", "banChatMember", "unbanChatMember",
    ]


def test_invite_links(bot, recording_client):
    bot.client.result = "https://ble.ir/+abc"
    assert bot.export_chat_invite_link(-100).endswith("+abc")
    bot.client.result = {"invite_link": "https://ble.ir/+x", "creator": {"id": 1, "is_bot": False, "first_name": "A"}}
    link = bot.create_chat_invite_link(-100, name="promo", member_limit=10)
    assert type(link).__name__ == "ChatInviteLink"
    bot.client.result = {"invite_link": "https://ble.ir/+x", "creator": {"id": 1, "is_bot": False, "first_name": "A"}}
    assert bot.revoke_chat_invite_link(-100, "https://ble.ir/+x").invite_link.endswith("+x")


def test_pre_checkout_answer(bot, recording_client):
    bot.client.result = True
    bot.answer_pre_checkout_query("pc1", ok=True)
    assert recording_client.calls[0]["method"] == "answerPreCheckoutQuery"
    bot.client.result = True
    bot.answer_pre_checkout_query("pc2", ok=False, error_message="out of stock")
    params = recording_client.calls[1]["params"]
    assert params["ok"] is False and params["error_message"] == "out of stock"


def test_bale_specific_handler_decorators_route(bot):
    received = []

    @bot.edited_message_handler()
    def edited(message):
        received.append(("edited", message.message_id))

    @bot.channel_post_handler()
    def post(message):
        received.append(("post", message.message_id))

    @bot.pre_checkout_query_handler()
    def checkout(query):
        received.append(("checkout", query.invoice_payload))

    bot.process_new_updates([
        {"update_id": 1, "edited_message": {**COMMAND_MESSAGE_JSON, "message_id": 11}},
        {"update_id": 2, "channel_post": {**COMMAND_MESSAGE_JSON, "message_id": 12,
                                          "chat": {"id": -100, "type": "channel", "title": "Ch"}}},
        {"update_id": 3, "pre_checkout_query": {
            "id": "pcq", "from": {"id": 1, "is_bot": False, "first_name": "A"},
            "currency": "IRR", "total_amount": 1000, "invoice_payload": "order-9",
        }},
    ])
    assert received == [("edited", 11), ("post", 12), ("checkout", "order-9")]


def test_send_long_message_splits(bot, recording_client):
    bot.client.result = COMMAND_MESSAGE_JSON
    long_text = "hello\n\n" * 2000  # > 4096 chars
    messages = bot.send_long_message(1, long_text)
    assert len(messages) > 1
    assert all(c["method"] == "sendMessage" for c in recording_client.calls)
    assert all(len(c["params"]["text"]) <= 4096 for c in recording_client.calls)


def test_download_file_returns_bytes(recording_client, monkeypatch):
    bot = Bot(token=TOKEN, client=recording_client)
    bot.client.result = {"file_id": "x", "file_unique_id": "y", "file_path": "docs/a.txt"}
    file = bot.get_file("x")
    monkeypatch.setattr(bot.client, "get_bytes", lambda url, timeout=None: b"RAW", raising=False)
    assert bot.download_file(file) == b"RAW"


def test_threaded_dispatch_processes_updates(recording_client):
    bot = Bot(token=TOKEN, client=recording_client, threaded=True, num_workers=2)
    received = []

    @bot.message_handler(func=lambda m: True)
    def handler(message):
        received.append(message)

    bot.process_new_updates([UPDATE_JSON])
    bot._executor.shutdown(wait=True)  # wait for the worker to finish
    assert len(received) == 1


def test_stop_polling_sets_event(recording_client):
    bot = Bot(token=TOKEN, client=recording_client)
    assert not bot._stop_event.is_set()
    bot.stop_polling()
    assert bot._stop_event.is_set()


def test_parse_mode_default_is_applied(bot, recording_client):
    bot2 = Bot(token=TOKEN, client=recording_client, parse_mode="HTML")
    bot2.client.result = COMMAND_MESSAGE_JSON
    bot2.send_message(1, "<b>hi</b>")
    assert recording_client.calls[0]["params"]["parse_mode"] == "HTML"
    explicit = Bot(token=TOKEN, client=recording_client, parse_mode="HTML")
    explicit.client.result = COMMAND_MESSAGE_JSON
    explicit.send_message(1, "text", parse_mode="Markdown")
    assert recording_client.calls[-1]["params"]["parse_mode"] == "Markdown"


def test_bot_context_manager_closes(recording_client):
    with Bot(token=TOKEN, client=recording_client) as bot:
        assert bot.token == TOKEN
    assert bot._stop_event.is_set()
