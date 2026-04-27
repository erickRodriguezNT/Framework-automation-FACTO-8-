"""
run.py - Entrypoint CLI del FACTO 8 Automation Framework.

Permite ejecutar flujos individuales o suites completas desde línea de comandos.

Uso:
    python run.py --flow factura
    python run.py --flow ppd --headless
    python run.py --suite smoke
    python run.py --suite regression
    python run.py --suite full
    python run.py --feature tests/features/factura.feature
    python run.py --dry-run
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

# --- Mapeo de flujos a sus feature files ---
FLOW_FEATURE_MAP = {
    "factura":           "tests/features/factura.feature",
    "nota_credito":      "tests/features/nota_credito.feature",
    "ppd":               "tests/features/ppd.feature",
    "complemento_pago":  "tests/features/complemento_pago.feature",
    "adenda":            "tests/features/adenda.feature",
}

# --- Mapeo de suites a markers de pytest ---
SUITE_MARKER_MAP = {
    "smoke":       "smoke",
    "regression":  "regression",
    "end_to_end":  "end_to_end",
    "dependencias": "dependencias",
    "full":        None,  # None = sin filtro de marker, ejecuta todo
}


def build_pytest_command(args: argparse.Namespace) -> list[str]:
    """Construye el comando pytest según los argumentos recibidos."""
    cmd = [sys.executable, "-m", "pytest"]

    # --- Selección de target ---
    if args.feature:
        if not Path(args.feature).exists():
            print(f"[ERROR] Feature file no encontrado: {args.feature}")
            sys.exit(1)
        cmd.append(args.feature)

    elif args.flow:
        feature_file = FLOW_FEATURE_MAP.get(args.flow)
        if not feature_file:
            print(f"[ERROR] Flujo '{args.flow}' no existe. Opciones: {list(FLOW_FEATURE_MAP.keys())}")
            sys.exit(1)
        cmd.append(feature_file)

    elif args.suite:
        if args.suite not in SUITE_MARKER_MAP:
            print(f"[ERROR] Suite '{args.suite}' no existe. Opciones: {list(SUITE_MARKER_MAP.keys())}")
            sys.exit(1)
        marker = SUITE_MARKER_MAP[args.suite]
        if marker:
            cmd.extend(["-m", marker])
        else:
            cmd.append("tests/")

    else:
        # Por defecto: smoke
        print("[INFO] Sin --flow ni --suite especificado. Ejecutando suite: smoke")
        cmd.extend(["-m", "smoke"])

    # --- Opciones adicionales ---
    if not args.quiet:
        cmd.append("-v")

    if args.headless:
        os.environ["HEADLESS"] = "true"

    if not args.no_allure:
        cmd.append("--alluredir=allure-results")

    if args.dry_run:
        cmd.append("--collect-only")

    return cmd


def main() -> None:
    parser = argparse.ArgumentParser(
        description="FACTO 8 Automation Framework - Runner principal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python run.py --flow factura
  python run.py --flow ppd --headless
  python run.py --suite smoke
  python run.py --suite regression
  python run.py --suite full
  python run.py --feature tests/features/factura.feature
  python run.py --dry-run
        """,
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--flow",
        choices=list(FLOW_FEATURE_MAP.keys()),
        help="Ejecutar un flujo específico por nombre",
    )
    group.add_argument(
        "--suite",
        choices=list(SUITE_MARKER_MAP.keys()),
        help="Ejecutar una suite de tests",
    )
    group.add_argument(
        "--feature",
        type=str,
        help="Ruta directa a un archivo .feature",
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        help="Forzar modo headless (sobreescribe variable HEADLESS del .env)",
    )
    parser.add_argument(
        "--no-allure",
        action="store_true",
        help="Deshabilitar generación de reporte Allure",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo recolectar tests sin ejecutarlos (--collect-only)",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Modo silencioso (menos output)",
    )

    args = parser.parse_args()
    cmd = build_pytest_command(args)

    print(f"\n{'=' * 60}")
    print("  FACTO 8 Automation Framework")
    print(f"{'=' * 60}")
    print(f"  Comando: {' '.join(cmd)}")
    print(f"{'=' * 60}\n")

    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
