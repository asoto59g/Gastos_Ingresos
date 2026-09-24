# Gastos e ingresos

Dashboard personal en Streamlit para revisar movimientos bancarios, clasificar gastos e ingresos y analizar el flujo mensual.

## Funciones principales

- Carga de extractos Excel o CSV desde la barra lateral.
- Uso automático de `Gastos_Ingresos.xlsx` si existe localmente en la carpeta del proyecto.
- Clasificación de movimientos por reglas editables en `classifier.py`.
- Filtros por rango de fechas, tipo de movimiento, categoría y búsqueda literal en la descripción.
- KPIs de ingresos, gastos, balance neto, cantidad de movimientos y saldo al corte.
- Gráficos interactivos por categoría y por mes; al seleccionar puntos se filtra el detalle.
- Descarga del detalle filtrado en CSV.

## Requisitos

- Python 3.10 o superior.
- Git.
- Un entorno virtual recomendado.

Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Ejecución local

```bash
streamlit run app_dashboard.py
```

En Windows también puedes usar:

```cmd
Iniciar_Dashboard.bat
```

## Formato esperado del archivo

El archivo debe incluir estas columnas o nombres equivalentes:

- `Fecha`
- `Descripción` o `Descripcion`
- `Débitos` o `Debitos`
- `Créditos` o `Creditos`

Columnas opcionales:

- `Referencia`
- `Balance`

## Datos privados

Los extractos bancarios y archivos auxiliares locales no deben subirse al repositorio. La app funciona con carga manual desde la barra lateral o con un archivo local llamado `Gastos_Ingresos.xlsx`.

Si necesitas compartir el proyecto, comparte solo el código y deja los datos fuera de Git.

## Estructura

```text
.
├── app_dashboard.py
├── classifier.py
├── requirements.txt
├── .streamlit/
│   └── config.toml
└── Iniciar_Dashboard.bat
```

## Personalización

Para mejorar la clasificación, agrega palabras clave en `classifier.py`. Las transacciones que caen en "Otros" aparecen en un panel de revisión dentro del dashboard.
