#!/bin/bash
# Script de inicialização do CarDataReader no R36S

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Variáveis de ambiente para pygame via KMS (sem X11)
export SDL_VIDEODRIVER=kmsdrm
export SDL_AUDIODRIVER=alsa

# Forçar fullscreen e desativar mock para hardware real
export CARDATAREADER_FULLSCREEN=1
export CARDATAREADER_MOCK=0

# Aguarda o serviço OBD (obd-bridge ou elm327) subir, se necessário
# sleep 2

python3 main.py
