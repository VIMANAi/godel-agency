from pysentimiento import create_analyzer
import json
import os
import sys

# Inicializar el analizador de sentimiento para español
# Este modelo solo pesa ~400MB y corre localmente
analyzer = create_analyzer(task="sentiment", lang="es")

def analizar_sentimiento_local(textos):
    """
    Analiza una lista de textos y devuelve el sentimiento predominante
    con una metodología de precisión local.
    """
    resultados = []
    for texto in textos:
        res = analyzer.predict(texto)
        # Convertimos el resultado a una puntuación numérica entre -1 y 1
        scores = res.probas
        # puntuacion = pos - neg
        puntuacion = scores['POS'] - scores['NEG']
        
        resultados.append({
            "texto": texto[:100] + "...",
            "label": res.output,
            "score": round(puntuacion, 2),
            "probas": scores
        })
    return resultados

# --- LOGICA DE EJECUCION ---
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Si se pasa un archivo como argumento
    if len(sys.argv) > 1:
        target_name = sys.argv[1]
        raw_path = os.path.join(base_dir, "data", "raw", target_name)
        
        if os.path.exists(raw_path):
            print(f"--- Procesando archivo: {target_name} ---")
            with open(raw_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Extraer textos (asumiendo formato SAIEL/Zeeschuimer convertido)
            textos = [item.get("text", "") for item in data if item.get("text")]
            
            if not textos:
                print("[ERROR] No se encontraron textos en el archivo.")
                sys.exit(1)
                
            print(f"Analizando {len(textos)} registros...")
            analitica = analizar_sentimiento_local(textos[:50]) # Limitado a 50 para velocidad
            
            output_name = f"sentimiento_{os.path.splitext(target_name)[0]}.json"
            output_path = os.path.join(base_dir, "data", "processed", output_name)
        else:
            print(f"[ERROR] No se encuentra el archivo: {raw_path}")
            sys.exit(1)
    else:
        # PRUEBA POR DEFECTO (ANDREA NAVARRO)
        print("--- Iniciando Análisis de Sentimiento Local (PRUEBA ANDREA NAVARRO) ---")
        textos_andrea = [
            "Andrea Navarro es fundadora de Morena y ha trabajado por el bienestar de Tepic.",
            "La diputada obtuvo la votación más alta del distrito, demostrando apoyo popular real.",
            "Se rumora que hay conflicto entre los Navarros y Geraldine por la policía en la feria.",
            "Andrea aclaró que no tiene parentesco con el gobernador Arturo Navarro.",
            "Es una joven dentista que camina las colonias y escucha a la gente."
        ]
        analitica = analizar_sentimiento_local(textos_andrea)
        output_path = os.path.join(base_dir, "data", "processed", "analisis_local_andrea.json")

    # Guardar resultados
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analitica, f, indent=4, ensure_ascii=False)
    
    print(f"\nResultados guardados en: {output_path}")
