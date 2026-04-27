"""
run_complemento_pago.py - Runner de la suite de Complemento de Pago.

    python tests/runners/run_complemento_pago.py
    python tests/runners/run_complemento_pago.py --headless
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
        "tests/features/complemento_pago.feature",
        "--tb=short", "-v",
        "--alluredir=allure-results",
    ]
    if headless:
        cmd += ["--headless"]

    return subprocess.run(cmd, cwd=str(PROJECT_ROOT)).returncode


if __name__ == "__main__":
    sys.exit(main())
