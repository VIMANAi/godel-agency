import pandas as pd
import json
import random


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
import os

save_path = "data/processed/datos_piloto_matriz.json"
os.makedirs(os.path.dirname(save_path), exist_ok=True)
resultados.to_json(save_path, orient="records")
print(f"\nProceso completado. Datos guardados en '{save_path}' para visualización.")
