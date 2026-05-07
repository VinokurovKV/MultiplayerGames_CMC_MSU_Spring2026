"""Sphinx configuration."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

project = "multiplayer_games_CMC2026"
author = "multiplayer_games_CMC2026 contributors"

extensions = ["sphinx.ext.autodoc"]
templates_path = []
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
language = "ru"
html_theme = "alabaster"
html_static_path = []
