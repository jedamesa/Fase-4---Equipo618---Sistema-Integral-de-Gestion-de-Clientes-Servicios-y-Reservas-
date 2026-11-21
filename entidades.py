"""Entidades generales y datos de los clientes del sistema Software FJ."""

from abc import ABC, abstractmethod
from datetime import datetime
import re
from excepciones import ClienteError


# BLOQUE 1: Entidad abstracta común
# Tarea: establecer los datos y operaciones que comparten las entidades
# del dominio. Las clases concretas implementan sus propias validaciones
# y la forma de entregar su información.
class EntidadBase(ABC):
    """Define los atributos y operaciones comunes de una entidad del dominio."""

    def __init__(self, id_entidad: str):
        """Guarda el identificador interno y la fecha de creación."""
        self._id_entidad = id_entidad
        self._fecha_creacion = datetime.now()

    @abstractmethod
    def validar(self) -> bool:
        """Valida las reglas de negocio concretas de la entidad."""
        pass

    @abstractmethod
    def obtener_informacion(self) -> dict:
        """Devuelve los datos de la entidad que usa el resto del sistema."""
        pass


# BLOQUE 2: Cliente y sus reglas de validación
# Tarea: representar la identidad del cliente, exponer sus datos controlados
# y verificar el nombre y el formato del correo antes del registro.
class Cliente(EntidadBase):
    """Representa al cliente identificado por un nombre y un correo único.

    El ID es interno para relacionar reservas. El usuario puede iniciar sesión
    con el nombre o con el correo electrónico.
    """

    _PATRON_CORREO = re.compile(
        r"[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+"
        r"(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*@"
        r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
        r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+"
    )

    # El patrón comprueba la estructura sintáctica; no verifica la existencia
    # real del buzón ni su disponibilidad para recibir mensajes.

    def __init__(self, id_cliente: str, nombre: str, correo: str):
        """Crea un cliente; las reglas del nombre y correo se revisan en validar."""
        super().__init__(id_cliente)
        if not isinstance(nombre, str):
            raise ClienteError("El nombre del cliente debe ser texto.")
        if not isinstance(correo, str):
            raise ClienteError("El correo electrónico debe ser texto.")
        self._nombre = " ".join(nombre.split())  # sin espacios repetidos
        self._correo = correo.strip()

    @property
    def nombre(self) -> str:
        """Nombre público del cliente, utilizado para mostrarlo y buscarlo."""
        return self._nombre

    @property
    def correo(self) -> str:
        """Correo público del cliente, utilizado para iniciar sesión."""
        return self._correo

    @property
    def id_cliente(self) -> str:
        """Identificador interno del cliente, usado para enlazar sus reservas."""
        return self._id_entidad

    @staticmethod
    def correo_tiene_formato_valido(correo: str) -> bool:
        """Indica si el texto parece un correo convencional con dominio.

        Esta comprobación sencilla es útil para la interfaz y el dominio. No
        verifica que el buzón exista ni que se pueda recibir correo en él.
        """
        if not isinstance(correo, str) or len(correo) > 254:
            return False
        parte_local, separador, _dominio = correo.partition("@")
        return (
            bool(separador)
            and len(parte_local) <= 64
            and Cliente._PATRON_CORREO.fullmatch(correo) is not None
        )

    def validar(self) -> bool:
        """Comprueba que nombre y correo cumplan las reglas de registro.

        El nombre acepta letras y espacios, con hasta 15 letras sin contar
        espacios. El correo debe tener una forma habitual de dirección
        local@dominio.extensión y respetar los límites de longitud.
        """
        if not self._nombre:
            raise ClienteError("El nombre del cliente no puede estar vacío.")

        if not all(c.isalpha() or c.isspace() for c in self._nombre):
            raise ClienteError(
                "El nombre contiene caracteres inválidos. "
                "Solo se permiten letras y espacios."
            )

        letras_reales = self._nombre.replace(" ", "")
        if len(letras_reales) > 15:
            raise ClienteError(
                f"El nombre excede las 15 letras permitidas "
                f"(tiene {len(letras_reales)})."
            )

        if not self.correo_tiene_formato_valido(self._correo):
            raise ClienteError(
                "El correo no tiene un formato válido. "
                "Use un formato como nombre@dominio.com."
            )

        return True

    def obtener_informacion(self) -> dict:
        """Devuelve una copia de los datos del cliente para mostrar o procesar."""
        return {
            "id_cliente": self._id_entidad,
            "nombre": self._nombre,
            "correo": self._correo,
            "registrado_en": self._fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')
        }