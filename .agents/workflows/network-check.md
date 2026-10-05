# /network-check - Enterprise Policy Routing & Security Verification

When invoked with `/network-check`:

1. **Verify Policy Routing Rules**:
   ```bash
   ip rule show
   ```
   Confirm presence of:
   - Priority 997: Management subnets -> table main
   - Priority 998: fwmark 0x65 (local_routes) -> table main
   - Priority 999: fwmark 0x64 (vpn_routes) -> table 100
   - Priority 1000: 10.42.0.0/24 -> table 100

2. **Verify Host Route Isolation**:
   ```bash
   ip route show default
   ```
   Confirm default gateway is on `eth0`, NEVER on `sing0`, `awg0`, or `tun0`.

3. **Verify IPv6 Leak Protection**:
   Confirm ip6tables forward policy drops/rejects client forwarding.

4. **Verify Hotspot Status & Active Backend**:
   ```bash
   hotspot --status
   ```
