# Enterprise Architecture & Component Isolation

- **Decoupled 3-Tier Enterprise Structure**:
  1. *Host Core Manager (`scripts/hotspot/`)*: Pure Python domain logic managing network interfaces, routing tables, and VPN services.
  2. *Firewall & Policy Dispatcher (`configs/90-hotspot-vpn-policy`)*: NetworkManager dispatcher managing kernel ip rules, iptables, and ipsets.
  3. *Isolated Telegram Bot Interface (`telegrambot/`)*: Dockerized Telegram management bot following Granular Modular Architecture (<300 lines/file).
- **Strict Container Isolation via `nsenter`**:
  - The Telegram Bot runs inside a Docker container.
  - To interact with the host system, the bot container delegates through `nsenter` to execute `/usr/local/bin/hotspot-manager.py` in the host's mount and PID namespaces.
  - **Single Source of Truth**: NEVER duplicate `hotspot-manager.py` or script logic into `telegrambot/`.
