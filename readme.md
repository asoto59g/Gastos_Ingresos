# Gastos_Ingresos

Aplicación web desarrollada con **Python y Streamlit** para el registro y control de **ingresos y gastos personales**.

La aplicación permite llevar un control sencillo de los movimientos financieros, consultar la información registrada y visualizar el comportamiento de ingresos y gastos.

## Características

* Registro de ingresos.
* Registro de gastos.
* Consulta de movimientos.
* Organización de la información financiera.
* Visualización de ingresos y gastos.
* Interfaz web sencilla mediante Streamlit.
* Ejecución local desde el navegador.

## Requisitos

* Windows, Linux o macOS.
* Python 3.10 o superior.
* Git.
* Streamlit.

Se recomienda utilizar un entorno virtual (`venv`) para instalar las dependencias del proyecto.

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/asoto59g/Gastos_Ingresos.git
cd Gastos_Ingresos
```

### 2. Crear un entorno virtual

En Windows:

```powershell
python -m venv .venv
```

### 3. Activar el entorno virtual

En Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

En Windows CMD:

```cmd
.venv\Scripts\activate
```

En Linux/macOS:

```bash
source .venv/bin/activate
```

### 4. Instalar las dependencias

Si el proyecto incluye `requirements.txt`:

```bash
pip install -r requirements.txt
```

Si todavía no existe el archivo `requirements.txt`, puede instalarse Streamlit directamente:

```bash
pip install streamlit
```

## Ejecución

Con el entorno virtual activado, ejecutar:

```bash
streamlit run app.py
```

Streamlit iniciará un servidor local y mostrará una dirección similar a:

```text
http://localhost:8501
```

Abrir esa dirección en el navegador para utilizar la aplicación.

## Estructura del proyecto

Una estructura típica del proyecto es:

```text
Gastos_Ingresos/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── .streamlit/
    └── secrets.toml
```

> El archivo `secrets.toml` debe mantenerse fuera de GitHub si contiene contraseñas, claves API u otra información privada.

## Actualizar el proyecto

Después de realizar cambios en la aplicación:

```bash
git add .
git commit -m "Actualización de la aplicación"
git push
```

## Tecnologías

* **Python**
* **Streamlit**
* **Git**
* **GitHub**

## Autor

**Alejandro Soto**

GitHub: [@asoto59g](https://github.com/asoto59g)

---

## Licencia

Este proyecto se publica en GitHub para fines personales y de desarrollo.
