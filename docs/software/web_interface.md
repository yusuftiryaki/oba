# 🌐 Web Arayüzü Kullanım Kılavuzu

## 🎯 Arayüz Genel Bakışı

### Ana Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│ 🤖 OBA Robot Kontrol Paneli              🔋87%  📶WiFi    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│ │ 📊 Robot Durumu │  │ 🗺️ Harita        │  │ 📹 Canlı     │ │
│ │                 │  │ Görünümü        │  │ Kamera       │ │
│ │ Durum: Biçiyor  │  │                 │  │              │ │
│ │ Hız: 0.8 m/s    │  │     🤖          │  │  [STREAM]    │ │
│ │ Alan: %65       │  │                 │  │              │ │
│ │ Süre: 1:23:45   │  │                 │  │              │ │
│ └─────────────────┘  └─────────────────┘  └──────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🎮 Hızlı Kontroller                                    │ │
│ │                                                         │ │
│ │ [▶️ Başlat] [⏸️ Duraklat] [⏹️ Durdur] [🏠 Eve Dön]      │ │
│ │                                                         │ │
│ │ [⚙️ Ayarlar] [📋 Loglar] [🔧 Bakım] [❓ Yardım]        │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 📱 Responsive Tasarım

Arayüz tüm cihazlarda çalışır:
- **Masaüstü**: Tam özellikli dashboard
- **Tablet**: Optimize edilmiş dokunmatik arayüz
- **Telefon**: Kompakt mobil görünüm
- **TV/Projeksiyon**: Büyük ekran modu

## 🔐 Giriş ve Güvenlik

### İlk Giriş Kurulumu

```python
# İlk kurulum adımları
def first_time_setup():
    """İlk kurulum sihirbazı"""
    
    steps = [
        "🌐 WiFi ağı konfigürasyonu",
        "👤 Admin kullanıcı oluşturma", 
        "🗺️ Çalışma alanı tanımlama",
        "⚙️ Robot parametreleri ayarlama",
        "🧪 Sistem testi",
        "✅ Kurulum tamamlama"
    ]
    
    return steps

# Varsayılan giriş bilgileri
DEFAULT_CREDENTIALS = {
    "username": "admin",
    "password": "oba2024!",
    "change_required": True
}
```

### Kullanıcı Yönetimi

#### Kullanıcı Rolleri
- **Admin**: Tam sistem kontrolü
- **Operator**: Günlük işlemler
- **Viewer**: Sadece görüntüleme
- **Maintenance**: Bakım işlemleri

#### Güvenlik Özellikleri
```javascript
// Session yönetimi
const SESSION_CONFIG = {
    timeout: 30, // dakika
    auto_logout: true,
    secure_cookies: true,
    csrf_protection: true
};

// Şifre politikası
const PASSWORD_POLICY = {
    min_length: 8,
    require_uppercase: true,
    require_lowercase: true,
    require_numbers: true,
    require_symbols: true,
    expiry_days: 90
};
```

## 📊 Ana Dashboard

### Robot Durum Kartı

```html
<!-- Robot Status Widget -->
<div class="status-card">
    <div class="status-header">
        <h3>🤖 Robot Durumu</h3>
        <span class="status-badge" id="robot-status">ÇALIŞIYOR</span>
    </div>
    
    <div class="status-metrics">
        <div class="metric">
            <span class="metric-label">Konum</span>
            <span class="metric-value" id="position">X: 12.5m, Y: 8.3m</span>
        </div>
        
        <div class="metric">
            <span class="metric-label">Hız</span>
            <span class="metric-value" id="speed">0.8 m/s</span>
        </div>
        
        <div class="metric">
            <span class="metric-label">Yönelim</span>
            <span class="metric-value" id="heading">45°</span>
        </div>
        
        <div class="metric">
            <span class="metric-label">Çalışma Süresi</span>
            <span class="metric-value" id="runtime">1:23:45</span>
        </div>
    </div>
    
    <div class="progress-section">
        <label>Alan Tamamlanma (%)</label>
        <div class="progress-bar">
            <div class="progress-fill" style="width: 65%"></div>
        </div>
        <span class="progress-text">65%</span>
    </div>
</div>
```

### Batarya ve Güç Monitörü

```javascript
// Batarya durumu güncelleme
function updateBatteryStatus() {
    fetch('/api/battery/status')
        .then(response => response.json())
        .then(data => {
            const batteryLevel = data.level;
            const voltage = data.voltage;
            const current = data.current;
            const timeRemaining = data.time_remaining;
            
            // Batarya göstergesi güncelle
            document.getElementById('battery-level').textContent = `${batteryLevel}%`;
            document.getElementById('battery-voltage').textContent = `${voltage}V`;
            document.getElementById('battery-current').textContent = `${current}A`;
            document.getElementById('time-remaining').textContent = timeRemaining;
            
            // Renk kodlaması
            const batteryBar = document.getElementById('battery-bar');
            if (batteryLevel > 50) {
                batteryBar.className = 'battery-bar battery-good';
            } else if (batteryLevel > 20) {
                batteryBar.className = 'battery-bar battery-warning';
            } else {
                batteryBar.className = 'battery-bar battery-critical';
            }
            
            // Uyarı kontrolleri
            if (batteryLevel < 20) {
                showNotification('⚠️ Düşük Batarya!', 'warning');
            }
        });
}

// Her 5 saniyede güncelle
setInterval(updateBatteryStatus, 5000);
```

### Real-time Harita Görünümü

```javascript
// Leaflet.js ile interaktif harita
class RobotMap {
    constructor(containerId) {
        this.map = L.map(containerId).setView([0, 0], 18);
        this.robotMarker = null;
        this.pathPolyline = null;
        this.workArea = null;
        
        // Özel robot ikonu
        this.robotIcon = L.icon({
            iconUrl: '/static/images/robot-icon.png',
            iconSize: [32, 32],
            iconAnchor: [16, 16]
        });
        
        this.initializeMap();
    }
    
    initializeMap() {
        // Basemap (OpenStreetMap veya özel)
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 20,
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);
        
        // Grid overlay
        this.addGridOverlay();
        
        // Event listeners
        this.map.on('click', this.onMapClick.bind(this));
    }
    
    updateRobotPosition(x, y, heading) {
        if (this.robotMarker) {
            this.robotMarker.setLatLng([y, x]);
            this.robotMarker.setRotationAngle(heading * 180 / Math.PI);
        } else {
            this.robotMarker = L.marker([y, x], {
                icon: this.robotIcon,
                rotationAngle: heading * 180 / Math.PI
            }).addTo(this.map);
        }
        
        // Haritayı robot konumunda merkezle
        this.map.setView([y, x], this.map.getZoom());
    }
    
    updatePath(pathPoints) {
        if (this.pathPolyline) {
            this.map.removeLayer(this.pathPolyline);
        }
        
        // Yolu çiz
        this.pathPolyline = L.polyline(pathPoints, {
            color: 'blue',
            weight: 3,
            opacity: 0.7
        }).addTo(this.map);
    }
    
    setWorkArea(areaPoints) {
        if (this.workArea) {
            this.map.removeLayer(this.workArea);
        }
        
        // Çalışma alanını çiz
        this.workArea = L.polygon(areaPoints, {
            color: 'green',
            weight: 2,
            fillColor: 'lightgreen',
            fillOpacity: 0.3
        }).addTo(this.map);
        
        // Haritayı alan sınırlarına fit et
        this.map.fitBounds(this.workArea.getBounds());
    }
    
    onMapClick(e) {
        // Tıklanan noktaya go-to komutu gönder
        const lat = e.latlng.lat;
        const lng = e.latlng.lng;
        
        if (confirm(`Robotu (${lng.toFixed(2)}, ${lat.toFixed(2)}) koordinatına gönder?`)) {
            this.sendGoToCommand(lng, lat);
        }
    }
    
    sendGoToCommand(x, y) {
        fetch('/api/navigation/goto', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                target_x: x,
                target_y: y
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('✅ Go-to komutu gönderildi', 'success');
            } else {
                showNotification('❌ Komut gönderilemedi: ' + data.error, 'error');
            }
        });
    }
}

// Harita örneği oluştur
const robotMap = new RobotMap('map-container');
```

## 🎮 Manuel Kontrol Arayüzü

### Joystick Kontrolü

```html
<!-- Manuel Kontrol Paneli -->
<div class="manual-control-panel">
    <div class="control-header">
        <h3>🎮 Manuel Kontrol</h3>
        <button id="manual-mode-toggle" class="btn btn-warning">
            Manuel Moda Geç
        </button>
    </div>
    
    <div class="joystick-container">
        <div id="movement-joystick" class="joystick">
            <div class="joystick-knob"></div>
        </div>
        <label>Hareket Kontrolü</label>
    </div>
    
    <div class="speed-control">
        <label>Hız Limiti (%)</label>
        <input type="range" id="speed-slider" min="10" max="100" value="50">
        <span id="speed-value">50%</span>
    </div>
    
    <div class="mower-control">
        <label>Biçme Motoru</label>
        <button id="mower-toggle" class="btn btn-success">Başlat</button>
        <input type="range" id="mower-speed" min="0" max="100" value="70">
        <span id="mower-speed-value">70%</span>
    </div>
</div>
```

```javascript
// Joystick kontrolü implementasyonu
class JoystickController {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.knob = this.container.querySelector('.joystick-knob');
        this.isDragging = false;
        this.centerX = 0;
        this.centerY = 0;
        this.maxRadius = 0;
        
        this.setupEventListeners();
        this.updateDimensions();
    }
    
    setupEventListeners() {
        // Mouse events
        this.knob.addEventListener('mousedown', this.startDrag.bind(this));
        document.addEventListener('mousemove', this.drag.bind(this));
        document.addEventListener('mouseup', this.endDrag.bind(this));
        
        // Touch events
        this.knob.addEventListener('touchstart', this.startDrag.bind(this));
        document.addEventListener('touchmove', this.drag.bind(this));
        document.addEventListener('touchend', this.endDrag.bind(this));
        
        // Window resize
        window.addEventListener('resize', this.updateDimensions.bind(this));
    }
    
    updateDimensions() {
        const rect = this.container.getBoundingClientRect();
        this.centerX = rect.width / 2;
        this.centerY = rect.height / 2;
        this.maxRadius = Math.min(rect.width, rect.height) / 2 - 20;
    }
    
    startDrag(e) {
        this.isDragging = true;
        e.preventDefault();
    }
    
    drag(e) {
        if (!this.isDragging) return;
        
        const rect = this.container.getBoundingClientRect();
        const clientX = e.clientX || e.touches[0].clientX;
        const clientY = e.clientY || e.touches[0].clientY;
        
        const deltaX = clientX - rect.left - this.centerX;
        const deltaY = clientY - rect.top - this.centerY;
        
        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
        const limitedDistance = Math.min(distance, this.maxRadius);
        
        const angle = Math.atan2(deltaY, deltaX);
        const x = limitedDistance * Math.cos(angle);
        const y = limitedDistance * Math.sin(angle);
        
        // Joystick knob pozisyonunu güncelle
        this.knob.style.transform = `translate(${x}px, ${y}px)`;
        
        // Robot komutlarını hesapla
        const normalizedX = x / this.maxRadius;
        const normalizedY = -y / this.maxRadius; // Y eksenini ters çevir
        
        this.sendMovementCommand(normalizedX, normalizedY);
    }
    
    endDrag() {
        this.isDragging = false;
        
        // Joystick'i merkeze döndür
        this.knob.style.transform = 'translate(0px, 0px)';
        
        // Robot durdur
        this.sendMovementCommand(0, 0);
    }
    
    sendMovementCommand(x, y) {
        // Joystick değerlerini robot hızlarına çevir
        const maxSpeed = document.getElementById('speed-slider').value / 100;
        
        // Arcade drive algoritması
        const linear = y * maxSpeed;
        const angular = x * maxSpeed * 2; // Dönüş hızı çarpanı
        
        // Robot komutunu gönder
        fetch('/api/control/manual_drive', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                linear_velocity: linear,
                angular_velocity: angular
            })
        })
        .catch(error => {
            console.error('Manuel kontrol hatası:', error);
        });
    }
}

// Joystick kontrolcüsünü başlat
const joystick = new JoystickController('movement-joystick');
```

### Klavye Kısayolları

```javascript
// Klavye kontrolleri
document.addEventListener('keydown', function(e) {
    // Sadece manuel modda çalış
    if (!isManualMode()) return;
    
    const speed = 0.5; // m/s
    const turn_speed = 1.0; // rad/s
    
    switch(e.key) {
        case 'ArrowUp':
        case 'w':
        case 'W':
            sendMovementCommand(speed, 0);
            break;
            
        case 'ArrowDown':
        case 's':
        case 'S':
            sendMovementCommand(-speed, 0);
            break;
            
        case 'ArrowLeft':
        case 'a':
        case 'A':
            sendMovementCommand(0, turn_speed);
            break;
            
        case 'ArrowRight':
        case 'd':
        case 'D':
            sendMovementCommand(0, -turn_speed);
            break;
            
        case ' ': // Space - Acil durdurma
            emergencyStop();
            e.preventDefault();
            break;
            
        case 'm':
        case 'M':
            toggleMowerMotor();
            break;
    }
});

// Tuş bırakıldığında dur
document.addEventListener('keyup', function(e) {
    if (!isManualMode()) return;
    
    if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 
         'w', 'W', 's', 'S', 'a', 'A', 'd', 'D'].includes(e.key)) {
        sendMovementCommand(0, 0);
    }
});
```

## ⚙️ Ayarlar Menüsü

### Robot Parametreleri

```html
<!-- Ayarlar Paneli -->
<div class="settings-panel">
    <div class="settings-section">
        <h4>🚀 Hareket Parametreleri</h4>
        
        <div class="setting-item">
            <label>Maksimum Hız (m/s)</label>
            <input type="number" id="max-speed" min="0.1" max="2.0" step="0.1" value="1.0">
        </div>
        
        <div class="setting-item">
            <label>Dönüş Hızı (rad/s)</label>
            <input type="number" id="turn-speed" min="0.1" max="3.0" step="0.1" value="1.5">
        </div>
        
        <div class="setting-item">
            <label>Hızlanma Rampa (%/s)</label>
            <input type="number" id="acceleration" min="10" max="100" step="5" value="50">
        </div>
    </div>
    
    <div class="settings-section">
        <h4>🌱 Biçme Parametreleri</h4>
        
        <div class="setting-item">
            <label>Biçme Yüksekliği (mm)</label>
            <input type="range" id="cutting-height" min="30" max="80" value="50">
            <span id="cutting-height-value">50mm</span>
        </div>
        
        <div class="setting-item">
            <label>Biçme Hızı (%)</label>
            <input type="range" id="mowing-speed" min="50" max="100" value="75">
            <span id="mowing-speed-value">75%</span>
        </div>
        
        <div class="setting-item">
            <label>Overlap Oranı (%)</label>
            <input type="range" id="overlap-ratio" min="5" max="30" value="10">
            <span id="overlap-ratio-value">10%</span>
        </div>
    </div>
    
    <div class="settings-section">
        <h4>🔋 Güç Yönetimi</h4>
        
        <div class="setting-item">
            <label>Düşük Batarya Seviyesi (%)</label>
            <input type="number" id="low-battery" min="10" max="50" value="20">
        </div>
        
        <div class="setting-item">
            <label>Şarj İstasyonuna Dönüş (%)</label>
            <input type="number" id="return-battery" min="15" max="30" value="25">
        </div>
        
        <div class="setting-item">
            <label>Eco Mode</label>
            <input type="checkbox" id="eco-mode">
            <span class="checkbox-label">Enerji tasarrufu modu</span>
        </div>
    </div>
    
    <div class="settings-actions">
        <button id="save-settings" class="btn btn-primary">💾 Kaydet</button>
        <button id="reset-settings" class="btn btn-secondary">🔄 Varsayılana Döndür</button>
        <button id="export-settings" class="btn btn-info">📤 Ayarları Dışa Aktar</button>
    </div>
</div>
```

### Alan Yönetimi

```javascript
// Alan tanımlama arayüzü
class AreaManager {
    constructor(mapInstance) {
        this.map = mapInstance;
        this.drawingMode = false;
        this.currentArea = null;
        this.areas = [];
        
        this.setupDrawingTools();
    }
    
    setupDrawingTools() {
        // Çizim araçları ekle
        this.drawControl = new L.Control.Draw({
            draw: {
                polygon: {
                    allowIntersection: false,
                    drawError: {
                        color: '#e1e100',
                        message: 'Çizgiler kesişemez!'
                    },
                    shapeOptions: {
                        color: 'blue',
                        weight: 2
                    }
                },
                polyline: false,
                rectangle: true,
                circle: false,
                marker: false,
                circlemarker: false
            },
            edit: {
                featureGroup: this.drawnItems
            }
        });
        
        this.map.addControl(this.drawControl);
        
        // Event listeners
        this.map.on('draw:created', this.onAreaCreated.bind(this));
        this.map.on('draw:edited', this.onAreaEdited.bind(this));
        this.map.on('draw:deleted', this.onAreaDeleted.bind(this));
    }
    
    onAreaCreated(e) {
        const layer = e.layer;
        const type = e.layerType;
        
        // Alan adı sor
        const areaName = prompt('Alan adını girin:', `Alan ${this.areas.length + 1}`);
        if (!areaName) return;
        
        // Alan bilgilerini kaydet
        const area = {
            id: Date.now(),
            name: areaName,
            type: type,
            coordinates: this.getLayerCoordinates(layer),
            area_m2: this.calculateArea(layer),
            created: new Date().toISOString()
        };
        
        this.areas.push(area);
        this.drawnItems.addLayer(layer);
        
        // Popup ekle
        layer.bindPopup(`
            <b>${area.name}</b><br>
            Alan: ${area.area_m2.toFixed(1)} m²<br>
            <button onclick="areaManager.editArea(${area.id})">Düzenle</button>
            <button onclick="areaManager.deleteArea(${area.id})">Sil</button>
            <button onclick="areaManager.startMowing(${area.id})">Biç</button>
        `);
        
        // Sunucuya kaydet
        this.saveAreaToServer(area);
        
        showNotification(`✅ ${areaName} alanı oluşturuldu`, 'success');
    }
    
    startMowing(areaId) {
        const area = this.areas.find(a => a.id === areaId);
        if (!area) return;
        
        if (confirm(`${area.name} alanında biçme işlemi başlatılsın mı?`)) {
            fetch('/api/tasks/start_mowing', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    area_id: areaId,
                    area_coordinates: area.coordinates
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('🌱 Biçme görevi başlatıldı', 'success');
                } else {
                    showNotification('❌ Görev başlatılamadı: ' + data.error, 'error');
                }
            });
        }
    }
    
    calculateArea(layer) {
        // Polygon alanını hesapla (m²)
        if (layer instanceof L.Polygon) {
            const latlngs = layer.getLatLngs()[0];
            return L.GeometryUtil.geodesicArea(latlngs);
        } else if (layer instanceof L.Rectangle) {
            const bounds = layer.getBounds();
            const ne = bounds.getNorthEast();
            const sw = bounds.getSouthWest();
            const width = L.latLng(sw.lat, ne.lng).distanceTo(L.latLng(sw.lat, sw.lng));
            const height = L.latLng(ne.lat, sw.lng).distanceTo(L.latLng(sw.lat, sw.lng));
            return width * height;
        }
        return 0;
    }
}
```

## 📊 İstatistikler ve Raporlar

### Performans Dashboard'u

```javascript
// İstatistik widget'ları
class StatsDashboard {
    constructor() {
        this.charts = {};
        this.initializeCharts();
        this.startRealTimeUpdates();
    }
    
    initializeCharts() {
        // Batarya grafiği
        this.charts.battery = new Chart(document.getElementById('battery-chart'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Batarya Seviyesi (%)',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        min: 0,
                        max: 100
                    }
                }
            }
        });
        
        // Hız grafiği
        this.charts.speed = new Chart(document.getElementById('speed-chart'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Hız (m/s)',
                    data: [],
                    borderColor: 'rgb(255, 99, 132)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        min: 0,
                        max: 2
                    }
                }
            }
        });
        
        // Alan coverage grafiği
        this.charts.coverage = new Chart(document.getElementById('coverage-chart'), {
            type: 'doughnut',
            data: {
                labels: ['Tamamlanan', 'Kalan'],
                datasets: [{
                    data: [0, 100],
                    backgroundColor: ['#4CAF50', '#E0E0E0']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    updateCharts(data) {
        const now = new Date().toLocaleTimeString();
        
        // Batarya chart güncelle
        this.addDataPoint(this.charts.battery, now, data.battery_level);
        
        // Hız chart güncelle
        this.addDataPoint(this.charts.speed, now, data.current_speed);
        
        // Coverage chart güncelle
        this.charts.coverage.data.datasets[0].data = [
            data.coverage_percentage,
            100 - data.coverage_percentage
        ];
        this.charts.coverage.update();
    }
    
    addDataPoint(chart, label, value) {
        chart.data.labels.push(label);
        chart.data.datasets[0].data.push(value);
        
        // Son 20 veri noktasını tut
        if (chart.data.labels.length > 20) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }
        
        chart.update();
    }
    
    startRealTimeUpdates() {
        setInterval(() => {
            fetch('/api/stats/realtime')
                .then(response => response.json())
                .then(data => this.updateCharts(data));
        }, 5000);
    }
}

// Stats dashboard'u başlat
const statsDashboard = new StatsDashboard();
```

---

**🎯 Hacı Abi Notu:** Web arayüzü robotun yüzü gibi, güzel ve kullanışlı yapmazsan kimse sevmez! Responsive tasarım yap, mobilde de çalışsın. Real-time güncellemeler için WebSocket kullan, sürekli refresh yapma. Güvenlik önlemlerini es geçme, authentication ve authorization şart. Joystick kontrolünde debounce uygula, spam komut gönderme. Error handling'i iyi yap, kullanıcıya anlayabileceği mesajlar ver! 🌐🎨
