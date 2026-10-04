"""Tests for NetworkManager VPN connection auto-detection."""

import unittest
from unittest.mock import patch

from tests.hotspot import hotspot_manager


class VpnConnectionDetectionTests(unittest.TestCase):
    def test_auto_detects_vpn_connection(self):
        nmcli_output = "eth0:802-3-ethernet\nmy-custom-vpn:vpn\n"
        with (
            patch.dict(hotspot_manager.CONFIG, {"vpn_name": ""}),
            patch.object(
                hotspot_manager,
                "run_args",
                side_effect=[
                    (True, nmcli_output, ""),
                    (False, "", ""),
                ],
            ),
        ):
            self.assertEqual(hotspot_manager.get_vpn_connection_name(), "my-custom-vpn")

    def test_uses_explicit_configured_vpn_connection(self):
        nmcli_output = "eth0:802-3-ethernet\ncustom-vpn:vpn\n"
        with (
            patch.dict(hotspot_manager.CONFIG, {"vpn_name": "custom-vpn"}),
            patch.object(
                hotspot_manager,
                "run_args",
                return_value=(True, nmcli_output, ""),
            ),
        ):
            self.assertEqual(hotspot_manager.get_vpn_connection_name(), "custom-vpn")

    def test_active_vpn_interface_custom_table(self):
        with (
            patch.dict(hotspot_manager.CONFIG, {"routing_table": 200}),
            patch.object(
                hotspot_manager,
                "run_args",
                return_value=(True, "default dev sing0 proto static scope link", ""),
            ) as mock_run,
        ):
            iface, name = hotspot_manager.get_active_vpn_interface()
            self.assertEqual(iface, "sing0")
            mock_run.assert_called_with(["ip", "route", "show", "table", "200"])

    def test_check_vpn_external_ip_custom_services(self):
        with (
            patch.dict("os.environ", {"IP_ECHO_SERVICES": "https://custom.ip.me"}),
            patch.object(
                hotspot_manager,
                "get_active_vpn_interface",
                return_value=("wg0", "WireGuard"),
            ),
            patch.object(
                hotspot_manager,
                "run_args",
                return_value=(True, "1.2.3.4\n", ""),
            ) as mock_run,
        ):
            ok, ip = hotspot_manager.check_vpn_external_ip()
            self.assertTrue(ok)
            self.assertEqual(ip, "1.2.3.4")
            call_args = mock_run.call_args[0][0]
            self.assertIn("https://custom.ip.me", call_args)


if __name__ == "__main__":
    unittest.main()
