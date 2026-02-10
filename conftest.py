"""Pytest configuration.

Ensures the repository root is on sys.path so that v1_bca_basic_system and
v2_analytics_modernisation can be imported during test collection.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
