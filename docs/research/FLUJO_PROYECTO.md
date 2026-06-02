# Sistema de Inteligencia Política Automatizada
## Flujo de Trabajo y Arquitectura Técnica

---

## 🎯 OBJETIVO DEL PROYECTO

Crear un **sistema de inteligencia política automatizado** que permita a candidatos y equipos de campaña:

1. **Monitorear el sentimiento ciudadano** en tiempo real a través de redes sociales
2. **Identificar narrativas emergentes** de forma automática (sin categorización manual)
3. **Predecir intención de voto** basándose en datos digitales (PDIV - Posicionamiento Digital de Intención de Voto)
4. **Detectar ataques coordinados** y campañas de desinformación
5. **Generar reportes estratégicos** de forma automática para toma de decisiones

**Diferenciador clave:** Procesamiento 100% local (sin enviar datos a APIs externas), garantizando privacidad y cumplimiento con LGPDPPSO y GDPR.

---

## 📊 FLUJO DE TRABAJO COMPLETO

### **FASE 1: Recolección de Datos (Data Collection)**

#### **Herramientas:**
- **Apify** (Automatización en la nube)
- **Zeeschuimer** (Captura manual local)
- **CrowdTangle** (Datos históricos oficiales de Meta - opcional)

#### **Proceso:**
1. **Identificación de objetivos:**
   - Perfiles de candidatos (Andrea Navarro, Geraldine Ponce, etc.)
   - Hashtags relevantes (#Nayarit, #Tepic2025, etc.)
   - Páginas de medios locales

2. **Extracción automatizada:**
   - Script `social_collector.py` se conecta a Apify
   - Descarga comentarios, posts, reacciones de Instagram/Facebook/TikTok
   - Almacena datos en formato JSON en `data/raw/`

3. **Captura histórica:**
   - Zeeschuimer captura posts antiguos mediante scroll manual
   - Exporta archivos `.ndjson` con metadata completa
   - Permite análisis de tendencias temporales (ej: "¿Cómo cambió el sentimiento hacia X en los últimos 6 meses?")

**Output:** Archivos JSON con estructura:
```json
{
  "source": "instagram",
  "user": "usuario123",
  "text": "Comentario del ciudadano",
  "date": "2026-02-17T12:00:00",
  "likes": 15,
  "collected_at": "2026-02-17T14:30:00"
}
```

---

### **FASE 2: Análisis de Sentimiento (Sentiment Analysis)**

#### **Herramientas:**
- **Pysentimiento** (Modelo de Hugging Face optimizado para español)
- **Sentence-Transformers** (Embeddings semánticos)

#### **Proceso:**
1. **Limpieza de datos:**
   - Eliminación de emojis, URLs, menciones
   - Normalización de texto (minúsculas, acentos)
   - Filtrado de spam y bots (detección por patrones)

2. **Análisis de sentimiento local:**
   - Script `local_sentiment.py` carga el modelo `pysentimiento`
   - Procesa cada comentario y asigna score: -1 (negativo) a +1 (positivo)
   - Clasifica en categorías: POS, NEG, NEU

3. **Generación de embeddings:**
   - Convierte cada texto en un vector de 768 dimensiones
   - Permite comparación semántica entre comentarios
   - Base para clustering de narrativas

**Output:** Datos enriquecidos con sentimiento:
```json
{
  "text": "Me encanta el trabajo de Andrea en Los Sauces",
  "sentiment_score": 0.89,
  "sentiment_label": "POS",
  "embedding": [0.23, -0.45, 0.67, ...]
}
```

---

### **FASE 3: Descubrimiento de Narrativas (Narrative Discovery)**

#### **Herramientas:**
- **Sensemaker Engine** (Motor propio basado en Jigsaw Perspective API)
- **KMeans Clustering** (Scikit-learn)
- **BERTopic** (Modelado de temas - opcional para escala industrial)

#### **Proceso:**
1. **Clustering automático:**
   - Script `sensemaker_engine.py` agrupa comentarios similares
   - Usa embeddings para identificar temas sin categorías predefinidas
   - Detecta narrativas emergentes (ej: "Crisis del agua", "Canchas recuperadas")

2. **Análisis de volumen y sentimiento:**
   - Calcula % de comentarios por narrativa
   - Promedio de sentimiento por tema
   - Identifica narrativas "tóxicas" (alto volumen + sentimiento negativo)

3. **Extracción de frases clave:**
   - Selecciona comentarios representativos de cada narrativa
   - Genera "quotes" para reportes

**Output:** Narrativas identificadas:
```json
{
  "narrative_id": 1,
  "theme": "Gestión: Canchas y Ebrard",
  "volume_percentage": 35.2,
  "avg_sentiment": 0.87,
  "key_phrases": [
    "Por fin recuperaron las canchas de Los Sauces",
    "Gracias Andrea por traer a Ebrard"
  ]
}
```

---

### **FASE 4: Cálculo de PDIV (Posicionamiento Digital de Intención de Voto)**

#### **Herramientas:**
- **Modelo PDIV** (Algoritmo propio)
- **Pandas/NumPy** (Procesamiento de datos)

#### **Proceso:**
1. **Ponderación de métricas:**
   - Volumen de menciones (30%)
   - Sentimiento promedio (40%)
   - Engagement (likes, shares) (20%)
   - Crecimiento semanal (10%)

2. **Normalización:**
   - Ajuste por tamaño de población (Tepic vs Nayarit)
   - Corrección por bots detectados
   - Ponderación por fuente (Instagram > Facebook > TikTok para jóvenes)

3. **Generación de score:**
   - PDIV = f(volumen, sentimiento, engagement, crecimiento)
   - Escala 0-100 (comparable con encuestas tradicionales)

**Output:** Matriz de posicionamiento:
```json
{
  "candidate": "Andrea Navarro",
  "pdiv_score": 21.5,
  "sentiment_avg": 0.86,
  "weekly_growth": 5.2,
  "position": "Challenger con momentum positivo"
}
```

---

### **FASE 5: Visualización y Reportes (Reporting)**

#### **Herramientas:**
- **Dashboard HTML/CSS/JS** (Chart.js para gráficas)
- **Jupyter Notebooks** (Análisis exploratorio)
- **Markdown → PDF** (Reportes ejecutivos)

#### **Proceso:**
1. **Dashboard interactivo:**
   - Gráfica de burbujas (Sentimiento vs PDIV)
   - Timeline de narrativas emergentes
   - Alertas de crisis (sentimiento negativo > umbral)

2. **Reportes automáticos:**
   - Generación semanal de PDF con insights
   - Sección "Narrativas a potenciar" (positivas)
   - Sección "Narrativas a neutralizar" (negativas)

3. **Alertas en tiempo real:**
   - Notificación si sentimiento cae >10% en 24h
   - Detección de ataques coordinados (volumen anormal + cuentas nuevas)

**Output:** Dashboard visual y reportes PDF listos para presentar al cliente.

---

## 🛠️ STACK TECNOLÓGICO

### **Recolección:**
- Apify (Cloud scraping)
- Zeeschuimer (Local capture)
- Python `apify-client`

### **Procesamiento:**
- Python 3.11+
- Pandas, NumPy (Data manipulation)
- Pysentimiento (Sentiment analysis)
- Sentence-Transformers (Embeddings)
- Scikit-learn (Clustering)

### **Almacenamiento:**
- JSON files (Raw data)
- SQLite (Opcional para datasets grandes)

### **Visualización:**
- HTML/CSS/JS (Dashboard)
- Chart.js (Gráficas interactivas)
- Jupyter (Análisis exploratorio)

### **Infraestructura:**
- Sistema operativo: Parrot OS / Ubuntu (para herramientas OSINT)
- Procesamiento: 100% local (sin APIs externas)
- Anonimato: AnonSurf/Tor (para scraping sensible)

---

## 🎯 PROFESIONALIZACIÓN DEL SISTEMA

### **Nivel 1: Piloto (Estado Actual)**
✅ Recolección manual de URLs
✅ Análisis de sentimiento básico
✅ Dashboard estático con datos de ejemplo
✅ Reportes manuales

### **Nivel 2: Automatización Básica (Próximo paso)**
🔄 Recolección automática diaria (cron jobs)
🔄 Análisis de sentimiento en batch
🔄 Dashboard con datos reales actualizados
🔄 Reportes semi-automáticos (plantillas)

### **Nivel 3: Sistema Profesional (Objetivo 3-6 meses)**
🎯 **Recolección continua:**
   - Scraping cada 6 horas
   - Integración con CrowdTangle
   - Alertas en tiempo real

🎯 **Análisis avanzado:**
   - Detección de bots con ML
   - Análisis de redes sociales (SNA)
   - Predicción de tendencias

🎯 **Interfaz profesional:**
   - Dashboard web con autenticación
   - API REST para integraciones
   - App móvil para el cliente

🎯 **Escalabilidad:**
   - Base de datos PostgreSQL
   - Procesamiento distribuido (Celery)
   - Cache con Redis

### **Nivel 4: Producto Comercial (Objetivo 1 año)**
🚀 **Multi-tenant:**
   - Múltiples clientes en la misma plataforma
   - Aislamiento de datos por cliente

🚀 **IA Avanzada:**
   - Modelos fine-tuned para política mexicana
   - Generación automática de estrategias

🚀 **Compliance:**
   - Auditoría completa (logs de acceso)
   - Certificación ISO 27001
   - Cumplimiento con EU AI Act

---

## 💰 MODELO DE NEGOCIO

### **Fase Piloto (Actual):**
- Cliente: Andrea Navarro (Tepic)
- Modelo: Proyecto único ($X MXN)
- Entregables: Dashboard + 3 reportes mensuales

### **Fase Profesional:**
- Clientes: 3-5 candidatos simultáneos
- Modelo: Suscripción mensual ($X MXN/mes por candidato)
- Entregables: Dashboard 24/7 + reportes semanales + alertas

### **Fase Comercial:**
- Clientes: Partidos políticos, consultoras
- Modelo: SaaS ($X MXN/mes + % de presupuesto de campaña)
- Entregables: Plataforma completa + soporte + capacitación

---

## 🔐 CUMPLIMIENTO LEGAL Y ÉTICO

### **Privacidad:**
- Procesamiento 100% local (sin envío a nubes externas)
- Solo datos públicos (no scraping de perfiles privados)
- Anonimización de usuarios en reportes

### **Transparencia:**
- Human-in-the-loop (revisión humana de análisis automáticos)
- Explicabilidad de decisiones del modelo
- Auditoría de sesgos algorítmicos

### **Normativas:**
- LGPDPPSO (México)
- GDPR (Europa - si se expande)
- Berkeley Protocol (OSINT ético)

---

## 📈 MÉTRICAS DE ÉXITO

### **Técnicas:**
- Precisión de sentimiento >85%
- Tiempo de procesamiento <5 min para 1000 comentarios
- Uptime del sistema >99%

### **Negocio:**
- Correlación PDIV vs encuestas tradicionales >0.7
- Detección de crisis 24-48h antes que medios
- ROI del cliente: Ahorro >30% vs métodos tradicionales

### **Impacto:**
- Decisiones estratégicas basadas en datos reales
- Reducción de "intuición política" no fundamentada
- Democratización del acceso a inteligencia política

---

## 🚀 ROADMAP

### **Q1 2026 (Actual):**
- ✅ Piloto con Andrea Navarro
- ✅ Motor de Sensemaker funcional
- 🔄 Dashboard con datos reales

### **Q2 2026:**
- Automatización completa (cron jobs)
- Integración con CrowdTangle
- 3 clientes simultáneos

### **Q3-Q4 2026:**
- Plataforma web multi-tenant
- API REST
- Certificación de seguridad

### **2027:**
- Expansión a otros estados
- Producto SaaS comercial
- Equipo de 5+ personas

---

**Documento generado:** 17 de febrero de 2026
**Versión:** 1.0
**Autor:** Sistema de Inteligencia Política - Consultoria Nayarit
