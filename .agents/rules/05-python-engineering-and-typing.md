# Python Engineering, Subprocess Safety & Typing Standards

- **Strict Type Annotations & Data Structures**:
  - Leverage `TypedDict` and type annotations across core packages (`scripts/hotspot/constants.py`).
  - Pass Pyright static type analysis (`pyrightconfig.json`).
- **Subprocess Execution Safety**:
  - NEVER execute unconstrained shell subprocesses without timeouts.
  - Always specify explicit timeouts (e.g. `timeout=5`, `timeout=15`).
  - Gracefully catch `subprocess.TimeoutExpired` and `subprocess.CalledProcessError`.
  - Prefer argument arrays over `shell=True` to prevent command injection.
- **Idempotency & Clean State**:
  - All configuration generation (`generate_singbox_config`, `set_adguard_state`, etc.) must be idempotent.
  - Temporary files must be safely written and cleaned up.
