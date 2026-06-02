# MATRIZ DE ADYACENCIA INTER-PROYECTO: SAIEL <-> SCIKIT-LEARN

Este documento demuestra cómo el ecosistema SAIEL se ancla en los cimientos de Scikit-Learn.

## 1. Vínculos de Dependencia Algorítmica

| SAIEL Crate | Scikit-Learn Crate (Core) | Algoritmo / Utilidad |
| :--- | :--- | :--- |
| `saiel.sensemaker` | `sklearn.cluster` | **KMeans:** Agrupamiento semántico de narrativas. |
| `saiel.pdiv_calculator` | `sklearn.preprocessing` | **RobustScaler / MinMaxScaler:** Normalización de scores de intención. |
| `saiel.pdiv_calculator` | `sklearn.metrics` | **Correlation Coefficients:** Validación de predicciones vs encuestas. |

## 2. Inyección de Inteligencia (OpenAI Cookbook)

| SAIEL Task | OpenAI Pattern | Aplicación |
| :--- | :--- | :--- |
| Auditoría de Datos | `verifying-implementations` | Validación de que la PII fue removida correctamente. |
| Análisis de Sentimiento | `engineered-prompts` | Gemini 1.5 Flash detectando ironía y tópicos políticos. |

## 3. Grafo de Decisión del Agente Supervisor
Si el Supervisor recibe una falla en `saiel.sensemaker`, el grafo le indica:
1.  Verificar `sklearn.cluster` para asegurar que el modelo KMeans está bien instanciado.
2.  Verificar `saiel.data_anonymizer` para asegurar que los textos no están vacíos tras la limpieza.
