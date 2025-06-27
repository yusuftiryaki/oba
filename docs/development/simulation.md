# 🎮 Simülasyon ve Test Ortamı

## 📋 İçindekiler
1. [Simülasyon Mimarisi](#simülasyon-mimarisi)
2. [Ortam Kurulumu](#ortam-kurulumu)
3. [Fizik Simülasyonu](#fizik-simülasyonu)
4. [Navigasyon Simülasyonu](#navigasyon-simülasyonu)
5. [Web Arayüzü Simülasyonu](#web-arayüzü-simülasyonu)
6. [Test Senaryoları](#test-senaryoları)
7. [Performans Ölçümü](#performans-ölçümü)
8. [Debugging Tools](#debugging-tools)

## 🏗️ Simülasyon Mimarisi

### Genel Yapı
```
simulation/
├── core/
│   ├── simulator.py        # Ana simülatör
│   ├── physics_engine.py   # Fizik motoru
│   └── world_model.py      # Dünya modeli
├── models/
│   ├── robot_model.py      # Robot modeli
│   ├── sensor_models.py    # Sensör modelleri
│   └── environment.py      # Çevre modeli
├── visualization/
│   ├── pygame_viewer.py    # Real-time görselleştirme
│   ├── web_viewer.py       # Web-based viewer
│   └── plotter.py          # Data plotting
└── scenarios/
    ├── basic_movement.py   # Temel hareket testleri
    ├── navigation_test.py  # Navigasyon testleri
    └── integration_test.py # Entegrasyon testleri
```

### Simülatör Bileşenleri
```python
# simulation/core/simulator.py
import numpy as np
import time
import threading
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class SimulationConfig:
    """Simülasyon konfigürasyonu."""
    time_step: float = 0.01  # 10ms
    real_time_factor: float = 1.0  # 1x = gerçek zamanlı
    world_size: Tuple[float, float] = (100.0, 100.0)  # meters
    enable_physics: bool = True
    enable_visualization: bool = True
    log_level: str = "INFO"

class RobotSimulator:
    """
    Ana robot simülatörü.
    
    Gerçek robot davranışını simüle ederek test ve geliştirme
    süreçlerini destekler.
    """
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.is_running = False
        self.simulation_time = 0.0
        
        # Bileşenleri başlat
        self.physics = PhysicsEngine(config)
        self.robot = RobotModel(config)
        self.environment = Environment(config)
        self.sensors = SensorModels(config)
        
        # Visualization (opsiyonel)
        if config.enable_visualization:
            self.viewer = PygameViewer(config)
        
        # Logging
        self.logger = self._setup_logger()
        
    def start(self):
        """Simülasyonu başlat."""
        self.is_running = True
        self.simulation_thread = threading.Thread(target=self._simulation_loop)
        self.simulation_thread.start()
        
        if hasattr(self, 'viewer'):
            self.viewer.start()
            
        self.logger.info("Simülasyon başlatıldı")
        
    def stop(self):
        """Simülasyonu durdur."""
        self.is_running = False
        
        if hasattr(self, 'simulation_thread'):
            self.simulation_thread.join()
            
        if hasattr(self, 'viewer'):
            self.viewer.stop()
            
        self.logger.info("Simülasyon durduruldu")
        
    def _simulation_loop(self):
        """Ana simülasyon döngüsü."""
        last_time = time.time()
        
        while self.is_running:
            current_time = time.time()
            real_dt = current_time - last_time
            
            # Simülasyon time step
            sim_dt = self.config.time_step
            
            # Fizik güncellemesi
            if self.config.enable_physics:
                self.physics.step(sim_dt)
                
            # Robot güncellemesi
            self.robot.update(sim_dt)
            
            # Sensör güncellemesi
            self.sensors.update(self.robot.state, self.environment)
            
            # Visualization güncellemesi
            if hasattr(self, 'viewer'):
                self.viewer.update(self.robot.state, self.environment)
                
            # Zamanlama
            self.simulation_time += sim_dt
            
            # Real-time sync
            target_sleep = sim_dt / self.config.real_time_factor
            actual_sleep = target_sleep - real_dt
            if actual_sleep > 0:
                time.sleep(actual_sleep)
                
            last_time = current_time
            
    def get_robot_state(self) -> Dict:
        """Robot durumunu al."""
        return {
            'position': self.robot.position,
            'velocity': self.robot.velocity,
            'orientation': self.robot.orientation,
            'battery_level': self.robot.battery_level,
            'motor_speeds': self.robot.motor_speeds,
            'sensor_data': self.sensors.get_all_data()
        }
        
    def send_command(self, command: Dict):
        """Robot komut gönder."""
        self.robot.execute_command(command)
```

## ⚙️ Ortam Kurulumu

### Gereksinimler
```python
# requirements-simulation.txt
pygame>=2.1.0          # Visualization
matplotlib>=3.5.0      # Plotting
numpy>=1.21.0          # Numerical computing
scipy>=1.7.0           # Scientific computing
pymunk>=6.2.0          # 2D physics engine
opencv-python>=4.5.0   # Computer vision
pyyaml>=6.0            # Configuration files
pytest>=7.0.0          # Testing framework
```

### Kurulum Scripti
```bash
#!/bin/bash
# setup_simulation.sh

echo "🎮 OBA Robot Simülasyon Ortamı Kurulumu"

# Python virtual environment
python -m venv simulation_env
source simulation_env/bin/activate  # Linux/Mac
# simulation_env\Scripts\activate.bat  # Windows

# Dependencies
pip install -r requirements-simulation.txt

# Test kurulum
python -c "import pygame, numpy, scipy, pymunk; print('✅ Tüm paketler başarıyla kuruldu')"

echo "🚀 Simülasyon ortamı hazır!"
echo "Kullanım: python simulation/run_simulation.py"
```

### Konfigürasyon
```yaml
# simulation/config/default.yaml
simulation:
  time_step: 0.01
  real_time_factor: 1.0
  world_size: [100.0, 100.0]
  enable_physics: true
  enable_visualization: true
  
robot:
  wheel_radius: 0.08        # meters
  wheelbase: 0.3           # meters  
  max_speed: 2.0           # m/s
  max_angular_speed: 3.14  # rad/s
  mass: 15.0               # kg
  
environment:
  obstacles:
    - type: "rectangle"
      position: [10, 10]
      size: [2, 1]
    - type: "circle" 
      position: [20, 15]
      radius: 1.5
      
  boundaries:
    min_x: 0
    max_x: 50
    min_y: 0
    max_y: 30
    
sensors:
  odometry:
    noise_std: 0.01       # Standard deviation
    bias: 0.001           # Systematic error
    
  gps:
    enabled: true
    noise_std: 0.1        # GPS noise
    update_rate: 1.0      # Hz
    
  imu:
    gyro_noise: 0.005     # rad/s
    accel_noise: 0.01     # m/s²
```

## 🔬 Fizik Simülasyonu

### Physics Engine
```python
# simulation/core/physics_engine.py
import pymunk
import numpy as np
from typing import List, Tuple

class PhysicsEngine:
    """2D fizik simülasyon motoru."""
    
    def __init__(self, config):
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)  # No gravity for top-down view
        
        # Collision types
        self.ROBOT_TYPE = 1
        self.OBSTACLE_TYPE = 2
        self.BOUNDARY_TYPE = 3
        
        self._setup_collision_handlers()
        self._create_world(config)
        
    def _setup_collision_handlers(self):
        """Çarpışma işleyicilerini kur."""
        
        def robot_obstacle_collision(arbiter, space, data):
            """Robot-engel çarpışması."""
            # Collision response
            print("⚠️ Robot engel ile çarpıştı!")
            return True
            
        def robot_boundary_collision(arbiter, space, data):
            """Robot-sınır çarpışması."""
            print("⚠️ Robot sınıra çarptı!")
            return True
            
        # Register handlers
        handler1 = self.space.add_collision_handler(
            self.ROBOT_TYPE, self.OBSTACLE_TYPE
        )
        handler1.begin = robot_obstacle_collision
        
        handler2 = self.space.add_collision_handler(
            self.ROBOT_TYPE, self.BOUNDARY_TYPE  
        )
        handler2.begin = robot_boundary_collision
        
    def _create_world(self, config):
        """Dünya objelerini oluştur."""
        
        # Boundaries
        world_size = config.world_size
        boundaries = [
            # Bottom
            pymunk.Segment(self.space.static_body, (0, 0), (world_size[0], 0), 1),
            # Top  
            pymunk.Segment(self.space.static_body, (0, world_size[1]), (world_size[0], world_size[1]), 1),
            # Left
            pymunk.Segment(self.space.static_body, (0, 0), (0, world_size[1]), 1),
            # Right
            pymunk.Segment(self.space.static_body, (world_size[0], 0), (world_size[0], world_size[1]), 1)
        ]
        
        for boundary in boundaries:
            boundary.collision_type = self.BOUNDARY_TYPE
            boundary.friction = 0.7
            self.space.add(boundary)
            
    def add_robot(self, position: Tuple[float, float], orientation: float) -> pymunk.Body:
        """Robot fizik gövdesi ekle."""
        
        # Robot body (circle for simplicity)
        moment = pymunk.moment_for_circle(15.0, 0, 0.2)  # mass=15kg, radius=0.2m
        body = pymunk.Body(15.0, moment)
        body.position = position
        body.angle = orientation
        
        # Robot shape
        shape = pymunk.Circle(body, 0.2)  # 0.2m radius
        shape.collision_type = self.ROBOT_TYPE
        shape.friction = 0.7
        
        self.space.add(body, shape)
        return body
        
    def add_obstacle(self, position: Tuple[float, float], size: Tuple[float, float]):
        """Dikdörtgen engel ekle."""
        
        # Static obstacle
        vertices = [
            (-size[0]/2, -size[1]/2),
            (size[0]/2, -size[1]/2),
            (size[0]/2, size[1]/2),
            (-size[0]/2, size[1]/2)
        ]
        
        shape = pymunk.Poly(self.space.static_body, vertices)
        shape.body.position = position
        shape.collision_type = self.OBSTACLE_TYPE
        shape.friction = 0.8
        
        self.space.add(shape)
        
    def step(self, dt: float):
        """Fizik simülasyonu bir adım ilerlet."""
        self.space.step(dt)
```

### Robot Fizik Modeli
```python
# simulation/models/robot_model.py
import numpy as np
import pymunk
from typing import Dict, Tuple

class RobotModel:
    """Robot fizik ve kinematik modeli."""
    
    def __init__(self, config):
        self.config = config
        
        # Robot parameters
        self.wheel_radius = config.robot.wheel_radius
        self.wheelbase = config.robot.wheelbase
        self.max_speed = config.robot.max_speed
        
        # State variables
        self.position = np.array([0.0, 0.0])  # x, y
        self.orientation = 0.0  # radians
        self.velocity = np.array([0.0, 0.0])  # vx, vy
        self.angular_velocity = 0.0  # rad/s
        
        # Motor states
        self.motor_speeds = np.array([0.0, 0.0])  # left, right (rad/s)
        self.target_speeds = np.array([0.0, 0.0])
        
        # Battery model
        self.battery_level = 100.0  # percentage
        self.power_consumption = 0.0  # watts
        
    def update(self, dt: float):
        """Robot durumunu güncelle."""
        
        # Motor dynamics (first-order lag)
        motor_tau = 0.1  # Motor time constant
        self.motor_speeds += (self.target_speeds - self.motor_speeds) * dt / motor_tau
        
        # Differential drive kinematics
        self._update_kinematics(dt)
        
        # Battery model
        self._update_battery(dt)
        
    def _update_kinematics(self, dt: float):
        """Diferansiyel sürüş kinematiği."""
        
        # Wheel speeds to robot velocities
        left_speed = self.motor_speeds[0] * self.wheel_radius
        right_speed = self.motor_speeds[1] * self.wheel_radius
        
        # Robot linear and angular velocities
        linear_vel = (left_speed + right_speed) / 2.0
        angular_vel = (right_speed - left_speed) / self.wheelbase
        
        # Update position and orientation
        self.position[0] += linear_vel * np.cos(self.orientation) * dt
        self.position[1] += linear_vel * np.sin(self.orientation) * dt
        self.orientation += angular_vel * dt
        
        # Normalize orientation to [-π, π]
        self.orientation = np.arctan2(np.sin(self.orientation), np.cos(self.orientation))
        
        # Update velocity for physics
        self.velocity[0] = linear_vel * np.cos(self.orientation)
        self.velocity[1] = linear_vel * np.sin(self.orientation)
        self.angular_velocity = angular_vel
        
    def _update_battery(self, dt: float):
        """Batarya modelini güncelle."""
        
        # Power consumption model
        motor_power = np.sum(np.abs(self.motor_speeds)) * 10  # Simplified model
        base_power = 5.0  # Base consumption (electronics)
        
        self.power_consumption = motor_power + base_power
        
        # Battery drain (simplified)
        battery_capacity = 5000  # mAh
        voltage = 14.8  # V
        energy_capacity = battery_capacity * voltage / 1000  # Wh
        
        energy_used = self.power_consumption * dt / 3600  # Wh
        battery_drain = (energy_used / energy_capacity) * 100  # percentage
        
        self.battery_level = max(0.0, self.battery_level - battery_drain)
        
    def execute_command(self, command: Dict):
        """Robot komutunu çalıştır."""
        
        if command['type'] == 'move':
            linear_vel = command.get('linear_velocity', 0.0)
            angular_vel = command.get('angular_velocity', 0.0)
            
            # Convert to wheel speeds
            left_vel = linear_vel - angular_vel * self.wheelbase / 2
            right_vel = linear_vel + angular_vel * self.wheelbase / 2
            
            # Convert to motor speeds (rad/s)
            self.target_speeds[0] = left_vel / self.wheel_radius
            self.target_speeds[1] = right_vel / self.wheel_radius
            
            # Speed limits
            max_motor_speed = self.max_speed / self.wheel_radius
            self.target_speeds = np.clip(self.target_speeds, -max_motor_speed, max_motor_speed)
            
        elif command['type'] == 'stop':
            self.target_speeds = np.array([0.0, 0.0])
```

## 🧭 Navigasyon Simülasyonu

### Sensör Simülasyonu
```python
# simulation/models/sensor_models.py
import numpy as np
from typing import Dict, List, Tuple, Optional

class SensorModels:
    """Tüm sensör modellerini içerir."""
    
    def __init__(self, config):
        self.config = config
        self.odometry = OdometrySimulator(config)
        self.gps = GPSSimulator(config)
        self.imu = IMUSimulator(config)
        
    def update(self, robot_state: Dict, environment):
        """Tüm sensörleri güncelle."""
        self.odometry.update(robot_state)
        self.gps.update(robot_state)
        self.imu.update(robot_state)
        
    def get_all_data(self) -> Dict:
        """Tüm sensör verilerini al."""
        return {
            'odometry': self.odometry.get_data(),
            'gps': self.gps.get_data(),
            'imu': self.imu.get_data()
        }

class OdometrySimulator:
    """Odometri sensör simülatörü."""
    
    def __init__(self, config):
        self.noise_std = config.sensors.odometry.noise_std
        self.bias = config.sensors.odometry.bias
        
        # Encoder counts
        self.left_encoder = 0
        self.right_encoder = 0
        self.last_position = np.array([0.0, 0.0])
        
    def update(self, robot_state: Dict):
        """Odometri verilerini güncelle."""
        
        # Calculate wheel rotations
        position = np.array(robot_state['position'])
        distance_moved = np.linalg.norm(position - self.last_position)
        
        # Add noise and bias
        noisy_distance = distance_moved + np.random.normal(0, self.noise_std) + self.bias
        
        # Convert to encoder counts (simplified)
        wheel_radius = 0.08  # meters
        counts_per_revolution = 1000
        
        encoder_increment = int(noisy_distance / (2 * np.pi * wheel_radius) * counts_per_revolution)
        
        self.left_encoder += encoder_increment
        self.right_encoder += encoder_increment
        
        self.last_position = position.copy()
        
    def get_data(self) -> Dict:
        """Odometri verilerini al."""
        return {
            'left_encoder': self.left_encoder,
            'right_encoder': self.right_encoder,
            'timestamp': time.time()
        }

class GPSSimulator:
    """GPS sensör simülatörü."""
    
    def __init__(self, config):
        self.enabled = config.sensors.gps.enabled
        self.noise_std = config.sensors.gps.noise_std
        self.update_rate = config.sensors.gps.update_rate
        self.last_update = 0
        
        # GPS origin (simulated)
        self.origin_lat = 39.0  # degrees
        self.origin_lon = 35.0  # degrees
        
    def update(self, robot_state: Dict):
        """GPS verilerini güncelle."""
        current_time = time.time()
        
        if not self.enabled:
            return
            
        # Check update rate
        if current_time - self.last_update < 1.0 / self.update_rate:
            return
            
        # Convert position to GPS coordinates
        position = robot_state['position']
        
        # Simple conversion (meters to degrees)
        lat_offset = position[1] / 111320  # meters to degrees (approximate)
        lon_offset = position[0] / (111320 * np.cos(np.radians(self.origin_lat)))
        
        # Add GPS noise
        lat_noise = np.random.normal(0, self.noise_std / 111320)
        lon_noise = np.random.normal(0, self.noise_std / 111320)
        
        self.latitude = self.origin_lat + lat_offset + lat_noise
        self.longitude = self.origin_lon + lon_offset + lon_noise
        
        self.last_update = current_time
        
    def get_data(self) -> Dict:
        """GPS verilerini al."""
        return {
            'latitude': getattr(self, 'latitude', self.origin_lat),
            'longitude': getattr(self, 'longitude', self.origin_lon),
            'altitude': 100.0,  # Fixed altitude
            'accuracy': self.noise_std,
            'timestamp': time.time()
        }
```

### Path Planning Test
```python
# simulation/scenarios/navigation_test.py
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple

class NavigationTestScenario:
    """Navigasyon test senaryoları."""
    
    def __init__(self, simulator):
        self.simulator = simulator
        self.waypoints = []
        self.path_history = []
        
    def test_straight_line(self, distance: float = 10.0):
        """Düz hat navigasyon testi."""
        
        print(f"🎯 Düz hat testi başlatılıyor: {distance}m")
        
        # Hedef nokta
        target = (distance, 0.0)
        
        # Robot komutları
        start_time = time.time()
        
        while True:
            robot_state = self.simulator.get_robot_state()
            position = robot_state['position']
            
            # Hedefe olan mesafe
            distance_to_target = np.linalg.norm(np.array(target) - np.array(position))
            
            if distance_to_target < 0.1:  # 10cm tolerance
                print("✅ Hedefe ulaşıldı!")
                break
                
            # Basit P kontrolcü
            kp = 0.5
            linear_vel = kp * distance_to_target
            linear_vel = min(linear_vel, 1.0)  # Max speed limit
            
            # Komut gönder
            command = {
                'type': 'move',
                'linear_velocity': linear_vel,
                'angular_velocity': 0.0
            }
            self.simulator.send_command(command)
            
            # Path history
            self.path_history.append(position)
            
            time.sleep(0.1)
            
        # Stop robot
        self.simulator.send_command({'type': 'stop'})
        
        # Sonuçları analiz et
        self._analyze_path_accuracy(target)
        
    def test_waypoint_following(self, waypoints: List[Tuple[float, float]]):
        """Waypoint takip testi."""
        
        print(f"🗺️ Waypoint takip testi: {len(waypoints)} nokta")
        
        for i, waypoint in enumerate(waypoints):
            print(f"Hedef {i+1}: {waypoint}")
            
            while True:
                robot_state = self.simulator.get_robot_state()
                position = np.array(robot_state['position'])
                target = np.array(waypoint)
                
                # Distance and angle to target
                diff = target - position
                distance = np.linalg.norm(diff)
                target_angle = np.arctan2(diff[1], diff[0])
                
                if distance < 0.2:  # Reached waypoint
                    print(f"✅ Waypoint {i+1} ulaşıldı")
                    break
                    
                # Angle error
                current_angle = robot_state['orientation']
                angle_error = target_angle - current_angle
                
                # Normalize angle
                angle_error = np.arctan2(np.sin(angle_error), np.cos(angle_error))
                
                # Control
                linear_vel = min(distance * 0.5, 1.0)
                angular_vel = angle_error * 1.0
                
                command = {
                    'type': 'move',
                    'linear_velocity': linear_vel,
                    'angular_velocity': angular_vel
                }
                self.simulator.send_command(command)
                
                self.path_history.append(position.tolist())
                time.sleep(0.1)
                
        self.simulator.send_command({'type': 'stop'})
        
    def _analyze_path_accuracy(self, target: Tuple[float, float]):
        """Yol hassasiyetini analiz et."""
        
        if not self.path_history:
            return
            
        path_array = np.array(self.path_history)
        final_position = path_array[-1]
        target_array = np.array(target)
        
        # Final error
        final_error = np.linalg.norm(final_position - target_array)
        
        # Path length
        path_length = 0
        for i in range(1, len(path_array)):
            path_length += np.linalg.norm(path_array[i] - path_array[i-1])
            
        # Ideal path length (straight line)
        ideal_length = np.linalg.norm(target_array)
        
        print(f"📊 Navigasyon Analizi:")
        print(f"   Final hata: {final_error:.3f} m")
        print(f"   Yol uzunluğu: {path_length:.3f} m")
        print(f"   İdeal uzunluk: {ideal_length:.3f} m")
        print(f"   Verimlilik: {ideal_length/path_length*100:.1f}%")
        
        # Plot path
        self._plot_path(target_array)
        
    def _plot_path(self, target: np.ndarray):
        """Yolu çiz."""
        
        if not self.path_history:
            return
            
        path_array = np.array(self.path_history)
        
        plt.figure(figsize=(10, 8))
        plt.plot(path_array[:, 0], path_array[:, 1], 'b-', linewidth=2, label='Robot yolu')
        plt.plot(0, 0, 'go', markersize=10, label='Başlangıç')
        plt.plot(target[0], target[1], 'ro', markersize=10, label='Hedef')
        
        plt.xlabel('X (metre)')
        plt.ylabel('Y (metre)')
        plt.title('Robot Navigasyon Yolu')
        plt.legend()
        plt.grid(True)
        plt.axis('equal')
        plt.show()
```

## 🎨 Görselleştirme

### Pygame Viewer
```python
# simulation/visualization/pygame_viewer.py
import pygame
import numpy as np
import math
from typing import Dict, List, Tuple

class PygameViewer:
    """Real-time simülasyon görselleştirme."""
    
    def __init__(self, config):
        self.config = config
        self.screen_width = 1200
        self.screen_height = 800
        self.scale = 10  # pixels per meter
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        self.GRAY = (128, 128, 128)
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("OBA Robot Simülasyon")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        # Path history
        self.path_history = []
        
    def start(self):
        """Viewer'ı başlat."""
        self.running = True
        
    def stop(self):
        """Viewer'ı durdur."""
        self.running = False
        pygame.quit()
        
    def update(self, robot_state: Dict, environment):
        """Görselleştirmeyi güncelle."""
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
        # Clear screen
        self.screen.fill(self.WHITE)
        
        # Draw environment
        self._draw_environment(environment)
        
        # Draw robot
        self._draw_robot(robot_state)
        
        # Draw path
        self._draw_path()
        
        # Draw UI
        self._draw_ui(robot_state)
        
        # Update display
        pygame.display.flip()
        self.clock.tick(60)  # 60 FPS
        
        # Add to path history
        position = robot_state['position']
        self.path_history.append(position)
        
        # Limit path history
        if len(self.path_history) > 1000:
            self.path_history.pop(0)
            
    def _draw_robot(self, robot_state: Dict):
        """Robot çiz."""
        
        position = robot_state['position']
        orientation = robot_state['orientation']
        
        # Convert to screen coordinates
        screen_x = int(position[0] * self.scale + self.screen_width // 2)
        screen_y = int(self.screen_height // 2 - position[1] * self.scale)
        
        # Robot body (circle)
        robot_radius = int(0.2 * self.scale)  # 0.2m radius
        pygame.draw.circle(self.screen, self.BLUE, (screen_x, screen_y), robot_radius)
        
        # Direction indicator
        direction_length = robot_radius * 1.5
        end_x = screen_x + int(direction_length * math.cos(orientation))
        end_y = screen_y - int(direction_length * math.sin(orientation))
        pygame.draw.line(self.screen, self.RED, (screen_x, screen_y), (end_x, end_y), 3)
        
        # Battery indicator
        battery_level = robot_state['battery_level']
        battery_color = self.GREEN if battery_level > 50 else self.YELLOW if battery_level > 20 else self.RED
        battery_width = int(robot_radius * 2 * battery_level / 100)
        battery_rect = pygame.Rect(screen_x - robot_radius, screen_y - robot_radius - 20, battery_width, 10)
        pygame.draw.rect(self.screen, battery_color, battery_rect)
        
    def _draw_path(self):
        """Robot yolunu çiz."""
        
        if len(self.path_history) < 2:
            return
            
        screen_points = []
        for position in self.path_history:
            screen_x = int(position[0] * self.scale + self.screen_width // 2)
            screen_y = int(self.screen_height // 2 - position[1] * self.scale)
            screen_points.append((screen_x, screen_y))
            
        if len(screen_points) > 1:
            pygame.draw.lines(self.screen, self.GRAY, False, screen_points, 2)
            
    def _draw_environment(self, environment):
        """Çevre objelerini çiz."""
        
        # Grid
        grid_size = int(1.0 * self.scale)  # 1 meter grid
        for x in range(0, self.screen_width, grid_size):
            pygame.draw.line(self.screen, (240, 240, 240), (x, 0), (x, self.screen_height), 1)
        for y in range(0, self.screen_height, grid_size):
            pygame.draw.line(self.screen, (240, 240, 240), (0, y), (self.screen_width, y), 1)
            
        # Coordinate axes
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        pygame.draw.line(self.screen, self.BLACK, (center_x, 0), (center_x, self.screen_height), 2)
        pygame.draw.line(self.screen, self.BLACK, (0, center_y), (self.screen_width, center_y), 2)
        
    def _draw_ui(self, robot_state: Dict):
        """UI elementlerini çiz."""
        
        # Status text
        status_lines = [
            f"Pozisyon: ({robot_state['position'][0]:.2f}, {robot_state['position'][1]:.2f})",
            f"Oryantasyon: {math.degrees(robot_state['orientation']):.1f}°",
            f"Batarya: {robot_state['battery_level']:.1f}%",
            f"Hız: {np.linalg.norm(robot_state['velocity']):.2f} m/s"
        ]
        
        for i, line in enumerate(status_lines):
            text_surface = self.font.render(line, True, self.BLACK)
            self.screen.blit(text_surface, (10, 10 + i * 30))
```

## 🧪 Test Senaryoları

### Otomatik Test Suite
```python
# simulation/scenarios/integration_test.py
import unittest
import time
import numpy as np
from simulation.core.simulator import RobotSimulator, SimulationConfig

class IntegrationTestSuite(unittest.TestCase):
    """Entegrasyon test suite."""
    
    def setUp(self):
        """Her test öncesi çalışır."""
        config = SimulationConfig(
            enable_visualization=False,  # Headless test
            real_time_factor=10.0        # 10x hızlı
        )
        self.simulator = RobotSimulator(config)
        self.simulator.start()
        time.sleep(0.1)  # Simulator başlatma
        
    def tearDown(self):
        """Her test sonrası çalışır."""
        self.simulator.stop()
        
    def test_basic_movement(self):
        """Temel hareket testi."""
        
        # İleri hareket komutu
        command = {
            'type': 'move',
            'linear_velocity': 0.5,
            'angular_velocity': 0.0
        }
        self.simulator.send_command(command)
        
        # 2 saniye bekle
        time.sleep(2.0)
        
        # Pozisyon kontrolü
        state = self.simulator.get_robot_state()
        position = state['position']
        
        # İleri gitmiş olmalı
        self.assertGreater(position[0], 0.5)  # X ekseni
        self.assertAlmostEqual(position[1], 0.0, delta=0.1)  # Y ekseni
        
    def test_rotation(self):
        """Dönüş testi."""
        
        # Dönüş komutu
        command = {
            'type': 'move',
            'linear_velocity': 0.0,
            'angular_velocity': 1.0  # 1 rad/s
        }
        self.simulator.send_command(command)
        
        # 1.57 saniye bekle (π/2 radyan)
        time.sleep(1.57)
        
        # Orientasyon kontrolü
        state = self.simulator.get_robot_state()
        orientation = state['orientation']
        
        # 90° dönmüş olmalı
        self.assertAlmostEqual(orientation, np.pi/2, delta=0.1)
        
    def test_battery_drain(self):
        """Batarya boşalma testi."""
        
        initial_state = self.simulator.get_robot_state()
        initial_battery = initial_state['battery_level']
        
        # Yüksek güçte çalışma
        command = {
            'type': 'move',
            'linear_velocity': 2.0,  # Max speed
            'angular_velocity': 2.0   # Max angular speed
        }
        self.simulator.send_command(command)
        
        # 10 saniye bekle
        time.sleep(10.0)
        
        # Batarya seviyesi düşmüş olmalı
        final_state = self.simulator.get_robot_state()
        final_battery = final_state['battery_level']
        
        self.assertLess(final_battery, initial_battery)
        
    def test_sensor_data_consistency(self):
        """Sensör veri tutarlılığı testi."""
        
        # Hareket komutu
        command = {
            'type': 'move',
            'linear_velocity': 1.0,
            'angular_velocity': 0.0
        }
        self.simulator.send_command(command)
        
        # Veri toplama
        sensor_data_history = []
        for _ in range(10):
            state = self.simulator.get_robot_state()
            sensor_data_history.append(state['sensor_data'])
            time.sleep(0.1)
            
        # Odometry tutarlılığı
        for i in range(1, len(sensor_data_history)):
            current = sensor_data_history[i]['odometry']
            previous = sensor_data_history[i-1]['odometry']
            
            # Encoder counts artmalı
            self.assertGreaterEqual(current['left_encoder'], previous['left_encoder'])
            self.assertGreaterEqual(current['right_encoder'], previous['right_encoder'])

def run_performance_tests():
    """Performans testleri."""
    
    print("🚀 Performans testleri başlatılıyor...")
    
    config = SimulationConfig(
        enable_visualization=False,
        real_time_factor=100.0  # 100x hızlı
    )
    
    simulator = RobotSimulator(config)
    simulator.start()
    
    # Test 1: Simulation FPS
    start_time = time.time()
    iterations = 1000
    
    for _ in range(iterations):
        state = simulator.get_robot_state()
        
    end_time = time.time()
    simulation_fps = iterations / (end_time - start_time)
    
    print(f"📊 Simülasyon FPS: {simulation_fps:.1f}")
    
    # Test 2: Memory usage
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_usage = process.memory_info().rss / 1024 / 1024  # MB
    
    print(f"💾 Bellek kullanımı: {memory_usage:.1f} MB")
    
    simulator.stop()

if __name__ == "__main__":
    # Unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Performance tests
    run_performance_tests()
```

## 📊 Monitoring ve Logging

### Data Logger
```python
# simulation/utils/data_logger.py
import csv
import json
import time
import threading
from typing import Dict, List
from datetime import datetime

class SimulationDataLogger:
    """Simülasyon veri logger."""
    
    def __init__(self, log_dir: str = "logs/simulation"):
        self.log_dir = log_dir
        self.is_logging = False
        self.data_buffer = []
        
        # Create log directory
        os.makedirs(log_dir, exist_ok=True)
        
        # Log files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_file = f"{log_dir}/simulation_{timestamp}.csv"
        self.json_file = f"{log_dir}/simulation_{timestamp}.json"
        
    def start_logging(self):
        """Logging başlat."""
        self.is_logging = True
        self.log_thread = threading.Thread(target=self._logging_loop)
        self.log_thread.start()
        
    def stop_logging(self):
        """Logging durdur."""
        self.is_logging = False
        if hasattr(self, 'log_thread'):
            self.log_thread.join()
            
        # Save remaining data
        self._save_data()
        
    def log_robot_state(self, robot_state: Dict):
        """Robot durumunu logla."""
        
        log_entry = {
            'timestamp': time.time(),
            'position_x': robot_state['position'][0],
            'position_y': robot_state['position'][1],
            'orientation': robot_state['orientation'],
            'velocity_x': robot_state['velocity'][0],
            'velocity_y': robot_state['velocity'][1],
            'battery_level': robot_state['battery_level'],
            'motor_left': robot_state['motor_speeds'][0],
            'motor_right': robot_state['motor_speeds'][1]
        }
        
        self.data_buffer.append(log_entry)
        
    def _logging_loop(self):
        """Logging döngüsü."""
        
        while self.is_logging:
            if len(self.data_buffer) > 100:  # Buffer full
                self._save_data()
                self.data_buffer.clear()
                
            time.sleep(1.0)  # 1 saniyede bir kontrol
            
    def _save_data(self):
        """Veriyi dosyaya kaydet."""
        
        if not self.data_buffer:
            return
            
        # CSV format
        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.data_buffer[0].keys())
            
            # Header (first time)
            if f.tell() == 0:
                writer.writeheader()
                
            writer.writerows(self.data_buffer)
            
        # JSON format (for detailed analysis)
        with open(self.json_file, 'w') as f:
            json.dump(self.data_buffer, f, indent=2)
```

---

## 🎯 Kullanım Örnekleri

### Hızlı Başlangıç
```python
# quick_start.py
from simulation.core.simulator import RobotSimulator, SimulationConfig
from simulation.scenarios.navigation_test import NavigationTestScenario

# Simülasyon konfigürasyonu
config = SimulationConfig(
    time_step=0.01,
    real_time_factor=1.0,
    enable_visualization=True
)

# Simülatörü başlat
simulator = RobotSimulator(config)
simulator.start()

# Test senaryosu
nav_test = NavigationTestScenario(simulator)

# Basit hareket testi
nav_test.test_straight_line(distance=5.0)

# Waypoint testi
waypoints = [(5, 0), (5, 5), (0, 5), (0, 0)]
nav_test.test_waypoint_following(waypoints)

# Simülatörü durdur
simulator.stop()
```

### Batch Test
```bash
#!/bin/bash
# run_simulation_tests.sh

echo "🧪 OBA Robot Simülasyon Testleri"

# Environment setup
source simulation_env/bin/activate

# Unit tests
echo "📋 Unit testler çalışıyor..."
python -m pytest simulation/tests/ -v

# Integration tests  
echo "🔗 Entegrasyon testleri çalışıyor..."
python simulation/scenarios/integration_test.py

# Performance tests
echo "⚡ Performans testleri çalışıyor..."
python simulation/utils/performance_test.py

# Navigation tests
echo "🧭 Navigasyon testleri çalışıyor..."
python simulation/scenarios/navigation_test.py

echo "✅ Tüm testler tamamlandı!"
```

---

## 📞 Destek ve Geliştirme

### Simülasyon Hataları
- **Fizik simülasyonu instabil**: `time_step` değerini küçültün
- **Görselleştirme yavaş**: `real_time_factor` değerini artırın
- **Sensör verileri eksik**: `config/simulation.yaml` kontrol edin

### Yeni Sensör Ekleme
1. `sensor_models.py`'da yeni sınıf oluşturun
2. `SensorModels` sınıfına ekleyin
3. Test senaryoları yazın
4. Dokümantasyonu güncelleyin

### Performans Optimizasyonu
- Numpy vectorization kullanın
- Gereksiz hesaplamaları cache'leyin
- Multiprocessing ile paralelleştirin
- Memory profiling yapın

---

*Bu simülasyon ortamı gerçek robot geliştirme sürecini hızlandırmak ve test etmek için tasarlanmıştır. Sürekli geliştirilmektedir!*
