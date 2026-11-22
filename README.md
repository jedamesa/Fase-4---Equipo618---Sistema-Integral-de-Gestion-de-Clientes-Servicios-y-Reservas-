# Sistema de Gestión - Software FJ

Este repositorio contiene el desarrollo del **Ejercicio 1: Sistema Integral de Gestión de Clientes, Servicios y Reservas**, correspondiente a la Fase 4 del curso de Programación Orientada a Objetos.

## Descripción del proyecto

Software FJ es una aplicación de consola en Python para registrar clientes y administrar reservas de salas, alquileres de equipos y asesorías. Los datos se mantienen en objetos y listas mientras el programa está abierto; no se utiliza una base de datos.

## Organización del código

- `main.py`: interfaz de consola, lectura de entradas, registro, inicio de sesión y operaciones del panel.
- `entidades.py`: entidad abstracta general y entidad `Cliente`, con validación de nombre y correo.
- `servicios.py`: clase abstracta `Servicio`, servicios concretos, cálculos, validaciones e inventario.
- `reserva.py`: clase `Reserva` y coordinador `SistemaGestionFJ`, que administra los clientes y reservas en memoria.
- `excepciones.py`: errores de negocio personalizados para informar fallos concretos.
- `logger.py`: configuración compartida para registrar eventos en el archivo `app.log` (se crea junto al código). La consola solo muestra los logs si se activa, como hace `simulacion.py`.
- `simulacion.py`: simulación automática de más de 10 operaciones (válidas e inválidas) para demostrar el manejo de errores sin interacción del usuario.

## Decisiones de arquitectura

- **Encapsulación:** los atributos internos de las entidades se consultan mediante propiedades y métodos públicos.
- **Herencia y polimorfismo:** los servicios especializados heredan de `Servicio` e implementan sus reglas particulares.
- **Listas en memoria:** clientes, reservas y unidades disponibles se manejan con listas; al cerrar el programa los clientes y reservas se reinician.
- **Inventario:** hay unidades `01` a `99` para salas y para cada tipo de equipo. Se asigna el número disponible menor y se libera al cancelar la reserva. No se manejan fechas de vencimiento. El inventario es compartido por clase; `reiniciar_inventario()` lo restablece. Un mismo objeto de servicio no puede asignarse a dos reservas activas, y la reserva cancelada conserva el dato de la unidad que usó.
- **Excepciones y logs:** las excepciones propias permiten diferenciar errores de cliente, servicio, costo, disponibilidad y reserva. El módulo `logging` agrega los eventos registrados al archivo `app.log` sin borrar las entradas previas. En la ejecución normal los logs no se imprimen en pantalla para no mezclarse con los menús.

## Principios de POO y su implementación

| Principio o mecanismo | Aplicación en el sistema | Clases y archivos |
|---|---|---|
| Abstracción | Las clases base definen operaciones comunes sin establecer las reglas concretas de cada entidad o servicio. | `EntidadBase` exige `validar()` y `obtener_informacion()`; `Servicio` exige `calcular_costo()`. En `entidades.py` y `servicios.py`. |
| Herencia | Las clases especializadas reutilizan la estructura de una clase base. | `Cliente` hereda de `EntidadBase`; `Servicio` también hereda de `EntidadBase`; `ReservaSalas`, `AlquilerEquipos` y `AsesoriasEspecializadas` heredan de `Servicio`. |
| Polimorfismo | El gestor trabaja con la interfaz común del servicio y cada tipo aplica sus propias validaciones, cálculos e información. Sin comprobar tipos concretos, el gestor llama a `asignar_unidad()` y `liberar_unidad()`: los servicios con inventario los sobrescriben y los demás heredan un comportamiento vacío. | Las implementaciones de `validar()`, `calcular_costo()`, `obtener_informacion()`, `asignar_unidad()` y `liberar_unidad()` en `servicios.py`. |
| Encapsulación | Los datos se guardan en atributos internos y se consultan mediante propiedades o métodos. | Atributos como `_nombre`, `_correo`, `_estado` y `_costo_total`; propiedades públicas de `Cliente` y `Reserva`. En `entidades.py` y `reserva.py`. |
| Manejo de excepciones | Los errores se representan con tipos propios, se registran y se propagan para que la interfaz informe el resultado. | Jerarquía de `ErrorSoftwareFJ` en `excepciones.py`; bloques `try/except/else/finally` y encadenamiento de errores en `SistemaGestionFJ` dentro de `reserva.py`. |
| Variantes del cálculo | Salas y asesorías admiten parámetros opcionales para calcular con distintos adicionales, niveles o modalidades. | `calcular_costo()` en `ReservaSalas` y `AsesoriasEspecializadas`, con firmas `@overload` para documentación de tipos en `servicios.py`. En ejecución de Python se utiliza una implementación con parámetros opcionales. |

## Verificación frente al enunciado del problema

| Requisito | Evidencia en el programa | Estado y alcance |
|---|---|---|
| Aplicación orientada a objetos para clientes, servicios y reservas, sin base de datos | `Cliente`, las clases de servicio, `Reserva` y `SistemaGestionFJ`; clientes y reservas se conservan en listas durante la ejecución. | Cumple. Los datos de clientes y reservas se reinician al cerrar el programa; el archivo se usa para logs, no como base de datos. |
| Clase abstracta para entidades generales | `EntidadBase` define las operaciones abstractas `validar()` y `obtener_informacion()`. | Cumple en `entidades.py`. |
| Clase `Cliente` con validación y encapsulación | Atributos internos para nombre y correo, propiedades de lectura y validación de formato, contenido y duplicados. | Cumple. El correo se valida sintácticamente; el programa no comprueba que el buzón exista. |
| Clase abstracta `Servicio` y al menos tres servicios derivados | `Servicio` y las clases `ReservaSalas`, `AlquilerEquipos` y `AsesoriasEspecializadas`. | Cumple en `servicios.py`. |
| Polimorfismo para costos, descripciones y validaciones | Las clases concretas implementan sus reglas de `validar()`, `calcular_costo()` y `obtener_informacion()`; la asignación y liberación de inventario se resuelven mediante métodos sobrescritos o heredados. | Cumple mediante llamadas a la interfaz común del servicio. |
| `Reserva` con cliente, servicio, duración y estado; confirmación, cancelación y procesamiento | `Reserva` conserva esos datos y administra los estados `PENDIENTE`, `CONFIRMADA` y `CANCELADA`, además del costo. | Cumple en `reserva.py`. Al cancelar una reserva con inventario se libera la unidad, conservando su identificador para mostrar el historial. |
| Variantes de métodos de cálculo de costos | `ReservaSalas.calcular_costo()` admite variaciones de proyector y catering; `AsesoriasEspecializadas.calcular_costo()` admite nivel y modalidad. | Cumple como variantes de llamada mediante parámetros opcionales. Precisión técnica: `@overload` documenta firmas para analizadores de tipos; Python ejecuta una única implementación por método, no varias sobrecargas dinámicas. |
| Excepciones personalizadas y bloques `try/except`, `else`, `finally` | Excepciones específicas en `excepciones.py`; manejo de errores de dominio e inesperados, `else`, `finally` y encadenamiento con `raise ... from ...` en `reserva.py`. | Cumple. En la creación de reservas, `finally` devuelve el recurso al inventario cuando la operación no se guarda. |
| Registrar errores y eventos en un archivo | `logger.py` configura `app.log`; la interfaz, el gestor y la simulación registran intentos inválidos y eventos relevantes. | Cumple para los flujos previstos del programa. Los logs se anexan al archivo y no se muestran en la consola normal; la simulación sí puede activarlos en pantalla. |
| Manejar registros, servicios y reservas correctos e incorrectos, y continuar ante errores | `simulacion.py` ejecuta 31 operaciones, incluyendo registros inválidos, servicios incorrectos, reservas exitosas y fallidas, cancelaciones y errores encadenados. | Cumple como escenario reproducible. Validación ejecutada: 31 operaciones, 10 exitosas, 21 errores esperados y 0 resultados inesperados. |
| Programa modular, organizado y ejecutable | Responsabilidades separadas en `main.py`, `entidades.py`, `servicios.py`, `reserva.py`, `excepciones.py` y `logger.py`; instrucciones en este README. | Cumple a nivel de estructura y ejecución por consola. |
| Trabajo colaborativo, participación del equipo y evidencia del uso de GitHub | No se deduce de los archivos fuente ni de la simulación local. | Requiere evidencia externa del repositorio: ramas, commits, issues y participación real de los integrantes, de acuerdo con la actividad académica. |
| Documento académico en PDF (portada, introducción, enlace al repositorio, conclusiones y referencias APA) | No forma parte de la aplicación ni de los módulos del programa. | Pendiente como entregable separado; este proyecto no acredita por sí solo la entrega del PDF. |

## Flujo de registro y reservas

### Registro e inicio de sesión

1. `menu_interactivo()` presenta las opciones de inicio de sesión, registro o salida.
2. Durante el registro, `registrar_cliente_interactivo()` recoge el nombre y el correo. La opción `0` cancela el formulario y vuelve al menú inicial.
3. `SistemaGestionFJ.registrar_cliente()` crea el objeto `Cliente`, ejecuta sus validaciones y evita nombres o correos duplicados antes de guardarlo en la lista en memoria.
4. El cliente recién registrado pasa directamente a `menu_cliente()`. Para iniciar sesión, el gestor busca al cliente por nombre o por correo sin distinguir mayúsculas.

### Creación, consulta y cancelación de una reserva

1. Desde el panel, `crear_reserva_cliente()` recoge los datos del servicio y crea el objeto especializado: sala, equipo o asesoría.
2. `SistemaGestionFJ.crear_reserva()` verifica el cliente y el servicio. Si corresponde, asigna una unidad de inventario; luego confirma la reserva y la añade a la lista en memoria.
3. Al confirmar, `Reserva.procesar()` valida el servicio y obtiene el costo mediante el método `calcular_costo()` del tipo de servicio concreto.
4. `mostrar_reservas_cliente()` consulta las reservas del cliente y presenta sus detalles, costo y estado.
5. Para cancelar, `SistemaGestionFJ.cancelar_reserva()` verifica que la reserva exista y pertenezca al cliente activo. `Reserva.cancelar()` cambia su estado y libera la unidad asignada, si existe.

Si la creación falla después de asignar una unidad, el bloque `finally` del gestor la devuelve al inventario. Los errores de dominio se registran mediante `logger.py` y se comunican a la interfaz mediante excepciones del dominio.

## Ejecución

Requiere Python 3.10 o superior. Todos los archivos `.py` del proyecto deben permanecer juntos en la misma carpeta. El nombre y la ubicación de esa carpeta pueden cambiar: las importaciones no dependen de un nombre de carpeta específico.

Desde una terminal situada en esa carpeta, ejecuta:

```text
python main.py
```

Para ver la simulación automática (31 operaciones: registros válidos e inválidos, servicios incorrectos, reservas exitosas y fallidas, cancelaciones y errores encadenados):

```text
python simulacion.py
```

Cada error queda registrado en `app.log` y el programa continúa hasta el resumen final.

En la pantalla inicial se puede iniciar sesión, registrar un cliente o salir. Al registrar, se solicita un nombre y un correo electrónico únicos. El nombre acepta letras y espacios y puede tener hasta 15 letras, sin contar espacios. El correo se revisa con una validación de formato habitual; esta comprobación no confirma que la dirección exista ni que pueda recibir mensajes.

El inicio de sesión permite elegir entre nombre de usuario y correo. Después de autenticarse se abre el panel del cliente, desde el cual puede consultar el catálogo, crear y ver reservas, cancelar las propias, cerrar sesión o salir del programa.

Durante el registro, la opción `0` permite cancelar y volver al menú inicial. Durante la captura de una reserva, la opción `0` permite volver a la selección de servicios sin crearla. Las entradas numéricas se validan; ante texto, datos vacíos, opciones no disponibles o valores fuera de rango, la interfaz explica qué corregir y solicita el dato nuevamente.

## Reservas, validaciones y tarifas

Las reservas pasan por los estados `PENDIENTE`, `CONFIRMADA` y `CANCELADA`. Al crearse, se procesa su costo y queda confirmada. La unidad asignada permanece ocupada hasta cancelar la reserva.

- **Salas:** capacidad de 1 a 25 personas; duración de 1 a 24 horas. Tarifa de $40.000 COP por hora, proyector por $25.000 COP y catering por $15.000 COP/persona. La cantidad de catering puede ser de 0 hasta la capacidad.
- **Equipos:** duración de 1 a 30 días. Laptop: $50.000 COP/día; cámara: $70.000 COP/día; sonido: $60.000 COP/día.
- **Asesorías:** duración de 1 a 8 horas. Tarifa base de $80.000 COP/hora, multiplicada por nivel Junior (1.0x), Senior (1.5x) o Master (2.0x); modalidad presencial agrega $40.000 COP.

Los cálculos de salas aceptan proyector y catering como argumentos opcionales; los de asesorías aceptan nivel y modalidad. Si se omiten, se utilizan los valores guardados en el objeto del servicio.

## Registro de eventos

Los eventos que la aplicación registra —por ejemplo, registros, inicios de sesión, reservas, cancelaciones y errores de entrada o de negocio— se guardan en `app.log`; con `python simulacion.py` también se muestran en la consola. Cada línea incluye fecha, nivel y mensaje. El archivo se crea junto al código al ejecutar el programa, sin importar desde qué carpeta se lance, y acumula entradas; se recomienda no versionar el log generado ni archivos temporales como `__pycache__`.
