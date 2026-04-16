import json
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Optional
from bitwatch.config import WebhookConfig


def build_payload(path: str, event: str, target_name: str) -> dict:
    return {
        "target": target_name,
        "event": event,
        "path": path,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def send_webhook(webhook: WebhookConfig, payload: dict) -> bool:
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    headers.update(webhook.headers or {})
    req = urllib.request.Request(
        webhook.url, data=data, headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
    except urllib.error.URLError as e:
        print(f"[bitwatch] Webhook error: {e}")
        return False


class Notifier:
    def __init__(self, webhook: WebhookConfig, target_name: str):
        self.webhook = webhook
        self.target_name = target_name

    def notify(self, path: str, event: str) -> bool:
        if self.webhook.events and event not in self.webhook.events:
            return False
        payload = build_payload(path, event, self.target_name)
        return send_webhook(self.webhook, payload)
