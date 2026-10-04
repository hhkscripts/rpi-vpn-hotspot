"""Backward-compatible test runner for modular telegram bot tests."""

import unittest

from tests.bot.test_app import TestTelegramBotAppCreation
from tests.bot.test_config import TestTelegramBotConfig
from tests.bot.test_health import TestTelegramBotHealthServer
from tests.bot.test_runner import TestTelegramBotRunnerConfigParsers
from tests.bot.test_ui import TestTelegramBotUI

__all__ = [
    "TestTelegramBotConfig",
    "TestTelegramBotUI",
    "TestTelegramBotRunnerConfigParsers",
    "TestTelegramBotHealthServer",
    "TestTelegramBotAppCreation",
]

if __name__ == "__main__":
    unittest.main()
