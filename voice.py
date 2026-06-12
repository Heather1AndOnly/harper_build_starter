"""Harper's voice — Fish Audio text-to-speech.

Sends text to the Fish Audio TTS endpoint and saves (and optionally plays) the
resulting audio. If no Fish Audio key is configured, speaking is a silent no-op
so the rest of the app keeps working.

Docs: https://docs.fish.audio/api-reference/endpoint/openapi-v1/text-to-speech
"""

import os
import shutil
import subprocess

import config

_TTS_URL = "https://api.fish.audio/v1/tts"
_counter = 0


def synth_bytes(text: str) -> bytes | None:
    """Synthesize `text` and return raw mp3 bytes (for st.audio), or None.

    Never raises — voice is a nice-to-have, not a blocker. Returns None when
    voice is disabled, the text is empty, or the request fails.
    """
    if not config.voice_enabled() or not text.strip():
        return None
    try:
        import requests

        payload = {
            "text": text,
            "format": "mp3",
            "latency": "normal",
            "chunk_length": 200,
        }
        if config.FISH_AUDIO_REFERENCE_ID:
            payload["reference_id"] = config.FISH_AUDIO_REFERENCE_ID

        resp = requests.post(
            _TTS_URL,
            headers={
                "Authorization": f"Bearer {config.FISH_AUDIO_API_KEY}",
                "Content-Type": "application/json",
                "model": config.FISH_AUDIO_MODEL,
            },
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        print(f"   (voice unavailable: {type(e).__name__})")
        return None


def speak(text: str, play: bool = True) -> str | None:
    """Synthesize `text` to an mp3 file (CLI use). Returns the path, or None."""
    audio = synth_bytes(text)
    if audio is None:
        return None

    global _counter
    _counter += 1
    path = f"harper_voice_{_counter:03d}.mp3"
    try:
        with open(path, "wb") as f:
            f.write(audio)
    except OSError:
        return None

    if play:
        _play(path)
    return path


def _play(path: str) -> None:
    """Best-effort local playback using whatever player is available."""
    for player in ("afplay", "mpg123", "ffplay", "play"):
        if shutil.which(player):
            args = [player, path]
            if player == "ffplay":
                args = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", path]
            try:
                subprocess.run(args, check=False)
            except Exception:
                pass
            return
    # No player found — the file is saved; just let the user know once.
    if not getattr(_play, "_warned", False):
        print(f"   (saved audio to {os.path.abspath(path)} — no audio player found)")
        _play._warned = True
