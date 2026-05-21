# Implements: F-033 (HTTP tool)
"""
HTTP request tool for calling external APIs.
Security: blocks internal IP ranges (SSRF protection).
"""
from __future__ import annotations

import ipaddress
import logging
import re
import socket
from typing import Any
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)

# Blocked internal IP ranges (SSRF protection)
BLOCKED_RANGES = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),  # link-local
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
]
ALLOWED_SCHEMES = {"http", "https"}
ALLOWED_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH"}


def _validate_url(url: str) -> None:
    """Block SSRF attempts by validating URL against blocked IP ranges."""
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError(f"URL scheme '{parsed.scheme}' is not allowed")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("URL has no hostname")

    # Resolve hostname to IP
    try:
        ip_str = socket.gethostbyname(hostname)
        ip = ipaddress.ip_address(ip_str)
        for blocked in BLOCKED_RANGES:
            if ip in blocked:
                raise ValueError(f"Requests to internal addresses are not allowed: {ip_str}")
    except socket.gaierror:
        raise ValueError(f"Could not resolve hostname: {hostname}")


async def run_http_request(input_data: dict[str, Any], org_id: str | None) -> dict:
    """
    Make an HTTP request to an external URL.
    
    Input: {
        "url": str,
        "method": str (default "GET"),
        "headers": dict (optional),
        "body": dict|str (optional),
        "timeout_seconds": int (default 30)
    }
    Output: {"status_code": int, "headers": dict, "body": str, "url": str}
    """
    url = input_data.get("url", "").strip()
    method = input_data.get("method", "GET").upper()
    headers = input_data.get("headers", {})
    body = input_data.get("body")
    timeout = min(int(input_data.get("timeout_seconds", 30)), 60)

    if not url:
        raise ValueError("url is required for http_request")
    if method not in ALLOWED_METHODS:
        raise ValueError(f"Method '{method}' is not allowed. Use: {ALLOWED_METHODS}")

    # SSRF protection
    _validate_url(url)

    # Remove dangerous headers
    safe_headers = {
        k: v for k, v in (headers or {}).items()
        if k.lower() not in {"authorization", "x-api-key", "cookie"}
    }
    safe_headers.setdefault("User-Agent", "NexusFlow-AI/1.0")

    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        if body and method in {"POST", "PUT", "PATCH"}:
            if isinstance(body, dict):
                response = await client.request(method, url, json=body, headers=safe_headers)
            else:
                response = await client.request(method, url, content=str(body), headers=safe_headers)
        else:
            response = await client.request(method, url, headers=safe_headers)

    # Truncate large responses
    body_text = response.text[:32768]

    logger.info("[HTTP] %s %s → %d", method, url, response.status_code)
    return {
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "body": body_text,
        "url": str(response.url),
    }
