# OBA - Montaj ve Kurulum Kılavuzu

## 🔧 Donanım Montajı

### 1. Şasi ve Palet Sistemi
```
UYARI: Tüm elektriksel bağlantılar yapılmadan önce güç kapalı olmalıdır!
```

#### Gerekli Malzemeler:
- Paletli şasi (özel imalat)
- 2x BLDC motor (paletler için)
- 2x Yüksek çözünürlüklü enkoder
- Motor montaj flanşları
- M8 civata seti

#### Montaj Adımları:
1. **Palet Motorlarının Montajı**:
   - Sol ve sağ palet motorlarını şasi üzerine monte edin
   - Motor flanşlarının sıkı olduğundan emin olun (25 Nm tork)
   - Enkoderleri motor millerine yerleştirin

2. **Kablo Yönetimi**:
   - Motor kablolarını şasi içinde güvenli bir şekilde yönlendirin
   - Enkoder kablolarını ayrı bir kanaldan geçirin (girişim önleme)

### 2. Biçme Sistemi

#### Gerekli Malzemeler:
- BLDC biçme motoru
- Misina kartuşu ve koruma kapağı
- Lineer aktüatör (yükseklik ayarı)
- Yükseklik ayar mekanizması

#### Montaj Adımları:
1. **Biçme Motorunun Montajı**:
   - Biçme motorunu robot ön kısmına monte edin
   - Koruma kapağını yerleştirin
   - Misina kartuşunu takın

2. **Yükseklik Ayar Sistemi**:
   - Lineer aktüatörü biçme ünitesi altına monte edin
   - Mekanik bağlantıları kontrol edin
   - Test hareketi yapın (güç olmadan)

### 3. Elektronik Sistemler

#### Ana Kontrolcü Montajı:
```
Raspberry Pi 4B + Çevre Birimleri
├── GPIO Genişletme Kartı
├── Motor Sürücü Kartları (2x)
├── Güç Dağıtım Modülü
└── Sensör Bağlantı Paneli
```

#### Bağlantı Şeması:
```
24V Batarya
│
├── 24V → Motor Sürücüler
│   ├── Sol Palet Motoru (GPIO 12,13)
│   ├── Sağ Palet Motoru (GPIO 16,26)
│   └── Biçme Motoru (GPIO 6,7)
│
├── 12V → DC-DC Dönüştürücü
│   └── Lineer Aktüatör (GPIO 25)
│
└── 5V → DC-DC Dönüştürücü
    ├── Raspberry Pi
    ├── Kamera
    └── Sensörler
```

#### Sensör Bağlantıları:
```
Raspberry Pi GPIO
├── I2C (GPIO 2,3) → BNO055 IMU
├── Enkoder 1 (GPIO 18,19) → Sol Palet
├── Enkoder 2 (GPIO 20,21) → Sağ Palet
├── IR Sensör 1 (GPIO 23) → Docking
├── IR Sensör 2 (GPIO 24) → Docking
└── CSI Port → Pi Kamera V3
```

### 4. Güç Sistemi

#### Batarya ve Şarj Sisteminin Kurulumu:
1. **Robot Bataryası (24V LiFePO4)**:
   - Bataryayı robot gövdesine güvenli şekilde monte edin
   - BMS (Battery Management System) bağlantılarını yapın
   - Şarj portunu robot dışında erişilebilir yere yerleştirin

2. **Güç Dağıtımı**:
   - Ana sigorta (30A) takın
   - Her motor için ayrı sigorta (10A) kullanın
   - Acil durdurma düğmesini ana güç hattına bağlayın

## 💻 Yazılım Kurulumu

### 1. Raspberry Pi OS Kurulumu

#### Gereksinimler:
- Raspberry Pi 4B (min. 4GB RAM)
- 64GB microSD kart (Class 10)
- Ethernet/Wi-Fi bağlantısı

#### Kurulum Adımları:
```bash
# 1. Raspberry Pi Imager ile OS yükleyin
# 2. SSH aktifleştirin
# 3. İlk boot sonrası:

sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip git python3-venv -y

# GPIO ve kamera aktifleştirme
sudo raspi-config
# Interface Options → Camera → Enable
# Interface Options → I2C → Enable
```

### 2. Proje Kodlarının Kurulumu

```bash
# Proje klasörünü oluşturun
cd /home/pi
git clone <proje-repository> ot-bicme
cd ot-bicme

# Python sanal ortamı oluşturun
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Sistem servisini oluşturun
sudo cp install/oba-robot.service /etc/systemd/system/
sudo systemctl enable oba-robot.service
```

### 3. Konfigürasyon

#### config.json Düzenleme:
```json
{
    "robot": {
        "wheel_base": 0.45,
        "wheel_diameter": 0.15,
        "max_speed": 1.0,
        "encoder_ppr": 1024
    },
    "battery": {
        "voltage_nominal": 24.0,
        "capacity_ah": 20.0,
        "low_threshold": 20.0,
        "critical_threshold": 5.0
    },
    "docking": {
        "station_coords": [0.0, 0.0],
        "approach_distance": 5.0,
        "precision_distance": 0.5
    }
}
```

## 🏗️ Şarj İstasyonu Kurulumu

### 1. Mekanik Kurulum
- İstasyonu düz, güneş alan bir alana yerleştirin
- Rüzgar direncini artırmak için zemine sabitleyin
- Docking pedlerini robot şarj portuna uygun şekilde konumlandırın

### 2. Elektriksel Bağlantılar
```
Güneş Paneli (150W)
│
└── MPPT Şarj Regülatörü (20A)
    │
    └── İstasyon Bataryası (100Ah)
        │
        └── DC-DC Şarj Devresi
            │
            └── Robot Şarj Pedleri
```

### 3. İşaretleyici Sistemi
- **AprilTag Yöntemi**: A4 boyutunda basılı AprilTag'i istasyon üzerine sabitleyin
- **IR LED Yöntemi**: Yüksek güçlü IR LED dizisini istasyonun üst kısmına monte edin

## 🧪 Sistem Testleri

### 1. Donanım Testleri

#### Motor Testleri:
```bash
# Test scriptini çalıştırın
python3 tests/hardware_test.py

# Beklenen çıktı:
# ✓ Sol palet motoru - OK
# ✓ Sağ palet motoru - OK  
# ✓ Biçme motoru - OK
# ✓ Lineer aktüatör - OK
```

#### Sensör Testleri:
```bash
python3 tests/sensor_test.py

# Beklenen çıktı:
# ✓ IMU kalibrasyon - OK
# ✓ Enkoder 1 - 1024 PPR
# ✓ Enkoder 2 - 1024 PPR
# ✓ Kamera - 1920x1080
# ✓ IR sensörler - OK
```

### 2. Yazılım Testleri

#### Odometri Kalibrasyonu:
```bash
# 1m düz hareket testi
python3 tests/odometry_calibration.py --distance 1.0

# 360° rotasyon testi  
python3 tests/odometry_calibration.py --rotation 360
```

#### Web Arayüzü Testi:
```bash
# Web sunucusunu başlatın
python3 src/web/web_server.py

# Tarayıcıda şu adresi açın:
# http://robot-ip:5000
```

## 🚨 Güvenlik Kontrolleri

### Pre-Flight Checklist:
- [ ] Acil durdurma düğmesi test edildi
- [ ] Batarya şarj seviyesi >50%
- [ ] Tüm sensörler kalibrasyon edildi
- [ ] Biçme koruma kapağı takılı
- [ ] Çalışma alanı engel temizlendi
- [ ] Web arayüzü bağlantısı test edildi
- [ ] Şarj istasyonu fonksiyonel

### İlk Çalıştırma:
1. **Manuel Kontrol Testi** (10 dakika)
2. **Kısa Mesafe Otonom Hareket** (5m çare)
3. **Biçme Sistemi Testi** (30 saniye)
4. **Docking Testi** (şarj istasyonuna yaklaşma)
5. **Tam Otonom Görev** (küçük alan)

## 📞 Destek ve Sorun Giderme

### Yaygın Sorunlar:

#### "Robot hareket etmiyor"
- Batarya seviyesini kontrol edin
- Motor bağlantılarını gözden geçirin
- GPIO pin konfigürasyonunu doğrulayın

#### "Konum takibi doğru değil"
- Enkoder bağlantılarını kontrol edin
- IMU kalibrasyonu yapın
- Kalman filtre parametrelerini ayarlayın

#### "Web arayüzüne erişilemiyor"
- Wi-Fi bağlantısını kontrol edin
- Firewall ayarlarını gözden geçirin
- Flask sunucu durumunu kontrol edin

### Log Dosyaları:
```bash
# Robot ana log
tail -f logs/oba_main.log

# Web sunucu log
tail -f logs/web_server.log

# Hata log
tail -f logs/errors.log
```

Bu kurulum kılavuzu ile robotunuz çalışır duruma gelecektir. Herhangi bir sorunda log dosyalarını kontrol edin!
