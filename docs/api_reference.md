# OBA Robot API Referansı

## Web API Endpoints

### Robot Kontrol API

#### POST /api/robot/start
Robot görevini başlatır.

**Request Body:**
```json
{
    "area_id": "alan1",
    "cutting_height": 5,
    "speed": 0.5
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Görev başlatıldı",
    "task_id": "task_20250627_143022"
}
```

#### POST /api/robot/stop
Robot görevini durdurur.

**Response:**
```json
{
    "status": "success",
    "message": "Robot durduruldu"
}
```

#### GET /api/robot/status
Robot durumunu getirir.

**Response:**
```json
{
    "state": "BIÇME",
    "position": {
        "x": 15.5,
        "y": 8.2,
        "heading": 45.0
    },
    "battery": {
        "level": 78,
        "voltage": 25.2,
        "current": 2.1,
        "time_remaining": "02:15:30"
    },
    "sensors": {
        "imu": {
            "temperature": 35,
            "calibration": "GOOD"
        },
        "encoders": {
            "left": 15420,
            "right": 15380
        }
    },
    "motors": {
        "left_track": {
            "speed": 0.3,
            "current": 1.2
        },
        "right_track": {
            "speed": 0.3,
            "current": 1.1
        },
        "cutting": {
            "speed": 2800,
            "current": 3.5
        }
    }
}
```

#### POST /api/robot/manual_control
Manuel kontrol komutları.

**Request Body:**
```json
{
    "command": "move",
    "direction": "forward",
    "speed": 0.2,
    "duration": 5.0
}
```

**Komut Türleri:**
- `move`: Hareket (forward, backward, left, right, stop)
- `cutting`: Biçme kontrolü (start, stop, height_up, height_down)
- `rotate`: Dönme (clockwise, counterclockwise)

### Navigasyon API

#### GET /api/navigation/position
Anlık konum bilgisi.

**Response:**
```json
{
    "position": {
        "x": 15.5,
        "y": 8.2,
        "heading": 45.0,
        "confidence": 0.95
    },
    "odometry": {
        "distance_traveled": 1250.5,
        "time_elapsed": "01:25:30"
    }
}
```

#### POST /api/navigation/goto
Belirli bir konuma git.

**Request Body:**
```json
{
    "target": {
        "x": 20.0,
        "y": 10.0,
        "heading": 90.0
    },
    "speed": 0.3
}
```

#### GET /api/navigation/path
Aktif rota bilgisi.

**Response:**
```json
{
    "current_path": [
        {"x": 15.5, "y": 8.2},
        {"x": 16.0, "y": 8.2},
        {"x": 16.5, "y": 8.2}
    ],
    "progress": 45.2,
    "estimated_completion": "00:35:15"
}
```

### Alan Yönetimi API

#### GET /api/areas
Tanımlı alanları listeler.

**Response:**
```json
{
    "areas": [
        {
            "id": "alan1",
            "name": "Doğu Bahçe",
            "bounds": [
                {"x": 0, "y": 0},
                {"x": 30, "y": 0},
                {"x": 30, "y": 20},
                {"x": 0, "y": 20}
            ],
            "area_m2": 600,
            "last_cut": "2025-06-25T14:30:00Z"
        }
    ]
}
```

#### POST /api/areas
Yeni alan tanımlar.

**Request Body:**
```json
{
    "name": "Yeni Alan",
    "bounds": [
        {"x": 0, "y": 0},
        {"x": 20, "y": 0},
        {"x": 20, "y": 15},
        {"x": 0, "y": 15}
    ]
}
```

### Güç Yönetimi API

#### GET /api/power/status
Güç durumu bilgisi.

**Response:**
```json
{
    "robot_battery": {
        "voltage": 25.2,
        "current": 2.1,
        "level": 78,
        "temperature": 32,
        "cycles": 45,
        "health": "GOOD"
    },
    "station_battery": {
        "voltage": 24.8,
        "current": 0.5,
        "level": 95,
        "solar_power": 120.5
    },
    "charging": false,
    "estimated_runtime": "02:15:30"
}
```

#### POST /api/power/charge
Şarj işlemini zorla başlat.

**Response:**
```json
{
    "status": "success",
    "message": "Şarj istasyonuna yönelim başladı"
}
```

### Sistem API

#### GET /api/system/info
Sistem bilgileri.

**Response:**
```json
{
    "version": "1.0.0",
    "uptime": "02:45:12",
    "cpu_usage": 45.2,
    "memory_usage": 62.1,
    "disk_usage": 28.5,
    "temperature": 58.2,
    "wifi_signal": -45
}
```

#### POST /api/system/shutdown
Sistemi güvenli şekilde kapat.

**Response:**
```json
{
    "status": "success",
    "message": "Sistem 30 saniye içinde kapanacak"
}
```

#### POST /api/system/restart
Sistemi yeniden başlat.

**Response:**
```json
{
    "status": "success",
    "message": "Sistem yeniden başlatılıyor"
}
```

## WebSocket API

### Real-time Veri Akışı

#### Bağlantı:
```javascript
const socket = io('http://robot-ip:5000');
```

#### Events:

##### 'robot_status'
Her saniye robot durumu gönderilir.
```json
{
    "timestamp": "2025-06-27T14:30:22Z",
    "state": "BIÇME",
    "position": {"x": 15.5, "y": 8.2, "heading": 45.0},
    "battery": 78,
    "speed": 0.3
}
```

##### 'camera_frame'
Kamera görüntüsü (Base64 encoded).
```json
{
    "timestamp": "2025-06-27T14:30:22.123Z",
    "frame": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
}
```

##### 'error'
Hata mesajları.
```json
{
    "timestamp": "2025-06-27T14:30:22Z",
    "level": "ERROR",
    "module": "motor_controller",
    "message": "Sol motor encoder yanıtı yok"
}
```

##### 'log'
Sistem logları.
```json
{
    "timestamp": "2025-06-27T14:30:22Z",
    "level": "INFO",
    "module": "main_controller",
    "message": "Görev başlatıldı: alan1"
}
```

#### Client Events:

##### 'manual_control'
Manuel kontrol komutları gönder.
```javascript
socket.emit('manual_control', {
    command: 'move',
    direction: 'forward',
    speed: 0.2
});
```

##### 'emergency_stop'
Acil durdurma.
```javascript
socket.emit('emergency_stop');
```

## Python API (Dahili Modüller)

### MainController Class

```python
from src.core.main_controller import MainController

controller = MainController()

# Robot durumunu başlat
controller.start()

# Durum değiştir
controller.set_state('BIÇME')

# Görev tanımla
controller.start_task(area_id='alan1', cutting_height=5)

# Durdur
controller.stop()
```

### KalmanOdometry Class

```python
from src.navigation.kalman_odometry import KalmanOdometry

odometry = KalmanOdometry()

# Enkoder verisi ekle
odometry.update_encoders(left_ticks=1024, right_ticks=1020)

# IMU verisi ekle
odometry.update_imu(accel=[0.1, 0.2, 9.8], gyro=[0.01, 0.02, 0.03])

# Konum al
position = odometry.get_position()
print(f"X: {position.x}, Y: {position.y}, Heading: {position.heading}")
```

### PathPlanner Class

```python
from src.navigation.path_planner import PathPlanner

planner = PathPlanner()

# Alan tanımla
area_bounds = [(0, 0), (30, 0), (30, 20), (0, 20)]
planner.set_work_area(area_bounds)

# Rota planla
path = planner.generate_mowing_pattern(
    cutting_width=0.5,
    overlap=0.1,
    pattern='boustrophedon'
)

# Sonraki hedef nokta al
next_point = planner.get_next_waypoint()
```

### MotorController Class

```python
from src.hardware.motor_controller import MotorController

motors = MotorController()

# İleri hareket
motors.move_forward(speed=0.3)

# Dönme
motors.turn_left(speed=0.2)

# Biçme motor kontrolü
motors.set_cutting_motor(rpm=2800)

# Yükseklik ayarı
motors.set_cutting_height(level=5)

# Durdur
motors.stop_all()
```

### PowerManager Class

```python
from src.hardware.power_manager import PowerManager

power = PowerManager()

# Batarya durumu
battery_info = power.get_battery_status()
print(f"Batarya: %{battery_info.level}")

# Şarj gerekli mi?
if power.should_charge():
    print("Şarj istasyonuna dönme zamanı!")

# Güç tüketim tahmini
estimated_time = power.estimate_runtime()
print(f"Kalan süre: {estimated_time} dakika")
```

## Hata Kodları

### HTTP Hata Kodları
- `400 Bad Request`: Geçersiz parametre
- `401 Unauthorized`: Kimlik doğrulama hatası
- `403 Forbidden`: İzin yok
- `404 Not Found`: Kaynak bulunamadı
- `409 Conflict`: Durum çakışması (örn: zaten çalışıyor)
- `500 Internal Server Error`: Sunucu hatası
- `503 Service Unavailable`: Servis kullanılamıyor

### Robot Hata Kodları
```json
{
    "error_code": "MOT001",
    "error_message": "Sol motor encoder yanıtı yok",
    "severity": "ERROR",
    "module": "motor_controller",
    "timestamp": "2025-06-27T14:30:22Z"
}
```

#### Hata Kod Kategorileri:
- **MOT001-099**: Motor hataları
- **NAV001-099**: Navigasyon hataları
- **POW001-099**: Güç hataları
- **SEN001-099**: Sensör hataları
- **COM001-099**: İletişim hataları
- **SYS001-099**: Sistem hataları

## Rate Limiting

API çağrıları rate limiting'e tabidir:
- **Robot Control**: 10 req/min
- **Status Queries**: 60 req/min
- **Manual Control**: 30 req/min
- **System Commands**: 5 req/min

## Authentication

API kimlik doğrulaması için JWT token kullanılır:

```bash
# Token alma
curl -X POST http://robot-ip:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# API çağrısında kullanım
curl -X GET http://robot-ip:5000/api/robot/status \
  -H "Authorization: Bearer <token>"
```

Bu API referansı ile robot sistemiyle etkileşimde bulunabilirsiniz.
