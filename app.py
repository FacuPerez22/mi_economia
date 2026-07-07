import streamlit as st
import datetime
import db

st.set_page_config(page_title="Mi Economía", layout="wide")

# ---------------------------------------------------
# LOGIN
# ---------------------------------------------------
if "usuario_id" not in st.session_state:
    st.session_state.usuario_id = None
    st.session_state.usuario_nombre = None

if st.session_state.usuario_id is None:
    st.title("🚕 Mi Economía - Control Taxi del FACU 4722")
    st.subheader("Iniciar sesión")

    with st.form("form_login"):
        usuario_input = st.text_input("Usuario")
        password_input = st.text_input("Contraseña", type="password")
        entrar = st.form_submit_button("Ingresar")

        if entrar:
            usuario_id = db.verificar_login(usuario_input, password_input)
            if usuario_id is not None:
                st.session_state.usuario_id = usuario_id
                st.session_state.usuario_nombre = usuario_input
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos ❌")

    st.stop()

# ---------------------------------------------------
# A PARTIR DE ACÁ, YA ESTÁ LOGUEADO
# ---------------------------------------------------
usuario_id = st.session_state.usuario_id

col_titulo, col_logout = st.columns([5, 1])
with col_titulo:
    st.title("🚕 Mi Economía - Control Taxi del FACU 4722")
with col_logout:
    if st.button("Cerrar sesión"):
        st.session_state.usuario_id = None
        st.session_state.usuario_nombre = None
        st.rerun()

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
        monto = st.number_input("Monto ($)", min_value=0, step=100, format="%d", value=None)
        descripcion = st.text_input("Descripción (opcional)")
        metodo_pago = st.radio("Método de pago", ["Efectivo", "Tarjeta"])

        enviado = st.form_submit_button("Guardar gasto")
        if enviado:
            monto = monto or 0
            categoria_id = next(id_cat for id_cat, nombre in categorias if nombre == categoria_nombre)
            db.guardar_gasto(fecha, categoria_id, monto, descripcion, metodo_pago, usuario_id)
            st.success(f"¡Gasto de ${monto:.0f} en '{categoria_nombre}' guardado! ✅")

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
        recaudacion_reloj = st.number_input("Recaudación TOTAL del reloj ($)", min_value=0, step=100, format="%d", value=None)

        st.markdown("**Uber** (si hiciste viajes por Uber hoy)")
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            reloj_uber = st.number_input("Reloj - parte Uber ($)", min_value=0, step=100, format="%d", value=None)
        with col_u2:
            uber_pago = st.number_input("Uber me pagó ($)", min_value=0, step=100, format="%d", value=None)

        st.markdown("**Cabify** (si hiciste viajes por Cabify hoy)")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            reloj_cabify = st.number_input("Reloj - parte Cabify ($)", min_value=0, step=100, format="%d", value=None)
        with col_c2:
            cabify_pago = st.number_input("Cabify me pagó ($)", min_value=0, step=100, format="%d", value=None)

        st.markdown("**Gastos del día**")
        gasto_gnc = st.number_input("Gasto en GNC ($)", min_value=0, step=100, format="%d", value=None)
        gasto_nafta = st.number_input("Gasto en Nafta ($)", min_value=0, step=100, format="%d", value=None)

        enviado = st.form_submit_button("Guardar turno")
        if enviado:
            recaudacion_reloj = recaudacion_reloj or 0
            reloj_uber = reloj_uber or 0
            uber_pago = uber_pago or 0
            reloj_cabify = reloj_cabify or 0
            cabify_pago = cabify_pago or 0
            gasto_gnc = gasto_gnc or 0
            gasto_nafta = gasto_nafta or 0

            db.guardar_turno_diario(fecha, recaudacion_reloj, reloj_uber, uber_pago, reloj_cabify, cabify_pago, gasto_gnc, gasto_nafta, usuario_id)

            comision_uber = reloj_uber - uber_pago
            comision_cabify = reloj_cabify - cabify_pago
            recaudacion_real = recaudacion_reloj - comision_uber - comision_cabify - gasto_gnc - gasto_nafta

            st.success("¡Turno guardado! ✅")
            st.info(f"Comisión Uber: ${comision_uber:.0f} | Comisión Cabify: ${comision_cabify:.0f}")
            st.info(f"💰 Recaudación real del día (en mano/pendiente): ${recaudacion_real:.0f}")

# ---------------------------------------------------
with tab_cierre:
    st.header("Cargar el ticket mensual del reloj")

    with st.form("form_cierre", clear_on_submit=True):
        mes_anio = st.text_input("Mes (formato AAAA-MM, ej: 2026-06)")
        km_totales = st.number_input("KM Totales", min_value=0, step=1, value=None)
        km_ocupados = st.number_input("KM Ocupados", min_value=0, step=1, value=None)
        fichas_totales = st.number_input("Fichas Totales", min_value=0, step=1, value=None)
        cantidad_viajes = st.number_input("Cantidad de Viajes", min_value=0, step=1, value=None)

        enviado = st.form_submit_button("Guardar cierre")
        if enviado:
            km_totales = km_totales or 0
            km_ocupados = km_ocupados or 0
            fichas_totales = fichas_totales or 0
            cantidad_viajes = cantidad_viajes or 0

            db.guardar_cierre_mensual(mes_anio, km_totales, km_ocupados, fichas_totales, cantidad_viajes, usuario_id)
            st.success(f"¡Cierre de {mes_anio} guardado! ✅")

# ---------------------------------------------------
with tab_tablero:
    st.header("Tu tablero")

    gastos = db.obtener_gastos(usuario_id)
    turnos = db.obtener_turnos(usuario_id)
    cierres = db.obtener_cierres(usuario_id)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💰 Poder de ahorro")
        ingresos = turnos["recaudacion_reloj"].sum() if not turnos.empty else 0
        comision_uber_total = (turnos["reloj_uber"] - turnos["uber_pago"]).sum() if not turnos.empty else 0
        comision_cabify_total = (turnos["reloj_cabify"] - turnos["cabify_pago"]).sum() if not turnos.empty else 0
        gastos_turnos = (turnos["gasto_gnc"] + turnos["gasto_nafta"]).sum() if not turnos.empty else 0
        gastos_vida_total = gastos["monto"].sum() if not gastos.empty else 0

        ingresos_reales = ingresos - comision_uber_total - comision_cabify_total
        ahorro = ingresos_reales - gastos_turnos - gastos_vida_total

        st.metric("Recaudación reloj (bruta)", f"${ingresos:.0f}")
        st.metric("Comisión Uber + Cabify", f"${(comision_uber_total + comision_cabify_total):.0f}")
        st.metric("Ingresos reales", f"${ingresos_reales:.0f}")
        st.metric("Gastos totales (vida + GNC/Nafta)", f"${(gastos_vida_total + gastos_turnos):.0f}")
        st.metric("Poder de ahorro", f"${ahorro:.0f}")

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