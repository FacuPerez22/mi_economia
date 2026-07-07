import mysql.connector
import streamlit as st
import pandas as pd
import bcrypt

def conectar():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        port=st.secrets["mysql"]["port"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],
        ssl_ca=st.secrets["mysql"]["ssl_ca"]
    )

# ---- LOGIN ----

def verificar_login(nombre_usuario, password_ingresada):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id, password_hash FROM usuarios WHERE nombre_usuario = %s",
        (nombre_usuario,)
    )
    fila = cursor.fetchone()
    cursor.close()
    conexion.close()

    if fila is None:
        return None  # usuario no existe

    usuario_id, hash_guardado = fila
    if bcrypt.checkpw(password_ingresada.encode(), hash_guardado.encode()):
        return usuario_id  # login correcto
    else:
        return None  # contraseña incorrecta

# ---- GUARDAR ----

def guardar_gasto(fecha, categoria_id, monto, descripcion, metodo_pago, usuario_id):
    conexion = conectar()
    cursor = conexion.cursor()
    query = """
        INSERT INTO gastos_vida (fecha, categoria_id, monto, descripcion, metodo_pago, usuario_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (fecha, categoria_id, monto, descripcion, metodo_pago, usuario_id))
    conexion.commit()
    cursor.close()
    conexion.close()

def guardar_turno_diario(fecha, recaudacion_reloj, recaudacion_apps, gasto_gnc, gasto_nafta, usuario_id):
    conexion = conectar()
    cursor = conexion.cursor()
    query = """
        INSERT INTO turnos_diarios (fecha, recaudacion_reloj, recaudacion_apps, gasto_gnc, gasto_nafta, usuario_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (fecha, recaudacion_reloj, recaudacion_apps, gasto_gnc, gasto_nafta, usuario_id))
    conexion.commit()
    cursor.close()
    conexion.close()

def guardar_cierre_mensual(mes_anio, km_totales, km_ocupados, fichas_totales, cantidad_viajes, usuario_id):
    conexion = conectar()
    cursor = conexion.cursor()
    query = """
        INSERT INTO cierres_mensuales (mes_anio, km_totales_mes, km_ocupados_mes, fichas_totales, cantidad_viajes_mes, usuario_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (mes_anio, km_totales, km_ocupados, fichas_totales, cantidad_viajes, usuario_id))
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
    return filas

def obtener_gastos(usuario_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT g.id, g.fecha, c.nombre AS categoria, g.monto, g.descripcion, g.metodo_pago
        FROM gastos_vida g
        JOIN categorias c ON g.categoria_id = c.id
        WHERE g.usuario_id = %s
        ORDER BY g.fecha DESC
    """, (usuario_id,))
    filas = cursor.fetchall()
    columnas = [col[0] for col in cursor.description]
    cursor.close()
    conexion.close()
    return pd.DataFrame(filas, columns=columnas)

def obtener_turnos(usuario_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM turnos_diarios WHERE usuario_id = %s ORDER BY fecha DESC", (usuario_id,))
    filas = cursor.fetchall()
    columnas = [col[0] for col in cursor.description]
    cursor.close()
    conexion.close()
    return pd.DataFrame(filas, columns=columnas)

def obtener_cierres(usuario_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM cierres_mensuales WHERE usuario_id = %s ORDER BY mes_anio DESC", (usuario_id,))
    filas = cursor.fetchall()
    columnas = [col[0] for col in cursor.description]
    cursor.close()
    conexion.close()
    return pd.DataFrame(filas, columns=columnas)