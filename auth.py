"""Dead-simple auth for exactly two people: Heather and Chuck.

No sign-up, no database — two fixed accounts whose passwords come from env vars
(see config.py). Passwords are compared with a constant-time check. This is
intentionally minimal; it's a private app for two people, not a public service.
"""

import hmac

import config

# The two (and only two) accounts. Display name + which env password to use.
USERS = {
    "heather": {"display": "Heather", "partner": "chuck"},
    "chuck": {"display": "Chuck", "partner": "heather"},
}

# Defaults used only when the env passwords aren't set yet, so the app still
# runs out of the box. config.passwords_set() lets the UI warn about this.
_DEFAULTS = {"heather": "unicorns", "chuck": "puppies"}


def _expected_password(username: str) -> str:
    if username == "heather":
        return config.HEATHER_PASSWORD or _DEFAULTS["heather"]
    if username == "chuck":
        return config.CHUCK_PASSWORD or _DEFAULTS["chuck"]
    return ""


def check_login(username: str, password: str) -> bool:
    """Return True if the username/password combo is valid."""
    username = (username or "").strip().lower()
    if username not in USERS:
        return False
    expected = _expected_password(username)
    # Constant-time compare to avoid timing leaks.
    return hmac.compare_digest(str(password), str(expected))


def display_name(username: str) -> str:
    return USERS.get(username, {}).get("display", username.title())


def partner_of(username: str) -> str:
    return USERS.get(username, {}).get("partner", "")


def using_default_passwords() -> bool:
    """True if either account is still on its built-in default password."""
    return not config.passwords_set()
