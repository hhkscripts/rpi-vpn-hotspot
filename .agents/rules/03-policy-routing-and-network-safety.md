# Policy Routing & Network Safety Invariants

- **Zero Host Default Route Hijacking**:
  - NEVER replace the host default gateway (`ip route replace default dev tun0/awg0`).
  - Host traffic must remain on `eth0` (`table main`) to protect local SSH management, Docker networking, and DNS integrity.
- **Enterprise Policy Routing Hierarchy**:
  - `priority 997`: Management subnets (`10.42.0.0/24` to `10.8.0.0/24`, `192.168.100.0/24`, `192.168.1.0/24`) -> `table main`.
  - `priority 998`: `fwmark 0x65` (`local_routes` ipset for Myanmar banking/Binance bypass) -> `table main`.
  - `priority 999`: `fwmark 0x64` (`vpn_routes` ipset for GitHub & selected services) -> `table 100`.
  - `priority 1000`: All other hotspot client traffic (`10.42.0.0/24`) -> `table 100` (VPN).
- **Leak Protection Standards**:
  - IPv6 Leak Protection: Enforce `drop` or `reject` on forwarding rules to prevent IPv6 VPN bypass.
  - DNS Leak Protection: Hotspot clients must query AdGuard Home at `10.42.0.1:53` which routes upstream queries securely over encrypted upstream DNS.
