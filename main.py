"""🦋 Harper — Relationship Mediator AI (terminal version)

NOTE: The real app is the phone-friendly web version — run `streamlit run app.py`.
This terminal version is kept for quick local testing of the AI + voice. It does
NOT have logins, private spaces, saved memory, or the cool-down flow; app.py does.

Run:  python main.py

Harper loads the personality profiles, then offers her core modes.
Conversations use OpenRouter for the AI brain and Fish Audio for voice.
Without API keys she still runs in a friendly offline mode.
"""

import config
from brain import CORE, Conversation, MODES
import voice

# Menu order for the five core modes.
MENU = ["heather", "chuck", "both", "checkin", "intimacy"]


def banner():
    print()
    print("🦋  Harper — Relationship Mediator AI")
    print("    Part of the Chaos³ Initiative | OMEGA System vΩ.11")
    print("-" * 52)
    print(f"Core empathy level : {CORE.get('empathy')}")
    print(f"Tone               : {CORE.get('tone')}")
    brain = "ON (OpenRouter)" if config.brain_enabled() else "OFFLINE (no key — scripted replies)"
    spk = "ON (Fish Audio)" if config.voice_enabled() else "OFF (text only)"
    print(f"AI brain           : {brain}")
    print(f"Voice              : {spk}")
    print("-" * 52)


def show_menu():
    print("\nWho would you like to talk to?\n")
    for i, key in enumerate(MENU, 1):
        m = MODES[key]
        print(f"  {i}. {m['title']}  —  {m['blurb']}")
    print("  0. Exit")


def pick_mode():
    while True:
        choice = input("\nChoose (0-5): ").strip()
        if choice == "0":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(MENU):
            return MENU[int(choice) - 1]
        print("Please enter a number from 0 to 5.")


def run_session(mode_key: str):
    convo = Conversation(mode_key)
    print(f"\n— {convo.mode['title']} —")
    print("(type 'menu' to switch modes, 'quit' to exit)\n")

    print(f"Harper: {convo.greeting}")
    voice.speak(convo.greeting)

    while True:
        try:
            user = input("You: ").strip()
        except EOFError:
            return "quit"
        if not user:
            continue
        low = user.lower()
        if low in ("menu", "back"):
            return "menu"
        if low in ("quit", "exit", "bye"):
            return "quit"

        reply = convo.ask(user)
        print(f"Harper: {reply}")
        voice.speak(reply)


def main():
    banner()
    if not config.brain_enabled():
        print(
            "\nTip: set OPENROUTER_API_KEY (and optionally FISH_AUDIO_API_KEY) in a"
            "\n.env file to unlock the full AI + voice experience. See .env.example.\n"
        )

    while True:
        show_menu()
        mode_key = pick_mode()
        if mode_key is None:
            break
        result = run_session(mode_key)
        if result == "quit":
            break

    print("\nHarper: Take care of each other. I'm here whenever you need me. 💙\n")


if __name__ == "__main__":
    main()
