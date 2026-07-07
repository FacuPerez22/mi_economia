import mysql.connector
import streamlit as st
import pandas as pd

def conectar():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        port=st.secrets["mysql"]["port"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],
        ssl_ca=st.secrets["mysql"]["ssl_ca"]
    )

# ---- GUARDAR ----

def guardar_gasto(fecha, categoria_id, monto, descripcion, metodo_pago):
    conexion = conectar()
    cursor = conexion.cursor()
    query = """
        INSERT INTO gastos_vida (fecha, categoria_id, monto, descripcion, metodo_pago)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (fecha, categoria_id, monto, descripcion, metodo_pago))
    conexion.commit()
    cursor.close()
    conexion.close()

def guardar_turno_diario(fecha, recaudacion_reloj, recaudacion_apps, gasto_gnc, gasto_nafta):
    conexion = conectar()
    cursor = conexion.cursor()
    query = """
        INSERT INTO turnos_diarios (fecha, recaudacion_reloj, recaudacion_apps, gasto_gnc, gasto_nafta)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (fecha, recaudacion_reloj, recaudacion_apps, gasto_gnc, gasto_nafta))
    conexion.commit()
    cursor.close()
    conexion.close()

def guardar_cierre_mensual(mes_anio, km_totales, km_ocupados, fichas_totales, cantidad_viajes):
    conexion = conectar()
    cursor = conexion.cursor()
    query = """
        INSERT INTO cierres_mensuales (mes_anio, km_totales_mes, km_ocupados_mes, fichas_totales, cantidad_viajes_mes)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (mes_anio, km_totales, km_ocupados, fichas_totales, cantidad_viajes))
    conexion.commit()
    cursor.close()
    conexion.close()

def agregar_categoria(nombre):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO categorias (nombre) VALUES (%s)", (nombre,))
    conexion.commit()
    cursor.close()
    conexion.close()

# ---- LEER ----

def obtener_categorias():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre FROM categorias ORDER BY nombre")
    filas = cursor.fetchall()
    cursor.close()
    conexion.close()
    return filas  # lista de tuplas (id, nombre)

def obtener_gastos():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT g.id, g.fecha, c.nombre AS categoria, g.monto, g.descripcion, g.metodo_pago
        FROM gastos_vida g
        JOIN categorias c ON g.categoria_id = c.id
        ORDER BY g.fecha DESC
    """)
    filas = cursor.fetchall()
    columnas = [col[0] for col in cursor.description]
    cursor.close()
    conexion.close()
    return pd.DataFrame(filas, columns=columnas)

def obtener_turnos():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM turnos_diarios ORDER BY fecha DESC")
    filas = cursor.fetchall()
    columnas = [col[0] for col in cursor.description]
    cursor.close()
    conexion.close()
    return pd.DataFrame(filas, columns=columnas)

def obtener_cierres():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM cierres_mensuales ORDER BY mes_anio DESC")
    filas = cursor.fetchall()
    columnas = [col[0] for col in cursor.description]
    cursor.close()
    conexion.close()
    return pd.DataFrame(filas, columns=columnas)