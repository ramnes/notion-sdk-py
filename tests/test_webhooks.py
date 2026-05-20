from notion_client.webhooks import sign_webhook_payload, verify_webhook_signature


def test_sign_webhook_payload():
    body = '{"verification_token":"abc"}'
    token = "secret"
    signature = sign_webhook_payload(body, token)
    assert signature.startswith("sha256=")
    assert len(signature) == len("sha256=") + 64

    assert sign_webhook_payload(body.encode("utf-8"), token) == signature


def test_verify_webhook_signature():
    body = '{"verification_token":"abc"}'
    token = "secret"
    signature = sign_webhook_payload(body, token)

    assert verify_webhook_signature(body, signature, token)
    assert verify_webhook_signature(body.encode("utf-8"), signature, token)

    assert not verify_webhook_signature(body, signature, "wrong-token")
    assert not verify_webhook_signature("tampered" + body, signature, token)
    assert not verify_webhook_signature(body, None, token)
    assert not verify_webhook_signature(body, "missing-prefix", token)
    assert not verify_webhook_signature(body, "sha256=not-hex", token)
