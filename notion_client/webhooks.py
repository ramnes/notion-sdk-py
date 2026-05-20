"""Helpers for receiving and verifying Notion webhook deliveries.

Notion signs each webhook request with HMAC-SHA256 over the raw HTTP body
using the subscription's verification token as the key, and sends the
resulting hex digest in the `X-Notion-Signature` header as `sha256=<hex>`.
To verify a delivery, callers must pass the body **exactly as it arrived
over the wire** — any JSON re-serialization will change the bytes and
invalidate the signature.
"""

import hmac
from hashlib import sha256
from typing import Optional, Union

_SIGNATURE_PREFIX = "sha256="


def sign_webhook_payload(body: Union[str, bytes], verification_token: str) -> str:
    """Compute the value Notion would send in `X-Notion-Signature` for a given
    body and verification token. Useful for unit-testing webhook handlers without
    standing up a real subscription.
    """
    if isinstance(body, str):
        body = body.encode("utf-8")
    digest = hmac.new(verification_token.encode("utf-8"), body, sha256).hexdigest()
    return f"{_SIGNATURE_PREFIX}{digest}"


def verify_webhook_signature(
    body: Union[str, bytes],
    signature: Optional[str],
    verification_token: str,
) -> bool:
    """Verify that a webhook delivery came from Notion and has not been tampered
    with.

    Performs a constant-time comparison; returns ``True`` only if the supplied
    ``signature`` matches HMAC-SHA256 of ``body`` keyed by ``verification_token``.
    Returns ``False`` (rather than raising) for any malformed input so the
    caller can respond with a single 401/403 path.
    """
    if not isinstance(signature, str) or not signature.startswith(_SIGNATURE_PREFIX):
        return False
    expected = sign_webhook_payload(body, verification_token)
    return hmac.compare_digest(signature, expected)
