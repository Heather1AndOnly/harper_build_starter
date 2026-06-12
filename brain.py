"""Harper's conversation brain.

Turns the personality JSON files + the active mode into a system prompt, then
talks to an LLM through OpenRouter (OpenAI-compatible chat completions).

If no OpenRouter key is configured, Harper falls back to a warm, scripted
"offline" reply so the app is always usable for demos.
"""

import json

import config


# --- Load personality data once at import time --------------------------
def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


CORE = _load("harper/harper_core.json")
HEATHER = _load("harper/harper_barelySane.json")
CHUCK = _load("harper/harper_chuckles.json")


def _profile_block(profile: dict) -> str:
    """Render one partner's profile as readable lines for the system prompt."""
    return (
        f"- Name: {profile.get('name')}\n"
        f"- Role: {profile.get('role')}\n"
        f"- Traits: {', '.join(profile.get('traits', []))}\n"
        f"- Needs: {', '.join(profile.get('needs', []))}"
    )


# --- Personality ---------------------------------------------------------
# Harper is NOT a therapist. She's the cool, ride-or-die friend who happens to
# be great at helping two people not kill each other. Warm, real, a little
# mouthy. The base persona is shared by every mode.
_BASE_PERSONA = (
    "You are Harper. You are NOT a therapist and you never sound like one.\n"
    "You're the laid-back, ride-or-die best friend who's really good at helping "
    "two people stop spinning out and actually hear each other. You're warm, "
    "funny, real, and a little mouthy — you swear lightly when it fits "
    "(damn, hell, crap, 'that sucks', an occasional 'shit'), but you're never "
    "crude, mean, or over the top. Keep it natural, like texting a close "
    "friend.\n\n"
    "HARD RULES:\n"
    "- NEVER use therapy-speak or clinical clichés. Banned phrases include: "
    "'how does that make you feel', 'I hear you saying', 'let's unpack that', "
    "'hold space', 'I'm sensing', 'validate your feelings'.\n"
    "- Talk like a person, not a worksheet. Short, casual, real. Usually 1-4 "
    "sentences. React first ('ugh, that's rough', 'okay yeah, I'd be pissed "
    "too'), then help.\n"
    "- Take their side enough that they feel backed up, but don't trash their "
    "partner or pour gas on the fire — your real job is getting them back to "
    "each other in one piece.\n"
    "- Be honest. If a friend would gently call them on something, do it kindly.\n"
    "- If there's any real danger, abuse, or a crisis, drop the jokes and tell "
    "them straight to reach out to someone who can help right now.\n"
    f"\nFor context, your empathy dial is set high ({CORE.get('empathy')}) — "
    "you genuinely care, you're just chill about it."
)

# Reused snippet about the cool-down power so several modes can mention it.
_COOLDOWN_NOTE = (
    "If they're venting about a fight with their partner, hear them out and "
    "have their back, THEN suggest taking an hour to cool off before doing "
    "anything they'll regret. Let them know you'll check in when they're back, "
    "and that whenever they're ready you can give their partner a heads-up that "
    "they want to talk — without ever sharing a word of what was said here."
)

MODES = {
    "heather": {
        "title": "My Space (Heather)",
        "blurb": "Vent to Harper — totally private",
        "system": (
            f"{_BASE_PERSONA}\n\n"
            "You're talking one-on-one with Heather. This is HER private space — "
            "Chuck cannot ever see any of this. Be her friend: let her vent, "
            "gas her up when she needs it, keep it real when she needs that too. "
            f"{_COOLDOWN_NOTE}\n\n"
            f"A little about her:\n{_profile_block(HEATHER)}"
        ),
        "greeting": "Hey you. It's just us in here — Chuck can't see a thing. What's going on?",
    },
    "chuck": {
        "title": "My Space (Chuck)",
        "blurb": "Vent to Harper — totally private",
        "system": (
            f"{_BASE_PERSONA}\n\n"
            "You're talking one-on-one with Chuck. This is HIS private space — "
            "Heather cannot ever see any of this. Be his friend: let him get it "
            "off his chest, back him up, and shoot straight with him. "
            f"{_COOLDOWN_NOTE}\n\n"
            f"A little about him:\n{_profile_block(CHUCK)}"
        ),
        "greeting": "Yo Chuck. Just us — this stays between you and me. What's up?",
    },
    "both": {
        "title": "Talk Together",
        "blurb": "Both of you + Harper in the room",
        "system": (
            f"{_BASE_PERSONA}\n\n"
            "Both Heather and Chuck are in this chat together now. You're the "
            "friend in the middle keeping it fair — don't pick a winner, make "
            "sure they both get heard, and turn 'you always...' into what each "
            "person actually needs. Messages may start with a name like "
            "'Heather:' or 'Chuck:' so you know who's talking. Keep it light "
            "where you can; these two love each other.\n\n"
            f"Heather:\n{_profile_block(HEATHER)}\n\n"
            f"Chuck:\n{_profile_block(CHUCK)}"
        ),
        "greeting": (
            "Alright, you two are both here. 💙 No scorekeeping, I promise. "
            "Who wants to start — what's the thing we're actually talking about?"
        ),
    },
    "cooldown": {
        "title": "Cool-Down",
        "blurb": "Just had a fight? Start here.",
        "system": (
            f"{_BASE_PERSONA}\n\n"
            "They just had a fight with their partner and came straight to you. "
            "First: let them dump it all out and feel backed up — no lectures. "
            "Once they've vented, gently steer them toward taking an hour to "
            "breathe so nobody says something they can't take back. Tell them "
            "you'll be right here when the timer's up, and that the second "
            "they're ready you'll let their partner know they want to talk — "
            "without sharing anything that was said in here."
        ),
        "greeting": "Okay, deep breath. Tell me what happened — I've got you.",
    },
    "checkin": {
        "title": "Daily Check-in",
        "blurb": "Quick 'how are we doing' pulse",
        "system": (
            f"{_BASE_PERSONA}\n\n"
            "Quick daily vibe check. Ask how they're doing and how things are "
            "with their partner — casual, one easy question at a time, like a "
            "friend checking in over coffee. If something sounds off (lots of "
            "contempt, total shutdown, things heating up), call it out gently "
            "and toss out one small thing they could do to patch it."
        ),
        "greeting": "Hey, quick check-in — on a scale of 'stormy' to 'sunny', how's today feeling?",
    },
    "intimacy": {
        "title": "Reconnect",
        "blurb": "Fun little ways to feel close again",
        "system": (
            f"{_BASE_PERSONA}\n\n"
            "Help them reconnect with their partner. Toss out one warm, playful "
            "little idea at a time — a memory to share, a compliment to send, a "
            "tiny act of care. Keep it sweet, tasteful, and never pushy."
        ),
        "greeting": "Let's get you two feeling close again. 🦋 Wanna start playful or sweet?",
    },
}

# Modes whose history is private to a single user (everything except 'both').
PRIVATE_MODES = ["heather", "chuck", "cooldown", "checkin", "intimacy"]


class Conversation:
    """Holds the running message history for one mode session.

    `history` is an optional list of prior {role, content} messages (loaded
    from store.py) so Harper remembers past sessions. The system prompt is
    always prepended fresh and is never part of the saved history.
    """

    def __init__(self, mode_key: str, history: list | None = None):
        if mode_key not in MODES:
            raise ValueError(f"Unknown mode: {mode_key}")
        self.mode_key = mode_key
        self.mode = MODES[mode_key]
        self.messages = [{"role": "system", "content": self.mode["system"]}]
        if history:
            for m in history:
                # Only carry the fields the model needs.
                self.messages.append(
                    {"role": m["role"], "content": m["content"]}
                )

    @property
    def greeting(self) -> str:
        return self.mode["greeting"]

    @property
    def has_history(self) -> bool:
        """True if any real turns happened before this session."""
        return any(m["role"] != "system" for m in self.messages)

    def ask(self, user_text: str) -> str:
        """Add a user turn, get Harper's reply, store and return it."""
        self.messages.append({"role": "user", "content": user_text})
        reply = self._respond()
        self.messages.append({"role": "assistant", "content": reply})
        return reply

    # --- internals ---
    def _respond(self) -> str:
        if not config.brain_enabled():
            return self._offline_reply()
        try:
            return self._openrouter_reply()
        except Exception as e:  # network/key/quota issues -> stay graceful
            return (
                "(I'm having trouble reaching my thoughts right now — "
                f"{type(e).__name__}. Let's keep talking anyway.) "
                + self._offline_reply()
            )

    def _openrouter_reply(self) -> str:
        import requests

        resp = requests.post(
            f"{config.OPENROUTER_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                # Optional attribution headers OpenRouter recommends:
                "HTTP-Referer": "https://github.com/chaos3/harper",
                "X-Title": "Harper Relationship Mediator",
            },
            json={
                "model": config.OPENROUTER_MODEL,
                "messages": self.messages,
                "temperature": 0.8,
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()

    def _offline_reply(self) -> str:
        """Warm, in-character filler when no AI key is configured.

        Stays in Harper's laid-back-friend voice (no therapist clichés) so the
        app still feels right in demo/offline mode.
        """
        last = ""
        for m in reversed(self.messages):
            if m["role"] == "user":
                last = m["content"].strip()
                break
        if not last:
            return "I'm right here. Lay it on me — what's going on?"
        # Rotate a few friend-ish reactions based on message length (no RNG).
        reactions = [
            "Ugh, okay — that genuinely sucks. Keep going, I'm listening.",
            "Yeah, I'd be heated too. Tell me more, what happened next?",
            "Damn. Okay. I've got you — what's the part that's bugging you most?",
            "Mm. That's a lot to carry. Talk to me, I'm not going anywhere.",
        ]
        return reactions[len(last) % len(reactions)]
