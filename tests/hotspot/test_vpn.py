"""Tests for VPN restarts, routing policy apply, and backend switches."""

import unittest
from unittest.mock import patch

from tests.hotspot import hotspot_manager


class RestartVpnTests(unittest.TestCase):
    def test_retries_activation_before_applying_policy(self):
        up_attempts = 0

        def fake_run_args(cmd, timeout=30):
            nonlocal up_attempts
            if cmd[:4] == ["sudo", "nmcli", "connection", "up"]:
                up_attempts += 1
                if up_attempts == 1:
                    return False, "", "temporary timeout"
            return True, "", ""

        with (
            patch.object(
                hotspot_manager, "get_configured_backend", return_value="tun0"
            ),
            patch.object(hotspot_manager, "check_vpn", return_value=False),
            patch.object(hotspot_manager, "run_args", side_effect=fake_run_args),
            patch.object(hotspot_manager, "wait_for_interface", return_value=True),
            patch.object(
                hotspot_manager, "apply_vpn_policy", return_value=True
            ) as policy,
            patch.object(hotspot_manager, "refresh_github_routes") as refresh,
            patch.object(hotspot_manager.time, "sleep"),
            patch.object(hotspot_manager, "log"),
        ):
            self.assertTrue(hotspot_manager.restart_vpn())

        self.assertEqual(up_attempts, 2)
        policy.assert_called_once_with()
        refresh.assert_called_once_with()

    def test_github_refresh_allows_sufficient_runtime(self):
        with (
            patch.object(hotspot_manager, "run_args") as run,
            patch.object(hotspot_manager, "GITHUB_ROUTE_SCRIPT", "/route-refresh"),
        ):
            run.side_effect = [(True, "", ""), (True, "", "")]
            hotspot_manager.refresh_github_routes()

        self.assertEqual(run.call_args_list[1].kwargs["timeout"], 120)


class SingboxBackendTests(unittest.TestCase):
    def test_get_active_vpn_interface_sing0(self):
        with patch.object(
            hotspot_manager,
            "run_args",
            return_value=(True, "default dev sing0 proto static scope link\n", ""),
        ):
            iface, name = hotspot_manager.get_active_vpn_interface()
            self.assertEqual(iface, "sing0")
            self.assertEqual(name, "VLESS")

    def test_switch_vpn_sing0(self):
        with (
            patch.object(hotspot_manager, "update_goodwifi_conf", return_value=True),
            patch.object(
                hotspot_manager, "get_vpn_connection_name", return_value="goodwifi-vpn"
            ),
            patch.object(hotspot_manager, "run_args", return_value=(True, "", "")),
            patch.object(hotspot_manager, "wait_for_interface", return_value=True),
            patch.object(
                hotspot_manager, "apply_vpn_policy", return_value=True
            ) as apply_pol,
            patch.object(hotspot_manager, "refresh_github_routes"),
            patch.object(hotspot_manager, "log"),
        ):
            self.assertTrue(hotspot_manager.switch_vpn("sing0"))
            apply_pol.assert_called_once_with("sing0")


if __name__ == "__main__":
    unittest.main()
