"""
run_ppd.py - Runner de la suite de CFDI PPD (data-driven desde Excel).

    python tests/runners/run_ppd.py
    python tests/runners/run_ppd.py --headless
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
        "tests/step_definitions/ppd_steps.py",
        "-m", "ppd",
        "--tb=short", "-v", "-s",
        "--alluredir=allure-results",
    ]
    if headless:
        cmd += ["--headless"]

    return subprocess.run(cmd, cwd=str(PROJECT_ROOT)).returncode


if __name__ == "__main__":
    sys.exit(main())
