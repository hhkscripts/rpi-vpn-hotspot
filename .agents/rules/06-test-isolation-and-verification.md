# Modular Test Isolation & Verification Invariants

- **Root Test Runner Purity (<40 Lines)**:
  - Root test runners (`tests/test_telegram_bot.py`, `tests/test_hotspot_manager.py`) are strictly thin aggregators.
  - NEVER declare `unittest.TestCase` classes directly inside root runner files.
  - All test cases MUST reside in modular files under `tests/bot/` and `tests/hotspot/`.
- **Pure Unit Isolation**:
  - Unit tests must mock all system calls (`subprocess.run`, `docker`, network requests).
  - No test may mutate host networking or disk configuration.
- **Mandatory Quality Gate (`analyze.sh`)**:
  - Before finalizing any changes or commits, run `.agents/skills/vpn-codebase-analysis/scripts/analyze.sh` to ensure all 6 gates and all unit tests pass cleanly.
