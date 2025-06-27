# ⚙️ Motor Teknik Özellikleri

## BLDC Motor Spesifikasyonları

### 🚜 Palet Motorları (2 adet)

#### Genel Özellikler
- **Model**: BLDC-2430-24V-3000RPM
- **Tip**: Brushless DC Motor
- **Güç**: 250W
- **Voltaj**: 24V DC
- **Akım**: 10.4A (maksimum)
- **Hız**: 3000 RPM (yüksüz)
- **Tork**: 0.8 Nm (sürekli)
- **Verimlilik**: >85%

#### Fiziksel Özellikler
- **Çap**: 60mm
- **Boy**: 120mm
- **Ağırlık**: 1.2kg
- **Montaj**: Flanş montajı (4x M5 vida)
- **Mil Çapı**: 8mm
- **Şaft Uzunluğu**: 25mm

#### Elektriksel Özellikler
```
Sargı Direnci: 2.3Ω ±5%
İndüktans: 8.5mH ±10%
Kutup Sayısı: 8
Slot Sayısı: 12
KV Değeri: 125 rpm/V
```

#### Performans Karakteristikleri

| RPM | Tork (Nm) | Güç (W) | Akım (A) | Verimlilik (%) |
|-----|-----------|---------|----------|----------------|
| 0 | 2.4 | 0 | 15.0 | 0 |
| 500 | 2.2 | 115 | 8.5 | 82 |
| 1000 | 2.0 | 209 | 7.8 | 85 |
| 1500 | 1.8 | 283 | 7.2 | 87 |
| 2000 | 1.6 | 335 | 6.8 | 89 |
| 2500 | 1.4 | 367 | 6.5 | 88 |
| 3000 | 1.2 | 377 | 6.4 | 85 |

### 🌱 Biçme Motoru

#### Genel Özellikler
- **Model**: BLDC-2838-24V-2400RPM
- **Tip**: Brushless DC Motor
- **Güç**: 400W
- **Voltaj**: 24V DC
- **Akım**: 16.7A (maksimum)
- **Hız**: 2400 RPM (yüksüz)
- **Tork**: 1.6 Nm (sürekli)
- **Verimlilik**: >88%

#### Fiziksel Özellikler
- **Çap**: 68mm
- **Boy**: 95mm
- **Ağırlık**: 1.8kg
- **Montaj**: Flanş montajı (6x M6 vida)
- **Mil Çapı**: 12mm
- **Şaft Uzunluğu**: 30mm

#### Elektriksel Özellikler
```
Sargı Direnci: 1.44Ω ±5%
İndüktans: 6.2mH ±10%
Kutup Sayısı: 10
Slot Sayısı: 12
KV Değeri: 100 rpm/V
```

## 🔧 Motor Sürücü Modülleri

### Palet Motor Sürücüleri (2 adet)

#### Teknik Özellikler
- **Model**: BLDC-Driver-24V-15A
- **Giriş Voltajı**: 12-36V DC
- **Çıkış Akımı**: 15A sürekli, 30A pik
- **PWM Frekansı**: 8-25kHz (ayarlanabilir)
- **Kontrol Sinyali**: 3.3V/5V TTL uyumlu
- **Koruma**: Overcurrent, Overvoltage, Thermal

#### Pin Konfigürasyonu
```
Güç Bağlantıları:
VCC+  : 24V pozitif (kırmızı)
VCC-  : 24V negatif (siyah)
M+    : Motor fazı A (sarı)
M-    : Motor fazı B (mavi)
M0    : Motor fazı C (yeşil)

Kontrol Bağlantıları:
PWM   : PWM hız sinyali (0-5V)
DIR   : Yön kontrolü (0/3.3V)
EN    : Enable sinyali (0/3.3V)
FB    : Hız feedback (analog)
GND   : Kontrol toprağı
```

#### PWM Kontrol Parametreleri
- **PWM Frekansı**: 20kHz (optimal)
- **Duty Cycle Aralığı**: 0-100%
- **Başlangıç Duty**: 5% (soft start)
- **Maksimum Duty**: 95% (güvenlik)
- **Hızlanma Rampa**: 2%/10ms
- **Yavaşlama Rampa**: 5%/10ms

### Biçme Motor Sürücüsü

#### Teknik Özellikler
- **Model**: BLDC-Driver-24V-25A
- **Giriş Voltajı**: 12-36V DC
- **Çıkış Akımı**: 25A sürekli, 50A pik
- **PWM Frekansı**: 8-25kHz (ayarlanabilir)
- **Kontrol Sinyali**: 3.3V/5V TTL uyumlu
- **Koruma**: Overcurrent, Overvoltage, Thermal, Stall Detection

#### Özel Özellikler
- **Otomatik Tork Artırma**: Yük artışında otomatik güç artırır
- **Stall Detection**: Bıçak sıkışması algılama
- **Thermal Protection**: 85°C'de güç düşürme
- **Emergency Stop**: Acil durdurma girişi

## ⚡ Güç Tüketimi Analizi

### Tipik Çalışma Senaryoları

#### Normal Biçme (Düz Arazi)
```
Sol Palet Motor:  150W @ 1500 RPM
Sağ Palet Motor:  150W @ 1500 RPM  
Biçme Motoru:     250W @ 2000 RPM
Toplam Güç:       550W
Batarya Akımı:    23A @ 24V
```

#### Ağır Biçme (Yoğun Ot)
```
Sol Palet Motor:  200W @ 1200 RPM
Sağ Palet Motor:  200W @ 1200 RPM
Biçme Motoru:     350W @ 1800 RPM
Toplam Güç:       750W
Batarya Akımı:    31A @ 24V
```

#### Eğimli Arazi (%10 eğim)
```
Sol Palet Motor:  180W @ 1300 RPM
Sağ Palet Motor:  180W @ 1300 RPM
Biçme Motoru:     280W @ 1900 RPM
Toplam Güç:       640W
Batarya Akımı:    27A @ 24V
```

#### Dönüş Manevrası
```
Sol Palet Motor:  100W @ 800 RPM (yavaş)
Sağ Palet Motor:  220W @ 1800 RPM (hızlı)
Biçme Motoru:     200W @ 1600 RPM (düşük)
Toplam Güç:       520W
Batarya Akımı:    22A @ 24V
```

### Verimlilik Optimizasyonu

#### Optimal Çalışma Noktaları
- **Palet Motorları**: 1500 RPM (%87 verimlilik)
- **Biçme Motoru**: 2000 RPM (%89 verimlilik)
- **Kombine Verimlilik**: %85-88

#### Enerji Tasarrufu Stratejileri
1. **Adaptif Hız Kontrolü**: Ot yoğunluğuna göre hız ayarı
2. **Smart Mowing**: Temiz alanlarda biçme motoru kapatma
3. **Regenerative Braking**: Eğimde inerken enerji geri kazanımı
4. **Sleep Mode**: Bekleme anında güç düşürme

## 🧮 Motor Kontrol Algoritmaları

### PID Hız Kontrolü

```python
class MotorController:
    def __init__(self):
        # PID parametreleri
        self.kp = 0.5    # Proportional gain
        self.ki = 0.1    # Integral gain  
        self.kd = 0.05   # Derivative gain
        
        # Değişkenler
        self.setpoint = 0
        self.integral = 0
        self.last_error = 0
        
    def update(self, current_rpm, target_rpm, dt):
        """PID kontrolü ile PWM değeri hesapla"""
        error = target_rpm - current_rpm
        
        # Proportional term
        p_term = self.kp * error
        
        # Integral term  
        self.integral += error * dt
        i_term = self.ki * self.integral
        
        # Derivative term
        d_term = self.kd * (error - self.last_error) / dt
        self.last_error = error
        
        # PWM değeri (0-100)
        pwm = p_term + i_term + d_term
        pwm = max(0, min(100, pwm))  # Sınırla
        
        return pwm
```

### Rampa Kontrolü

```python
class RampController:
    def __init__(self, max_acceleration=50):  # RPM/saniye
        self.max_accel = max_acceleration
        self.current_speed = 0
        
    def update(self, target_speed, dt):
        """Yumuşak hız geçişi"""
        speed_diff = target_speed - self.current_speed
        max_change = self.max_accel * dt
        
        if abs(speed_diff) <= max_change:
            self.current_speed = target_speed
        else:
            if speed_diff > 0:
                self.current_speed += max_change
            else:
                self.current_speed -= max_change
                
        return self.current_speed
```

### Diferansiyel Sürüş

```python
class DifferentialDrive:
    def __init__(self, wheel_base=0.6):  # metre
        self.wheel_base = wheel_base
        
    def calculate_wheel_speeds(self, linear_vel, angular_vel):
        """
        Doğrusal ve açısal hızdan tekerlek hızlarını hesapla
        linear_vel: m/s
        angular_vel: rad/s
        """
        # Tekerlek hızları (m/s)
        left_vel = linear_vel - (angular_vel * self.wheel_base / 2)
        right_vel = linear_vel + (angular_vel * self.wheel_base / 2)
        
        # RPM'e çevir (tekerlek çapı: 0.2m)
        wheel_circumference = 0.2 * 3.14159
        left_rpm = (left_vel / wheel_circumference) * 60
        right_rpm = (right_vel / wheel_circumference) * 60
        
        return left_rpm, right_rpm
```

## 🔧 Kalibrasyon Prosedürleri

### Enkoder Kalibrasyonu

```python
def calibrate_encoders():
    """Enkoder hassasiyetini kalibre et"""
    print("🔧 Enkoder kalibrasyonu başlıyor...")
    
    # 10 tur motor çevir
    for i in range(10):
        print(f"Tur {i+1}/10")
        
        # Motoru 1 tur çevir (360 derece)
        target_pulses = 600  # 600 pulse/tur
        start_pulse = read_encoder()
        
        # Motor çalıştır
        run_motor_one_revolution()
        
        # Pulse sayısını oku
        actual_pulses = read_encoder() - start_pulse
        
        # Hata hesapla
        error_percent = ((actual_pulses - target_pulses) / target_pulses) * 100
        print(f"  Hedef: {target_pulses}, Gerçek: {actual_pulses}, Hata: {error_percent:.1f}%")
        
    print("✅ Enkoder kalibrasyonu tamamlandı!")
```

### Motor Performans Testi

```python
def motor_performance_test():
    """Motor performansını test et"""
    print("🧪 Motor performans testi...")
    
    test_speeds = [500, 1000, 1500, 2000, 2500, 3000]
    
    for speed in test_speeds:
        print(f"Test hızı: {speed} RPM")
        
        # Hızı ayarla
        set_motor_speed(speed)
        time.sleep(2)  # Stabilleşme süresi
        
        # Ölçümler al
        actual_speed = measure_actual_speed()
        current = measure_motor_current()
        voltage = measure_motor_voltage()
        power = current * voltage
        
        # Sonuçları kaydet
        efficiency = (actual_speed / speed) * 100
        
        print(f"  Gerçek hız: {actual_speed} RPM")
        print(f"  Akım: {current:.1f}A")
        print(f"  Güç: {power:.1f}W") 
        print(f"  Verimlilik: {efficiency:.1f}%")
        print("-" * 30)
        
    print("✅ Performans testi tamamlandı!")
```

## 📊 Bakım ve Arıza Tanılama

### Periyodik Bakım

#### Günlük Kontroller
- [ ] Motor sıcaklığı kontrol (<60°C)
- [ ] Titreşim/gürültü kontrol
- [ ] Kablo bağlantıları kontrol
- [ ] Enkoder sinyali kontrol

#### Haftalık Kontroller  
- [ ] Motor performans testi
- [ ] Sürücü kartları kontrol
- [ ] PWM sinyal kalitesi ölçümü
- [ ] Güç tüketimi analizi

#### Aylık Kontroller
- [ ] Rulman greslemesi
- [ ] Motor temizliği
- [ ] Elektriksel bağlantı kontrolü
- [ ] Kalibrasyon kontrolü

### Arıza Tanılama

#### Problem: Motor Çalışmıyor

**Kontrol Adımları:**
1. **Güç Kontrolü**: 24V var mı?
2. **PWM Sinyali**: Sürücüye PWM geliyor mu?
3. **Enable Sinyali**: Enable aktif mi?
4. **Sürücü LED'leri**: Hata kodu var mı?

```python
def diagnose_motor_not_running():
    """Motor çalışmama tanısı"""
    print("🔍 Motor tanılama başlıyor...")
    
    # Güç kontrolü
    voltage = measure_supply_voltage()
    if voltage < 22:
        return "⚠️ Düşük voltaj! Bataryayı kontrol et."
    
    # PWM sinyali kontrolü
    pwm_active = check_pwm_signal()
    if not pwm_active:
        return "⚠️ PWM sinyali yok! Raspberry Pi kontrol et."
    
    # Enable kontrolü
    enable_active = check_enable_signal()
    if not enable_active:
        return "⚠️ Enable sinyali pasif! Yazılım kontrol et."
    
    # Motor direnci kontrolü
    resistance = measure_motor_resistance()
    if resistance > 5.0:  # Normal: 2.3Ω
        return "⚠️ Motor sargı hasarlı! Motor değiştir."
    
    return "✅ Elektriksel ölçümler normal, mekanik kontrol et."
```

#### Problem: Hız Kontrolü Çalışmıyor

**Kontrol Adımları:**
1. **Enkoder Sinyali**: Feedback geliyor mu?
2. **PID Parametreleri**: Uygun mu?
3. **PWM Frekansı**: 20kHz'de mi?
4. **Load Testi**: Aşırı yük var mı?

```python
def diagnose_speed_control():
    """Hız kontrolü tanısı"""
    print("🔍 Hız kontrolü tanılama...")
    
    # Enkoder test
    encoder_count = test_encoder_reading()
    if encoder_count == 0:
        return "⚠️ Enkoder sinyali yok! Bağlantı kontrol et."
    
    # PID parametre kontrolü
    if check_pid_oscillation():
        return "⚠️ PID salınımı var! Parametreleri ayarla."
    
    # Yük kontrolü
    current = measure_motor_current()
    if current > 15:  # Aşırı yük
        return "⚠️ Aşırı yük! Mekanik sistemi kontrol et."
    
    return "✅ Hız kontrolü normal çalışıyor."
```

---

**🎯 Hacı Abi Notu:** Motorlar robotun kasları gibi, düzgün bakım yapmazsan güçsüz kalır! PWM değerlerini ayarlarken sabırlı ol, rampa kontrolünü es geçme. Akım ölçümünü takip et, aşırı yük motoru yakar! Test scriptlerini düzenli çalıştır, performans grafiklerini tut. Sorun çıkarsa elektriksel ölçümlerden başla, sonra mekanik kontrol et! 🤖⚙️
