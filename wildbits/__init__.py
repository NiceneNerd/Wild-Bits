import os
from pathlib import Path

EXEC_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
DATA_DIR = Path.home() / ".wildbits"
