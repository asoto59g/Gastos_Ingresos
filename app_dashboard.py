import io
import unicodedata
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from classifier import (
    CAT_EFECTIVO,
    CAT_OTROS,
    SUB_ALIMENTACION_CARNICERIAS,
    SUB_ALIMENTACION_PANADERIAS,
    SUB_ALIMENTACION_RESTAURANTES,
    SUB_ALIMENTACION_SUPERMERCADOS,
    classify_transaction,
)

ROOT = Path(__file__).resolve().parent
DEFAULT_EXCEL = ROOT / "Transacciones_Sinteticas_1000_6Meses.xlsx"

st.set_page_config(
    page_title="Gastos e ingresos",
    page_icon=":material/account_balance:",
    layout="wide",
    initial_sidebar_state="expanded",
)

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, Segoe UI, sans-serif", color="#111827", size=13),
    margin=dict(l=8, r=8, t=48, b=8),
    legend=dict(orientation="h", yanchor="bottom", y=-0.22, x=0),
    hoverlabel=dict(bgcolor="#111827", font_color="#F9FAFB"),
    xaxis=dict(gridcolor="#E5E7EB", zerolinecolor="#D1D5DB"),
    yaxis=dict(gridcolor="#E5E7EB", zerolinecolor="#D1D5DB"),
)

COLOR_GASTO = "#DC2626"
COLOR_INGRESO = "#059669"
COLOR_NETO = "#2563EB"
DONUT_COLORS = ["#2563EB", "#059669", "#7C3AED", "#DC2626", "#D97706", "#0891B2", "#6B7280", "#EA580C"]


def _norm_col(name: object) -> str:
    """Normaliza cadenas eliminando acentos, espacios extra y caracteres especiales."""
    text = unicodedata.normalize("NFKD", str(name))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.lower().replace("*", "").strip()


def _colones(value: float) -> str:
    return f"₡{value:,.0f}"


def _clean_numeric_val(v) -> float:
    """
    Limpia y convierte un valor numérico soportando formato latino (750.000,00)
    e internacional (750,000.00).
    """
    if pd.isna(v):
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).replace("₡", "").replace("$", "").strip()
    if not s or s.lower() in ["nan", "none", "null", "-"]:
        return 0.0
    
    if "," in s and "." in s:
        if s.find(".") < s.find(","):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s and "." not in s:
        parts = s.split(",")
        if len(parts[-1]) == 2:
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "." in s and "," not in s:
        parts = s.split(".")
        if len(parts) > 1 and all(len(p) == 3 for p in parts[1:]):
            s = s.replace(".", "")

    try:
        return float(s)
    except ValueError:
        return 0.0


def _clean_numeric_series(series: pd.Series) -> pd.Series:
    return series.apply(_clean_numeric_val)


def _normalize_category_for_display(category: str) -> str:
    """Normaliza las subcategorías de alimentación para mostrarlas como 'Alimentación' en gráficos."""
    if isinstance(category, str) and category.startswith("Alimentación:"):
        return "Alimentación"
    return str(category)


@st.cache_data(show_spinner="Leyendo movimientos…", max_entries=4)
def load_transactions(file_bytes: bytes, filename: str) -> pd.DataFrame:
    buffer = io.BytesIO(file_bytes)
    if filename.lower().endswith(".csv"):
        df = pd.read_csv(buffer)
    else:
        df = pd.read_excel(buffer)
    df = df.dropna(axis=1, how="all")

    cols_norm = {col: _norm_col(col) for col in df.columns}
    rename = {}
    
    # 1. Identificar Fecha
    for col, key in cols_norm.items():
        if any(t in key for t in ["fecha", "date"]):
            rename[col] = "Fecha"
            break
            
    # 2. Identificar Descripción
    for col, key in cols_norm.items():
        if any(t in key for t in ["descripcion", "detalle", "concepto", "leyenda", "movimiento"]):
            rename[col] = "Descripcion"
            break

    # 3. Identificar Referencia y Balance
    for col, key in cols_norm.items():
        if any(t in key for t in ["referencia", "ref", "comprobante", "voucher"]):
            rename[col] = "Referencia"
        elif any(t in key for t in ["balance", "saldo"]):
            rename[col] = "Balance"

    # 4. Identificar Débitos, Créditos o Columna Única de Monto
    deb_col = None
    cred_col = None
    monto_col = None

    for col, key in cols_norm.items():
        if any(t in key for t in ["debito", "egreso", "gasto", "debit", "salida", "cargo"]):
            deb_col = col
        elif any(t in key for t in ["credito", "ingres", "credit", "abono", "deposito", "entrada"]):
            cred_col = col
        elif any(t in key for t in ["monto", "importe", "valor", "amount"]) and not deb_col and not cred_col:
            monto_col = col

    if deb_col:
        rename[deb_col] = "Debitos"
    if cred_col:
        rename[cred_col] = "Creditos"

    df = df.rename(columns=rename)

    # Si hay una sola columna "Monto" o similar y no venían "Debitos"/"Creditos" separados
    if "Debitos" not in df.columns and "Creditos" not in df.columns and monto_col:
        monto_vals = _clean_numeric_series(df[monto_col])
        df["Debitos"] = monto_vals.apply(lambda x: abs(x) if x < 0 else 0.0)
        df["Creditos"] = monto_vals.apply(lambda x: abs(x) if x > 0 else 0.0)

    if "Debitos" not in df.columns:
        df["Debitos"] = 0.0
    if "Creditos" not in df.columns:
        df["Creditos"] = 0.0

    required = ["Fecha", "Descripcion"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"Columnas faltantes en {filename}: {', '.join(missing)}. "
            "Se esperan al menos Fecha y Descripción."
        )

    df = df.dropna(subset=["Fecha"])
    df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Fecha"])
    df["Descripcion"] = df["Descripcion"].fillna("").astype(str).str.strip()

    # Limpieza numérica de Débitos y Créditos
    df["Debitos"] = _clean_numeric_series(df["Debitos"]).abs()
    df["Creditos"] = _clean_numeric_series(df["Creditos"]).abs()

    if "Referencia" not in df.columns:
        df["Referencia"] = ""
    if "Balance" not in df.columns:
        df["Balance"] = pd.NA

    df["Referencia"] = df["Referencia"].fillna("").astype(str).str.strip()
    df["Balance"] = pd.to_numeric(df["Balance"], errors="coerce")

    # Clasificación por reglas
    df["Categoria"] = [
        classify_transaction(desc, debit, credit)
        for desc, debit, credit in zip(df["Descripcion"], df["Debitos"], df["Creditos"])
    ]
    
    # Asignación de Tipo garantizada: Ingreso si Créditos > 0 y Créditos > Débitos
    df["Tipo"] = [
        "Ingreso" if c > 0 and c > d else ("Gasto" if d > 0 else ("Ingreso" if c > 0 else "Gasto"))
        for d, c in zip(df["Debitos"], df["Creditos"])
    ]
    
    df["Monto"] = df[["Debitos", "Creditos"]].max(axis=1)
    df["Mes"] = df["Fecha"].dt.to_period("M").astype(str)
    return df.sort_values("Fecha").reset_index(drop=True)


def _file_bytes() -> tuple[bytes, str]:
    uploaded = st.session_state.get("uploaded_excel")
    if uploaded is not None:
        return uploaded.getvalue(), uploaded.name
    if DEFAULT_EXCEL.exists():
        return DEFAULT_EXCEL.read_bytes(), DEFAULT_EXCEL.name
    raise FileNotFoundError(
        "No hay archivo. Coloca Gastos_Ingresos.xlsx en esta carpeta o cárgalo en la barra lateral."
    )


def _chart_points(event) -> list[dict]:
    if event is None:
        return []
    selection = getattr(event, "selection", None)
    if selection is None and isinstance(event, dict):
        selection = event.get("selection")
    if selection is None:
        return []
    points = getattr(selection, "points", None)
    if points is None and isinstance(selection, dict):
        points = selection.get("points")
    return list(points or [])


def _apply_chart_filters(df: pd.DataFrame, cats: set[str], months: set[str], types: set[str]) -> pd.DataFrame:
    out = df
    if cats:
        # Si se selecciona "Alimentación", incluir todas sus subcategorías
        if "Alimentación" in cats:
            alimentacion_subs = [
                SUB_ALIMENTACION_RESTAURANTES,
                SUB_ALIMENTACION_SUPERMERCADOS,
                SUB_ALIMENTACION_CARNICERIAS,
                SUB_ALIMENTACION_PANADERIAS,
            ]
            cats_with_subs = cats.union(set(alimentacion_subs))
            out = out[out["Categoria"].isin(cats_with_subs)]
        else:
            out = out[out["Categoria"].isin(cats)]
    if months:
        out = out[out["Mes"].isin(months)]
    if types == {"Gasto"}:
        out = out[out["Tipo"] == "Gasto"]
    elif types == {"Ingreso"}:
        out = out[out["Tipo"] == "Ingreso"]
    return out


def donut(labels, values, title: str) -> go.Figure:
    layout = PLOTLY_LAYOUT | {
        "height": 500,
        "margin": dict(l=8, r=8, t=48, b=150),
        "legend": dict(
            orientation="h",
            yanchor="top",
            y=-0.34,
            xanchor="center",
            x=0.5,
        ),
    }
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.55,
            marker=dict(colors=DONUT_COLORS, line=dict(color="white", width=2)),
            textinfo="percent",
            hovertemplate="%{label}<br>₡%{value:,.0f}<br>%{percent}<extra></extra>",
        )
    )
    fig.update_layout(title=title, **layout)
    return fig


def main() -> None:
    st.sidebar.header(":material/folder_open: Datos")
    st.sidebar.caption("Se usa el Excel de la carpeta. Puedes sustituirlo cargando otro extracto.")
    st.sidebar.file_uploader(
        "Cargar Excel / CSV",
        type=["xlsx", "xls", "csv"],
        key="uploaded_excel",
    )
    if st.sidebar.button("Vaciar caché de datos", icon=":material/refresh:"):
        st.cache_data.clear()
        st.rerun()

    try:
        raw_bytes, filename = _file_bytes()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()

    try:
        df = load_transactions(raw_bytes, filename)
    except Exception as exc:
        st.error(f"No se pudo leer el archivo: {exc}")
        st.stop()

    st.title(":material/analytics: Gastos e ingresos")
    st.caption(f"Fuente: **{filename}** · {len(df):,} movimientos · {df['Fecha'].min():%d/%m/%Y} – {df['Fecha'].max():%d/%m/%Y}")

    min_date = df["Fecha"].min().date()
    max_date = df["Fecha"].max().date()

    with st.sidebar:
        st.header(":material/filter_list: Filtros")
        rango = st.date_input(
            "Rango de fechas",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="date_range",
        )
        tipo = st.segmented_control(
            "Tipo",
            ["Todos", "Gastos", "Ingresos"],
            default="Todos",
            key="transaction_type",
        )
        buscar = st.text_input(
            "Buscar en descripción",
            placeholder="Ej. Uber, JPS, SINPE…",
            key="description_search",
        )
        categorias = sorted(df["Categoria"].unique())
        selected_cat = st.multiselect("Categoría (vacío = todas)", categorias, key="category_filter")
        excluir_cajero = st.toggle("Excluir retiros de cajero del gasto", value=True, key="exclude_cash")
        st.caption("Los retiros de efectivo no son un gasto: el dinero sigue en tu bolsillo.")

    if isinstance(rango, (list, tuple)):
        if len(rango) == 2:
            date_from, date_to = rango
        elif len(rango) == 1:
            date_from = date_to = rango[0]
        else:
            date_from, date_to = min_date, max_date
    else:
        date_from = date_to = rango

    if tipo is None:
        tipo = "Todos"

    mask = (df["Fecha"].dt.date >= date_from) & (df["Fecha"].dt.date <= date_to)
    filtered = df.loc[mask].copy()
    if tipo == "Gastos":
        filtered = filtered[filtered["Tipo"] == "Gasto"]
    elif tipo == "Ingresos":
        filtered = filtered[filtered["Tipo"] == "Ingreso"]
    if selected_cat:
        filtered = filtered[filtered["Categoria"].isin(selected_cat)]
    if buscar.strip():
        q = buscar.strip().lower()
        filtered = filtered[filtered["Descripcion"].str.lower().str.contains(q, na=False, regex=False)]
    if excluir_cajero:
        filtered = filtered[filtered["Categoria"] != CAT_EFECTIVO]

    if filtered.empty:
        st.warning("No hay movimientos con esos filtros.")
        st.stop()

    gastos = filtered.loc[filtered["Tipo"] == "Gasto", "Debitos"].sum()
    ingresos = filtered.loc[filtered["Tipo"] == "Ingreso", "Creditos"].sum()
    neto = ingresos - gastos
    meses = max(filtered["Mes"].nunique(), 1)
    ahorro_pct = (neto / ingresos * 100) if ingresos else 0.0
    saldo = None
    if "Balance" in filtered.columns and filtered["Balance"].notna().any():
        saldo = filtered["Balance"].dropna().iloc[-1]

    flujo = filtered.groupby("Mes", as_index=False)[["Debitos", "Creditos"]].sum()
    flujo["Neto"] = flujo["Creditos"] - flujo["Debitos"]

    with st.container(horizontal=True):
        st.metric(
            "Ingresos",
            _colones(ingresos),
            f"{_colones(ingresos / meses)} / mes",
            border=True,
            chart_data=flujo["Creditos"].tolist(),
            chart_type="area",
        )
        st.metric(
            "Gastos",
            _colones(gastos),
            f"{_colones(gastos / meses)} / mes",
            border=True,
            chart_data=flujo["Debitos"].tolist(),
            chart_type="area",
        )
        st.metric(
            "Balance neto",
            _colones(neto),
            f"{ahorro_pct:.0f}% de los ingresos",
            border=True,
            chart_data=flujo["Neto"].tolist(),
            chart_type="line",
        )
        st.metric("Movimientos", f"{len(filtered):,}", f"{meses} mes(es)", border=True)
        st.metric("Saldo al corte", _colones(saldo) if saldo is not None else "—", border=True)

    gastos_df = filtered[filtered["Tipo"] == "Gasto"]
    ingresos_df = filtered[filtered["Tipo"] == "Ingreso"]
    
    # Normalizar categorías para gráficos (subcategorías de alimentación se agrupan)
    gastos_df_copy = gastos_df.copy()
    gastos_df_copy["Categoria_Display"] = gastos_df_copy["Categoria"].apply(_normalize_category_for_display)
    gastos_cat = (
        gastos_df_copy.groupby("Categoria_Display", as_index=False)["Debitos"].sum().sort_values("Debitos", ascending=False)
    )
    
    ingresos_df_copy = ingresos_df.copy()
    ingresos_df_copy["Categoria_Display"] = ingresos_df_copy["Categoria"].apply(_normalize_category_for_display)
    ingresos_cat = (
        ingresos_df_copy.groupby("Categoria_Display", as_index=False)["Creditos"].sum().sort_values("Creditos", ascending=False)
    )

    left, right = st.columns(2)
    clicked_cats: set[str] = set()
    with left:
        with st.container(border=True):
            if not gastos_cat.empty:
                fig_g = donut(gastos_cat["Categoria_Display"], gastos_cat["Debitos"], "Gastos por categoría")
                ev_g = st.plotly_chart(fig_g, width="stretch", on_select="rerun", key="pie_gastos", selection_mode="points")
                for point in _chart_points(ev_g):
                    if point.get("label"):
                        clicked_cats.add(point["label"])
            else:
                st.info("Sin gastos en el periodo.")
    with right:
        with st.container(border=True):
            if not ingresos_cat.empty:
                fig_i = donut(ingresos_cat["Categoria_Display"], ingresos_cat["Creditos"], "Ingresos por categoría")
                ev_i = st.plotly_chart(fig_i, width="stretch", on_select="rerun", key="pie_ingresos", selection_mode="points")
                for point in _chart_points(ev_i):
                    if point.get("label"):
                        clicked_cats.add(point["label"])
            else:
                st.info("Sin ingresos en el periodo.")

    fig_bar = go.Figure()
    fig_bar.add_trace(
        go.Bar(x=flujo["Mes"], y=flujo["Debitos"], name="Gastos", marker_color=COLOR_GASTO, hovertemplate="₡%{y:,.0f}<extra>Gastos</extra>")
    )
    fig_bar.add_trace(
        go.Bar(x=flujo["Mes"], y=flujo["Creditos"], name="Ingresos", marker_color=COLOR_INGRESO, hovertemplate="₡%{y:,.0f}<extra>Ingresos</extra>")
    )
    fig_bar.add_trace(
        go.Scatter(
            x=flujo["Mes"],
            y=flujo["Neto"],
            name="Neto",
            mode="lines+markers",
            line=dict(color=COLOR_NETO, width=2),
            hovertemplate="₡%{y:,.0f}<extra>Neto</extra>",
        )
    )
    fig_bar.update_layout(title="Flujo mensual", barmode="group", yaxis_title="Colones", **PLOTLY_LAYOUT)
    with st.container(border=True):
        ev_bar = st.plotly_chart(fig_bar, width="stretch", on_select="rerun", key="flujo_mes", selection_mode="points")

    clicked_months: set[str] = set()
    clicked_types: set[str] = set()
    for point in _chart_points(ev_bar):
        if point.get("x") is not None:
            clicked_months.add(str(point["x"]))
        curve = point.get("curve_number", point.get("curveNumber"))
        if curve == 0:
            clicked_types.add("Gasto")
        elif curve == 1:
            clicked_types.add("Ingreso")

    st.subheader("Promedio mensual por categoría")
    tab_g, tab_i, tab_top = st.tabs(["Gastos", "Ingresos", "Comercios más frecuentes"], on_change="rerun", key="monthly_tabs")
    if tab_g.open:
        with tab_g:
            if not gastos_df.empty:
                avg_g = (gastos_df_copy.groupby("Categoria_Display")["Debitos"].sum() / meses).reset_index(name="Promedio")
                avg_g = avg_g.sort_values("Promedio")
                fig = go.Figure(
                    go.Bar(
                        y=avg_g["Categoria_Display"],
                        x=avg_g["Promedio"],
                        orientation="h",
                        marker_color=COLOR_GASTO,
                        text=avg_g["Promedio"].map(_colones),
                        textposition="outside",
                        cliponaxis=False,
                        hovertemplate="%{y}: ₡%{x:,.0f}<extra></extra>",
                    )
                )
                fig.update_layout(title=f"Promedio de gasto · {meses} mes(es)", height=max(360, 28 * len(avg_g) + 80), **PLOTLY_LAYOUT)
                st.plotly_chart(fig, width="stretch")
    if tab_i.open:
        with tab_i:
            if not ingresos_df.empty:
                avg_i = (ingresos_df_copy.groupby("Categoria_Display")["Creditos"].sum() / meses).reset_index(name="Promedio")
                avg_i = avg_i.sort_values("Promedio")
                fig = go.Figure(
                    go.Bar(
                        y=avg_i["Categoria_Display"],
                        x=avg_i["Promedio"],
                        orientation="h",
                        marker_color=COLOR_INGRESO,
                        text=avg_i["Promedio"].map(_colones),
                        textposition="outside",
                        cliponaxis=False,
                        hovertemplate="%{y}: ₡%{x:,.0f}<extra></extra>",
                    )
                )
                fig.update_layout(title=f"Promedio de ingreso · {meses} mes(es)", height=max(320, 28 * len(avg_i) + 80), **PLOTLY_LAYOUT)
                st.plotly_chart(fig, width="stretch")
    if tab_top.open:
        with tab_top:
            top = (
                gastos_df.groupby("Descripcion", as_index=False)
                .agg(Veces=("Debitos", "size"), Total=("Debitos", "sum"))
                .sort_values("Total", ascending=False)
                .head(15)
            )
            if top.empty:
                st.info("Sin gastos para ranking de comercios.")
            else:
                fig = go.Figure(
                    go.Bar(
                        y=top["Descripcion"][::-1],
                        x=top["Total"][::-1],
                        orientation="h",
                        marker_color="#6B7280",
                        customdata=top["Veces"][::-1],
                        hovertemplate="%{y}<br>₡%{x:,.0f} · %{customdata} veces<extra></extra>",
                    )
                )
                fig.update_layout(title="Top 15 comercios / descripciones", height=520, **PLOTLY_LAYOUT)
                st.plotly_chart(fig, width="stretch")

    # Desglose de subcategorías de Alimentación
    alimentacion_subs = [
        SUB_ALIMENTACION_RESTAURANTES,
        SUB_ALIMENTACION_SUPERMERCADOS,
        SUB_ALIMENTACION_CARNICERIAS,
        SUB_ALIMENTACION_PANADERIAS,
    ]
    gastos_alimentacion = gastos_df[gastos_df["Categoria"].isin(alimentacion_subs)]
    if not gastos_alimentacion.empty:
        st.subheader("Desglose de Alimentación")
        subcat_avg = (gastos_alimentacion.groupby("Categoria")["Debitos"].sum() / meses).reset_index(name="Promedio")
        subcat_avg = subcat_avg.sort_values("Promedio")
        if not subcat_avg.empty:
            # Asegurar que la columna existe
            if "Categoria" in subcat_avg.columns:
                fig = go.Figure(
                    go.Bar(
                        y=subcat_avg["Categoria"],
                        x=subcat_avg["Promedio"],
                        orientation="h",
                        marker_color="#DC2626",
                        text=subcat_avg["Promedio"].map(_colones),
                        textposition="outside",
                        cliponaxis=False,
                        hovertemplate="%{y}: ₡%{x:,.0f}<extra></extra>",
                    )
                )
                fig.update_layout(
                    title=f"Promedio mensual de Alimentación por subcategoría · {meses} mes(es)",
                    height=max(280, 28 * len(subcat_avg) + 80),
                    **PLOTLY_LAYOUT,
                )
                st.plotly_chart(fig, width="stretch")

    sheet = _apply_chart_filters(filtered, clicked_cats, clicked_months, clicked_types)
    hints = []
    if clicked_cats:
        hints.append("categorías " + ", ".join(sorted(clicked_cats)))
    if clicked_months:
        hints.append("meses " + ", ".join(sorted(clicked_months)))
    if len(clicked_types) == 1:
        hints.append("tipo " + next(iter(clicked_types)).lower())
    if hints:
        st.info("Filtro del gráfico: " + " · ".join(hints) + ". Clic de nuevo en el gráfico o recarga para limpiar.")

    otros = filtered[filtered["Categoria"] == CAT_OTROS]
    if not otros.empty:
        review_expander = st.expander(
            f"Revisar sin clasificar ({len(otros)} movimientos · {_colones(otros['Debitos'].sum())})",
            icon=":material/rule:",
            key="review_uncategorized",
            on_change="rerun",
        )
        if review_expander.open:
            with review_expander:
                review = (
                    otros.groupby("Descripcion", as_index=False)
                    .agg(Veces=("Descripcion", "size"), Debitos=("Debitos", "sum"), Creditos=("Creditos", "sum"))
                    .sort_values("Veces", ascending=False)
                )
                st.dataframe(review, width="stretch", hide_index=True)
                st.caption("Estas descripciones caen en «Otros». Se pueden agregar reglas en classifier.py.")

    st.subheader("Detalle de movimientos")
    display_columns = ["Fecha", "Referencia", "Descripcion", "Categoria", "Tipo", "Debitos", "Creditos", "Balance"]
    show = sheet.reindex(columns=display_columns).copy()
    show["Fecha"] = show["Fecha"].dt.strftime("%d/%m/%Y")
    st.dataframe(
        show,
        width="stretch",
        height=440,
        hide_index=True,
        column_config={
            "Fecha": st.column_config.TextColumn("Fecha"),
            "Referencia": st.column_config.TextColumn("Referencia"),
            "Descripcion": st.column_config.TextColumn("Descripción", width="large", pinned=True),
            "Categoria": st.column_config.TextColumn("Categoría"),
            "Debitos": st.column_config.NumberColumn("Débitos", format="₡%d"),
            "Creditos": st.column_config.NumberColumn("Créditos", format="₡%d"),
            "Balance": st.column_config.NumberColumn("Saldo", format="₡%d"),
        },
    )

    csv = show.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Descargar detalle (CSV)",
        csv,
        file_name="movimientos_filtrados.csv",
        mime="text/csv",
        icon=":material/download:",
    )


if __name__ == "__main__":
    main()
