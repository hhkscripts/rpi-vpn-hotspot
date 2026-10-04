"""Unit tests for bot config and user authorization."""

import unittest
from unittest.mock import patch

from telegrambot.core.config import check_authorization


class TestTelegramBotConfig(unittest.TestCase):
    """Test configuration and authorization checks."""

    def test_check_authorization_default_deny(self):
        with (
            patch("telegrambot.core.config.ALLOWED_USER_IDS", []),
            patch("telegrambot.core.config.ALLOW_ALL_USERS", False),
        ):
            self.assertFalse(check_authorization(12345))
            self.assertFalse(check_authorization(99999))

    def test_check_authorization_explicit_allow_all(self):
        with (
            patch("telegrambot.core.config.ALLOWED_USER_IDS", []),
            patch("telegrambot.core.config.ALLOW_ALL_USERS", True),
        ):
            self.assertTrue(check_authorization(12345))
            self.assertTrue(check_authorization(99999))

    def test_check_authorization_with_restrictions(self):
        with patch("telegrambot.core.config.ALLOWED_USER_IDS", [111, 222]):
            self.assertTrue(check_authorization(111))
            self.assertTrue(check_authorization(222))
            self.assertFalse(check_authorization(333))


if __name__ == "__main__":
    unittest.main()
