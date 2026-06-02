# Thin Adapter to godel-core shared package
import sys
from pathlib import Path

CORE_PATH = Path("/home/fratfn/Desarrollo/godel-core")
if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))

from config.skills_composer import *
