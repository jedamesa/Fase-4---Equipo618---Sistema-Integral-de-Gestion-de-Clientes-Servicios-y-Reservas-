"""Excepciones de dominio utilizadas para comunicar errores del sistema."""


# BLOQUE 1: Excepción base
# Tarea: conservar el mensaje y el origen del error en un formato común para
# que la interfaz pueda mostrarlo y el logger pueda registrarlo.
class ErrorSoftwareFJ(Exception):
    """Clase base principal para todas las excepciones de Software FJ."""

    def __init__(self, mensaje: str, origen: str = "SISTEMA"):
        self.mensaje = mensaje
        self.origen = origen
        super().__init__(f"[{self.origen}] - {self.mensaje}")


# BLOQUE 2: Errores específicos del dominio
# Tarea: distinguir los fallos por área para permitir capturas específicas
# o una captura general de ErrorSoftwareFJ.
class ClienteError(ErrorSoftwareFJ):
    """Excepción para errores de validación, formato y registro de clientes."""

    pass


class ServicioError(ErrorSoftwareFJ):
    """Excepción para parámetros inválidos al configurar un servicio."""

    pass


class CalculoCostoError(ErrorSoftwareFJ):
    """Excepción para fallos en cálculos financieros, tarifas o tiempos inválidos."""

    pass


class DisponibilidadError(ErrorSoftwareFJ):
    """Excepción lanzada cuando no hay unidades libres en el pool de equipos."""

    pass


class ReservaError(ErrorSoftwareFJ):
    """Excepción para fallos en las transacciones y ciclo de vida de las reservas."""

    pass