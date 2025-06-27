# 🏗️ Kod Mimarisi ve Modül Yapısı

## 📊 Genel Sistem Mimarisi

### Katmanlı Mimari Yaklaşımı

```
    ┌─────────────────────────────────────────┐
    │             Web Interface Layer         │
    │    Flask Web Server + REST API         │
    └─────────────────┬───────────────────────┘
                      │
    ┌─────────────────┴───────────────────────┐
    │          Application Layer              │
    │   Main Controller + State Machine       │
    └─────────────────┬───────────────────────┘
                      │
    ┌─────────────────┴───────────────────────┐
    │            Service Layer                │
    │  Navigation + Planning + Safety         │
    └─────────────────┬───────────────────────┘
                      │
    ┌─────────────────┴───────────────────────┐
    │           Hardware Layer                │
    │   Motors + Sensors + Power Management   │
    └─────────────────────────────────────────┘
```

### 🗂️ Proje Klasör Yapısı

```
src/
├── 📁 core/                    # Ana kontrol katmanı
│   ├── main_controller.py      # Ana durum makinesi
│   ├── state_machine.py        # Durum geçiş mantığı
│   ├── robot_config.py         # Konfigürasyon yöneticisi
│   └── event_manager.py        # Olay yönetim sistemi
│
├── 📁 navigation/              # Navigasyon sistemi
│   ├── kalman_odometry.py      # Konum takip algoritması
│   ├── path_planner.py         # Rota planlama
│   ├── obstacle_avoidance.py   # Engel kaçınma
│   ├── docking_controller.py   # Şarj istasyonu yaklaşma
│   └── localization.py         # Konum belirleme
│
├── 📁 hardware/                # Donanım soyutlama katmanı
│   ├── motor_controller.py     # Motor kontrolü
│   ├── sensor_interface.py     # Sensör okuma
│   ├── power_manager.py        # Güç yönetimi
│   ├── gpio_manager.py         # GPIO soyutlama
│   └── camera_interface.py     # Kamera kontrolü
│
├── 📁 web/                     # Web arayüzü
│   ├── web_server.py           # Flask uygulaması
│   ├── api_endpoints.py        # REST API tanımları
│   ├── websocket_handler.py    # Real-time iletişim
│   ├── templates/              # HTML şablonları
│   └── static/                 # CSS, JS, images
│
├── 📁 algorithms/              # Algoritmalar
│   ├── kalman_filter.py        # Kalman filtresi
│   ├── pid_controller.py       # PID kontrolcü
│   ├── path_planning/          # Path planning algoritmaları
│   │   ├── rrt_star.py         # RRT* algoritması
│   │   ├── a_star.py           # A* algoritması
│   │   └── coverage_planner.py # Alan kaplama planlama
│   └── mapping/                # Haritalama
│       ├── grid_map.py         # Grid tabanlı harita
│       └── occupancy_grid.py   # Occupancy grid
│
├── 📁 safety/                  # Güvenlik sistemleri
│   ├── safety_manager.py       # Ana güvenlik denetleyici
│   ├── emergency_stop.py       # Acil durdurma
│   ├── collision_detection.py  # Çarpışma algılama
│   └── system_monitor.py       # Sistem sağlık izleme
│
├── 📁 utils/                   # Yardımcı araçlar
│   ├── logger.py               # Logging sistemi
│   ├── config_parser.py        # Konfigürasyon okuma
│   ├── math_utils.py           # Matematik fonksiyonları
│   ├── communication.py        # İletişim araçları
│   └── data_structures.py      # Veri yapıları
│
└── 📁 tests/                   # Test kodları
    ├── unit_tests/             # Birim testler
    ├── integration_tests/      # Entegrasyon testleri
    ├── hardware_tests/         # Donanım testleri
    └── simulation/             # Simülasyon testleri
```

## 🧩 Modül Detayları ve Bağımlılıklar

### Core Modülü

#### main_controller.py - Ana Kontrolcü
```python
"""
Ana robot kontrolcüsü - Hacı Abi'nin beyni!
"""

from typing import Dict, Any
from enum import Enum
import asyncio
import logging

class RobotState(Enum):
    """Robot durumları"""
    IDLE = "idle"
    NAVIGATING = "navigating"
    MOWING = "mowing"
    CHARGING = "charging"
    ERROR = "error"
    EMERGENCY = "emergency"

class MainController:
    """Ana robot kontrolcüsü"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.current_state = RobotState.IDLE
        self.logger = logging.getLogger(__name__)
        
        # Alt sistemleri başlat
        self._initialize_subsystems()
        
    def _initialize_subsystems(self):
        """Alt sistemleri başlat"""
        from navigation.kalman_odometry import KalmanOdometry
        from hardware.motor_controller import MotorController
        from safety.safety_manager import SafetyManager
        
        self.odometry = KalmanOdometry(self.config['navigation'])
        self.motors = MotorController(self.config['motors'])
        self.safety = SafetyManager(self.config['safety'])
        
        self.logger.info("🤖 Alt sistemler başlatıldı")
        
    async def run_main_loop(self):
        """Ana çalışma döngüsü"""
        self.logger.info("🚀 Ana döngü başlatılıyor...")
        
        while True:
            try:
                # Güvenlik kontrolü - her döngüde!
                if not self.safety.is_system_safe():
                    await self._handle_emergency()
                    continue
                
                # Durum makinesini çalıştır
                await self._execute_current_state()
                
                # Döngü bekleme süresi
                await asyncio.sleep(0.1)  # 10Hz ana döngü
                
            except Exception as e:
                self.logger.error(f"❌ Ana döngü hatası: {e}")
                await self._handle_error(e)
                
    async def _execute_current_state(self):
        """Mevcut duruma göre işlem yap"""
        state_handlers = {
            RobotState.IDLE: self._handle_idle_state,
            RobotState.NAVIGATING: self._handle_navigation_state,
            RobotState.MOWING: self._handle_mowing_state,
            RobotState.CHARGING: self._handle_charging_state,
            RobotState.ERROR: self._handle_error_state
        }
        
        handler = state_handlers.get(self.current_state)
        if handler:
            await handler()
        else:
            self.logger.warning(f"⚠️ Bilinmeyen durum: {self.current_state}")
```

#### state_machine.py - Durum Makinesi
```python
"""
Robot durum makinesi - Karar verme merkezi
"""

import asyncio
from typing import Dict, Callable, Optional
from enum import Enum

class StateTransition:
    """Durum geçiş tanımı"""
    
    def __init__(self, from_state: str, to_state: str, 
                 condition: Callable, action: Optional[Callable] = None):
        self.from_state = from_state
        self.to_state = to_state
        self.condition = condition
        self.action = action

class StateMachine:
    """Genel amaçlı durum makinesi"""
    
    def __init__(self, initial_state: str):
        self.current_state = initial_state
        self.transitions: Dict[str, list] = {}
        self.state_handlers: Dict[str, Callable] = {}
        self.history = []
        
    def add_transition(self, transition: StateTransition):
        """Durum geçişi ekle"""
        if transition.from_state not in self.transitions:
            self.transitions[transition.from_state] = []
        self.transitions[transition.from_state].append(transition)
        
    def set_state_handler(self, state: str, handler: Callable):
        """Durum işleyici tanımla"""
        self.state_handlers[state] = handler
        
    async def update(self):
        """Durum makinesini güncelle"""
        # Mevcut durumun işleyicisini çalıştır
        if self.current_state in self.state_handlers:
            await self.state_handlers[self.current_state]()
            
        # Geçiş koşullarını kontrol et
        if self.current_state in self.transitions:
            for transition in self.transitions[self.current_state]:
                if await transition.condition():
                    await self._execute_transition(transition)
                    break
                    
    async def _execute_transition(self, transition: StateTransition):
        """Durum geçişini gerçekleştir"""
        old_state = self.current_state
        
        # Geçiş eylemi varsa çalıştır
        if transition.action:
            await transition.action()
            
        # Yeni duruma geç
        self.current_state = transition.to_state
        self.history.append((old_state, self.current_state))
        
        print(f"🔄 Durum geçişi: {old_state} → {self.current_state}")

# Robot için özel durum makinesi
class RobotStateMachine(StateMachine):
    """Robot durum makinesi"""
    
    def __init__(self, robot_controller):
        super().__init__("IDLE")
        self.robot = robot_controller
        self._setup_robot_transitions()
        
    def _setup_robot_transitions(self):
        """Robot durum geçişlerini tanımla"""
        
        # IDLE → MOWING
        self.add_transition(StateTransition(
            "IDLE", "MOWING",
            condition=self._check_mowing_command,
            action=self._start_mowing
        ))
        
        # MOWING → CHARGING 
        self.add_transition(StateTransition(
            "MOWING", "CHARGING",
            condition=self._check_low_battery,
            action=self._start_charging
        ))
        
        # CHARGING → IDLE
        self.add_transition(StateTransition(
            "CHARGING", "IDLE", 
            condition=self._check_battery_full,
            action=self._finish_charging
        ))
        
        # Herhangi bir durum → EMERGENCY
        for state in ["IDLE", "MOWING", "CHARGING"]:
            self.add_transition(StateTransition(
                state, "EMERGENCY",
                condition=self._check_emergency,
                action=self._handle_emergency
            ))
            
    async def _check_mowing_command(self) -> bool:
        """Biçme komutu var mı kontrol et"""
        return self.robot.has_pending_mowing_task()
        
    async def _check_low_battery(self) -> bool:
        """Batarya düşük mü kontrol et"""
        battery_level = self.robot.get_battery_level()
        return battery_level < 20  # %20 altı
        
    async def _check_battery_full(self) -> bool:
        """Batarya dolu mu kontrol et"""
        battery_level = self.robot.get_battery_level()
        return battery_level > 95  # %95 üstü
        
    async def _check_emergency(self) -> bool:
        """Acil durum var mı kontrol et"""
        return self.robot.safety.has_emergency()
```

### Navigation Modülü

#### kalman_odometry.py - Konum Takip
```python
"""
Kalman Filtreli Odometri - GPS'siz konum takibi
"""

import numpy as np
import time
from typing import Tuple, Optional

class KalmanOdometry:
    """Kalman filtreli odometri sistemi"""
    
    def __init__(self, config: dict):
        self.config = config
        
        # Durum vektörü: [x, y, theta, vx, vy, omega]
        self.state = np.zeros(6)
        
        # Kovaryans matrisi
        self.P = np.eye(6) * 0.1
        
        # Süreç gürültüsü matrisi
        self.Q = np.diag([0.01, 0.01, 0.01, 0.1, 0.1, 0.1])
        
        # Ölçüm gürültüsü matrisi  
        self.R = np.diag([0.05, 0.05, 0.02])  # [encoder_L, encoder_R, IMU]
        
        # Robot parametreleri
        self.wheel_base = config.get('wheel_base', 0.54)  # metre
        self.wheel_radius = config.get('wheel_radius', 0.1)  # metre
        
        self.last_time = time.time()
        self.last_encoder_left = 0
        self.last_encoder_right = 0
        
    def predict(self, dt: float):
        """Tahmin adımı (süreç modeli)"""
        
        # Durum geçiş matrisi
        F = np.array([
            [1, 0, 0, dt, 0,  0],
            [0, 1, 0, 0,  dt, 0],
            [0, 0, 1, 0,  0,  dt],
            [0, 0, 0, 1,  0,  0],
            [0, 0, 0, 0,  1,  0],
            [0, 0, 0, 0,  0,  1]
        ])
        
        # Durum tahmini
        self.state = F @ self.state
        
        # Kovaryans güncellemesi
        self.P = F @ self.P @ F.T + self.Q
        
    def update(self, encoder_left: int, encoder_right: int, 
               imu_heading: float) -> Tuple[float, float, float]:
        """Güncelleme adımı (ölçüm modeli)"""
        
        current_time = time.time()
        dt = current_time - self.last_time
        
        if dt > 0:
            # Tahmin adımı
            self.predict(dt)
            
            # Enkoder verilerinden hız hesapla
            d_left = (encoder_left - self.last_encoder_left) * self.wheel_radius
            d_right = (encoder_right - self.last_encoder_right) * self.wheel_radius
            
            # Robot hızları
            linear_vel = (d_left + d_right) / (2 * dt)
            angular_vel = (d_right - d_left) / (self.wheel_base * dt)
            
            # Ölçüm vektörü
            z = np.array([d_left/dt, d_right/dt, imu_heading])
            
            # Beklenen ölçüm
            h = np.array([
                self.state[3] - self.state[5] * self.wheel_base / 2,  # sol tekerlek hızı
                self.state[3] + self.state[5] * self.wheel_base / 2,  # sağ tekerlek hızı  
                self.state[2]  # heading
            ])
            
            # Ölçüm Jacobian'ı
            H = np.array([
                [0, 0, 0, 1, 0, -self.wheel_base/2],
                [0, 0, 0, 1, 0, +self.wheel_base/2],
                [0, 0, 1, 0, 0, 0]
            ])
            
            # Kalman gain
            S = H @ self.P @ H.T + self.R
            K = self.P @ H.T @ np.linalg.inv(S)
            
            # Durum güncellemesi
            y = z - h  # innovation
            self.state = self.state + K @ y
            
            # Kovaryans güncellemesi
            I = np.eye(6)
            self.P = (I - K @ H) @ self.P
            
            # Heading açısını [-π, π] aralığında tut
            self.state[2] = np.arctan2(np.sin(self.state[2]), np.cos(self.state[2]))
            
        # Değerleri güncelle
        self.last_time = current_time
        self.last_encoder_left = encoder_left
        self.last_encoder_right = encoder_right
        
        return self.state[0], self.state[1], self.state[2]  # x, y, theta
        
    def get_pose(self) -> Tuple[float, float, float]:
        """Mevcut pozisyonu döndür"""
        return self.state[0], self.state[1], self.state[2]
        
    def get_velocity(self) -> Tuple[float, float, float]:
        """Mevcut hızları döndür"""
        return self.state[3], self.state[4], self.state[5]
        
    def reset_pose(self, x: float = 0, y: float = 0, theta: float = 0):
        """Pozisyonu sıfırla"""
        self.state[0] = x
        self.state[1] = y
        self.state[2] = theta
        self.P = np.eye(6) * 0.1  # Kovaryansı sıfırla
```

### Hardware Modülü

#### motor_controller.py - Motor Kontrolü
```python
"""
Motor kontrolcü - Robotun kasları
"""

import RPi.GPIO as GPIO
import time
import threading
from typing import Tuple, Optional

class MotorController:
    """3 motorlu sistem kontrolcüsü"""
    
    def __init__(self, config: dict):
        self.config = config
        
        # GPIO pin tanımları
        self.LEFT_PWM = config['pins']['left_pwm']
        self.LEFT_DIR = config['pins']['left_dir']
        self.RIGHT_PWM = config['pins']['right_pwm']
        self.RIGHT_DIR = config['pins']['right_dir']
        self.MOWER_PWM = config['pins']['mower_pwm']
        self.MOWER_DIR = config['pins']['mower_dir']
        
        # GPIO kurulumu
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([self.LEFT_PWM, self.LEFT_DIR, 
                   self.RIGHT_PWM, self.RIGHT_DIR,
                   self.MOWER_PWM, self.MOWER_DIR], GPIO.OUT)
        
        # PWM objelerini oluştur
        self.left_pwm = GPIO.PWM(self.LEFT_PWM, 20000)   # 20kHz
        self.right_pwm = GPIO.PWM(self.RIGHT_PWM, 20000)
        self.mower_pwm = GPIO.PWM(self.MOWER_PWM, 20000)
        
        # PWM'leri başlat
        self.left_pwm.start(0)
        self.right_pwm.start(0)
        self.mower_pwm.start(0)
        
        # Güvenlik limitleri
        self.max_speed = config.get('max_speed', 100)
        self.ramping_enabled = config.get('ramping_enabled', True)
        self.ramp_rate = config.get('ramp_rate', 50)  # %/saniye
        
        # Mevcut hızlar
        self.current_left = 0
        self.current_right = 0
        self.current_mower = 0
        
        # Ramping thread
        self.ramping_thread = None
        self.ramping_active = False
        
    def set_drive_motors(self, left_speed: float, right_speed: float):
        """Sürüş motorlarını ayarla (-100 ile +100 arası)"""
        
        # Hız limitlerini kontrol et
        left_speed = max(-self.max_speed, min(self.max_speed, left_speed))
        right_speed = max(-self.max_speed, min(self.max_speed, right_speed))
        
        if self.ramping_enabled:
            self._ramp_to_speed(left_speed, right_speed)
        else:
            self._set_motor_immediate(left_speed, right_speed)
            
    def _set_motor_immediate(self, left_speed: float, right_speed: float):
        """Motorları anında ayarla (rampa olmadan)"""
        
        # Sol motor
        if left_speed >= 0:
            GPIO.output(self.LEFT_DIR, GPIO.HIGH)
            self.left_pwm.ChangeDutyCycle(abs(left_speed))
        else:
            GPIO.output(self.LEFT_DIR, GPIO.LOW)
            self.left_pwm.ChangeDutyCycle(abs(left_speed))
            
        # Sağ motor
        if right_speed >= 0:
            GPIO.output(self.RIGHT_DIR, GPIO.HIGH)
            self.right_pwm.ChangeDutyCycle(abs(right_speed))
        else:
            GPIO.output(self.RIGHT_DIR, GPIO.LOW)
            self.right_pwm.ChangeDutyCycle(abs(right_speed))
            
        self.current_left = left_speed
        self.current_right = right_speed
        
    def _ramp_to_speed(self, target_left: float, target_right: float):
        """Yumuşak hız geçişi"""
        
        if self.ramping_active:
            return  # Zaten rampa çalışıyor
            
        self.ramping_active = True
        
        def ramp_thread():
            """Rampa thread fonksiyonu"""
            dt = 0.02  # 20ms güncelleme
            
            while (abs(self.current_left - target_left) > 1 or 
                   abs(self.current_right - target_right) > 1):
                
                # Hız değişimi hesapla
                max_change = self.ramp_rate * dt
                
                # Sol motor rampa
                diff_left = target_left - self.current_left
                if abs(diff_left) <= max_change:
                    new_left = target_left
                else:
                    new_left = self.current_left + (max_change if diff_left > 0 else -max_change)
                
                # Sağ motor rampa  
                diff_right = target_right - self.current_right
                if abs(diff_right) <= max_change:
                    new_right = target_right
                else:
                    new_right = self.current_right + (max_change if diff_right > 0 else -max_change)
                
                # Motorları güncelle
                self._set_motor_immediate(new_left, new_right)
                
                time.sleep(dt)
                
            self.ramping_active = False
            
        self.ramping_thread = threading.Thread(target=ramp_thread)
        self.ramping_thread.start()
        
    def set_mower_motor(self, speed: float):
        """Biçme motorunu ayarla (0-100 arası)"""
        speed = max(0, min(100, speed))
        
        GPIO.output(self.MOWER_DIR, GPIO.HIGH)  # Biçme motoru tek yön
        self.mower_pwm.ChangeDutyCycle(speed)
        self.current_mower = speed
        
    def emergency_stop(self):
        """Acil durdurma - tüm motorları durdur"""
        self.left_pwm.ChangeDutyCycle(0)
        self.right_pwm.ChangeDutyCycle(0) 
        self.mower_pwm.ChangeDutyCycle(0)
        
        self.current_left = 0
        self.current_right = 0
        self.current_mower = 0
        
        print("🚨 EMERGENCY STOP - Tüm motorlar durduruldu!")
        
    def get_motor_status(self) -> dict:
        """Motor durumlarını döndür"""
        return {
            'left_speed': self.current_left,
            'right_speed': self.current_right,
            'mower_speed': self.current_mower,
            'ramping_active': self.ramping_active
        }
        
    def cleanup(self):
        """GPIO temizliği"""
        self.emergency_stop()
        self.left_pwm.stop()
        self.right_pwm.stop()
        self.mower_pwm.stop()
        GPIO.cleanup()

# PID Kontrolcü sınıfı
class PIDController:
    """PID kontrolcü - hız/pozisyon kontrolü için"""
    
    def __init__(self, kp: float, ki: float, kd: float, 
                 output_min: float = -100, output_max: float = 100):
        self.kp = kp
        self.ki = ki  
        self.kd = kd
        self.output_min = output_min
        self.output_max = output_max
        
        self.setpoint = 0
        self.integral = 0
        self.last_error = 0
        self.last_time = time.time()
        
    def update(self, current_value: float) -> float:
        """PID çıkışını hesapla"""
        current_time = time.time()
        dt = current_time - self.last_time
        
        if dt <= 0:
            return 0
            
        # Hata hesabı
        error = self.setpoint - current_value
        
        # P terimi
        p_term = self.kp * error
        
        # I terimi
        self.integral += error * dt
        i_term = self.ki * self.integral
        
        # D terimi
        d_term = self.kd * (error - self.last_error) / dt
        
        # Toplam çıkış
        output = p_term + i_term + d_term
        
        # Çıkışı sınırla
        output = max(self.output_min, min(self.output_max, output))
        
        # Değerleri güncelle
        self.last_error = error
        self.last_time = current_time
        
        return output
        
    def set_setpoint(self, setpoint: float):
        """Hedef değeri ayarla"""
        self.setpoint = setpoint
        
    def reset(self):
        """PID değerlerini sıfırla"""
        self.integral = 0
        self.last_error = 0
        self.last_time = time.time()
```

## 🔗 Modüller Arası İletişim

### Event-Driven Architecture

```python
"""
Olay tabanlı mimari - modüller arası haberleşme
"""

import asyncio
from typing import Dict, List, Callable, Any
from dataclasses import dataclass
from enum import Enum

class EventType(Enum):
    """Olay tipleri"""
    BATTERY_LOW = "battery_low"
    OBSTACLE_DETECTED = "obstacle_detected"
    MOWING_COMPLETE = "mowing_complete"
    EMERGENCY_STOP = "emergency_stop"
    POSITION_UPDATE = "position_update"
    SENSOR_ERROR = "sensor_error"

@dataclass
class Event:
    """Olay veri yapısı"""
    type: EventType
    data: Dict[str, Any]
    timestamp: float
    source: str

class EventManager:
    """Olay yöneticisi - modüller arası haberleşme"""
    
    def __init__(self):
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_queue = asyncio.Queue()
        self.running = False
        
    def subscribe(self, event_type: EventType, callback: Callable):
        """Olaya abone ol"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """Abonelikten çık"""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(callback)
            
    async def publish(self, event: Event):
        """Olay yayınla"""
        await self.event_queue.put(event)
        
    async def start_processing(self):
        """Olay işleme döngüsünü başlat"""
        self.running = True
        
        while self.running:
            try:
                # Olay bekle
                event = await self.event_queue.get()
                
                # Abonelere gönder
                if event.type in self.subscribers:
                    for callback in self.subscribers[event.type]:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(event)
                            else:
                                callback(event)
                        except Exception as e:
                            print(f"❌ Event callback hatası: {e}")
                            
            except Exception as e:
                print(f"❌ Event processing hatası: {e}")
                
    def stop_processing(self):
        """Olay işlemeyi durdur"""
        self.running = False
```

### Dependency Injection

```python
"""
Bağımlılık enjeksiyonu - modül bağımlılıklarını yönet
"""

from typing import Dict, Type, Any, TypeVar, Optional
import inspect

T = TypeVar('T')

class DIContainer:
    """Dependency Injection container"""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, callable] = {}
        
    def register_singleton(self, interface: Type[T], implementation: T):
        """Singleton servis kaydet"""
        self._services[interface] = implementation
        
    def register_factory(self, interface: Type[T], factory: callable):
        """Factory fonksiyonu kaydet"""
        self._factories[interface] = factory
        
    def get(self, interface: Type[T]) -> T:
        """Servis al"""
        # Önce singleton'ları kontrol et
        if interface in self._services:
            return self._services[interface]
            
        # Sonra factory'leri kontrol et
        if interface in self._factories:
            instance = self._factories[interface]()
            return instance
            
        # Otomatik dependency injection
        return self._auto_inject(interface)
        
    def _auto_inject(self, cls: Type[T]) -> T:
        """Otomatik bağımlılık enjeksiyonu"""
        # Constructor parametrelerini al
        sig = inspect.signature(cls.__init__)
        kwargs = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
                
            # Parameter tipini al
            param_type = param.annotation
            if param_type != inspect.Parameter.empty:
                # Recursively resolve dependency
                kwargs[param_name] = self.get(param_type)
                
        return cls(**kwargs)

# Global DI container
container = DIContainer()

def configure_services():
    """Servisleri yapılandır"""
    from navigation.kalman_odometry import KalmanOdometry
    from hardware.motor_controller import MotorController
    from safety.safety_manager import SafetyManager
    
    # Konfigürasyon
    config = {
        'navigation': {'wheel_base': 0.54},
        'motors': {'max_speed': 100},
        'safety': {'emergency_pin': 27}
    }
    
    # Servisleri kaydet
    container.register_singleton(dict, config)
    container.register_factory(KalmanOdometry, 
                              lambda: KalmanOdometry(config['navigation']))
    container.register_factory(MotorController,
                              lambda: MotorController(config['motors']))
    container.register_factory(SafetyManager,
                              lambda: SafetyManager(config['safety']))
```

---

**🎯 Hacı Abi Notu:** Kod mimarisi robotun sinir sistemi gibi, iyi organize etmezsen spagetti kod olur! Modüler tasarım yap, bağımlılıkları azalt. Event-driven mimari kullan, sıkı coupling'den kaçın. DI container ile servisleri yönet, test edilebilir kod yaz. Async/await kullan, blocking operation yapma. Logger kullan, hata ayıklamayı kolaylaştır. Clean code prensiplerini uygula, gelecekteki sen teşekkür edecek! 🤖🧠
