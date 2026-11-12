# Instructor Guide - sql101

Guía operativa para impartir **sql101 · SQL para Ingeniería y Analítica de Datos** con consistencia técnica y pedagógica. El material no fija fechas ni horarios para que sirva en cualquier edición.

## Estructura (6 horas, 8 *notebooks*)

Los *notebooks* se numeran por tema, en orden. Cada uno es independiente: tiene su propia celda de configuración y puede abrirse y ejecutarse por separado. Los *notebooks* de «Introducción» a «Denormalización» tienen su versión resuelta en `soluciones/NN_tema_soluciones.ipynb`, que es una copia completa de la lección con las soluciones.

**Estándar del taller:** todo el *SQL* de «Introducción» a «Denormalización» es *ANSI SQL*. Dilo explícitamente al inicio: el motor es *DuckDB*, pero lo que se aprende sirve en cualquier motor. Lo que no es estándar aparece en **notas de dialecto**; no lo enseñes como sintaxis principal.

**Motor:** *DuckDB*, dentro del *Codespace*. No requiere cuentas ni conexión a la nube.

**Datos:** *TheLook*, tienda de ropa ficticia, generada por `scripts/generar_datos.py` con semilla fija: todos ven los mismos resultados. El esquema replica `bigquery-public-data.thelook_ecommerce`.

**Proporción:** cerca de 50% explicación con ejemplos ejecutados, 40% ejercicios en clase y 10% cierre, dudas y práctica.

## Objetivo y agenda

**Objetivo:** Que el participante escriba consultas *ANSI SQL* para responder preguntas de negocio y para transformar datos en tablas listas para analítica.

Al terminar, el participante podrá:
1. Consultar, filtrar y ordenar datos, manejando `NULL` correctamente.
2. Construir indicadores con agregaciones y combinar tablas sin duplicar filas.
3. Trabajar con fechas e intervalos y estructurar consultas complejas con *CTE*.
4. Usar funciones de ventana para rankings, deduplicación y comparación entre periodos.
5. Crear tablas y vistas, y cargar datos de forma incremental con `MERGE`.
6. Diseñar una tabla denormalizada y validar su granularidad.

**Agenda (360 min):**

| Min | Bloque | Notebook |
|---|---|---|
| 25 | Tablas y relaciones, *SQL* en ingeniería y analítica, *ANSI SQL*, *DuckDB*, entorno y datos | «Introducción» |
| 50 | Consultas básicas y ejercicios 1 a 4 | «Consultas básicas» |
| 40 | Agregaciones y ejercicios 1 a 3 | «Agregaciones» |
| 45 | `JOIN`, duplicación de filas, `CASE` y ejercicios 1 a 3 | «Combinación de tablas y lógica condicional» |
| 15 | Descanso | |
| 50 | Fechas, subconsultas, *CTE* contra subconsultas y ejercicios 1 a 3 | «Fechas, subconsultas y expresiones de tabla comunes» |
| 45 | Funciones de ventana y ejercicios 1 a 3 | «Funciones de ventana» |
| 35 | Tablas, vistas, *DML*, `MERGE` y ejercicios 1 y 2 | «Tablas, vistas y carga de datos» |
| 25 | Denormalización y ejercicios 1 y 2 | «Denormalización» |
| 30 | Cierre, dudas y práctica sugerida | |

Los ejercicios que no alcancen a resolverse en clase quedan como práctica; los retos son siempre opcionales.

## Mensajes clave por *notebook*

- «Introducción»: el estándar es lo que se aprende; el motor es la herramienta. Mostrar la tabla de alternativas.
- «Consultas básicas»: `NULL` no es igual a nada (ni a `NULL`). `FETCH FIRST` y `LIMIT` recortan el resultado, no la búsqueda.
- «Agregaciones»: la regla de oro de `GROUP BY`. Mostrar que *DuckDB* rechaza la consulta inválida que *SQLite* aceptaría.
- «Combinación de tablas y lógica condicional»: identificar la granularidad de cada tabla antes de combinar.
- «Fechas, subconsultas y expresiones de tabla comunes»: rangos semiabiertos para fechas; *CTE* para pasos de transformación, subconsultas para filtros cortos.
- «Funciones de ventana»: `ROW_NUMBER` + filtro es el patrón de deduplicación más usado en ingeniería de datos.
- «Tablas, vistas y carga de datos»: `MERGE` es la base de la carga incremental; deduplicar el lote antes de aplicarlo.
- «Denormalización»: una tabla denormalizada debe tener exactamente las filas de su tabla de hechos.

## Checklist previa a clase

- Recordar a los alumnos que traigan una cuenta de GitHub con horas disponibles de *Codespaces*.
- *Codespace* creado desde `main`; `postCreateCommand` terminado y `data/thelook.duckdb` presente.
- Workflow `notebooks-smoke.yml` en verde: los *notebooks* de «Introducción» a «Denormalización» y sus soluciones corren de principio a fin.
- Material de la sesión publicado.

## Checklist de cierre de sesión

- Se cubrieron los objetivos de la sesión.
- Asistencia registrada.
- Grabación y práctica publicadas.
- Dudas frecuentes registradas para mejorar los *notebooks*.

## Riesgos comunes y mitigación

- ***Could not set lock on file*:** otro *notebook* tiene abierta en escritura la base `data/curso.duckdb` («Tablas, vistas y carga de datos», «Denormalización» y sus soluciones). Cerrar su *kernel* con **Kernel → Shut Down**. Los *notebooks* de «Introducción» a «Funciones de ventana» abren los datos en sólo lectura y no causan este error.
- **Datos modificados o dañados:** ejecutar `python scripts/cargar_datos.py` en la terminal para restablecer `data/thelook.duckdb`. Para reiniciar la base de trabajo, borrar `data/curso.duckdb`.
- **Error al repetir «Tablas, vistas y carga de datos» o «Denormalización»:** cada lección reinicia su esquema (`analitica` o `modelo`) al comenzar; ejecutar desde la celda de configuración, en orden.
- **Alumnos que copian consultas a otro motor:** es lo esperado. Si algo falla, revisar las notas de dialecto (comillas, `FETCH FIRST`, fechas).
- **Resultados vacíos inesperados:** casi siempre es una comparación con `= NULL` o un filtro de texto con mayúsculas distintas.
- **Cambios del ecosistema:** las versiones están fijadas en `requirements.txt`; no actualizar durante una edición. `MERGE` requiere *DuckDB* 1.4 o superior.
- **Tiempo insuficiente:** priorizar de «Consultas básicas» a «Funciones de ventana»; «Tablas, vistas y carga de datos» y «Denormalización» pueden presentarse como demostración, y los retos quedan como práctica.
