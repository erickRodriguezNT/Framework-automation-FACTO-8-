"""
retry.py - Decorador de reintentos para el framework FACTO 8.

Usa tenacity para lógica robusta de reintentos con backoff configurable.
Útil para operaciones UI inestables o condiciones de carrera.

Uso:
    from app.utils.retry import retry_on_failure

    @retry_on_failure(attempts=3, delay=1.0)
    def click_boton_inestable():
        page.click(LOCATOR_BOTON)

    @retry_on_failure(attempts=5, delay=2.0, exponential=True)
    def operacion_con_backoff():
        page.wait_for_element(LOCATOR_RESULTADO)
"""
import functools
from typing import Callable, Type

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    wait_fixed,
)

from app.utils.logger import get_logger

logger = get_logger(__name__)


def retry_on_failure(
    attempts: int = 3,
    delay: float = 1.0,
    exceptions: tuple = (Exception,),
    exponential: bool = False,
) -> Callable:
    """
    Decorador que reintenta una función cuando lanza una excepción.

    Args:
        attempts:    Número máximo de intentos (incluyendo el primero).
        delay:       Segundos entre intentos (fijo) o base si exponential=True.
        exceptions:  Tupla de tipos de excepción que disparan el reintento.
                     Por defecto cualquier Exception.
        exponential: Si True, usa backoff exponencial (delay * 2^n).

    Returns:
        Decorador que envuelve la función con lógica de reintento.
    """
    wait_strategy = (
        wait_exponential(multiplier=delay, min=delay, max=delay * 10)
        if exponential
        else wait_fixed(delay)
    )

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retrying_func = retry(
                stop=stop_after_attempt(attempts),
                wait=wait_strategy,
                retry=retry_if_exception_type(exceptions),
                reraise=True,
            )(func)
            return retrying_func(*args, **kwargs)

        return wrapper

    return decorator


def retry_click(attempts: int = 3, delay: float = 0.5) -> Callable:
    """
    Decorador especializado para reintentar clicks de Selenium.

    Captura ElementClickInterceptedException y StaleElementReferenceException.

    Args:
        attempts: Número máximo de intentos.
        delay:    Segundos entre intentos.
    """
    from selenium.common.exceptions import (
        ElementClickInterceptedException,
        StaleElementReferenceException,
    )
    return retry_on_failure(
        attempts=attempts,
        delay=delay,
        exceptions=(ElementClickInterceptedException, StaleElementReferenceException),
    )
