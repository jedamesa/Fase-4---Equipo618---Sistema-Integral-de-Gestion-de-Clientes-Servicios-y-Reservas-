"""Entidades de reserva y coordinación de los datos en memoria del sistema."""

from logger import log
from excepciones import (
    ErrorSoftwareFJ,
    ReservaError,
    ClienteError,
)
from entidades import Cliente
from servicios import Servicio


# BLOQUE 1: Reserva y ciclo de vida
# Tarea: vincular un cliente con un servicio, calcular el costo y controlar
# el paso de pendiente a confirmada o cancelada.
class Reserva:
    """Une un cliente con un servicio y controla el estado de su reserva."""

    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, duracion: int):
        """Crea una reserva pendiente; el costo se calcula al procesarla."""
        self._id_reserva = id_reserva
        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion
        self._estado = "PENDIENTE"
        self._costo_total = 0

    def procesar(self) -> float:
        """Valida el servicio y calcula su costo sin cambiar el estado."""
        if self._estado != "PENDIENTE":
            raise ReservaError("Solo se pueden procesar reservas pendientes.")
        self._servicio.validar()
        costo_total = self._servicio.calcular_costo(self._duracion)
        if costo_total < 0:
            raise ReservaError("El costo calculado no puede ser negativo.")
        self._costo_total = costo_total
        return costo_total

    def confirmar(self):
        """Procesa y confirma una reserva que aún está pendiente."""
        if self._estado != "PENDIENTE":
            raise ReservaError("Solo se pueden confirmar reservas pendientes.")
        self.procesar()
        self._estado = "CONFIRMADA"

    def cancelar(self):
        """Cancela la reserva y devuelve al inventario su recurso asignado."""
        if self._estado == "CANCELADA":
            raise ReservaError("La reserva ya se encuentra cancelada previamente.")
        # Primero se libera el recurso; si fallara, el estado no queda inconsistente.
        self._servicio.liberar_unidad()
        self._estado = "CANCELADA"

    @property
    def id_reserva(self) -> str:
        """Identificador público que se muestra al cliente para sus gestiones."""
        return self._id_reserva

    @property
    def id_cliente(self) -> str:
        """ID interno del cliente propietario de la reserva."""
        return self._cliente.id_cliente

    def obtener_informacion(self) -> dict:
        """Devuelve los campos necesarios para mostrar la reserva en pantalla."""
        return {
            "ID Reserva": self._id_reserva,
            "Cliente": self._cliente.nombre,
            "Servicio": self._servicio.obtener_informacion(),
            "Duración": self._duracion,
            "Total COP": self._costo_total,
            "Estado": self._estado
        }


# BLOQUE 2: Gestor en memoria
# Tarea: concentrar el registro de clientes y reservas, sus consultas y las
# reglas que relacionan unas entidades con otras durante una ejecución.
class SistemaGestionFJ:
    """Administra clientes y reservas usando listas en memoria.

    Este gestor es el punto común de las operaciones: valida relaciones,
    asigna IDs internos, registra eventos y conserva los datos mientras vive
    el programa.
    """

    def __init__(self):
        """Inicializa las colecciones y contadores de IDs de esta ejecución."""
        self._clientes: list[Cliente] = []
        self._reservas: list[Reserva] = []
        self._contador_clientes = 1
        self._contador_reservas = 1


    # BLOQUE 3: Registro de clientes
    # Tarea: validar la información y evitar clientes con nombre o correo duplicado.
    def registrar_cliente(self, nombre: str, correo: str):
        """Valida y guarda un cliente con nombre y correo únicos.

        La comparación de nombre ignora mayúsculas y espacios repetidos; la
        comparación de correo ignora mayúsculas. Los errores se registran y se
        vuelven a lanzar para que la interfaz pueda explicarlos al usuario.
        """
        try:
            id_cliente = f"CLI-{self._contador_clientes:03d}"
            nuevo_cliente = Cliente(id_cliente, nombre, correo)
            nuevo_cliente.validar()

            nombre_normalizado = " ".join(nombre.split()).casefold()
            correo_normalizado = nuevo_cliente.correo.casefold()
            if any(
                " ".join(cliente.nombre.split()).casefold() == nombre_normalizado
                for cliente in self._clientes
            ):
                raise ClienteError("Ya existe un cliente registrado con ese nombre.")
            if any(
                cliente.correo.casefold() == correo_normalizado
                for cliente in self._clientes
            ):
                raise ClienteError("Ya existe un cliente registrado con ese correo.")

        except ErrorSoftwareFJ as e:
            log.error(f"[CLIENTE: {nombre}] Intento fallido de registro: {e.mensaje}")
            raise
        else:
            self._clientes.append(nuevo_cliente)
            self._contador_clientes += 1
            log.info(f"[SISTEMA] Cliente registrado: {nombre} ({id_cliente})")
            return nuevo_cliente


    # BLOQUE 4: Creación y persistencia de reservas
    # Tarea: validar el cliente y el servicio, asignar inventario, confirmar la
    # reserva y conservar la operación de forma consistente ante fallos.
    def crear_reserva(self, id_cliente: str, servicio: Servicio, duracion: int):
        """Crea y confirma una reserva vinculada a un cliente existente.

        El método asigna inventario cuando el servicio lo requiere. Si ocurre
        un error antes de guardar la reserva, el bloque finally devuelve la
        unidad asignada para evitar que quede ocupada por una operación fallida.
        Los errores de dominio se registran y se propagan; los errores
        inesperados se encadenan dentro de ErrorSoftwareFJ.
        """
        unidad_asignada = False
        reserva_guardada = False
        try:
            cliente = next(
                (
                    cliente
                    for cliente in self._clientes
                    if cliente.id_cliente == id_cliente
                ),
                None,
            )
            if cliente is None:
                raise ClienteError(f"El cliente con ID {id_cliente} no existe en memoria.")

            servicio.validar()

            id_reserva = f"RES-{self._contador_reservas:03d}"
            nueva_reserva = Reserva(id_reserva, cliente, servicio, duracion)

            # Polimorfismo: los servicios sin inventario no hacen nada aquí.
            servicio.asignar_unidad()
            unidad_asignada = True
            nueva_reserva.confirmar()
            
        except ErrorSoftwareFJ as e:
            log.error(f"[SISTEMA] Error al procesar reserva: {e.mensaje}")
            raise
        except Exception as ex:
            log.critical(f"[SISTEMA] Falla inesperada: {ex}")
            raise ErrorSoftwareFJ("Error interno") from ex
        else:
            try:
                self._reservas.append(nueva_reserva)
                self._contador_reservas += 1
                reserva_guardada = True
            except Exception as ex:
                if nueva_reserva in self._reservas:
                    self._reservas.remove(nueva_reserva)
                log.critical(f"[SISTEMA] Falla inesperada al guardar la reserva: {ex}")
                raise ErrorSoftwareFJ("No se pudo guardar la reserva.") from ex
            log.info(f"[SISTEMA] Reserva {id_reserva} exitosa para {cliente.nombre}.")
            return nueva_reserva
        finally:
            if unidad_asignada and not reserva_guardada:
                servicio.liberar_unidad()


    # BLOQUE 5: Búsquedas, consultas y cancelación
    # Tarea: localizar clientes, consultar sus reservas y cancelar solo las
    # reservas cuyo propietario coincide con el cliente activo.
    def obtener_cliente(self, id_cliente: str) -> Cliente:
        """Busca un cliente por su ID interno o genera un error de dominio."""
        id_cliente = id_cliente.strip()
        cliente = next(
            (cliente for cliente in self._clientes if cliente.id_cliente == id_cliente),
            None,
        )
        if cliente is None:
            log.error(f"[CLIENTE] No existe un cliente con el ID {id_cliente}.")
            raise ClienteError(f"No existe un cliente con el ID {id_cliente}.")
        return cliente

    def obtener_cliente_por_nombre(self, nombre: str) -> Cliente:
        """Inicia la búsqueda por nombre sin distinguir mayúsculas ni espacios."""
        nombre_normalizado = " ".join(nombre.split()).casefold()
        for cliente in self._clientes:
            if " ".join(cliente.nombre.split()).casefold() == nombre_normalizado:
                return cliente
        log.error(
            f"[INICIO DE SESIÓN] No existe un cliente registrado con el nombre {nombre!r}."
        )
        raise ClienteError("No existe un cliente registrado con ese nombre.")

    def obtener_cliente_por_correo(self, correo: str) -> Cliente:
        """Busca un cliente usando su correo, sin distinguir mayúsculas."""
        correo_normalizado = correo.strip().casefold()
        for cliente in self._clientes:
            if cliente.correo.casefold() == correo_normalizado:
                return cliente
        log.error("[INICIO DE SESIÓN] No existe un cliente registrado con ese correo.")
        raise ClienteError("No existe un cliente registrado con ese correo.")

    def obtener_clientes(self) -> list[Cliente]:
        """Devuelve una copia superficial para no exponer la lista interna."""
        return self._clientes.copy()

    def obtener_reservas_cliente(self, id_cliente: str) -> list[Reserva]:
        """Devuelve las reservas que pertenecen al cliente indicado."""
        id_cliente = id_cliente.strip()
        self.obtener_cliente(id_cliente)
        return [
            reserva for reserva in self._reservas
            if reserva.id_cliente == id_cliente
        ]

    def cancelar_reserva(self, id_reserva: str, id_cliente: str):
        """Cancela una reserva solo si existe y pertenece al cliente activo."""
        try:
            id_reserva = id_reserva.strip()
            reserva = next(
                (
                    reserva
                    for reserva in self._reservas
                    if reserva.id_reserva == id_reserva
                ),
                None,
            )
            if reserva is None:
                raise ReservaError(f"La reserva {id_reserva} no existe.")
            if reserva.id_cliente != id_cliente:
                raise ReservaError(
                    f"La reserva {id_reserva} no pertenece al cliente activo."
                )
            reserva.cancelar()
        except ErrorSoftwareFJ as e:
            log.error(f"[SISTEMA] Fallo cancelando reserva: {e.mensaje}")
            raise
        else:
            log.info(f"[SISTEMA] Reserva {id_reserva} cancelada correctamente.")