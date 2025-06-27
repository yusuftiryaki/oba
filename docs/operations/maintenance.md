# 🔧 Bakım ve Onarım Kılavuzu

## 📋 İçindekiler
1. [Periyodik Bakım Takvimi](#periyodik-bakım-takvimi)
2. [Günlük Kontroller](#günlük-kontroller)
3. [Haftalık Bakım](#haftalık-bakım)
4. [Aylık Bakım](#aylık-bakım)
5. [Mevsimlik Bakım](#mevsimlik-bakım)
6. [Parça Değiştirme](#parça-değiştirme)
7. [Sorun Giderme](#sorun-giderme)
8. [Yedek Parça Listesi](#yedek-parça-listesi)

## 🗓️ Periyodik Bakım Takvimi

### Günlük (Her Kullanım Sonrası)
- [ ] **Temizlik**: Gövde ve biçme ünitesinin temizlenmesi
- [ ] **Görsel Kontrol**: Hasarlar, çatlaklar, gevşek bağlantılar
- [ ] **Batarya Durumu**: Şarj seviyesi ve bağlantı kontrolleri
- [ ] **Güvenlik Sensörleri**: Çarpışma ve yağmur sensörü testi

### Haftalık
- [ ] **Tekerlek Kontrolü**: Aşınma, hasar, yabancı madde kontrolü
- [ ] **Motor Test**: Ses, titreşim, sıcaklık kontrolleri
- [ ] **Kablaj Kontrolü**: Bağlantılar, izolasyon, yıpranma
- [ ] **Web Arayüzü**: Tüm fonksiyonların çalışma testi

### Aylık
- [ ] **Derin Temizlik**: Tüm bileşenlerin detaylı temizlenmesi
- [ ] **Kalibrasyon**: Sensör ve navigation kalibrasyonu
- [ ] **Yazılım Güncelleme**: Mevcut güncellemelerin kontrolü
- [ ] **Performans Testi**: Hız, hassasiyet, batarya testleri

### Mevsimlik (3 Ayda Bir)
- [ ] **Komple Demontaj**: Ana bileşenlerin ayrılması ve kontrolü
- [ ] **Elektriksel Test**: Tüm devrelerin test edilmesi
- [ ] **Mekanik Yağlama**: Hareketli parçaların yağlanması
- [ ] **Doküman Güncelleme**: Bakım kayıtlarının güncellenmesi

## 🔍 Günlük Kontroller

### 1. Görsel İnceleme

#### Gövde Kontrolü
```bash
✓ Çatlak veya kırık kontrol
✓ Vida ve bağlantı gevşekliği
✓ Boya ve kaplama durumu
✓ Su sızıntısı izleri
```

#### Biçme Ünitesi
```bash
✓ Bıçak keskinliği ve durumu
✓ Bıçak koruma kapağı
✓ Motor bağlantıları
✓ Debris (çim artığı) temizliği
```

### 2. Fonksiyonel Testler

#### Hareket Testi
```python
# Test scripti: scripts/daily_check.py
import sys
sys.path.append('src')
from hardware.motor_controller import MotorController

def daily_movement_test():
    motor = MotorController()
    
    # İleri/geri test
    print("İleri hareket testi...")
    motor.move_forward(speed=0.2, duration=2)
    
    print("Geri hareket testi...")  
    motor.move_backward(speed=0.2, duration=2)
    
    # Dönüş testi
    print("Sağa dönüş testi...")
    motor.turn_right(speed=0.3, duration=1)
    
    print("Sola dönüş testi...")
    motor.turn_left(speed=0.3, duration=1)
    
    motor.stop()
    print("✅ Hareket testleri tamamlandı")

if __name__ == "__main__":
    daily_movement_test()
```

#### Sensör Testi
```python
# Test scripti: scripts/sensor_check.py
def daily_sensor_test():
    from navigation.kalman_odometry import KalmanOdometry
    from hardware.power_manager import PowerManager
    
    # Odometri testi
    odometry = KalmanOdometry()
    position = odometry.get_position()
    print(f"Mevcut pozisyon: {position}")
    
    # Güç sistemi testi
    power = PowerManager()
    battery_level = power.get_battery_level()
    print(f"Batarya seviyesi: {battery_level}%")
    
    if battery_level < 20:
        print("⚠️ UYARI: Batarya seviyesi düşük!")
    
    print("✅ Sensör testleri tamamlandı")
```

## 🔧 Haftalık Bakım

### 1. Tekerlek Bakımı

#### Kontrol Listesi
- [ ] **Lastik Basıncı**: Uygun basınç (1.5 bar)
- [ ] **Yüzey Aşınması**: Düzgün aşınma kontrolü
- [ ] **Rulman Sesleri**: Anormal ses kontrolü
- [ ] **Teker Ayarı**: Paralel ayar kontrolü

#### Temizlik Prosedürü
```bash
1. Robotu güvenli konuma getir
2. Güç sistemini kapat
3. Her tekeri ayrı ayrı temizle
4. Rulmanları kontrol et
5. Gerekirse yağlama yap
6. Sistem testini gerçekleştir
```

### 2. Motor Kontrolü

#### Performans Ölçümü
```python
# Motor performans testi
def weekly_motor_test():
    import time
    from hardware.motor_controller import MotorController
    
    motor = MotorController()
    
    # Sıcaklık ölçümü
    temp_initial = motor.get_temperature()
    print(f"Başlangıç sıcaklığı: {temp_initial}°C")
    
    # 5 dakika çalışma testi
    start_time = time.time()
    motor.move_forward(speed=0.5, duration=300)
    
    # Final sıcaklık
    temp_final = motor.get_temperature()
    print(f"Final sıcaklığı: {temp_final}°C")
    
    temp_rise = temp_final - temp_initial
    if temp_rise > 20:
        print("⚠️ UYARI: Motor aşırı ısınıyor!")
    
    motor.stop()
```

## 🔩 Aylık Bakım

### 1. Kalibrasyon İşlemleri

#### Navigation Kalibrasyonu
```python
# Aylık kalibrasyon scripti
def monthly_calibration():
    from tests.odometry_calibration import run_calibration
    
    print("🎯 Odometri kalibrasyonu başlatılıyor...")
    
    # 10 metre düz hat testi
    result = run_calibration(distance=10.0)
    
    if result['accuracy'] < 0.95:
        print("⚠️ Kalibrasyon gerekli!")
        # Otomatik kalibrasyon
        run_auto_calibration()
    else:
        print("✅ Kalibrasyon başarılı")
    
    return result
```

#### Sensör Kalibrasyonu
```python
def sensor_calibration():
    # Gyroscope kalibrasyonu
    print("Gyroscope kalibrasyonu - 30 saniye sabit durun...")
    time.sleep(30)
    
    # Accelerometer kalibrasyonu  
    print("Accelerometer kalibrasyonu...")
    # X, Y, Z eksen kalibrasyonu
    
    # Compass kalibrasyonu
    print("Compass kalibrasyonu - 360° dönüş yapın...")
    # Otomatik dönüş ve kalibrasyon
```

### 2. Yazılım Güncelleme

#### Update Kontrolü
```python
def check_for_updates():
    import requests
    import json
    
    try:
        # GitHub'dan son sürüm kontrolü
        response = requests.get("https://api.github.com/repos/oba-robot/releases/latest")
        latest_version = response.json()["tag_name"]
        
        # Mevcut sürüm
        with open("config/config.json", "r") as f:
            config = json.load(f)
            current_version = config["system"]["version"]
        
        if latest_version != current_version:
            print(f"🆕 Yeni sürüm mevcut: {latest_version}")
            return True
        else:
            print("✅ Güncel sürüm kullanılıyor")
            return False
            
    except Exception as e:
        print(f"❌ Güncelleme kontrolü başarısız: {e}")
        return False
```

## ⚡ Mevsimlik Bakım

### Kış Hazırlığı (Ekim-Kasım)
```bash
# Kış depolama prosedürü
1. Son derin temizlik
2. Bataryayı %50 şarj et
3. Serin, kuru yerde depola
4. Aylık şarj kontrolü
5. Plastik koruyucu örtü
```

### Bahar Aktivasyonu (Mart-Nisan)
```bash
# Bahar reaktivasyon
1. Görsel kontrol
2. Batarya şarj testi
3. Tam kalibrasyon
4. Test sürüşü
5. Yazılım güncelleme
```

## 🛠️ Parça Değiştirme

### Batarya Değişimi

#### Gerekli Malzemeler
- Yeni Li-Po batarya (14.8V, 5000mAh)
- Tornavida seti
- Multimetre
- İzolasyon bandı

#### Prosedür
```bash
1. ⚠️ GÜVENLİK: Tüm güç kaynakları kapalı
2. Eski bataryayı çıkar (4 vida)
3. Bağlantıları not et/fotoğrafla
4. Yeni bataryayı bağla
5. Polarite kontrolü (KIRMIZI=+, SİYAH=-)
6. Test ölçümü (14.8V ±0.2V)
7. Güvenlik kapağını kapat
8. İlk şarj testi (30 dakika)
```

### Bıçak Değişimi

#### Güvenlik Uyarıları
⚠️ **UYARI**: Bıçak keskindir! Eldiven kullanın!
⚠️ **UYARI**: Motor tamamen durdurulmuş olmalı!

#### Değişim Adımları
```bash
1. Motor gücünü kes
2. Koruyucu eldiven giy
3. Bıçak sabitleme vidasını gevşet
4. Eski bıçağı çıkar
5. Yeni bıçağı yerleştir
6. Vida sıkma torku: 5 Nm
7. Koruma kapağını kapat
8. Test sürüşü (düşük hız)
```

## 🚨 Sorun Giderme

### Yaygın Problemler ve Çözümleri

#### Problem: Robot hareket etmiyor
```bash
Kontrol Listesi:
□ Güç anahtarı açık mı?
□ Batarya şarjı yeterli mi? (>10%)
□ Acil durdurma butonu basılı mı?
□ Motor sürücü LED'i yanıyor mu?
□ Web arayüzünde hata mesajı var mı?

Çözüm Adımları:
1. Güç sistemini yeniden başlat
2. Bataryayı şarj et
3. Acil durdurmayı sıfırla
4. Motor bağlantılarını kontrol et
5. Log dosyalarını incele
```

#### Problem: Navigation hatası
```bash
Semptomlar:
- Robot kayboldu
- Yanlış yöne gidiyor
- Docking başarısız

Çözüm:
1. Manuel konuma götür
2. Odometry reset yap
3. Kalibrasyon çalıştır
4. Sensör temizliği yap
5. GPS koordinatlarını güncelle
```

#### Problem: Web arayüzüne bağlanmıyor
```bash
Kontrol:
□ WiFi bağlantısı aktif mi?
□ IP adresi doğru mu? (192.168.1.100)
□ Port 8080 açık mı?
□ Firewall engeli var mı?

Terminal Test:
ping 192.168.1.100
telnet 192.168.1.100 8080
```

### Hata Kodları

| Kod | Açıklama | Çözüm |
|-----|----------|-------|
| E001 | Batarya düşük | Şarj edin |
| E002 | Motor arızası | Motor kontrolcü restart |
| E003 | Sensör hatası | Sensör temizliği/kalibrasyon |
| E004 | Navigation kayıp | Manual reset |
| E005 | WiFi bağlantı yok | Network ayarları |
| E006 | Docking hatası | İstasyon pozisyon kontrolü |

## 📦 Yedek Parça Listesi

### Kritik Parçalar (Mutlaka Bulundurulmalı)
```bash
📦 Batarya (Li-Po 14.8V 5000mAh) - 1 adet
🔩 Motor sürücü kartı - 1 adet  
⚙️ Biçme motoru - 1 adet
🛞 Teker (2 adet set) - 1 set
🔪 Yedek bıçak - 3 adet
📡 WiFi anteni - 1 adet
🔌 Şarj adaptörü - 1 adet
```

### Sarf Malzemeler
```bash
🔧 Vida takımı (M3, M4, M5)
🔗 Kablo bağları (20 adet)
📼 İzolasyon bandı
🧼 Temizlik malzemeleri
🛢️ Elektronik spreyler
🧤 İş eldivenleri
```

### Opsiyonel Parçalar
```bash
📹 Yedek kamera modülü
🌡️ Sıcaklık sensörü
💾 microSD kart (32GB)
🔊 Buzzer (sesli uyarı)
💡 LED şerit (status gösterge)
```

## 📊 Bakım Kayıt Formu

### Günlük Bakım Kaydı
```markdown
📅 Tarih: ___________
👤 Yapan: ___________

Görsel Kontrol:
□ Gövde durumu: İYİ / KÖTÜ
□ Biçme ünitesi: İYİ / KÖTÜ  
□ Kablaj: İYİ / KÖTÜ
□ Tekerlekler: İYİ / KÖTÜ

Fonksiyonel Test:
□ Hareket testi: BAŞARILI / BAŞARISIZ
□ Biçme testi: BAŞARILI / BAŞARISIZ
□ Güvenlik: BAŞARILI / BAŞARISIZ

Batarya:
Şarj seviyesi: ____%
Şarj süresi: ___ dakika

Notlar:
_________________________________
_________________________________
```

## 🎯 Bakım KPI'ları

### Hedef Metrikler
- **Çalışma Süresi**: >95% uptime
- **Bakım Sıklığı**: Haftalık <2 saat
- **Parça Ömrü**: Bıçak >200 saat
- **Batarya Ömrü**: >500 şarj döngüsü
- **MTBF**: >1000 saat (Mean Time Between Failures)

### Performans Takibi
```python
# Bakım metrik takibi
def track_maintenance_metrics():
    with open("logs/maintenance.log", "a") as f:
        timestamp = datetime.now().isoformat()
        uptime = get_system_uptime()
        battery_cycles = get_battery_cycles()
        blade_hours = get_blade_usage_hours()
        
        f.write(f"{timestamp},{uptime},{battery_cycles},{blade_hours}\n")
```

---

## 📞 Teknik Destek

### Acil Durum İletişim
- **Teknik Destek**: +90 XXX XXX XXXX
- **E-posta**: support@oba-robot.com
- **Online Chat**: www.oba-robot.com/support

### Doküman Güncelleme
Bu doküman sürekli güncellenmektedir. En son sürüm için:
- GitHub: [oba-robot/docs](https://github.com/oba-robot/docs)
- Wiki: [oba-robot.wiki](https://wiki.oba-robot.com)

---

*Bu dokümantasyon OBA Robot v1.0 için hazırlanmıştır. Güvenlik kurallarına uyarak bakım işlemlerini gerçekleştirin!*
