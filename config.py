"""Central configuration for Harper.

All secrets and tunables come from environment variables so the app stays safe
to commit and still runs (in offline mode) when no keys are present.

Copy .env.example to .env and fill in your keys, or export them in your shell.
"""

import os

# Optionally load a local .env file if python-dotenv is installed.
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    # python-dotenv is optional; env vars set in the shell still work.
    pass


# --- OpenRouter (the conversation brain) ---------------------------------
# Get a key at https://openrouter.ai/keys
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_BASE_URL = os.getenv(
    "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
).strip()
# Any model slug from https://openrouter.ai/models
OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL", "openai/gpt-4o-mini"
).strip()


# --- Accounts (just the two of you) --------------------------------------
# Passwords for the two fixed logins. Set these in .env before sharing!
# If left blank, defaults are used and the app shows a warning on screen.
HEATHER_PASSWORD = os.getenv("HEATHER_PASSWORD", "").strip()
CHUCK_PASSWORD = os.getenv("CHUCK_PASSWORD", "").strip()

# How long Harper's cool-down lasts, in minutes.
try:
    COOLDOWN_MINUTES = int(os.getenv("COOLDOWN_MINUTES", "60"))
except ValueError:
    COOLDOWN_MINUTES = 60

# Path to Harper's portrait image. Drop your generated picture here.
# If the file doesn't exist, a built-in placeholder face is shown.
HARPER_AVATAR = os.getenv("HARPER_AVATAR", "assets/harper.png").strip()


# --- Fish Audio (text-to-speech) -----------------------------------------
# Get a key at https://fish.audio  ->  API Keys
FISH_AUDIO_API_KEY = os.getenv("FISH_AUDIO_API_KEY", "").strip()
# A voice "reference_id" copied from the Fish Audio discovery page,
# or one you created by cloning a voice. NOT the ElevenLabs voice id.
FISH_AUDIO_REFERENCE_ID = os.getenv("FISH_AUDIO_REFERENCE_ID", "").strip()
# Model: "s1" or "s2-pro"
FISH_AUDIO_MODEL = os.getenv("FISH_AUDIO_MODEL", "s2-pro").strip()


def brain_enabled() -> bool:
    """True when we have what we need to call the AI."""
    return bool(OPENROUTER_API_KEY)


def voice_enabled() -> bool:
    """True when we can synthesize speech."""
    return bool(FISH_AUDIO_API_KEY)


def passwords_set() -> bool:
    """True when both account passwords were configured (not defaults)."""
    return bool(HEATHER_PASSWORD) and bool(CHUCK_PASSWORD)
