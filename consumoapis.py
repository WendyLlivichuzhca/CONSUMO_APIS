# ============================================
# 🌐 CONSUMO DE API + SQLITE + PANDAS + PLOTLY + STREAMLIT
# ============================================

import requests
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ============================
# 🎨 CONFIGURACIÓN DE LA APP
# ============================
st.set_page_config(page_title="Consumo de API con SQLite y Plotly", layout="wide")

st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #e3f2fd 0%, #e0f7fa 100%);
    font-family: 'Poppins', sans-serif;
    color: #333;
}
h1, h2 {
    color: #00796b;
}
</style>
""", unsafe_allow_html=True)


# ============================
# TÍTULO EN LA BARRA LATERAL
# ============================
st.sidebar.title("🧩 Consumo de API + SQLite + Pandas + Plotly")
# ============================
# 🗂 MENÚ LATERAL
# ============================
menu = st.sidebar.radio("📂 Menú", ["API", "SQLite", "Pandas", "Visualizaciones", "Exportación"])

# ============================
# 🔍 1️⃣ CONSUMO DE API
# ============================
API_URL = 'https://jsonplaceholder.typicode.com/users'
DB_NAME = 'usuarios3.db'



if menu == "API":
    st.header("Consumo de la API")
    st.write(f"Conectando a: `{API_URL}`")

    response = requests.get(API_URL, timeout=20)
    if response.status_code != 200:
        st.error(f"Error al consumir la API ({response.status_code})")
        st.stop()

    users = response.json()
    st.success(f"Se recibieron {len(users)} registros desde la API")
    st.dataframe(pd.DataFrame(users))

if menu == "SQLite":
    st.header("Guardar datos en SQLite")
    st.write(f"Conectando a la API: `{API_URL}`")

    # Botón para guardar datos manualmente
    if st.button("💾 Guardar datos en SQLite"):
        try:
            response = requests.get(API_URL, timeout=20)
            if response.status_code != 200:
                st.error(f"Error al consumir la API ({response.status_code})")
            else:
                users = response.json()
                conn = sqlite3.connect(DB_NAME)
                cur = conn.cursor()
                cur.execute('DROP TABLE IF EXISTS users;')
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        username TEXT,
                        email TEXT,
                        phone TEXT,
                        website TEXT
                    )
                ''')
                for u in users:
                    cur.execute('''
                        INSERT OR REPLACE INTO users (id, name, username, email, phone, website)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (u.get('id'), u.get('name'), u.get('username'), u.get('email'), u.get('phone'), u.get('website')))
                conn.commit()
                conn.close()
                st.success("✅ Datos guardados exitosamente en la base de datos SQLite")
        except Exception as e:
            st.error(f"❌ Ocurrió un error: {e}")


if menu == "Pandas":
    st.header("Lectura y procesamiento con Pandas")
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()
    st.dataframe(df)

    # Procesamiento
    df["name_length"] = df["name"].astype(str).apply(len)
    df["email_domain"] = df["email"].astype(str).apply(lambda x: x.split("@")[-1].lower() if "@" in str(x) else None)
    st.success("Procesamiento completado")

if menu == "Visualizaciones":
    st.header("Visualizaciones con Plotly")
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()
    df["name_length"] = df["name"].astype(str).apply(len)
    df["email_domain"] = df["email"].astype(str).apply(lambda x: x.split("@")[-1].lower() if "@" in str(x) else None)


    st.subheader("📊 Longitud de los nombres")
    fig1 = px.histogram(df, x="name_length", nbins=10, title="Distribución de caracteres en los nombres")
    fig1.update_layout(xaxis_title="Cantidad de caracteres", yaxis_title="Frecuencia")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("📈 Usuarios por dominio de email")
    dom_counts = df["email_domain"].value_counts().reset_index()
    dom_counts.columns = ["email_domain", "count"]
    fig2 = px.bar(dom_counts, x="count", y="email_domain", orientation="h", title="Usuarios por dominio de correo")
    fig2.update_layout(xaxis_title="Cantidad de usuarios", yaxis_title="Dominio")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("🥧 Distribución de dominios de email (Donut)")
    fig3 = px.pie(dom_counts, names="email_domain", values="count", hole=0.4)
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("📋 Tabla de usuarios")
    fig4 = go.Figure(data=[go.Table(
        header=dict(
            values=list(df[['id','name','username','email','phone','website']].columns),
            fill_color='lightgrey',
            align='left'
        ),
        cells=dict(
            values=[df[c] for c in ['id','name','username','email','phone','website']],
            align='left'
        )
    )])
    st.plotly_chart(fig4, use_container_width=True)

if menu == "Exportación":
    st.header("Exportación de gráficos")
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()
    df["name_length"] = df["name"].astype(str).apply(len)

    fig1 = px.histogram(df, x="name_length", nbins=10, title="Distribución de caracteres en los nombres")
    fig1.update_layout(xaxis_title="Cantidad de caracteres", yaxis_title="Frecuencia")

    if st.button("Exportar histograma a HTML"):
        fig1.write_html("hist_name_length.html", include_plotlyjs="cdn")
        st.success("Gráfico exportado como `hist_name_length.html`")

st.info("Proceso completado exitosamente.")
