# /test - Run Modular Unit Tests

When invoked with `/test [bot|hotspot|all]`:

1. **Telegram Bot Tests**:
   ```bash
   PYTHONHOME= PYTHONPATH=telegrambot/.venv/lib/python3.11/site-packages:. python3 -m unittest -v tests/test_telegram_bot.py
   ```
2. **Hotspot Manager Tests**:
   ```bash
   PYTHONHOME= PYTHONPATH= python3 -m unittest -v tests/test_hotspot_manager.py
   ```
3. **Integration & Shell Regression Tests**:
   ```bash
   bash tests/test-auto-commit.sh
   bash tests/test-vpn-scripts.sh
   ```
