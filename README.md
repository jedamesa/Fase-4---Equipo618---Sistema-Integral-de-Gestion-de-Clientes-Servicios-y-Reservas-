# Sistema de Gestión - Software FJ 

Este repositorio contiene el desarrollo del **Ejercicio 1: Sistema Integral de Gestión de Clientes, Servicios y Reservas** correspondiente a la Fase 4 (Componente Práctico) del curso de Programación Orientada a Objetos.

##  Descripción del Proyecto
Software FJ es una aplicación de consola desarrollada en Python que permite gestionar clientes y tres tipos de servicios (Reserva de Salas, Alquiler de Equipos y Asesorías Especializadas). 

El sistema está diseñado con una arquitectura robusta orientada a objetos (POO) y no utiliza bases de datos externas. Su característica principal es el **manejo avanzado de excepciones**, garantizando que la aplicación nunca colapse ante errores de digitación, reglas de negocio o fallos del sistema.

##  Decisiones de Arquitectura y Diseño
Para cumplir rigurosamente con los requerimientos de la guía y rúbrica de evaluación, se tomaron las siguientes decisiones de diseño:
- **Persistencia en Memoria:** Los objetos (clientes, servicios, reservas) se gestionan mediante listas en tiempo de ejecución.
- **Pool de Recursos (Inventario):** El alquiler de equipos funciona con un sistema dinámico de asignación y liberación automática de unidades (de la unidad 01 a la 99).
- **Registro de Logs (Trazabilidad):** Todo evento, éxito o fallo, se registra de forma persistente en el archivo `app.log` utilizando el módulo nativo `logging`, separando los errores del usuario de los errores internos.
- **Resiliencia y Control de Flujo:** Se implementó una jerarquía de excepciones personalizadas (`ClienteError`, `ServicioError`, `DisponibilidadError`, etc.) y bloques estructurados de `try/except/else/finally` con encadenamiento de errores.

##  Cómo ejecutar y evaluar el programa
Para probar el sistema, descarga o clona este repositorio y ejecuta el archivo principal desde tu terminal de Python:

```bash
python main.py
