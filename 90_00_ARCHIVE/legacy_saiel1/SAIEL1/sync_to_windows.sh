#!/bin/bash
# =============================================================
# SAIEL - Script de Sincronizacion Parrot -> Windows
# Uso: bash sync_to_windows.sh
# =============================================================

WINDOWS_IP="192.168.100.27"
WINDOWS_USER="dcamb"
WINDOWS_PATH="/c/Users/dcamb/Desktop/Consultoria_Inteligencia"
LOCAL_PATH="$HOME/SAIEL_Inteligencia_Politica"
SSH_KEY="$HOME/.ssh/saiel_key"

echo "=============================================="
echo "SAIEL - Sincronizacion Parrot -> Windows"
echo "=============================================="

# 1. Verificar conexion SSH
echo "[1/4] Verificando conexion con Windows..."
if ssh -i $SSH_KEY -o ConnectTimeout=5 $WINDOWS_USER@$WINDOWS_IP "echo ok" > /dev/null 2>&1; then
    echo "[OK] Conexion establecida con $WINDOWS_IP"
else
    echo "[ERROR] No se puede conectar a Windows."
    echo "Verifica que SSH este activo en Windows (192.168.100.27)"
    exit 1
fi

# 2. Sincronizar datos raw
echo "[2/4] Enviando datos a Windows..."
rsync -avz --progress \
    -e "ssh -i $SSH_KEY" \
    $LOCAL_PATH/data/raw/ \
    $WINDOWS_USER@$WINDOWS_IP:$WINDOWS_PATH/data/raw/

if [ $? -eq 0 ]; then
    echo "[OK] Datos sincronizados exitosamente"
else
    echo "[ERROR] Fallo la sincronizacion de datos"
    exit 1
fi

# 3. Disparar el orquestador en Windows
echo "[3/4] Iniciando analisis en Windows..."
ssh -i $SSH_KEY $WINDOWS_USER@$WINDOWS_IP \
    "python C:/Users/dcamb/Desktop/Consultoria_Inteligencia/orchestrator.py"

if [ $? -eq 0 ]; then
    echo "[OK] Analisis completado en Windows"
else
    echo "[AVISO] El analisis puede estar corriendo en segundo plano"
fi

# 4. Traer resultados de vuelta
echo "[4/4] Descargando resultados..."
rsync -avz \
    -e "ssh -i $SSH_KEY" \
    $WINDOWS_USER@$WINDOWS_IP:$WINDOWS_PATH/data/processed/ \
    $LOCAL_PATH/data/processed/

rsync -avz \
    -e "ssh -i $SSH_KEY" \
    $WINDOWS_USER@$WINDOWS_IP:$WINDOWS_PATH/reports/ \
    $LOCAL_PATH/reports/

echo "=============================================="
echo "[COMPLETADO] Pipeline ejecutado exitosamente"
echo "Revisa el dashboard en: $LOCAL_PATH/reports/DASHBOARD_NAYARIT.html"
echo "=============================================="
