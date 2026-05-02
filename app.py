import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime, date, time

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Mis Finanzas",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# ESTILOS GLOBALES
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
}

/* Fondo general */
.stApp {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    min-height: 100vh;
}

/* Crédito superior derecho */
.credito-header {
    position: fixed;
    top: 14px;
    right: 20px;
    z-index: 9999;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 11px;
    color: rgba(255,255,255,0.65);
    font-family: 'Sora', sans-serif;
    line-height: 1.4;
    text-align: right;
    backdrop-filter: blur(8px);
    max-width: 340px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d1a 0%, #141428 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}

[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
}

/* Título principal */
.titulo-principal {
    font-family: 'Sora', sans-serif;
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(90deg, #4fffb0, #00c6ff, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.2rem;
}

.subtitulo {
    color: rgba(255,255,255,0.5);
    font-size: 0.95rem;
    margin-bottom: 2rem;
}

/* Cards de métricas */
.metric-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px;
    padding: 20px 24px;
    text-align: center;
    backdrop-filter: blur(10px);
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.metric-card:hover {
    transform: translateY(-3px);
    border-color: rgba(79,255,176,0.3);
}

.metric-valor {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.8rem;
    font-weight: 600;
    margin: 4px 0;
}

.metric-label {
    font-size: 0.8rem;
    color: rgba(255,255,255,0.5);
    text-transform: uppercase;
    letter-spacing: 1px;
}

.verde  { color: #4fffb0; }
.rojo   { color: #ff6b6b; }
.azul   { color: #60a5fa; }
.blanco { color: #ffffff; }

/* Tabla de historial */
.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
}

/* Formulario */
.stForm {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.5rem;
}

/* Botones */
.stButton > button {
    background: linear-gradient(135deg, #4fffb0, #00c6ff);
    color: #0a0a15;
    border: none;
    border-radius: 10px;
    font-family: 'Sora', sans-serif;
    font-weight: 600;
    font-size: 0.95rem;
    padding: 0.6rem 1.4rem;
    transition: opacity 0.2s ease, transform 0.1s ease;
}

.stButton > button:hover {
    opacity: 0.88;
    transform: scale(1.02);
}

/* Inputs */
.stTextInput input, .stNumberInput input, .stSelectbox select {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 8px !important;
    color: #fff !important;
}

/* Radio de navegación */
.stRadio > div {
    gap: 6px;
}

/* Separador */
hr {
    border-color: rgba(255,255,255,0.08);
    margin: 1rem 0;
}

/* Alertas */
.stSuccess, .stInfo, .stWarning, .stError {
    border-radius: 10px;
}

/* Sección de gráfico */
.grafico-titulo {
    font-size: 1.1rem;
    font-weight: 600;
    color: rgba(255,255,255,0.85);
    margin-bottom: 0.5rem;
}

/* Botón de eliminar pequeño */
.stButton.eliminar > button {
    background: rgba(255,107,107,0.15);
    color: #ff6b6b;
    border: 1px solid rgba(255,107,107,0.3);
    font-size: 0.75rem;
    padding: 0.3rem 0.7rem;
}
</style>

<div class="credito-header">
    📘 Proyecto de <strong>Fermín Guzmán</strong> y <strong>Esteban Pedraza</strong><br>
    Materia: Diseño de productos
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ARCHIVO DE DATOS
# ─────────────────────────────────────────────
ARCHIVO_CSV = "transacciones.csv"
COLUMNAS = ["ID", "Fecha", "Hora", "Concepto", "Categoría", "Tipo", "Monto"]

CATEGORIAS_GASTO   = ["Alimentación", "Transporte", "Entretenimiento", "Salud",
                      "Educación", "Ropa", "Hogar", "Servicios", "Otros"]
CATEGORIAS_INGRESO = ["Salario", "Freelance", "Inversiones", "Regalo",
                      "Venta", "Bono", "Otros"]


def cargar_datos() -> pd.DataFrame:
    """Carga el CSV de transacciones o devuelve un DataFrame vacío."""
    if os.path.exists(ARCHIVO_CSV):
        df = pd.read_csv(ARCHIVO_CSV)
        for col in COLUMNAS:
            if col not in df.columns:
                df[col] = ""
        return df[COLUMNAS]
    return pd.DataFrame(columns=COLUMNAS)


def guardar_datos(df: pd.DataFrame):
    """Persiste el DataFrame en CSV."""
    df.to_csv(ARCHIVO_CSV, index=False)


def siguiente_id(df: pd.DataFrame) -> int:
    if df.empty:
        return 1
    return int(df["ID"].max()) + 1


def balance_color(val: float) -> str:
    return "verde" if val >= 0 else "rojo"


# ─────────────────────────────────────────────
# ESTADO DE SESIÓN
# ─────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = cargar_datos()

df = st.session_state.df

# ─────────────────────────────────────────────
# SIDEBAR – MENÚ DE NAVEGACIÓN
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💸 Mis Finanzas")
    st.markdown("---")
    pagina = st.radio(
        "Navegación",
        ["📝 Registrar Transacción", "📋 Historial", "📊 Gráficos"],
        label_visibility="collapsed",
    )
    st.markdown("---")

    # Resumen rápido en el sidebar
    if not df.empty:
        ingresos_total = df[df["Tipo"] == "Ingreso"]["Monto"].sum()
        gastos_total   = df[df["Tipo"] == "Gasto"]["Monto"].sum()
        balance        = ingresos_total - gastos_total
        col_color      = balance_color(balance)

        st.markdown("**Resumen rápido**")
        st.markdown(f"🟢 Ingresos: `${ingresos_total:,.2f}`")
        st.markdown(f"🔴 Gastos: `${gastos_total:,.2f}`")
        st.markdown(f"⚖️ Balance: **`${balance:,.2f}`**")
        st.markdown("---")

    st.caption("v2.0 — Gestor de Finanzas")

# ─────────────────────────────────────────────
# ENCABEZADO PRINCIPAL
# ─────────────────────────────────────────────
st.markdown('<p class="titulo-principal">💸 Gestor de Finanzas Personales</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitulo">Registra, analiza y visualiza tus movimientos financieros, desarrollado por Fermín Guzmán y Esteban Pedraza.</p>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MÉTRICAS GLOBALES (siempre visibles)
# ─────────────────────────────────────────────
if not df.empty:
    ingresos_total = df[df["Tipo"] == "Ingreso"]["Monto"].sum()
    gastos_total   = df[df["Tipo"] == "Gasto"]["Monto"].sum()
    balance        = ingresos_total - gastos_total
    n_transacciones = len(df)
else:
    ingresos_total = gastos_total = balance = 0.0
    n_transacciones = 0

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">💰 Total Ingresos</div>
        <div class="metric-valor verde">${ingresos_total:,.2f}</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">💸 Total Gastos</div>
        <div class="metric-valor rojo">${gastos_total:,.2f}</div>
    </div>""", unsafe_allow_html=True)
with c3:
    bcolor = "verde" if balance >= 0 else "rojo"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">⚖️ Balance</div>
        <div class="metric-valor {bcolor}">${balance:,.2f}</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🗒️ Transacciones</div>
        <div class="metric-valor azul">{n_transacciones}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# PÁGINA 1 – REGISTRAR TRANSACCIÓN
# ═══════════════════════════════════════════════════════════════════
if pagina == "📝 Registrar Transacción":
    st.subheader("📝 Registrar nueva transacción")

    with st.form("registro_form", clear_on_submit=True):
        col_izq, col_der = st.columns(2)

        with col_izq:
            concepto = st.text_input("Concepto", placeholder="Ej. Café, Nómina, Netflix…")
            tipo     = st.selectbox("Tipo de movimiento", ["Gasto", "Ingreso"])
            monto    = st.number_input("Monto ($)", min_value=0.01, step=0.01, format="%.2f")

        with col_der:
            # Tipo determina las categorías disponibles
            cats = CATEGORIAS_GASTO if tipo == "Gasto" else CATEGORIAS_INGRESO
            categoria = st.selectbox("Categoría", cats)

            st.markdown("**📅 Fecha y hora de la transacción**")
            fecha_sel = st.date_input("Fecha", value=date.today())
            hora_sel  = st.time_input("Hora", value=datetime.now().time(), step=60)

        nota = st.text_area("Notas adicionales (opcional)", height=80,
                            placeholder="Agrega cualquier detalle extra…")

        guardar = st.form_submit_button("💾 Guardar Transacción", use_container_width=True)

    if guardar:
        if not concepto.strip():
            st.error("⚠️ El concepto no puede estar vacío.")
        elif monto <= 0:
            st.error("⚠️ El monto debe ser mayor a cero.")
        else:
            nueva = {
                "ID":        siguiente_id(df),
                "Fecha":     str(fecha_sel),
                "Hora":      hora_sel.strftime("%H:%M"),
                "Concepto":  concepto.strip(),
                "Categoría": categoria,
                "Tipo":      tipo,
                "Monto":     round(monto, 2),
            }
            st.session_state.df = pd.concat(
                [df, pd.DataFrame([nueva])], ignore_index=True
            )
            guardar_datos(st.session_state.df)
            emoji = "🟢" if tipo == "Ingreso" else "🔴"
            st.success(
                f"{emoji} ¡Registrado! **{tipo}** de **${monto:,.2f}** "
                f"en **{categoria}** — *{concepto}* "
                f"({str(fecha_sel)} {hora_sel.strftime('%H:%M')})"
            )
            st.rerun()

# ═══════════════════════════════════════════════════════════════════
# PÁGINA 2 – HISTORIAL
# ═══════════════════════════════════════════════════════════════════
elif pagina == "📋 Historial":
    st.subheader("📋 Historial de transacciones")

    if df.empty:
        st.info("📭 Aún no hay transacciones registradas. ¡Empieza en la sección de Registro!")
    else:
        # Filtros
        with st.expander("🔍 Filtros", expanded=True):
            f1, f2, f3 = st.columns(3)
            with f1:
                filtro_tipo = st.multiselect("Tipo", ["Gasto", "Ingreso"],
                                             default=["Gasto", "Ingreso"])
            with f2:
                todas_cats = sorted(df["Categoría"].unique().tolist())
                filtro_cat = st.multiselect("Categoría", todas_cats, default=todas_cats)
            with f3:
                filtro_buscar = st.text_input("Buscar concepto", placeholder="Escribe algo…")

        df_filtrado = df[
            df["Tipo"].isin(filtro_tipo) &
            df["Categoría"].isin(filtro_cat)
        ]
        if filtro_buscar:
            df_filtrado = df_filtrado[
                df_filtrado["Concepto"].str.contains(filtro_buscar, case=False, na=False)
            ]

        # Ordenar por fecha y hora descendente
        df_mostrar = df_filtrado.sort_values(
            ["Fecha", "Hora"], ascending=[False, False]
        ).reset_index(drop=True)

        st.markdown(f"**{len(df_mostrar)}** transacciones encontradas")

        # Colorear la columna Tipo
        def color_tipo(val):
            if val == "Ingreso":
                return "background-color: rgba(79,255,176,0.15); color: #4fffb0;"
            return "background-color: rgba(255,107,107,0.15); color: #ff6b6b;"

        styled = (
            df_mostrar
            .style
            .map(color_tipo, subset=["Tipo"])
            .format({"Monto": "${:,.2f}"})
        )
        st.dataframe(styled, use_container_width=True, height=420)

        # Exportar CSV
        csv_export = df_mostrar.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Exportar historial filtrado (.csv)",
            data=csv_export,
            file_name="historial_finanzas.csv",
            mime="text/csv",
        )

        st.markdown("---")
        st.markdown("**⚠️ Eliminar transacción por ID**")
        col_del1, col_del2 = st.columns([1, 3])
        with col_del1:
            id_eliminar = st.number_input("ID a eliminar", min_value=1, step=1,
                                          label_visibility="collapsed")
        with col_del2:
            if st.button("🗑️ Eliminar"):
                if id_eliminar in st.session_state.df["ID"].values:
                    st.session_state.df = st.session_state.df[
                        st.session_state.df["ID"] != id_eliminar
                    ].reset_index(drop=True)
                    guardar_datos(st.session_state.df)
                    st.success(f"Transacción #{int(id_eliminar)} eliminada.")
                    st.rerun()
                else:
                    st.error(f"No existe la transacción con ID {int(id_eliminar)}.")

# ═══════════════════════════════════════════════════════════════════
# PÁGINA 3 – GRÁFICOS
# ═══════════════════════════════════════════════════════════════════
elif pagina == "📊 Gráficos":
    st.subheader("📊 Análisis visual de tus finanzas")

    if df.empty:
        st.info("📭 Registra algunas transacciones para ver los gráficos.")
    else:
        df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce")
        df_gastos   = df[df["Tipo"] == "Gasto"]
        df_ingresos = df[df["Tipo"] == "Ingreso"]

        PALETA_GASTOS   = px.colors.sequential.Reds_r
        PALETA_INGRESOS = px.colors.sequential.Greens_r
        BG_CHART        = "rgba(0,0,0,0)"
        FONT_COLOR      = "rgba(255,255,255,0.80)"
        PAPER_BG        = "rgba(255,255,255,0.04)"

        def estilo_fig(fig):
            fig.update_layout(
                paper_bgcolor=PAPER_BG,
                plot_bgcolor=BG_CHART,
                font=dict(color=FONT_COLOR, family="Sora, sans-serif"),
                margin=dict(t=40, b=20, l=20, r=20),
                legend=dict(
                    bgcolor="rgba(0,0,0,0)",
                    font=dict(color=FONT_COLOR, size=12),
                ),
            )
            return fig

        # ── Fila 1: Pie de gastos | Pie de ingresos ──────────────
        st.markdown("### 🥧 Distribución por categorías")
        col_g, col_i = st.columns(2)

        with col_g:
            st.markdown('<p class="grafico-titulo">🔴 Gastos por categoría</p>',
                        unsafe_allow_html=True)
            if df_gastos.empty:
                st.warning("Sin gastos registrados.")
            else:
                grp_g = df_gastos.groupby("Categoría")["Monto"].sum().reset_index()
                fig_pie_g = px.pie(
                    grp_g, names="Categoría", values="Monto",
                    color_discrete_sequence=px.colors.qualitative.Set1,
                    hole=0.40,
                )
                fig_pie_g.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(estilo_fig(fig_pie_g), use_container_width=True)

        with col_i:
            st.markdown('<p class="grafico-titulo">🟢 Ingresos por categoría</p>',
                        unsafe_allow_html=True)
            if df_ingresos.empty:
                st.warning("Sin ingresos registrados.")
            else:
                grp_i = df_ingresos.groupby("Categoría")["Monto"].sum().reset_index()
                fig_pie_i = px.pie(
                    grp_i, names="Categoría", values="Monto",
                    color_discrete_sequence=px.colors.qualitative.Set2,
                    hole=0.40,
                )
                fig_pie_i.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(estilo_fig(fig_pie_i), use_container_width=True)

        st.markdown("---")

        # ── Fila 2: Barras comparativas por categoría ─────────────
        st.markdown("### 📊 Montos por categoría")
        col_bg, col_bi = st.columns(2)

        with col_bg:
            st.markdown('<p class="grafico-titulo">Gastos por categoría</p>',
                        unsafe_allow_html=True)
            if not df_gastos.empty:
                grp_bg = (df_gastos.groupby("Categoría")["Monto"]
                          .sum().sort_values(ascending=False).reset_index())
                fig_bg = px.bar(
                    grp_bg, x="Categoría", y="Monto",
                    color="Monto",
                    color_continuous_scale="Reds",
                    text_auto=".2s",
                )
                fig_bg.update_traces(textposition="outside")
                fig_bg.update_layout(coloraxis_showscale=False,
                                     xaxis_tickangle=-30)
                st.plotly_chart(estilo_fig(fig_bg), use_container_width=True)

        with col_bi:
            st.markdown('<p class="grafico-titulo">Ingresos por categoría</p>',
                        unsafe_allow_html=True)
            if not df_ingresos.empty:
                grp_bi = (df_ingresos.groupby("Categoría")["Monto"]
                          .sum().sort_values(ascending=False).reset_index())
                fig_bi = px.bar(
                    grp_bi, x="Categoría", y="Monto",
                    color="Monto",
                    color_continuous_scale="Greens",
                    text_auto=".2s",
                )
                fig_bi.update_traces(textposition="outside")
                fig_bi.update_layout(coloraxis_showscale=False,
                                     xaxis_tickangle=-30)
                st.plotly_chart(estilo_fig(fig_bi), use_container_width=True)

        st.markdown("---")

        # ── Fila 3: Evolución temporal ────────────────────────────
        st.markdown("### 📈 Evolución en el tiempo")
        df_time = df.copy()
        df_time["Fecha"] = pd.to_datetime(df_time["Fecha"], errors="coerce")
        df_time = df_time.dropna(subset=["Fecha"])

        if not df_time.empty:
            df_pivot = (df_time.groupby(["Fecha", "Tipo"])["Monto"]
                        .sum().reset_index())
            fig_line = px.line(
                df_pivot, x="Fecha", y="Monto", color="Tipo",
                markers=True,
                color_discrete_map={"Ingreso": "#4fffb0", "Gasto": "#ff6b6b"},
                labels={"Monto": "Monto ($)", "Fecha": "Fecha"},
            )
            fig_line.update_traces(line_width=2.5, marker_size=7)
            fig_line.update_xaxes(showgrid=False)
            fig_line.update_yaxes(showgrid=True,
                                  gridcolor="rgba(255,255,255,0.08)")
            st.plotly_chart(estilo_fig(fig_line), use_container_width=True)
        else:
            st.warning("No hay datos con fechas válidas para la evolución temporal.")

        st.markdown("---")

        # ── Indicador de balance visual ────────────────────────────
        st.markdown("### ⚖️ Balance total")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=balance,
            delta={"reference": 0, "valueformat": ",.2f"},
            number={"prefix": "$", "valueformat": ",.2f",
                    "font": {"size": 40, "color": FONT_COLOR}},
            gauge={
                "axis": {"range": [-(gastos_total or 1), (ingresos_total or 1)],
                         "tickcolor": FONT_COLOR},
                "bar":  {"color": "#4fffb0" if balance >= 0 else "#ff6b6b"},
                "bgcolor": "rgba(255,255,255,0.05)",
                "steps": [
                    {"range": [-(gastos_total or 1), 0],
                     "color": "rgba(255,107,107,0.15)"},
                    {"range": [0, (ingresos_total or 1)],
                     "color": "rgba(79,255,176,0.15)"},
                ],
                "threshold": {
                    "line": {"color": "white", "width": 2},
                    "thickness": 0.75,
                    "value": balance,
                },
            },
        ))
        fig_gauge.update_layout(
            paper_bgcolor=PAPER_BG,
            font=dict(color=FONT_COLOR, family="Sora, sans-serif"),
            margin=dict(t=30, b=10, l=30, r=30),
            height=280,
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
