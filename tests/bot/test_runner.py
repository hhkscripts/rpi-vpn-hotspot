"""Unit tests for config state inspection and runner helpers."""

import unittest
from unittest.mock import mock_open, patch

from telegrambot.core.runner import (
    get_current_adguard_state,
    get_current_ipv6_mode,
    get_current_unlimited_country,
)


class TestTelegramBotRunnerConfigParsers(unittest.TestCase):
    """Test reading configurations from goodwifi.conf."""

    def test_get_current_unlimited_country(self):
        with patch("os.path.exists", return_value=True):
            with patch(
                "builtins.open",
                mock_open(read_data='UNLIMITED_COUNTRY="sg"\n'),
            ):
                res = get_current_unlimited_country()
                self.assertEqual(res, "sg")

    def test_get_current_ipv6_mode(self):
        with patch("os.path.exists", return_value=True):
            with patch(
                "builtins.open",
                mock_open(read_data='IPV6_LEAK_PROTECTION="reject"\n'),
            ):
                res = get_current_ipv6_mode()
                self.assertEqual(res, "reject")

    def test_get_current_adguard_state(self):
        with patch("os.path.exists", return_value=True):
            with patch(
                "builtins.open",
                mock_open(read_data='ADGUARD_ENABLED="false"\n'),
            ):
                res = get_current_adguard_state()
                self.assertFalse(res)


if __name__ == "__main__":
    unittest.main()
