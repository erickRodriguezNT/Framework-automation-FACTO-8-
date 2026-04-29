"""
run_nota_credito.py - Runner de la suite de Nota de Crédito.

    python tests/runners/run_nota_credito.py
    python tests/runners/run_nota_credito.py --headless
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
        "tests/step_definitions/nota_credito_steps.py",
        "-m", "nota_credito",
        "--tb=short",
        "-v",
        "-s",
        "--alluredir=allure-results",
    ]
    if headless:
        cmd += ["--headless"]

    return subprocess.run(cmd, cwd=str(PROJECT_ROOT)).returncode


if __name__ == "__main__":
    sys.exit(main())
