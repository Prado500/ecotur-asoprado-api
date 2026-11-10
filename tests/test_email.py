"""
Characterization tests for the real send_verification_email, with only SMTP doubled.

The router's autouse double replaces the name the router imported, not this function, so
these tests run the real body. They pin structure rather than bytes: the HTML may change
in whitespace, while its link, its button and its dispatch may not.
"""

import re
from collections.abc import Iterator
from html.parser import HTMLParser
from typing import Any
from unittest.mock import patch

import pytest
from fastapi_mail import MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import ValidationError

from app.core import email as email_module
from app.core.config import get_settings
from app.core.email import send_verification_email

RECIPIENT = "turista@test.com"
FIRST_NAME = "David"
TOKEN = "header.payload.signature"
BASE_URL = "https://ecotur.test"
VERIFICATION_LINK = f"{BASE_URL}/usuarios/verificar-email?token={TOKEN}"


class _BodyCollector(HTMLParser):
    """Collects each <a> tag's attributes and every text node with its tag, <style> included."""

    def __init__(self) -> None:
        super().__init__()
        self.anchors: list[dict[str, str | None]] = []
        self.texts: list[tuple[str, dict[str, str | None], str]] = []
        self._open: tuple[str, dict[str, str | None]] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Opens the tag, and keeps its attributes when it is an anchor."""
        attributes = dict(attrs)
        self._open = (tag, attributes)
        if tag == "a":
            self.anchors.append(attributes)

    def handle_endtag(self, tag: str) -> None:
        """Closes the open tag, so text after it belongs to no tag."""
        self._open = None

    def handle_data(self, data: str) -> None:
        """Records non-blank text with the open tag; comments and attributes never get here."""
        text = data.strip()
        if self._open is not None and text:
            tag, attrs = self._open
            self.texts.append((tag, attrs, text))


@pytest.fixture
def send_message() -> Iterator[Any]:
    """Doubles the SMTP client's send_message, keeping its real signature.

    Yields:
        The autospecced stand-in for FastMail.send_message.
    """
    with patch.object(email_module.fast_mail, "send_message", autospec=True) as mock:
        yield mock


async def _send_and_capture(send_message: Any, first_name: str = FIRST_NAME) -> MessageSchema:
    """Runs the real function and returns the message it handed to the SMTP client."""
    await send_verification_email(RECIPIENT, first_name, TOKEN, BASE_URL)
    call = send_message.await_args
    message: MessageSchema = call.args[0] if call.args else call.kwargs["message"]
    return message


def _body_of(message: MessageSchema) -> str:
    """Narrows the body to str, the only form this function builds."""
    assert isinstance(message.body, str)
    return message.body


async def test_dispatches_one_html_message_to_the_recipient(send_message: Any) -> None:
    """Happy path: one HTML message, addressed only to the given recipient."""
    message = await _send_and_capture(send_message)

    send_message.assert_awaited_once_with(message)
    assert [recipient.email for recipient in message.recipients] == [RECIPIENT]
    assert message.subject
    assert message.subtype is MessageType.html


async def test_body_carries_the_link_in_the_button_and_as_plain_text(send_message: Any) -> None:
    """The link is the button's href and, once, visible text in a styled <p>; button has text."""
    body = _body_of(await _send_and_capture(send_message))

    assert body.count(VERIFICATION_LINK) == 2

    parser = _BodyCollector()
    parser.feed(body)
    assert len(parser.anchors) == 1
    anchor = parser.anchors[0]
    assert anchor["href"] == VERIFICATION_LINK
    assert anchor["class"] == "btn"
    style = anchor["style"]
    assert style is not None
    assert " ".join(style.split()) == "color: #ffffff !important; text-decoration: none;"
    assert len([t for tag, _, t in parser.texts if tag == "a"]) == 1

    link_texts = [(tag, attrs) for tag, attrs, text in parser.texts if text == VERIFICATION_LINK]
    assert [tag for tag, _ in link_texts] == ["p"]
    p_style = link_texts[0][1].get("style")
    assert p_style is not None
    assert " ".join(p_style.split()) == "font-size: 12px; color: #006875; word-break: break-all;"


async def test_smtp_failure_propagates(send_message: Any) -> None:
    """Failure: an SMTP error reaches the caller untouched, after a single attempt."""
    error = ConnectionErrors("SMTP unreachable")
    send_message.side_effect = error

    with pytest.raises(ConnectionErrors) as exc_info:
        await send_verification_email(RECIPIENT, FIRST_NAME, TOKEN, BASE_URL)

    assert exc_info.value is error
    assert send_message.await_count == 1
    call = send_message.await_args
    message: MessageSchema = call.args[0] if call.args else call.kwargs["message"]
    assert [recipient.email for recipient in message.recipients] == [RECIPIENT]


async def test_invalid_recipient_is_rejected_before_sending(send_message: Any) -> None:
    """Failure: an address that is not an email never reaches the SMTP client."""
    with pytest.raises(ValidationError):
        await send_verification_email("not-an-email", FIRST_NAME, TOKEN, BASE_URL)

    send_message.assert_not_called()


async def test_body_renders_a_compound_first_name_verbatim(send_message: Any) -> None:
    """Edge: a compound name with accents reaches the body exactly as it came in."""
    compound_name = "María José"

    body = _body_of(await _send_and_capture(send_message, first_name=compound_name))

    assert compound_name in body


async def test_css_braces_are_rendered_unescaped(send_message: Any) -> None:
    """Edge: doubled braces come out single, 9 rules, none empty, and the .btn rule exists."""
    body = _body_of(await _send_and_capture(send_message))

    assert "{{" not in body
    assert "}}" not in body
    assert body.count("{") == 9
    assert body.count("}") == 9
    assert re.search(r"\{\s*\}", body) is None
    assert re.search(r"\.btn\s*\{", body) is not None


def test_smtp_client_is_configured_from_settings() -> None:
    """Edge case: the SMTP client takes its account, sender, port and server from Settings."""
    s = get_settings()
    config = email_module.fast_mail.config

    assert (
        config.MAIL_USERNAME,
        config.MAIL_PASSWORD.get_secret_value(),
        config.MAIL_FROM,
        config.MAIL_PORT,
        config.MAIL_SERVER,
    ) == (s.mail_username, s.mail_password, s.mail_sender, s.mail_port, s.mail_server)
