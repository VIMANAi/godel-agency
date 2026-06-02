# Thin Adapter to global godel-core tests
import sys
from pathlib import Path

CORE_PATH = Path("/home/fratfn/Desarrollo/godel-core")
if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))

import tests.test_sdlc_suite
if __name__ == "__main__":
    tests.test_sdlc_suite.run_tests()
