# 🚕 Mi Economía — Control financiero para taxistas

Aplicación web para que un taxista lleve el control diario de sus ingresos, gastos y eficiencia de trabajo, reemplazando el cuaderno y la planilla de Excel que se usaban antes. Desarrollada como proyecto personal por **Facundo Pérez**, estudiante de la **Tecnicatura Superior en Desarrollo de Software (ISPC)**.

🔗 **App en producción:** https://mieconomia-facuperez.streamlit.app

---

## 📌 ¿Qué problema resuelve?

Un taxista que además trabaja con aplicaciones (Uber, Cabify) maneja varias fuentes de ingreso con reglas distintas:

- Viajes de calle, cobrados en **efectivo** o por **transferencia**.
- Viajes por app, donde la plataforma **transfiere el monto neto** (ya descontada su comisión) y, ocasionalmente, el pasajero paga en efectivo.
- Gastos operativos diarios (GNC, nafta, comida) que hay que diferenciar de los gastos personales.
- La necesidad de saber, en todo momento, **cuánta plata tiene realmente** en el bolsillo y en el banco — no solo cuánto facturó.

**Mi Economía** centraliza todo esto en un tablero simple, pensado para cargarse desde el celular entre viaje y viaje.

---

## ⚙️ Funcionalidades

### 📊 Tablero
- **Saldo real** separado en efectivo (bolsillo) y banco/MercadoPago, calculado a partir de un **saldo inicial configurable** — así el sistema no depende de que el historial completo esté cargado sin errores; simplemente se define "hoy tengo tanto" y de ahí en más el sistema va sumando y restando.
- Comisión de Uber y Cabify **calculada automáticamente** (reloj del viaje − lo que pagó la app).
- Indicadores de **eficiencia de trabajo**: porcentaje de kilómetros con pasajero vs. kilómetros libres, e ingreso promedio por kilómetro recorrido.
- **Arqueo de caja**: al cerrar el turno, el conductor puede contar el efectivo real que tiene y el sistema le muestra si coincide con lo calculado (y por cuánto difiere si no).

### 🚗 Cargar Turno
Formulario diario que separa cada fuente de ingreso (calle / Uber / Cabify) en efectivo vs. transferencia, registra los kilómetros recorridos y ocupados, y los gastos operativos del día (GNC, nafta, comida laboral).

### 💸 Cargar Gasto
Registro de gastos personales por categoría (con posibilidad de crear categorías nuevas), diferenciando método de pago (efectivo o tarjeta) — dato que se usa para saber de qué "pozo" (efectivo o banco) sale cada gasto.

### 🗂️ Resumen Mensual
- Desglose de gastos operativos (GNC/nafta/comida) y personales por categoría, con gráfico de barras.
- **Cierre de mes**: guarda una foto histórica (ingresos, gastos, resultado neto, kilómetros) sin resetear el saldo corriente, para poder comparar mes a mes.

### 📅 Cierre Mensual (ticket del reloj)
Carga del ticket oficial mensual del reloj del taxi (km totales, km ocupados, fichas, cantidad de viajes) como dato de referencia oficial.

### 🔐 Multi-usuario
Sistema de login con contraseñas hasheadas (bcrypt), pensado para que más de un conductor pueda usar la misma instancia de la app con sus propios datos aislados.

---

## 🛠️ Stack tecnológico

| Capa | Tecnología |
|---|---|
| Frontend / UI | [Streamlit](https://streamlit.io/) |
| Backend / lógica | Python 3 |
| Base de datos | MySQL (hosteada en Clever Cloud) |
| Autenticación | bcrypt (hash de contraseñas) |
| Manipulación de datos | pandas |
| Hosting | Streamlit Community Cloud |
| Control de versiones | Git / GitHub |

---

## 🏗️ Arquitectura

```
┌─────────────────┐        ┌──────────────┐        ┌───────────────┐
│   app.py         │        │   db.py      │        │   MySQL        │
│  (interfaz        │──────▶│  (capa de     │──────▶│  (Clever Cloud) │
│   Streamlit)       │        │   acceso a    │        │                │
│                    │◀──────│   datos)      │◀──────│                │
└─────────────────┘        └──────────────┘        └───────────────┘
```

Separación en capas: `app.py` concentra toda la interfaz y la lógica de presentación/cálculo; `db.py` es la única capa que habla con la base de datos (ningún SQL vive dentro de `app.py`), lo que facilita testear o reemplazar la base sin tocar la UI.

---

## 🗄️ Modelo de datos

| Tabla | Qué guarda |
|---|---|
| `usuarios` | Login (usuario + hash de contraseña) |
| `categorias` | Categorías de gastos personales, editable por el usuario |
| `gastos_vida` | Gastos personales (fecha, categoría, monto, método de pago) |
| `turnos_diarios` | Un registro por turno: ingresos por fuente (calle/Uber/Cabify) separados en efectivo/transferencia, comisiones de apps, km recorridos/ocupados, gastos operativos, arqueo de caja |
| `cierres_mensuales` | Ticket oficial mensual del reloj del taxi (km, fichas, viajes) |
| `saldo_inicial` | Punto de partida real (efectivo + banco) desde el cual se calcula el saldo actual |
| `cierres_financieros` | Fotos históricas de cada mes cerrado (ingresos, gastos, resultado neto, km) |

---

## 💡 Decisiones de diseño

Algunas decisiones que fueron cambiando a medida que el uso real de la app mostraba huecos en el modelo original:

- **Separar efectivo de transferencia en cada fuente de ingreso**, en vez de un solo campo "ingreso del día", para poder saber exactamente cuánta plata debería haber en el bolsillo vs. en el banco.
- **Calcular la comisión de Uber/Cabify en vez de pedirla como dato**, restando lo que pagó la app al monto del reloj — reduce la carga de datos y evita errores manuales.
- **Saldo inicial en vez de arrastrar todo el historial**: si el historial tiene errores de carga viejos, en vez de intentar corregir cada registro pasado, se define un punto de partida real y confiable a partir del cual el sistema empieza a calcular.
- **Arqueo de caja**: comparar lo calculado por el sistema contra lo que el usuario cuenta físicamente, para detectar errores de carga temprano en vez de descubrirlos semanas después.
- **Migraciones SQL idempotentes**: los scripts de migración de base de datos chequean si un cambio ya fue aplicado antes de aplicarlo, para poder re-ejecutarlos sin miedo a romper la base.

---

## 🚀 Cómo correrlo localmente

```bash
git clone <url-del-repo>
cd mi-economia
pip install streamlit mysql-connector-python pandas bcrypt
```

Crear `.streamlit/secrets.toml`:

```toml
[mysql]
host = "tu-host-mysql"
port = 3306
user = "tu-usuario"
password = "tu-password"
database = "tu-base"
ssl_ca = "ruta/al/certificado.pem"
```

Correr la app:

```bash
streamlit run app.py
```

---

## 📈 Próximos pasos

- Gráfico de tendencia de eficiencia diaria (% ocupado a lo largo del tiempo) para identificar zonas u horarios más rentables.
- Exportar el cierre mensual a PDF/Excel.
- Notificaciones o alertas cuando el arqueo de caja no coincide.

---

## 👤 Autor

**Facundo Pérez** — Estudiante de Tecnicatura Superior en Desarrollo de Software, ISPC (Córdoba, Argentina). Proyecto personal desarrollado a partir de una necesidad real de su trabajo como taxista.
