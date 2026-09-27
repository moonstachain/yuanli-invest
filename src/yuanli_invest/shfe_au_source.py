"""Bounded read-only retrieval of official SHFE daily futures reports."""

from __future__ import annotations

from datetime import datetime
import ssl
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, HTTPSHandler, ProxyHandler, Request, build_opener


SHFE_ROOT = "https://www.shfe.com.cn/data/tradedata/future/dailydata"


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, newurl):
        raise ValueError("SHFE redirect blocked")


def fetch_shfe(day: str, *, opener=None) -> bytes:
    datetime.strptime(day, "%Y-%m-%d")
    url = f"{SHFE_ROOT}/kx{day.replace('-', '')}.dat"
    opener = opener or build_opener(
        ProxyHandler({}), HTTPSHandler(context=ssl.create_default_context()), _NoRedirect()
    )
    with opener.open(Request(url, headers={"Accept": "application/json"}), timeout=25) as response:
        if response.status != 200 or urlsplit(response.url).hostname != "www.shfe.com.cn":
            raise ValueError("unexpected SHFE response")
        raw = response.read(1_000_001)
        if len(raw) > 1_000_000:
            raise ValueError("oversized SHFE response")
    return raw
