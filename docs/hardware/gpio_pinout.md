# 🔌 GPIO Pin Haritası ve Bağlantılar

## Raspberry Pi 4B GPIO Kullanımı

### 📍 Pin Atama Tablosu

| GPIO Pin | Fizik Pin | Fonksiyon | Bağlantı | Notlar |
|----------|-----------|----------|----------|---------|
| GPIO 2 | 3 | I2C SDA | BNO055 IMU | Pull-up dahili |
| GPIO 3 | 5 | I2C SCL | BNO055 IMU | Pull-up dahili |
| GPIO 4 | 7 | Genel IO | DHT22 Sıcaklık/Nem | 1-Wire protokol |
| GPIO 6 | 31 | PWM | Biçme Motor PWM | Hardware PWM |
| GPIO 7 | 26 | Genel IO | Biçme Motor Dir | Yön kontrolü |
| GPIO 8 | 24 | SPI CE0 | LiDAR SPI | SPI interface |
| GPIO 9 | 21 | SPI MISO | LiDAR SPI | SPI interface |
| GPIO 10 | 19 | SPI MOSI | LiDAR SPI | SPI interface |
| GPIO 11 | 23 | SPI CLK | LiDAR SPI | SPI interface |
| GPIO 12 | 32 | PWM | Sol Palet PWM | Hardware PWM |
| GPIO 13 | 33 | PWM | Sol Palet DIR | Hardware PWM |
| GPIO 14 | 8 | UART TX | Debug UART | Serial debug |
| GPIO 15 | 10 | UART RX | Debug UART | Serial debug |
| GPIO 16 | 36 | PWM | Sağ Palet PWM | Hardware PWM |
| GPIO 17 | 11 | Genel IO | Kamera Enable | Kamera kontrol |
| GPIO 18 | 12 | PWM | Sol Enkoder A | Interrupt capable |
| GPIO 19 | 35 | PWM | Sol Enkoder B | Interrupt capable |
| GPIO 20 | 38 | Genel IO | Sağ Enkoder A | Interrupt capable |
| GPIO 21 | 40 | Genel IO | Sağ Enkoder B | Interrupt capable |
| GPIO 22 | 15 | Genel IO | IR LED Enable | IR aydınlatma |
| GPIO 23 | 16 | Genel IO | IR Sensör Sol | Dijital giriş |
| GPIO 24 | 18 | Genel IO | IR Sensör Sağ | Dijital giriş |
| GPIO 25 | 22 | Genel IO | Lineer Aktüatör | PWM/Dijital |
| GPIO 26 | 37 | PWM | Sağ Palet DIR | Hardware PWM |
| GPIO 27 | 13 | Genel IO | Emergency Stop | Acil durdurma |

### 🔋 Güç Pinleri

| Pin | Voltaj | Akım Kapasitesi | Kullanım |
|-----|--------|----------------|----------|
| Pin 2, 4 | 5V | 3A toplam | Sensörler, Pi beslemesi |
| Pin 1, 17 | 3.3V | 50mA | Düşük güç sensörleri |
| Pin 6, 9, 14, 20, 25, 30, 34, 39 | GND | - | Ortak toprak |

### 🆕 YENİ SENSÖR BAĞLANTILARI

#### LiDAR Sensör (RPLiDAR A1M8)
```
LiDAR ─────┬─── VCC ──── 5V (Pin 2)
           ├─── GND ──── GND (Pin 6)
           ├─── MOSI ─── GPIO 10 (Pin 19) - SPI MOSI
           ├─── MISO ─── GPIO 9 (Pin 21)  - SPI MISO
           ├─── CLK ──── GPIO 11 (Pin 23) - SPI CLK
           └─── CS ───── GPIO 8 (Pin 24)  - SPI CE0
```

#### Pi Kamera v2.1
```
Pi Kamera ─┬─── CSI Connector (Ribbon cable)
           ├─── Enable ── GPIO 17 (Pin 11)
           └─── LED ───── Dahili (kamera üzerinde)
```

#### Acil Durdurma Butonu
```
E-Stop ────┬─── NO ────── GPIO 27 (Pin 13)
           ├─── COM ───── GND (Pin 9)
           └─── NC ────── Kullanılmıyor
```

## 🏗️ Bağlantı Şemaları

### Motor Kontrolcü Bağlantıları

```
Raspberry Pi 4B ──┐
                  │
    ┌─────────────┼─── GPIO 12 (PWM) ──► Sol Motor Sürücü PWM
    │             │
    │             ┼─── GPIO 13 (DIR) ──► Sol Motor Sürücü DIR
    │             │
    │             ┼─── GPIO 16 (PWM) ──► Sağ Motor Sürücü PWM
    │             │
    │             ┼─── GPIO 26 (DIR) ──► Sağ Motor Sürücü DIR
    │             │
    │             ┼─── GPIO 6 (PWM) ───► Biçme Motor PWM
    │             │
    │             ┼─── GPIO 7 (DIR) ───► Biçme Motor DIR
    │             │
    └─────────────┼─── GPIO 25 (PWM) ──► Lineer Aktüatör PWM
```

### Sensör Bağlantıları

```
BNO055 IMU ────┬─── VIN ──── 3.3V (Pin 1)
               ├─── GND ──── GND (Pin 6)
               ├─── SDA ──── GPIO 2 (Pin 3)
               └─── SCL ──── GPIO 3 (Pin 5)

Sol Enkoder ───┬─── VCC ──── 5V (Pin 2)
               ├─── GND ──── GND (Pin 9)
               ├─── A ────── GPIO 18 (Pin 12)
               └─── B ────── GPIO 19 (Pin 35)

Sağ Enkoder ───┬─── VCC ──── 5V (Pin 4)
               ├─── GND ──── GND (Pin 14)
               ├─── A ────── GPIO 20 (Pin 38)
               └─── B ────── GPIO 21 (Pin 40)

DHT22 Sensör ──┬─── VCC ──── 3.3V (Pin 1)
               ├─── GND ──── GND (Pin 6)
               ├─── DATA ─── GPIO 4 (Pin 7)
               └─── NC ────── Kullanılmıyor

IR Sol ────────┬─── VCC ──── 3.3V (Pin 17)
               ├─── GND ──── GND (Pin 20)
               └─── OUT ──── GPIO 23 (Pin 16)

IR Sağ ────────┬─── VCC ──── 3.3V (Pin 17)
               ├─── GND ──── GND (Pin 25)
               └─── OUT ──── GPIO 24 (Pin 18)

Emergency Stop ┬─── NO ───── GPIO 27 (Pin 13)
               └─── COM ──── GND (Pin 9)
```

## ⚙️ Pin Konfigürasyonu

### Python GPIO Kurulumu

```python
import RPi.GPIO as GPIO
import pigpio
from time import sleep

# GPIO modunu ayarla
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Motor PWM pinleri
MOTOR_LEFT_PWM = 12
MOTOR_LEFT_DIR = 13
MOTOR_RIGHT_PWM = 16
MOTOR_RIGHT_DIR = 26
MOWER_PWM = 6
MOWER_DIR = 7

# Sensör pinleri
IR_SENSOR_LEFT = 23
IR_SENSOR_RIGHT = 24
EMERGENCY_STOP = 27

# Enkoder pinleri
ENCODER_LEFT_A = 18
ENCODER_LEFT_B = 19
ENCODER_RIGHT_A = 20
ENCODER_RIGHT_B = 21

# SPI LiDAR pinleri
LIDAR_SPI_CE = 8
LIDAR_SPI_MOSI = 10
LIDAR_SPI_MISO = 9
LIDAR_SPI_CLK = 11

# I2C IMU pinleri
IMU_SDA = 2  # I2C SDA
IMU_SCL = 3  # I2C SCL

# Pin kurulumları
def setup_gpio():
    # Motor pinleri - Çıkış
    GPIO.setup(MOTOR_LEFT_PWM, GPIO.OUT)
    GPIO.setup(MOTOR_LEFT_DIR, GPIO.OUT)
    GPIO.setup(MOTOR_RIGHT_PWM, GPIO.OUT)
    GPIO.setup(MOTOR_RIGHT_DIR, GPIO.OUT)
    GPIO.setup(MOWER_PWM, GPIO.OUT)
    GPIO.setup(MOWER_DIR, GPIO.OUT)

    # Enkoder pinleri - Giriş (pull-up ile)
    GPIO.setup(ENCODER_LEFT_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(ENCODER_LEFT_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(ENCODER_RIGHT_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(ENCODER_RIGHT_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Sensör pinleri - Giriş
    GPIO.setup(IR_SENSOR_LEFT, GPIO.IN)
    GPIO.setup(IR_SENSOR_RIGHT, GPIO.IN)

    # Lineer aktüatör - Çıkış
    GPIO.setup(LINEAR_ACTUATOR, GPIO.OUT)

    # PWM objelerini oluştur
    left_pwm = GPIO.PWM(MOTOR_LEFT_PWM, 20000)  # 20kHz
    right_pwm = GPIO.PWM(MOTOR_RIGHT_PWM, 20000)
    mower_pwm = GPIO.PWM(MOWER_PWM, 20000)

    return left_pwm, right_pwm, mower_pwm
```

### PWM Kurulumu
```python
# Motor PWM'leri ayarla (1kHz frekans)
pwm_freq = 1000
left_motor_pwm = GPIO.PWM(MOTOR_LEFT_PWM, pwm_freq)
right_motor_pwm = GPIO.PWM(MOTOR_RIGHT_PWM, pwm_freq)
mower_pwm = GPIO.PWM(MOWER_PWM, pwm_freq)

# PWM'leri başlat (%0 ile)
left_motor_pwm.start(0)
right_motor_pwm.start(0)
mower_pwm.start(0)
```

## 🔧 Elektriksel Özellikler

### PWM Konfigürasyonu

| Pin | Frekans | Çözünürlük | Kullanım Amacı |
|-----|---------|------------|----------------|
| GPIO 12 | 20kHz | 8-bit | Sol palet hız kontrolü |
| GPIO 16 | 20kHz | 8-bit | Sağ palet hız kontrolü |
| GPIO 26 | 20kHz | 8-bit | Sağ palet hız kontrolü |
| GPIO 6 | 20kHz | 8-bit | Biçme motor hız kontrolü |

### Enkoder Sinyalleri

```
Enkoder A/B Fazı:
     ┌───┐   ┌───┐   ┌───
A ───┘   └───┘   └───┘
   ┌───┐   ┌───┐   ┌───┐
B ─┘   └───┘   └───┘   └─

- A fazında yükselen kenar = ileri yön
- A fazında düşen kenar = geri yön
- Çözünürlük: 600 pulse/tur (quadrature)
- Maksimum frekans: 50kHz
```

### I2C Konfigürasyonu

```bash
# I2C'yi etkinleştir
sudo raspi-config nonint do_i2c 0

# I2C hızını ayarla (400kHz)
echo 'dtparam=i2c_arm=on,i2c_arm_baudrate=400000' >> /boot/config.txt

# I2C cihazları tara
i2cdetect -y 1

# BNO055 adresi: 0x28 veya 0x29
```

## 🛡️ Güvenlik Korumaları

### Overcurrent Koruması

```python
import psutil
import time

class GPIOProtection:
    def __init__(self):
        self.max_current = 3.0  # Ampere
        self.monitor_interval = 0.1  # saniye

    def monitor_current(self):
        while True:
            # CPU sıcaklığını kontrol et
            temp = self.get_cpu_temp()
            if temp > 70:  # 70°C üzeri
                self.emergency_stop()

            time.sleep(self.monitor_interval)

    def get_cpu_temp(self):
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = int(f.read().strip()) / 1000.0
        return temp

    def emergency_stop(self):
        # Tüm PWM çıkışlarını durdur
        GPIO.output(MOTOR_LEFT_PWM, GPIO.LOW)
        GPIO.output(MOTOR_RIGHT_PWM, GPIO.LOW)
        GPIO.output(MOWER_PWM, GPIO.LOW)
        print("ACIL DURUM: Sistem durduruldu!")
```

### Pull-up/Pull-down Konfigürasyonu

| Pin Tipi | Konfigürasyon | Sebep |
|----------|--------------|-------|
| Enkoder | PULL_UP | Gürültü filtreleme |
| IR Sensör | Harici | Sensör dahili pull-up |
| Motor Dir | Varsayılan | Açık devre koruması |

## 🔍 Test ve Doğrulama

### GPIO Test Scripti

```python
#!/usr/bin/env python3
"""GPIO pin test scripti - Hacı Abi"""

import RPi.GPIO as GPIO
import time

def test_all_pins():
    """Bütün pinleri tek tek test et"""
    print("🔧 Hacı Abi'nin GPIO Testi Başlıyor!")

    setup_gpio()

    print("📍 Motor pinlerini test ediyoruz...")
    test_motor_pins()

    print("📍 Enkoder pinlerini test ediyoruz...")
    test_encoder_pins()

    print("📍 Sensör pinlerini test ediyoruz...")
    test_sensor_pins()

    print("✅ Tüm testler tamamlandı!")
    GPIO.cleanup()

def test_motor_pins():
    """Motor pinlerini test et"""
    pins = [12, 13, 16, 26, 6, 7]
    for pin in pins:
        print(f"  🔸 GPIO {pin} test ediliyor...")
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.1)
        print(f"  ✅ GPIO {pin} OK")

def test_encoder_pins():
    """Enkoder pinlerini test et"""
    encoder_pins = [18, 19, 20, 21]
    for pin in encoder_pins:
        state = GPIO.input(pin)
        print(f"  🔸 Enkoder GPIO {pin}: {state}")

def test_sensor_pins():
    """Sensör pinlerini test et"""
    sensor_pins = [23, 24]
    for pin in sensor_pins:
        state = GPIO.input(pin)
        print(f"  🔸 IR Sensör GPIO {pin}: {state}")

if __name__ == "__main__":
    test_all_pins()
```

## 📋 Bakım Kontrol Listesi

### Günlük Kontroller
- [ ] GPIO bağlantılarında gevşeklik var mı?
- [ ] Kablo uçlarında korozyon var mı?
- [ ] Pi sıcaklığı normal mi? (<60°C)

### Haftalık Kontroller
- [ ] I2C bus fonksiyonel mi?
- [ ] Enkoder sinyalleri temiz mi?
- [ ] PWM çıkışları doğru frekansda mı?

### Aylık Kontroller
- [ ] GPIO test scripti çalıştırıldı mı?
- [ ] Kablo yalıtımları kontrol edildi mi?
- [ ] Güç tüketimi normal mi?

## 🆘 Sorun Giderme

### Yaygın Sorunlar

#### 1. "GPIO already in use" Hatası
```bash
# GPIO'ları temizle
python3 -c "import RPi.GPIO as GPIO; GPIO.cleanup()"

# Process'leri kontrol et
sudo lsof | grep gpio
```

#### 2. I2C Cihaz Bulunamıyor
```bash
# I2C status kontrolü
sudo systemctl status i2c

# Cihaz taraması
i2cdetect -y 1

# I2C config kontrolü
cat /boot/config.txt | grep i2c
```

#### 3. PWM Çalışmıyor
```bash
# PWM overlay'i kontrol et
ls /sys/class/pwm/

# Device tree overlays
cat /boot/config.txt | grep pwm
```

#### 4. Enkoder Okuma Problemi
```python
# Interrupt test
def encoder_callback(channel):
    print(f"Enkoder interrupt: GPIO {channel}")

GPIO.add_event_detect(18, GPIO.BOTH, callback=encoder_callback)
```

---

**🎯 Hacı Abi Notu:** Bu GPIO haritası, robotumuzun sinir sistemi gibi. Her pin'in kendine has görevi var, yanlış bağlantı yaparsan robot kafasını kaşır! Test scriptlerini düzenli çalıştır, bağlantıları kontrol et. Sorun çıkarsa panik yapma, metodlu çöz! 🤖⚡
