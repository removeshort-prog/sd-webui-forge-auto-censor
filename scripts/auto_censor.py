"""Forge Neo extension entry point for [自动打码]."""

import sys
from pathlib import Path

extension_root = str(Path(__file__).resolve().parents[1])
if extension_root not in sys.path:
    sys.path.insert(0, extension_root)

from modules import script_callbacks
from forge_auto_censor.ui import create_ui

script_callbacks.on_ui_tabs(create_ui)
