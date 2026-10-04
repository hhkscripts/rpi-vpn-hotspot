"""Unit tests for bot application creation and handler registration."""

import unittest
from unittest.mock import patch


class TestTelegramBotAppCreation(unittest.TestCase):
    """Test building application and registering handlers."""

    def test_create_application(self):
        with patch("telegrambot.bot.BOT_TOKEN", "123456:FAKE_TOKEN_FOR_TESTING"):
            from telegrambot.bot import create_application

            app = create_application()
            self.assertIsNotNone(app)
            # Verify handlers are registered
            handlers_count = sum(len(handlers) for handlers in app.handlers.values())
            self.assertGreater(handlers_count, 15)


if __name__ == "__main__":
    unittest.main()
