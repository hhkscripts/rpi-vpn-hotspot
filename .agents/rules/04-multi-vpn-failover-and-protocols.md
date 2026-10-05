# Multi-Backend VPN Failover & Protocol Hierarchy

- **Supported Protocols & Backend Precedence**:
  1. *Sing-box Reality (`sing0`)*: Highest priority. VLESS-Reality protocol with TLS masquerading for robust DPI circumvention.
  2. *AmneziaWG (`awg0`)*: Header-obfuscated WireGuard (`Jc`, `Jmin`, `Jmax`, `S1`, `S2`, `H1`-`H4`) for DPI bypass.
  3. *WireGuard (`wg0`)*: Standard low-latency kernel tunnel.
  4. *OpenVPN (`tun0`)*: NetworkManager managed tunnel with `--replay-window 8192 60` diversion wrapper.
- **Table = off Requirement**:
  - In WireGuard and AmneziaWG configs (`/etc/wireguard/wg0.conf`, `/etc/amnezia/amneziawg/awg0.conf`), `Table = off` is strictly required to prevent hijacking Pi default routes.
- **MTU Standards**:
  - WireGuard / AmneziaWG: MTU 1280.
  - OpenVPN: MTU 1400.
