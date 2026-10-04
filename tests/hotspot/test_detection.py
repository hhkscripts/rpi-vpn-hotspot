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


if __name__ == "__main__":
    unittest.main()
