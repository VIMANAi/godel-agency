-- ==============================================================================
-- SAIEL: ESQUEMA DE BASE DE DATOS LOCAL (SQLite)
-- Ubicación: data/db/saiel_local.db (Generado dinámicamente)
-- Versión: 2.5 (Demographics and Historical Elections Support)
-- ==============================================================================

-- 1. Tabla de Comentarios y Posts Anonimizados
CREATE TABLE IF NOT EXISTS comentarios (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    text TEXT NOT NULL,
    user TEXT,
    user_id TEXT,
    likes INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    candidate TEXT,
    date TEXT NOT NULL,
    collected_at TEXT NOT NULL,
    anonymized INTEGER DEFAULT 1,
    quality_score REAL DEFAULT 1.0
);

-- 2. Tabla de Resultados de Sentimiento
CREATE TABLE IF NOT EXISTS resultados_sentimiento (
    comentario_id TEXT PRIMARY KEY,
    score REAL DEFAULT 0.0,
    label TEXT DEFAULT 'neutro',
    topic TEXT DEFAULT 'General',
    es_bot INTEGER DEFAULT 0,
    intensidad INTEGER DEFAULT 3,
    fecha_analisis TEXT NOT NULL,
    FOREIGN KEY (comentario_id) REFERENCES comentarios (id) ON DELETE CASCADE
);

-- 3. Tabla de Puntuaciones PDIV Históricas (Trazabilidad Electorales)
CREATE TABLE IF NOT EXISTS pdiv_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidato TEXT NOT NULL,
    pdiv_score REAL NOT NULL,
    sentimiento_score REAL NOT NULL,
    volumen_score REAL NOT NULL,
    engagement_score REAL NOT NULL,
    crecimiento_score REAL NOT NULL,
    region TEXT NOT NULL,
    total_menciones INTEGER DEFAULT 0,
    fecha_calculo TEXT NOT NULL
);

-- 4. Tabla de Alertas de Crisis
CREATE TABLE IF NOT EXISTS alertas_crisis (
    id TEXT PRIMARY KEY,
    severidad TEXT NOT NULL, -- 'ALTA', 'MEDIA', 'BAJA'
    mensaje TEXT NOT NULL,
    fecha_alerta TEXT NOT NULL,
    status TEXT DEFAULT 'ACTIVE' -- 'ACTIVE', 'RESOLVED'
);

-- 5. Tabla de Demografía Municipal (INEGI 2020)
CREATE TABLE IF NOT EXISTS inegi_demographics (
    municipio TEXT PRIMARY KEY,
    poblacion INTEGER NOT NULL,
    factor_poblacion REAL NOT NULL
);

-- 6. Tabla de Votos Históricos (IEEN Nayarit)
CREATE TABLE IF NOT EXISTS ieen_historical_votes (
    partido TEXT PRIMARY KEY,
    votos_proporcion REAL NOT NULL
);

-- 7. Tabla de Encuestas Electorales (Ground Truth)
CREATE TABLE IF NOT EXISTS electoral_polls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    encuestadora TEXT NOT NULL,
    candidato TEXT NOT NULL,
    intencion_voto REAL NOT NULL,
    margen_error REAL NOT NULL
);

-- Índices para optimización de consultas analíticas (SoC)
CREATE INDEX IF NOT EXISTS idx_comentarios_candidato ON comentarios(candidate);
CREATE INDEX IF NOT EXISTS idx_comentarios_fecha ON comentarios(date);
CREATE INDEX IF NOT EXISTS idx_pdiv_candidato ON pdiv_scores(candidato);
CREATE INDEX IF NOT EXISTS idx_pdiv_fecha ON pdiv_scores(fecha_calculo);
CREATE INDEX IF NOT EXISTS idx_polls_candidato ON electoral_polls(candidato);
