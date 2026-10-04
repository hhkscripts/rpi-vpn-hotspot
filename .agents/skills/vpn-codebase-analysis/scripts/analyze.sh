#!/usr/bin/env bash
# ==============================================================================
# Codebase Analysis & Verification Script for VPN & Telegram Bot
# ==============================================================================
set -eo pipefail

REPO_ROOT="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$REPO_ROOT" ]; then
    REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
fi
cd "$REPO_ROOT"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}=====================================================${NC}"
echo -e "${CYAN} 🔍 VPN & Telegram Bot Codebase Analysis Report${NC}"
echo -e "${CYAN}=====================================================${NC}"

FAILURES=0

# 1. Check for Duplicate Files
echo -e "\n${YELLOW}[1/5] Checking Duplicate Files & Hygiene...${NC}"
if [ -f "telegrambot/hotspot-manager.py" ]; then
    echo -e "${RED}❌ FAILED: Duplicate hotspot-manager.py found in telegrambot/!${NC}"
    FAILURES=$((FAILURES + 1))
else
    echo -e "${GREEN}✅ PASSED: No duplicate hotspot-manager.py found.${NC}"
fi

# 2. Syntax & Compilation Check
echo -e "\n${YELLOW}[2/5] Checking Python Syntax & Compilation...${NC}"
PYTHON_ENV="PYTHONHOME= PYTHONPATH=${REPO_ROOT}/telegrambot/.venv/lib/python3.11/site-packages:${REPO_ROOT}"
SYNTAX_ERRORS=0
while IFS= read -r pyfile; do
    if ! env $PYTHON_ENV python3 -m py_compile "$pyfile" 2>/dev/null; then
        echo -e "${RED}❌ Syntax error in: $pyfile${NC}"
        SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
    fi
done < <(find scripts telegrambot tests -name "*.py" -not -path '*/.*' -not -path '*/venv/*')

if [ "$SYNTAX_ERRORS" -eq 0 ]; then
    echo -e "${GREEN}✅ PASSED: All Python files compiled successfully.${NC}"
else
    echo -e "${RED}❌ FAILED: $SYNTAX_ERRORS file(s) have syntax errors.${NC}"
    FAILURES=$((FAILURES + 1))
fi

# 3. File Size & Sweet Spot Architecture Check
echo -e "\n${YELLOW}[3/5] Verifying Sweet Spot Line Counts (<300 lines)...${NC}"
OVERSIZED=0
while IFS= read -r pyfile; do
    LINES=$(wc -l < "$pyfile")
    if [ "$LINES" -gt 300 ]; then
        echo -e "${RED}⚠️  Oversized: $pyfile has $LINES lines (exceeds 300 sweet spot).${NC}"
        OVERSIZED=$((OVERSIZED + 1))
    fi
done < <(find telegrambot scripts tests -name "*.py" -not -path '*/.*' -not -path '*/venv/*')

if [ "$OVERSIZED" -eq 0 ]; then
    echo -e "${GREEN}✅ PASSED: All Telegram Bot, Hotspot script, and test files are strictly in the sweet spot!${NC}"
else
    echo -e "${RED}❌ FAILED: $OVERSIZED file(s) exceed 300 lines.${NC}"
    FAILURES=$((FAILURES + 1))
fi

# 4. Telegram Bot Unit Tests
echo -e "\n${YELLOW}[4/5] Running Telegram Bot Unit Tests...${NC}"
if env $PYTHON_ENV python3 -m unittest -v tests/test_telegram_bot.py; then
    echo -e "${GREEN}✅ PASSED: All Telegram Bot unit tests succeeded.${NC}"
else
    echo -e "${RED}❌ FAILED: Telegram Bot unit tests failed.${NC}"
    FAILURES=$((FAILURES + 1))
fi

# 5. Hotspot Manager & Routing Tests
echo -e "\n${YELLOW}[5/5] Running Hotspot Manager & Script Tests...${NC}"
if env PYTHONHOME= PYTHONPATH= python3 -m unittest -v tests/test_hotspot_manager.py; then
    echo -e "${GREEN}✅ PASSED: All Hotspot Manager unit tests succeeded.${NC}"
else
    echo -e "${RED}❌ FAILED: Hotspot Manager unit tests failed.${NC}"
    FAILURES=$((FAILURES + 1))
fi

echo -e "\n${CYAN}=====================================================${NC}"
if [ "$FAILURES" -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL ANALYSIS CHECKS PASSED! Codebase is healthy.${NC}"
    exit 0
else
    echo -e "${RED}💥 $FAILURES CHECK(S) FAILED! Please inspect issues above.${NC}"
    exit 1
fi
