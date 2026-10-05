# /analyze - Full Enterprise Codebase Analysis

When invoked with `/analyze`:

1. **Run Full Analysis Suite**:
   Execute the automated verification script:
   ```bash
   bash .agents/skills/vpn-codebase-analysis/scripts/analyze.sh
   ```
2. **Quality Gates Verified**:
   - Gate 1: No duplicate `hotspot-manager.py` in `telegrambot/`.
   - Gate 2: Zero Python syntax and compilation errors.
   - Gate 3: Sweet Spot file sizing (<300 lines per file).
   - Gate 4: Modular test runner purity (<40 lines, no embedded TestCases in root runners).
   - Gate 5: Telegram Bot unit tests (32 tests).
   - Gate 6: Hotspot Manager unit tests (30 tests).
3. **Report Status**:
   Confirm that all 6 gates and all 62 unit tests passed cleanly.
