import streamlit as st
import datetime
import pandas as pd
import db

st.set_page_config(page_title="Mi Economía", layout="wide")


def formato_pesos(monto):
    """Formatea un número como $ con punto de miles, ej: $1.234.567"""
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

tab_tablero, tab_gasto, tab_turno, tab_cierre, tab_resumen = st.tabs([
    "📊 Tablero", "💸 Cargar Gasto", "🚗 Cargar Turno", "📅 Cierre Mensual", "🗂️ Resumen Mensual"
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
            st.success(f"¡Gasto de {formato_pesos(monto)} en '{categoria_nombre}' guardado! ✅")

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

        st.markdown("**Kilometros del dia** (opcional, para medir eficiencia)")
        col_km1, col_km2 = st.columns(2)
        with col_km1:
            km_recorridos = st.number_input("KM totales recorridos hoy", min_value=0.0, step=1.0, value=None)
        with col_km2:
            km_ocupados = st.number_input("KM con pasajero (ocupado)", min_value=0.0, step=1.0, value=None)

        st.markdown("**Viajes de calle** (parados en la calle, no por app)")
        st.caption("Poné el total que marca el reloj y cuanto de eso fue transferencia. El efectivo se calcula solo, restando.")
        col_cal1, col_cal2 = st.columns(2)
        with col_cal1:
            total_calle = st.number_input("Total facturado (reloj) en viajes de calle ($)", min_value=0, step=100, format="%d", value=None)
        with col_cal2:
            transferencia_calle = st.number_input("De eso, cuanto fue transferencia ($)", min_value=0, step=100, format="%d", value=None)

        st.markdown("**Uber**")
        reloj_uber = st.number_input("Reloj - parte Uber ($)", min_value=0, step=100, format="%d", value=None)
        uber_transferido = st.number_input("Uber me pago ($)", min_value=0, step=100, format="%d", value=None)
        with st.expander("Te pagaron algo en efectivo por Uber hoy? (poco frecuente)"):
            uber_efectivo = st.number_input("Cobrado en efectivo por viajes Uber ($)", min_value=0, step=100, format="%d", value=None)

        st.markdown("**Cabify**")
        reloj_cabify = st.number_input("Reloj - parte Cabify ($)", min_value=0, step=100, format="%d", value=None)
        cabify_transferido = st.number_input("Cabify me pago ($)", min_value=0, step=100, format="%d", value=None)
        with st.expander("Te pagaron algo en efectivo por Cabify hoy? (poco frecuente)"):
            cabify_efectivo = st.number_input("Cobrado en efectivo por viajes Cabify ($)", min_value=0, step=100, format="%d", value=None)

        st.markdown("**Gastos fijos del dia**")
        gasto_gnc = st.number_input("Gasto en GNC ($)", min_value=0, step=100, format="%d", value=None)
        gasto_nafta = st.number_input("Gasto en Nafta ($)", min_value=0, step=100, format="%d", value=None)
        gasto_comida_laboral = st.number_input("Comida laboral ($)", min_value=0, step=100, format="%d", value=None)

        enviado = st.form_submit_button("Guardar turno")
        if enviado:
            total_calle = total_calle or 0
            km_recorridos = km_recorridos or 0
            km_ocupados = km_ocupados or 0
            transferencia_calle = transferencia_calle or 0
            reloj_uber = reloj_uber or 0
            uber_transferido = uber_transferido or 0
            uber_efectivo = uber_efectivo or 0
            reloj_cabify = reloj_cabify or 0
            cabify_transferido = cabify_transferido or 0
            cabify_efectivo = cabify_efectivo or 0
            gasto_gnc = gasto_gnc or 0
            gasto_nafta = gasto_nafta or 0
            gasto_comida_laboral = gasto_comida_laboral or 0
            efectivo_contado_real = 0

            if transferencia_calle > total_calle:
                st.error(
                    f"La transferencia (${transferencia_calle:,.0f}) es mayor que el total facturado "
                    f"(${total_calle:,.0f}). Revisa esos dos numeros, no se guardo el turno."
                )
                st.stop()

            efectivo_calle = total_calle - transferencia_calle
            recaudacion_reloj = total_calle + reloj_uber + reloj_cabify

            db.guardar_turno_diario(
                fecha, recaudacion_reloj, km_recorridos, km_ocupados,
                efectivo_calle, transferencia_calle,
                reloj_uber, uber_transferido, uber_efectivo,
                reloj_cabify, cabify_transferido, cabify_efectivo,
                efectivo_contado_real,
                gasto_gnc, gasto_nafta, gasto_comida_laboral,
                usuario_id
            )

            comision_uber = (reloj_uber - uber_efectivo) - uber_transferido
            comision_cabify = (reloj_cabify - cabify_efectivo) - cabify_transferido

            efectivo_del_dia = efectivo_calle + uber_efectivo + cabify_efectivo
            transferencia_del_dia = transferencia_calle + uber_transferido + cabify_transferido
            gastos_del_dia = gasto_gnc + gasto_nafta + gasto_comida_laboral
            neto_del_dia = efectivo_del_dia + transferencia_del_dia - gastos_del_dia

            st.success("Turno guardado!")
            st.info(f"Efectivo de calle calculado: {formato_pesos(efectivo_calle)} (de ${total_calle:,.0f} facturados)".replace(",", "."))
            st.info(f"Efectivo del dia: {formato_pesos(efectivo_del_dia)} | Transferencias del dia: {formato_pesos(transferencia_del_dia)}")
            if reloj_uber > 0:
                st.info(f"Comision Uber del dia: {formato_pesos(comision_uber)}")
            if reloj_cabify > 0:
                st.info(f"Comision Cabify del dia: {formato_pesos(comision_cabify)}")
            st.info(f"Neto real del dia (efectivo + transferencias - gastos): {formato_pesos(neto_del_dia)}")

            if km_recorridos > 0:
                eficiencia_dia = (km_ocupados / km_recorridos) * 100
                ingreso_por_km = neto_del_dia / km_recorridos if km_recorridos > 0 else 0
                st.info(f"Eficiencia del dia: {eficiencia_dia:.1f}% ocupado | {formato_pesos(ingreso_por_km)} por km recorrido")

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
    saldo = db.obtener_saldo_inicial(usuario_id)

    with st.expander("⚙️ Configurar saldo inicial (arrancar de cero con la plata real)"):
        st.caption(
            "Cargá acá cuánta plata tenés realmente HOY en el bolsillo y en el banco/MercadoPago. "
            "A partir de esa fecha, el tablero va a sumar lo que entra y restar lo que sale — "
            "sin arrastrar los datos viejos que puedan estar mal cargados."
        )
        with st.form("form_saldo_inicial"):
            fecha_inicio = st.date_input(
                "Fecha de arranque",
                value=saldo["fecha_inicio"] if saldo else datetime.date.today()
            )
            col_si1, col_si2 = st.columns(2)
            with col_si1:
                efectivo_inicial = st.number_input(
                    "Efectivo real que tenés hoy ($)", min_value=0, step=100, format="%d",
                    value=int(saldo["efectivo_inicial"]) if saldo else 0
                )
            with col_si2:
                banco_inicial = st.number_input(
                    "Banco/MercadoPago real que tenés hoy ($)", min_value=0, step=100, format="%d",
                    value=int(saldo["banco_inicial"]) if saldo else 0
                )
            guardar_saldo = st.form_submit_button("Guardar saldo inicial")
            if guardar_saldo:
                db.guardar_saldo_inicial(usuario_id, fecha_inicio, efectivo_inicial, banco_inicial)
                st.success("¡Saldo inicial guardado! Recargá la página para verlo reflejado. ✅")
                st.rerun()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💰 Poder de ahorro (real)")

        if not turnos.empty:
            turnos["fecha"] = pd.to_datetime(turnos["fecha"]).dt.date
        if not gastos.empty:
            gastos["fecha"] = pd.to_datetime(gastos["fecha"]).dt.date

        if saldo:
            fecha_desde = saldo["fecha_inicio"]
            turnos_periodo = turnos[turnos["fecha"] >= fecha_desde] if not turnos.empty else turnos
            gastos_periodo = gastos[gastos["fecha"] >= fecha_desde] if not gastos.empty else gastos
        else:
            fecha_desde = None
            turnos_periodo = turnos
            gastos_periodo = gastos

        if not turnos_periodo.empty:
            efectivo_movimiento = (turnos_periodo["efectivo_calle"] + turnos_periodo["uber_efectivo"] + turnos_periodo["cabify_efectivo"]).sum()
            transferencia_movimiento = (turnos_periodo["transferencia_calle"] + turnos_periodo["uber_transferido"] + turnos_periodo["cabify_transferido"]).sum()
            recaudacion_bruta = turnos_periodo["recaudacion_reloj"].sum()
            gastos_turnos = (turnos_periodo["gasto_gnc"] + turnos_periodo["gasto_nafta"] + turnos_periodo["gasto_comida_laboral"]).sum()
            comision_uber_total = ((turnos_periodo["reloj_uber"] - turnos_periodo["uber_efectivo"]) - turnos_periodo["uber_transferido"]).sum()
            comision_cabify_total = ((turnos_periodo["reloj_cabify"] - turnos_periodo["cabify_efectivo"]) - turnos_periodo["cabify_transferido"]).sum()
        else:
            efectivo_movimiento = transferencia_movimiento = recaudacion_bruta = gastos_turnos = 0
            comision_uber_total = comision_cabify_total = 0

        if not gastos_periodo.empty:
            gastos_vida_efectivo = gastos_periodo.loc[gastos_periodo["metodo_pago"] == "Efectivo", "monto"].sum()
            gastos_vida_tarjeta = gastos_periodo.loc[gastos_periodo["metodo_pago"] == "Tarjeta", "monto"].sum()
        else:
            gastos_vida_efectivo = gastos_vida_tarjeta = 0

        gastos_vida_total = gastos_vida_efectivo + gastos_vida_tarjeta

        efectivo_actual = (saldo["efectivo_inicial"] if saldo else 0) + efectivo_movimiento - gastos_turnos - gastos_vida_efectivo
        banco_actual = (saldo["banco_inicial"] if saldo else 0) + transferencia_movimiento - gastos_vida_tarjeta
        ahorro = efectivo_actual + banco_actual

        if saldo:
            st.caption(f"📌 Calculado desde el {fecha_desde.strftime('%d/%m/%Y')} (tu saldo inicial)")
        else:
            st.caption("📌 Todavía no configuraste un saldo inicial — está sumando TODO tu historial cargado. Te recomendamos configurarlo arriba ⚙️")

        st.metric("💵 Efectivo real (tu bolsillo)", formato_pesos(efectivo_actual))
        st.metric("🏦 Banco/MercadoPago real", formato_pesos(banco_actual))
        st.metric("Poder de ahorro total", formato_pesos(ahorro))
        st.divider()
        st.metric("Recaudación reloj (bruta, informativo)", formato_pesos(recaudacion_bruta))
        st.metric("🟢 Comisión Uber acumulada", formato_pesos(comision_uber_total))
        st.metric("🟣 Comisión Cabify acumulada", formato_pesos(comision_cabify_total))
        st.metric("Gastos totales del período", formato_pesos(gastos_vida_total + gastos_turnos))

        if not turnos.empty and turnos.iloc[0]["efectivo_contado_real"] > 0:
            ultimo_turno = turnos.iloc[0]
            efectivo_esperado_ultimo = (
                ultimo_turno["efectivo_calle"] + ultimo_turno["uber_efectivo"] + ultimo_turno["cabify_efectivo"]
                - ultimo_turno["gasto_gnc"] - ultimo_turno["gasto_nafta"] - ultimo_turno["gasto_comida_laboral"]
            )
            diferencia_ultimo = ultimo_turno["efectivo_contado_real"] - efectivo_esperado_ultimo
            st.caption(f"🔎 Arqueo último turno ({ultimo_turno['fecha']}): diferencia de {formato_pesos(diferencia_ultimo)}")

    with col2:
        st.subheader("🚗 Eficiencia del auto")
        if not cierres.empty:
            ultimo = cierres.iloc[0]
            eficiencia = (ultimo["km_ocupados_mes"] / ultimo["km_totales_mes"]) * 100
            st.metric(f"Eficiencia ({ultimo['mes_anio']}) — ticket oficial", f"{eficiencia:.1f}%")
            st.metric("KM Totales (ticket)", f"{ultimo['km_totales_mes']:,}".replace(",", "."))
            st.metric("KM Ocupados (ticket)", f"{ultimo['km_ocupados_mes']:,}".replace(",", "."))
        else:
            st.info("Todavía no cargaste ningún cierre mensual (ticket del reloj).")

        st.divider()
        st.caption("📍 Basado en lo que cargaste día a día en 'Cargar Turno'")
        turnos_con_km = turnos_periodo[turnos_periodo["km_recorridos"] > 0] if not turnos_periodo.empty else turnos_periodo
        if turnos_con_km is not None and not turnos_con_km.empty:
            km_recorridos_total = turnos_con_km["km_recorridos"].sum()
            km_ocupados_total = turnos_con_km["km_ocupados"].sum()
            eficiencia_diaria = (km_ocupados_total / km_recorridos_total) * 100
            ingreso_periodo_con_km = (
                turnos_con_km["efectivo_calle"] + turnos_con_km["transferencia_calle"]
                + turnos_con_km["uber_efectivo"] + turnos_con_km["uber_transferido"]
                + turnos_con_km["cabify_efectivo"] + turnos_con_km["cabify_transferido"]
            ).sum()
            ingreso_por_km = ingreso_periodo_con_km / km_recorridos_total if km_recorridos_total > 0 else 0
            st.metric("Eficiencia diaria promedio", f"{eficiencia_diaria:.1f}%")
            st.metric("Ingreso por km recorrido", formato_pesos(ingreso_por_km))
        else:
            st.info("Todavía no cargaste kilómetros en tus turnos diarios.")

    st.divider()

    st.subheader("📋 Últimos gastos cargados")
    st.dataframe(gastos, use_container_width=True)

    st.subheader("📋 Últimos turnos cargados")
    st.dataframe(turnos, use_container_width=True)

# ---------------------------------------------------
with tab_resumen:
    st.header("Resumen mensual de gastos")

    gastos_r = db.obtener_gastos(usuario_id)
    turnos_r = db.obtener_turnos(usuario_id)

    if not gastos_r.empty:
        gastos_r["fecha"] = pd.to_datetime(gastos_r["fecha"])
    if not turnos_r.empty:
        turnos_r["fecha"] = pd.to_datetime(turnos_r["fecha"])

    meses_disponibles = sorted(set(
        (gastos_r["fecha"].dt.to_period("M").astype(str).tolist() if not gastos_r.empty else [])
        + (turnos_r["fecha"].dt.to_period("M").astype(str).tolist() if not turnos_r.empty else [])
    ), reverse=True)

    if not meses_disponibles:
        st.info("Todavía no hay datos cargados para armar un resumen.")
    else:
        mes_elegido = st.selectbox("Elegí el mes", meses_disponibles)

        gastos_mes = gastos_r[gastos_r["fecha"].dt.to_period("M").astype(str) == mes_elegido] if not gastos_r.empty else gastos_r
        turnos_mes = turnos_r[turnos_r["fecha"].dt.to_period("M").astype(str) == mes_elegido] if not turnos_r.empty else turnos_r

        st.subheader("⛽ Gastos operativos del mes (turnos)")
        col_op1, col_op2, col_op3 = st.columns(3)
        total_gnc_mes = turnos_mes["gasto_gnc"].sum() if not turnos_mes.empty else 0
        total_nafta_mes = turnos_mes["gasto_nafta"].sum() if not turnos_mes.empty else 0
        total_comida_mes = turnos_mes["gasto_comida_laboral"].sum() if not turnos_mes.empty else 0
        col_op1.metric("GNC", formato_pesos(total_gnc_mes))
        col_op2.metric("Nafta", formato_pesos(total_nafta_mes))
        col_op3.metric("Comida laboral", formato_pesos(total_comida_mes))

        st.divider()

        st.subheader("🧾 Gastos personales del mes por categoría")
        if not gastos_mes.empty:
            resumen_categorias = (
                gastos_mes.groupby("categoria")["monto"]
                .agg(total="sum", cantidad="count")
                .sort_values("total", ascending=False)
            )
            st.dataframe(resumen_categorias, use_container_width=True)
            st.bar_chart(resumen_categorias["total"])
            st.metric("Total gastos personales del mes", formato_pesos(gastos_mes["monto"].sum()))
        else:
            st.info("No hay gastos personales cargados en este mes.")

        st.divider()
        total_mes = total_gnc_mes + total_nafta_mes + total_comida_mes + (gastos_mes["monto"].sum() if not gastos_mes.empty else 0)
        st.metric("💸 Total general de gastos del mes", formato_pesos(total_mes))

        st.divider()
        st.subheader("🔒 Cerrar este mes")
        st.caption(
            "Guarda una foto de este mes (ingresos, gastos, resultado neto y km) para consultar más adelante. "
            "No resetea tu saldo — la plata sigue acumulándose normalmente."
        )

        ingreso_efectivo_mes = (turnos_mes["efectivo_calle"] + turnos_mes["uber_efectivo"] + turnos_mes["cabify_efectivo"]).sum() if not turnos_mes.empty else 0
        ingreso_transferencia_mes = (turnos_mes["transferencia_calle"] + turnos_mes["uber_transferido"] + turnos_mes["cabify_transferido"]).sum() if not turnos_mes.empty else 0
        gastos_operativos_mes = total_gnc_mes + total_nafta_mes + total_comida_mes
        gastos_personales_mes = gastos_mes["monto"].sum() if not gastos_mes.empty else 0
        resultado_neto_mes = ingreso_efectivo_mes + ingreso_transferencia_mes - gastos_operativos_mes - gastos_personales_mes
        km_recorridos_mes_total = turnos_mes["km_recorridos"].sum() if not turnos_mes.empty else 0
        km_ocupados_mes_total = turnos_mes["km_ocupados"].sum() if not turnos_mes.empty else 0

        col_cierre1, col_cierre2 = st.columns(2)
        col_cierre1.metric("Ingreso del mes (efectivo + transferencia)", formato_pesos(ingreso_efectivo_mes + ingreso_transferencia_mes))
        col_cierre2.metric("Resultado neto del mes", formato_pesos(resultado_neto_mes))

        if st.button(f"🔒 Cerrar {mes_elegido}"):
            db.guardar_cierre_financiero(
                usuario_id, mes_elegido,
                ingreso_efectivo_mes, ingreso_transferencia_mes,
                gastos_operativos_mes, gastos_personales_mes, resultado_neto_mes,
                km_recorridos_mes_total, km_ocupados_mes_total
            )
            st.success(f"¡{mes_elegido} cerrado y guardado! ✅")
            st.rerun()

        cierres_financieros = db.obtener_cierres_financieros(usuario_id)
        if not cierres_financieros.empty:
            st.divider()
            st.subheader("📚 Historial de meses cerrados")
            st.dataframe(cierres_financieros, use_container_width=True)