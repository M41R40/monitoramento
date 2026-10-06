from monitor_comum import (
    conectar_banco,
    buscar_alvos,
    salvar_verificacao,
    new_driver,
    check
)


def main():

    conn = conectar_banco()

    alvos = buscar_alvos(conn, "normal")

    print(f"Total de sites normais: {len(alvos)}")

    driver = new_driver(
        headless=True,
        tor=False
    )

    online = 0
    offline = 0

    try:

        for i, (alvo_id, url) in enumerate(alvos, 1):

            print(
                f"[{i}/{len(alvos)}] "
                f"Verificando: {url}"
            )

            resultado = check(
                driver,
                url
            )

            salvar_verificacao(
                conn,
                alvo_id,
                resultado
            )

            if resultado["status"] == "online":
                online += 1
            else:
                offline += 1

            print(
                f"    {resultado['status'].upper()} "
                f"| {resultado['ms']} ms "
                f"| {resultado['title'] or resultado['erro']}"
            )

    finally:

        driver.quit()
        conn.close()

    print()
    print("===== RESULTADO =====")
    print(f"Online : {online}")
    print(f"Offline: {offline}")


if __name__ == "__main__":
    main()
