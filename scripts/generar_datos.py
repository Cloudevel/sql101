"""Genera un conjunto de datos sintético con un subconjunto compatible del esquema de ``thelook_ecommerce``.

Las tablas son ``distribution_centers``, ``products``, ``users``, ``orders`` y
``order_items``, con nombres de columnas compatibles con el *dataset* público de
BigQuery ``bigquery-public-data.thelook_ecommerce``. Los datos son ficticios
(marcas y personas inventadas) y deterministas: con la misma semilla se obtienen
siempre los mismos registros, de modo que todos los participantes ven los
mismos resultados.

Uso:
    python scripts/generar_datos.py [--salida data/csv] [--semilla 2026]
"""

import argparse
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

N_PRODUCTOS = 2_000
N_USUARIOS = 15_000
INICIO = datetime(2021, 1, 1)
FIN = datetime(2025, 12, 31, 23, 59, 59)

CENTROS = [
    (1, "Memphis TN", 35.1174, -89.9711),
    (2, "Chicago IL", 41.8369, -87.6847),
    (3, "Houston TX", 29.7604, -95.3698),
    (4, "Los Angeles CA", 34.05, -118.25),
    (5, "New Orleans LA", 29.95, -90.0667),
    (6, "Port Authority of New York/New Jersey NY/NJ", 40.634, -73.7834),
    (7, "Philadelphia PA", 39.95, -75.1667),
    (8, "Mobile AL", 30.6944, -88.0431),
    (9, "Charleston SC", 32.7833, -79.9333),
    (10, "Savannah GA", 32.0167, -81.1167),
]

# categoría: (departamentos, precio mínimo, precio máximo, sustantivos para el nombre)
CATEGORIAS = {
    "Jeans": (["Men", "Women"], 25, 180, ["Denim Jeans", "Slim Fit Jeans", "Bootcut Jeans", "Skinny Denim"]),
    "Pants": (["Men", "Women"], 20, 120, ["Chino Pants", "Cargo Pants", "Dress Pants"]),
    "Shorts": (["Men", "Women"], 12, 70, ["Denim Shorts", "Board Shorts", "Athletic Shorts"]),
    "Tops & Tees": (["Men", "Women"], 8, 60, ["Crew Tee", "V-Neck Tee", "Tank Top", "Henley"]),
    "Sweaters": (["Men", "Women"], 25, 200, ["Cardigan", "Crewneck Sweater", "Turtleneck"]),
    "Fashion Hoodies & Sweatshirts": (["Men", "Women"], 20, 110, ["Pullover Hoodie", "Zip Hoodie", "Fleece Sweatshirt"]),
    "Outerwear & Coats": (["Men", "Women"], 50, 600, ["Parka", "Trench Coat", "Puffer Jacket", "Wool Coat"]),
    "Active": (["Men", "Women"], 15, 90, ["Training Top", "Running Tights", "Track Jacket"]),
    "Swim": (["Men", "Women"], 15, 120, ["Swim Trunks", "Bikini Set", "One-Piece Swimsuit"]),
    "Sleep & Lounge": (["Men", "Women"], 12, 80, ["Pajama Set", "Lounge Pants", "Robe"]),
    "Socks": (["Men", "Women"], 4, 25, ["Crew Socks", "Ankle Socks", "Wool Socks"]),
    "Accessories": (["Men", "Women"], 6, 150, ["Leather Belt", "Beanie", "Scarf", "Sunglasses"]),
    "Underwear": (["Men"], 8, 45, ["Boxer Briefs", "Trunks"]),
    "Suits & Sport Coats": (["Men"], 120, 900, ["Two-Piece Suit", "Sport Coat", "Blazer"]),
    "Intimates": (["Women"], 10, 70, ["Bralette", "Lace Bra", "Briefs"]),
    "Dresses": (["Women"], 25, 300, ["Maxi Dress", "Wrap Dress", "Cocktail Dress"]),
    "Skirts": (["Women"], 18, 120, ["Pleated Skirt", "Denim Skirt", "Midi Skirt"]),
    "Leggings": (["Women"], 12, 80, ["High-Rise Leggings", "Yoga Leggings"]),
    "Blazers & Jackets": (["Women"], 40, 350, ["Tailored Blazer", "Denim Jacket", "Bomber Jacket"]),
}

MARCAS = [
    "Altamira", "Bosque Norte", "Cobalto", "Duna", "Estuario", "Faro Azul", "Granito",
    "Hilo Fino", "Ibérica", "Jacaranda", "Kalma", "Lince", "Marea", "Nogal", "Ónix",
    "Pampa", "Quetzal", "Roble", "Sierra Alta", "Tule", "Umbral", "Valle Claro",
    "Xalapa Co.", "Yute", "Zenzontle",
]
ADJETIVOS = ["Classic", "Essential", "Vintage", "Modern", "Relaxed", "Premium", "Everyday", "Urban", "Organic Cotton"]

# país: (peso, estados o provincias)
PAISES = {
    "United States": (33, ["California", "Texas", "New York", "Florida", "Illinois", "Washington", "Ohio", "Georgia"]),
    "China": (22, ["Guangdong", "Shanghai", "Beijing", "Zhejiang", "Jiangsu"]),
    "Brasil": (14, ["São Paulo", "Rio de Janeiro", "Minas Gerais", "Bahia", "Paraná"]),
    "South Korea": (5, ["Seoul", "Busan", "Incheon"]),
    "France": (5, ["Île-de-France", "Provence-Alpes-Côte d'Azur", "Auvergne-Rhône-Alpes"]),
    "United Kingdom": (5, ["England", "Scotland", "Wales"]),
    "Germany": (4, ["Bayern", "Berlin", "Hamburg", "Hessen"]),
    "Spain": (4, ["Madrid", "Cataluña", "Andalucía", "Valencia"]),
    "Japan": (3, ["Tokyo", "Osaka", "Kanagawa"]),
    "Australia": (3, ["New South Wales", "Victoria", "Queensland"]),
    "Mexico": (2, ["Ciudad de México", "Jalisco", "Nuevo León", "Puebla"]),
}

NOMBRES_F = ["Ana", "María", "Lucía", "Sofía", "Emma", "Olivia", "Mia", "Laura", "Camila", "Valentina",
             "Julia", "Sara", "Chloe", "Hana", "Yuna", "Lena", "Isabel", "Paula", "Grace", "Mei"]
NOMBRES_M = ["Juan", "Carlos", "Luis", "Mateo", "Lucas", "Liam", "Noah", "Diego", "Pedro", "Daniel",
             "Javier", "Hugo", "Leo", "Ethan", "Kenji", "Min-jun", "Felix", "Tomás", "Wei", "Jacob"]
APELLIDOS = ["García", "Martínez", "López", "Hernández", "Smith", "Johnson", "Brown", "Silva", "Santos",
             "Oliveira", "Wang", "Li", "Zhang", "Kim", "Park", "Müller", "Schmidt", "Dubois", "Martin",
             "Tanaka", "Sato", "Jones", "Williams", "Pérez", "Sánchez", "Romero", "Costa", "Chen"]
ORIGENES = [("Search", 70), ("Organic", 15), ("Facebook", 6), ("Email", 5), ("Display", 4)]
ESTADOS_ORDEN = [("Complete", 25), ("Shipped", 30), ("Processing", 20), ("Cancelled", 15), ("Returned", 10)]

FORMATO = "%Y-%m-%d %H:%M:%S"


def fecha(dt):
    return dt.strftime(FORMATO) if dt else ""


def momento_aleatorio(rng, inicio, fin):
    segundos = int((fin - inicio).total_seconds())
    return inicio + timedelta(seconds=rng.randint(0, max(segundos, 0)))


def elegir(rng, pares):
    valores, pesos = zip(*pares)
    return rng.choices(valores, weights=pesos)[0]


def generar_productos(rng):
    productos = []
    for pid in range(1, N_PRODUCTOS + 1):
        categoria = rng.choice(list(CATEGORIAS))
        departamentos, pmin, pmax, sustantivos = CATEGORIAS[categoria]
        departamento = rng.choice(departamentos)
        # Algunos productos no tienen marca registrada (para practicar COALESCE).
        marca = rng.choice(MARCAS) if rng.random() > 0.01 else None
        nombre = f"{marca + ' ' if marca else ''}{rng.choice(ADJETIVOS)} {rng.choice(sustantivos)}"
        precio = round(rng.uniform(pmin, pmax), 2)
        costo = round(precio * rng.uniform(0.35, 0.6), 2)
        # Unos cuantos productos sin centro de distribución asignado (para practicar LEFT JOIN).
        centro = rng.randint(1, len(CENTROS)) if rng.random() > 0.005 else None
        productos.append({
            "id": pid, "cost": costo, "category": categoria, "name": nombre, "brand": marca,
            "retail_price": precio, "department": departamento, "sku": f"SKU{pid:06d}",
            "distribution_center_id": centro,
        })
    return productos


def generar_usuarios(rng):
    paises = [(p, peso) for p, (peso, _) in PAISES.items()]
    usuarios = []
    for uid in range(1, N_USUARIOS + 1):
        genero = rng.choice(["F", "M"])
        nombre = rng.choice(NOMBRES_F if genero == "F" else NOMBRES_M)
        apellido = rng.choice(APELLIDOS)
        pais = elegir(rng, paises)
        usuarios.append({
            "id": uid, "first_name": nombre, "last_name": apellido,
            "email": f"{nombre}.{apellido}{uid}@example.com".lower(),
            "age": rng.randint(12, 70), "gender": genero,
            "state": rng.choice(PAISES[pais][1]), "country": pais,
            "traffic_source": elegir(rng, ORIGENES),
            "created_at": momento_aleatorio(rng, INICIO, FIN - timedelta(days=30)),
        })
    return usuarios


def generar_ordenes(rng, usuarios, productos):
    # Las ventas crecen con el tiempo y tienen un pico en noviembre y diciembre.
    def peso_mes(dt):
        crecimiento = 1 + (dt.year - INICIO.year) * 0.35
        temporada = 1.6 if dt.month in (11, 12) else 1.0
        return crecimiento * temporada

    # Cada cliente compra en el departamento de su género, como en thelook_ecommerce.
    # Los productos con id múltiplo de 50 nunca se venden (para practicar anti-joins).
    por_departamento = {"Women": [], "Men": []}
    for p in productos:
        if p["id"] % 50 != 0:
            por_departamento[p["department"]].append(p)

    ordenes, articulos = [], []
    order_id = item_id = 0
    for u in usuarios:
        # Alrededor del 20 % de los clientes nunca compra (para practicar LEFT JOIN).
        n_ordenes = rng.choices([0, 1, 2, 3, 4, 5, 6], weights=[20, 40, 18, 10, 6, 4, 2])[0]
        for _ in range(n_ordenes):
            while True:
                creada = momento_aleatorio(rng, u["created_at"], FIN)
                if rng.random() < peso_mes(creada) / 3.5:
                    break
            estado = elegir(rng, ESTADOS_ORDEN)
            enviada = entregada = devuelta = None
            if estado in ("Shipped", "Complete", "Returned"):
                enviada = creada + timedelta(hours=rng.randint(4, 72))
            if estado in ("Complete", "Returned"):
                entregada = enviada + timedelta(hours=rng.randint(24, 120))
            if estado == "Returned":
                devuelta = entregada + timedelta(days=rng.randint(2, 20))
            n_articulos = rng.choices([1, 2, 3, 4], weights=[60, 25, 10, 5])[0]
            order_id += 1
            ordenes.append({
                "order_id": order_id, "user_id": u["id"], "status": estado, "gender": u["gender"],
                "created_at": creada, "returned_at": devuelta, "shipped_at": enviada,
                "delivered_at": entregada, "num_of_item": n_articulos,
            })
            catalogo = por_departamento["Women" if u["gender"] == "F" else "Men"]
            for _ in range(n_articulos):
                p = rng.choice(catalogo)
                item_id += 1
                articulos.append({
                    "id": item_id, "order_id": order_id, "user_id": u["id"], "product_id": p["id"],
                    "status": estado, "created_at": creada, "shipped_at": enviada,
                    "delivered_at": entregada, "returned_at": devuelta, "sale_price": p["retail_price"],
                })
    return ordenes, articulos


def escribir_csv(ruta, filas, columnas):
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(columnas)
        for fila in filas:
            w.writerow(["" if fila[c] is None else (fecha(fila[c]) if isinstance(fila[c], datetime) else fila[c])
                        for c in columnas])


COLUMNAS = {
    "distribution_centers": ["id", "name", "latitude", "longitude"],
    "products": ["id", "cost", "category", "name", "brand", "retail_price", "department", "sku",
                 "distribution_center_id"],
    "users": ["id", "first_name", "last_name", "email", "age", "gender", "state", "country",
              "traffic_source", "created_at"],
    "orders": ["order_id", "user_id", "status", "gender", "created_at", "returned_at", "shipped_at",
               "delivered_at", "num_of_item"],
    "order_items": ["id", "order_id", "user_id", "product_id", "status", "created_at", "shipped_at",
                    "delivered_at", "returned_at", "sale_price"],
}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--salida", default="data/csv", help="carpeta de salida de los CSV")
    parser.add_argument("--semilla", type=int, default=2026)
    args = parser.parse_args()

    rng = random.Random(args.semilla)
    salida = Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)

    centros = [dict(zip(COLUMNAS["distribution_centers"], c)) for c in CENTROS]
    productos = generar_productos(rng)
    usuarios = generar_usuarios(rng)
    ordenes, articulos = generar_ordenes(rng, usuarios, productos)

    for tabla, filas in [("distribution_centers", centros), ("products", productos), ("users", usuarios),
                         ("orders", ordenes), ("order_items", articulos)]:
        escribir_csv(salida / f"{tabla}.csv", filas, COLUMNAS[tabla])
        print(f"{tabla:<22}{len(filas):>8,} filas")


if __name__ == "__main__":
    main()
