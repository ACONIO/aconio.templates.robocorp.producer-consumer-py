"""Manage global module configuration."""

from __future__ import annotations
from dataclasses import dataclass

import requests


class Config:
    """Global configurations available in `aconio.fon`."""

    base_url: str = "https://finanzonline.bmf.gv.at"

    teilnehmer_id: str = None
    benutzer_id: str = None
    pin: str = None


@dataclass
class Authentication:
    cookies: requests.cookies.RequestsCookieJar
    request_key: str
