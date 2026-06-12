"""Harper's face — a portrait that reacts (Tier 1 avatar).

This shows a single portrait of Harper with:
- a gentle "breathing" idle animation so she feels present,
- a glow that pulses while she's talking (when her voice/reply just landed),
- a mood-colored aura that shifts with the tone of her last message.

It does NOT do true lip-sync (that's a paid talking-head service). It's an
expressive portrait + voice, which reads as alive and costs nothing.

Drop a real picture at assets/harper.png (see config.HARPER_AVATAR). Until then
a built-in placeholder is used.
"""

import base64
import os

import config

# Mood -> aura color. Keyword-driven; falls back to calm blue.
_MOODS = {
    "calm":       "#7db5ff",   # soft blue (default / neutral)
    "happy":      "#ffd479",   # warm gold (upbeat, playful)
    "gentle":     "#c9a7ff",   # lilac (tender, comforting)
    "alert":      "#ffb35c",   # amber (red-flag / concern)
}

_MOOD_KEYWORDS = {
    "happy":  ["haha", "lol", "love this", "yay", "awesome", "🥳", "😄", "😂",
               "proud of you", "let's go", "nice", "sweet"],
    "alert":  ["whoa", "hold on", "that's not okay", "red flag", "serious",
               "concerned", "not cool", "careful", "🚩", "danger", "hurt"],
    "gentle": ["i've got you", "breathe", "take your time", "it's okay",
               "i'm here", "sorry", "that sucks", "💙", "🦋", "rough"],
}


def detect_mood(text: str) -> str:
    """Best-effort mood from Harper's message text -> a key in _MOODS."""
    if not text:
        return "calm"
    low = text.lower()
    # Priority: alert > gentle > happy > calm.
    for mood in ("alert", "gentle", "happy"):
        if any(kw in low for kw in _MOOD_KEYWORDS[mood]):
            return mood
    return "calm"


# --- placeholder ---------------------------------------------------------
_PLACEHOLDER_SVG = """
<svg xmlns='http://www.w3.org/2000/svg' width='320' height='320' viewBox='0 0 320 320'>
  <defs>
    <radialGradient id='bg' cx='50%' cy='40%' r='70%'>
      <stop offset='0%' stop-color='#3a2f5b'/>
      <stop offset='100%' stop-color='#1c1430'/>
    </radialGradient>
  </defs>
  <rect width='320' height='320' rx='160' fill='url(#bg)'/>
  <circle cx='160' cy='130' r='52' fill='#e9d6c2'/>
  <path d='M88 250 q72 -70 144 0 q-72 36 -144 0z' fill='#e9d6c2'/>
  <text x='160' y='300' font-family='sans-serif' font-size='20' fill='#cbb6ff'
        text-anchor='middle'>Harper 🦋</text>
</svg>
"""


def _avatar_data_uri() -> str:
    """Return a data: URI for Harper's image, or the placeholder SVG."""
    path = config.HARPER_AVATAR
    if path and os.path.exists(path):
        ext = os.path.splitext(path)[1].lower().lstrip(".") or "png"
        mime = "jpeg" if ext in ("jpg", "jpeg") else ext
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        return f"data:image/{mime};base64,{b64}"
    # Placeholder SVG, inlined.
    b64 = base64.b64encode(_PLACEHOLDER_SVG.strip().encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


def using_placeholder() -> bool:
    return not (config.HARPER_AVATAR and os.path.exists(config.HARPER_AVATAR))


def render(st, mood: str = "calm", talking: bool = False, size: int = 180) -> None:
    """Render Harper's avatar into the given Streamlit module.

    mood     -> one of _MOODS keys (controls aura color)
    talking  -> True pulses the glow harder (use right after she replies)
    size     -> pixel diameter
    """
    color = _MOODS.get(mood, _MOODS["calm"])
    uri = _avatar_data_uri()
    pulse = "harper-talking" if talking else "harper-idle"

    html = f"""
    <style>
    @keyframes harperBreathe {{
        0%   {{ transform: scale(1.00); }}
        50%  {{ transform: scale(1.03); }}
        100% {{ transform: scale(1.00); }}
    }}
    @keyframes harperTalk {{
        0%   {{ box-shadow: 0 0 18px 4px {color}55; }}
        50%  {{ box-shadow: 0 0 38px 12px {color}cc; }}
        100% {{ box-shadow: 0 0 18px 4px {color}55; }}
    }}
    @keyframes harperGlow {{
        0%   {{ box-shadow: 0 0 14px 3px {color}44; }}
        50%  {{ box-shadow: 0 0 22px 6px {color}77; }}
        100% {{ box-shadow: 0 0 14px 3px {color}44; }}
    }}
    .harper-wrap {{ display:flex; justify-content:center; margin: 4px 0 10px; }}
    .harper-face {{
        width: {size}px; height: {size}px; border-radius: 50%;
        background-image: url('{uri}');
        background-size: cover; background-position: center;
        border: 3px solid {color}aa;
        animation: harperBreathe 4s ease-in-out infinite;
    }}
    .harper-idle    {{ animation: harperBreathe 4s ease-in-out infinite,
                                  harperGlow 3.5s ease-in-out infinite; }}
    .harper-talking {{ animation: harperBreathe 2.2s ease-in-out infinite,
                                  harperTalk 1s ease-in-out infinite; }}
    </style>
    <div class="harper-wrap">
        <div class="harper-face {pulse}"></div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
