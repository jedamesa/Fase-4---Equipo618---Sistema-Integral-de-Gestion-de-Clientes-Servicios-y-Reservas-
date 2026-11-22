"""Simulación automática de Software FJ (sin interacción del usuario).

Ejecuta más de 10 operaciones completas: registros de clientes válidos e
inválidos, creación correcta e incorrecta de servicios, reservas exitosas y
fallidas, y cancelaciones. Cada error se captura, se muestra y se registra en
app.log; el programa nunca se detiene y al final imprime un resumen.

Uso:  python simulacion.py
"""

from typing import Any, Callable

from logger import log, activar_consola  # type: ignore[reportAttributeAccessIssue]
from excepciones import ErrorSoftwareFJ
from reserva import SistemaGestionFJ, Reserva
from servicios import (
    Servicio,
    ReservaSalas,
    AlquilerEquipos,
    AsesoriasEspecializadas,
)


# BLOQUE 1: Utilidades de la simulación
# Tarea: ejecutar cada operación de forma segura, mostrar su resultado y
# llevar la cuenta de éxitos y errores controlados.
_contador = 0
_resumen = {"exitosas": 0, "errores_controlados": 0, "inesperadas": 0}


def _cop(valor: float) -> str:
    return f"${valor:,.0f}".replace(",", ".") + " COP"


def _inventario() -> str:
    equipos = ", ".join(
        f"{tipo}: {len(unidades)}"
        for tipo, unidades in AlquilerEquipos.pool_unidades.items()
    )
    return f"Inventario libre -> salas: {len(ReservaSalas.salas_disponibles)} | {equipos}"


def ejecutar(
    titulo: str,
    accion: Callable[[], Any],
    debe_fallar: bool = False,
    registrar: bool = False,
) -> Any | None:
    """Ejecuta una operación y clasifica el resultado.

    debe_fallar: la operación es una prueba negativa (se espera un error).
    registrar:   el error ocurre fuera del gestor (por ejemplo, al construir
                 un servicio), así que aquí se escribe en el log.
    """
    global _contador
    _contador += 1
    print(f"\n[OP {_contador:02d}] {titulo}")
    try:
        valor = accion()
    except ErrorSoftwareFJ as e:
        if registrar:
            log.error(f"[SIMULACIÓN] {e.mensaje}")
        print(f"   ERROR CONTROLADO ({type(e).__name__}): {e.mensaje}")
        if e.__cause__ is not None:  # encadenamiento de excepciones
            print(f"   Causa original: {type(e.__cause__).__name__}: {e.__cause__}")
        _resumen["errores_controlados" if debe_fallar else "inesperadas"] += 1
        return None
    except Exception as ex:  # cualquier otro fallo tampoco detiene la simulación
        log.critical(f"[SIMULACIÓN] Falla no prevista: {ex!r}")
        print(f"   FALLA NO PREVISTA ({type(ex).__name__}): {ex}")
        _resumen["inesperadas"] += 1
        return None

    if debe_fallar:
        print("   AVISO: se esperaba un error y la operación se completó.")
        _resumen["inesperadas"] += 1
    else:
        print("   OK")
        _resumen["exitosas"] += 1
    return valor


def _reservar(
    sistema: SistemaGestionFJ,
    id_cliente: str,
    servicio: Servicio,
    duracion: int,
) -> Reserva:
    reserva = sistema.crear_reserva(id_cliente, servicio, duracion)
    info = reserva.obtener_informacion()
    print(f"   {info['ID Reserva']} | {info['Estado']} | {_cop(info['Total COP'])}")
    print(f"   Detalle: {info['Servicio']}")
    return reserva


class ServicioDefectuoso(Servicio):
    """Servicio de prueba cuyo cálculo falla, para forzar errores inesperados."""

    def __init__(self, modo: str):
        super().__init__("SRV-DEF", "Servicio defectuoso", 1000.0)
        self._modo = modo

    def validar(self) -> bool:
        return True

    def calcular_costo(self, _duracion: int) -> float:
        if self._modo == "negativo":
            return -500.0
        return self._tarifa_base / (_duracion - _duracion)  # ZeroDivisionError

    def obtener_informacion(self) -> dict:
        return {"servicio": self._nombre_servicio}


# BLOQUE 2: Escenario completo
def main():
    activar_consola()  # la simulación muestra también los logs en pantalla
    # El inventario es compartido por clase: se reinicia para partir de cero.
    ReservaSalas.reiniciar_inventario()  # type: ignore[reportAttributeAccessIssue]
    AlquilerEquipos.reiniciar_inventario()  # type: ignore[reportAttributeAccessIssue]
    sistema = SistemaGestionFJ()
    log.info("[SIMULACIÓN] ===== Inicio de la simulación =====")

    print("=" * 64)
    print(" SIMULACIÓN SOFTWARE FJ")
    print("=" * 64)

    # ---- A. Clientes ----
    print("\n--- A. REGISTRO DE CLIENTES ---")
    ana = ejecutar(
        "Registro válido: Ana Gomez",
        lambda: sistema.registrar_cliente("Ana Gomez", "ana@correo.com"),
    )
    luis = ejecutar(
        "Registro válido: Luis Perez",
        lambda: sistema.registrar_cliente("Luis Perez", "luis@correo.com"),
    )
    assert ana is not None and luis is not None, (
        "Los registros válidos iniciales deben producir objetos Cliente."
    )
    ejecutar(
        "Registro inválido: nombre con dígitos (Carlos123)",
        lambda: sistema.registrar_cliente("Carlos123", "carlos@correo.com"),
        debe_fallar=True,
    )
    ejecutar(
        "Registro inválido: correo sin arroba",
        lambda: sistema.registrar_cliente("Marta Ruiz", "marta-correo.com"),
        debe_fallar=True,
    )
    ejecutar(
        "Registro inválido: nombre con más de 15 letras",
        lambda: sistema.registrar_cliente("Maximiliano Fernandez", "max@correo.com"),
        debe_fallar=True,
    )
    ejecutar(
        "Registro inválido: nombre duplicado (ana   GOMEZ)",
        lambda: sistema.registrar_cliente("ana   GOMEZ", "otra@correo.com"),
        debe_fallar=True,
    )
    ejecutar(
        "Registro inválido: correo duplicado (el de Luis)",
        lambda: sistema.registrar_cliente("Marta Ruiz", "LUIS@correo.com"),
        debe_fallar=True,
    )

    # ---- B. Servicios inválidos ----
    print("\n--- B. CREACIÓN INCORRECTA DE SERVICIOS ---")
    ejecutar(
        "Equipo con tipo que no es texto (AlquilerEquipos('E', 123))",
        lambda: AlquilerEquipos("SRV-X", 123),  # type: ignore[arg-type]
        debe_fallar=True,
        registrar=True,
    )
    ejecutar(
        "Asesoría con modalidad inválida (establecer_modalidad('si'))",
        lambda: AsesoriasEspecializadas("SRV-X", "Junior").establecer_modalidad("si"),  # type: ignore[arg-type]
        debe_fallar=True,
        registrar=True,
    )
    ejecutar(
        "Sala con capacidad 99 (máximo 25)",
        lambda: _reservar(sistema, ana.id_cliente, ReservaSalas("SRV-X", 99), 2),
        debe_fallar=True,
    )
    ejecutar(
        "Equipo no disponible en el catálogo: Drone",
        lambda: _reservar(sistema, ana.id_cliente, AlquilerEquipos("SRV-X", "Drone"), 2),
        debe_fallar=True,
    )
    ejecutar(
        "Asesoría con nivel inexistente: Dios",
        lambda: _reservar(sistema, ana.id_cliente, AsesoriasEspecializadas("SRV-X", "Dios"), 2),
        debe_fallar=True,
    )

    # ---- C. Reservas exitosas ----
    print("\n--- C. RESERVAS EXITOSAS ---")
    sala_ana = ReservaSalas("SRV-001", 10, proyector=True, personas_catering=4)
    r_sala = ejecutar(
        "Sala para 10 personas, 3 h, proyector y catering para 4 (Ana)",
        lambda: _reservar(sistema, ana.id_cliente, sala_ana, 3),
    )
    r_camara = ejecutar(
        "Alquiler de cámara por 2 días (Ana)",
        lambda: _reservar(sistema, ana.id_cliente, AlquilerEquipos("SRV-002", "camara"), 2),
    )
    assert r_sala is not None and r_camara is not None, (
        "Las reservas iniciales válidas deben producir objetos Reserva."
    )
    asesoria_luis = AsesoriasEspecializadas("SRV-003", "senior")
    asesoria_luis.establecer_modalidad(True)
    ejecutar(
        "Asesoría Senior presencial por 2 h (Luis)",
        lambda: _reservar(sistema, luis.id_cliente, asesoria_luis, 2),
    )
    print(f"\n   {_inventario()}")

    # ---- D. Variantes del cálculo de costos ----
    print("\n--- D. CÁLCULO CON PARÁMETROS OPCIONALES (SOBRECARGA) ---")

    def variantes_sala():
        sala = ReservaSalas("SRV-T1", 10, proyector=False, personas_catering=0)
        print(f"   calcular_costo(2)           = {_cop(sala.calcular_costo(2))}")
        print(f"   calcular_costo(2, True)     = {_cop(sala.calcular_costo(2, True))}")
        print(f"   calcular_costo(2, True, 5)  = {_cop(sala.calcular_costo(2, True, 5))}")

    def variantes_asesoria():
        ases = AsesoriasEspecializadas("SRV-T2", "Junior")
        print(f"   calcular_costo(1)                    = {_cop(ases.calcular_costo(1))}")
        print(f"   calcular_costo(1, 'Master')          = {_cop(ases.calcular_costo(1, 'Master'))}")
        print(f"   calcular_costo(1, 'Master', True)    = {_cop(ases.calcular_costo(1, 'Master', True))}")

    ejecutar("Variantes de costo en ReservaSalas", variantes_sala)
    ejecutar("Variantes de costo en AsesoriasEspecializadas", variantes_asesoria)

    # ---- E. Reservas fallidas ----
    print("\n--- E. RESERVAS FALLIDAS ---")
    ejecutar(
        "Sala con duración 0 horas (la unidad asignada debe devolverse)",
        lambda: _reservar(sistema, ana.id_cliente, ReservaSalas("SRV-X", 5), 0),
        debe_fallar=True,
    )
    print(f"   {_inventario()}")
    ejecutar(
        "Equipo con duración 31 días (máximo 30)",
        lambda: _reservar(sistema, ana.id_cliente, AlquilerEquipos("SRV-X", "Laptop"), 31),
        debe_fallar=True,
    )
    ejecutar(
        "Cliente inexistente (CLI-999)",
        lambda: _reservar(sistema, "CLI-999", ReservaSalas("SRV-X", 5), 1),
        debe_fallar=True,
    )
    ejecutar(
        "Reutilizar el servicio de una reserva activa (sala de Ana)",
        lambda: _reservar(sistema, luis.id_cliente, sala_ana, 1),
        debe_fallar=True,
    )
    ejecutar(
        "Parámetro faltante: servicio None (error inesperado encadenado)",
        lambda: _reservar(sistema, ana.id_cliente, None, 1),  # type: ignore[arg-type]
        debe_fallar=True,
    )
    ejecutar(
        "Cálculo roto: división por cero dentro del servicio (error encadenado)",
        lambda: _reservar(sistema, ana.id_cliente, ServicioDefectuoso("dividir"), 1),
        debe_fallar=True,
    )
    ejecutar(
        "Cálculo inconsistente: el servicio devuelve un costo negativo",
        lambda: _reservar(sistema, ana.id_cliente, ServicioDefectuoso("negativo"), 1),
        debe_fallar=True,
    )

    # Se deja una sola unidad de sonido para demostrar el agotamiento.
    AlquilerEquipos.pool_unidades["Sonido"] = ["Sonido 01"]
    ejecutar(
        "Equipo de sonido: queda 1 unidad (reserva exitosa)",
        lambda: _reservar(sistema, luis.id_cliente, AlquilerEquipos("SRV-004", "sonido"), 1),
    )
    ejecutar(
        "Equipo de sonido: ya no hay unidades disponibles",
        lambda: _reservar(sistema, ana.id_cliente, AlquilerEquipos("SRV-005", "sonido"), 1),
        debe_fallar=True,
    )

    # ---- F. Cancelaciones ----
    print("\n--- F. CANCELACIONES ---")
    ejecutar(
        "Ana cancela su reserva de sala (debe liberar la Sala 01)",
        lambda: sistema.cancelar_reserva(r_sala.id_reserva, ana.id_cliente),
    )
    print(f"   {_inventario()}")
    ejecutar(
        "Cancelar de nuevo la misma reserva",
        lambda: sistema.cancelar_reserva(r_sala.id_reserva, ana.id_cliente),
        debe_fallar=True,
    )
    ejecutar(
        "Luis intenta cancelar una reserva de Ana",
        lambda: sistema.cancelar_reserva(r_camara.id_reserva, luis.id_cliente),
        debe_fallar=True,
    )
    ejecutar(
        "Cancelar una reserva que no existe (RES-999)",
        lambda: sistema.cancelar_reserva("RES-999", ana.id_cliente),
        debe_fallar=True,
    )
    ejecutar(
        "Nueva sala: reutiliza la Sala 01 que acaba de quedar libre",
        lambda: _reservar(sistema, luis.id_cliente, ReservaSalas("SRV-006", 8), 1),
    )

    # ---- Resultado final ----
    print("\n--- ESTADO FINAL DE LAS RESERVAS ---")
    for cliente in sistema.obtener_clientes():
        print(f"\nCliente: {cliente.nombre} ({cliente.id_cliente})")
        for reserva in sistema.obtener_reservas_cliente(cliente.id_cliente):
            info = reserva.obtener_informacion()
            print(
                f"  {info['ID Reserva']} | {info['Estado']:<10} | "
                f"{_cop(info['Total COP']):>16} | {info['Servicio']}"
            )

    print("\n" + "=" * 64)
    print(f" Operaciones ejecutadas        : {_contador}")
    print(f" Exitosas                      : {_resumen['exitosas']}")
    print(f" Errores controlados (esperados): {_resumen['errores_controlados']}")
    print(f" Resultados no esperados       : {_resumen['inesperadas']}")
    print(" El programa continuó sin interrupciones. Ver detalle en app.log")
    print("=" * 64)
    log.info(f"[SIMULACIÓN] ===== Fin: {_contador} operaciones =====")


if __name__ == "__main__":
    main()
