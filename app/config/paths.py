"""
paths.py - Gestión centralizada de rutas del framework FACTO 8.

Todas las rutas de output, evidencias y recursos del proyecto
se calculan aquí en función de OUTPUT_DIR (configurable vía .env).

Uso:
    from app.config.paths import FrameworkPaths
    paths = FrameworkPaths("outputs")
    paths.create_all_output_dirs()
    print(paths.screenshots_dir)
"""
from pathlib import Path


class FrameworkPaths:
    """
    Centraliza y calcula todas las rutas del framework.

    Las rutas de output son relativas a OUTPUT_DIR.
    Las rutas de código son absolutas (calculadas desde este archivo).
    """

    # --- Rutas de código fuente (absolutas) ---
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    APP_DIR: Path = PROJECT_ROOT / "app"
    TESTS_DIR: Path = PROJECT_ROOT / "tests"
    TEST_DATA_DIR: Path = PROJECT_ROOT / "tests" / "test_data"
    FEATURES_DIR: Path = PROJECT_ROOT / "tests" / "features"

    def __init__(self, output_dir: str = "outputs"):
        """
        Inicializa las rutas de output.

        Args:
            output_dir: Ruta relativa o absoluta al directorio de salida.
                        Si es relativa, se calcula desde PROJECT_ROOT.
        """
        if Path(output_dir).is_absolute():
            self.output_root = Path(output_dir)
        else:
            self.output_root = self.PROJECT_ROOT / output_dir

        # --- Sub-directorios de output ---
        self.screenshots_dir = self.output_root / "screenshots"
        self.pdf_dir = self.output_root / "pdf"
        self.xml_dir = self.output_root / "xml"
        self.logs_dir = self.output_root / "logs"
        self.json_dir = self.output_root / "json"
        self.zip_dir = self.output_root / "zip"

    def create_all_output_dirs(self) -> None:
        """Crea todos los directorios de output si no existen."""
        for directory in self._all_output_dirs():
            directory.mkdir(parents=True, exist_ok=True)

    def get_execution_dir(self, execution_id: str) -> Path:
        """Retorna el directorio base para una ejecución específica."""
        return self.screenshots_dir / execution_id

    def get_flow_evidence_dir(self, execution_id: str, flow_name: str) -> Path:
        """Retorna el directorio de evidencia para un flujo en una ejecución."""
        path = self.screenshots_dir / execution_id / flow_name
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_test_data_file(self, flow_name: str, filename: str) -> Path:
        """Retorna la ruta a un archivo de test data de un flujo."""
        return self.TEST_DATA_DIR / flow_name / filename

    def _all_output_dirs(self) -> list[Path]:
        return [
            self.output_root,
            self.screenshots_dir,
            self.pdf_dir,
            self.xml_dir,
            self.logs_dir,
            self.json_dir,
            self.zip_dir,
        ]

    def __repr__(self) -> str:
        return f"FrameworkPaths(output_root={self.output_root!r})"
