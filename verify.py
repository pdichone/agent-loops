"""The verifier: run the tests against a candidate quote.py. Code, not a model: same answer every time.

    python verify.py runs/scratch/quote.py              # the visible tests
    python verify.py runs/scratch/quote.py --hidden     # the held-out tests
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from functools import cache
from pathlib import Path

TASK = Path(__file__).parent / "task"


@dataclass
class Report:
    passed: int
    total: int
    failures: str  # one line per failing test: which test, the cart, what we got vs expected

    @property
    def green(self) -> bool:
        return self.passed == self.total


def _pytest(code: str, tests: str) -> str:
    with tempfile.TemporaryDirectory() as d:
        Path(d, "quote.py").write_text(code)
        shutil.copy(TASK / tests, d)
        try:
            p = subprocess.run(
                [sys.executable, "-m", "pytest", tests, "-q", "-vv", "--tb=no", "-rfE", "-p", "no:cacheprovider"],
                cwd=d, capture_output=True, text=True, timeout=60, env={**os.environ, "COLUMNS": "2000"})
        except subprocess.TimeoutExpired:
            return "TIMEOUT: the tests did not finish in 60 seconds"
    return p.stdout + p.stderr


@cache
def _total(tests: str) -> int:
    """How many tests the file holds (collected against the reference solution)."""
    out = _pytest((Path(__file__).parent / "reference" / "quote.py").read_text(), tests)
    return int(re.search(r"(\d+) passed", out).group(1))


def verify(code: str, hidden: bool = False) -> Report:
    tests = "test_hidden.py" if hidden else "test_visible.py"
    out = _pytest(code, tests)
    passed = re.search(r"(\d+) passed", out)
    lines = [l.removeprefix("FAILED ") for l in out.splitlines() if l.startswith(("FAILED", "ERROR"))]
    if not lines and not passed:  # it didn't even import: show the error
        lines = out.strip().splitlines()[-15:]
    return Report(int(passed.group(1)) if passed else 0, _total(tests), "\n".join(lines)[:6000])


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("--hidden", action="store_true")
    a = p.parse_args()
    r = verify(Path(a.file).read_text(), a.hidden)
    print(r.failures)
    print(f"\n{r.passed}/{r.total} tests pass")
