"""Unit tests for Docker health check HTTP request handler."""

import unittest
from unittest.mock import MagicMock

from telegrambot.core.health import BotHealthHandler, set_bot_ready


class TestTelegramBotHealthServer(unittest.TestCase):
    """Test Docker health check HTTP request handler."""

    def test_health_handler_ok(self):
        set_bot_ready(True)
        handler = BotHealthHandler.__new__(BotHealthHandler)
        handler.path = "/bot-health"
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()
        handler.wfile = MagicMock()

        handler.do_GET()
        handler.send_response.assert_called_with(200)

    def test_health_handler_starting(self):
        set_bot_ready(False)
        handler = BotHealthHandler.__new__(BotHealthHandler)
        handler.path = "/bot-health"
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()
        handler.wfile = MagicMock()

        handler.do_GET()
        handler.send_response.assert_called_with(503)

    def test_health_handler_not_found(self):
        handler = BotHealthHandler.__new__(BotHealthHandler)
        handler.path = "/unknown"
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()
        handler.wfile = MagicMock()

        handler.do_GET()
        handler.send_response.assert_called_with(404)


if __name__ == "__main__":
    unittest.main()
