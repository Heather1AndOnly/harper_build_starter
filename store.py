"""Tiny JSON-file persistence for Harper.

Everything lives in data/store.json (gitignored). The shape:

{
  "users": {
    "heather": {
      "private": { "<mode>": [ {role, content}, ... ] },
      "cooldown_until": 1718200000.0 | null,
      "last_mood": "stormy" | null
    },
    "chuck": { ... }
  },
  "shared": { "both": [ {role, content, speaker}, ... ] },
  "signals": [ {from, to, type, created_at} ]
}

Privacy rule: each user's "private" data is only ever read for that logged-in
user. The "shared" room is the only mutual space. Signals carry NO message
content — just the fact that someone is ready to talk.
"""

import json
import os
import time

_DATA_DIR = "data"
_PATH = os.path.join(_DATA_DIR, "store.json")


def _empty_user():
    return {"private": {}, "cooldown_until": None, "last_mood": None}


def _empty_store():
    return {
        "users": {"heather": _empty_user(), "chuck": _empty_user()},
        "shared": {"both": []},
        "signals": [],
    }


def load() -> dict:
    if not os.path.exists(_PATH):
        return _empty_store()
    try:
        with open(_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return _empty_store()
    # Heal any missing top-level keys so callers never KeyError.
    base = _empty_store()
    for k in base:
        data.setdefault(k, base[k])
    for u in ("heather", "chuck"):
        data["users"].setdefault(u, _empty_user())
        for fk, fv in _empty_user().items():
            data["users"][u].setdefault(fk, fv)
    data["shared"].setdefault("both", [])
    return data


def save(data: dict) -> None:
    os.makedirs(_DATA_DIR, exist_ok=True)
    tmp = _PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, _PATH)  # atomic-ish write


# --- history ------------------------------------------------------------
def get_history(data: dict, username: str, mode: str) -> list:
    """Return the stored message history for a user+mode (or shared room)."""
    if mode == "both":
        return data["shared"]["both"]
    return data["users"][username]["private"].setdefault(mode, [])


def append_message(data: dict, username: str, mode: str, role: str,
                   content: str, speaker: str | None = None) -> None:
    msg = {"role": role, "content": content}
    if speaker:
        msg["speaker"] = speaker
    get_history(data, username, mode).append(msg)


def clear_history(data: dict, username: str, mode: str) -> None:
    if mode == "both":
        data["shared"]["both"] = []
    else:
        data["users"][username]["private"][mode] = []


# --- cool-down ----------------------------------------------------------
def set_cooldown(data: dict, username: str, minutes: int) -> float:
    until = time.time() + minutes * 60
    data["users"][username]["cooldown_until"] = until
    return until


def get_cooldown(data: dict, username: str) -> float | None:
    return data["users"][username].get("cooldown_until")


def cooldown_remaining(data: dict, username: str) -> int:
    """Seconds left on the cool-down, or 0 if none/expired."""
    until = get_cooldown(data, username)
    if not until:
        return 0
    return max(0, int(until - time.time()))


def clear_cooldown(data: dict, username: str) -> None:
    data["users"][username]["cooldown_until"] = None


def set_mood(data: dict, username: str, mood: str) -> None:
    data["users"][username]["last_mood"] = mood


# --- partner signals (no content, just a nudge) -------------------------
def add_signal(data: dict, from_user: str, to_user: str, kind: str) -> None:
    # Avoid stacking duplicate pending signals of the same kind.
    for s in data["signals"]:
        if s["from"] == from_user and s["to"] == to_user and s["type"] == kind:
            return
    data["signals"].append(
        {"from": from_user, "to": to_user, "type": kind, "created_at": time.time()}
    )


def pop_signals_for(data: dict, username: str) -> list:
    """Return and remove all pending signals addressed to this user."""
    mine = [s for s in data["signals"] if s["to"] == username]
    data["signals"] = [s for s in data["signals"] if s["to"] != username]
    return mine


def peek_signals_for(data: dict, username: str) -> list:
    """Look at pending signals without removing them."""
    return [s for s in data["signals"] if s["to"] == username]
