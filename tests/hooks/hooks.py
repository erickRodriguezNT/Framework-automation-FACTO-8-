"""
hooks.py - Hooks de pytest para setup/teardown y evidencia de fallos.

Provee:
- pytest_runtest_makereport: captura el resultado del test para el fixture
  screenshot_on_failure definido en tests/conftest.py
- attach_screenshot_to_allure: adjunta un screenshot al reporte de Allure
  cuando un test falla

Uso (en tests/conftest.py):
    from tests.hooks.hooks import attach_screenshot_to_allure, pytest_runtest_makereport
"""
from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import pytest


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> None:
    """
    Hook de pytest que captura el resultado del test y lo guarda en el nodo.

    Esto permite que el fixture screenshot_on_failure en conftest.py
    acceda al resultado (passed/failed) después del yield.
    """
    outcome = yield
    report = outcome.get_result()

    # Solo nos interesa la fase de llamada (call), no setup/teardown
    if report.when == "call":
        item._last_report = report  # type: ignore[attr-defined]


def attach_screenshot_to_allure(driver: Any, test_name: str) -> None:
    """
    Toma un screenshot y lo adjunta al reporte de Allure.

    Si Allure no está disponible, guarda el screenshot en el
    directorio de evidencia de fallos.

    Args:
        driver:    Instancia del WebDriver activo.
        test_name: Nombre del test para nombrar el screenshot.
    """
    try:
        import allure
        screenshot = driver.get_screenshot_as_png()
        allure.attach(
            screenshot,
            name=f"FALLO_{test_name}",
            attachment_type=allure.attachment_type.PNG,
        )
    except ImportError:
        # Allure no disponible: guardar en disco
        _save_failure_screenshot_to_disk(driver, test_name)
    except Exception as exc:
        _save_failure_screenshot_to_disk(driver, test_name)


def _save_failure_screenshot_to_disk(driver: Any, test_name: str) -> None:
    """
    Fallback: guarda el screenshot de fallo en outputs/screenshots/failures/

    Args:
        driver:    WebDriver activo.
        test_name: Nombre del test fallido.
    """
    try:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = test_name.replace("/", "_").replace("\\", "_").replace(" ", "_")
        fail_dir = Path("outputs") / "screenshots" / "failures"
        fail_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = fail_dir / f"FALLO_{safe_name}_{timestamp}.png"
        driver.save_screenshot(str(screenshot_path))
    except Exception:
        pass  # Si el driver ya no está disponible, no hacer nada
