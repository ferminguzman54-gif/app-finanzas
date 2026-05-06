import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
from datetime import datetime, date

# ─────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Mis Finanzas",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────
# ESTILOS GLOBALES
# ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Sora', sans-serif; }

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
    line-height: 1.5;
    text-align: right;
    backdrop-filter: blur(8px);
    max-width: 360px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d1a 0%, #141428 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* Título */
.titulo-principal {
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(90deg, #4fffb0, #00c6ff, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.2rem;
}

.subtitulo { color: rgba(255,255,255,0.5); font-size: 0.95rem; margin-bottom: 2rem; }

/* Tarjetas de métricas */
.metric-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px;
    padding: 20px 24px;
    text-align: center;
    backdrop-filter: blur(10px);
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.metric-card:hover { transform: translateY(-3px); border-color: rgba(79,255,176,0.3); }
.metric-valor { font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: 600; margin: 4px 0; }
.metric-label { font-size: 0.78rem; color: rgba(255,255,255,0.5); text-transform: uppercase; letter-spacing: 1px; }

/* Botones */
.stButton > button {
    background: linear-gradient(135deg, #4fffb0, #00c6ff);
    color: #0a0a15;
    border: none;
    border-radius: 10px;
    font-family: 'Sora', sans-serif;
    font-weight: 600;
    font-size: 0.9rem;
    padding: 0.55rem 1.2rem;
    transition: opacity 0.2s ease, transform 0.1s ease;
}
.stButton > button:hover { opacity: 0.85; transform: scale(1.02); }

/* Leyenda de obligatorios */
.leyenda-req { color: rgba(255,255,255,0.45); font-size: 0.8rem; margin-bottom: 0.6rem; }
.req { color: #ff6b6b; font-weight: 700; }

/* Calculadora resultado */
.calc-box {
    background: rgba(79,255,176,0.08);
    border: 1px solid rgba(79,255,176,0.25);
    border-radius: 10px;
    padding: 10px 18px;
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.35rem;
    color: #4fffb0;
    margin-top: 6px;
}

/* Gráfico titulo */
.grafico-titulo { font-size: 1.1rem; font-weight: 600; color: rgba(255,255,255,0.85); margin-bottom: 0.4rem; }

hr { border-color: rgba(255,255,255,0.08); margin: 1.2rem 0; }
</style>

<div class="credito-header">
    📘 Proyecto de <strong>Fermín Guzmán</strong> y <strong>Esteban Pedraza</strong><br>
    Materia: <em>Diseño de productos</em>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────────────
ARCHIVO_CSV         = "transacciones.csv"
ARCHIVO_PRESUPUESTO = "presupuesto.json"
COLUMNAS = ["ID", "Fecha", "Hora", "Concepto", "Categoría", "Tipo", "Monto", "Cuenta"]

CATEGORIAS_GASTO   = ["Alimentación", "Transporte", "Entretenimiento", "Salud",
                      "Educación", "Ropa", "Hogar", "Servicios", "Otros"]
CATEGORIAS_INGRESO = ["Salario", "Freelance", "Inversiones", "Regalo",
                      "Venta", "Bono", "Otros"]
CUENTAS = ["Efectivo", "Ahorro", "Cuenta bancaria",
           "Tarjeta de crédito", "Inversiones", "Otra"]

# ─────────────────────────────────────────────────────────────────────
# HELPERS DE PERSISTENCIA
# ─────────────────────────────────────────────────────────────────────
def cargar_datos() -> pd.DataFrame:
    if os.path.exists(ARCHIVO_CSV):
        df = pd.read_csv(ARCHIVO_CSV, encoding="utf-8")
        for col in COLUMNAS:
            if col not in df.columns:
                df[col] = ""
        return df[COLUMNAS]
    return pd.DataFrame(columns=COLUMNAS)

def guardar_datos(df: pd.DataFrame):
    df.to_csv(ARCHIVO_CSV, index=False, encoding="utf-8")

def cargar_presupuesto() -> dict:
    if os.path.exists(ARCHIVO_PRESUPUESTO):
        with open(ARCHIVO_PRESUPUESTO, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"activo": False, "monto": 1000.0}

def guardar_presupuesto(data: dict):
    with open(ARCHIVO_PRESUPUESTO, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

def siguiente_id(df: pd.DataFrame) -> int:
    return 1 if df.empty else int(df["ID"].max()) + 1

# ─────────────────────────────────────────────────────────────────────
# ESTADO DE SESIÓN
# ─────────────────────────────────────────────────────────────────────
if "df"                not in st.session_state:
    st.session_state.df                = cargar_datos()
if "presupuesto"       not in st.session_state:
    st.session_state.presupuesto       = cargar_presupuesto()
if "calc_resultado"    not in st.session_state:
    st.session_state.calc_resultado    = None
if "monto_precargado"  not in st.session_state:
    st.session_state.monto_precargado  = 0.01
# tipo_seleccionado vive fuera del form para que las categorías sean dinámicas
if "tipo_seleccionado" not in st.session_state:
    st.session_state.tipo_seleccionado = "Gasto"

df          = st.session_state.df
presupuesto = st.session_state.presupuesto

# ─────────────────────────────────────────────────────────────────────
# MÉTRICAS GLOBALES
# ─────────────────────────────────────────────────────────────────────
ingresos_total  = df[df["Tipo"] == "Ingreso"]["Monto"].sum() if not df.empty else 0.0
gastos_total    = df[df["Tipo"] == "Gasto"]["Monto"].sum()   if not df.empty else 0.0
balance         = ingresos_total - gastos_total
n_transacciones = len(df)
balance_color   = "#4fffb0" if balance >= 0 else "#ff6b6b"

# ─────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💸 Mis Finanzas")
    st.markdown("---")
    pagina = st.radio(
        "nav",
        ["📝 Registrar Transacción", "📋 Historial", "📊 Gráficos"],
        label_visibility="collapsed",
    )
    st.markdown("---")

    # ── Resumen rápido con colores correctos ──
    st.markdown("**Resumen rápido**")
    st.markdown(
        f'🟢 Ingresos:&nbsp;<span style="color:#4fffb0;font-family:monospace;font-weight:600">'
        f'${ingresos_total:,.2f}</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'🔴 Gastos:&nbsp;<span style="color:#ff6b6b;font-family:monospace;font-weight:600">'
        f'${gastos_total:,.2f}</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'⚖️ Balance:&nbsp;<span style="color:{balance_color};font-family:monospace;font-weight:700">'
        f'${balance:,.2f}</span>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── Presupuesto mensual ──
    st.markdown("**⚙️ Presupuesto mensual**")
    pres_activo = st.toggle("Activar presupuesto", value=presupuesto.get("activo", False))

    if pres_activo:
        monto_pres_inp = st.number_input(
            "Monto mensual ($)",
            min_value=1.0,
            value=float(presupuesto.get("monto", 1000.0)),
            step=50.0,
            format="%.2f",
        )
        if st.button("💾 Guardar presupuesto"):
            nuevo_pres = {"activo": True, "monto": monto_pres_inp}
            st.session_state.presupuesto = nuevo_pres
            guardar_presupuesto(nuevo_pres)
            presupuesto = nuevo_pres
            st.success("✅ Presupuesto guardado.")
    else:
        if presupuesto.get("activo"):
            nuevo_pres = {"activo": False, "monto": presupuesto.get("monto", 1000.0)}
            st.session_state.presupuesto = nuevo_pres
            guardar_presupuesto(nuevo_pres)
            presupuesto = nuevo_pres

    st.markdown("---")
    st.caption("v3.0 — Gestor de Finanzas")

# ─────────────────────────────────────────────────────────────────────
# ENCABEZADO PRINCIPAL
# ─────────────────────────────────────────────────────────────────────
st.markdown('<p class="titulo-principal">💸 Gestor de Finanzas Personales</p>',
            unsafe_allow_html=True)
st.markdown('<p class="subtitulo">Registra, analiza y visualiza tus movimientos financieros.</p>',
            unsafe_allow_html=True)

# ─── TARJETAS DE MÉTRICAS ─────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">💰 Total Ingresos</div>
        <div class="metric-valor" style="color:#4fffb0">${ingresos_total:,.2f}</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">💸 Total Gastos</div>
        <div class="metric-valor" style="color:#ff6b6b">${gastos_total:,.2f}</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">⚖️ Balance</div>
        <div class="metric-valor" style="color:{balance_color}">${balance:,.2f}</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🗒️ Transacciones</div>
        <div class="metric-valor" style="color:#60a5fa">{n_transacciones}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── ALERTA DE PRESUPUESTO (global, siempre visible) ─────────────────
presupuesto = st.session_state.presupuesto
if presupuesto.get("activo") and presupuesto.get("monto", 0) > 0:
    mp  = presupuesto["monto"]
    pct = (gastos_total / mp) * 100
    if pct >= 100:
        st.error(
            f"⚠️ **¡Superaste tu presupuesto!** Llevas gastado **${gastos_total:,.2f}** "
            f"de **${mp:,.2f}** ({pct:.1f} %). Revisa tus prioridades y modera los gastos."
        )
    elif pct >= 80:
        st.warning(
            f"🔔 **Cuidado**, llevas el {pct:.1f} % de tu presupuesto gastado "
            f"(${gastos_total:,.2f} de ${mp:,.2f}). Mantén el control."
        )
    elif pct > 0:
        st.success(
            f"✅ **¡Vas muy bien!** Solo has usado el {pct:.1f} % de tu presupuesto "
            f"(${gastos_total:,.2f} de ${mp:,.2f}). ¡Tu plan marcha exactamente como lo planeaste!"
        )

# ═════════════════════════════════════════════════════════════════════
# PÁGINA 1 — REGISTRAR TRANSACCIÓN
# ═════════════════════════════════════════════════════════════════════
if pagina == "📝 Registrar Transacción":
    st.subheader("📝 Registrar nueva transacción")
    st.markdown(
        '<p class="leyenda-req"><span class="req">*</span> Indica campo obligatorio</p>',
        unsafe_allow_html=True,
    )

    # ── TIPO fuera del form → permite actualizar categorías dinámicamente ──
    tipo_sel = st.selectbox(
        "Tipo de movimiento *",
        ["Gasto", "Ingreso"],
        index=0 if st.session_state.tipo_seleccionado == "Gasto" else 1,
        key="tipo_seleccionado",
    )
    cats = CATEGORIAS_GASTO if tipo_sel == "Gasto" else CATEGORIAS_INGRESO

    # ── CALCULADORA (fuera del form para permitir interacción) ────────────
    with st.expander("🧮 Calculadora de apoyo — el resultado se puede usar como monto"):
        col_c1, col_c2, col_c3 = st.columns([5, 2, 5])
        with col_c1:
            c_n1 = st.number_input("Número 1", value=0.0, step=0.01, format="%.2f", key="c_n1")
        with col_c2:
            c_op = st.selectbox("Op.", ["+", "−", "×", "÷"], key="c_op",
                                label_visibility="hidden")
        with col_c3:
            c_n2 = st.number_input("Número 2", value=0.0, step=0.01, format="%.2f", key="c_n2")

        col_calc_btn, col_calc_res = st.columns([1, 2])
        with col_calc_btn:
            if st.button("= Calcular", key="btn_calc"):
                if c_op == "÷" and c_n2 == 0:
                    st.error("División entre cero no permitida.")
                    st.session_state.calc_resultado = None
                else:
                    ops = {"+": c_n1 + c_n2, "−": c_n1 - c_n2,
                           "×": c_n1 * c_n2, "÷": c_n1 / c_n2}
                    st.session_state.calc_resultado = round(ops[c_op], 2)

        with col_calc_res:
            if st.session_state.calc_resultado is not None:
                r = st.session_state.calc_resultado
                st.markdown(f'<div class="calc-box">= &nbsp;${r:,.2f}</div>',
                            unsafe_allow_html=True)

        if st.session_state.calc_resultado is not None:
            if st.button("📋 Usar como monto del registro", key="btn_usar_calc"):
                st.session_state.monto_precargado = float(st.session_state.calc_resultado)
                st.success(f"Monto ${st.session_state.calc_resultado:,.2f} listo para el formulario.")

    st.markdown("")

    # ── FORMULARIO ────────────────────────────────────────────────────────
    with st.form("registro_form", clear_on_submit=True):
        col_izq, col_der = st.columns(2)

        with col_izq:
            concepto  = st.text_input("Concepto *", placeholder="Ej. Café, Nómina, Netflix…")
            categoria = st.selectbox("Categoría *", cats)
            cuenta    = st.selectbox("Cuenta *", CUENTAS)

        with col_der:
            monto_val = float(max(0.01, st.session_state.monto_precargado))
            monto     = st.number_input("Monto ($) *", min_value=0.01, value=monto_val,
                                        step=0.01, format="%.2f")
            fecha_sel = st.date_input("Fecha *", value=date.today())
            hora_sel  = st.time_input("Hora *", value=datetime.now().time(), step=60)

        nota = st.text_area("Notas adicionales", height=72,
                            placeholder="Detalle opcional…")

        guardar = st.form_submit_button("💾 Guardar Transacción", use_container_width=True)

    if guardar:
        errores = []
        if not concepto.strip():
            errores.append("El **concepto** es obligatorio.")
        if monto <= 0:
            errores.append("El **monto** debe ser mayor a cero.")
        if errores:
            for e in errores:
                st.error(f"⚠️ {e}")
        else:
            nueva = {
                "ID":        siguiente_id(st.session_state.df),
                "Fecha":     str(fecha_sel),
                "Hora":      hora_sel.strftime("%H:%M"),
                "Concepto":  concepto.strip(),
                "Categoría": categoria,
                "Tipo":      tipo_sel,
                "Monto":     round(monto, 2),
                "Cuenta":    cuenta,
            }
            st.session_state.df = pd.concat(
                [st.session_state.df, pd.DataFrame([nueva])], ignore_index=True
            )
            guardar_datos(st.session_state.df)
            st.session_state.monto_precargado = 0.01
            st.session_state.calc_resultado   = None
            emoji = "🟢" if tipo_sel == "Ingreso" else "🔴"
            st.success(
                f"{emoji} ¡Registrado! **{tipo_sel}** de **${monto:,.2f}** "
                f"en **{categoria}** — {cuenta} — *{concepto}* "
                f"({fecha_sel} {hora_sel.strftime('%H:%M')})"
            )
            st.rerun()

# ═════════════════════════════════════════════════════════════════════
# PÁGINA 2 — HISTORIAL
# ═════════════════════════════════════════════════════════════════════
elif pagina == "📋 Historial":
    st.subheader("📋 Historial de transacciones")

    if df.empty:
        st.info("📭 Aún no hay transacciones registradas. ¡Empieza en la sección de Registro!")
    else:
        df = st.session_state.df

        # ── Banner de presupuesto ──
        presupuesto = st.session_state.presupuesto
        if presupuesto.get("activo") and presupuesto.get("monto", 0) > 0:
            mp  = presupuesto["monto"]
            pct = (gastos_total / mp) * 100
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                st.metric("Presupuesto mensual", f"${mp:,.2f}")
            with col_p2:
                st.metric("Total gastado", f"${gastos_total:,.2f}",
                          delta=f"{pct:.1f} % del presupuesto",
                          delta_color="inverse")
            with col_p3:
                restante = mp - gastos_total
                st.metric("Restante", f"${restante:,.2f}",
                          delta_color="normal" if restante >= 0 else "inverse")
            st.markdown("---")

        # ── Filtros ──
        with st.expander("🔍 Filtros", expanded=True):
            f1, f2, f3, f4 = st.columns(4)
            with f1:
                filtro_tipo = st.multiselect("Tipo", ["Gasto", "Ingreso"],
                                             default=["Gasto", "Ingreso"])
            with f2:
                todas_cats = sorted(df["Categoría"].dropna().unique().tolist())
                filtro_cat = st.multiselect("Categoría", todas_cats, default=todas_cats)
            with f3:
                todas_cuentas = sorted(df["Cuenta"].dropna().unique().tolist()) \
                    if "Cuenta" in df.columns else []
                filtro_cuenta = st.multiselect("Cuenta", todas_cuentas,
                                               default=todas_cuentas) if todas_cuentas else []
            with f4:
                filtro_buscar = st.text_input("Buscar concepto", placeholder="Escribe algo…")

        df_filtrado = df[
            df["Tipo"].isin(filtro_tipo) &
            df["Categoría"].isin(filtro_cat)
        ]
        if filtro_cuenta:
            df_filtrado = df_filtrado[df_filtrado["Cuenta"].isin(filtro_cuenta)]
        if filtro_buscar:
            df_filtrado = df_filtrado[
                df_filtrado["Concepto"].str.contains(filtro_buscar, case=False, na=False)
            ]

        df_mostrar = (
            df_filtrado
            .sort_values(["Fecha", "Hora"], ascending=[False, False])
            .reset_index(drop=True)
        )
        st.markdown(f"**{len(df_mostrar)}** transacciones encontradas")

        def color_tipo(val):
            if val == "Ingreso":
                return "background-color:rgba(79,255,176,0.15);color:#4fffb0;"
            return "background-color:rgba(255,107,107,0.15);color:#ff6b6b;"

        styled = (
            df_mostrar.style
            .applymap(color_tipo, subset=["Tipo"])
            .format({"Monto": "${:,.2f}"})
        )
        st.dataframe(styled, use_container_width=True, height=420)

        # ── Exportar CSV con BOM para que Excel maneje acentos correctamente ──
        csv_bytes = df_mostrar.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            "⬇️ Exportar historial filtrado (.csv)",
            data=csv_bytes,
            file_name="historial_finanzas.csv",
            mime="text/csv; charset=utf-8-sig",
        )

        st.markdown("---")
        st.markdown("**🗑️ Eliminar transacción por ID**")
        col_d1, col_d2 = st.columns([1, 3])
        with col_d1:
            id_del = st.number_input("ID", min_value=1, step=1,
                                     label_visibility="collapsed")
        with col_d2:
            if st.button("🗑️ Eliminar"):
                if int(id_del) in st.session_state.df["ID"].values:
                    st.session_state.df = (
                        st.session_state.df[st.session_state.df["ID"] != int(id_del)]
                        .reset_index(drop=True)
                    )
                    guardar_datos(st.session_state.df)
                    st.success(f"Transacción #{int(id_del)} eliminada.")
                    st.rerun()
                else:
                    st.error(f"No existe ninguna transacción con ID {int(id_del)}.")

# ═════════════════════════════════════════════════════════════════════
# PÁGINA 3 — GRÁFICOS
# ═════════════════════════════════════════════════════════════════════
elif pagina == "📊 Gráficos":
    st.subheader("📊 Análisis visual de tus finanzas")

    if df.empty:
        st.info("📭 Registra algunas transacciones para ver los gráficos.")
    else:
        df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce")
        df_gastos   = df[df["Tipo"] == "Gasto"]
        df_ingresos = df[df["Tipo"] == "Ingreso"]

        PAPER_BG   = "rgba(255,255,255,0.04)"
        FONT_COLOR = "rgba(255,255,255,0.82)"

        def estilo_fig(fig):
            fig.update_layout(
                paper_bgcolor=PAPER_BG,
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=FONT_COLOR, family="Sora, sans-serif"),
                margin=dict(t=40, b=20, l=20, r=20),
                legend=dict(bgcolor="rgba(0,0,0,0)",
                            font=dict(color=FONT_COLOR, size=12)),
            )
            return fig

        # ── Presupuesto vs Gasto ──────────────────────────────────────────
        presupuesto = st.session_state.presupuesto
        if presupuesto.get("activo") and presupuesto.get("monto", 0) > 0:
            mp  = presupuesto["monto"]
            pct = (gastos_total / mp) * 100
            st.markdown("### 💰 Presupuesto vs. Gasto actual")
            fig_pres = go.Figure(go.Bar(
                x=["Presupuesto mensual", "Total gastado"],
                y=[mp, gastos_total],
                marker_color=["#60a5fa",
                              "#ff6b6b" if gastos_total > mp else "#4fffb0"],
                text=[f"${mp:,.2f}", f"${gastos_total:,.2f}"],
                textposition="outside",
                width=[0.4, 0.4],
            ))
            fig_pres.update_layout(
                paper_bgcolor=PAPER_BG, plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=FONT_COLOR, family="Sora, sans-serif"),
                margin=dict(t=30, b=20, l=20, r=20),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.07)"),
            )
            st.plotly_chart(fig_pres, use_container_width=True)
            st.markdown("---")

        # ── Pie por categorías ────────────────────────────────────────────
        st.markdown("### 🥧 Distribución por categorías")
        col_g, col_i = st.columns(2)

        with col_g:
            st.markdown('<p class="grafico-titulo">🔴 Gastos por categoría</p>',
                        unsafe_allow_html=True)
            if df_gastos.empty:
                st.warning("Sin gastos registrados.")
            else:
                grp_g = df_gastos.groupby("Categoría")["Monto"].sum().reset_index()
                fig_pg = px.pie(grp_g, names="Categoría", values="Monto",
                                color_discrete_sequence=px.colors.qualitative.Set1,
                                hole=0.40)
                fig_pg.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(estilo_fig(fig_pg), use_container_width=True)

        with col_i:
            st.markdown('<p class="grafico-titulo">🟢 Ingresos por categoría</p>',
                        unsafe_allow_html=True)
            if df_ingresos.empty:
                st.warning("Sin ingresos registrados.")
            else:
                grp_i = df_ingresos.groupby("Categoría")["Monto"].sum().reset_index()
                fig_pi = px.pie(grp_i, names="Categoría", values="Monto",
                                color_discrete_sequence=px.colors.qualitative.Set2,
                                hole=0.40)
                fig_pi.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(estilo_fig(fig_pi), use_container_width=True)

        st.markdown("---")

        # ── Barras por categoría ─────────────────────────────────────────
        st.markdown("### 📊 Montos por categoría")
        col_bg, col_bi = st.columns(2)

        with col_bg:
            st.markdown('<p class="grafico-titulo">Gastos</p>', unsafe_allow_html=True)
            if not df_gastos.empty:
                grp_bg = (df_gastos.groupby("Categoría")["Monto"]
                          .sum().sort_values(ascending=False).reset_index())
                fig_bg = px.bar(grp_bg, x="Categoría", y="Monto",
                                color="Monto", color_continuous_scale="Reds",
                                text_auto=".2s")
                fig_bg.update_traces(textposition="outside")
                fig_bg.update_layout(coloraxis_showscale=False, xaxis_tickangle=-30)
                st.plotly_chart(estilo_fig(fig_bg), use_container_width=True)

        with col_bi:
            st.markdown('<p class="grafico-titulo">Ingresos</p>', unsafe_allow_html=True)
            if not df_ingresos.empty:
                grp_bi = (df_ingresos.groupby("Categoría")["Monto"]
                          .sum().sort_values(ascending=False).reset_index())
                fig_bi = px.bar(grp_bi, x="Categoría", y="Monto",
                                color="Monto", color_continuous_scale="Greens",
                                text_auto=".2s")
                fig_bi.update_traces(textposition="outside")
                fig_bi.update_layout(coloraxis_showscale=False, xaxis_tickangle=-30)
                st.plotly_chart(estilo_fig(fig_bi), use_container_width=True)

        st.markdown("---")

        # ── Por cuenta ───────────────────────────────────────────────────
        if "Cuenta" in df.columns and df["Cuenta"].dropna().any():
            st.markdown("### 🏦 Distribución por cuenta")
            col_cg, col_ci = st.columns(2)

            with col_cg:
                st.markdown('<p class="grafico-titulo">Gastos por cuenta</p>',
                            unsafe_allow_html=True)
                if not df_gastos.empty:
                    grp_cg = df_gastos.groupby("Cuenta")["Monto"].sum().reset_index()
                    fig_cg = px.pie(grp_cg, names="Cuenta", values="Monto",
                                    color_discrete_sequence=px.colors.qualitative.Pastel1,
                                    hole=0.35)
                    fig_cg.update_traces(textposition="inside", textinfo="percent+label")
                    st.plotly_chart(estilo_fig(fig_cg), use_container_width=True)

            with col_ci:
                st.markdown('<p class="grafico-titulo">Ingresos por cuenta</p>',
                            unsafe_allow_html=True)
                if not df_ingresos.empty:
                    grp_ci = df_ingresos.groupby("Cuenta")["Monto"].sum().reset_index()
                    fig_ci = px.pie(grp_ci, names="Cuenta", values="Monto",
                                    color_discrete_sequence=px.colors.qualitative.Pastel2,
                                    hole=0.35)
                    fig_ci.update_traces(textposition="inside", textinfo="percent+label")
                    st.plotly_chart(estilo_fig(fig_ci), use_container_width=True)

            st.markdown("---")

        # ── Evolución temporal ───────────────────────────────────────────
        st.markdown("### 📈 Evolución en el tiempo")
        df_time = df.copy()
        df_time["Fecha"] = pd.to_datetime(df_time["Fecha"], errors="coerce")
        df_time = df_time.dropna(subset=["Fecha"])

        if not df_time.empty:
            df_pivot = (df_time.groupby(["Fecha", "Tipo"])["Monto"]
                        .sum().reset_index())
            fig_line = px.line(
                df_pivot, x="Fecha", y="Monto", color="Tipo", markers=True,
                color_discrete_map={"Ingreso": "#4fffb0", "Gasto": "#ff6b6b"},
            )
            fig_line.update_traces(line_width=2.5, marker_size=7)
            fig_line.update_xaxes(showgrid=False)
            fig_line.update_yaxes(showgrid=True,
                                  gridcolor="rgba(255,255,255,0.07)")
            st.plotly_chart(estilo_fig(fig_line), use_container_width=True)
        else:
            st.warning("No hay fechas válidas para la línea de tiempo.")

        st.markdown("---")

        # ── Gauge de balance ─────────────────────────────────────────────
        st.markdown("### ⚖️ Balance total")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=balance,
            delta={"reference": 0, "valueformat": ",.2f"},
            number={"prefix": "$", "valueformat": ",.2f",
                    "font": {"size": 42, "color": FONT_COLOR}},
            gauge={
                "axis": {
                    "range": [-(gastos_total or 1), (ingresos_total or 1)],
                    "tickcolor": FONT_COLOR,
                },
                "bar":  {"color": "#4fffb0" if balance >= 0 else "#ff6b6b"},
                "bgcolor": "rgba(255,255,255,0.05)",
                "steps": [
                    {"range": [-(gastos_total or 1), 0],
                     "color": "rgba(255,107,107,0.12)"},
                    {"range": [0, (ingresos_total or 1)],
                     "color": "rgba(79,255,176,0.12)"},
                ],
            },
        ))
        fig_gauge.update_layout(
            paper_bgcolor=PAPER_BG,
            font=dict(color=FONT_COLOR, family="Sora, sans-serif"),
            margin=dict(t=30, b=10, l=30, r=30),
            height=280,
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
