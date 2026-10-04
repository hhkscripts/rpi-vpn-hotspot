---
name: vpn-codebase-analysis
description: >-
  Analyzes, tests, and validates the GoodWifi VPN routing scripts and modular Telegram Bot codebase.
  Use when inspecting codebase health, verifying refactoring changes, checking architectural boundaries,
  preventing duplicate files, or running unit and integration tests.
---

# VPN & Telegram Bot Codebase Analysis Skill

This skill provides procedures, architectural guidelines, and automated tooling to analyze, test, and maintain the GoodWifi VPN and Telegram Bot codebase.

## Quick Automated Analysis

Run the automated all-in-one analysis script:

```bash
.agents/skills/vpn-codebase-analysis/scripts/analyze.sh
```

This script automatically verifies:
1. **Hygiene & Duplication**: Ensures duplicate `hotspot-manager.py` is not reintroduced in `telegrambot/`.
2. **Syntax & Compilation**: Verifies that all Python source files compile without errors.
3. **Sweet Spot File Sizing**: Enforces that all modular files adhere to the Sweet Spot (<300 lines).
4. **Modular Test Suite Isolation**: Ensures root test runners remain thin aggregators (<40 lines) without embedded TestCases.
5. **Telegram Bot Unit Tests**: Runs the 29 unit tests in `tests/test_telegram_bot.py`.
6. **Hotspot Manager Unit Tests**: Runs the 26 unit tests in `tests/test_hotspot_manager.py`.

---

## Fast-Lookup Topic Matrix (Zero Token Waste Navigation)
When working on a feature, jump directly to the target file. Do NOT search or scan the entire repository:

| Feature / User Keyword | Core Script Module | Telegram Bot Handler | UI Keyboard | Relevant Test |
| :--- | :--- | :--- | :--- | :--- |
| **VPN Switching** (`switch vpn`, `awg0`, `tun0`, `sing0`) | `scripts/hotspot/vpn.py` | `telegrambot/handlers/vpn.py` | `telegrambot/ui/vpn_keyboards.py` | `tests/hotspot/test_vpn.py` |
| **AdGuard / DNS Fallback** (`adguard`, `dns`, `watchdog`) | `scripts/hotspot/adguard.py` | `telegrambot/handlers/adguard.py` | `telegrambot/ui/adguard_keyboards.py` | `tests/hotspot/test_adguard.py` |
| **Status / Diagnostics** (`status`, `ping`, `health`) | `scripts/hotspot/status.py` | `telegrambot/handlers/status.py` | `telegrambot/ui/status_keyboards.py` | `tests/bot/test_runner.py` |
| **Exit Countries** (`country`, `singbox`, `vless`, `reality`) | `scripts/hotspot/singbox.py`, `profiles.py` | `telegrambot/handlers/country.py` | `telegrambot/ui/country_keyboards.py` | `tests/hotspot/test_singbox.py` |
| **IPv6 Protection** (`ipv6`, `drop`, `reject`) | `scripts/hotspot/adguard.py` | `telegrambot/handlers/ipv6.py` | `telegrambot/ui/ipv6_keyboards.py` | `tests/hotspot/test_ipv6.py` |
| **Routing & Firewall** (`routing`, `iptables`, `policy`) | `scripts/hotspot/routing.py`, `90-hotspot-vpn-policy` | - | - | `tests/test-vpn-scripts.sh` |
| **Dynamic Emojis / Sticker Pack** (`emoji`, `sticker`, `flag`) | `telegrambot/core/dynamic_emojis.py` | `telegrambot/handlers/status.py` | `telegrambot/ui/dynamic_emojis.py` | `tests/bot/test_dynamic_emojis.py` |
| **Text Router & Dispatch** (`menu`, `router`, `callback`) | - | `telegrambot/handlers/text_router.py` | `telegrambot/ui/main_keyboard.py` | `tests/bot/test_router.py` |
| **Client Devices** (`clients`, `dhcp`, `mac`) | `scripts/hotspot/detection.py` | `telegrambot/handlers/maintenance.py` | - | `tests/hotspot/test_detection.py` |
| **Bot Auth & Config** (`auth`, `token`, `allowed users`) | - | `telegrambot/core/config.py` | - | `tests/bot/test_config.py` |
| **Host CLI Dispatch** (`cli`, `args`, `flags`) | `scripts/hotspot/cli.py` | `telegrambot/core/runner.py` | - | `tests/hotspot/test_runner.py` |


## Architectural Map & Guidelines

### 1. Telegram Bot (`telegrambot/`)
The Telegram Bot is structured as a **Granular Modular Architecture** where each file has a single responsibility and stays within 30–200 lines:

| Package | Purpose | Key Files |
| :--- | :--- | :--- |
| `constants/` | Static metadata | `emojis.py`, `flags.py`, `profiles.py` |
| `core/` | Configuration & execution | `config.py`, `health.py`, `runner.py` |
| `ui/` | Keyboards & button markup | `main_keyboard.py`, `status_keyboards.py`, `vpn_keyboards.py`, `country_keyboards.py`, `adguard_keyboards.py`, `ipv6_keyboards.py` |
| `handlers/` | Telegram commands & callbacks | `common.py`, `status.py`, `vpn.py`, `country.py`, `adguard.py`, `ipv6.py`, `maintenance.py`, `text_router.py` |
| `bot.py` | Main entrypoint | `bot.py` (~120 lines, wires application & handlers) |

### 2. Core Routing & CLI Manager (`scripts/`)
* **Thin CLI Entrypoint**: `scripts/hotspot-manager.py` (~30 lines) is installed to `/usr/local/bin/hotspot-manager.py` by `setup.sh`.
* **Modular Core Package (`scripts/hotspot/`)**:
  * `constants.py`: Constants, TypedDicts, configurations, emojis.
  * `context.py`: Dynamic execution facade resolver.
  * `runner.py`: Subprocess runner, config parsers, docker status.
  * `singbox.py`: Sing-box configuration generator & server switcher.
  * `profiles.py`: Country profiles discovery.
  * `routing.py`: Policy routing & route refreshers.
  * `detection.py`: Interface and connection detector.
  * `vpn.py`: Backend switching and service lifecycles.
  * `adguard.py`: AdGuard DNS and IPv6 protection.
  * `status.py`: Health checks and diagnostic runner.
  * `formatter.py`: Telegram HTML and Terminal formatting.
  * `cli.py`: Argument parser and dispatch router.
* **Container Isolation**: The Telegram Bot runs in Docker and interacts with the host via `nsenter` calling `/usr/local/bin/hotspot-manager.py`. It should never contain a duplicate copy of the script.

### 3. Modular Unit Tests (`tests/`)
* **Telegram Bot Suite (`tests/bot/`)**: Granular tests covering config, health server, runner parsers, UI keyboards, and app creation. Unified runner: `tests/test_telegram_bot.py`.
* **Hotspot Manager Suite (`tests/hotspot/`)**: Granular tests covering runner/docker, VPN lifecycles, connection detection, AdGuard DNS, IPv6 protection, and Sing-box config generation. Unified runner: `tests/test_hotspot_manager.py`.

---

## Testing Commands Reference

### Unit Tests
```bash
# Telegram Bot tests
PYTHONHOME= PYTHONPATH=telegrambot/.venv/lib/python3.11/site-packages:. python3 -m unittest -v tests/test_telegram_bot.py

# Hotspot Manager tests
PYTHONHOME= PYTHONPATH= python3 -m unittest -v tests/test_hotspot_manager.py
```

### Shell & Routing Integration Tests
```bash
# Auto-commit tests
tests/test-auto-commit.sh

# VPN routing regression tests
tests/test-vpn-scripts.sh
```

---

## Architectural Invariants (Do Not Break)
1. **Never copy `hotspot-manager.py` into `telegrambot/`**: Maintain single source of truth in `scripts/`.
2. **Keep files in the Sweet Spot (<300 lines)**: If a handler grows beyond 300 lines, extract helper logic into `core/` or `ui/`.
3. **Keep `sys.path` compatibility in `bot.py`**: Ensures the bot works both standalone inside Docker (`/app`) and within the repository.
4. **Modular Test Suite Isolation**: Root test runner files (`tests/test_telegram_bot.py`, `tests/test_hotspot_manager.py`) must remain thin aggregators (<40 lines). No `unittest.TestCase` subclasses may be defined directly in root runners. All tests must reside in `tests/bot/` and `tests/hotspot/`.

