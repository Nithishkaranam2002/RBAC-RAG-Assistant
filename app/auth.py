# app/auth.py
"""
Lightweight auth: map username → role using users.json.
Production systems would replace this with SSO or JWT.
"""

import json
from pathlib import Path

# Path: repo_root / users.json
USERS_FILE = Path(__file__).resolve().parent.parent / "users.json"

with USERS_FILE.open(encoding="utf-8") as f:
    _USER_ROLE_MAP = json.load(f)

def get_user_role(username: str) -> str | None:
    """
    Return the role for a given username (case-insensitive).
    If user isn't registered, return None.
    """
    return _USER_ROLE_MAP.get(username.lower())
