"""Tests for IPv6 leak protection modes."""

import unittest
from unittest.mock import patch

from tests.hotspot import hotspot_manager


class Ipv6ModeTests(unittest.TestCase):
    def test_get_configured_ipv6_mode_defaults_to_reject(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            self.assertEqual(hotspot_manager.get_configured_ipv6_mode(), "reject")

    def test_set_ipv6_mode_rejects_invalid_values(self):
        self.assertFalse(hotspot_manager.set_ipv6_mode("invalid"))

    def test_set_ipv6_mode_valid(self):
        with (
            patch.object(
                hotspot_manager, "update_goodwifi_conf", return_value=True
            ) as upd,
            patch.object(hotspot_manager, "apply_vpn_policy", return_value=True) as pol,
            patch.object(hotspot_manager, "log"),
        ):
            self.assertTrue(hotspot_manager.set_ipv6_mode("reject"))
            upd.assert_called_once_with("IPV6_LEAK_PROTECTION", "reject")
            pol.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
