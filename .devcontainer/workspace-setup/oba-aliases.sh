#!/bin/bash
# OBA Robot Development Aliases
# Bu dosya dev container başlangıcında yüklenir

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Helper function
oba_log() {
    echo -e "${GREEN}[OBA]${NC} $1"
}

# Robot Application Commands
alias oba-start='oba_log "Starting robot application..." && python3 main.py'
alias oba-web='oba_log "Starting web interface..." && python3 -m src.web.web_server'
alias oba-sim='oba_log "Starting simulation..." && python3 -m simulation.run_simulation'

# Development Commands
alias oba-test='oba_log "Running test suite..." && python3 -m pytest tests/ -v --cov=src'
alias oba-lint='oba_log "Running linter..." && pylint src/'
alias oba-format='oba_log "Formatting code..." && black src/ tests/ scripts/ simulation/'
alias oba-type='oba_log "Type checking..." && mypy src/'
alias oba-security='oba_log "Security check..." && bandit -r src/'

# Utility Commands
alias oba-clean='oba_log "Cleaning cache..." && find . -type d -name "__pycache__" -delete'
alias oba-install='oba_log "Installing dependencies..." && pip3 install -r requirements.txt -r requirements-dev.txt'
alias oba-status='oba_log "System status..." && python3 scripts/system_status.py'
alias oba-safety='oba_log "Safety check..." && python3 scripts/safety_check.py'

# Log Commands
alias oba-logs='tail -f logs/development.log'
alias oba-logs-error='grep ERROR logs/development.log | tail -20'
alias oba-logs-clear='oba_log "Clearing logs..." && > logs/development.log'

# Git Shortcuts
alias oba-commit='git add . && git commit -m'
alias oba-push='git push origin $(git branch --show-current)'
alias oba-pull='git pull origin $(git branch --show-current)'
alias oba-status-git='git status --short'

# Docker/Container Commands
alias oba-restart='oba_log "Restarting container..." && exit'
alias oba-rebuild='oba_log "Use: Dev Containers: Rebuild Container from VS Code"'

# Quick Navigation
alias oba-src='cd /workspaces/ot-bicme/src'
alias oba-tests='cd /workspaces/ot-bicme/tests'
alias oba-docs='cd /workspaces/ot-bicme/docs'
alias oba-config='cd /workspaces/ot-bicme/config'
alias oba-sim-dir='cd /workspaces/ot-bicme/simulation'

# Help Command
oba-help() {
    cat << 'EOF'

╔══════════════════════════════════════════════════════════════╗
║                    🤖 OBA Robot Commands                    ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  🚀 Application Commands:                                    ║
║    oba-start      → Start robot application                  ║
║    oba-web        → Start web interface                      ║
║    oba-sim        → Start simulation                         ║
║                                                              ║
║  🧪 Development Commands:                                    ║
║    oba-test       → Run test suite                           ║
║    oba-lint       → Run linter                               ║
║    oba-format     → Format code                              ║
║    oba-type       → Type checking                            ║
║    oba-security   → Security check                           ║
║                                                              ║
║  🛠️  Utility Commands:                                       ║
║    oba-clean      → Clean cache                              ║
║    oba-install    → Install dependencies                     ║
║    oba-status     → System status                            ║
║    oba-safety     → Safety check                             ║
║                                                              ║
║  📝 Log Commands:                                            ║
║    oba-logs       → Tail development logs                    ║
║    oba-logs-error → Show recent errors                       ║
║    oba-logs-clear → Clear logs                               ║
║                                                              ║
║  📁 Navigation:                                              ║
║    oba-src        → Go to src/                               ║
║    oba-tests      → Go to tests/                             ║
║    oba-docs       → Go to docs/                              ║
║    oba-config     → Go to config/                            ║
║    oba-sim-dir    → Go to simulation/                        ║
║                                                              ║
║  🔧 Git Shortcuts:                                           ║
║    oba-commit "msg" → Add & commit with message              ║
║    oba-push       → Push to current branch                   ║
║    oba-pull       → Pull from current branch                 ║
║    oba-status-git → Git status (short)                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

EOF
}

# Welcome message
oba_log "OBA Robot aliases loaded! Use ${YELLOW}oba-help${NC} to see all commands."
