import streamlit as st
import psycopg
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# CONFIGURAÇÃO DO BANCO
# ==========================================

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# ==========================================
# CONEXÃO COM O BANCO
# ==========================================

def conectar_banco():
    return psycopg.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


# ==========================================
# CONFIGURAÇÃO DO STREAMLIT
# ==========================================

st.set_page_config(
    page_title="Site Monitoring",
    page_icon="🌐",
    layout="wide"
)


# ==========================================
# TÍTULO
# ==========================================

st.title("🌐 Site Monitoring")


# ==========================================
# CONECTAR AO BANCO
# ==========================================

conn = conectar_banco()


# ==========================================
# CONSULTAS
# ==========================================

with conn.cursor() as cur:

    # --------------------------------------
    # Total de alvos
    # --------------------------------------

    cur.execute("""
        SELECT COUNT(*)
        FROM alvos
    """)

    total_alvos = cur.fetchone()[0]


    # --------------------------------------
    # Sites normais
    # --------------------------------------

    cur.execute("""
        SELECT COUNT(*)
        FROM alvos
        WHERE tipo = 'normal'
    """)

    total_normal = cur.fetchone()[0]


    # --------------------------------------
    # Sites .onion
    # --------------------------------------

    cur.execute("""
        SELECT COUNT(*)
        FROM alvos
        WHERE tipo = 'onion'
    """)

    total_onion = cur.fetchone()[0]


    # --------------------------------------
    # Total de verificações
    # --------------------------------------

    cur.execute("""
        SELECT COUNT(*)
        FROM verificacoes
    """)

    total_verificacoes = cur.fetchone()[0]


    # --------------------------------------
    # ÚLTIMA VERIFICAÇÃO DE CADA SITE
    # --------------------------------------

    cur.execute("""
        SELECT
            a.url,
            a.tipo,
            v.status,
            v.checked_at
        FROM alvos a
        LEFT JOIN LATERAL (
            SELECT
                status,
                checked_at
            FROM verificacoes
            WHERE verificacoes.alvo_id = a.id
            ORDER BY checked_at DESC
            LIMIT 1
        ) v ON TRUE
        ORDER BY a.id
    """)

    resultados = cur.fetchall()


# ==========================================
# FECHAR CONEXÃO
# ==========================================

conn.close()


# ==========================================
# INDICADORES
# ==========================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Monitored Targets",
        total_alvos
    )


with col2:

    st.metric(
        "Sites surface",
        total_normal
    )


with col3:

    st.metric(
        ".onion Sites",
        total_onion
    )


with col4:

    st.metric(
        "Total Checks",
        total_verificacoes
    )


# ==========================================
# SEPARADOR
# ==========================================

st.divider()


# ==========================================
# DATAFRAME
# ==========================================

df = pd.DataFrame(
    resultados,
    columns=[
        "URL",
        "Tipo",
        "Status",
        "Data/Hora da verificação"
    ]
)


# ==========================================
# FILTROS
# ==========================================

st.subheader("Filtros")


col1, col2 = st.columns(2)


with col1:

    filtro_status = st.selectbox(
        "Status",
        [
            "Todos",
            "ONLINE",
            "OFFLINE"
        ]
    )


with col2:

    filtro_tipo = st.selectbox(
        "Tipo de site",
        [
            "Todos",
            "normal",
            "onion"
        ]
    )


# ==========================================
# APLICAR FILTRO DE STATUS
# ==========================================

if filtro_status != "Todos":

    df = df[
        df["Status"].str.upper() == filtro_status
    ]


# ==========================================
# APLICAR FILTRO DE TIPO
# ==========================================

if filtro_tipo != "Todos":

    df = df[
        df["Tipo"].str.lower() == filtro_tipo
    ]


# ==========================================
# RESULTADO DOS FILTROS
# ==========================================

st.write(
    f"**Sites encontrados: {len(df)}**"
)


# ==========================================
# COLORIR STATUS
# ==========================================

def colorir_status(valor):

    if str(valor).lower() == "online":

        return (
            "background-color: green; "
            "color: white; "
            "font-weight: bold;"
        )

    elif str(valor).lower() == "offline":

        return (
            "background-color: red; "
            "color: white; "
            "font-weight: bold;"
        )

    return ""


styled_df = df.style.map(
    colorir_status,
    subset=["Status"]
)


# ==========================================
# EXIBIR TABELA
# ==========================================

st.dataframe(
    styled_df,
    use_container_width=True,
    hide_index=True
)
