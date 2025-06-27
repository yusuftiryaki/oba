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
