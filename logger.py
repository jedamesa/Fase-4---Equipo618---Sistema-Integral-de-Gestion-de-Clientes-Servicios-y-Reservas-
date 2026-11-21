"""Configuración del registro de eventos y errores de Software FJ."""

import logging
import sys
from pathlib import Path

# El log se guarda junto al código, sin importar desde dónde se ejecute el programa.
RUTA_LOG = Path(__file__).resolve().parent / "app.log"

_FORMATO = logging.Formatter(
    fmt='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


# BLOQUE 1: Configuración del registro
# Tarea: crear una instancia compartida con formato uniforme que escriba en
# archivo, sin duplicar manejadores al importar el módulo más de una vez.
def configurar_logger():
    """Crea el logger compartido por los módulos de la aplicación.

    Los eventos se agregan a app.log para conservar el historial. La consola
    no recibe logs por defecto para no mezclarlos con los menús; la simulación
    puede activarla con activar_consola().
    """
    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Evita añadir handlers duplicados si más de un módulo importa el logger.
    if not logger.handlers:
        # El modo append conserva eventos de ejecuciones anteriores.
        file_handler = logging.FileHandler(RUTA_LOG, mode='a', encoding='utf-8')
        file_handler.setFormatter(_FORMATO)
        logger.addHandler(file_handler)

    return logger


def activar_consola():
    """Muestra además los logs en pantalla (útil para la simulación)."""
    logger = logging.getLogger("SoftwareFJ")
    if any(
        isinstance(handler, logging.StreamHandler)
        and not isinstance(handler, logging.FileHandler)
        for handler in logger.handlers
    ):
        return
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(_FORMATO)
    logger.addHandler(console_handler)


# BLOQUE 2: Instancia compartida
# Tarea: ofrecer a los demás módulos el mismo logger ya configurado.
log = configurar_logger()
