#!/bin/bash
# Post-create setup script - Container oluşturulduktan sonra çalışır

set -e

echo "🚀 OBA Robot Development Environment Setup Started..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log function
log() {
    echo -e "${GREEN}[SETUP]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Change to workspace directory
cd /workspace

log "Installing Python dependencies..."

# Ana requirements.txt'i yükle
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    log "Main requirements installed"
else
    warn "requirements.txt not found"
fi

# Development requirements (eğer varsa)
if [ -f "requirements-dev.txt" ]; then
    pip3 install -r requirements-dev.txt
    log "Development requirements installed"
fi

# Simulation requirements (eğer varsa)
if [ -f "requirements-simulation.txt" ]; then
    pip3 install -r requirements-simulation.txt
    log "Simulation requirements installed"
fi

log "Setting up GPIO mocking..."

# GPIO mock setup
python3 -c "
import sys
import fake_rpi
sys.modules['RPi'] = fake_rpi.RPi
sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO
sys.modules['smbus'] = fake_rpi.smbus
print('GPIO mocking configured')
"

log "Creating development directories..."

# Development directories oluştur
mkdir -p logs
mkdir -p data
mkdir -p temp
mkdir -p simulation/outputs
mkdir -p test_outputs

log "Setting up git hooks..."

# Git hooks setup (eğer .git varsa)
if [ -d ".git" ]; then
    # Pre-commit hook for code formatting
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Auto-format Python files before commit
files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')
if [ ! -z "$files" ]; then
    echo "Formatting Python files..."
    black $files
    git add $files
fi
EOF
    chmod +x .git/hooks/pre-commit
    log "Git hooks configured"
fi

log "Setting up virtual display..."

# Virtual display setup for GUI applications
if ! pgrep -x "Xvfb" > /dev/null; then
    Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
    export DISPLAY=:99
    log "Virtual display started"
fi

log "Creating configuration files..."

# Development config oluştur (eğer yoksa)
if [ ! -f "config/development.json" ]; then
    cat > config/development.json << 'EOF'
{
  "environment": "development",
  "debug": true,
  "simulation_mode": true,
  "gpio_mock": true,
  "camera_mock": true,
  "web": {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": true
  },
  "logging": {
    "level": "DEBUG",
    "file": "logs/development.log"
  }
}
EOF
    log "Development config created"
else
    log "Development config already exists"
fi

log "Setting up development aliases..."

# Bash aliases for development
cat >> ~/.bashrc << 'EOF'

# OBA Robot Development Aliases
alias oba-start="python3 main.py"
alias oba-test="python3 -m pytest tests/"
alias oba-sim="python3 -m simulation.run_simulation"
alias oba-web="python3 -m src.web.web_server"
alias oba-format="black src/ tests/ scripts/"
alias oba-lint="pylint src/"
alias oba-logs="tail -f logs/development.log"
alias oba-clean="find . -type d -name __pycache__ -delete"

# Docker shortcuts
alias dc="docker-compose"
alias dps="docker ps"

# Python shortcuts
alias py="python3"
alias pip="pip3"

EOF

log "Creating test data..."

# Test verisi oluştur
cat > data/test_areas.json << 'EOF'
{
  "test_area_1": {
    "name": "Front Garden",
    "boundaries": [
      [0, 0],
      [10, 0],
      [10, 8],
      [0, 8]
    ],
    "obstacles": [
      {
        "type": "tree",
        "position": [3, 4],
        "radius": 0.5
      }
    ]
  }
}
EOF

log "Setting up Jupyter Lab configuration..."

# Jupyter configuration
jupyter lab --generate-config -y
cat >> ~/.jupyter/jupyter_lab_config.py << 'EOF'
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.allow_root = True
c.ServerApp.open_browser = False
c.ServerApp.token = ''
c.ServerApp.password = ''
EOF

log "Setting permissions..."

# Dosya izinlerini düzelt
chmod +x scripts/*.py 2>/dev/null || true
chmod 755 logs data temp simulation/outputs test_outputs 2>/dev/null || true

log "Running initial tests..."

# Basit import testi
python3 -c "
try:
    import numpy
    import flask
    import cv2
    print('✅ Core dependencies working')
except ImportError as e:
    print(f'❌ Import error: {e}')
"

# Mock GPIO testi
python3 -c "
try:
    import fake_rpi
    import sys
    sys.modules['RPi'] = fake_rpi.RPi
    sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO
    from RPi import GPIO
    print('✅ GPIO mocking working')
except Exception as e:
    print(f'❌ GPIO mock error: {e}')
"

log "Creating helpful README for development..."

cat > DEVELOPMENT.md << 'EOF'
# 🛠️ OBA Robot Development Environment

Bu devcontainer ile robot geliştirme ortamınız hazır!

## 🚀 Hızlı Başlangıç

```bash
# Robot başlat
oba-start

# Web arayüzü başlat
oba-web

# Testleri çalıştır
oba-test

# Simülasyon başlat
oba-sim
```

## 🔧 Development Tools

- **Code Formatting**: `oba-format`
- **Linting**: `oba-lint`
- **Clean Cache**: `oba-clean`
- **View Logs**: `oba-logs`

## 🌐 Ports

- **5000**: Flask Web Server
- **8080**: Development Server
- **8888**: Jupyter Lab

## 📁 Important Directories

- `logs/`: Log files
- `data/`: Test data
- `simulation/outputs/`: Simulation results
- `test_outputs/`: Test results

## 🎮 Mock Mode

GPIO ve kamera mock mode'da çalışıyor:
- `GPIO_MOCK=1`
- `CAMERA_MOCK=1`

Bu sayede gerçek hardware olmadan development yapabilirsiniz.
EOF

echo ""
log "🎉 OBA Robot Development Environment Setup Complete!"
echo ""
info "Available commands:"
echo "  oba-start    - Start the robot application"
echo "  oba-test     - Run tests"
echo "  oba-sim      - Start simulation"
echo "  oba-web      - Start web server"
echo "  oba-format   - Format code"
echo ""
info "Access points:"
echo "  Web UI: http://localhost:5000"
echo "  Jupyter: http://localhost:8888"
echo ""
info "Happy coding! 🤖"
