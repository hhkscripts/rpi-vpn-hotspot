#!/usr/bin/env python3
"""
Execution Context Resolver for Hotspot Manager.

Provides dynamic resolution of active module/facade to support standalone CLI runs,
package imports, and unittest mock patching on hotspot_manager seamlessly.
"""

import sys
from typing import Any


class Context:
    """Resolves the active execution facade.

    When tests patch attributes on `hotspot_manager`, calls routed through
    Context.get() immediately reflect those patches.
    """

    @staticmethod
    def get() -> Any:
        if "hotspot_manager" in sys.modules:
            return sys.modules["hotspot_manager"]
        if "hotspot" in sys.modules:
            return sys.modules["hotspot"]
        return sys.modules.get("__main__", sys.modules[__name__])
