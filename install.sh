#!/bin/bash
# ============================================================
#  PhoneOSINT - Script de instalación para Kali Linux
#  Solo para entornos controlados y uso educativo
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════╗"
echo "║     PhoneOSINT - Instalación              ║"
echo "║     Kali Linux / Entorno Controlado       ║"
echo "╚═══════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar que sea root o sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}[!] Recomendado correr como root o con sudo${NC}"
fi

# Verificar Python3
echo -e "${CYAN}[*] Verificando Python3...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[!] Python3 no encontrado. Instalando...${NC}"
    apt-get install -y python3 python3-pip
else
    echo -e "${GREEN}[+] Python3 encontrado: $(python3 --version)${NC}"
fi

# Instalar pip si no está
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}[*] Instalando pip3...${NC}"
    apt-get install -y python3-pip
fi

# Instalar dependencias
echo -e "${CYAN}[*] Instalando dependencias Python...${NC}"
pip3 install -r requirements.txt --break-system-packages

# Dar permisos de ejecución
chmod +x src/phoneosint.py
chmod +x modules/batch_analysis.py

# Crear alias opcional
echo -e "\n${CYAN}[?] ¿Deseas crear un alias 'phoneosint' en bash? (s/n)${NC}"
read -r response
if [[ "$response" =~ ^[Ss]$ ]]; then
    echo "alias phoneosint='python3 $(pwd)/src/phoneosint.py'" >> ~/.bashrc
    echo -e "${GREEN}[+] Alias creado. Reinicia la terminal o ejecuta: source ~/.bashrc${NC}"
fi

echo -e "\n${GREEN}[+] Instalación completada.${NC}"
echo -e "${CYAN}[*] Uso básico:${NC}"
echo -e "    python3 src/phoneosint.py +573001234567"
echo -e "    python3 src/phoneosint.py +573001234567 -o reporte.json"
echo -e "    python3 modules/batch_analysis.py data/numeros.txt"
echo -e "\n${RED}[!] AVISO LEGAL: Usar solo con autorización. Solo para entornos controlados.${NC}\n"
