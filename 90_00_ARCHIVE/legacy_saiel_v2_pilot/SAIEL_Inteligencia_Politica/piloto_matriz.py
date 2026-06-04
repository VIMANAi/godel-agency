import random

import pandas as pd


def generar_datos_piloto(temas, candidatos):
    """
    Simula la recolección de datos orgánicos para el piloto.
    """
    data = []
    for _ in range(100):
        candidato = random.choice(candidatos)
        tema = random.choice(temas)
        # Generar un sentimiento entre -1 (muy negativo) y 1 (muy positivo)
        sentimiento = round(random.uniform(-1, 1), 2)
        # Generar un nivel de impacto/volumen de la mención
        impacto = random.randint(10, 500)

        data.append({"candidato": candidato, "tema": tema, "sentimiento": sentimiento, "impacto": impacto})
    return pd.DataFrame(data)


def crear_matriz_posicionamiento(df):
    """
    Calcula las coordenadas para la matriz.
    """
    matriz = df.groupby("candidato").agg({"sentimiento": "mean", "impacto": "sum"}).reset_index()

    # Normalizar impacto para visualización (0 a 100)
    matriz["volumen_conversacion"] = (matriz["impacto"] / matriz["impacto"].max()) * 100
    return matriz


# --- CONFIGURACIÓN DEL PILOTO ---
temas_interes = ["Seguridad", "Economía", "Salud", "Corrupción"]
candidatos_demo = ["Candidato A (Nuestro)", "Rival X", "Rival Y"]

print("--- Iniciando Simulación de Escucha Activa ---")
df_organico = generar_datos_piloto(temas_interes, candidatos_demo)

print("--- Procesando Matriz de Posicionamiento ---")
resultados = crear_matriz_posicionamiento(df_organico)

# Simulación de cuadrantes
print("\nRESULTADOS DE LA MATRIZ (Radar de Percepción):")
for _, row in resultados.iterrows():
    percepcion = "POSITIVA" if row["sentimiento"] > 0 else "NEGATIVA"
    nivel = "ALTO IMPACTO" if row["volumen_conversacion"] > 50 else "BAJO IMPACTO"

    print(f"\n> {row['candidato']}:")
    print(f"  - Sentimiento Promedio: {row['sentimiento']} ({percepcion})")
    print(f"  - Volumen de Conversación: {int(row['volumen_conversacion'])}% ({nivel})")

# Guardar para reporte
resultados.to_json("c:/Users/dcamb/Desktop/Consultoria_Inteligencia/datos_piloto_matriz.json", orient="records")
print("\nProceso completado. Datos guardados en 'datos_piloto_matriz.json' para visualización.")
