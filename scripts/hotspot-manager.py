#!/usr/bin/env python3
"""
Raspberry Pi Hotspot Manager - Smart Monitoring CLI
Thin entrypoint delegating to the modular hotspot package.
"""

import gc
import sys
import time  # noqa: F401
from pathlib import Path

# Ensure library search paths include repository scripts and system install directories
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
for _lib in ["/usr/local/lib/hotspot", "/usr/local/lib"]:
    if _lib not in sys.path and Path(_lib).exists():
        sys.path.append(_lib)

# Ensure this module is registered in sys.modules as hotspot_manager
# so dynamic dispatches and test mocks on hotspot_manager resolve correctly
if "hotspot_manager" not in sys.modules:
    for _obj in gc.get_referrers(globals()):
        if isinstance(_obj, type(sys)) and getattr(_obj, "__name__", "") == __name__:
            sys.modules["hotspot_manager"] = _obj
            break

import hotspot  # noqa: F401, E402
from hotspot import *  # noqa: F401, F403, E402
from hotspot import main  # noqa: E402

if __name__ == "__main__":
    main()
