"""
Hotspot Manager Unit Tests Package.
Provides centralized loaded hotspot_manager module reference for test modules.
"""

import importlib.util
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).parents[2] / "scripts" / "hotspot-manager.py"
SPEC = importlib.util.spec_from_file_location("hotspot_manager", MODULE_PATH)
assert SPEC and SPEC.loader
hotspot_manager = importlib.util.module_from_spec(SPEC)
sys.modules["hotspot_manager"] = hotspot_manager
SPEC.loader.exec_module(hotspot_manager)

__all__ = ["hotspot_manager"]
