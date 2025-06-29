// OBA Robot Web Arayüzü - Ana JavaScript Dosyası

class OBAWebInterface {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.manualControlActive = false;
        this.currentSpeed = 50;
        this.controlPadActive = false;
        this.cameraEnabled = false;

        this.init();
    }

    init() {
        console.log('🤖 OBA Robot Web Interface başlatılıyor...');

        // Socket.IO bağlantısı
        this.initSocket();

        // UI event'lerini ayarla
        this.initEventListeners();

        // Manuel kontrol setup
        this.initManualControl();

        // Periyodik güncellemeler
        this.startPeriodicUpdates();

        // Keyboard shortcuts
        this.initKeyboardShortcuts();

        console.log('✅ Web interface hazır!');
    }

    initSocket() {
        this.socket = io();

        this.socket.on('connect', () => {
            this.connected = true;
            this.updateConnectionStatus(true);
            console.log('🔗 Sunucuya bağlandı');
            this.showToast('Sunucuya bağlandı', 'success');
        });

        this.socket.on('disconnect', () => {
            this.connected = false;
            this.updateConnectionStatus(false);
            console.log('❌ Sunucu bağlantısı kesildi');
            this.showToast('Bağlantı kesildi', 'warning');
        });

        this.socket.on('robot_status_update', (data) => {
            this.updateRobotStatus(data);
        });

        this.socket.on('camera_status', (data) => {
            this.cameraEnabled = data.enabled;
            this.updateCameraStatus();
        });

        this.socket.on('control_ack', (data) => {
            if (!data.success) {
                this.showToast('Kontrol hatası: ' + data.error, 'error');
            }
        });
    }

    initEventListeners() {
        // Emergency stop button
        const emergencyBtn = document.getElementById('emergency-stop-btn');
        if (emergencyBtn) {
            emergencyBtn.addEventListener('click', () => this.emergencyStop());
        }

        // Clear emergency button
        const clearEmergencyBtn = document.getElementById('clear-emergency-btn');
        if (clearEmergencyBtn) {
            clearEmergencyBtn.addEventListener('click', () => this.clearEmergency());
        }

        // Speed slider
        const speedSlider = document.getElementById('speed-slider');
        if (speedSlider) {
            speedSlider.addEventListener('input', (e) => {
                this.currentSpeed = parseInt(e.target.value);
                this.updateSpeedDisplay();
            });
        }

        // Manual control toggle
        const manualToggle = document.getElementById('manual-control-toggle');
        if (manualToggle) {
            manualToggle.addEventListener('change', (e) => {
                this.toggleManualControl(e.target.checked);
            });
        }

        // Camera toggle
        const cameraToggle = document.getElementById('camera-toggle');
        if (cameraToggle) {
            cameraToggle.addEventListener('click', () => this.toggleCamera());
        }
    }

    initManualControl() {
        const controlPad = document.getElementById('movement-pad');
        const controlCenter = document.getElementById('movement-center');

        if (!controlPad || !controlCenter) return;

        let isDragging = false;
        let startX, startY, centerX, centerY;

        const padRect = controlPad.getBoundingClientRect();
        const padRadius = padRect.width / 2;

        // Mouse events
        controlCenter.addEventListener('mousedown', (e) => {
            if (!this.manualControlActive) return;

            isDragging = true;
            controlPad.classList.add('active');

            const rect = controlPad.getBoundingClientRect();
            centerX = rect.left + rect.width / 2;
            centerY = rect.top + rect.height / 2;

            startX = e.clientX;
            startY = e.clientY;

            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging || !this.manualControlActive) return;

            const deltaX = e.clientX - centerX;
            const deltaY = e.clientY - centerY;
            const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

            // Sınırla
            const maxDistance = padRadius - 30;
            let x = deltaX;
            let y = deltaY;

            if (distance > maxDistance) {
                const ratio = maxDistance / distance;
                x = deltaX * ratio;
                y = deltaY * ratio;
            }

            // Control center'ı hareket ettir
            controlCenter.style.transform = `translate(calc(-50% + ${x}px), calc(-50% + ${y}px))`;

            // Robot komutlarını hesapla
            const linear = -y / maxDistance; // İleri/geri
            const angular = -x / maxDistance; // Sol/sağ

            this.sendManualControl(linear, angular);
        });

        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                controlPad.classList.remove('active');
                controlCenter.style.transform = 'translate(-50%, -50%)';
                this.sendManualControl(0, 0); // Durdur
            }
        });

        // Touch events (mobile)
        controlCenter.addEventListener('touchstart', (e) => {
            if (!this.manualControlActive) return;

            const touch = e.touches[0];
            const mouseEvent = new MouseEvent('mousedown', {
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            controlCenter.dispatchEvent(mouseEvent);
            e.preventDefault();
        });

        document.addEventListener('touchmove', (e) => {
            if (!isDragging) return;

            const touch = e.touches[0];
            const mouseEvent = new MouseEvent('mousemove', {
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            document.dispatchEvent(mouseEvent);
            e.preventDefault();
        });

        document.addEventListener('touchend', (e) => {
            const mouseEvent = new MouseEvent('mouseup', {});
            document.dispatchEvent(mouseEvent);
            e.preventDefault();
        });
    }

    initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (!this.manualControlActive) return;

            let linear = 0, angular = 0;
            const speed = this.currentSpeed / 100;

            switch (e.key.toLowerCase()) {
                case 'w':
                case 'arrowup':
                    linear = speed;
                    break;
                case 's':
                case 'arrowdown':
                    linear = -speed;
                    break;
                case 'a':
                case 'arrowleft':
                    angular = speed;
                    break;
                case 'd':
                case 'arrowright':
                    angular = -speed;
                    break;
                case ' ':
                    this.emergencyStop();
                    e.preventDefault();
                    break;
                default:
                    return;
            }

            this.sendManualControl(linear, angular);
            e.preventDefault();
        });

        document.addEventListener('keyup', (e) => {
            if (!this.manualControlActive) return;

            if (['w', 's', 'a', 'd', 'arrowup', 'arrowdown', 'arrowleft', 'arrowright'].includes(e.key.toLowerCase())) {
                this.sendManualControl(0, 0);
                e.preventDefault();
            }
        });
    }

    sendManualControl(linear, angular) {
        if (!this.connected || !this.manualControlActive) return;

        const data = {
            linear: linear * (this.currentSpeed / 100),
            angular: angular * (this.currentSpeed / 100)
        };

        this.socket.emit('manual_control', data);
    }

    toggleManualControl(enabled) {
        this.manualControlActive = enabled;

        const controlPad = document.getElementById('movement-pad');
        if (controlPad) {
            controlPad.style.opacity = enabled ? '1' : '0.5';
            controlPad.style.pointerEvents = enabled ? 'auto' : 'none';
        }

        if (enabled) {
            this.showToast('Manuel kontrol aktif', 'info');
        } else {
            this.showToast('Manuel kontrol deaktif', 'info');
            this.sendManualControl(0, 0); // Durdur
        }
    }

    emergencyStop() {
        fetch('/api/emergency_stop', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.showToast('ACİL DURDURMA AKTİF!', 'error');
                    this.manualControlActive = false;
                    const toggle = document.getElementById('manual-control-toggle');
                    if (toggle) toggle.checked = false;
                    this.toggleManualControl(false);
                }
            })
            .catch(error => {
                console.error('Emergency stop hatası:', error);
                this.showToast('Acil durdurma hatası', 'error');
            });
    }

    clearEmergency() {
        fetch('/api/clear_emergency', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.showToast('Acil durdurma kaldırıldı', 'success');
                }
            })
            .catch(error => {
                console.error('Clear emergency hatası:', error);
                this.showToast('Emergency clear hatası', 'error');
            });
    }

    toggleCamera() {
        if (this.cameraEnabled) {
            this.socket.emit('stop_camera');
        } else {
            this.socket.emit('start_camera');
        }
    }

    updateConnectionStatus(connected) {
        const indicator = document.getElementById('connection-status');
        const text = document.getElementById('connection-text');

        if (indicator) {
            indicator.className = `status-indicator ${connected ? 'status-online' : 'status-offline'}`;
        }

        if (text) {
            text.textContent = connected ? 'Bağlı' : 'Bağlantı Kesildi';
        }
    }

    updateRobotStatus(status) {
        // Battery level
        if (status.power && status.power.battery_level !== undefined) {
            const batteryLevel = document.getElementById('battery-level');
            const batteryBar = document.getElementById('battery-bar');

            if (batteryLevel) {
                batteryLevel.textContent = status.power.battery_level.toFixed(1) + '%';
            }

            if (batteryBar) {
                batteryBar.style.width = status.power.battery_level + '%';

                // Renk değiştir
                if (status.power.battery_level < 20) {
                    batteryBar.className = 'progress-bar bg-danger';
                } else if (status.power.battery_level < 50) {
                    batteryBar.className = 'progress-bar bg-warning';
                } else {
                    batteryBar.className = 'progress-bar bg-success';
                }
            }
        }

        // Robot state
        if (status.main_controller && status.main_controller.state) {
            const stateElement = document.getElementById('robot-state');
            if (stateElement) {
                stateElement.textContent = status.main_controller.state;

                // Badge rengi
                stateElement.className = 'badge ' + this.getStateBadgeClass(status.main_controller.state);
            }
        }

        // Position
        if (status.main_controller && status.main_controller.position) {
            const posElement = document.getElementById('robot-position');
            if (posElement) {
                const pos = status.main_controller.position;
                posElement.textContent = `X: ${pos.x.toFixed(2)}, Y: ${pos.y.toFixed(2)}`;
            }
        }

        // Voltage and current
        if (status.power) {
            const voltageElement = document.getElementById('battery-voltage');
            const currentElement = document.getElementById('battery-current');

            if (voltageElement && status.power.voltage) {
                voltageElement.textContent = status.power.voltage.toFixed(1) + 'V';
            }

            if (currentElement && status.power.current) {
                currentElement.textContent = status.power.current.toFixed(2) + 'A';
            }
        }

        // Navigation progress
        if (status.navigation) {
            const progressElement = document.getElementById('progress-bar');
            const progressText = document.getElementById('progress');

            if (progressElement && status.navigation.progress !== undefined) {
                progressElement.style.width = status.navigation.progress + '%';
            }

            if (progressText && status.navigation.progress !== undefined) {
                progressText.textContent = status.navigation.progress.toFixed(1) + '%';
            }
        }
    }

    getStateBadgeClass(state) {
        const stateClasses = {
            'IDLE': 'bg-secondary',
            'MOWING': 'bg-success',
            'RETURNING': 'bg-info',
            'CHARGING': 'bg-warning',
            'EMERGENCY': 'bg-danger',
            'MANUAL': 'bg-primary'
        };

        return stateClasses[state] || 'bg-secondary';
    }

    updateSpeedDisplay() {
        const speedDisplay = document.getElementById('speed-value');
        if (speedDisplay) {
            speedDisplay.textContent = this.currentSpeed;
        }
    }

    updateCameraStatus() {
        const cameraBtn = document.getElementById('camera-toggle');
        const cameraImg = document.getElementById('camera-feed');

        if (cameraBtn) {
            cameraBtn.innerHTML = this.cameraEnabled ?
                '<i class="fas fa-camera-slash"></i> Kamera Kapat' :
                '<i class="fas fa-camera"></i> Kamera Aç';

            cameraBtn.className = this.cameraEnabled ?
                'btn btn-warning' : 'btn btn-primary';
        }

        if (cameraImg) {
            cameraImg.style.display = this.cameraEnabled ? 'block' : 'none';
        }
    }

    startPeriodicUpdates() {
        // Her 2 saniyede bir status güncelle
        setInterval(() => {
            if (this.connected) {
                fetch('/api/status')
                    .then(response => response.json())
                    .then(data => {
                        this.updateRobotStatus(data.robot);
                    })
                    .catch(error => {
                        console.error('Status update hatası:', error);
                    });
            }
        }, 2000);
    }

    showToast(message, type = 'info') {
        // Toast notification göster
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();

        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
        toast.setAttribute('role', 'alert');

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        toastContainer.appendChild(toast);

        // Bootstrap toast'ı göster
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        // Otomatik temizle
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(container);
        return container;
    }
}

// Global functions for HTML onclick events
function emergencyStop() {
    if (window.obaInterface) {
        window.obaInterface.emergencyStop();
    }
}

function clearEmergency() {
    if (window.obaInterface) {
        window.obaInterface.clearEmergency();
    }
}

function toggleCamera() {
    if (window.obaInterface) {
        window.obaInterface.toggleCamera();
    }
}

function toggleManualControl() {
    const toggle = document.getElementById('manual-control-toggle');
    if (window.obaInterface && toggle) {
        window.obaInterface.toggleManualControl(toggle.checked);
    }
}

function updateSpeed() {
    const slider = document.getElementById('speed-slider');
    if (window.obaInterface && slider) {
        window.obaInterface.currentSpeed = parseInt(slider.value);
        window.obaInterface.updateSpeedDisplay();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 DOM yüklendi, OBA interface başlatılıyor...');
    window.obaInterface = new OBAWebInterface();
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = OBAWebInterface;
}
