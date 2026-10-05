# /vpn - Multi-Backend VPN Operations

When invoked with `/vpn [status|switch|country]`:

1. **Status**:
   ```bash
   hotspot --status
   ```
2. **Switch Backend**:
   - Sing-box Reality: `hotspot --switch-vpn sing0`
   - AmneziaWG: `hotspot --switch-vpn awg0`
   - OpenVPN: `hotspot --switch-vpn tun0`
   - Auto-Failover: `hotspot --switch-vpn auto`
3. **Switch Exit Country**:
   ```bash
   hotspot --country <profile_name>
   ```
