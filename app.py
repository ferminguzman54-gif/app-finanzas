import streamlit as st
import pandas as pd

# Título de la página
st.set_page_config(page_title="Mis Finanzas", page_icon="💸")
st.title("💸 Gestor de Finanzas Personales")

# Subtítulo
st.write("Bienvenido a tu nueva aplicación. Aquí podrás registrar y analizar tus gastos.")

# Un formulario básico para registrar datos
st.subheader("Registrar un nuevo movimiento")
with st.form("registro_gastos"):
    concepto = st.text_input("Concepto (ej. Comida, Transporte)")
    monto = st.number_input("Monto", min_value=0.0, format="%f")
    tipo = st.selectbox("Tipo", ["Gasto", "Ingreso"])
    
    # Botón para guardar
    guardado = st.form_submit_button("Guardar Registro")
    
    if guardado:
        st.success(f"¡Registraste un {tipo} de ${monto} en {concepto}!")

# Nota sobre el futuro de la app
st.info("💡 Más adelante, podemos conectar esta aplicación para que guarde todos los registros automáticamente en un Google Sheets.")
