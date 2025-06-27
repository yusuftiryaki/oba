# Geliştirme Rehberi 👨‍💻

Merhaba kod yazarları! Hacı Abi burada, OBA Robot projesine nasıl katkıda bulunacağınızı, hangi araçları kullanacağınızı ve development workflow'unu öğreteceğim. Bu sayfa geliştiricilerin "survival guide"ı! 🛠️

## 🚀 Quick Start - Hızlı Başlangıç

### 📋 Ön Gereksinimler

```bash
# System Requirements
- Python 3.8+ 
- Node.js 16+
- Git 2.30+
- VS Code (önerilen)
- Raspberry Pi 4 (donanım geliştirme için)

# Hardware Requirements  
- 8GB+ RAM (geliştirme için)
- 50GB+ free disk space
- USB camera (test için)
- Arduino/ESP32 (sensör testleri için)
```

### ⚡ 5 Dakikada Setup

```bash
# 1. Repository'yi clone et
git clone https://github.com/oba-robot/ot-bicme.git
cd ot-bicme

# 2. Virtual environment oluştur
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate     # Windows

# 3. Dependencies yükle
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Pre-commit hooks kurulum
pre-commit install

# 5. Test et
python -m pytest tests/

# 6. Robot servisi başlat
python src/main.py

# 7. Web interface'i aç
# Browser'da: http://localhost:8080
```

## 🏗️ Proje Yapısı

### 📁 Dizin Organizasyonu

```
ot-bicme/
├── 📁 src/                     # Ana kaynak kodlar
│   ├── 🤖 robot/              # Robot kontrol modülleri
│   │   ├── hardware/          # Donanım interface'leri
│   │   ├── sensors/           # Sensör sürücüleri
│   │   ├── navigation/        # Navigasyon algoritmaları
│   │   └── communication/     # İletişim modülleri
│   ├── 🌐 web/               # Web interface
│   │   ├── static/           # CSS, JS, images
│   │   ├── templates/        # HTML templates
│   │   └── api/             # REST API endpoints
│   └── 🧪 tests/            # Test dosyaları
├── 📁 docs/                   # Dokümantasyon
├── 📁 configs/               # Konfigürasyon dosyaları
├── 📁 scripts/               # Utility script'leri
├── 📁 data/                  # Veri dosyaları
└── 📁 tools/                 # Geliştirme araçları
```

### 🔧 Ana Modüller

```python
# Core robot modules
src/robot/
├── core.py           # Robot ana sınıfı
├── motors.py         # Motor kontrolü
├── sensors.py        # Sensör yönetimi
├── camera.py         # Kamera işlemleri
├── navigation.py     # Path planning & navigation
├── safety.py         # Güvenlik sistemleri
└── config.py         # Konfigürasyon yönetimi

# Web interface modules  
src/web/
├── app.py           # Flask uygulaması
├── routes.py        # URL routing
├── websocket.py     # WebSocket handlers
├── auth.py          # Kimlik doğrulama
└── utils.py         # Yardımcı fonksiyonlar
```

## 🛠️ Development Environment

### 🐍 Python Environment

```bash
# Python version management (pyenv kullanarak)
pyenv install 3.9.16
pyenv local 3.9.16

# Virtual environment best practices
python -m venv venv --prompt oba-robot
source venv/bin/activate

# Development dependencies
pip install -e .  # Editable install
pip install -r requirements-dev.txt

# Key development packages
pytest>=7.0.0          # Testing framework
black>=22.0.0          # Code formatting
flake8>=4.0.0          # Linting
mypy>=0.950            # Type checking
pre-commit>=2.17.0     # Git hooks
sphinx>=4.0.0          # Documentation
coverage>=6.0          # Test coverage
```

### 📝 VS Code Setup

```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        ".mypy_cache": true
    }
}
```

```json
// .vscode/launch.json - Debug konfigürasyonu
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Robot Main",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/main.py",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src"
            }
        },
        {
            "name": "Web Server",
            "type": "python", 
            "request": "launch",
            "program": "${workspaceFolder}/src/web/app.py",
            "args": ["--debug"],
            "console": "integratedTerminal"
        },
        {
            "name": "Pytest",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/", "-v"],
            "console": "integratedTerminal"
        }
    ]
}
```

### 🔌 Önerilen Extensions

```bash
# VS Code Extensions (otomatik yükleme için)
code --install-extension ms-python.python
code --install-extension ms-python.black-formatter  
code --install-extension ms-python.flake8
code --install-extension ms-python.mypy-type-checker
code --install-extension ms-toolsai.jupyter
code --install-extension ms-vscode.cmake-tools
code --install-extension redhat.vscode-yaml
code --install-extension bradlc.vscode-tailwindcss
```

## 📏 Code Standards

### 🎨 Code Formatting

```python
# .flake8 konfigürasyonu
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    venv,
    .venv,
    build,
    dist

# Black formatting
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
extend-exclude = '''
/(
  | venv
  | build
  | dist
)/
'''
```

### 🏷️ Type Hints

```python
# Good type hints example
from typing import List, Dict, Optional, Tuple, Union
import numpy as np

class Robot:
    def __init__(self, config: Dict[str, any]) -> None:
        self.position: Tuple[float, float] = (0.0, 0.0)
        self.sensors: Dict[str, any] = {}
        
    def move_to(self, target: Tuple[float, float]) -> bool:
        """Robot'u hedef konuma hareket ettir."""
        success = self._navigate_to_position(target)
        return success
        
    def get_sensor_reading(self, sensor_name: str) -> Optional[float]:
        """Sensör okuma değerini al."""
        if sensor_name not in self.sensors:
            return None
        return self.sensors[sensor_name].read()
        
    def scan_area(self) -> List[Tuple[float, float]]:
        """Çevredeki engelleri tara."""
        obstacles: List[Tuple[float, float]] = []
        # Scanning logic...
        return obstacles
```

### 📝 Documentation Standards

```python
def calculate_path(
    start: Tuple[float, float], 
    end: Tuple[float, float], 
    obstacles: List[Tuple[float, float]]
) -> List[Tuple[float, float]]:
    """
    A* algoritması kullanarak optimum yolu hesaplar.
    
    Args:
        start: Başlangıç koordinatı (x, y)
        end: Hedef koordinat (x, y)  
        obstacles: Engel koordinatları listesi
        
    Returns:
        Optimum yol koordinatları listesi. Yol bulunamazsa boş liste.
        
    Raises:
        ValueError: Geçersiz koordinat verildiğinde
        
    Example:
        >>> path = calculate_path((0, 0), (10, 10), [(5, 5)])
        >>> print(path)
        [(0, 0), (1, 1), (2, 2), ..., (10, 10)]
        
    Note:
        Bu fonksiyon hesaplama açısından pahalıdır. Büyük haritalar için
        optimize edilmiş versiyonunu kullanın.
    """
    if not _validate_coordinates(start, end):
        raise ValueError("Geçersiz koordinat formatı")
        
    # A* implementation...
    return path
```

## 🧪 Testing Strategy

### 🎯 Test Kategorileri

```python
# tests/conftest.py - Pytest fixtures
import pytest
from unittest.mock import Mock
from src.robot.core import Robot

@pytest.fixture
def mock_robot():
    """Mock robot instance for testing"""
    robot = Mock(spec=Robot)
    robot.position = (0.0, 0.0)
    robot.is_moving = False
    return robot

@pytest.fixture 
def test_config():
    """Test configuration"""
    return {
        'motor_speed': 50,
        'sensor_timeout': 1.0,
        'debug_mode': True
    }

# Unit Tests
# tests/test_navigation.py
import pytest
from src.robot.navigation import PathPlanner

class TestPathPlanner:
    def test_simple_path(self):
        """Test basic path planning"""
        planner = PathPlanner()
        path = planner.plan_path((0, 0), (5, 5))
        
        assert len(path) > 0
        assert path[0] == (0, 0)
        assert path[-1] == (5, 5)
        
    def test_obstacle_avoidance(self):
        """Test obstacle avoidance"""
        planner = PathPlanner()
        obstacles = [(2, 2), (3, 3)]
        path = planner.plan_path((0, 0), (5, 5), obstacles)
        
        # Path should not go through obstacles
        for obstacle in obstacles:
            assert obstacle not in path
            
    @pytest.mark.parametrize("start,end,expected_length", [
        ((0, 0), (1, 1), 2),
        ((0, 0), (0, 5), 6),
        ((2, 2), (2, 2), 1)  # Same start/end
    ])
    def test_path_lengths(self, start, end, expected_length):
        """Test expected path lengths"""
        planner = PathPlanner()
        path = planner.plan_path(start, end)
        assert len(path) == expected_length
```

### 🏃‍♂️ Integration Tests

```python
# tests/test_integration.py
import pytest
import time
from src.robot.core import Robot

class TestRobotIntegration:
    @pytest.fixture(scope="class")
    def robot(self):
        """Real robot instance for integration tests"""
        config = {
            'simulation_mode': True,  # Hardware gerektirmez
            'debug_mode': True
        }
        robot = Robot(config)
        yield robot
        robot.shutdown()
        
    def test_full_movement_cycle(self, robot):
        """Test complete movement cycle"""
        # Start position
        initial_pos = robot.get_position()
        
        # Move forward
        robot.move_forward(distance=1.0)
        time.sleep(0.1)  # Allow movement
        
        pos_after_forward = robot.get_position()
        assert pos_after_forward != initial_pos
        
        # Return to start
        robot.move_to_position(initial_pos)
        time.sleep(0.1)
        
        final_pos = robot.get_position()
        assert abs(final_pos[0] - initial_pos[0]) < 0.1
        assert abs(final_pos[1] - initial_pos[1]) < 0.1
        
    def test_sensor_reading_consistency(self, robot):
        """Test sensor reading consistency"""
        readings = []
        for _ in range(5):
            reading = robot.get_ultrasonic_distance()
            readings.append(reading)
            time.sleep(0.1)
            
        # Readings should be consistent (±10%)
        avg_reading = sum(readings) / len(readings)
        for reading in readings:
            assert abs(reading - avg_reading) / avg_reading < 0.1
```

### 🎭 Hardware Mocking

```python
# tests/mocks/hardware.py
from unittest.mock import Mock
import random

class MockGPIO:
    """GPIO mock for testing without hardware"""
    OUT = 1
    IN = 0
    HIGH = 1
    LOW = 0
    
    _pin_states = {}
    
    @classmethod
    def setup(cls, pin, mode):
        cls._pin_states[pin] = cls.LOW if mode == cls.OUT else None
        
    @classmethod  
    def output(cls, pin, state):
        cls._pin_states[pin] = state
        
    @classmethod
    def input(cls, pin):
        return cls._pin_states.get(pin, cls.LOW)
        
class MockCamera:
    """Camera mock for testing"""
    def __init__(self):
        self.is_open = False
        
    def open(self):
        self.is_open = True
        return True
        
    def capture_frame(self):
        if not self.is_open:
            raise RuntimeError("Camera not open")
        # Return dummy frame
        return np.zeros((480, 640, 3), dtype=np.uint8)
        
    def close(self):
        self.is_open = False

# tests/conftest.py - Mock injection
@pytest.fixture(autouse=True)
def mock_hardware(monkeypatch):
    """Automatically mock hardware for all tests"""
    monkeypatch.setattr('RPi.GPIO', MockGPIO())
    monkeypatch.setattr('src.robot.camera.Camera', MockCamera)
```

## 🔄 Git Workflow

### 🌿 Branch Strategy

```bash
# Branch naming convention
main                    # Production ready code
develop                # Integration branch
feature/sensor-fusion   # Feature branches
bugfix/motor-calibration # Bug fix branches  
hotfix/emergency-stop   # Critical fixes
release/v2.1.0         # Release preparation

# Workflow example
git checkout develop
git pull origin develop
git checkout -b feature/new-sensor-support

# ... development work ...

git add .
git commit -m "feat: add MPU9250 IMU sensor support

- Add MPU9250 driver class
- Implement 9-axis sensor reading
- Add calibration procedures
- Update sensor manager integration
- Add unit tests for new sensor

Closes #123"

git push origin feature/new-sensor-support
# Create pull request to develop
```

### 📝 Commit Message Convention

```bash
# Format: <type>(<scope>): <subject>
# 
# <body>
# 
# <footer>

# Types:
feat:     # New feature
fix:      # Bug fix
docs:     # Documentation
style:    # Formatting, no code change  
refactor: # Code change that neither fixes bug nor adds feature
test:     # Adding tests
chore:    # Maintenance

# Examples:
feat(sensors): add temperature sensor support
fix(motors): resolve PWM frequency issue
docs(api): update REST endpoint documentation
test(navigation): add path planning unit tests
refactor(camera): simplify image processing pipeline
```

### 🔍 Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files
    -   id: check-merge-conflict

-   repo: https://github.com/psf/black
    rev: 22.10.0
    hooks:
    -   id: black
        language_version: python3

-   repo: https://github.com/pycqa/flake8
    rev: 5.0.4
    hooks:
    -   id: flake8

-   repo: https://github.com/pre-commit/mirrors-mypy  
    rev: v0.991
    hooks:
    -   id: mypy
        additional_dependencies: [types-all]

-   repo: local
    hooks:
    -   id: pytest
        name: pytest
        entry: pytest tests/ -v
        language: system
        pass_filenames: false
        always_run: true
```

## 🚀 Build & Deploy

### 📦 Build Process

```bash
# build.sh - Production build script
#!/bin/bash

echo "🔨 OBA Robot Build Process"

# 1. Environment check
python --version
node --version
git status

# 2. Clean previous builds  
rm -rf dist/ build/ *.egg-info/
rm -rf src/web/static/dist/

# 3. Install dependencies
pip install -r requirements.txt
npm install

# 4. Run tests
python -m pytest tests/ --cov=src/ --cov-report=html
if [ $? -ne 0 ]; then
    echo "❌ Tests failed, build aborted"
    exit 1
fi

# 5. Type checking
mypy src/
if [ $? -ne 0 ]; then
    echo "❌ Type checking failed"
    exit 1
fi

# 6. Build web assets
npm run build

# 7. Build Python package
python setup.py sdist bdist_wheel

# 8. Build Docker image
docker build -t oba-robot:latest .

echo "✅ Build completed successfully!"
```

### 🐳 Docker Setup

```dockerfile
# Dockerfile
FROM python:3.9-slim-buster

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY configs/ ./configs/

# Create non-root user
RUN useradd -m -u 1000 robot && chown -R robot:robot /app
USER robot

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start application
CMD ["python", "src/main.py"]
```

```yaml
# docker-compose.yml - Development environment
version: '3.8'

services:
  robot:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./src:/app/src
      - ./configs:/app/configs
      - /dev:/dev  # Hardware access
    environment:
      - DEBUG=1
      - LOG_LEVEL=DEBUG
    privileged: true  # GPIO access
    
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
      
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - robot
```

### 🚀 Deployment Pipeline

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10']
        
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
        
    - name: Lint with flake8
      run: flake8 src/ tests/
      
    - name: Type check with mypy
      run: mypy src/
      
    - name: Test with pytest
      run: pytest tests/ --cov=src/ --cov-report=xml
      
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      
  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: docker build -t oba-robot:${{ github.sha }} .
      
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push oba-robot:${{ github.sha }}
        
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to production
      run: |
        ssh ${{ secrets.PROD_USER }}@${{ secrets.PROD_HOST }} \
        "docker pull oba-robot:${{ github.sha }} && \
         docker stop oba-robot || true && \
         docker run -d --name oba-robot --rm -p 8080:8080 oba-robot:${{ github.sha }}"
```

## 🐛 Debugging Guide

### 🔍 Debugging Tools

```python
# debug_utils.py - Debugging utilities
import logging
import time
import functools
import traceback

def setup_logging():
    """Setup comprehensive logging"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('debug.log'),
            logging.StreamHandler()
        ]
    )

def debug_trace(func):
    """Debug decorator to trace function calls"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.debug(f"{func.__name__} completed in {duration:.4f}s, result={result}")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed: {e}")
            logger.error(traceback.format_exc())
            raise
    return wrapper

# Usage example
@debug_trace
def move_robot(distance):
    # Function implementation
    pass
```

### 🔧 Hardware Debugging

```python
# hardware_debug.py
import RPi.GPIO as GPIO
import time

class GPIODebugger:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        
    def test_pin(self, pin_num):
        """Test individual GPIO pin"""
        print(f"Testing GPIO pin {pin_num}")
        
        # Test as output
        GPIO.setup(pin_num, GPIO.OUT)
        for state in [GPIO.HIGH, GPIO.LOW]:
            GPIO.output(pin_num, state)
            print(f"Pin {pin_num} set to {'HIGH' if state else 'LOW'}")
            time.sleep(1)
            
        # Test as input
        GPIO.setup(pin_num, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        for _ in range(5):
            state = GPIO.input(pin_num)
            print(f"Pin {pin_num} reads: {'HIGH' if state else 'LOW'}")
            time.sleep(0.5)
            
    def scan_i2c_devices(self):
        """Scan for I2C devices"""
        import smbus
        bus = smbus.SMBus(1)
        
        print("Scanning I2C bus...")
        devices = []
        for addr in range(0x03, 0x78):
            try:
                bus.read_byte(addr)
                devices.append(hex(addr))
            except:
                pass
                
        if devices:
            print(f"Found I2C devices: {', '.join(devices)}")
        else:
            print("No I2C devices found")
```

## 📊 Performance Monitoring

### 📈 Profiling Tools

```python
# profiler.py
import cProfile
import pstats
import io
import time
import psutil
import threading

class PerformanceProfiler:
    def __init__(self):
        self.profiler = cProfile.Profile()
        self.monitoring = False
        
    def profile_function(self, func, *args, **kwargs):
        """Profile a specific function"""
        self.profiler.enable()
        result = func(*args, **kwargs)
        self.profiler.disable()
        
        # Print results
        s = io.StringIO()
        ps = pstats.Stats(self.profiler, stream=s)
        ps.sort_stats('cumulative')
        ps.print_stats()
        print(s.getvalue())
        
        return result
        
    def start_monitoring(self):
        """Start system monitoring"""
        self.monitoring = True
        threading.Thread(target=self._monitor_system, daemon=True).start()
        
    def _monitor_system(self):
        """Monitor system resources"""
        while self.monitoring:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            print(f"CPU: {cpu_percent}% | RAM: {memory.percent}% | Disk: {disk.percent}%")
            time.sleep(5)
```

## 💡 Best Practices

### 🏆 Development Best Practices

```python
# ✅ Good Practices

# 1. Use type hints everywhere
def calculate_distance(point1: Tuple[float, float], 
                      point2: Tuple[float, float]) -> float:
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

# 2. Use dataclasses for structured data
from dataclasses import dataclass

@dataclass
class SensorReading:
    sensor_type: str
    value: float
    timestamp: float
    unit: str = "unknown"

# 3. Use context managers for resources
class Camera:
    def __enter__(self):
        self.open()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Usage:
with Camera() as cam:
    frame = cam.capture()

# 4. Use enums for constants
from enum import Enum

class RobotState(Enum):
    IDLE = "idle"
    MOVING = "moving" 
    CHARGING = "charging"
    ERROR = "error"

# 5. Use logging instead of print
import logging
logger = logging.getLogger(__name__)

def move_forward(distance):
    logger.info(f"Moving forward {distance} units")
    # implementation...
    logger.debug("Movement completed successfully")
```

### ❌ Anti-patterns to Avoid

```python
# ❌ Bad Practices - Avoid these!

# 1. Magic numbers
speed = 127  # What is 127? PWM value? Percentage?

# ✅ Better:
MAX_PWM_VALUE = 255
speed = MAX_PWM_VALUE // 2  # 50% speed

# 2. Global variables
current_position = (0, 0)  # Global state is bad

# ✅ Better: Use a class
class Robot:
    def __init__(self):
        self.current_position = (0, 0)

# 3. Ignoring exceptions
try:
    sensor_value = read_sensor()
except:
    pass  # Silent failure is dangerous!

# ✅ Better:
try:
    sensor_value = read_sensor()
except SensorError as e:
    logger.error(f"Sensor read failed: {e}")
    sensor_value = get_default_value()

# 4. Long functions
def robot_main_loop():  # 200+ lines function
    # Too much responsibility!

# ✅ Better: Break into smaller functions
def robot_main_loop():
    update_sensors()
    plan_movement()
    execute_movement()
    update_status()
```

## 🆘 Troubleshooting

### 🐛 Common Issues

```bash
# Issue: Permission denied for GPIO
sudo usermod -a -G gpio $USER
# Logout and login again

# Issue: I2C not working
sudo raspi-config  # Enable I2C
sudo apt-get install python3-smbus

# Issue: Camera not detected
sudo raspi-config  # Enable camera
sudo modprobe bcm2835-v4l2

# Issue: Import errors
export PYTHONPATH="${PYTHONPATH}:/path/to/project/src"

# Issue: Port already in use
sudo lsof -i :8080
sudo kill -9 <PID>

# Issue: GPIO cleanup errors
# Add to your code:
import atexit
atexit.register(GPIO.cleanup)
```

### 📞 Getting Help

```bash
# 🆘 Help Channels
Slack: #development-help
Email: dev-support@oba-robot.com
Forum: forum.oba-robot.com
Wiki: wiki.oba-robot.com

# 🐛 Bug Reports
GitHub Issues: github.com/oba-robot/issues
Priority: Critical > High > Medium > Low
Template: Use issue templates

# 📖 Documentation
API Docs: docs.oba-robot.com/api
Tutorials: docs.oba-robot.com/tutorials  
Examples: examples.oba-robot.com
```

## 🎯 Sonuç

Bu development guide ile OBA Robot projesinde verimli bir şekilde çalışabilirsiniz! Unutmayın:

1. **Code Quality**: Her zaman temiz, okunabilir kod yazın
2. **Testing**: Test yazmadan kod yazmayın  
3. **Documentation**: Kod yazdığınız kadar doküman da yazın
4. **Collaboration**: Ekip çalışmasını unutmayın
5. **Learning**: Sürekli öğrenmeye açık olun

**Hacı Abi'nin Dev Mantras:**
- "Çalışan kod yazmak kolay, sürdürülebilir kod yazmak zor!"
- "Bug'lar kaçınılmaz, ama test edilmemiş bug'lar utanç verici!"
- "İyi geliştirici kod yazar, büyük geliştirici kod okur!"
- "Documentation yazmak gelecekteki kendinize hediye!"

---

**📞 Development Support:**
- Slack: #development  
- E-posta: dev@oba-robot.com
- Ofis: Dev Lab, 3. kat (kahve makinesi yanında! ☕)
- Office Hours: Pazartesi-Cuma 09:00-17:00

**Son Güncelleme**: 15 Aralık 2024  
**Hazırlayan**: Hacı Abi & Development Team 👨‍💻  
**Versiyon**: v1.0.0 ✅

*"En iyi kod, anlaşılabilen koddur!"* - Hacı Abi'nin geliştirme felsefesi 🚀
