import psycopg
import time

from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException
import os
from dotenv import load_dotenv

load_dotenv()

# =========================
# CONFIGURAÇÕES
# =========================

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
FIREFOX_BIN = "/snap/firefox/current/usr/lib/firefox/firefox"
GECKODRIVER = "/usr/local/bin/geckodriver"

PAGE_TIMEOUT = 45 
TOR_PAGE_TIMEOUT = 90


# =========================
# BANCO DE DADOS
# =========================

def conectar_banco():
    return psycopg.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def buscar_alvos(conn, tipo):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, url
            FROM public.alvos
            WHERE tipo = %s
            ORDER BY id
        """, (tipo,))

        return cur.fetchall()


def salvar_verificacao(conn, alvo_id, resultado):

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO public.verificacoes
            (
                alvo_id,
                url,
                status,
                final_url,
                title,
                erro,
                ms,
                checked_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            alvo_id,
            resultado["url"],
            resultado["status"],
            resultado["final_url"],
            resultado["title"],
            resultado["erro"],
            resultado["ms"],
            resultado["checked_at"]
        ))

    conn.commit()


# =========================
# SELENIUM
# =========================

def new_driver(headless=True, tor=False):

    opts = Options()

    opts.binary_location = FIREFOX_BIN

    if headless:
        opts.add_argument("--headless")

    opts.page_load_strategy = "eager"

    if tor:

        opts.set_preference(
            "network.proxy.type",
            1
        )

        opts.set_preference(
            "network.proxy.socks",
            "127.0.0.1"
        )

        opts.set_preference(
            "network.proxy.socks_port",
            9050
        )

        opts.set_preference(
            "network.proxy.socks_version",
            5
        )

        opts.set_preference(
            "network.proxy.socks_remote_dns",
            True
        )

        opts.set_preference(
            "network.proxy.no_proxies_on",
            ""
        )

        opts.set_preference(
            "network.dns.blockDotOnion",
            False
        )

        opts.set_preference(
            "javascript.enabled",
            False
        )

        opts.set_preference(
            "network.prefetch-next",
            False
        )

        opts.set_preference(
            "network.dns.disablePrefetch",
            True
        )

        opts.set_preference(
            "network.http.speculative-parallel-limit",
            0
        )

        opts.set_preference(
            "media.peerconnection.enabled",
            False
        )

        opts.set_preference(
            "toolkit.telemetry.enabled",
            False
        )

        opts.set_preference(
            "datareporting.healthreport.uploadEnabled",
            False
        )

    driver = webdriver.Firefox(
        service=Service(GECKODRIVER),
        options=opts
    )

    driver.set_page_load_timeout(
        TOR_PAGE_TIMEOUT if tor else PAGE_TIMEOUT
    )

    return driver


# =========================
# NORMALIZAÇÃO
# =========================

def normalize(url):

    url = url.strip()

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url


# =========================
# VERIFICAÇÃO
# =========================

def check(driver, url):

    start = time.perf_counter()

    resultado = {
        "url": url,
        "status": "",
        "final_url": "",
        "title": "",
        "erro": "",
        "ms": 0
    }

    try:

        driver.get(url)

        current_url = driver.current_url

        if current_url.startswith("about:"):

            query = parse_qs(
                urlparse(current_url).query
            )

            resultado["status"] = "offline"

            resultado["erro"] = query.get(
                "e",
                ["neterror"]
            )[0]

        else:

            resultado["status"] = "online"

            resultado["final_url"] = current_url

            resultado["title"] = (
                driver.title or ""
            ).strip()

    except TimeoutException:

        resultado["status"] = "offline"
        resultado["erro"] = "timeout"

        # Tenta interromper o carregamento atual
        try:
            driver.execute_script(
                "window.stop();"
            )
        except Exception:
            pass

    except WebDriverException as e:

        resultado["status"] = "offline"

        resultado["erro"] = (
            e.msg or type(e).__name__
        ).splitlines()[0][:120]

    except Exception as e:

        resultado["status"] = "offline"

        resultado["erro"] = (
            str(e) or type(e).__name__
        ).splitlines()[0][:120]

    resultado["ms"] = round(
        (time.perf_counter() - start) * 1000
    )

    resultado["checked_at"] = (
        datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
    )

    return resultado
