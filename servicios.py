"""Servicios de Software FJ, sus reglas, costos e inventario en memoria."""

from abc import ABC, abstractmethod
from typing import overload

from entidades import EntidadBase
from excepciones import (
    CalculoCostoError,
    DisponibilidadError,
    ReservaError,
    ServicioError,
)


# BLOQUE 1: Validación común de duración
# Tarea: aplicar un control compartido de tipo y límites antes de calcular
# el costo de cualquier servicio con duración.
def _validar_duracion_entera(
    duracion: int, maximo: int, descripcion: str
) -> None:
    """Rechaza duraciones que no sean enteros positivos dentro del límite."""
    if not isinstance(duracion, int) or isinstance(duracion, bool):
        raise CalculoCostoError(
            f"La duración {descripcion} debe ser un número entero."
        )
    if duracion < 1:
        raise CalculoCostoError(f"La duración {descripcion} debe ser de al menos 1.")
    if duracion > maximo:
        raise CalculoCostoError(
            f"La duración {descripcion} no puede superar {maximo}."
        )


# BLOQUE 2: Servicio abstracto
# Tarea: definir los datos compartidos por los servicios concretos y exigir
# que cada uno implemente el cálculo de su costo.
class Servicio(EntidadBase, ABC):
    """Base abstracta de servicios con nombre y tarifa de referencia."""

    def __init__(self, id_servicio: str, nombre_servicio: str, tarifa_base: float):
        """Inicializa los datos comunes heredados por cada servicio concreto."""
        super().__init__(id_servicio)
        self._nombre_servicio = nombre_servicio
        self._tarifa_base = tarifa_base

    @abstractmethod
    def calcular_costo(self, duracion: int) -> float:
        """Calcula el costo siguiendo las reglas del servicio concreto."""
        pass

    # Los servicios con inventario (salas, equipos) sobrescriben estos métodos.
    # Los demás (asesorías) heredan este comportamiento vacío, así el gestor
    # no necesita conocer cada tipo de servicio.
    def asignar_unidad(self):
        """Asigna una unidad del inventario; por defecto no hay inventario."""
        return None

    def liberar_unidad(self) -> None:
        """Devuelve la unidad al inventario; por defecto no hace nada."""
        return None


# BLOQUE 3: Reserva de salas
# Tarea: validar las condiciones de la sala, calcular tarifa y adicionales,
# y administrar la asignación y liberación de una sala numerada.
class ReservaSalas(Servicio):
    """Reserva salas numeradas y calcula tarifa, proyector y catering."""

    salas_disponibles = [f"Sala {numero:02d}" for numero in range(1, 100)]

    def __init__(
        self,
        id_servicio: str,
        capacidad: int,
        proyector: bool = False,
        personas_catering: int = 0,
    ):
        """Guarda capacidad y opciones solicitadas antes de asignar una sala."""
        super().__init__(id_servicio, "Reserva de Sala de Conferencias", 40000.0)
        self._capacidad = capacidad
        self._proyector = proyector
        self._personas_catering = personas_catering
        self._sala_asignada = None
        self._ultima_sala = None  # se conserva para mostrar reservas canceladas

    def validar(self) -> bool:
        """Valida capacidad, opción de proyector y cantidad de catering."""
        if not isinstance(self._capacidad, int) or isinstance(self._capacidad, bool):
            raise ServicioError("La capacidad de la sala debe ser un número entero.")
        if not 1 <= self._capacidad <= 25:
            raise ServicioError(
                "La capacidad de la sala debe estar entre 1 y 25 personas."
            )
        if not isinstance(self._proyector, bool):
            raise ServicioError("La opción de proyector debe ser Sí o No.")
        if (
            not isinstance(self._personas_catering, int)
            or isinstance(self._personas_catering, bool)
        ):
            raise ServicioError(
                "Las personas para catering deben ser un número entero."
            )
        if not 0 <= self._personas_catering <= self._capacidad:
            raise ServicioError(
                "Las personas para catering deben estar entre 0 y la capacidad "
                "de la sala."
            )
        return True

    @overload
    def calcular_costo(self, duracion: int) -> float: ...

    @overload
    def calcular_costo(
        self, duracion: int, proyector: bool
    ) -> float: ...

    @overload
    def calcular_costo(
        self,
        duracion: int,
        proyector: bool,
        personas_catering: int,
    ) -> float: ...

    def calcular_costo(
        self,
        duracion: int,
        proyector: bool | None = None,
        personas_catering: int | None = None,
    ) -> float:
        """Calcula horas y extras; argumentos omitidos usan la configuración."""
        _validar_duracion_entera(duracion, 24, "en horas")
        self.validar()
        incluir_proyector = (
            self._proyector if proyector is None else proyector
        )
        cantidad_catering = (
            self._personas_catering
            if personas_catering is None
            else personas_catering
        )
        if not isinstance(incluir_proyector, bool):
            raise CalculoCostoError("La opción de proyector debe ser Sí o No.")
        if (
            not isinstance(cantidad_catering, int)
            or isinstance(cantidad_catering, bool)
            or not 0 <= cantidad_catering <= self._capacidad
        ):
            raise CalculoCostoError(
                "Las personas para catering deben estar entre 0 y la capacidad "
                "de la sala."
            )

        total = self._tarifa_base * duracion
        if incluir_proyector:
            total += 25000
        return total + 15000 * cantidad_catering

    def asignar_unidad(self) -> str:
        """Asigna la sala de menor número disponible."""
        if self._sala_asignada is not None:
            raise ReservaError(
                "Este servicio ya tiene una sala asignada a otra reserva."
            )
        if not self.salas_disponibles:
            raise DisponibilidadError(
                "No hay salas disponibles en el inventario (01-99)."
            )
        self._sala_asignada = self.salas_disponibles.pop(0)
        return self._sala_asignada

    def liberar_unidad(self) -> None:
        """Devuelve la sala al inventario y restablece el orden numérico."""
        if self._sala_asignada is not None:
            self._ultima_sala = self._sala_asignada
            self.salas_disponibles.append(self._sala_asignada)
            self.salas_disponibles.sort(
                key=lambda sala: int(sala.split()[-1])
            )
            self._sala_asignada = None

    @classmethod
    def reiniciar_inventario(cls) -> None:
        """Restablece las salas 01-99 (el inventario es compartido por clase)."""
        cls.salas_disponibles = [f"Sala {numero:02d}" for numero in range(1, 100)]

    def obtener_informacion(self) -> dict:
        """Devuelve los detalles que usa el panel de reservas."""
        return {
            "id": self._id_entidad,
            "servicio": self._nombre_servicio,
            "sala": self._sala_asignada or self._ultima_sala,
            "capacidad": self._capacidad,
            "proyector": self._proyector,
            "personas_catering": self._personas_catering,
        }


# BLOQUE 4: Alquiler de equipos
# Tarea: aplicar tarifas por tipo y duración, y mantener inventarios
# independientes para laptops, cámaras y equipos de sonido.
class AlquilerEquipos(Servicio):
    """Alquiler con inventario independiente para cada clase de equipo."""

    pool_unidades = {
        nombre: [f"{nombre} {numero:02d}" for numero in range(1, 100)]
        for nombre in ("Laptop", "Cámara", "Sonido")
    }
    tarifas_por_equipo = {
        "laptop": ("Laptop", 50000.0),
        "camara": ("Cámara", 70000.0),
        "cámara": ("Cámara", 70000.0),
        "sonido": ("Sonido", 60000.0),
    }

    def __init__(self, id_servicio: str, tipo_equipo: str):
        """Normaliza el tipo solicitado y guarda su tarifa diaria."""
        if not isinstance(tipo_equipo, str):
            raise ServicioError("El tipo de equipo debe indicarse como texto.")
        equipo_normalizado = tipo_equipo.strip().casefold()
        equipo, tarifa = self.tarifas_por_equipo.get(
            equipo_normalizado, (tipo_equipo.strip(), 0.0)
        )
        super().__init__(id_servicio, f"Alquiler de {equipo}", tarifa)
        self._tipo_equipo = equipo
        self._unidad_asignada = None
        self._ultima_unidad = None  # se conserva para mostrar reservas canceladas

    def validar(self) -> bool:
        """Acepta únicamente laptop, cámara o sonido."""
        if self._tipo_equipo.casefold() not in ("laptop", "cámara", "sonido"):
            raise ServicioError("El equipo debe ser Laptop, Cámara o Sonido.")
        return True

    def asignar_unidad(self) -> str:
        """Asigna la unidad de menor número del tipo solicitado."""
        if self._unidad_asignada is not None:
            raise ReservaError(
                "Este servicio ya tiene una unidad asignada a otra reserva."
            )
        unidades_disponibles = self.pool_unidades[self._tipo_equipo]
        if not unidades_disponibles:
            raise DisponibilidadError(
                f"No hay unidades disponibles de {self._tipo_equipo} (01-99)."
            )
        self._unidad_asignada = unidades_disponibles.pop(0)
        return self._unidad_asignada

    def liberar_unidad(self) -> None:
        """Devuelve la unidad asignada a la lista ordenada de su tipo."""
        if self._unidad_asignada:
            self._ultima_unidad = self._unidad_asignada
            unidades_disponibles = self.pool_unidades[self._tipo_equipo]
            unidades_disponibles.append(self._unidad_asignada)
            unidades_disponibles.sort(
                key=lambda unidad: int(unidad.split()[-1])
            )
            self._unidad_asignada = None

    @classmethod
    def reiniciar_inventario(cls) -> None:
        """Restablece las unidades 01-99 de cada tipo de equipo."""
        cls.pool_unidades = {
            nombre: [f"{nombre} {numero:02d}" for numero in range(1, 100)]
            for nombre in ("Laptop", "Cámara", "Sonido")
        }

    def calcular_costo(self, duracion: int) -> float:
        """Multiplica la tarifa del equipo por los días de alquiler."""
        _validar_duracion_entera(duracion, 30, "en días")
        self.validar()
        return self._tarifa_base * duracion

    def obtener_informacion(self) -> dict:
        """Devuelve el tipo y la unidad para el panel del cliente."""
        return {
            "id": self._id_entidad,
            "servicio": self._nombre_servicio,
            "tipo_equipo": self._tipo_equipo,
            "unidad": self._unidad_asignada or self._ultima_unidad,
        }


# BLOQUE 5: Asesorías especializadas
# Tarea: validar el nivel y la modalidad, y calcular el valor según las horas,
# el multiplicador del nivel y el recargo presencial cuando corresponda.
class AsesoriasEspecializadas(Servicio):
    """Asesoría con tarifas por nivel y recargo para modalidad presencial."""

    def __init__(self, id_servicio: str, nivel: str):
        """Configura el nivel solicitado y comienza en modalidad virtual."""
        if not isinstance(nivel, str):
            raise ServicioError("El nivel de asesoría debe indicarse como texto.")
        super().__init__(id_servicio, "Asesoría Especializada", 80000.0)
        self._nivel = nivel.strip().capitalize()
        self._presencial = False

    def establecer_modalidad(self, presencial: bool) -> None:
        """Guarda si la asesoría se prestará presencialmente."""
        if not isinstance(presencial, bool):
            raise ServicioError(
                "La modalidad presencial debe indicarse como Sí o No."
            )
        self._presencial = presencial

    def validar(self) -> bool:
        """Comprueba el nivel y que la modalidad tenga tipo booleano."""
        if self._nivel not in ("Junior", "Senior", "Master"):
            raise ServicioError("El nivel debe ser Junior, Senior o Master.")
        if not isinstance(self._presencial, bool):
            raise ServicioError(
                "La modalidad presencial debe indicarse como Sí o No."
            )
        return True

    @overload
    def calcular_costo(self, duracion: int) -> float: ...

    @overload
    def calcular_costo(
        self, duracion: int, nivel: str
    ) -> float: ...

    @overload
    def calcular_costo(
        self, duracion: int, nivel: str, presencial: bool
    ) -> float: ...

    def calcular_costo(
        self,
        duracion: int,
        nivel: str | None = None,
        presencial: bool | None = None,
    ) -> float:
        """Calcula horas por tarifa y nivel, más el recargo presencial opcional."""
        _validar_duracion_entera(duracion, 8, "en horas")
        self.validar()
        if nivel is not None and not isinstance(nivel, str):
            raise CalculoCostoError("El nivel debe indicarse como texto.")

        nivel_aplicado = self._nivel if nivel is None else nivel.strip().capitalize()
        multiplicadores = {"Junior": 1.0, "Senior": 1.5, "Master": 2.0}
        if nivel_aplicado not in multiplicadores:
            raise CalculoCostoError("El nivel debe ser Junior, Senior o Master.")

        modalidad_presencial = (
            self._presencial if presencial is None else presencial
        )
        if not isinstance(modalidad_presencial, bool):
            raise CalculoCostoError(
                "La modalidad presencial debe indicarse como Sí o No."
            )

        costo_horas = (
            self._tarifa_base
            * multiplicadores[nivel_aplicado]
            * duracion
        )
        recargo_presencial = 40000 if modalidad_presencial else 0
        return costo_horas + recargo_presencial

    def obtener_informacion(self) -> dict:
        """Devuelve nivel y modalidad para el panel de reservas."""
        return {
            "id": self._id_entidad,
            "servicio": self._nombre_servicio,
            "nivel": self._nivel,
            "modalidad": "Presencial" if self._presencial else "Virtual",
        }
