"""🦋 Harper — web app (phone-friendly, two logins, private spaces).

Run locally:   streamlit run app.py
On Replit:     the .replit file runs it automatically.

Heather and Chuck each log in on their own phone. Each has a private space
only they can see. The "Talk Together" room is the only shared space. After a
fight, the Cool-Down flow gives them an hour to breathe, then Harper checks in
and can nudge the partner — without ever leaking what was said.
"""

import time

import streamlit as st

import auth
import avatar
import brain
import config
import store
import voice

st.set_page_config(page_title="Harper", page_icon="🦋", layout="centered")


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def _ss(key, default):
    if key not in st.session_state:
        st.session_state[key] = default
    return st.session_state[key]


def fmt_mmss(seconds: int) -> str:
    m, s = divmod(max(0, seconds), 60)
    return f"{m:02d}:{s:02d}"


# ----------------------------------------------------------------------
# Login gate
# ----------------------------------------------------------------------
def login_screen():
    st.markdown("## 🦋 Harper")
    st.caption("Your laid-back relationship buddy. Private for you and Chuck.")

    if auth.using_default_passwords():
        st.warning(
            "Heads up: default passwords are in use (heather/`unicorns`, "
            "chuck/`puppies`). Set HEATHER_PASSWORD and CHUCK_PASSWORD in your "
            ".env before sharing this link.",
            icon="⚠️",
        )

    with st.form("login"):
        username = st.text_input("Who are you?", placeholder="heather or chuck")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Come in 💙", use_container_width=True)
    if submitted:
        if auth.check_login(username, password):
            st.session_state.user = username.strip().lower()
            st.rerun()
        else:
            st.error("Nope, that's not right. Try again.")


# ----------------------------------------------------------------------
# Cool-down + partner-signal banners
# ----------------------------------------------------------------------
def render_cooldown_status(user: str):
    """Show the live countdown if a cool-down is running, and greet on reopen."""
    data = store.load()
    remaining = store.cooldown_remaining(data, user)

    if remaining > 0:
        @st.fragment(run_every=1)
        def _tick():
            d = store.load()
            left = store.cooldown_remaining(d, user)
            if left <= 0:
                st.rerun()
            st.info(
                f"🧊 **Cool-down:** {fmt_mmss(left)} left. Go breathe — "
                "I'll be right here. No texting them anything wild, okay?",
                icon="🧊",
            )
        try:
            _tick()
        except Exception:
            # Older Streamlit without run_every fragments: static + refresh.
            st.info(f"🧊 Cool-down: {fmt_mmss(remaining)} left.", icon="🧊")
            if st.button("Refresh timer"):
                st.rerun()
        return

    # Cool-down just ended (timestamp set but now expired) -> greet on reopen.
    if store.get_cooldown(data, user) is not None:
        partner = auth.display_name(auth.partner_of(user))
        st.success(
            f"Hey — your hour's up. You feeling any better? Wanna talk it out "
            f"with me, or want me to let {partner} know you're ready to talk?",
            icon="💙",
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button(f"Let {partner} know I'm ready", use_container_width=True):
                d = store.load()
                store.add_signal(d, user, auth.partner_of(user), "ready_to_talk")
                store.clear_cooldown(d, user)
                store.save(d)
                st.toast(f"Done — {partner} will see it next time they open Harper.")
                st.rerun()
        with c2:
            if st.button("Not yet, just clear it", use_container_width=True):
                d = store.load()
                store.clear_cooldown(d, user)
                store.save(d)
                st.rerun()


def render_partner_signals(user: str):
    """Show (and clear) any 'ready to talk' nudges from the partner."""
    data = store.load()
    signals = store.peek_signals_for(data, user)
    if not signals:
        return
    partner_user = auth.partner_of(user)
    partner = auth.display_name(partner_user)
    if any(s["type"] == "ready_to_talk" for s in signals):
        st.success(
            f"💌 {partner} is ready to talk about earlier, whenever you are. "
            "No pressure — head to **Talk Together** when you're good.",
            icon="💌",
        )
        if st.button("Got it 👍"):
            d = store.load()
            store.pop_signals_for(d, user)
            store.save(d)
            st.rerun()


# ----------------------------------------------------------------------
# Chat
# ----------------------------------------------------------------------
def render_chat(user: str, mode_key: str):
    mode = brain.MODES[mode_key]
    is_shared = mode_key == "both"

    st.subheader(mode["title"])
    st.caption(mode["blurb"] + ("  ·  🔒 only you can see this" if not is_shared
                                 else "  ·  👥 shared with your partner"))

    data = store.load()
    history = store.get_history(data, user, mode_key)

    # Harper's face, up top. Aura color follows the mood of her latest message;
    # the slot lets us switch to a "talking" pulse in place after she replies.
    last_harper = next((m["content"] for m in reversed(history)
                        if m["role"] == "assistant"), mode["greeting"])
    avatar_slot = st.empty()
    with avatar_slot.container():
        avatar.render(st, mood=avatar.detect_mood(last_harper), talking=False)

    # Greeting first time in an empty thread.
    if not history:
        with st.chat_message("assistant", avatar="🦋"):
            st.write(mode["greeting"])

    # Render saved history.
    for m in history:
        if m["role"] == "system":
            continue
        icon = "🦋" if m["role"] == "assistant" else "🧑"
        with st.chat_message(m["role"], avatar=icon):
            if is_shared and m.get("speaker"):
                st.markdown(f"**{m['speaker']}:** {m['content']}")
            else:
                st.write(m["content"])

    # Persistent cool-down starter: in Cool-Down mode, once they've vented and
    # there's no timer running, always offer to start the hour. (Placing this
    # here — not after a message — means it survives Streamlit's reruns.)
    if mode_key == "cooldown" and history and store.cooldown_remaining(data, user) == 0:
        if st.button("🧊 Start my cool-down hour", use_container_width=True):
            d = store.load()
            store.set_cooldown(d, user, config.COOLDOWN_MINUTES)
            store.save(d)
            st.rerun()

    # In the shared room, tag who's speaking.
    speaker = auth.display_name(user) if is_shared else None

    prompt = st.chat_input("Talk to Harper…")
    if not prompt:
        return

    # Echo the user's message.
    with st.chat_message("user", avatar="🧑"):
        st.markdown(f"**{speaker}:** {prompt}" if is_shared else prompt)

    # Persist user turn.
    data = store.load()
    user_content = f"{speaker}: {prompt}" if is_shared else prompt
    store.append_message(data, user, mode_key, "user", user_content, speaker)

    # Build conversation from the saved history and get Harper's reply.
    convo_history = [
        {"role": x["role"], "content": x["content"]}
        for x in store.get_history(data, user, mode_key)
    ]
    convo = brain.Conversation(mode_key)
    convo.messages = [convo.messages[0]] + convo_history  # system + history
    with st.chat_message("assistant", avatar="🦋"):
        with st.spinner("Harper's thinking…"):
            reply = convo._respond()
        st.write(reply)
        audio = voice.synth_bytes(reply)
        if audio:
            st.audio(audio, format="audio/mp3", autoplay=True)

    # Make Harper "come alive" — re-render her face with the new mood and a
    # talking pulse, in place (no rerun, so the audio keeps playing).
    with avatar_slot.container():
        avatar.render(st, mood=avatar.detect_mood(reply), talking=True)

    store.append_message(data, user, mode_key, "assistant", reply)
    store.save(data)

    # In Cool-Down mode, rerun so the "Start my cool-down hour" button appears
    # now that there's history to act on.
    if mode_key == "cooldown" and store.cooldown_remaining(data, user) == 0:
        st.rerun()


# ----------------------------------------------------------------------
# Main app (logged in)
# ----------------------------------------------------------------------
def mode_order_for(user: str) -> list:
    """Cool-down + this user's own private space first, then shared + extras."""
    own = "heather" if user == "heather" else "chuck"
    return ["cooldown", own, "both", "checkin", "intimacy"]


def app_screen():
    user = st.session_state.user
    name = auth.display_name(user)
    modes = mode_order_for(user)

    with st.sidebar:
        st.markdown(f"### 🦋 Hey {name}")
        if not config.brain_enabled():
            st.caption("⚙️ Offline mode (no AI key) — replies are basic.")
        if not config.voice_enabled():
            st.caption("🔇 Voice off (no Fish Audio key).")
        if avatar.using_placeholder():
            st.caption("🖼️ Placeholder face — add assets/harper.png to see her.")

        mode_key = st.radio(
            "Where to?",
            options=modes,
            format_func=lambda k: brain.MODES[k]["title"],
            key="mode",
        )

        st.divider()
        if st.button("Log out"):
            for k in ("user", "mode"):
                st.session_state.pop(k, None)
            st.rerun()

    # Banners at the top.
    render_partner_signals(user)
    render_cooldown_status(user)

    render_chat(user, mode_key)


def main():
    _ss("user", None)
    if not st.session_state.user:
        login_screen()
        return
    _ss("mode", "cooldown")
    app_screen()


if __name__ == "__main__":
    main()
