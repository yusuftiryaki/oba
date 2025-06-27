# 🤖 Otonom Bahçe Asistanı (OBA)

Meyve bahçelerinde yabancı ot biçme görevini otonom olarak yerine getiren paletli robot sistemi.

![Robot Status](https://img.shields.io/badge/status-development-yellow)
![Python Version](https://img.shields.io/badge/python-3.9+-blue)
![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%204B-red)
![DevContainer](https://img.shields.io/badge/devcontainer-ready-green)

## 🚀 Hızlı Başlangıç

### 🐳 DevContainer ile Geliştirme (Önerilen)
```bash
# Repository'i klonlayın
git clone <repository-url>
cd ot-bicme

# VS Code'da açın
code .

# DevContainer'da açın: Ctrl+Shift+P → "Dev Containers: Reopen in Container"
# İlk setup 5-10 dakika sürer, sonrasında her şey hazır!

# Robot başlat
oba-start

# Web arayüzü: http://localhost:5000
```

DevContainer tüm dependencies'i, mock hardware'i ve development tools'ları içerir. Detaylar: [DEVCONTAINER.md](./DEVCONTAINER.md)

### 🛠️ Manuel Kurulum
```bash
# Depoyu klonlayın
git clone <repository-url> ot-bicme
cd ot-bicme

# Python sanal ortamı oluşturun
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Konfigürasyonu düzenleyin
cp config/config.json.example config/config.json
```

### 3. Test Çalıştırma
```bash
# Simülasyon modunda başlatın
python main.py --simulate

# Web arayüzüne erişin
# http://localhost:5000
```

## 🎮 Kullanım

### Web Arayüzü
- **Ana Sayfa**: Robot durumu ve temel kontroller
- **Kontrol Paneli**: Manuel hareket kontrolü
- **Canlı Kamera**: Gerçek zamanlı görüntü akışı
- **Alan Yönetimi**: Çalışma alanları tanımlama
- **Ayarlar**: Sistem parametreleri

### Otonom Görev Başlatma
1. Web arayüzünde çalışma alanını seçin
2. Biçme yüksekliğini ayarlayın
3. "Görevi Başlat" butonuna tıklayın
4. Robot otomatik olarak:
   - Alanı tarayarak rota planlar
   - Sistematik biçme işlemi yapar
   - Batarya düştüğünde şarj istasyonuna döner

## 📊 Performans Metrikleri

| Özellik | Değer |
|---------|-------|
| Çalışma Süresi | 2+ saat |
| Konum Hassasiyeti | ±1 metre (1 saat sonunda) |
| Docking Hassasiyeti | ±1 cm |
| Web Arayüzü Gecikmesi | <500ms |
| Maksimum Eğim | ±15% |
| Çalışma Hızı | 0.1-1.0 m/s |

## 🔧 Donanım Konfigürasyonu

### GPIO Pin Haritası
```
Raspberry Pi 4B GPIO
├── GPIO 2,3      → I2C (IMU)
├── GPIO 6,7      → Biçme Motor PWM
├── GPIO 12,13    → Sol Palet PWM
├── GPIO 16,26    → Sağ Palet PWM
├── GPIO 18,19    → Sol Enkoder
├── GPIO 20,21    → Sağ Enkoder
├── GPIO 23,24    → IR Sensörler
├── GPIO 25       → Lineer Aktüatör
└── CSI Port      → Pi Kamera
```

### Güç Dağıtımı
```
24V LiFePO4 → Motor Sürücüler (24V)
            → DC-DC → Raspberry Pi (5V)
            → DC-DC → Sensörler (5V/3.3V)
            → DC-DC → Lineer Aktüatör (12V)
```

## 🧪 Test ve Geliştirme

### Unit Testler
```bash
# Tüm testleri çalıştır
python -m pytest tests/

# Belirli bir modülü test et
python -m pytest tests/test_odometry.py -v

# Donanım testleri (gerçek hardware gerekir)
python tests/hardware_test.py
```

### Kalibrasyon
```bash
# Odometri kalibrasyonu
python tests/odometry_calibration.py

# IMU kalibrasyonu
python tests/imu_calibration.py

# Kamera kalibrasyonu
python tests/camera_calibration.py
```

## 📈 Durum Makinesi

Robot 4 ana durumda çalışır:

1. **BEKLEME**: Sistem hazır, komut bekliyor
2. **BIÇME**: Otonom ot biçme işlemi
3. **ŞARJA_DÖNME**: Batarya düşünce istasyona yönelme
4. **ŞARJ_OLMA**: İstasyonda şarj işlemi

Detaylı durum diyagramı için: [docs/state_machine.md](docs/state_machine.md)

## 🔒 Güvenlik

### Güvenlik Özellikleri:
- ⛔ Acil durdurma düğmesi
- 🚨 Düşük batarya koruması
- 🛡️ Motor overcurrent koruması
- 📱 Web arayüzü authentication
- 🔄 Failsafe durum makinesi

### Güvenlik Kontrolleri:
```bash
# Pre-flight checklist
python scripts/safety_check.py

# Sistem durumu
python scripts/system_status.py
```

## 🐛 Sorun Giderme

### Yaygın Sorunlar:

#### Robot Hareket Etmiyor
```bash
# Motor bağlantılarını kontrol et
python tests/motor_test.py

# GPIO durumunu kontrol et
python scripts/gpio_status.py
```

#### Konum Takibi Hatalı
```bash
# Sensör verilerini kontrol et
python tests/sensor_debug.py

# Kalman filtre parametrelerini ayarla
nano config/config.json
```

#### Web Arayüzü Erişilemiyor
```bash
# Network durumunu kontrol et
ifconfig
ping <robot-ip>

# Web sunucu loglarını kontrol et
tail -f logs/web_server.log
```

### Log Dosyaları:
- `logs/oba_main.log` - Ana sistem logları
- `logs/web_server.log` - Web sunucu logları
- `logs/navigation.log` - Navigasyon logları
- `logs/errors.log` - Hata logları

## 📚 Dokümantasyon

- [Sistem Mimarisi](docs/system_architecture.md)
- [Durum Makinesi](docs/state_machine.md)
- [Kurulum Kılavuzu](docs/installation_guide.md)
- [API Referansı](docs/api_reference.md)

## 🤝 Katkıda Bulunma

1. Fork'layın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit'leyin (`git commit -m 'Add amazing feature'`)
4. Push'layın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📜 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 👥 Geliştirici Ekibi

- **Proje Lideri**: [İsim]
- **Yazılım Geliştirici**: [İsim]
- **Donanım Mühendisi**: [İsim]
- **Test Mühendisi**: [İsim]

## 📞 İletişim

- **E-posta**: [email@example.com]
- **Issues**: GitHub Issues sayfasını kullanın
- **Discussions**: GitHub Discussions

---

⭐ Projeyi beğendiyseniz star vermeyi unutmayın!

## 📋 Changelog

### v1.0.0 (Geliştirme Aşamasında)
- [x] Temel robot hareketi
- [x] Kalman filtreli odometri
- [x] Web arayüzü
- [x] Otonom biçme
- [ ] Docking sistemi
- [ ] Güneş enerjili şarj
- [ ] Sahada test

### Gelecek Sürümler:
- v1.1.0: Gelişmiş engel algılama
- v1.2.0: Çoklu alan yönetimi
- v2.0.0: Yapay zeka entegrasyonu
