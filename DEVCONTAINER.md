# 🐳 OBA Robot DevContainer Setup

Bu dosya OBA Robot projesini DevContainer ortamında geliştirmek için gerekli tüm ayarlamaları içerir.

## 🚀 Hızlı Başlangıç

### Ön Gereksinimler
- Docker Desktop (Windows/Mac) veya Docker Engine (Linux)
- Visual Studio Code
- Remote - Containers extension

### Container'ı Başlatma

1. **Repository'i klonlayın:**
   ```bash
   git clone <repository-url>
   cd ot-bicme
   ```

2. **VS Code'da açın:**
   ```bash
   code .
   ```

3. **DevContainer'da yeniden açın:**
   - `Ctrl+Shift+P` → "Dev Containers: Reopen in Container"
   - Ya da sol alt köşedeki "><" ikonuna tıklayın

4. **İlk setup bekleyin:**
   - Container build edilecek ve dependencies yüklenecek
   - Bu işlem 5-10 dakika sürebilir

## 🛠️ Container Özellikleri

### Yüklü Olan Tools
- **Python 3.11** + pip, setuptools, wheel
- **Development Tools**: black, pylint, flake8, mypy, pytest
- **Simulation**: pygame, pymunk, matplotlib
- **Web Development**: Flask, gunicorn, redis
- **Computer Vision**: OpenCV, Pillow
- **Hardware Mocking**: fake-rpi, gpiozero simulators

### VS Code Extensions
- Python support with IntelliSense
- Black formatter
- Pylint linting
- Jupyter support
- Docker support
- GitHub Copilot

### Port Forwarding
- **5000**: Flask Web Server
- **8080**: Development Server
- **8888**: Jupyter Lab

## 🔧 Geliştirme Komutları

### Robot Uygulaması
```bash
# Ana robot uygulamasını başlat
oba-start

# Web arayüzünü başlat
oba-web

# Simülasyonu başlat
oba-sim
```

### Test ve Kalite
```bash
# Testleri çalıştır
oba-test

# Kod formatla
oba-format

# Lint kontrolü
oba-lint

# Cache temizle
oba-clean
```

### VS Code Tasks
- `Ctrl+Shift+P` → "Tasks: Run Task" ile erişilebilir:
  - Start Robot Application
  - Start Web Server
  - Run Tests
  - Run Simulation
  - Format Code
  - Lint Code

## 🎮 Mock Mode

Container'da tüm hardware mock mode'da çalışır:

### GPIO Mocking
```python
# fake-rpi kullanılır
import sys
import fake_rpi
sys.modules['RPi'] = fake_rpi.RPi
sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO
```

### Kamera Mocking
```python
# OpenCV test patterns kullanılır
if os.getenv('CAMERA_MOCK') == '1':
    # Mock camera implementation
```

### Environment Variables
- `ROBOT_ENV=development`
- `GPIO_MOCK=1`
- `CAMERA_MOCK=1`
- `DISPLAY=:99` (Virtual display)

## 📁 Önemli Dizinler

```
/workspace/
├── logs/                 # Log dosyaları
├── data/                 # Test verileri
├── temp/                 # Geçici dosyalar
├── simulation/outputs/   # Simülasyon çıktıları
└── test_outputs/         # Test sonuçları
```

## 🌐 Web Arayüzleri

### Robot Web Interface
- URL: http://localhost:5000
- Robot kontrolü ve monitoring

### Jupyter Lab
- URL: http://localhost:8888
- Data analysis ve prototyping
- No password/token required

## 🐛 Debugging

### VS Code Debug Configurations
- **Debug Robot Application**: Ana uygulamayı debug et
- **Debug Web Server**: Web server'ı debug et
- **Debug Tests**: Test'leri debug et
- **Debug Simulation**: Simülasyonu debug et
- **Debug Robot + Web**: İkisini birden debug et

### Debug Environment
```bash
# Debug mode ile başlat
ROBOT_ENV=development python main.py

# Verbose logging
export LOG_LEVEL=DEBUG
```

## 📊 Monitoring ve Logging

### Log Files
```bash
# Ana log
tail -f logs/development.log

# Component logs
tail -f logs/web_server.log
tail -f logs/navigation.log
tail -f logs/hardware.log
```

### Performance Monitoring
```bash
# Memory profiling
memory_profiler python main.py

# Line profiling
kernprof -l -v main.py
```

## 🔄 Development Workflow

### Kod Değişiklikleri
1. Kodunuzu yazın
2. Otomatik formatting (save'de)
3. Lint kontrolleri
4. Test çalıştırın
5. Commit'leyin

### Pre-commit Hooks
- Otomatik code formatting
- Import sorting
- Basic syntax checks

## 🆘 Sorun Giderme

### Container Build Hatası
```bash
# Cache temizle ve rebuild et
docker system prune -a
# VS Code'da: Dev Containers: Rebuild Container
```

### Permission Hatası
```bash
# Container içinde:
sudo chown -R vscode:vscode /workspace
```

### Display Hatası (Simulation)
```bash
# Virtual display kontrol et
ps aux | grep Xvfb

# Yeniden başlat
sudo pkill Xvfb
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
```

### Python Import Hatası
```bash
# Python path kontrol et
echo $PYTHONPATH

# Manuel set et
export PYTHONPATH=/workspace:$PYTHONPATH
```

## 📚 Ek Kaynaklar

- [VS Code DevContainers Documentation](https://code.visualstudio.com/docs/remote/containers)
- [Docker Documentation](https://docs.docker.com/)
- [Robot Project Documentation](./docs/README.md)

## 🤝 Katkıda Bulunma

1. Development environment'ı kurun
2. Feature branch oluşturun
3. Değişikliklerinizi yapın
4. Test'leri çalıştırın
5. Pull request gönderin

---

**Not**: Bu DevContainer setup'ı hem development hem de CI/CD pipeline'lar için kullanılabilir. Production deployment için ayrı container setup'ı kullanılır.
