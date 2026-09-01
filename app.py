import streamlit as st
import datetime
import pandas as pd
import db

st.set_page_config(page_title="Mi Economía", layout="wide")

def formato_pesos(monto):
    return f"${monto:,.0f}".replace(",", ".")

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
# SISTEMA PRINCIPAL
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

tab_tablero, tab_gasto, tab_turno, tab_deposito, tab_ahorro, tab_cierre, tab_resumen = st.tabs([
    "📊 Tablero", "💸 Cargar Gasto", "🚗 Cargar Turno", "🏦 Depósito", "🐷 Ahorro", "📅 Cierre", "🗂️ Resumen"
])

# ---------------------------------------------------
with tab_gasto:
    st.header("Cargar un gasto")
    categorias = db.obtener_categorias()
    nombres_categorias = [nombre for id_cat, nombre, tipo in categorias]

    with st.form("form_gasto", clear_on_submit=True):
        fecha = st.date_input("Fecha", value=datetime.date.today())
        categoria_nombre = st.selectbox("Categoría", nombres_categorias)
        monto = st.number_input("Monto ($)", min_value=0, step=100, format="%d", value=None)
        descripcion = st.text_input("Descripción (opcional)")
        metodo_pago = st.radio("Método de pago", ["Efectivo", "Tarjeta"])

        if st.form_submit_button("Guardar gasto"):
            monto = monto or 0
            categoria_id = next(id_cat for id_cat, nombre, tipo in categorias if nombre == categoria_nombre)
            db.guardar_gasto(fecha, categoria_id, monto, descripcion, metodo_pago, usuario_id)
            st.success(f"¡Gasto de {formato_pesos(monto)} en '{categoria_nombre}' guardado! ✅")

    st.divider()
    st.subheader("¿Necesitás una categoría nueva?")
    with st.form("form_nueva_categoria", clear_on_submit=True):
        nueva_categoria = st.text_input("Nombre de la categoría")
        tipo_nueva_categoria = st.radio("¿Qué tipo de gasto es?", ["Personal (vida)", "Operativo (relacionado al auto)"])
        if st.form_submit_button("Agregar categoría") and nueva_categoria.strip() != "":
            tipo_valor = "operativo" if tipo_nueva_categoria.startswith("Operativo") else "personal"
            db.agregar_categoria(nueva_categoria.strip(), tipo_valor)
            st.success(f"Categoría '{nueva_categoria}' agregada.")
            st.rerun()

# ---------------------------------------------------
with tab_turno:
    st.header("Cargar el turno de hoy")
    with st.form("form_turno", clear_on_submit=True):
        fecha = st.date_input("Fecha", value=datetime.date.today())

        col_km1, col_km2 = st.columns(2)
        with col_km1:
            km_recorridos = st.number_input("KM totales", min_value=0.0, step=1.0, value=None)
        with col_km2:
            km_ocupados = st.number_input("KM ocupados", min_value=0.0, step=1.0, value=None)

        st.markdown("**Viajes de calle**")
        col_cal1, col_cal2 = st.columns(2)
        with col_cal1:
            total_calle = st.number_input("Facturado reloj ($)", min_value=0, step=100, format="%d", value=None)
        with col_cal2:
            transferencia_calle = st.number_input("Transferencia ($)", min_value=0, step=100, format="%d", value=None)

        st.markdown("**Uber**")
        reloj_uber = st.number_input("Reloj Uber ($)", min_value=0, step=100, format="%d", value=None)
        uber_transferido = st.number_input("Uber pagó ($)", min_value=0, step=100, format="%d", value=None)
        with st.expander("Cobrado en efectivo Uber (raro)"):
            uber_efectivo = st.number_input("Efectivo Uber ($)", min_value=0, step=100, format="%d", value=None)

        st.markdown("**Cabify**")
        reloj_cabify = st.number_input("Reloj Cabify ($)", min_value=0, step=100, format="%d", value=None)
        cabify_transferido = st.number_input("Cabify pagó ($)", min_value=0, step=100, format="%d", value=None)
        with st.expander("Cobrado en efectivo Cabify (raro)"):
            cabify_efectivo = st.number_input("Efectivo Cabify ($)", min_value=0, step=100, format="%d", value=None)

        st.markdown("**Gastos del dia**")
        gasto_gnc = st.number_input("Gasto GNC ($)", min_value=0, step=100, format="%d", value=None)
        gasto_nafta = st.number_input("Gasto Nafta ($)", min_value=0, step=100, format="%d", value=None)
        gasto_comida_laboral = st.number_input("Comida laboral ($)", min_value=0, step=100, format="%d", value=None)

        if st.form_submit_button("Guardar turno"):
            total_calle = total_calle or 0
            transferencia_calle = transferencia_calle or 0
            if transferencia_calle > total_calle:
                st.error("Error: La transferencia no puede ser mayor al total.")
                st.stop()

            db.guardar_turno_diario(
                fecha, total_calle + (reloj_uber or 0) + (reloj_cabify or 0), km_recorridos or 0, km_ocupados or 0,
                total_calle - transferencia_calle, transferencia_calle,
                reloj_uber or 0, uber_transferido or 0, uber_efectivo or 0,
                reloj_cabify or 0, cabify_transferido or 0, cabify_efectivo or 0,
                0, gasto_gnc or 0, gasto_nafta or 0, gasto_comida_laboral or 0, usuario_id
            )
            st.success("Turno guardado correctamente.")

# ---------------------------------------------------
with tab_deposito:
    st.header("Depositar efectivo al banco")
    with st.form("form_deposito", clear_on_submit=True):
        fecha_dep = st.date_input("Fecha", value=datetime.date.today())
        monto_dep = st.number_input("Monto ($)", min_value=0, step=100, format="%d", value=None)
        descripcion_dep = st.text_input("Descripción")
        if st.form_submit_button("Guardar depósito") and (monto_dep or 0) > 0:
            db.guardar_deposito(fecha_dep, monto_dep, descripcion_dep, usuario_id)
            st.success(f"Depósito de {formato_pesos(monto_dep)} guardado.")

    st.divider()
    st.subheader("🧮 Ajuste de caja")
    with st.form("form_ajuste", clear_on_submit=True):
        fecha_ajuste = st.date_input("Fecha", value=datetime.date.today())
        cuenta_ajuste = st.radio("Cuenta", ["Efectivo", "Banco"])
        tipo_ajuste = st.radio("Operación", ["Sumar", "Restar"])
        monto_ajuste = st.number_input("Monto ($)", min_value=0, step=100, format="%d", value=None)
        motivo_ajuste = st.text_input("Motivo")
        if st.form_submit_button("Guardar ajuste") and (monto_ajuste or 0) > 0:
            monto_final = monto_ajuste if tipo_ajuste == "Sumar" else -monto_ajuste
            db.guardar_ajuste(fecha_ajuste, "efectivo" if cuenta_ajuste == "Efectivo" else "banco", monto_final, motivo_ajuste, usuario_id)
            st.success("Ajuste guardado.")

# ---------------------------------------------------
with tab_ahorro:
    st.header("🐷 Registrar fondo de ahorro")
    st.caption("Esta plata se descontará de tu disponible diario y pasará a tu historial de ahorros intocables.")
    
    with st.form("form_ahorro", clear_on_submit=True):
        fecha_ahorro = st.date_input("Fecha", value=datetime.date.today())
        origen_ahorro = st.radio("¿De dónde sacaste esta plata?", ["Banco", "Efectivo"])
        monto_ahorro = st.number_input("Monto a guardar ($)", min_value=0, step=1000, format="%d", value=None)
        motivo_ahorro = st.text_input("Objetivo o nota (ej: Ahorro Septiembre)")
        
        if st.form_submit_button("Guardar Ahorro"):
            if (monto_ahorro or 0) > 0:
                db.guardar_ahorro(fecha_ahorro, monto_ahorro, origen_ahorro, motivo_ahorro, usuario_id)
                st.success(f"¡Excelente! Separaste {formato_pesos(monto_ahorro)} para tu fondo.")
                st.balloons()
            else:
                st.warning("Ingresá un monto mayor a 0.")

    st.divider()
    st.subheader("📚 Historial de Ahorros")
    ahorros_df = db.obtener_ahorros(usuario_id)
    st.dataframe(ahorros_df, use_container_width=True)

# ---------------------------------------------------
with tab_cierre:
    st.header("Cargar el ticket mensual del reloj")
    with st.form("form_cierre", clear_on_submit=True):
        mes_anio = st.text_input("Mes (AAAA-MM)")
        km_totales = st.number_input("KM Totales", min_value=0, step=1, value=None)
        km_ocupados = st.number_input("KM Ocupados", min_value=0, step=1, value=None)
        fichas_totales = st.number_input("Fichas Totales", min_value=0, step=1, value=None)
        cantidad_viajes = st.number_input("Cantidad Viajes", min_value=0, step=1, value=None)
        if st.form_submit_button("Guardar cierre"):
            db.guardar_cierre_mensual(mes_anio, km_totales or 0, km_ocupados or 0, fichas_totales or 0, cantidad_viajes or 0, usuario_id)
            st.success("Cierre guardado.")

# ---------------------------------------------------
with tab_tablero:
    st.header("Tu tablero")

    gastos = db.obtener_gastos(usuario_id)
    turnos = db.obtener_turnos(usuario_id)
    cierres = db.obtener_cierres(usuario_id)
    saldo = db.obtener_saldo_inicial(usuario_id)
    depositos = db.obtener_depositos(usuario_id)
    ajustes = db.obtener_ajustes(usuario_id)
    ahorros = db.obtener_ahorros(usuario_id)

    with st.expander("⚙️ Configurar saldo inicial"):
        with st.form("form_saldo_inicial"):
            fecha_inicio = st.date_input("Fecha de arranque", value=saldo["fecha_inicio"] if saldo else datetime.date.today())
            col_si1, col_si2 = st.columns(2)
            with col_si1:
                efectivo_inicial = st.number_input("Efectivo real inicial", min_value=0, value=int(saldo["efectivo_inicial"]) if saldo else 0)
            with col_si2:
                banco_inicial = st.number_input("Banco real inicial", min_value=0, value=int(saldo["banco_inicial"]) if saldo else 0)
            if st.form_submit_button("Guardar"):
                db.guardar_saldo_inicial(usuario_id, fecha_inicio, efectivo_inicial, banco_inicial)
                st.rerun()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💰 Estado de Caja")
        
        for df in [turnos, gastos, depositos, ajustes, ahorros]:
            if not df.empty: df["fecha"] = pd.to_datetime(df["fecha"]).dt.date

        if saldo:
            fd = saldo["fecha_inicio"]
            turnos_p = turnos[turnos["fecha"] >= fd] if not turnos.empty else turnos
            gastos_p = gastos[gastos["fecha"] >= fd] if not gastos.empty else gastos
            depos_p = depositos[depositos["fecha"] >= fd] if not depositos.empty else depositos
            ajustes_p = ajustes[ajustes["fecha"] >= fd] if not ajustes.empty else ajustes
            ahorros_p = ahorros[ahorros["fecha"] >= fd] if not ahorros.empty else ahorros
        else:
            turnos_p, gastos_p, depos_p, ajustes_p, ahorros_p = turnos, gastos, depositos, ajustes, ahorros

        # Cálculos de ingresos y egresos diarios
        ef_in = (turnos_p["efectivo_calle"] + turnos_p["uber_efectivo"] + turnos_p["cabify_efectivo"]).sum() if not turnos_p.empty else 0
        bn_in = (turnos_p["transferencia_calle"] + turnos_p["uber_transferido"] + turnos_p["cabify_transferido"]).sum() if not turnos_p.empty else 0
        gast_t = (turnos_p["gasto_gnc"] + turnos_p["gasto_nafta"] + turnos_p["gasto_comida_laboral"]).sum() if not turnos_p.empty else 0
        
        gast_ef = gastos_p.loc[gastos_p["metodo_pago"] == "Efectivo", "monto"].sum() if not gastos_p.empty else 0
        gast_bn = gastos_p.loc[gastos_p["metodo_pago"] == "Tarjeta", "monto"].sum() if not gastos_p.empty else 0
        
        dep = depos_p["monto"].sum() if not depos_p.empty else 0
        aj_ef = ajustes_p.loc[ajustes_p["cuenta"] == "efectivo", "monto"].sum() if not ajustes_p.empty else 0
        aj_bn = ajustes_p.loc[ajustes_p["cuenta"] == "banco", "monto"].sum() if not ajustes_p.empty else 0

        # Restar los ahorros del circulante
        ahorro_ef = ahorros_p.loc[ahorros_p["origen"] == "Efectivo", "monto"].sum() if not ahorros_p.empty else 0
        ahorro_bn = ahorros_p.loc[ahorros_p["origen"] == "Banco", "monto"].sum() if not ahorros_p.empty else 0
        ahorro_total_hist = ahorros["monto"].sum() if not ahorros.empty else 0

        ef_real = (saldo["efectivo_inicial"] if saldo else 0) + ef_in - gast_t - gast_ef - dep + aj_ef - ahorro_ef
        bn_real = (saldo["banco_inicial"] if saldo else 0) + bn_in - gast_bn + dep + aj_bn - ahorro_bn

        st.metric("💵 Efectivo operativo", formato_pesos(ef_real))
        st.metric("🏦 Banco operativo", formato_pesos(bn_real))
        st.metric("Plata total circulante", formato_pesos(ef_real + bn_real))
        
        st.divider()
        st.subheader("🏆 Ahorro Consolidado")
        st.metric("Fondo Intocable", formato_pesos(ahorro_total_hist))

    with col2:
        st.subheader("🚗 Eficiencia")
        if not cierres.empty:
            ultimo = cierres.iloc[0]
            st.metric("Eficiencia mes reloj", f"{(ultimo['km_ocupados_mes'] / ultimo['km_totales_mes']) * 100:.1f}%")
        
        turnos_km = turnos_p[turnos_p["km_recorridos"] > 0] if not turnos_p.empty else turnos_p
        if turnos_km is not None and not turnos_km.empty:
            km_rec = turnos_km["km_recorridos"].sum()
            km_ocu = turnos_km["km_ocupados"].sum()
            ingresos_km = (turnos_km["efectivo_calle"] + turnos_km["transferencia_calle"] + turnos_km["uber_efectivo"] + turnos_km["uber_transferido"] + turnos_km["cabify_efectivo"] + turnos_km["cabify_transferido"]).sum()
            st.metric("Eficiencia diaria promedio", f"{(km_ocu / km_rec) * 100:.1f}%")
            st.metric("Ingreso por km", formato_pesos(ingresos_km / km_rec if km_rec > 0 else 0))

# ---------------------------------------------------
with tab_resumen:
    st.header("Resumen mensual")
    gastos_r = db.obtener_gastos(usuario_id)
    turnos_r = db.obtener_turnos(usuario_id)

    if not gastos_r.empty: gastos_r["fecha"] = pd.to_datetime(gastos_r["fecha"])
    if not turnos_r.empty: turnos_r["fecha"] = pd.to_datetime(turnos_r["fecha"])

    meses = sorted(set(
        (gastos_r["fecha"].dt.to_period("M").astype(str).tolist() if not gastos_r.empty else []) +
        (turnos_r["fecha"].dt.to_period("M").astype(str).tolist() if not turnos_r.empty else [])
    ), reverse=True)

    if meses:
        mes = st.selectbox("Elegí el mes", meses)
        g_m = gastos_r[gastos_r["fecha"].dt.to_period("M").astype(str) == mes] if not gastos_r.empty else gastos_r
        t_m = turnos_r[turnos_r["fecha"].dt.to_period("M").astype(str) == mes] if not turnos_r.empty else turnos_r

        gnc_m = t_m["gasto_gnc"].sum() if not t_m.empty else 0
        nafta_m = t_m["gasto_nafta"].sum() if not t_m.empty else 0
        comida_m = t_m["gasto_comida_laboral"].sum() if not t_m.empty else 0
        ub_c = ((t_m["reloj_uber"] - t_m["uber_efectivo"]) - t_m["uber_transferido"]).sum() if not t_m.empty else 0
        cb_c = ((t_m["reloj_cabify"] - t_m["cabify_efectivo"]) - t_m["cabify_transferido"]).sum() if not t_m.empty else 0

        st.subheader("⛽ Operativo del mes")
        with st.expander("Ver detalle", expanded=True):
            c1, c2, c3 = st.columns(3)
            c1.metric("GNC", formato_pesos(gnc_m))
            c2.metric("Nafta", formato_pesos(nafta_m))
            c3.metric("Comida", formato_pesos(comida_m))
            c4, c5 = st.columns(2)
            c4.metric("Comisión Uber", formato_pesos(ub_c))
            c5.metric("Comisión Cabify", formato_pesos(cb_c))

        op_ex = g_m.loc[g_m["tipo"] == "operativo", "monto"].sum() if not g_m.empty else 0
        pers = g_m.loc[g_m["tipo"] == "personal", "monto"].sum() if not g_m.empty else 0

        st.divider()
        st.subheader("Totales")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total operativo", formato_pesos(gnc_m + nafta_m + comida_m + op_ex))
        c2.metric("Total personal", formato_pesos(pers))
        c3.metric("Total general", formato_pesos(gnc_m + nafta_m + comida_m + op_ex + pers))