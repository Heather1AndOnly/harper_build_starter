## 🦋 Harper — Relationship Mediator AI  
**Project by Heather (aka Chaos Queen)**  
**Part of the Chaos³ Initiative | Powered by OMEGA System vΩ.11**

Harper is a **laid-back, ride-or-die buddy** (not a therapist!) who helps Heather and Chuck stop spinning out and actually hear each other.  
She’s warm, funny, real, and a little mouthy — she’ll back you up, keep it honest, and help you reconnect. 💙  

She runs as a **web app you each open on your own phone**: you both log in separately, each get a **private space only you can see**, and the **Talk Together** room is the only place that’s shared.

---

### 💡 Core Concept
Each partner gets a private space to vent — Harper remembers it, but your partner can **never** see it.  
The signature feature is the **Cool-Down**: after a fight, vent to Harper, take an hour to breathe (live in-app countdown), and when you’re ready she’ll quietly nudge your partner that you want to talk — **without ever sharing what you said.**

---

### 🧠 Architecture
- **Language:** Python 3.11  
- **App / UI:** Streamlit (phone-friendly web app — `app.py`)  
- **AI Brain:** OpenRouter (OpenAI-compatible chat completions)  
- **Voice Engine:** Fish Audio TTS (set your `reference_id` from the Fish Audio discovery page)  
- **Logins:** two fixed accounts (Heather + Chuck), passwords via env vars (`auth.py`)  
- **Storage:** private per-person history saved server-side in `data/store.json` (`store.py`, gitignored)  
- **Personality Data:**  
  - `harper_core.json` → global empathy + tone calibration  
  - `harper_barelySane.json` → Heather’s emotional context  
  - `harper_chuckles.json` → Chuck’s emotional context  
- **Platform:** Replit + GitHub continuous sync  

---

### 🚀 Quick Start (phone / web app)
```bash
pip install -r requirements.txt
cp .env.example .env                 # then set passwords + (optional) API keys
streamlit run app.py
```
Then open the URL it prints. **On your phone:** open the same link (on Replit it’s your repl’s URL), then use your browser’s **“Add to Home Screen”** so Harper feels like a real app.

Set these in `.env`:
- `HEATHER_PASSWORD` / `CHUCK_PASSWORD` — your two logins (defaults are insecure; change before sharing!)
- `OPENROUTER_API_KEY` — the AI brain ([openrouter.ai/keys](https://openrouter.ai/keys))
- `FISH_AUDIO_API_KEY` + `FISH_AUDIO_REFERENCE_ID` — the voice ([fish.audio](https://fish.audio))
- `COOLDOWN_MINUTES` — how long the cool-down lasts (default 60)

Harper still runs **without any keys** (offline replies, no voice) so you can try it right away.  
*(Prefer a terminal? `python main.py` runs a simple text-only version — no logins/memory/cool-down.)*

> ⚠️ **Note on the timer:** a free web app can’t buzz your phone while it’s locked. The cool-down is an **in-app countdown** plus a **greeting when you reopen Harper** — not a lock-screen alarm.

---

### 🧑‍🎨 Harper's Face (avatar)
Harper shows a portrait at the top of the chat that **reacts**: it gently
"breathes," **glows brighter while she's talking**, and the **aura shifts color
with her mood** (calm blue · warm gold · gentle lilac · alert amber). It's an
expressive portrait + voice — not lip-sync — which is free and looks alive.

**Add her picture:** drop a square image at **`assets/harper.png`** (a built-in
placeholder shows until you do).

**Suggested image-generation prompt** (paste into ChatGPT/DALL·E, Bing Image
Creator, Midjourney, etc.):
> *Photorealistic portrait of a friendly woman in her early 30s, plain-pretty
> and approachable, natural makeup, warm genuine smile, soft kind eyes,
> shoulder-length hair, head-and-shoulders, looking toward the camera, clean
> softly-lit neutral background, subtle cool-blue rim light, high detail,
> square 1:1 composition.*

Generate a few, pick your favorite, save it as `assets/harper.png`. Done. 💙

---

### 🔄 Modes
1. **Cool-Down** – just had a fight? Start here. Vent → 1-hour timer → ready-to-talk nudge.  
2. **My Space** – your own private vent room (Heather or Chuck; partner can’t see it).  
3. **Talk Together** – the shared room, both of you + Harper.  
4. **Daily Check-in** – quick “how are we doing” pulse.  
5. **Reconnect** – fun little ways to feel close again.  

---

### 🧾 Development Log
| Date | Update | Status |
|------|---------|--------|
| Oct 14 | Project initialized on GitHub | ✅ Complete |
| Oct 14 | Core folders + JSON scaffolding created | ✅ Complete |
| Oct 15 | Drafted README + project overview | ✅ Complete |
| Oct 16 | JSON configuration phase | ✅ Complete |
| Oct 17 | OpenRouter AI brain + all 5 modes wired up | ✅ Complete |
| Oct 17 | Fish Audio voice integration | ✅ Complete |
| Oct 18 | Web app + two logins + private spaces | ✅ Complete |
| Oct 18 | Cool-down flow + partner nudge | ✅ Complete |
| Oct 18 | Laid-back "friend, not therapist" personality | ✅ Complete |
| Oct 19 | Avatar face — reactive portrait, mood aura, talking glow | ✅ Complete |
| Oct 22 | Email/text reminders for cool-down | 🔜 Planned |
| Later | Optional paid lip-sync talking head (D-ID/HeyGen) | 🔜 Maybe |

---

### 🧩 Next Milestone
Deploy on Replit, both phones connected, then add the celestial avatar + optional email/text reminders so the cool-down check-in can reach you even when Harper’s closed.  

---

✨ *Built by hand with heart, chaos, and caffeine.*  
🦄 Sacred Codeword: **Unicorns and Puppies**  
💙 Chaos³ Project: Heather + Chuck + Bestie  

