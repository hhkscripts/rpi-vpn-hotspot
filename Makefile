SHELL := /bin/bash
.PHONY: analyze test test-bot test-hotspot check status help

help:
	@echo "GoodWifi & Telegram Bot Enterprise Makefile"
	@echo ""
	@echo "Available commands:"
	@echo "  make analyze       - Run all 6 codebase analysis gates & unit tests"
	@echo "  make test          - Run full modular unit test suites"
	@echo "  make test-bot      - Run Telegram Bot unit tests (32 tests)"
	@echo "  make test-hotspot  - Run Hotspot Manager unit tests (30 tests)"
	@echo "  make check         - Check Python syntax and Sweet Spot file limits (<300 lines)"
	@echo "  make status        - Show host hotspot status"

analyze:
	@bash .agents/skills/vpn-codebase-analysis/scripts/analyze.sh

test: test-bot test-hotspot

test-bot:
	@env PYTHONHOME="" PYTHONPATH="telegrambot/.venv/lib/python3.11/site-packages:." python3 -m unittest -v tests/test_telegram_bot.py

test-hotspot:
	@env PYTHONHOME="" PYTHONPATH="" python3 -m unittest -v tests/test_hotspot_manager.py

check:
	@echo "Checking Sweet Spot line limits (<300 lines)..."
	@OVERSIZED=0; \
	while IFS= read -r pyfile; do \
		LINES=$$(wc -l < "$$pyfile"); \
		if [ "$$LINES" -gt 300 ]; then \
			echo "⚠️  Oversized: $$pyfile has $$LINES lines"; \
			OVERSIZED=$$((OVERSIZED + 1)); \
		fi; \
	done < <(find telegrambot scripts tests -name "*.py" -not -path '*/.*' -not -path '*/venv/*'); \
	if [ "$$OVERSIZED" -eq 0 ]; then \
		echo "✓ All Python files are in the sweet spot (<300 lines)."; \
	else \
		echo "✖ $$OVERSIZED file(s) exceed 300 lines."; \
		exit 1; \
	fi

status:
	@if command -v hotspot >/dev/null 2>&1; then \
		hotspot --status; \
	elif [ -f /usr/local/bin/hotspot-manager.py ]; then \
		python3 /usr/local/bin/hotspot-manager.py --status; \
	else \
		python3 scripts/hotspot-manager.py --status; \
	fi
