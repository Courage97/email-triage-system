# pathfix.py
# Drop this file in the project root.
# Import it as the FIRST line in any file that has cross-package imports.
# Usage: import pathfix  # noqa

import sys
import os

_root = os.path.dirname(os.path.abspath(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)