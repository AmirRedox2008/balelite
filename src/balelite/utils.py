"""Utility helpers: escaping, text splitting and deep links."""

from __future__ import annotations

from typing import List

__all__ = [
    "create_deep_link",
    "escape_html",
    "escape_markdown",
    "split_text",
]

#: Hard limit for a single message's text/caption length (Bale follows the
#: same 4096-char convention as the Telegram Bot API it was modelled on).
MAX_MESSAGE_LENGTH = 4096


def escape_html(text: str) -> str:
    """Escape a string for safe use inside HTML parse-mode messages."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def escape_markdown(text: str, version: int = 1) -> str:
    """Escape a string for safe use inside Markdown messages.

    The Bale Bot API supports classic Markdown, so ``version=1`` (the legacy
    ``* _ ` [`` subset) is the default; ``version=2`` escapes the fuller
    MarkdownV2 set for servers that accept it.
    """
    text = str(text)
    if version == 2:
        for char in (
            "_", "*", "[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!",
        ):
            text = text.replace(char, f"\\{char}")
        return text
    for char in ("*", "_", "`", "["):
        text = text.replace(char, f"\\{char}")
    return text


def split_text(text: str, limit: int = MAX_MESSAGE_LENGTH) -> List[str]:
    """Split a long text into message-sized chunks (≤ ``limit`` chars).

    Splits at paragraph boundaries first (blank lines), then newlines, then
    hard-wraps at ``limit`` — so chunks stay as readable as possible. Empty
    input returns ``[]``; short input returns a single chunk.
    """
    text = str(text or "")
    if len(text) <= limit:
        return [text] if text else []

    chunks: List[str] = []
    remaining = text
    while remaining:
        if len(remaining) <= limit:
            chunks.append(remaining)
            break
        window = remaining[:limit + 1]
        cut = window.rfind("\n\n")
        if cut < limit // 2:
            cut = window.rfind("\n")
        if cut < limit // 2:
            cut = window.rfind(" ")
        if cut < limit // 2:
            cut = limit
        chunks.append(remaining[:cut].rstrip())
        remaining = remaining[cut:].lstrip("\n").lstrip()
    return [chunk for chunk in chunks if chunk]


def create_deep_link(username: str, payload: str, start: str = "start") -> str:
    """Build a Bale deep link: ``https://ble.ir/<bot>?start=<payload>``.

    ``payload`` may contain ``A-Z a-z 0-9 _ -`` (max 64 chars) and is
    delivered to the bot as the ``/start`` command argument.
    """
    payload = str(payload)
    if not payload or len(payload) > 64 or not all(
        ch.isalnum() or ch in "_-" for ch in payload
    ):
        raise ValueError("payload must be 1-64 chars of [A-Za-z0-9_-]")
    return f"https://ble.ir/{str(username).lstrip('@')}?{start}={payload}"
