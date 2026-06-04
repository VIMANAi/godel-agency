
import requests

TOKEN = "REDACTED_APIFY_TOKEN"


def check_apify_account():
    print("--- 🛰️ CONECTANDO CON EL API REST DE APIFY ---")
    headers = {"Authorization": f"Bearer {TOKEN}"}

    # 1. Obtener datos de la cuenta (Créditos y Límites)
    url_me = "https://api.apify.com/v2/users/me"
    try:
        res = requests.get(url_me, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()["data"]
            print("\n✅ Conexión Exitosa con la Cuenta de Apify!")
            print(f" -> Usuario: {data.get('username')}")
            print(f" -> Email: {data.get('email')}")

            # Límites y créditos
            limits = data.get("limits", {})
            subscription = data.get("subscription", {})
            print(f" -> Tipo de Suscripción: {subscription.get('planId', 'Free')}")
            print(f" -> Créditos Mensuales Totales: ${limits.get('monthlyUsageUsd', 0.0):.2f} USD")

            # Consumo actual
            print(f" -> Consumo Actual en este Periodo: ${data.get('currentUsageUsd', 0.0):.2f} USD")

        else:
            print(f"❌ Error al consultar usuario: Código {res.status_code}")
            print(res.text)
    except Exception as e:
        print(f"❌ Excepción al conectar: {e}")

    # 2. Obtener lista de corridas (Runs) del Actor
    # Buscamos corridas en el rango de Febrero 2026 (2026-02-01 a 2026-02-28)
    url_runs = "https://api.apify.com/v2/actor-runs?limit=30"
    try:
        res = requests.get(url_runs, headers=headers, timeout=10)
        if res.status_code == 200:
            runs = res.json()["data"]["items"]
            print("\n📋 HISTORIAL DE RUNS ENCONTRADOS (ÚLTIMOS 30):")

            feb_runs_count = 0
            for r in runs:
                started = r.get("startedAt", "")
                # Parsear fecha
                # Formato: 2026-02-20T17:43:56.562Z
                dt_str = started.split("T")[0]

                # Filtrar runs de febrero 2026
                is_feb = dt_str.startswith("2026-02")
                if is_feb:
                    feb_runs_count += 1

                # Mostrar detalles
                status = r.get("status")
                actor_id = r.get("actId")
                run_id = r.get("id")
                dataset_id = r.get("defaultDatasetId")
                usage_usd = r.get("usageUsd", 0.0)

                # Mapear IDs legibles
                actor_name = "instagram-comment-scraper" if "instagram" in actor_id else "facebook-scraper/other"
                if is_feb:
                    print(
                        f" ⚠️ [FEB 2026] Run ID: {run_id} | Actor: {actor_name} | Fecha: {started} | Estado: {status} | Dataset: {dataset_id} | Costo: ${usage_usd:.4f} USD"
                    )
                else:
                    print(f"   [OTRO] Run ID: {run_id} | Fecha: {started} | Estado: {status} | Dataset: {dataset_id}")

            print(
                f"\n✓ Auditoría de Corridas de Febrero: Se identificaron {feb_runs_count} corridas activas de ese mes."
            )

        else:
            print(f"❌ Error al consultar corridas: Código {res.status_code}")
    except Exception as e:
        print(f"❌ Excepción al consultar corridas: {e}")


if __name__ == "__main__":
    check_apify_account()
