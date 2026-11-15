"""Entry point for PyInstaller builds (python -m acr does the same)."""
import sys

from acr.gui.app import main

sys.exit(main())
