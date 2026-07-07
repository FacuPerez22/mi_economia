import streamlit as st
import datetime
import db

st.set_page_config(page_title="Mi Economía", layout="wide")
st.title("🚕 Mi Economía - Control Taxi del FACU 4722")

tab_tablero, tab_gasto, tab_turno, tab_cierre = st.tabs([
    "📊 Tablero", "💸 Cargar Gasto", "🚗 Cargar Turno", "📅 Cierre Mensual"
])

# ---------------------------------------------------
with tab_gasto:
    st.header("Cargar un gasto")

    categorias = db.obtener_categorias()
    nombres_categorias = [nombre for id_cat, nombre in categorias]

    with st.form("form_gasto", clear_on_submit=True):
        fecha = st.date_input("Fecha", value=datetime.date.today())
        categoria_nombre = st.selectbox("Categoría", nombres_categorias)
        monto = st.number_input("Monto ($)", min_value=0, step=100, format="%d")
        descripcion = st.text_input("Descripción (opcional)")
        metodo_pago = st.radio("Método de pago", ["Efectivo", "Tarjeta"])

        enviado = st.form_submit_button("Guardar gasto")
        if enviado:
            categoria_id = next(id_cat for id_cat, nombre in categorias if nombre == categoria_nombre)
            db.guardar_gasto(fecha, categoria_id, monto, descripcion, metodo_pago)
            st.success(f"¡Gasto de ${monto} en '{categoria_nombre}' guardado! ✅")

    st.divider()
    st.subheader("¿Necesitás una categoría nueva?")
    with st.form("form_nueva_categoria", clear_on_submit=True):
        nueva_categoria = st.text_input("Nombre de la categoría nueva (ej: Veterinario)")
        agregar = st.form_submit_button("Agregar categoría")
        if agregar and nueva_categoria.strip() != "":
            db.agregar_categoria(nueva_categoria.strip())
            st.success(f"Categoría '{nueva_categoria}' agregada. Ya la vas a ver en el desplegable de arriba.")
            st.rerun()

# ---------------------------------------------------
with tab_turno:
    st.header("Cargar el turno de hoy")

    with st.form("form_turno", clear_on_submit=True):
        fecha = st.date_input("Fecha", value=datetime.date.today(), key="fecha_turno")
        recaudacion_reloj = st.number_input("Recaudación del reloj ($)", min_value=0, step=100, format="%d")
        recaudacion_apps = st.number_input("Recaudación de apps ($)", min_value=0, step=100, format="%d")
        gasto_gnc = st.number_input("Gasto en GNC ($)", min_value=0, step=100, format="%d")
        gasto_nafta = st.number_input("Gasto en Nafta ($)", min_value=0, step=100, format="%d")

        enviado = st.form_submit_button("Guardar turno")
        if enviado:
            db.guardar_turno_diario(fecha, recaudacion_reloj, recaudacion_apps, gasto_gnc, gasto_nafta)
            diferencia = recaudacion_reloj - recaudacion_apps
            st.success(f"¡Turno guardado! Recaudación pura de calle: ${diferencia:.2f} ✅")

# ---------------------------------------------------
with tab_cierre:
    st.header("Cargar el ticket mensual del reloj")

    with st.form("form_cierre", clear_on_submit=True):
        mes_anio = st.text_input("Mes (formato AAAA-MM, ej: 2026-06)")
        km_totales = st.number_input("KM Totales", min_value=0, step=1)
        km_ocupados = st.number_input("KM Ocupados", min_value=0, step=1)
        fichas_totales = st.number_input("Fichas Totales", min_value=0, step=1)
        cantidad_viajes = st.number_input("Cantidad de Viajes", min_value=0, step=1)

        enviado = st.form_submit_button("Guardar cierre")
        if enviado:
            db.guardar_cierre_mensual(mes_anio, km_totales, km_ocupados, fichas_totales, cantidad_viajes)
            st.success(f"¡Cierre de {mes_anio} guardado! ✅")

# ---------------------------------------------------
with tab_tablero:
    st.header("Tu tablero")

    gastos = db.obtener_gastos()
    turnos = db.obtener_turnos()
    cierres = db.obtener_cierres()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💰 Poder de ahorro")
        ingresos = turnos["recaudacion_reloj"].sum() if not turnos.empty else 0
        gastos_totales = gastos["monto"].sum() if not gastos.empty else 0
        ahorro = ingresos - gastos_totales

        st.metric("Ingresos totales", f"${ingresos:,.0f}")
        st.metric("Gastos totales", f"${gastos_totales:,.0f}")
        st.metric("Poder de ahorro", f"${ahorro:,.0f}")

    with col2:
        st.subheader("🚗 Eficiencia del auto")
        if not cierres.empty:
            ultimo = cierres.iloc[0]
            eficiencia = (ultimo["km_ocupados_mes"] / ultimo["km_totales_mes"]) * 100
            st.metric(f"Eficiencia ({ultimo['mes_anio']})", f"{eficiencia:.1f}%")
            st.metric("KM Totales", f"{ultimo['km_totales_mes']}")
            st.metric("KM Ocupados", f"{ultimo['km_ocupados_mes']}")
        else:
            st.info("Todavía no cargaste ningún cierre mensual.")

    st.divider()

    st.subheader("📋 Últimos gastos cargados")
    st.dataframe(gastos, use_container_width=True)

    st.subheader("📋 Últimos turnos cargados")
    st.dataframe(turnos, use_container_width=True)

    #streamlit run app.py --server.address=0.0.0.0
    