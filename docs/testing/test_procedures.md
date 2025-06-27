# Test Prosedürleri 🧪

Aha bu sayfa! OBA robotumuzu test etme konusunda Hacı Abi'nin deneyimlerini paylaşacağım. Test yapmak tıpkı doktora gitmek gibi - zaman zaman canını sıkabilir ama zorunlu! 😄

## 🚀 Test Türleri

### 1. Birim Testleri (Unit Tests)
Robottaki her bir komponenti tek tek test ediyoruz:

```bash
# Sensör testleri
python test_sensors.py
# Motor testleri  
python test_motors.py
# Navigasyon testleri
python test_navigation.py
```

### 2. Entegrasyon Testleri
```bash
# Tüm sistemin bir arada çalışması
python test_integration.py
# Web arayüzü ile robot haberleşmesi
python test_web_integration.py
```

### 3. Sistem Testleri
```bash
# Gerçek ortamda tam test
python test_full_system.py
```

## 🛠️ Manuel Test Prosedürleri

### Başlangıç Kontrol Listesi
- [ ] Güç sistemini kontrol et (12V, 5V, 3.3V)
- [ ] Sensörlerin bağlantılarını kontrol et
- [ ] Motor sürücülerin çalıştığını doğrula
- [ ] WiFi bağlantısını test et
- [ ] Web arayüzüne erişimi kontrol et

### Hareket Testleri

#### Test 1: Temel Hareket
1. **İleri Hareket (5 saniye)**
   ```python
   robot.move_forward(speed=50, duration=5)
   ```
   - ✅ Düz gidiyor mu?
   - ✅ Hız sabit mi?
   - ✅ Beklenmedik titreşim var mı?

2. **Geri Hareket (3 saniye)**
   ```python
   robot.move_backward(speed=40, duration=3)
   ```

3. **Dönüş Testleri**
   ```python
   robot.turn_left(90)  # 90 derece sol
   robot.turn_right(90) # 90 derece sağ
   ```

#### Test 2: Navigasyon
```python
# Hedefe git testi
target_x, target_y = 100, 200
robot.goto_position(target_x, target_y)
```

**Kontrol Edilecekler:**
- Hedefe ulaştı mı?
- Engelleri dolaştı mı?
- Yol planlaması makul mü?

### Sensör Testleri

#### Ultrasonik Sensör
```python
import time

for i in range(10):
    distance = robot.get_ultrasonic_distance()
    print(f"Mesafe {i+1}: {distance} cm")
    time.sleep(1)
```

**Beklenen Sonuçlar:**
- Sabit bir duvarın karşısında ± 2cm hassasiyet
- Maksimum menzil: 200cm
- Minimum menzil: 2cm

#### Kamera Testi
```python
# Görüntü alma testi
image = robot.capture_image()
robot.save_image(image, "test_image.jpg")

# Nesne tanıma testi
objects = robot.detect_objects(image)
print(f"Tespit edilen nesneler: {objects}")
```

#### IMU Sensörü
```python
# Açı ölçümü testi
for i in range(5):
    angle = robot.get_heading()
    print(f"Mevcut açı: {angle} derece")
    robot.turn_left(90)
    time.sleep(2)
```

## 🌐 Web Arayüzü Testleri

### Manuel UI Testleri
1. **Ana Sayfa Kontrolü**
   - [ ] Sayfa açılıyor mu?
   - [ ] Robot durumu görünüyor mu?
   - [ ] Canlı video akışı çalışıyor mu?

2. **Kontrol Testleri**
   - [ ] Yön tuşları çalışıyor mu?
   - [ ] Hız ayarı değişiyor mu?
   - [ ] Acil dur butonu çalışıyor mu?

3. **Harita Testleri**
   - [ ] Robotun konumu gösteriliyor mu?
   - [ ] Hedef belirleme çalışıyor mu?
   - [ ] Engeller haritada görünüyor mu?

### Otomatik Web Testleri
```python
# Selenium ile otomatik test
from selenium import webdriver

driver = webdriver.Chrome()
driver.get("http://robot-ip:8080")

# Kontrol butonu testi
forward_btn = driver.find_element_by_id("forward-btn")
forward_btn.click()
time.sleep(2)

# Robot hareket etmeli
assert robot.is_moving() == True
```

## 🎯 Performans Testleri

### Hız Testi
```python
import time

start_pos = robot.get_position()
start_time = time.time()

robot.move_forward(speed=100, duration=10)

end_pos = robot.get_position()
end_time = time.time()

distance = calculate_distance(start_pos, end_pos)
actual_speed = distance / (end_time - start_time)

print(f"Hesaplanan hız: {actual_speed} cm/s")
```

### Pil Dayanıklılık Testi
```python
start_voltage = robot.get_battery_voltage()
start_time = time.time()

# 1 saat boyunca normal operasyon
robot.start_autonomous_mode()
time.sleep(3600)  # 1 saat

end_voltage = robot.get_battery_voltage()
end_time = time.time()

voltage_drop = start_voltage - end_voltage
hours = (end_time - start_time) / 3600

print(f"Saatte voltaj düşüşü: {voltage_drop/hours} V/saat")
```

## 🔍 Stres Testleri

### Sürekli Çalışma Testi
```python
# 8 saat boyunca çalışma testi
import time

start_time = time.time()
error_count = 0

while (time.time() - start_time) < 28800:  # 8 saat
    try:
        robot.patrol_room()
        time.sleep(60)  # 1 dakika ara
    except Exception as e:
        error_count += 1
        print(f"Hata #{error_count}: {e}")
        
print(f"Toplam hata sayısı: {error_count}")
```

### Aşırı Yük Testi
```python
# Maksimum ağırlık ile test
robot.add_test_weight(2000)  # 2kg ekstra ağırlık
robot.move_forward(speed=50, duration=10)

# Motor akımlarını kontrol et
motor_currents = robot.get_motor_currents()
for motor, current in motor_currents.items():
    if current > MAX_SAFE_CURRENT:
        print(f"UYARI: {motor} motoru aşırı akım çekiyor!")
```

## 📊 Test Sonuçları Değerlendirmesi

### Geçme Kriterleri

**Hareket Testleri:**
- Düz çizgi sapması: ±5cm (10m mesafe için)
- Dönüş hassasiyeti: ±5 derece
- Maksimum hız: En az 50 cm/s

**Sensör Testleri:**
- Ultrasonik hassasiyet: ±2cm
- Kamera frame rate: En az 15 FPS
- IMU hassasiyeti: ±2 derece

**Performans Testleri:**
- Pil ömrü: En az 4 saat
- WiFi menzili: En az 20m
- Tepki süresi: Maksimum 200ms

### Test Raporu Şablonu
```markdown
# Test Raporu - [Tarih]

## Test Edilen Versiyon
- Yazılım: v1.2.3
- Donanım: Rev 2.1

## Test Sonuçları
- Geçen testler: 45/50
- Başarı oranı: %90
- Kritik hatalar: 2
- Uyarılar: 8

## Önemli Bulgular
1. Motor titreşimi yüksek hızlarda artıyor
2. WiFi bağlantısı bazen kopuyor
3. Kamera düşük ışıkta zorlanıyor

## Öneriler
- Motor montajını yeniden kontrol et
- WiFi anteni pozisyonunu iyileştir
- Kamera için LED ışık ekle
```

## 🚨 Güvenlik Testleri

### Acil Dur Testi
```python
# Robot hareket halindeyken acil dur
robot.start_movement()
time.sleep(2)
robot.emergency_stop()

# 1 saniye içinde durmalı
stop_time = measure_stop_time()
assert stop_time < 1.0, "Acil dur çok yavaş!"
```

### Engel Algılama Testi
```python
# Engel karşısında durma testi
robot.move_forward(speed=30)
# Manuel olarak engel koy
time.sleep(5)

# Robot durmalı
assert robot.is_stopped(), "Robot engeli algılamadı!"
```

## 💡 İpuçları

1. **Test Ortamını Hazırla**: Düz zemin, iyi aydınlatma, engelsiz alan
2. **Sistemli Test Et**: Her bileşeni ayrı ayrı, sonra hep birlikte
3. **Sonuçları Kaydet**: Her test sonrasında detaylı notlar al
4. **Hataları Analiz Et**: Sadece "çalışıyor/çalışmıyor" değil, neden?
5. **Düzenli Test Et**: Her kod değişikliği sonrası mutlaka test

## 🎪 Son Söz

Test yapmak sabır işi ama robotun güvenilir çalışması için şart! Unutma, iyi test edilmiş bir robot = mutlu Hacı Abi = başarılı proje! 

Eğer test sırasında tuhaf sesler duyarsan, hemen dur ve kontrol et. Robot "beep beep" demiyorsa, bir sorun vardır! 😊

---
**Not**: Bu prosedürleri takip ederken kahve molası almayı unutma! Test yapmak uzun iş, kafein dostu! ☕
