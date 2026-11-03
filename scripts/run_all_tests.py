"""Run complete automated test suite."""

import pytest
import sys

if __name__ == "__main__":
    code = pytest.main(["tests/", "-v", "--tb=short"])
    sys.exit(code)

