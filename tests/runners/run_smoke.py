"""
run_smoke.py - Runner del smoke test de todos los módulos.

    python tests/runners/run_smoke.py
    python tests/runners/run_smoke.py --headless
"""
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[2]


def main() -> int:
    args = sys.argv[1:]
    headless = "--headless" in args

    cmd = [
        sys.executable, "-m", "pytest",
        "-m", "smoke",
        "--tb=short", "-v",
        "--alluredir=allure-results",
    ]
    if headless:
        cmd += ["--headless"]

    return subprocess.run(cmd, cwd=str(PROJECT_ROOT)).returncode


if __name__ == "__main__":
    sys.exit(main())
