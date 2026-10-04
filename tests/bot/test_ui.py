"""Unit tests for bot keyboards and UI builders."""

import unittest

from telegrambot.ui.adguard_keyboards import make_adguard_keyboard
from telegrambot.ui.country_keyboards import (
    make_country_keyboard,
    make_region_keyboard,
)
from telegrambot.ui.ipv6_keyboards import make_ipv6_keyboard
from telegrambot.ui.main_keyboard import MAIN_KEYBOARD
from telegrambot.ui.status_keyboards import make_status_keyboard
from telegrambot.ui.vpn_keyboards import make_switch_vpn_keyboard


class TestTelegramBotUI(unittest.TestCase):
    """Test inline and reply keyboard constructors."""

    def test_main_keyboard_structure(self):
        self.assertIsNotNone(MAIN_KEYBOARD)
        button_texts = [btn.text for row in MAIN_KEYBOARD.keyboard for btn in row]
        self.assertIn("Status", button_texts)
        self.assertIn("Clients", button_texts)
        self.assertIn("Restart", button_texts)
        self.assertIn("Restart VPN", button_texts)
        self.assertIn("Fix", button_texts)
        self.assertIn("Switch VPN", button_texts)
        self.assertIn("IPv6 Mode", button_texts)
        self.assertIn("AdGuard", button_texts)
        self.assertIn("Help", button_texts)

    def test_status_keyboard_sing0_active(self):
        kb = make_status_keyboard("Connected to sing0 (VLESS Reality)")
        callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
        self.assertIn("switch_awg0", callbacks)
        self.assertIn("menu_ipv6", callbacks)
        self.assertIn("menu_adguard", callbacks)
        self.assertIn("refresh_status", callbacks)
        self.assertIn("menu_country", callbacks)

    def test_status_keyboard_awg0_active(self):
        kb = make_status_keyboard("Connected to awg0 (AmneziaWG)")
        callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
        self.assertIn("switch_sing0", callbacks)

    def test_switch_vpn_keyboard(self):
        kb = make_switch_vpn_keyboard()
        callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
        self.assertIn("switch_reality_1", callbacks)
        self.assertIn("switch_reality_2", callbacks)
        self.assertIn("switch_awg0", callbacks)
        self.assertIn("switch_tun0", callbacks)
        self.assertIn("menu_country", callbacks)
        self.assertIn("switch_auto", callbacks)

    def test_adguard_keyboard_toggle(self):
        kb_on = make_adguard_keyboard(adguard_on=True)
        callbacks_on = [
            btn.callback_data for row in kb_on.inline_keyboard for btn in row
        ]
        self.assertIn("adguard_off", callbacks_on)

        kb_off = make_adguard_keyboard(adguard_on=False)
        callbacks_off = [
            btn.callback_data for row in kb_off.inline_keyboard for btn in row
        ]
        self.assertIn("adguard_on", callbacks_off)

    def test_ipv6_keyboard(self):
        kb = make_ipv6_keyboard()
        callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
        self.assertIn("ipv6_drop", callbacks)
        self.assertIn("ipv6_reject", callbacks)
        self.assertIn("ipv6_off", callbacks)

    def test_region_and_country_keyboards(self):
        reg_kb = make_region_keyboard()
        reg_callbacks = [
            btn.callback_data for row in reg_kb.inline_keyboard for btn in row
        ]
        self.assertIn("region_asia", reg_callbacks)
        self.assertIn("country_direct", reg_callbacks)

        country_kb = make_country_keyboard("asia")
        self.assertIsNotNone(country_kb)


if __name__ == "__main__":
    unittest.main()
