"""Interfaz de consola para registrar clientes y administrar sus reservas."""

import sys
from reserva import SistemaGestionFJ
from servicios import (
    ReservaSalas,
    AlquilerEquipos,
    AsesoriasEspecializadas,
)
from entidades import Cliente
from excepciones import ErrorSoftwareFJ
from logger import log


# BLOQUE 1: Control de navegación entre pantallas
# Tarea: usar señales internas para regresar de un formulario sin cerrar el programa.
class _VolverSeleccionServicio(Exception):
    """Señala que el usuario quiere abandonar la captura de una reserva."""

    pass


class _VolverMenuInicial(Exception):
    """Señala que el usuario canceló el registro y vuelve al menú inicial."""

    pass


# BLOQUE 2: Lectura y validación de datos
# Tarea: comprobar las entradas de consola antes de utilizarlas en el sistema.
# Las funciones de este bloque repiten la pregunta cuando hay errores, registran
# el intento en el log y muestran cómo corregirlo.
def _opciones_disponibles(opciones: dict[str, str]) -> str:
    """Devuelve los números de una lista de opciones para mensajes de error."""
    return ", ".join(opciones)


def _recordar_regreso(permitir_volver: bool) -> str:
    """Agrega a la ayuda el atajo de regreso cuando el flujo lo permite."""
    if permitir_volver:
        return " Ingrese 0 para volver al menú de selección."
    return ""


def _leer_entero(
    mensaje: str,
    campo: str,
    minimo: int | None = None,
    maximo: int | None = None,
    permitir_volver: bool = False,
) -> int:
    """Lee un entero dentro del rango indicado y repite si la entrada es inválida."""
    rango = (
        f"Ingrese un valor entre {minimo} y {maximo}."
        if minimo is not None and maximo is not None
        else f"Ingrese un valor mínimo de {minimo}."
        if minimo is not None
        else f"Ingrese un valor máximo de {maximo}."
        if maximo is not None
        else "Ingrese un número entero."
    )
    while True:
        print(mensaje)
        if permitir_volver:
            print("[0] Volver al menú de selección de servicio")
        entrada = input("Valor: ").strip()
        if permitir_volver and entrada == "0":
            raise _VolverSeleccionServicio
        if not entrada:
            error = f"No ha ingresado ningún dato. {rango}{_recordar_regreso(permitir_volver)}"
            log.error(f"[ENTRADA] {campo}: dato vacío.")
            print(f"Error: {error}")
            continue

        if not entrada.isascii() or not entrada.isdecimal():
            error = (
                f"El dato de {campo.lower()} debe ser un número entero "
                "(solo dígitos, sin letras ni símbolos). "
                f"{rango}{_recordar_regreso(permitir_volver)}"
            )
            log.error(f"[ENTRADA] Dato no numérico para {campo}.")
            print(f"Error: {error}")
            continue

        digitos_significativos = entrada.lstrip("0") or "0"
        if maximo is not None and len(digitos_significativos) > len(str(maximo)):
            error = f"El valor supera el máximo permitido para {campo.lower()}. {rango}"
            log.error(f"[ENTRADA] Valor fuera de rango para {campo}.")
            print(f"Error: {error}{_recordar_regreso(permitir_volver)}")
            continue

        try:
            valor = int(digitos_significativos)
        except ValueError:
            error = f"El dato de {campo.lower()} es demasiado largo. {rango}"
            log.error(f"[ENTRADA] Dato excesivamente largo para {campo}.")
            print(f"Error: {error}{_recordar_regreso(permitir_volver)}")
            continue
        if minimo is not None and valor < minimo:
            error = f"El valor mínimo para {campo.lower()} es {minimo}. {rango}"
        elif maximo is not None and valor > maximo:
            error = f"El valor máximo para {campo.lower()} es {maximo}. {rango}"
        else:
            return valor

        log.error(f"[ENTRADA] {campo}: valor fuera de rango.")
        print(f"Error: {error}{_recordar_regreso(permitir_volver)}")


def _leer_opcion_numerica(
    mensaje: str,
    opciones: dict[str, str],
    permitir_volver: bool = False,
) -> str:
    """Lee una opción numérica permitida y explica las opciones si falla."""
    opciones_permitidas = _opciones_disponibles(opciones)
    if permitir_volver and "0" not in opciones:
        opciones_permitidas = f"0, {opciones_permitidas}"
    max_digitos = max(len(opcion) for opcion in opciones)
    while True:
        respuesta = input(mensaje).strip()
        if permitir_volver and respuesta == "0":
            raise _VolverSeleccionServicio
        if respuesta in opciones:
            return respuesta
        if not respuesta:
            error = (
                "No ha ingresado ningún dato. Puede escoger entre "
                f"las opciones {opciones_permitidas}."
            )
            log.error("[ENTRADA] No se ingresó una opción.")
        elif not respuesta.isascii() or not respuesta.isdecimal():
            error = (
                "Debe ingresar solo números. Puede escoger entre "
                f"las opciones {opciones_permitidas}."
            )
            log.error("[ENTRADA] Se ingresaron caracteres no numéricos en una opción.")
        elif len(respuesta) > max_digitos:
            error = (
                f"Ingrese como máximo {max_digitos} "
                f"{'dígito' if max_digitos == 1 else 'dígitos'}. "
                f"Opciones disponibles: {opciones_permitidas}."
            )
            log.error("[ENTRADA] La opción ingresada excede la cantidad de dígitos.")
        else:
            error = (
                f"Opción fuera de rango. Seleccione una de estas opciones: "
                f"{opciones_permitidas}."
            )
            log.error("[ENTRADA] Se ingresó una opción no válida.")
        print(f"Error: {error}")


def _leer_nombre_cliente(
    mensaje: str, permitir_volver: bool = False
) -> str:
    """Lee un nombre válido; en el registro, permite volver con 0."""
    while True:
        if permitir_volver:
            print("[0] Volver al menú inicial")
        nombre_cliente = " ".join(input(mensaje).split())
        if permitir_volver and nombre_cliente == "0":
            raise _VolverMenuInicial
        if not nombre_cliente:
            error = "No ha ingresado ningún nombre. Escriba el nombre del cliente."
        elif not all(
            letra.isalpha() or letra.isspace() for letra in nombre_cliente
        ):
            error = "El nombre solo puede contener letras y espacios. Inténtelo de nuevo."
        elif len(nombre_cliente.replace(" ", "")) > 15:
            error = (
                "El nombre puede tener como máximo 15 letras, sin contar espacios. "
                "Inténtelo de nuevo."
            )
        else:
            return nombre_cliente

        log.error("[ENTRADA] Nombre de cliente no válido.")
        print(f"Error: {error}")


def _leer_correo_cliente(permitir_volver: bool = False) -> str:
    """Lee un correo con formato válido y, opcionalmente, permite cancelar."""
    while True:
        if permitir_volver:
            print("[0] Volver al menú inicial")
        correo = input("Ingrese el correo electrónico: ").strip()
        if permitir_volver and correo == "0":
            raise _VolverMenuInicial
        if Cliente.correo_tiene_formato_valido(correo):
            return correo

        log.error("[ENTRADA] Correo electrónico no válido.")
        print(
            "Error: El correo no tiene un formato válido. "
            "Use un formato como nombre@dominio.com."
        )


def _leer_id_reserva() -> str:
    """Lee un ID de reserva con el formato RES- seguido de al menos tres dígitos."""
    while True:
        id_reserva = input("Ingrese el ID de la reserva (formato RES-001): ").strip()
        if not id_reserva:
            error = "No ha ingresado ningún ID. Use el formato RES-001."
        elif (
            len(id_reserva) > 20
            or not id_reserva.startswith("RES-")
            or not id_reserva[4:].isascii()
            or not id_reserva[4:].isdecimal()
            or len(id_reserva[4:]) < 3
        ):
            error = "El ID no tiene el formato esperado. Use RES- seguido de al menos 3 dígitos."
        else:
            return id_reserva

        log.error("[ENTRADA] ID de reserva no válido.")
        print(f"Error: {error}")


def _leer_si_no(pregunta: str) -> bool:
    """Presenta opciones numéricas Sí/No y devuelve True cuando se elige Sí."""
    opciones = {
        "0": "Volver al menú de selección de servicio",
        "1": "Sí",
        "2": "No",
    }
    print(pregunta)
    print("[0] Volver al menú de selección de servicio")
    print("[1] Sí")
    print("[2] No")
    opcion = _leer_opcion_numerica("Opción: ", opciones)
    if opcion == "0":
        raise _VolverSeleccionServicio
    return opcion == "1"


# BLOQUE 3: Presentación de información
# Tarea: formatear valores y mostrar el catálogo o las reservas en un formato legible.
def _formatear_cop(valor: float) -> str:
    """Muestra un importe en pesos colombianos sin decimales."""
    return f"${valor:,.0f}".replace(",", ".")


def _esperar_enter(
    mensaje: str = "Presione ENTER para regresar al Panel Principal..."
) -> None:
    """Pausa la pantalla para que el usuario pueda leerla antes de continuar."""
    input(mensaje)


def mostrar_catalogo_servicios(cliente):
    """Muestra las tarifas y características de los servicios disponibles."""
    print("\n" + "=" * 50)
    print("           CATÁLOGO DE SERVICIOS - SOFTWARE FJ")
    print(f"           Cliente activo: {cliente.nombre}")
    print("=" * 50)
    print("1. RESERVA DE SALAS DE CONFERENCIAS")
    print("   • Tarifa base: $40.000 COP / hora")
    print("   • Adicionales: Proyector (+$25.000 COP),")
    print("     Catering (+$15.000 COP/persona)")
    print("   • Capacidad máxima: 25 personas")
    print()
    print("2. ALQUILER DE EQUIPOS TECNOLÓGICOS")
    print("   • Tarifas por día:")
    print("     - Laptop: $50.000 COP/día")
    print("     - Cámara: $70.000 COP/día")
    print("     - Sonido: $60.000 COP/día")
    print("   • Asignación automática de unidades por inventario (Pool).")
    print()
    print("3. ASESORÍAS ESPECIALIZADAS")
    print("   • Tarifa hora base: $80.000 COP / hora")
    print("   • Multiplicador por nivel: Junior (1.0x), Senior (1.5x), Master (2.0x)")
    print("   • Recargo por modalidad Presencial: +$40.000 COP")
    print("=" * 50)
    _esperar_enter()


def mostrar_reservas_cliente(sistema: SistemaGestionFJ, cliente):
    """Construye y muestra una tabla con las reservas del cliente activo.

    Consulta los datos al gestor y adapta los detalles según el tipo de servicio:
    sala, equipo o asesoría. Esta función solo presenta información; no modifica
    las reservas.
    """
    reservas = sistema.obtener_reservas_cliente(cliente.id_cliente)
    print("\n" + "=" * 50)
    print("               MIS RESERVAS")
    print(f"           Cliente activo: {cliente.nombre}")
    print("=" * 50)
    encabezados = ["ID Reserva", "Servicio", "Detalles", "Total", "Estado"]
    filas = []
    if not reservas:
        print("Aún no tienes reservas.")
    else:
        for reserva in reservas:
            informacion = reserva.obtener_informacion()
            servicio = informacion["Servicio"]
            duracion = informacion["Duración"]
            if "capacidad" in servicio:
                servicio_texto = f"Sala ({duracion} hrs)"
                detalles = f"{servicio['sala']}, Cap: {servicio['capacidad']} p"
                if servicio["proyector"]:
                    detalles += ", Proyector"
                if servicio["personas_catering"]:
                    detalles += f", Catering: {servicio['personas_catering']} p"
            elif "tipo_equipo" in servicio:
                servicio_texto = f"{servicio['tipo_equipo']} ({duracion} días)"
                detalles = f"Alquiler Tecnológico, Unidad: {servicio['unidad']}"
            else:
                servicio_texto = f"Asesoría ({duracion} hrs)"
                detalles = f"Nivel: {servicio['nivel']}, {servicio['modalidad']}"

            filas.append(
                [
                    informacion["ID Reserva"],
                    servicio_texto,
                    detalles,
                    _formatear_cop(informacion["Total COP"]),
                    informacion["Estado"],
                ]
            )

    anchos = [
        max(len(encabezados[indice]), *(len(fila[indice]) for fila in filas))
        if filas
        else len(encabezados[indice])
        for indice in range(len(encabezados))
    ]
    separador = "-+-".join("-" * ancho for ancho in anchos)
    print(" | ".join(
        f"{encabezado:<{anchos[indice]}}"
        for indice, encabezado in enumerate(encabezados)
    ))
    print(separador)
    for fila in filas:
        print(" | ".join(
            f"{valor:<{anchos[indice]}}"
            for indice, valor in enumerate(fila)
        ))
    print(separador)
    _esperar_enter()


# BLOQUE 4: Creación de reservas
# Tarea: recopilar los datos específicos de un servicio y pedir al gestor que
# valide, procese y guarde la reserva.
def crear_reserva_cliente(sistema: SistemaGestionFJ, cliente):
    """Guía al cliente en la selección, configuración y creación de una reserva.

    Según el tipo elegido, solicita únicamente los datos necesarios y crea el
    objeto de servicio correspondiente. La asignación de recursos, el cálculo
    del costo y el registro de la reserva quedan a cargo de SistemaGestionFJ.
    Si el usuario vuelve durante la captura, descarta los datos incompletos y
    regresa a la selección de servicio.
    """
    while True:
        print("\n" + "=" * 50)
        print("           NUEVA RESERVA - SELECCIÓN DE SERVICIO")
        print(f"           Cliente activo: {cliente.nombre}")
        print("=" * 50)
        print("[1] Reservar Sala de Conferencias")
        print("[2] Alquilar Equipo Tecnológico")
        print("[3] Solicitar Asesoría Especializada")
        print("[4] Volver al Panel Principal")
        print("=" * 50)
        opciones = {
            "1": "Reservar Sala de Conferencias",
            "2": "Alquilar Equipo Tecnológico",
            "3": "Solicitar Asesoría Especializada",
            "4": "Volver al Panel Principal",
        }
        opcion = _leer_opcion_numerica("Opción: ", opciones)
        if opcion == "4":
            return

        id_servicio = (
            f"SRV-{cliente.id_cliente}-"
            f"{len(sistema.obtener_reservas_cliente(cliente.id_cliente)) + 1:03d}"
        )
        try:
            if opcion == "1":
                capacidad = _leer_entero(
                    "Ingrese la capacidad de la sala (1-25): ",
                    "Capacidad de la sala",
                    minimo=1,
                    maximo=25,
                    permitir_volver=True,
                )
                duracion = _leer_entero(
                    "Ingrese la duración en horas (1-24): ",
                    "Duración en horas",
                    minimo=1,
                    maximo=24,
                    permitir_volver=True,
                )
                proyector = _leer_si_no("¿Desea alquilar proyector?: ")
                desea_catering = _leer_si_no("¿Desea agregar catering?: ")
                personas_catering = 0
                if desea_catering:
                    personas_catering = _leer_entero(
                        f"Ingrese el número de personas para catering (1-{capacidad}): ",
                        "Personas para catering",
                        minimo=1,
                        maximo=capacidad,
                        permitir_volver=True,
                    )
                servicio = ReservaSalas(
                    id_servicio, capacidad, proyector, personas_catering
                )
            elif opcion == "2":
                print("Seleccione el equipo:")
                print("[0] Volver al menú de selección de servicio")
                print("[1] Laptop - $50.000 COP/día")
                print("[2] Cámara - $70.000 COP/día")
                print("[3] Sonido - $60.000 COP/día")
                equipos = {"1": "Laptop", "2": "Cámara", "3": "Sonido"}
                tipo_equipo = equipos[
                    _leer_opcion_numerica(
                        "Opción: ", equipos, permitir_volver=True
                    )
                ]
                duracion = _leer_entero(
                    "Ingrese la duración en días (1-30): ",
                    "Duración en días",
                    minimo=1,
                    maximo=30,
                    permitir_volver=True,
                )
                servicio = AlquilerEquipos(id_servicio, tipo_equipo)
            else:
                print("Seleccione el nivel de asesoría:")
                print("[0] Volver al menú de selección de servicio")
                print("[1] Junior")
                print("[2] Senior")
                print("[3] Master")
                niveles = {"1": "Junior", "2": "Senior", "3": "Master"}
                nivel = niveles[
                    _leer_opcion_numerica(
                        "Opción: ", niveles, permitir_volver=True
                    )
                ]
                duracion = _leer_entero(
                    "Ingrese la duración en horas (1-8): ",
                    "Duración en horas",
                    minimo=1,
                    maximo=8,
                    permitir_volver=True,
                )
                servicio = AsesoriasEspecializadas(id_servicio, nivel)
                servicio.establecer_modalidad(
                    _leer_si_no("¿La asesoría será presencial?: ")
                )

            reserva = sistema.crear_reserva(
                cliente.id_cliente, servicio, duracion
            )
            print(
                f"Reserva creada correctamente. ID: "
                f"{reserva.obtener_informacion()['ID Reserva']}; "
                f"total: {_formatear_cop(reserva.obtener_informacion()['Total COP'])} COP."
            )
        except _VolverSeleccionServicio:
            print("Volviendo al menú de selección de servicio.")
            continue
        except ErrorSoftwareFJ as e:
            print(f"No se pudo crear la reserva: {e.mensaje}")


# BLOQUE 5: Operaciones del panel del cliente
# Tarea: conectar las opciones del panel con las consultas y acciones del sistema.
def cancelar_reserva_cliente(sistema: SistemaGestionFJ, cliente):
    """Solicita el identificador de una reserva y pide su cancelación al gestor.

    El gestor verifica que la reserva pertenezca al cliente y que pueda
    cancelarse; aquí se informa el resultado sin duplicar esas reglas de negocio.
    """
    id_reserva = _leer_id_reserva()
    try:
        sistema.cancelar_reserva(id_reserva, cliente.id_cliente)
        print(f"La reserva {id_reserva} fue cancelada correctamente.")
    except ErrorSoftwareFJ as e:
        print(f"No se pudo cancelar la reserva: {e.mensaje}")


def menu_cliente(sistema: SistemaGestionFJ, cliente):
    """Mantiene el panel del cliente activo hasta cerrar sesión o salir.

    Cada opción delega una operación concreta a su función de interfaz. Cerrar
    sesión retorna al menú inicial; salir termina el proceso.
    """
    while True:
        print("\n" + "=" * 50)
        print("       SOFTWARE FJ - PANEL PRINCIPAL CLIENTE")
        print()
        print(f"       Cliente activo: {cliente.nombre}")
        print("=" * 50)
        print("[1] Ver Catálogo de Servicios y Tarifas")
        print("[2] Realizar una Reserva (Salas, Equipos, Asesorías)")
        print("[3] Ver Mi Panel de Reservas")
        print("[4] Cancelar una Reserva")
        print("[5] Cerrar Sesión (Volver a Pantalla Inicial)")
        print("[6] Salir del Sistema")
        print("=" * 50)
        opciones = {
            "1": "Ver Catálogo de Servicios y Tarifas",
            "2": "Realizar una Reserva",
            "3": "Ver Mi Panel de Reservas",
            "4": "Cancelar una Reserva",
            "5": "Cerrar Sesión",
            "6": "Salir del Sistema",
        }
        opcion = _leer_opcion_numerica("Opción: ", opciones)
        if opcion in ("1", "2", "3", "4"):
            # Red de seguridad: un fallo inesperado se registra y el panel sigue activo.
            try:
                if opcion == "1":
                    mostrar_catalogo_servicios(cliente)
                elif opcion == "2":
                    crear_reserva_cliente(sistema, cliente)
                elif opcion == "3":
                    mostrar_reservas_cliente(sistema, cliente)
                else:
                    cancelar_reserva_cliente(sistema, cliente)
            except ErrorSoftwareFJ as e:
                log.error(f"[PANEL] Error de negocio no controlado antes: {e.mensaje}")
                print(f"No se pudo completar la operación: {e.mensaje}")
            except Exception as ex:
                log.critical(f"[PANEL] Falla inesperada: {ex!r}")
                print("Ocurrió un error inesperado, pero el sistema sigue activo.")
        elif opcion == "5":
            print("Sesión cerrada.")
            return
        elif opcion == "6":
            print("Saliendo del sistema...")
            sys.exit(0)
        else:
            print("Opción inválida.")


# BLOQUE 6: Acceso de clientes
# Tarea: autenticar clientes existentes o registrar nuevos y dirigirlos a su panel.
def iniciar_sesion(sistema: SistemaGestionFJ):
    """Busca un cliente existente usando su nombre o su correo electrónico.

    La búsqueda y las reglas de identidad pertenecen al gestor. Si la credencial
    no corresponde a un cliente registrado, se muestra el error y se vuelve al
    menú inicial; si coincide, se abre el panel del cliente.
    """
    print("\n" + "=" * 50)
    print("             INICIAR SESIÓN")
    print("=" * 50)
    print("[1] Ingresar con nombre de usuario")
    print("[2] Ingresar con correo electrónico")
    print("[3] Volver al menú inicial")
    metodo_ingreso = _leer_opcion_numerica(
        "Seleccione cómo desea iniciar sesión: ",
        {
            "1": "Ingresar con nombre de usuario",
            "2": "Ingresar con correo electrónico",
            "3": "Volver al menú inicial",
        },
    )
    if metodo_ingreso == "3":
        return

    try:
        if metodo_ingreso == "1":
            nombre_cliente = _leer_nombre_cliente(
                "Ingrese su nombre de usuario: ", permitir_volver=True
            )
            cliente = sistema.obtener_cliente_por_nombre(nombre_cliente)
        else:
            correo = _leer_correo_cliente(permitir_volver=True)
            cliente = sistema.obtener_cliente_por_correo(correo)
    except _VolverMenuInicial:
        print("Inicio de sesión cancelado. Volviendo al menú inicial.")
        return
    except ErrorSoftwareFJ as e:
        print(f"No se pudo iniciar sesión: {e.mensaje}")
        return
    log.info(f"[INICIO DE SESIÓN] Cliente autenticado: {cliente.nombre} ({cliente.id_cliente})")
    menu_cliente(sistema, cliente)


def registrar_cliente_interactivo(sistema: SistemaGestionFJ):
    """Recopila los datos del nuevo cliente y coordina su registro.

    El usuario puede cancelar desde la solicitud del nombre o del correo. Cuando
    el registro se completa, se abre el panel del cliente recién creado; los
    datos inválidos se informan y se permite intentarlo de nuevo.
    """
    while True:
        try:
            nombre_cliente = _leer_nombre_cliente(
                "Ingrese nombre (solo letras, max. 15 sin contar espacios): ",
                permitir_volver=True,
            )
            correo = _leer_correo_cliente(permitir_volver=True)
            cliente = sistema.registrar_cliente(nombre_cliente, correo)
        except _VolverMenuInicial:
            print("Registro cancelado. Volviendo al menú inicial.")
            return
        except ErrorSoftwareFJ as e:
            print(f"No se pudo registrar el cliente: {e.mensaje}")
            continue

        print("Cliente guardado en memoria.")
        menu_cliente(sistema, cliente)
        return


# BLOQUE 7: Menú inicial y arranque del programa
# Tarea: crear el gestor en memoria, presentar las opciones de entrada y
# mantener la aplicación disponible hasta que el usuario decida salir.
def menu_interactivo():
    """Ejecuta el ciclo principal de la interfaz de consola.

    El gestor se crea una sola vez para que los clientes y reservas permanezcan
    disponibles mientras la aplicación está abierta. Desde este menú se inicia
    sesión, se registra un cliente o se finaliza el programa.
    """
    sistema = SistemaGestionFJ()
    while True:
        print("\n" + "=" * 50)
        print("           ¡BIENVENIDO A SOFTWARE FJ!             ")
        print("=" * 50)
        print("Servicios disponibles:")
        print("  • Reserva de salas de conferencias")
        print("  • Alquiler de equipos tecnologicos")
        print("  • Asesorias especializadas")
        print("=" * 50)
        print("Selecciona una opcion para ingresar:")
        print("[1] Iniciar sesión (con nombre de usuario o correo)")
        print("[2] Registrar nuevo cliente")
        print("[3] Salir del sistema")
        print("=" * 50)
        
        opciones = {
            "1": "Iniciar sesion",
            "2": "Registrar nuevo cliente",
            "3": "Salir del sistema",
        }
        opcion = _leer_opcion_numerica("Opcion: ", opciones)
        
        if opcion in ("1", "2"):
            try:
                if opcion == "1":
                    iniciar_sesion(sistema)
                else:
                    registrar_cliente_interactivo(sistema)
            except Exception as ex:
                log.critical(f"[MENÚ] Falla inesperada: {ex!r}")
                print("Ocurrió un error inesperado, pero el sistema sigue activo.")
        elif opcion == "3":
            print("Saliendo...")
            sys.exit(0)
        else:
            print("Opción inválida.")


# Punto de entrada: convierte interrupciones de consola en una salida controlada.
if __name__ == "__main__":
    try:
        menu_interactivo()
    except KeyboardInterrupt:
        log.warning("[SISTEMA] Ejecución interrumpida por el usuario.")
        print("\nOperación interrumpida. Saliendo del sistema.")
    except EOFError:
        log.warning("[SISTEMA] Entrada finalizada inesperadamente.")
        print("\nNo se recibió más entrada. Saliendo del sistema.")