# OPORTUNIDADES ALGORÍTMICAS: SCIKIT-LEARN PARA SAIEL

Este documento mapea algoritmos avanzados de Scikit-Learn hacia objetivos estratégicos del proyecto de Inteligencia Política.

## 1. Detección de Guerra Sucia (Anomalías)
*   **Algoritmo:** `sklearn.ensemble.IsolationForest`
*   **Crate Origen:** `sklearn.ensemble`
*   **Aplicación SAIEL:** Identificar picos de menciones negativas coordinadas. Si un volumen de conversación se desvía drásticamente del comportamiento histórico un martes a las 3 AM, el sistema dispara una alerta de "Ataque de Bots".

## 2. Optimización de Predicción (Regresión)
*   **Algoritmo:** `sklearn.linear_model.Ridge`
*   **Crate Origen:** `sklearn.linear_model`
*   **Aplicación SAIEL:** Ajustar los pesos de la fórmula PDIV. En lugar de usar `0.4` para sentimiento por intuición, el modelo entrena con resultados electorales pasados para encontrar el peso real de la opinión digital en el voto físico.

## 3. Descubrimiento de Narrativas (Tópicos)
*   **Algoritmo:** `sklearn.decomposition.LatentDirichletAllocation` (LDA)
*   **Crate Origen:** `sklearn.decomposition`
*   **Aplicación SAIEL:** Clasificar miles de comentarios en temas automáticamente (Seguridad, Salud, Corrupción). Permite ver de qué "habla la calle" sin que un humano lea cada mensaje.

## 4. Perfilamiento de Audiencia (Clasificación)
*   **Algoritmo:** `sklearn.ensemble.RandomForestClassifier`
*   **Crate Origen:** `sklearn.ensemble`
*   **Aplicación SAIEL:** Clasificar a los usuarios en "Votante Probable", "Simpatizante", "Opositor" o "Bot" basado en sus patrones de interacción (likes, frecuencia de posteo, sentimiento).

---
*Documento de Estrategia Algorítmica v1.0*
