"""Configurable OpenClaw/ClawBot push adapter.

OpenClaw deployments differ, so this adapter intentionally keeps the HTTP
contract configurable. It is disabled unless OPENCLAW_PUSH_URL is set.
"""

from __future__ import annotations

import os
from typing import Any

import requests
from dotenv import load_dotenv

from sjtu_agent.paths import ENV_PATH

load_dotenv(ENV_PATH)
load_dotenv()


def _headers() -> dict[str, str]:
    token = os.getenv("OPENCLAW_PUSH_TOKEN", "").strip()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def push_text(text: str, *, title: str = "SJTU Agent", target: str = "") -> bool:
    url = os.getenv("OPENCLAW_PUSH_URL", "").strip()
    if not url:
        return False

    payload: dict[str, Any] = {
        "source": "sjtu-agent",
        "title": title,
        "text": text,
        "message": text,
        "content": text,
    }
    target = target or os.getenv("OPENCLAW_PUSH_TO", "").strip()
    if target:
        payload["to"] = target

    resp = requests.post(url, json=payload, headers=_headers(), timeout=15)
    resp.raise_for_status()
    return True


def push_reminder(title: str, subtitle: str, body: str) -> bool:
    lines = [f"🔔 {title}"]
    if subtitle:
        lines.append(subtitle)
    if body:
        lines.append(body)
    return push_text("\n".join(lines), title=title)
