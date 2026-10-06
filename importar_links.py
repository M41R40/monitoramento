import psycopg
import os
from dotenv import load_dotenv

load_dotenv()


# ==========================================
# CONFIGURAÇÃO
# ==========================================

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

ARQUIVO_LINKS = "links.txt"


# ==========================================
# CONEXÃO
# ==========================================

conn = psycopg.connect(
    host=DB_HOST,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)


# ==========================================
# LER LINKS
# ==========================================

with open(ARQUIVO_LINKS, "r", encoding="utf-8") as arquivo:

    links = []

    for linha in arquivo:

        url = linha.strip()

        # Ignorar linhas vazias
        if not url:
            continue

        # Ignorar comentários
        if url.startswith("#"):
            continue

        # Adicionar https caso não tenha protocolo
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        links.append(url)


# ==========================================
# INSERIR NOVOS LINKS
# ==========================================

novos = 0
existentes = 0

with conn.cursor() as cur:

    for url in links:

        # Identificar tipo
        if ".onion" in url.lower():
            tipo = "onion"
        else:
            tipo = "normal"

        cur.execute("""
            SELECT id
            FROM alvos
            WHERE url = %s
        """, (url,))

        existe = cur.fetchone()

        if existe:

            existentes += 1

        else:

            cur.execute("""
                INSERT INTO alvos (url, tipo)
                VALUES (%s, %s)
            """, (url, tipo))

            novos += 1


# ==========================================
# SALVAR
# ==========================================

conn.commit()
conn.close()


# ==========================================
# RESULTADO
# ==========================================

print()
print("===== SINCRONIZAÇÃO =====")
print(f"Links encontrados no arquivo: {len(links)}")
print(f"Novos links adicionados:      {novos}")
print(f"Links já existentes:          {existentes}")
print("==========================")
