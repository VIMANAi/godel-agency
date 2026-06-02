# Thin Adapter to godel-core shared package
import sys
from pathlib import Path

import os

def _get_core_path():
    env_path = os.environ.get("GODEL_CORE_PATH")
    if env_path:
        return Path(env_path)
    current = Path(__file__).resolve()
    for parent in current.parents:
        if parent.name == "Agency":
            sibling = parent.parent / "godel-core"
            if sibling.exists():
                return sibling
            break
    return Path("/home/fratfn/Desarrollo/godel-core")

CORE_PATH = _get_core_path()
if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))

from config import *
