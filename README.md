<h1 align="center">💜 stream-notifier-bot</h1>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/python-3.12+-89b4fa?style=for-the-badge&logo=python&logoColor=11111b">
    <source media="(prefers-color-scheme: light)" srcset="https://img.shields.io/badge/python-3.12+-4c7a5d?style=for-the-badge&logo=python&logoColor=ffffff">
    <img alt="Python" src="https://img.shields.io/badge/python-3.12+-89b4fa?style=for-the-badge&logo=python&logoColor=11111b">
  </picture>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/aiogram-3.x-a6e3a1?style=for-the-badge&logo=telegram&logoColor=11111b">
    <source media="(prefers-color-scheme: light)" srcset="https://img.shields.io/badge/aiogram-3.x-2ca5e0?style=for-the-badge&logo=telegram&logoColor=ffffff">
    <img alt="aiogram" src="https://img.shields.io/badge/aiogram-3.x-a6e3a1?style=for-the-badge&logo=telegram&logoColor=11111b">
  </picture>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/built__with-uv-f9e2af?style=for-the-badge&logo=fastapi&logoColor=11111b">
    <source media="(prefers-color-scheme: light)" srcset="https://img.shields.io/badge/built__with-uv-de5d83?style=for-the-badge&logo=fastapi&logoColor=ffffff">
    <img alt="uv" src="https://img.shields.io/badge/built__with-uv-f9e2af?style=for-the-badge&logo=fastapi&logoColor=11111b">
  </picture>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/docker-compose-cba6f7?style=for-the-badge&logo=docker&logoColor=11111b">
    <source media="(prefers-color-scheme: light)" srcset="https://img.shields.io/badge/docker-compose-2496ed?style=for-the-badge&logo=docker&logoColor=ffffff">
    <img alt="Docker" src="https://img.shields.io/badge/docker-compose-cba6f7?style=for-the-badge&logo=docker&logoColor=11111b">
  </picture>
</p>

<p align="center">
  A clean, high-performance asynchronous service engineered to track Twitch stream states in real time and automatically publish interactive notifications to a Telegram channel, featuring seamless automated commenting inside the linked discussion group.
</p>

---

## ⚡ Key Features

- 🎯 **Twitch Helix Engine:** Asynchronous, stateless polling mechanism with fully automated OAuth2 App Access Token lifecycle management.
- 🖼️ **Dynamic Asset Handling:** Fetches live stream metadata and handles binary image streams on the fly to deliver fresh, high-resolution thumbnails.
- 🔄 **In-Place State Mutation:** Automatically edits original Telegram channel posts when the stream goes offline, swapping active control buttons for a direct VOD link.
- 💬 **Smart Discussion Threading:** Detects automatic post forwards in the linked discussion chat and instantly drops a customizable call-to-action comment to boost engagement.
- 🌐 **Hot-Reload Localization:** Fully decoupled translation layer (`ru.yml`, `en.yml`) that applies updates immediately on the host without requiring a container rebuild or service restart.

---

## 📐 System Architecture & Data Flow

```text
       ┌────────────────────────┐
       │    Twitch Helix API    │
       └───────────┬────────────┘
                   │ [JSON Polling Engine]
                   ▼
       ┌────────────────────────┐
       │     State Manager      ├─► [Live] ──► Fetch Binary Thumbnail
       └───────────┬────────────┘ └─► [Offline] ► Swap Buttons to VOD Record
                   │
                   │ [Dispatches Payload]
                   ▼
       ┌────────────────────────┐
       │  Telegram Channel Bot  │ ◄─── Uses Locales (en.yml / ru.yml)
       └───────────┬────────────┘
                   │
                   │ [Telegram Auto-Forward]
                   ▼
       ┌────────────────────────┐
       │  Discussion Group Chat │ ───► Injects Auto-Comment to Thread
       └────────────────────────┘
```

---

## ⚙️ Token Acquisition & Prerequisites

### 🔹 Telegram Setup
1. **BOT_TOKEN:** Create a new bot instance using [@BotFather](https://t.me/BotFather), run the `/newbot` command, and securely copy the generated API token.
2. **CHANNEL_ID & DISCUSSION_ID:** Add the bot to your target channel and its linked discussion group as an administrator with full post-publishing and message-deletion privileges. Extract the exact unique IDs (prefixed with `-100`) by forwarding a message from the channel/chat to [@getidsbot](https://t.me/getidsbot).
3. **CHANNEL_CHAT_LINK:** Obtain the public or private invitation link to your discussion chat (e.g., https://t.me/your_chat) to populate interactive inline keyboard targets.

### 🔹 Twitch Developer Platform
1. Log into your account via the [Twitch Developer Console](https://dev.twitch.tv).
2. Register a new application profile (**Register Your Application**):
   - Input a unique, descriptive application identifier name.
   - Configure the OAuth Redirect URL boundary to `http://localhost`.
   - Set the category classification to `Application Integration`.
3. Open your application settings to copy the **Client ID**, then generate a fresh **Client Secret** (save it securely, as it will only be displayed once).

---

## 📄 Environment Configuration (`.env`)

Create a `.env` configuration file in your project root using the production template below:

```env
# Telegram Configuration
BOT_TOKEN=1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ
CHANNEL_ID=-1001111111111
DISCUSSION_ID=-1002222222222
CHANNEL_CHAT_LINK=https://t.me/example_chat

# Twitch Integration
TWITCH_CLIENT_ID=uio456pasdfghjklzxcvbnm123456
TWITCH_SECRET=mnbvcxzlkjhgfdsaqpwoeiru789012
STREAMER_USERNAME=twitch
```

---

## 🌐 Localization Schema Layout

The translation engine watches directory patterns natively. Below is the exact structural representation of the decoupled localization blueprint (`locales/en.yml`):

```yaml
notifications:
  buttons:
    link: "Go to Chat"
    watch_vod: "Watch VOD"
  auto_comment:
    text: "👋 Hi! Thanks for the forward. Join our main chat to chat!"
  online:
    caption: "🔴 <b>%{stream_title}</b>\n\n🎮 Game: %{game_name}\n\nJoin the stream!"
  offline:
    caption: "💤 Stream has ended. See you next time! The broadcast recording is available below."
```

---

## 🚀 Deployment Blueprints

### 📦 Option A: Containerized Runtime via Docker Compose (Recommended)
Utilizes a lean, multi-stage `Dockerfile` architecture engineered with `uv` to maintain a minimal production footprint.

Launch the service stack silently in the background:
```bash
docker compose up -d --build
```

> [!NOTE]
> The host `./locales` directory is mounted as a Read-Only (`:ro`) target configuration volume. You can modify your translation files directly on the host server, and changes will be parsed dynamically without container teardowns.

Monitor real-time application logs:
```bash
docker compose logs -f app
```

### 🛠️ Option B: Native Systemd System Unit (Ubuntu/Debian)
For deployment directly within the operating system's native process tracking infrastructure:

1. Provision an isolated virtual environment and synchronize pinned constraints:
```bash
uv venv
source .venv/bin/activate
uv sync --frozen --no-dev
```

2. Establish a new system service configuration unit:
```bash
sudo nano /etc/systemd/system/stream-notifier-bot.service
```

3. Populate the service layout file precisely:
```ini
[Unit]
Description=Telegram & Twitch Stream Notifier Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/stream-notifier-bot
ExecStart=/home/ubuntu/stream-notifier-bot/.venv/bin/python -m src.main
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1
Environment=PYTHONPATH=/home/ubuntu/stream-notifier-bot

[Install]
WantedBy=multi-user.target
```

4. Reload system control daemon structures and activate the background worker:
```bash
sudo systemctl daemon-reload
sudo systemctl enable stream-notifier-bot --now
```

5. Intercept active execution logging pipelines:
```bash
sudo journalctl -u stream-notifier-bot -f
```

---

## 🔍 Troubleshooting

### 💡 The bot does not drop comments in the discussion group
- **Root Cause:** The bot is either missing specific admin boundaries inside the group chat or the `DISCUSSION_ID` inside your `.env` does not match the true hidden target identity.
- **Solution:** Verify the bot has both `Can Post Messages` and `Can Delete Messages` privileges enabled within the chat admin settings dashboard. Re-verify the `-100` channel prefix.

### 💡 Twitch requests crash with `401 Unauthorized` errors
- **Root Cause:** Your `TWITCH_SECRET` or `TWITCH_CLIENT_ID` configuration pairs are stale, corrupted, or the App Access Token has expired natively without proper tracking synchronization.
- **Solution:** Wipe local runtime variables, generate a fresh replacement token inside the Twitch Console dashboard, and restart the service runtime completely.

---

## 📄 License

This software is distributed under the terms of the [MIT License](LICENSE). Feel free to inspect, refactor, or scale the repository infrastructure globally.

---

<p align="center">
  Built with ❤️ and clean code paradigms.
</p>