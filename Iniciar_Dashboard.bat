@echo off
cd /d "%~dp0"
echo Iniciando el dashboard de gastos e ingresos...
echo No cierres esta ventana.
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m streamlit run app_dashboard.py
) else (
  python -m streamlit run app_dashboard.py
)
pause
