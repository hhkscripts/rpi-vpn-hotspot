# Telegram Bot For GoodWifi

This optional bot controls the Raspberry Pi GoodWifi hotspot through Telegram. It runs in Docker and calls the same host manager used by the CLI:

```text
/usr/local/bin/hotspot-manager.py
```

Service/container name:

```text
mpxraspberrypibot
```

## Setup

Create a Telegram bot with `@BotFather`, then configure the bot container:

```bash
cd telegrambot
cp .env.example .env
nano .env
```

Required:

```text
TELEGRAM_BOT_TOKEN=<bot-token>
```

Optional (Security & Configuration):

```text
# Security (Default-Deny): Comma-separated list of authorized Telegram user IDs
TELEGRAM_ALLOWED_USERS=12345678,87654321

# Development override: set to true to allow all users (NOT recommended for production)
TELEGRAM_ALLOW_ALL_USERS=false

# Docker health server
BOT_HEALTH_HOST=0.0.0.0
BOT_HEALTH_PORT=8081
BOT_SERVICE_NAME=mpxraspberrypibot
```

Start or update the bot:

```bash
docker compose up -d --build
```

## Commands

| Command | Description |
| --- | --- |
| `/start` | Start the bot |
| `/status` | Show hotspot status |
| `/restart` | Restart hotspot services and reapply routing |
| `/restart_vpn` | Restart VPN and refresh modular routes (local & vpn) |
| `/fix` | Run the manager's automatic fix path |
| `/clients` | Show connected client count |
| `/help` | Show command help |

## Health Endpoint

The bot exposes a health endpoint for the central Cloudflare tunnel:

```text
https://mpxraspberrypibot.hhk.my.id/bot-health
```

Cloudflare should point to:

```text
http://mpxraspberrypibot:8081
```

The central `cloudflared` container is managed outside this project. Do not run a separate `cloudflared` process from this directory.

## Troubleshooting

Check container state and logs:

```bash
docker compose ps
docker compose logs -f
```

Check the host manager directly:

```bash
sudo /usr/local/bin/hotspot-manager.py --status
```

If Telegram replies but the hotspot action fails, fix the host-side GoodWifi setup first from the main [README](../README.md).

## Modular Architecture

The bot codebase follows a granular, single-responsibility structure with small modules:

```text
telegrambot/
├── bot.py                  # Main entrypoint & handler registration (~120 lines)
├── constants/
│   ├── emojis.py           # Custom emoji IDs and HTML tags
│   ├── flags.py            # Country flags mapping
│   └── profiles.py         # Country profile discovery & region metadata
├── core/
│   ├── config.py           # Configuration & user authorization
│   ├── health.py           # Docker HTTP health check server
│   └── runner.py           # nsenter host execution & state readers
├── ui/
│   ├── main_keyboard.py    # Reply keyboard with custom emojis
│   ├── status_keyboards.py # Inline status & action buttons
│   ├── vpn_keyboards.py    # VPN switcher buttons
│   ├── country_keyboards.py# Region & country selection grids
│   ├── adguard_keyboards.py# AdGuard toggle buttons
│   └── ipv6_keyboards.py   # IPv6 leak protection buttons
└── handlers/
    ├── common.py           # /start and /help commands
    ├── status.py           # /status command & refresh callback
    ├── vpn.py              # VPN backend switching handlers
    ├── country.py          # Exit country switching handlers
    ├── adguard.py          # AdGuard DNS toggle handlers
    ├── ipv6.py             # IPv6 mode switching handlers
    ├── maintenance.py      # Restart, fix, and clients handlers
    └── text_router.py      # Plain text message routing
```

## Running Unit Tests

To run the unit tests for the bot:

```bash
python3 -m unittest -v tests/test_telegram_bot.py
```
