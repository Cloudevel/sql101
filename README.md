# SQL para Ingeniería y Analítica de Datos (sql101)

[![SQL](https://img.shields.io/badge/SQL-ANSI-336791?style=for-the-badge)](https://modern-sql.com/standard)
[![DuckDB](https://img.shields.io/badge/Motor-DuckDB-FFF000?style=for-the-badge&logo=duckdb&logoColor=black)](https://duckdb.org/)
[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Codespaces](https://img.shields.io/badge/GitHub-Codespaces-brightgreen?style=for-the-badge&logo=github&logoColor=white)](https://codespaces.new/Cloudevel/sql101)
[![License](https://img.shields.io/badge/License-CC--BY%204.0-blue.svg?style=for-the-badge)](LICENSE)

Este repositorio contiene el material oficial del taller **sql101 · SQL para Ingeniería y Analítica de Datos** de **Cloudevel®**, impartido por José Luis Chiquete Valdivieso. El taller enseña *SQL* apegado al estándar *ANSI*, desde la primera consulta hasta las transformaciones que se usan en ingeniería de datos: agregaciones, combinación de tablas, fechas, expresiones de tabla comunes, funciones de ventana, carga incremental con `MERGE` y denormalización.

---

## 🗺️ Ruta de Aprendizaje

### Prerrequisitos

Ninguno. No se requiere experiencia previa con *SQL* ni con *Python*: el código de *Python* se limita a la celda de configuración de cada *notebook*.

### Cursos relacionados

| Curso | Título | Repositorio |
| :--- | :--- | :--- |
| GCP301 | *Data Warehousing* con *BigQuery* y *SQL* | [Cloudevel/gcp301](https://github.com/Cloudevel/gcp301) |
| GCP311 | Ingeniería de datos con GCP | [Cloudevel/gcp311](https://github.com/Cloudevel/gcp311) |

---

## 🚀 Acerca del Taller

Un taller de **6 horas** sobre *notebooks* de *Jupyter* que corren en **GitHub Codespaces**. Cada consulta se escribe y se ejecuta directamente en una celda. Al completarlo serás capaz de:

* **Consultar datos:** seleccionar, filtrar, ordenar y manejar valores nulos correctamente.
* **Construir indicadores:** agregaciones, agrupamiento y conteo condicional.
* **Combinar tablas:** `INNER` y `LEFT JOIN`, detectar duplicación de filas y aplicar lógica con `CASE`.
* **Analizar en el tiempo:** fechas, intervalos, subconsultas y expresiones de tabla comunes (`WITH`).
* **Usar funciones de ventana:** rankings, deduplicación, comparación entre periodos y acumulados.
* **Hacer ingeniería de datos con *SQL*:** crear tablas y vistas, y cargar datos con `INSERT`, `UPDATE`, `DELETE` y `MERGE`.
* **Modelar para analítica:** denormalizar sin perder el control de la granularidad.

### 📐 *ANSI SQL* primero

Todo el *SQL* de «Introducción» a «Denormalización» es estándar y funciona, con cambios mínimos, en *PostgreSQL*, *BigQuery*, *Snowflake*, *SQL Server* y otros motores. Cuando un motor usa otra sintaxis, se explica en una **nota de dialecto**.

### 🦆 Motor del taller: *DuckDB*

**En este taller se usa [*DuckDB*](https://duckdb.org)**, un motor analítico que corre dentro del propio *Codespace*, sin servidor ni cuentas. Se eligió porque está muy apegado al estándar (tipos de fecha reales, funciones de ventana, `MERGE`), almacena los datos por columnas como un *data warehouse* y rechaza las consultas inválidas en lugar de aceptarlas en silencio. La comparación con *SQLite*, *PostgreSQL*, *BigQuery* y otras alternativas está en [«Introducción»](01_introduccion.ipynb).

A lo largo del taller se analizan los datos de **TheLook**, una tienda de ropa en línea ficticia: clientes, órdenes, artículos vendidos, productos y centros de distribución.

---

## 📅 Temario y Estructura

| Módulo | Temas | Notebooks |
| :--- | :--- | :--- |
| 1. Fundamentos | *SQL* en ingeniería y analítica, *ANSI SQL*, *DuckDB*, `SELECT`, `WHERE`, `NULL`, `ORDER BY`, `FETCH FIRST` | «Introducción»<br>«Consultas básicas» |
| 2. Resumir y combinar | Agregaciones, `GROUP BY`, `HAVING`, `JOIN`, `CASE` | «Agregaciones»<br>«Combinación de tablas y lógica condicional» |
| 3. Análisis | Fechas e intervalos, subconsultas, *CTE*, funciones de ventana | «Fechas, subconsultas y expresiones de tabla comunes»<br>«Funciones de ventana» |
| 4. Ingeniería de datos | *DDL*, *DML*, `MERGE`, vistas, denormalización | «Tablas, vistas y carga de datos»<br>«Denormalización» |

### Práctica

* Los *notebooks* de «Introducción» a «Denormalización» terminan con **ejercicios** y **retos opcionales**; se trabajan en clase y como práctica.
* Las versiones resueltas están en `soluciones/` (`NN_..._soluciones.ipynb`).

### 📚 Contenidos

#### 🧭 Tabla de contenidos (enlaces rápidos)
- [«Introducción»](01_introduccion.ipynb)
- [«Consultas básicas»](02_consultas_basicas.ipynb)
- [«Agregaciones»](03_agregaciones.ipynb)
- [«Combinación de tablas y lógica condicional»](04_joins_y_case.ipynb)
- [«Fechas, subconsultas y expresiones de tabla comunes»](05_fechas_subconsultas_y_cte.ipynb)
- [«Funciones de ventana»](06_funciones_de_ventana.ipynb)
- [«Tablas, vistas y carga de datos»](07_tablas_vistas_y_carga.ipynb)
- [«Denormalización»](08_denormalizacion.ipynb)

#### 🔹 Módulo 1: Fundamentos
* «Introducción» - tablas, relaciones y álgebra relacional; *OLTP* y *OLAP*; *SQL* en ingeniería y analítica; historia de *SQL* e importancia de *ANSI SQL*; dialectos; por qué *DuckDB* y sus alternativas; entorno, celdas `%%sql` y datos del taller; `INFORMATION_SCHEMA`.
* «Consultas básicas» - `SELECT`, alias y columnas calculadas; `SELECT *` en motores columnares; `DISTINCT`; `WHERE` con `AND`, `OR`, `IN`, `BETWEEN`, `LIKE`; `NULL` y `COALESCE`; `ORDER BY`; `FETCH FIRST` y `LIMIT` (y por qué limitar el resultado no limita la búsqueda); orden lógico de ejecución.

#### 🔹 Módulo 2: Resumir y combinar
* «Agregaciones» - `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`; `GROUP BY` y su regla de oro; `HAVING`; conteo condicional con `CASE` y `FILTER`; `NULLIF`; indicadores de ventas.
* «Combinación de tablas y lógica condicional» - Claves primarias y foráneas; `INNER JOIN` y `LEFT JOIN`; varias tablas; duplicación de filas; `CASE`, agrupamiento por `CASE` y pivotes con agregación condicional.

#### 🔹 Módulo 3: Análisis
* «Fechas, subconsultas y expresiones de tabla comunes» - `DATE`, `TIMESTAMP` e `INTERVAL`; `CAST` y `EXTRACT`; rangos semiabiertos; aritmética de fechas; subconsultas escalares, con `IN`, en `FROM` y correlacionadas con `EXISTS`; `WITH`; *CTE* contra subconsultas; `UNION ALL` y `UNION DISTINCT`.
* «Funciones de ventana» - `OVER` y `PARTITION BY`; agregaciones como ventana; `ROW_NUMBER`, `RANK`, `DENSE_RANK`; deduplicación y último registro; `LAG` y `LEAD`; acumulados y promedios móviles con `ROWS BETWEEN`.

#### 🔹 Módulo 4: Ingeniería de datos
* «Tablas, vistas y carga de datos» - Esquemas; `CREATE TABLE` con restricciones; `CREATE TABLE AS`; vistas; `INSERT`, `UPDATE`, `DELETE`; carga incremental con `MERGE`; `DROP`.
* «Denormalización» - Normalizar para operar y denormalizar para analizar; esquema de estrella y tabla ancha; arquitecturas de Inmon y Kimball; *data warehouses* en la nube; granularidad; validación; medidas de otra granularidad; datos desactualizados.


> **📝 Nota:** Las celdas `-- TU CÓDIGO AQUÍ` y **✍️ Tu respuesta** son para ti. Cada *notebook* es independiente y se puede abrir y ejecutar por separado.

#### 📁 Datos
* `scripts/generar_datos.py` - Genera los datos sintéticos de *TheLook* con un subconjunto compatible del esquema del *dataset* público [`bigquery-public-data.thelook_ecommerce`](https://console.cloud.google.com/marketplace/product/bigquery-public-data/thelook-ecommerce). Son deterministas (semilla 2026): todos los participantes ven los mismos resultados. Incluyen a propósito clientes sin compras, productos sin ventas, productos sin marca y órdenes sin enviar.
* `scripts/cargar_datos.py` - Carga los datos en `data/thelook.duckdb`. Ejecútalo de nuevo para restablecer la base en cualquier momento.

| Tabla | Filas | Contenido |
| :--- | ---: | :--- |
| `distribution_centers` | 10 | Centros de distribución |
| `products` | 2,000 | Catálogo de productos |
| `users` | 15,000 | Clientes |
| `orders` | 24,440 | Órdenes de compra (2021-2025) |
| `order_items` | 39,023 | Artículos de cada orden |

---

## 🛠️ Instalación y Uso

¡Olvídate de configurar entornos locales! Este repositorio está configurado para **GitHub Codespaces**.

### Crear el *Codespace*

1. Haz clic en el botón **"Code"** (verde) arriba a la derecha.
2. Ve a la pestaña **"Codespaces"**.
3. Haz clic en **"Create codespace on main"**.

El entorno se iniciará automáticamente con:
* *Python* 3.12
* Extensiones de *Python* y *Jupyter* para VS Code
* *DuckDB* y *JupySQL* con versiones fijadas en `requirements.txt`
* Los datos del taller ya generados en `data/thelook.duckdb`

La primera vez tarda unos minutos. Después abre [«Introducción»](01_introduccion.ipynb), elige el kernel **Python 3.12** (`/usr/local/bin/python`) en **Select Kernel** y ejecuta las celdas en orden con `Shift + Enter`.

> ⚠️ «Tablas, vistas y carga de datos» y «Denormalización» escriben en una base de trabajo (`data/curso.duckdb`) que sólo un *notebook* puede tener abierta a la vez. Antes de abrir una de ellas, cierra el *kernel* de las otras (**Kernel → Shut Down**). Los *notebooks* de «Introducción» a «Funciones de ventana» abren los datos en sólo lectura y pueden usarse al mismo tiempo.

> 💡 Codespaces se detiene solo tras un rato de inactividad; para no gastar tus horas gratuitas, detenlo al terminar: **github.com/codespaces** → `…` → **Stop codespace**.

### Ejecución Local (Opcional)
Si prefieres trabajar en tu máquina:

```bash
# Clonar el repositorio
git clone https://github.com/Cloudevel/sql101.git
cd sql101

# Crear entorno virtual (Python 3.12)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias y generar los datos
pip install -r requirements.txt
python scripts/generar_datos.py
python scripts/cargar_datos.py

# Iniciar Jupyter
jupyter lab
```

---

## 📖 Recursos Adicionales

* [Documentación oficial de *DuckDB*](https://duckdb.org/docs/)
* [Documentación de *JupySQL*](https://jupysql.ploomber.io/)
* [Referencia de *GoogleSQL* (*BigQuery*)](https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax)
* [Comparación de características de *SQL* entre motores (Modern SQL)](https://modern-sql.com/)
* [Documentación de *PostgreSQL*: compatibilidad con el estándar](https://www.postgresql.org/docs/current/features.html)

---

## 📝 Licencia

Este proyecto está bajo la licencia **Creative Commons Atribución 4.0 Internacional (CC-BY 4.0)**.

**Eres libre de:**
- ✅ Compartir el material en cualquier medio o formato
- ✅ Adaptar, remezclar y crear contenido derivado
- ✅ Usar con fines comerciales

**Con la condición de:**
- 📌 **Atribución:** Debes dar crédito apropiado, proporcionar un enlace a la licencia e indicar si se han realizado cambios.

Para más información, visita: https://creativecommons.org/licenses/by/4.0/

Véase el archivo [LICENSE](LICENSE) para los términos completos.

&copy; José Luis Chiquete Valdivieso. 2017-2026.
