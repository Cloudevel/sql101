"""Carga los CSV generados por ``generar_datos.py`` en una base de datos DuckDB.

Uso:
    python scripts/cargar_datos.py [--csv data/csv]

Crea ``data/thelook.duckdb``. Si la base ya existe,
se reemplaza, lo que permite volver al estado inicial en cualquier momento.
"""

import argparse
from pathlib import Path

import duckdb

ESQUEMA = """
CREATE TABLE distribution_centers (
  id INTEGER PRIMARY KEY,
  name VARCHAR NOT NULL,
  latitude DOUBLE PRECISION,
  longitude DOUBLE PRECISION
);
CREATE TABLE products (
  id INTEGER PRIMARY KEY,
  cost DECIMAL(10, 2),
  category VARCHAR,
  name VARCHAR,
  brand VARCHAR,
  retail_price DECIMAL(10, 2),
  department VARCHAR,
  sku VARCHAR,
  distribution_center_id INTEGER REFERENCES distribution_centers (id)
);
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  first_name VARCHAR,
  last_name VARCHAR,
  email VARCHAR,
  age INTEGER,
  gender VARCHAR,
  state VARCHAR,
  country VARCHAR,
  traffic_source VARCHAR,
  created_at TIMESTAMP
);
CREATE TABLE orders (
  order_id INTEGER PRIMARY KEY,
  user_id INTEGER REFERENCES users (id),
  status VARCHAR,
  gender VARCHAR,
  created_at TIMESTAMP,
  returned_at TIMESTAMP,
  shipped_at TIMESTAMP,
  delivered_at TIMESTAMP,
  num_of_item INTEGER
);
CREATE TABLE order_items (
  id INTEGER PRIMARY KEY,
  order_id INTEGER REFERENCES orders (order_id),
  user_id INTEGER REFERENCES users (id),
  product_id INTEGER REFERENCES products (id),
  status VARCHAR,
  created_at TIMESTAMP,
  shipped_at TIMESTAMP,
  delivered_at TIMESTAMP,
  returned_at TIMESTAMP,
  sale_price DECIMAL(10, 2)
);
"""

TABLAS = ["distribution_centers", "products", "users", "orders", "order_items"]


def cargar_duckdb(ruta_db, carpeta_csv):
    con = duckdb.connect(str(ruta_db))
    con.execute(ESQUEMA)
    for tabla in TABLAS:
        archivo = (carpeta_csv / f"{tabla}.csv").as_posix()
        con.execute(f"INSERT INTO {tabla} SELECT * FROM read_csv('{archivo}', header = true, nullstr = '')")
    return con


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--csv", default="data/csv", help="carpeta con los CSV")
    args = parser.parse_args()

    carpeta_csv = Path(args.csv)
    ruta_db = Path("data") / "thelook.duckdb"
    for archivo in [ruta_db, Path(f"{ruta_db}.wal")]:
        archivo.unlink(missing_ok=True)

    con = cargar_duckdb(ruta_db, carpeta_csv)
    for tabla in TABLAS:
        n = con.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
        print(f"{tabla:<22}{n:>8,} filas")
    con.close()
    print(f"Base de datos creada en {ruta_db}")


if __name__ == "__main__":
    main()
