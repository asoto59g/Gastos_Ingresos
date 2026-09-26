"""Reglas de clasificación de movimientos bancarios (colones, Costa Rica)."""

# v1.1 - Subcategorías de Alimentación implementadas
from __future__ import annotations

import unicodedata

INGRESO_PENSION = "Pensión / ROP / CCSS"
INGRESO_FAMILIA = "Pago de hijo / familiares"
INGRESO_LOTERIA = "Ingresos por lotería"
INGRESO_IMPUESTOS = "Reintegro de impuestos"
INGRESO_OTROS = "Otros ingresos / transferencias"

CAT_ALIMENTACION = "Alimentación"
CAT_AGUA = "Agua"
CAT_TELEFONIA = "Telefonía / internet"
CAT_ELECTRICIDAD = "Electricidad"
CAT_LOTERIA = "Lotería"
CAT_IMPUESTOS = "Impuestos / trámites"
CAT_VIAJES = "Viajes / alojamiento"
CAT_DIGITAL = "Servicios digitales / software"
CAT_SALUD = "Salud y cuidado personal"
CAT_SEGUROS = "Seguros (INS)"
CAT_COMPRAS = "Compras / tiendas"
CAT_TRANSPORTE = "Transporte / vehículos"
CAT_EFECTIVO = "Retiro cajero (efectivo)"
CAT_COMISIONES = "Comisiones bancarias / IVA"
CAT_TRANSFERENCIAS = "Transferencias / SINPE"
CAT_OTROS = "Otros servicios y gastos"

# Subcategorías de Alimentación
SUB_ALIMENTACION_RESTAURANTES = "Alimentación: Restaurantes"
SUB_ALIMENTACION_SUPERMERCADOS = "Alimentación: Supermercados"
SUB_ALIMENTACION_CARNICERIAS = "Alimentación: Carnicerías"
SUB_ALIMENTACION_PANADERIAS = "Alimentación: Panaderías"


def normalize_text(value: object) -> str:
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return " ".join(text.lower().replace("_", " ").split())


def _matches(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


# Ingresos: primera coincidencia gana.
_INCOME_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        INGRESO_PENSION,
        (
            "pension",
            "caja seguro social",
            "coop de producc",
            "bcr pension",
        ),
    ),
    (
        INGRESO_FAMILIA,
        ("fabian", "oscar alejandro", "oscar_alejandro"),
    ),
    (
        INGRESO_LOTERIA,
        ("jps", "junta proteccion", "loteria", "rifa"),
    ),
    (
        INGRESO_IMPUESTOS,
        ("impuesto", "reintegro"),
    ),
)

# Subcategorías de Alimentación: se evalúan antes de las categorías principales
_ALIMENTACION_SUBCATEGORIES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        SUB_ALIMENTACION_RESTAURANTES,
        (
            "burger",
            "bar ",
            "taco",
            "tacos",
            "kfc",
            "uber eats",
            "pops",
            "restaurante",
            "restaurant",
            "soda",
            "ceviche",
            "chicharronera",
            "pizza",
            "mc donald",
            "pollos",
            "pollo ",
            "pedidos ya",
            "pedido",
            "comida",
            "marsiqueria",
            "marisqueria",
            "marisco",
            "subway",
            "tramo",
            "batido",
            "casado",
            "cadados",
            "dos gallos",
            "gallo carne",
            "gallito",
            "carne curry",
            "carnes asadas",
            "dowling",
            "copo",
            "chopsuey",
            "chop suey",
            "chowmin",
            "chow min",
            "shopsuey",
            "chalupa",
            "pizzeria",
            "churros",
            "coffee bar",
            "bocadito",
            "olla de barro",
            "mico rico",
            "palenque",
            "cocina criolla",
            "pampero",
        ),
    ),
    (
        SUB_ALIMENTACION_SUPERMERCADOS,
        (
            "minisuper",
            "mini super",
            "supermercado",
            "compre bien",
            "super todo",
            "mega super",
            "maxipali",
            "mxm ",
            "jsm market",
            "kiosco",
            "gessa",
            "bolpa",
            "musmanni",
            "country house",
            "chaparrastique",
            "del valle",
            "cuatro mares",
            "4 mares",
            "pequeno arbol",
            "auto mercado",
            "walmart",
            "perimercado",
            "super compro",
            "quickshop",
            "ue *costa",
            "del vall",
        ),
    ),
    (
        SUB_ALIMENTACION_CARNICERIAS,
        (
            "carniceria",
            "cerdo",
            "arroz",
            "camaron",
            "langosta",
            "pepa",
            "pina de tamal",
            "crema",
            "queso",
            "cuajada",
            "miel",
            "naranja",
            "naranjo",
            "limon",
            "limones",
            "fajitas",
            "pipasa",
        ),
    ),
    (
        SUB_ALIMENTACION_PANADERIAS,
        (
            "panaderia",
            "heladeria",
            "cafeteria",
            "biscocheria",
            "patacon",
            "guacamole",
            "casa almendro",
            "hacienda la pacifica",
            "sr patacon",
        ),
    ),
)

# Gastos: orden de especificidad (evitar 'super' o 'mega' genéricos).
_EXPENSE_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        CAT_COMISIONES,
        (
            "comision",
            "iva -",
            "iva ",
            "valor de tarjeta",
            "comision pin",
            "comision cd sinpe",
            "comision sinpe",
        ),
    ),
    (
        CAT_EFECTIVO,
        ("ret. s/tarjeta", "ret s/tarjeta", "retiro atm", "atm *"),
    ),
    (
        CAT_SEGUROS,
        ("ins en linea", "ins cv"),
    ),
    (
        CAT_AGUA,
        ("pago aya", " aya ", "aya "),
    ),
    (
        CAT_ELECTRICIDAD,
        ("ice sector electricidad", "electricidad"),
    ),
    (
        CAT_TELEFONIA,
        (
            "telecable",
            "ice tel",
            "pase-83",
            "colocell",
        ),
    ),
    (
        CAT_LOTERIA,
        ("jps", "junta proteccion", "pago rifa", "rifa", "chances", "chance"),
    ),
    (
        CAT_DIGITAL,
        (
            "microsoft",
            "google",
            "openai",
            "cursor",
            "dronelink",
            "webodm",
            "dji",
            "laptop",
            "reparacion laptop",
            "sinpe movil video",
            "sinpe movil videos",
            "paypal",
            "uber *one",
            "uber one",
            "allmapsoft",
            "deserltd",
            "iqtest",
            "namecominc",
            "sortlek",
            "windy",
            "uav forecast",
            "bateria",
        ),
    ),
    (
        CAT_SALUD,
        (
            "farmacia",
            "farmavalue",
            "macrosalud",
            "macro salud",
            "macrob",
            "macrobiotica",
            "salutem",
            "hospital clinica",
            "cita hosp",
            "clinica",
            "medico",
            "dr ",
            "quiropractica",
            "asociacion de servicios medico",
            "corte pelo",
            "sinpe movil corte",
            "sinpe movil pelo",
            "super salon",
            "veterinaria",
            "optica",
            "duretan",
            "vasenilla",
            " gel",
            "gel ",
        ),
    ),
    (
        CAT_TRANSPORTE,
        (
            "estacion de serv",
            "servicentro",
            "lubricentro",
            "guacamaya",
            "taller",
            "uber rides",
            "global via",
            "parquimetro",
            "parqueo",
            " parq",
            "kia",
            "rev tv",
            "auto servicio",
            "ciclo taller",
            "dekra",
            "sinpe movil taxi",
            "sinpe movil gas",
            "sinpe movil frenos",
            "bici",
            "bqr000",
        ),
    ),
    (
        CAT_VIAJES,
        ("hotel", "casa tamarindo"),
    ),
    (
        CAT_ALIMENTACION,
        (
            "burger",
            "bar ",
            "taco",
            "tacos",
            "tamal",
            "tamales",
            "vigoron",
            "vigorones",
            "fresco",
            "frescos",
            "jugo",
            "tilapia",
            "minisuper",
            "mini super",
            "supermercado",
            "compre bien",
            "kfc",
            "pul p",
            "uber eats",
            "pops",
            "restaurante",
            "restaurant",
            "soda",
            "ceviche",
            "chicharronera",
            "pizza",
            "mc donald",
            "pollos",
            "pollo ",
            "pedidos ya",
            "pedido",
            "comida",
            "marsiqueria",
            "marisqueria",
            "marisco",
            "subway",
            "tramo",
            "carniceria",
            "batido",
            "casado",
            "cadados",
            "arroz",
            "camaron",
            "langosta",
            "dos gallos",
            "gallo carne",
            "gallito",
            "carne curry",
            "carnes asadas",
            "dowling",
            "copo",
            "chopsuey",
            "chop suey",
            "chowmin",
            "chow min",
            "shopsuey",
            "chalupa",
            "crema",
            "pepa",
            "pina de tamal",
            "cerdo",
            "naranja",
            "naranjo",
            "queso",
            "cuajada",
            "miel",
            "limon",
            "limones",
            "fajitas",
            "gessa",
            "maxipali",
            "mxm ",
            "jsm market",
            "panaderia",
            "kiosco",
            "heladeria",
            "cafeteria",
            "biscocheria",
            "patacon",
            "guacamole",
            "mega super",
            "super todo",
            "bolpa",
            "musmanni",
            "country house",
            "chaparrastique",
            "del valle",
            "cuatro mares",
            "4 mares",
            "cocina criolla",
            "pampero",
            "pipasa",
            "sr patacon",
            "pequeno arbol",
            "auto mercado",
            "walmart",
            "perimercado",
            "super compro",
            "quickshop",
            "pizzeria",
            "churros",
            "coffee bar",
            "bocadito",
            "olla de barro",
            "mico rico",
            "palenque",
            "casa almendro",
            "hacienda la pacifica",
            "ue *costa",
            "del vall",
            "tacos",
            "cuajada",
            "gallos",
            "tamales",
            "miel",
            "chow_min",
            "chowmin",
            "comida",
            "frescos",
            "tamal",
            "mangos",
            "limones",
            "carne",
            "vigorones",
            "gallito",
            "downling",
        ),
    ),
    (
        CAT_IMPUESTOS,
        (
            "municipalidad",
            "disolucion socieda",
            "impuestos",
            "impuesto",
            "copia",
        ),
    ),
    (
        CAT_COMPRAS,
        (
            "tienda",
            "best brands",
            "colono",
            "ferreteria",
            "ferretera",
            "sur quimica",
            "mundo",
            "ekono",
            "sauko",
            "zauko",
            "monge",
            "xiaomi",
            "retail",
            "alm el rey",
            "bazar",
            "matas",
            "souvenir",
            "intelec",
            "distribuidora",
            "distjose",
            "agropecuaria",
            "e commerce",
            "ecommerce",
            "temu",
            "leonisa",
            "novex",
            "pasatelas",
            "tecni color",
            "bellitec",
            "mangas",
            "maceta",
            "hormiga maceta",
            "sinpe movil compras",
            "video electronica",
            "pequeno mundo",
            "mega bodega",
            "do it center",
            "steren",
            "radioshack",
            "cerrajeria",
            "calzado",
            "ropa american",
            "variedades",
        ),
    ),
    (
        CAT_TRANSFERENCIAS,
        ("sinpe", "tef ", "tef de", "tef a"),
    ),
)


def classify_transaction(descripcion: object, debitos: float, creditos: float) -> str:
    text = normalize_text(descripcion)
    is_income = float(creditos or 0) > float(debitos or 0)

    if is_income:
        for category, keywords in _INCOME_RULES:
            if _matches(text, keywords):
                return category
        return INGRESO_OTROS

    # Primero verificar subcategorías de alimentación
    for subcategory, keywords in _ALIMENTACION_SUBCATEGORIES:
        if _matches(text, keywords):
            return subcategory

    # Hotel con restaurante es comida, no hospedaje.
    if "restaurant" in text:
        return SUB_ALIMENTACION_RESTAURANTES

    for category, keywords in _EXPENSE_RULES:
        if _matches(text, keywords):
            return category
    return CAT_OTROS
