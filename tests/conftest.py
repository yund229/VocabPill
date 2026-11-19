import sys
from pathlib import Path

# Allow running pytest from the repo root without installing the package.
ROOT = str(Path(__file__).resolve().parent.parent)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
