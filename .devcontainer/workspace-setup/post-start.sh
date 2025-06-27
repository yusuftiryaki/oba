#!/bin/bash
# Post-start setup script - Container her başlatıldığında çalışır

set -e

echo "🔄 OBA Robot Container Starting..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[START]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log "Loading OBA aliases..."
# Load OBA development aliases
source /workspaces/ot-bicme/.devcontainer/workspace-setup/oba-aliases.sh

log "Starting virtual display..."

# Virtual display başlat (eğer çalışmıyorsa)
if ! pgrep -x "Xvfb" > /dev/null; then
    Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
    export DISPLAY=:99
    sleep 2
    log "Virtual display started"
fi

log "Checking services..."

# Log directory kontrolü
mkdir -p logs data temp

# Geliştirme sunucularının durumunu kontrol et
if pgrep -f "python.*web_server" > /dev/null; then
    info "Web server is already running"
else
    info "Web server is not running - use 'oba-web' to start"
fi

log "Environment ready!"

# Startup mesajı
cat << 'EOF'

╔══════════════════════════════════════════════════════════════╗
║                    🤖 OBA Robot DevContainer                 ║
║                  Otonom Bahçe Asistanı Geliştirme          ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Quick Commands:                                             ║
║    oba-start    → Start robot application                    ║
║    oba-web      → Start web interface                       ║
║    oba-sim      → Start simulation                          ║
║    oba-test     → Run test suite                            ║
║                                                              ║
║  Web Interfaces:                                             ║
║    Robot UI:    http://localhost:5000                       ║
║    Jupyter:     http://localhost:8888                       ║
║                                                              ║
║  Development:                                                ║
║    GPIO & Camera are in MOCK mode for development           ║
║    Logs: tail -f logs/development.log                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

EOF

echo "Ready to code! 🚀"
