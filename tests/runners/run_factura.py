"""
run_factura.py - Runner de la suite de Factura.

Ejecuta todos los escenarios del feature de Factura usando pytest.
Se puede ejecutar directamente:
    python tests/runners/run_factura.py
    python tests/runners/run_factura.py --headless
    python tests/runners/run_factura.py --smoke
"""
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[2]


def main() -> int:
    args = sys.argv[1:]
    headless = "--headless" in args
    smoke_only = "--smoke" in args

    cmd = [
        sys.executable, "-m", "pytest",
        "tests/step_definitions/factura_steps.py",
        "-m", "factura",
        "--tb=short",
        "-v",
        "-s",
        "--alluredir=allure-results",
    ]

    if headless:
        cmd += ["--headless"]

    if smoke_only:
        cmd += ["-m", "smoke"]

    return subprocess.run(cmd, cwd=str(PROJECT_ROOT)).returncode


if __name__ == "__main__":
    sys.exit(main())
