<img width="1273" height="499" alt="preview" src="https://github.com/user-attachments/assets/82d6785b-1d79-41cf-ac23-975ffdef20f5" />

# Gastos e ingresos
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Framework](https://img.shields.io/badge/framework-Streamlit-FF4B4B.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Maintenance](https://img.shields.io/badge/maintained%3F-yes-brightgreen.svg)

Dashboard personal en Streamlit para revisar movimientos bancarios, clasificar gastos e ingresos y analizar el flujo mensual.

Link app:  https://gastosingresos-ee8ss32ejf9hhayd8xvohi.streamlit.app/

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

El archivo debe incluir estas columnas o nombres equivalentes y no contener encabezados de resumen del banco u otros datos:

- `Fecha`
- `Descripción` o `Descripcion`
- `Débitos` o `Debitos`
- `Créditos` o `Creditos`

Columnas opcionales:

- `Referencia`
- `Balance`

## Datos privados

Los extractos bancarios y archivos auxiliares locales no deben subirse al repositorio. La app funciona con carga manual desde la barra lateral o con un archivo local llamado `Transacciones_Sinteticas_1000_6Meses.xlsx`.

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

## Subcategorías de Alimentación

La categoría "Alimentación" ahora incluye subcategorías para un análisis más detallado:

- **Restaurantes**: Comidas en restaurantes, sodas, fast food, delivery (Uber Eats, Pedidos Ya)
- **Supermercados**: Compras en supermercados, minimercados, tiendas de abarrotes
- **Carnicerías**: Compras específicas de carnes y productos cárnicos
- **Panaderías**: Panaderías, heladerías, cafeterías, biscocherías

Los gráficos principales muestran "Alimentación" como una categoría unificada, mientras que hay una sección específica de "Desglose de Alimentación" que muestra el promedio mensual por subcategoría. En el detalle de movimientos se muestra la subcategoría específica (ej: "Alimentación: Restaurantes").

## Cambios recientes

- **v1.1**: Implementación de subcategorías para la categoría Alimentación
  - Nuevas constantes en `classifier.py` para subcategorías
  - Reglas de clasificación específicas para cada subcategoría
  - Actualización de `app_dashboard.py` para mostrar desglose de subcategorías
  - Cálculo de promedio mensual por subcategoría en lugar de acumulado del periodo
  - Corrección de formato de line endings para compatibilidad con Streamlit Cloud
  - Actualización: redeploy forzado para corregir error de importación
