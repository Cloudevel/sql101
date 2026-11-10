# Curso básico de SQL para ingeniería y analítica de datos

Curso práctico de 6 horas de *SQL* apegado al estándar *ANSI*. Las consultas se ejecutan directamente en las celdas de notebooks de *Jupyter*, sobre [*DuckDB*](https://duckdb.org), dentro de un contenedor de desarrollo listo para *GitHub Codespaces*.

## Cómo empezar

### En *GitHub Codespaces*

1. En la página del repositorio, selecciona **Code → Codespaces → Create codespace on main**.
2. Espera a que termine la configuración. El contenedor instala las dependencias, genera los datos y crea la base `data/thelook.duckdb`.
3. Abre `01_introduccion.ipynb`, selecciona el *kernel* de *Python* y ejecuta las celdas en orden.

### En tu equipo

Requiere [*VS Code*](https://code.visualstudio.com), la extensión [*Dev Containers*](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) y *Docker*. Clona el repositorio, ábrelo en *VS Code* y selecciona **Reopen in Container**.

Sin contenedor, basta con *Python* 3.10 o superior:

```bash
pip install -r requirements.txt
python scripts/generar_datos.py
python scripts/cargar_datos.py
```

## Temario

| # | Notebook | Contenido | Tiempo |
|---|---|---|---|
| 1 | `01_introduccion.ipynb` | *SQL* en ingeniería y analítica, *ANSI SQL* y dialectos, por qué *DuckDB*, entorno y datos | 0:25 |
| 2 | `02_consultas_basicas.ipynb` | `SELECT`, alias, `DISTINCT`, `WHERE`, `LIKE`, `NULL`, `ORDER BY`, `FETCH FIRST` | 0:50 |
| 3 | `03_agregaciones.ipynb` | `COUNT`, `SUM`, `AVG`, `GROUP BY`, `HAVING`, conteo condicional | 0:40 |
| 4 | `04_joins_y_case.ipynb` | Claves, `INNER` / `LEFT JOIN`, duplicación de filas, `CASE` y pivotes | 0:45 |
| | | *Descanso* | 0:15 |
| 5 | `05_fechas_subconsultas_y_cte.ipynb` | Tipos temporales, `EXTRACT`, `INTERVAL`, subconsultas, `EXISTS`, `WITH`, *CTE* contra subconsultas, `UNION` | 0:50 |
| 6 | `06_funciones_de_ventana.ipynb` | `OVER`, `ROW_NUMBER`, `RANK`, deduplicación, `LAG` / `LEAD`, acumulados y promedios móviles | 0:45 |
| 7 | `07_tablas_vistas_y_carga.ipynb` | Esquemas, `CREATE TABLE`, `CREATE TABLE AS`, vistas, `INSERT`, `UPDATE`, `DELETE`, `MERGE` | 0:35 |
| 8 | `08_denormalizacion.ipynb` | Normalizar contra denormalizar, esquema de estrella, tabla ancha, granularidad y riesgos | 0:25 |
| 9 | `09_apendice_bigquery.ipynb` | Demostración: dialecto *GoogleSQL*, costo por bytes, particionamiento, campos anidados | 0:10 |
| | | Cierre y dudas | 0:20 |
| | `soluciones.ipynb` | Soluciones de los ejercicios de las lecciones 1 a 8 | |

## Enfoque

* **Estándar primero.** Todo el *SQL* de las lecciones 1 a 8 es *ANSI SQL*. Cuando un motor usa otra sintaxis (*BigQuery*, *PostgreSQL*, *SQL Server*, *SQLite*), se explica en una **nota de dialecto**.
* **Ejecutable.** Cada celda que comienza con `%%sql` ([*JupySQL*](https://jupysql.ploomber.io)) es una consulta; lo que sigue a `%%sql` puede copiarse tal cual a otro motor.
* **Datos con propósito.** El generador incluye a propósito clientes sin compras, productos sin ventas, productos sin marca y sin centro de distribución, y órdenes sin enviar, para practicar `LEFT JOIN`, `NOT EXISTS`, `COALESCE` e `IS NULL`.

## Datos

`scripts/generar_datos.py` genera datos sintéticos y deterministas (semilla 2026) con el mismo esquema que el *dataset* público [`bigquery-public-data.thelook_ecommerce`](https://console.cloud.google.com/marketplace/product/bigquery-public-data/thelook-ecommerce), de modo que las consultas pueden ejecutarse también en *BigQuery*. Las marcas y personas son ficticias.

| Tabla | Filas | Contenido |
|---|---|---|
| `distribution_centers` | 10 | Centros de distribución |
| `products` | 2,000 | Catálogo de productos |
| `users` | 15,000 | Clientes |
| `orders` | 24,440 | Órdenes de compra (2021–2025) |
| `order_items` | 39,023 | Artículos de cada orden |

Para restablecer los datos: `python scripts/cargar_datos.py`.

## Notas para el instructor

* Las lecciones 1 a 6 abren `data/thelook.duckdb` en **sólo lectura**, así que pueden tenerse varias abiertas a la vez.
* Las lecciones 7 y 8 y las soluciones escriben en una base de trabajo, `data/curso.duckdb`, que expone los datos del curso como vistas de sólo lectura. *DuckDB* permite un solo proceso de escritura por archivo: si aparece *Could not set lock on file*, hay que cerrar (**Shut Down**) el *kernel* de los otros notebooks que usan `curso.duckdb`.
* Las lecciones 7 y 8 reinician su esquema (`analitica` y `modelo`) al comenzar, así que pueden ejecutarse de nuevo desde el principio.
* El apéndice de *BigQuery* requiere una cuenta de *Google Cloud*; puede presentarse como demostración desde la consola. El *sandbox* gratuito no permite `INSERT`, `UPDATE`, `DELETE` ni `MERGE`.

## Estructura

```
.devcontainer/devcontainer.json   Configuración de Codespaces / Dev Containers
scripts/generar_datos.py          Generador de datos sintéticos
scripts/cargar_datos.py           Carga de los CSV en DuckDB
data/                             CSV y bases de datos generados (no se versionan)
img/                              Imágenes de los notebooks
0X_*.ipynb                        Lecciones
soluciones.ipynb                  Soluciones de los ejercicios
```

## Licencia

El contenido de los notebooks se publica bajo la licencia [*Creative Commons* Atribución 4.0 Internacional](http://creativecommons.org/licenses/by/4.0/). El código se publica bajo la licencia *MIT* (ver `LICENSE`).
