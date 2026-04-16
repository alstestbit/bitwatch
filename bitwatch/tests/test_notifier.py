import json
import pytest
from unittest.mock import patch, MagicMock
from bitwatch.notifier import build_payload, send_webhook, Notifier
from bitwatch.config import WebhookConfig


def make_webhook(**kwargs) -> WebhookConfig:
    defaults = {"url": "http://example.com/hook", "events": None, "headers": {}}
    defaults.update(kwargs)
    return WebhookConfig(**defaults)


def test_build_payload():
    payload = build_payload("/some/file.txt", "modified", "my-target")
    assert payload["path"] == "/some/file.txt"
    assert payload["event"] == "modified"
    assert payload["target"] == "my-target"
    assert "timestamp" in payload


def test_send_webhook_success():
    webhook = make_webhook()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = send_webhook(webhook, {"event": "created"})
    assert result is True


def test_send_webhook_failure():
    import urllib.error
    webhook = make_webhook()
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("timeout")):
        result = send_webhook(webhook, {"event": "created"})
    assert result is False


def test_notifier_filters_events():
    webhook = make_webhook(events=["created"])
    notifier = Notifier(webhook=webhook, target_name="t")
    with patch("bitwatch.notifier.send_webhook") as mock_send:
        notifier.notify("/f", "modified")
        mock_send.assert_not_called()
        notifier.notify("/f", "created")
        mock_send.assert_called_once()


def test_notifier_no_filter_sends_all():
    webhook = make_webhook(events=None)
    notifier = Notifier(webhook=webhook, target_name="t")
    with patch("bitwatch.notifier.send_webhook", return_value=True) as mock_send:
        notifier.notify("/f", "deleted")
        mock_send.assert_called_once()
