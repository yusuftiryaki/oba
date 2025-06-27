# 💻 Kod Geliştirme Kılavuzu

## 📋 İçindekiler
1. [Genel Kod Standartları](#genel-kod-standartları)
2. [Python Kod Kuralları](#python-kod-kuralları)
3. [JavaScript/HTML Kuralları](#javascriptml-kuralları)
4. [Git Workflow](#git-workflow)
5. [Test Yazma Kılavuzu](#test-yazma-kılavuzu)
6. [Dokümantasyon Standartları](#dokümantasyon-standartları)
7. [Code Review Süreci](#code-review-süreci)
8. [Güvenlik Kuralları](#güvenlik-kuralları)

## 📏 Genel Kod Standartları

### Temel İlkeler
```bash
🎯 SOLID Principles
🧹 Clean Code
🔄 DRY (Don't Repeat Yourself)  
🧪 Test-Driven Development
📝 Self-Documenting Code
⚡ Performance-First
🔒 Security-First
```

### Klasör Yapısı Kuralları
```
src/
├── core/           # Ana sistem bileşenleri
├── navigation/     # Navigasyon ve hareket
├── hardware/       # Donanım arayüzleri
├── web/           # Web arayüzü
├── utils/         # Yardımcı fonksiyonlar
└── tests/         # Test dosyaları

config/            # Konfigürasyon dosyaları
docs/             # Dokümantasyon
scripts/          # Yardımcı scriptler
logs/             # Log dosyaları
```

### Dosya İsimlendirme
```bash
✅ DOĞRU:
- main_controller.py
- kalman_odometry.py
- motor_controller.py
- test_navigation.py

❌ YANLIŞ:
- MainController.py
- kalmanOdometry.py
- motorcontroller.py
- testNavigation.py
```

## 🐍 Python Kod Kuralları

### PEP 8 Standartları

#### Import Sıralama
```python
# 1. Standard library imports
import os
import sys
import time
import json
from datetime import datetime

# 2. Related third party imports  
import numpy as np
import flask
from flask import request, jsonify

# 3. Local application/library imports
from core.main_controller import MainController
from navigation.kalman_odometry import KalmanOdometry
from hardware.motor_controller import MotorController
```

#### Fonksiyon ve Sınıf Tanımları
```python
class RobotController:
    """
    Ana robot kontrol sınıfı.
    
    Bu sınıf robotun tüm ana fonksiyonlarını yönetir:
    - Hareket kontrolü
    - Navigasyon sistemi
    - Güvenlik kontrolleri
    
    Attributes:
        state (str): Robotun mevcut durumu
        position (tuple): Robotun pozisyonu (x, y, theta)
        battery_level (float): Batarya seviyesi (0-100)
    
    Example:
        >>> robot = RobotController()
        >>> robot.start_mowing()
        >>> robot.return_to_dock()
    """
    
    def __init__(self, config_path: str = "config/config.json"):
        """
        Robot kontrolcüsünü başlatır.
        
        Args:
            config_path (str): Konfigürasyon dosyası yolu
            
        Raises:
            FileNotFoundError: Konfigürasyon dosyası bulunamazsa
            ValueError: Geçersiz konfigürasyon parametresi
        """
        self.config = self._load_config(config_path)
        self.state = "IDLE"
        self.position = (0.0, 0.0, 0.0)
        self.battery_level = 100.0
        
        # Logger kurulumu
        self.logger = self._setup_logger()
        
    def start_mowing(self, area_id: str = "default") -> bool:
        """
        Biçme işlemini başlatır.
        
        Args:
            area_id (str): Biçilecek alan ID'si
            
        Returns:
            bool: İşlem başarılı ise True
            
        Raises:
            ValueError: Geçersiz alan ID'si
            RuntimeError: Robot hazır değilse
        """
        # Pre-flight kontroller
        if not self._pre_flight_check():
            self.logger.error("Pre-flight kontrol başarısız")
            return False
            
        # Alan doğrulama
        if not self._validate_area(area_id):
            raise ValueError(f"Geçersiz alan ID: {area_id}")
            
        # Biçme başlat
        try:
            self.state = "MOWING"
            self.logger.info(f"Biçme başlatıldı: {area_id}")
            return True
        except Exception as e:
            self.logger.error(f"Biçme başlatma hatası: {e}")
            self.state = "ERROR"
            return False
            
    def _pre_flight_check(self) -> bool:
        """Uçuş öncesi güvenlik kontrolleri."""
        checks = [
            self._check_battery(),
            self._check_motors(),
            self._check_sensors(),
            self._check_connectivity()
        ]
        return all(checks)
```

#### Error Handling
```python
# Specific exceptions first, general exceptions last
try:
    result = dangerous_operation()
except FileNotFoundError as e:
    logger.error(f"Dosya bulunamadı: {e}")
    return None
except PermissionError as e:
    logger.error(f"İzin hatası: {e}")
    return None
except Exception as e:
    logger.error(f"Beklenmeyen hata: {e}")
    raise
finally:
    cleanup_resources()
```

#### Type Hints
```python
from typing import List, Dict, Optional, Union, Tuple

def calculate_path(
    start: Tuple[float, float], 
    goal: Tuple[float, float],
    obstacles: List[Tuple[float, float]],
    max_speed: float = 1.0
) -> Optional[List[Tuple[float, float]]]:
    """
    Başlangıç ve hedef nokta arasında güvenli yol hesaplar.
    
    Args:
        start: Başlangıç koordinatı (x, y)
        goal: Hedef koordinat (x, y)  
        obstacles: Engel koordinat listesi
        max_speed: Maksimum hız (m/s)
        
    Returns:
        Yol koordinat listesi veya None (yol bulunamazsa)
    """
    pass
```

### Logging Standartları

#### Logger Kurulumu
```python
import logging
from datetime import datetime

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Standart logger kurulumu."""
    
    # Logger oluştur
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Handler oluştur
    handler = logging.FileHandler(f"logs/{name}_{datetime.now().strftime('%Y%m%d')}.log")
    handler.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(handler)
    logger.addHandler(console_handler)
    
    return logger

# Kullanım
logger = setup_logger("navigation")
logger.info("Navigasyon sistemi başlatıldı")
logger.warning("Düşük batarya seviyesi: %d%%", battery_level)
logger.error("Motor hatası: %s", error_message)
```

#### Log Seviyeleri
```python
# DEBUG: Geliştirme aşamasında detaylı bilgi
logger.debug("Pozisyon güncellemesi: x=%.2f, y=%.2f", x, y)

# INFO: Normal işlem bilgileri
logger.info("Biçme işlemi başlatıldı")

# WARNING: Potansiyel problemler
logger.warning("Batarya seviyesi düşük: %d%%", battery_level)

# ERROR: Hata durumları (sistem çalışmaya devam eder)
logger.error("Sensör okuma hatası: %s", error)

# CRITICAL: Kritik hatalar (sistem durabilir)
logger.critical("Motor kontrolcü yanıt vermiyor!")
```

## 🌐 JavaScript/HTML Kuralları

### JavaScript Standartları

#### ES6+ Syntax
```javascript
// Arrow functions
const calculateDistance = (x1, y1, x2, y2) => {
    return Math.sqrt((x2-x1)**2 + (y2-y1)**2);
};

// Template literals
const status = `Robot durumu: ${state}, Batarya: ${battery}%`;

// Destructuring
const {x, y, theta} = robot.position;
const [latitude, longitude] = gps.coordinates;

// Async/await
async function fetchRobotStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        updateUI(data);
    } catch (error) {
        console.error('Status alınamadı:', error);
        showErrorMessage('Bağlantı hatası');
    }
}
```

#### DOM Manipulation
```javascript
// Modern DOM selection
const statusPanel = document.querySelector('#status-panel');
const allButtons = document.querySelectorAll('.control-button');

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    initializeUI();
    startStatusUpdates();
});

// Class operations
statusPanel.classList.add('connected');
statusPanel.classList.toggle('active');
statusPanel.classList.remove('error');
```

### HTML5 Semantic Structure
```html
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OBA Robot - Kontrol Paneli</title>
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
    <header>
        <nav aria-label="Ana navigasyon">
            <h1>OBA Robot</h1>
            <ul>
                <li><a href="/" aria-current="page">Dashboard</a></li>
                <li><a href="/control">Kontrol</a></li>
                <li><a href="/areas">Alanlar</a></li>
            </ul>
        </nav>
    </header>
    
    <main>
        <section aria-labelledby="status-heading">
            <h2 id="status-heading">Robot Durumu</h2>
            <div class="status-grid" role="grid">
                <!-- Status cards -->
            </div>
        </section>
        
        <section aria-labelledby="control-heading">
            <h2 id="control-heading">Manuel Kontrol</h2>
            <div class="control-panel" role="group" aria-label="Robot kontrolleri">
                <button type="button" class="btn btn-primary" id="start-btn">
                    Başlat
                </button>
                <button type="button" class="btn btn-danger" id="stop-btn">
                    Durdur
                </button>
            </div>
        </section>
    </main>
    
    <footer>
        <p>&copy; 2024 OBA Robot - Sürüm 1.0</p>
    </footer>
    
    <script src="/static/js/main.js"></script>
</body>
</html>
```

### CSS Standartları
```css
/* CSS Custom Properties */
:root {
    --primary-color: #2ecc71;
    --danger-color: #e74c3c;
    --warning-color: #f39c12;
    --text-color: #2c3e50;
    --bg-color: #ecf0f1;
    --border-radius: 8px;
    --transition: all 0.3s ease;
}

/* BEM Methodology */
.status-card {
    background: white;
    border-radius: var(--border-radius);
    padding: 1rem;
    transition: var(--transition);
}

.status-card__title {
    font-size: 1.2em;
    font-weight: bold;
    color: var(--text-color);
}

.status-card__value {
    font-size: 2em;
    color: var(--primary-color);
}

.status-card--error {
    border-left: 4px solid var(--danger-color);
}

/* Mobile-first responsive design */
.control-panel {
    display: grid;
    gap: 1rem;
    grid-template-columns: 1fr;
}

@media (min-width: 768px) {
    .control-panel {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (min-width: 1024px) {
    .control-panel {
        grid-template-columns: repeat(4, 1fr);
    }
}
```

## 🔄 Git Workflow

### Branch Strategy
```bash
main                 # Production ready code
├── develop         # Integration branch  
├── feature/*       # New features
├── bugfix/*        # Bug fixes
├── hotfix/*        # Critical fixes
└── release/*       # Release preparation
```

### Commit Message Standards
```bash
# Format: <type>(<scope>): <description>

# Types:
feat:     # New feature
fix:      # Bug fix  
docs:     # Documentation
style:    # Code style (formatting, missing semi colons, etc)
refactor: # Code refactoring
test:     # Adding missing tests
chore:    # Maintenance tasks

# Examples:
feat(navigation): add path optimization algorithm
fix(motors): resolve left motor calibration issue
docs(api): update endpoint documentation
test(odometry): add kalman filter unit tests
```

### Pull Request Template
```markdown
## 📝 Açıklama
Bu PR'da yapılan değişikliklerin kısa açıklaması.

## 🎯 Değişiklik Türü
- [ ] 🆕 Yeni özellik (breaking change olmayan)
- [ ] 🐛 Bug fix (breaking change olmayan) 
- [ ] 💥 Breaking change (mevcut fonksiyonaliteyi etkiler)
- [ ] 📚 Dokümantasyon güncelleme

## ✅ Test Edildi
- [ ] Unit testler geçiyor
- [ ] Integration testler geçiyor
- [ ] Manuel test edildi
- [ ] Code review yapıldı

## 📷 Ekran Görüntüleri
Eğer UI değişikliği varsa, önce/sonra görüntüleri.

## 📋 Checklist
- [ ] Kod PEP8 standartlarına uygun
- [ ] Yeni testler eklendi
- [ ] Dokümantasyon güncellendi
- [ ] CHANGELOG.md güncellendi
```

### Pre-commit Hooks
```bash
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.9

  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]

  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## 🧪 Test Yazma Kılavuzu

### Unit Test Yapısı
```python
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from navigation.kalman_odometry import KalmanOdometry

class TestKalmanOdometry(unittest.TestCase):
    """Kalman odometry unit testleri."""
    
    def setUp(self):
        """Her test öncesinde çalışır."""
        self.odometry = KalmanOdometry()
        
    def tearDown(self):
        """Her test sonrasında çalışır."""
        self.odometry = None
        
    def test_initial_position(self):
        """İlk pozisyon testi."""
        position = self.odometry.get_position()
        expected = (0.0, 0.0, 0.0)  # x, y, theta
        
        self.assertEqual(position, expected)
        
    def test_position_update(self):
        """Pozisyon güncelleme testi."""
        # Test verisi
        encoder_left = 100  # encoder counts
        encoder_right = 100
        dt = 0.1  # time delta
        
        # Position update
        self.odometry.update_position(encoder_left, encoder_right, dt)
        
        # Verify position changed
        position = self.odometry.get_position()
        self.assertNotEqual(position[0], 0.0)  # x should change
        
    @patch('navigation.kalman_odometry.GPIO')
    def test_encoder_reading(self, mock_gpio):
        """Encoder okuma testi (mock ile)."""
        # Mock GPIO responses
        mock_gpio.input.side_effect = [1, 0, 1, 0]  # encoder pulses
        
        # Read encoders
        left_count = self.odometry._read_encoder_left()
        right_count = self.odometry._read_encoder_right()
        
        # Verify calls
        self.assertEqual(mock_gpio.input.call_count, 4)
        self.assertIsInstance(left_count, int)
        self.assertIsInstance(right_count, int)
        
    def test_distance_calculation(self):
        """Mesafe hesaplama testi."""
        encoder_counts = 1000
        expected_distance = 1.57  # meters (for our wheel configuration)
        
        distance = self.odometry._counts_to_distance(encoder_counts)
        
        self.assertAlmostEqual(distance, expected_distance, places=2)
        
    def test_invalid_encoder_values(self):
        """Geçersiz encoder değerleri testi."""
        with self.assertRaises(ValueError):
            self.odometry.update_position(-100, 100, 0.1)  # negative encoder
            
        with self.assertRaises(ValueError):
            self.odometry.update_position(100, 100, -0.1)  # negative time

if __name__ == '__main__':
    unittest.main()
```

### Integration Test
```python
import unittest
import time
import requests
from threading import Thread

class TestWebIntegration(unittest.TestCase):
    """Web server integration testleri."""
    
    @classmethod
    def setUpClass(cls):
        """Test sınıfı başlangıcında çalışır."""
        # Start web server in background
        from web.web_server import app
        cls.server_thread = Thread(
            target=app.run, 
            kwargs={'host': '127.0.0.1', 'port': 5000},
            daemon=True
        )
        cls.server_thread.start()
        time.sleep(1)  # Wait for server to start
        
    def test_status_endpoint(self):
        """Status endpoint testi."""
        response = requests.get('http://127.0.0.1:5000/api/status')
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('state', data)
        self.assertIn('position', data)
        self.assertIn('battery_level', data)
        
    def test_control_endpoint(self):
        """Control endpoint testi."""
        # Start command
        response = requests.post(
            'http://127.0.0.1:5000/api/control/start',
            json={'area_id': 'test_area'}
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Stop command
        response = requests.post('http://127.0.0.1:5000/api/control/stop')
        self.assertEqual(response.status_code, 200)
```

### Test Coverage
```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run -m pytest tests/
coverage report -m
coverage html  # HTML report in htmlcov/

# Target: >90% code coverage
```

## 📚 Dokümantasyon Standartları

### Docstring Format (Google Style)
```python
def calculate_motor_speeds(linear_vel: float, angular_vel: float) -> Tuple[float, float]:
    """
    Doğrusal ve açısal hızdan motor hızlarını hesaplar.
    
    Bu fonksiyon differensiyel sürüş kinematiğini kullanarak
    istenen robot hızlarından her bir motorun hızını hesaplar.
    
    Args:
        linear_vel (float): İleri/geri hız (m/s)
        angular_vel (float): Dönüş hızı (rad/s)
        
    Returns:
        Tuple[float, float]: (left_speed, right_speed) m/s cinsinden
        
    Raises:
        ValueError: Hız limitleri aşılırsa
        
    Example:
        >>> left, right = calculate_motor_speeds(0.5, 0.1)
        >>> print(f"Sol: {left:.2f}, Sağ: {right:.2f}")
        Sol: 0.45, Sağ: 0.55
        
    Note:
        Maksimum hız limiti config dosyasından alınır.
        Wheelbase (tekerlek arası mesafe) 0.3 metre kabul edilir.
    """
    pass
```

### README Template
```markdown
# 🤖 Module Name

Kısa modül açıklaması.

## 🎯 Amaç

Bu modülün ne işe yaradığı.

## 📦 Kurulum

```bash
pip install -r requirements.txt
```

## 🚀 Kullanım

```python
from module import Class

# Örnek kullanım
instance = Class()
result = instance.method()
```

## 🔧 Konfigürasyon

| Parametre | Açıklama | Varsayılan |
|-----------|----------|------------|
| param1    | Açıklama | değer      |

## 🧪 Testler

```bash
python -m pytest tests/
```

## 📚 API Referansı

Detaylı API dokümantasyonu için [docs/api.md](docs/api.md)

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun
3. Commit yapın
4. Pull request açın
```

## 👥 Code Review Süreci

### Review Checklist

#### Fonksiyonalite
- [ ] Kod gereksinimi karşılıyor mu?
- [ ] Edge case'ler düşünülmüş mü?
- [ ] Error handling yeterli mi?
- [ ] Performance optimizasyonu yapılmış mı?

#### Kod Kalitesi
- [ ] Clean code prensipleri uygulanmış mı?
- [ ] Fonksiyonlar tek sorumluluk prensibi?
- [ ] Variable isimleri açık ve anlaşılır mı?
- [ ] Magic number'lar constant olarak tanımlanmış mı?

#### Test & Dokümantasyon
- [ ] Unit testler yazılmış mı?
- [ ] Test coverage yeterli mi? (>80%)
- [ ] Docstring'ler eksiksiz mi?
- [ ] Dokümantasyon güncellendi mi?

#### Güvenlik
- [ ] Input validation yapılıyor mu?
- [ ] SQL injection koruması var mı?
- [ ] Sensitive data log'lanmıyor mu?
- [ ] Authentication/authorization doğru mu?

### Review Comments Template
```markdown
# Büyük Problem 🚨
Bu değişiklik sistem güvenliğini etkileyebilir.

# Öneri 💡  
Bu kısmı şöyle yaparsak daha iyi olur: [öneri]

# Küçük İyileştirme ✨
Variable ismi daha açıklayıcı olabilir.

# Soru ❓
Bu fonksiyonun performansı test edildi mi?

# Tebrik 🎉
Harika bir optimizasyon!
```

## 🔒 Güvenlik Kuralları

### Input Validation
```python
def validate_coordinates(x: float, y: float) -> bool:
    """Koordinat validasyonu."""
    
    # Type check
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        raise TypeError("Koordinatlar sayısal olmalı")
        
    # Range check  
    if not (-1000 <= x <= 1000) or not (-1000 <= y <= 1000):
        raise ValueError("Koordinatlar alan sınırları dışında")
        
    # NaN/Inf check
    if math.isnan(x) or math.isnan(y) or math.isinf(x) or math.isinf(y):
        raise ValueError("Geçersiz koordinat değeri")
        
    return True

def sanitize_area_name(name: str) -> str:
    """Alan adını temizle."""
    # Remove dangerous characters
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', name)
    
    # Length limit
    if len(sanitized) > 50:
        sanitized = sanitized[:50]
        
    return sanitized
```

### Secret Management
```python
import os
from cryptography.fernet import Fernet

# Environment variables for secrets
API_KEY = os.environ.get('ROBOT_API_KEY')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

# Never commit secrets to git
# Use .env files with .gitignore

# Encryption for stored secrets
def encrypt_secret(secret: str, key: bytes) -> bytes:
    """Secret'ı şifrele."""
    f = Fernet(key)
    return f.encrypt(secret.encode())

def decrypt_secret(encrypted: bytes, key: bytes) -> str:
    """Secret'ı çöz."""
    f = Fernet(key)
    return f.decrypt(encrypted).decode()
```

### SQL Injection Prevention
```python
# ❌ YANLIŞ - SQL Injection riski
def get_user_data(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute_query(query)

# ✅ DOĞRU - Parametrized query
def get_user_data(user_id: int):
    query = "SELECT * FROM users WHERE id = ?"
    return execute_query(query, (user_id,))
```

## 📊 Performans Standartları

### Profiling
```python
import cProfile
import pstats
from functools import wraps

def profile_function(func):
    """Fonksiyon performans profiling decorator."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        
        result = func(*args, **kwargs)
        
        pr.disable()
        stats = pstats.Stats(pr)
        stats.sort_stats('cumulative')
        stats.print_stats(10)  # Top 10 functions
        
        return result
    return wrapper

# Kullanım
@profile_function
def expensive_calculation():
    # Ağır hesaplama
    pass
```

### Memory Usage
```python
import tracemalloc
import psutil
import os

def monitor_memory_usage():
    """Memory kullanımını monitör et."""
    
    # System memory
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    print(f"RSS Memory: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"VMS Memory: {memory_info.vms / 1024 / 1024:.2f} MB")
    
    # Python memory tracing
    tracemalloc.start()
    
    # Your code here
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory: {current / 1024 / 1024:.2f} MB")
    print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")
    
    tracemalloc.stop()
```

## 🚀 Deployment Checklist

### Production Ready Checklist
- [ ] All tests passing
- [ ] Code coverage >90%
- [ ] No debug code left
- [ ] Logging configured properly
- [ ] Error handling complete
- [ ] Performance tested
- [ ] Security review done
- [ ] Documentation updated
- [ ] Backup plan ready
- [ ] Rollback plan ready

---

## 📞 Yardım ve Destek

### İletişim Kanalları
- **GitHub Issues**: Kod ile ilgili sorular
- **Slack**: #development kanalı
- **E-posta**: dev-team@oba-robot.com

### Kaynaklar
- [Python PEP 8](https://pep8.org/)
- [JavaScript Style Guide](https://github.com/airbnb/javascript)
- [Clean Code Principles](https://clean-code-developer.com/)
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)

---

*Bu kılavuz tüm geliştirici ekibin uyması gereken standartları içerir. Güncellemeler için PR açın!*
