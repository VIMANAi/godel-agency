# SAIEL - Sistema de Inteligencia Política
## Instrucciones para Parrot OS

### Cómo acceder a este proyecto desde Parrot:

#### Opción 1: rclone (Recomendado)
```bash
# Instalar rclone
sudo apt install rclone -y

# Configurar Google Drive
rclone config
# → n (new remote)
# → nombre: gdrive
# → tipo: 13 (Google Drive)
# → Autenticar en navegador

# Montar Drive
mkdir -p ~/GoogleDrive
rclone mount gdrive: ~/GoogleDrive --daemon

# Acceder al proyecto
cd ~/GoogleDrive/Mi\ unidad/SAIEL_Inteligencia_Politica/
```

#### Opción 2: google-drive-ocamlfuse
```bash
sudo add-apt-repository ppa:alessandro-strada/ppa
sudo apt update
sudo apt install google-drive-ocamlfuse -y
google-drive-ocamlfuse ~/GoogleDrive
```

### Flujo de Trabajo desde Parrot:

1. **Captura datos con Zeeschuimer:**
   - Abre Firefox en Parrot
   - Instala Zeeschuimer
   - Haz scroll en perfiles de candidatos
   - Exporta como `zeeschuimer_CANDIDATO_FECHA.ndjson`

2. **Guarda en Drive:**
   ```bash
   cp ~/Downloads/zeeschuimer_*.ndjson ~/GoogleDrive/Mi\ unidad/SAIEL_Inteligencia_Politica/data/raw/
   ```

3. **El archivo aparece automáticamente en Windows:**
   - Ruta: `G:\Mi unidad\SAIEL_Inteligencia_Politica\data\raw\`
   - Antigravity (Cursor) lo procesa automáticamente

### Estructura del Proyecto:
```
SAIEL_Inteligencia_Politica/
├── engine/              # Scripts de análisis
│   ├── social_collector.py
│   ├── mass_collector.py
│   ├── sensemaker_engine.py
│   └── local_sentiment.py
├── reports/             # Dashboards y reportes
│   └── DASHBOARD_NAYARIT.html
├── data/
│   ├── raw/             # Datos de Zeeschuimer/Apify
│   └── processed/       # Resultados del análisis
└── tools/               # Herramientas auxiliares
```
