"""
Characterization tests for the real send_verification_email, with only SMTP doubled.

The router's autouse double replaces the name the router imported, not this function, so
these tests run the real body. They pin structure rather than bytes: the HTML may change
in whitespace, while its link, its button and its dispatch may not.
"""

from collections.abc import Iterator
from html.parser import HTMLParser
from typing import Any
from unittest.mock import patch

import pytest
from fastapi_mail import MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import ValidationError

from app.core import email as email_module
from app.core.email import send_verification_email

RECIPIENT = "turista@test.com"
FIRST_NAME = "David"
TOKEN = "header.payload.signature"
BASE_URL = "https://ecotur.test"
VERIFICATION_LINK = f"{BASE_URL}/usuarios/verificar-email?token={TOKEN}"


class _AnchorCollector(HTMLParser):
    """Collects the attributes of every <a> tag in the document it is fed."""

    def __init__(self) -> None:
        super().__init__()
        self.anchors: list[dict[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Keeps the attributes of the tag when it is an anchor."""
        if tag == "a":
            self.anchors.append(dict(attrs))


@pytest.fixture
def send_message() -> Iterator[Any]:
    """Doubles the SMTP client's send_message, keeping its real signature."""
    with patch.object(email_module.fast_mail, "send_message", autospec=True) as mock:
        yield mock


async def _send_and_capture(send_message: Any, first_name: str = FIRST_NAME) -> MessageSchema:
    """Runs the real function and returns the message it handed to the SMTP client."""
    await send_verification_email(RECIPIENT, first_name, TOKEN, BASE_URL)
    message: MessageSchema = send_message.await_args.args[0]
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
    assert isinstance(message.subject, str)
    assert message.subject
    assert message.subtype is MessageType.html


async def test_body_carries_the_link_in_the_button_and_as_plain_text(send_message: Any) -> None:
    """The link appears twice, and the button is the only anchor and keeps its attributes."""
    body = _body_of(await _send_and_capture(send_message))

    assert body.count(VERIFICATION_LINK) == 2

    parser = _AnchorCollector()
    parser.feed(body)
    assert len(parser.anchors) == 1
    anchor = parser.anchors[0]
    assert anchor["href"] == VERIFICATION_LINK
    assert anchor["class"] == "btn"
    style = anchor["style"]
    assert style is not None
    assert " ".join(style.split()) == "color: #ffffff !important; text-decoration: none;"


async def test_smtp_failure_propagates(send_message: Any) -> None:
    """Failure: an SMTP error reaches the caller untouched, after a single attempt."""
    error = ConnectionErrors("SMTP unreachable")
    send_message.side_effect = error

    with pytest.raises(ConnectionErrors) as exc_info:
        await send_verification_email(RECIPIENT, FIRST_NAME, TOKEN, BASE_URL)

    assert exc_info.value is error
    send_message.assert_awaited_once()


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
    """Edge: the f-string's doubled braces come out single, one pair per CSS rule (9 rules)."""
    body = _body_of(await _send_and_capture(send_message))

    assert "{{" not in body
    assert "}}" not in body
    assert body.count("{") == 9
    assert body.count("}") == 9
