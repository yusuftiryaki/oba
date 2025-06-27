# Elektronik Şemalar ve Devre Diyagramları ⚡

Merhaba elektroni̇k meraklıları! Hacı Abi burada, OBA robotumuzun elektronik kalbi olan devreleri gösteriyorum. Bu sayfa robotumuzun "beyninin" nasıl bağlı olduğunu anlatan çizimler içeriyor! 🧠⚡

## 🔌 Ana Devre Şemaları

### 🖥️ Ana Kontrol Kartı (Main Board)

#### PCB Layout Overview
```
     [USB-C]    [Power LED]    [Status LED]
        │           │             │
    ┌───┴───────────┴─────────────┴───┐
    │  🔲 Raspberry Pi 4 Headers     │
    │                                │
    │  🔲 GPIO Expander              │
    │                                │
    │  🔲 Motor Driver L298N         │
    │                                │
    │  🔲 Sensor Interface           │
    │                                │
    │  🔲 Power Management           │
    └────────────────────────────────┘
     [Motor 1] [Motor 2] [Sensors] [Battery]
```

#### Pin Assignment Tablosu
| Pin | İşlev | Bağlantı | Voltaj |
|-----|-------|----------|--------|
| 1 | 3.3V Power | VCC | 3.3V |
| 2 | 5V Power | Motor VCC | 5V |
| 3 | GPIO 2 (SDA) | I2C Data | 3.3V |
| 4 | 5V Power | Sensors | 5V |
| 5 | GPIO 3 (SCL) | I2C Clock | 3.3V |
| 6 | Ground | Common GND | 0V |
| 7 | GPIO 4 | Motor 1 PWM | 3.3V |
| 8 | GPIO 14 (TXD) | Serial TX | 3.3V |
| 9 | Ground | Common GND | 0V |
| 10 | GPIO 15 (RXD) | Serial RX | 3.3V |

### ⚡ Güç Dağıtım Şeması

```
    [12V Battery Pack]
           │
    ┌──────┴──────┐
    │   FUSE 10A  │ ← Koruma sigortası
    └──────┬──────┘
           │
    ┌──────┴──────┐
    │ DC-DC 12V→5V│ ← Buck converter
    │    5A       │
    └──────┬──────┘
           │
    ┌──────┴──────┐
    │ LDO 5V→3.3V │ ← Lineer regülatör
    │    2A       │
    └──────┬──────┘
           │
    ┌──────┴──────┐
    │ Power Rails │
    │ 12V: Motors │
    │ 5V: Sensors │ 
    │ 3.3V: Logic │
    └─────────────┘
```

#### Güç Tüketimi Analizi
```
💡 Voltaj Seviyeleri:
12V Rail: Motors, High Power (Max 3A)
5V Rail:  Raspberry Pi, Sensors (Max 2A) 
3.3V Rail: Logic, WiFi, GPIO (Max 1A)

⚡ Toplam Güç:
Idle:     8W  (Battery: ~6 hours)
Normal:   18W (Battery: ~3 hours)
Max:      35W (Battery: ~1.5 hours)
```

### 🔄 Motor Sürücü Devresi

```
     [Left Motor]              [Right Motor]
          │                         │
    ┌─────┴─────┐             ┌─────┴─────┐
    │   M1+     │             │   M2+     │
    │   M1-     │             │   M2-     │
    └─────┬─────┘             └─────┬─────┘
          │                         │
    ┌─────┴─────────────────────────┴─────┐
    │         L298N Dual Motor Driver     │
    │                                     │
    │ IN1 ←─ GPIO 18    IN3 ←─ GPIO 24   │
    │ IN2 ←─ GPIO 19    IN4 ←─ GPIO 25   │
    │ ENA ←─ GPIO 16    ENB ←─ GPIO 26   │
    │                                     │
    │ VCC ←─ 12V        VSS ←─ 5V        │
    │ GND ←─ Common Ground                │
    └─────────────────────────────────────┘
```

#### Motor Kontrol Sinyalleri
```python
# Motor kontrolü için GPIO konfigürasyonu
MOTOR_1_PWM = 16    # Enable A
MOTOR_1_IN1 = 18    # Direction 1
MOTOR_1_IN2 = 19    # Direction 2

MOTOR_2_PWM = 26    # Enable B  
MOTOR_2_IN3 = 24    # Direction 1
MOTOR_2_IN4 = 25    # Direction 2

# Hareket fonksiyonları
def move_forward():
    GPIO.output(MOTOR_1_IN1, HIGH)
    GPIO.output(MOTOR_1_IN2, LOW)
    GPIO.output(MOTOR_2_IN3, HIGH) 
    GPIO.output(MOTOR_2_IN4, LOW)
    
def turn_left():
    GPIO.output(MOTOR_1_IN1, LOW)   # Sol motor geri
    GPIO.output(MOTOR_1_IN2, HIGH)
    GPIO.output(MOTOR_2_IN3, HIGH)  # Sağ motor ileri
    GPIO.output(MOTOR_2_IN4, LOW)
```

## 📡 Sensör Bağlantı Şemaları

### 🔊 Ultrasonik Sensör (HC-SR04)

```
    ┌─────────────────┐
    │   HC-SR04       │
    │                 │
    │ VCC ←─ 5V       │
    │ Trig←─ GPIO 23  │
    │ Echo←─ GPIO 24  │  
    │ GND ←─ Ground   │
    └─────────────────┘
          │     │
    ┌─────┴─────┴─────┐
    │ Voltage Divider │  ← Echo sinyali 5V→3.3V
    │   R1: 1kΩ       │
    │   R2: 2kΩ       │
    └─────────────────┘
```

#### Ölçüm Prensibi
```
1. Trig pininden 10μs sinyal gönder
2. Echo pininden dönen sinyali ölç
3. Süre = Echo pulse width
4. Mesafe = (Süre × 340m/s) / 2

Kod örneği:
def get_distance():
    GPIO.output(TRIG, HIGH)
    time.sleep(0.00001)  # 10μs
    GPIO.output(TRIG, LOW)
    
    while GPIO.input(ECHO) == LOW:
        start = time.time()
    
    while GPIO.input(ECHO) == HIGH:
        end = time.time()
    
    duration = end - start
    distance = (duration * 34300) / 2  # cm
    return distance
```

### 📷 Kamera Modülü (Pi Camera v2)

```
    ┌───────────────────┐
    │  Pi Camera v2     │
    │                   │
    │  [Lens Assembly]  │
    │                   │  
    │  15-pin Ribbon ──→│─┐
    └───────────────────┘ │
                          │
    ┌─────────────────────┘
    │
    │ Raspberry Pi 4
    │ CSI Camera Port
    │ ┌─────────────────┐
    └→│ 15-pin Connector│
      └─────────────────┘
```

#### Kamera Spesifikasyonları
```
📸 Teknik Özellikler:
- Sensor: Sony IMX219 
- Çözünürlük: 8MP (3280 × 2464)
- Video: 1080p30, 720p60, 640x480p90
- Lens: f/2.0, 160° görüş alanı
- Focus: Fixed focus
- Interface: MIPI CSI-2

🔧 Bağlantı:
- Data Rate: 4 lanes × 1 Gbps
- Power: 3.3V @ 250mA
- Control: I2C @ 400kHz
```

### 🧭 IMU Sensörü (MPU6050)

```
    ┌─────────────────┐
    │    MPU6050      │
    │  (6-axis IMU)   │
    │                 │
    │ VCC ←─ 3.3V     │
    │ GND ←─ Ground   │
    │ SCL ←─ GPIO 3   │ ← I2C Clock
    │ SDA ←─ GPIO 2   │ ← I2C Data
    │ INT ←─ GPIO 27  │ ← Interrupt
    │ AD0 ←─ Ground   │ ← Address select
    └─────────────────┘
```

#### I2C Adres Konfigürasyonu
```
Device Address: 0x68 (AD0 = LOW)
                0x69 (AD0 = HIGH)

Register Map:
0x3B-0x40: Accelerometer (X,Y,Z)
0x41-0x42: Temperature  
0x43-0x48: Gyroscope (X,Y,Z)
0x6B:      Power Management
0x75:      WHO_AM_I (0x68)

Örnek okuma kodu:
def read_imu():
    # Wake up MPU6050
    bus.write_byte_data(0x68, 0x6B, 0)
    
    # Read accelerometer
    acc_x = read_word_2c(0x3B)
    acc_y = read_word_2c(0x3D)
    acc_z = read_word_2c(0x3F)
    
    # Read gyroscope
    gyro_x = read_word_2c(0x43)
    gyro_y = read_word_2c(0x45) 
    gyro_z = read_word_2c(0x47)
```

## 🔋 Güç Yönetimi Devresi

### 🔌 Pil ve Şarj Sistemi

```
[18650 Li-ion Battery Pack 3S2P]
            │
    ┌───────┴───────┐
    │  BMS Module   │ ← Battery Management System
    │  • Protection │
    │  • Balancing  │
    │  • Monitoring │
    └───────┬───────┘
            │
    ┌───────┴───────┐
    │ Power Switch  │ ← Ana güç düğmesi
    │   DPDT 10A    │
    └───────┬───────┘
            │
    ┌───────┴───────┐
    │ Voltage Reg.  │ ← LM2596 Buck Converter
    │ 12V → 5V/5A   │
    └───────┬───────┘
            │
    ┌───────┴───────┐
    │ Distribution  │ ← Güç dağıtım barası
    │   12V Rail    │
    │   5V Rail     │
    │   3.3V Rail   │
    └───────────────┘
```

#### Pil Koruma Devresi (BMS)
```
🔋 BMS Features:
- Overvoltage Protection:  >4.3V/cell
- Undervoltage Protection: <2.8V/cell  
- Overcurrent Protection:  >10A
- Temperature Protection:  >60°C
- Cell Balancing:          ±50mV
- Short Circuit:           <100μs

📊 Monitoring Signals:
- Battery Voltage: ADC Channel 0
- Cell Voltages:   I2C Bus (0x48)
- Temperature:     GPIO 22 (1-Wire)
- Current:         INA219 (I2C 0x40)
```

### ⚡ Acil Durum Güç Kesicisi

```
    [Emergency Stop Button]
           │
    ┌──────┴──────┐
    │   Relay     │ ← 12V SPDT Relay
    │   Coil      │   (Fail-safe type)
    └──────┬──────┘
           │
    ┌──────┴──────┐
    │ Power Line  │ ← Ana güç hattını keser
    │  Breaker    │
    └─────────────┘

Kod kontrolü:
GPIO.setup(EMERGENCY_STOP, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def emergency_stop_callback(channel):
    # Tüm motorları durdur
    stop_all_motors()
    # Güç kesicisini etkinleştir  
    GPIO.output(POWER_RELAY, LOW)
    # Acil durum logunu kaydet
    log_emergency_stop()

GPIO.add_event_detect(EMERGENCY_STOP, GPIO.FALLING, 
                     callback=emergency_stop_callback)
```

## 📱 İletişim ve Arayüz Devreleri

### 📶 WiFi/Bluetooth Modülü

```
    ┌─────────────────┐
    │ Raspberry Pi 4  │
    │ Built-in        │
    │ • WiFi 802.11ac │
    │ • Bluetooth 5.0 │
    │ • Antenna PCB   │
    └─────────────────┘
           │
    ┌──────┴──────┐
    │  External   │ ← Harici anten (isteğe bağlı)
    │   Antenna   │   2.4/5GHz dual-band
    │   U.FL      │
    └─────────────┘

Performans:
- WiFi Range: ~20m indoor
- Bluetooth: ~10m
- Data Rate: 150Mbps (2.4GHz), 433Mbps (5GHz)
```

### 💡 LED Status Göstergeleri

```
    [Status LED Array]
    
    🔴 Power LED    (GPIO 12) ← Güç durumu
    🟢 WiFi LED     (GPIO 13) ← Ağ bağlantısı  
    🔵 Status LED   (GPIO 6)  ← Sistem durumu
    🟡 Activity LED (GPIO 5)  ← Hareket durumu

LED Kontrol Kodu:
class StatusLEDs:
    def __init__(self):
        self.power_led = 12
        self.wifi_led = 13  
        self.status_led = 6
        self.activity_led = 5
        
    def set_power(self, state):
        GPIO.output(self.power_led, state)
        
    def blink_status(self, pattern):
        # Morse code benzeri pattern
        for signal in pattern:
            GPIO.output(self.status_led, HIGH)
            time.sleep(signal)
            GPIO.output(self.status_led, LOW)
            time.sleep(0.1)
```

## 🔧 PCB Tasarım Dosyaları

### 📐 Katman Bilgileri (4-Layer PCB)

```
Layer Stack-up:
┌─────────────────┐ ← Top Layer (Components)
│   Signal L1     │   Trace width: 0.2mm min
├─────────────────┤ ← Prepreg
│   Ground L2     │   Pour: Solid ground plane
├─────────────────┤ ← Core (1.6mm)
│   Power L3      │   Pour: +5V, +3.3V planes
├─────────────────┤ ← Prepreg  
│   Signal L4     │   Bottom layer routing
└─────────────────┘ ← Bottom Layer

Total Thickness: 1.6mm ±10%
Copper Weight: 1oz (35μm)
Via Size: 0.2mm drill, 0.45mm pad
```

#### PCB Spesifikasyonları
```
📏 Board Dimensions: 100mm × 80mm
🔌 Connector Types:
   - GPIO Header: 2×20 pin, 2.54mm pitch
   - Motor Connectors: JST-XH 2-pin
   - Sensor Headers: JST-PH 4-pin
   - Power Input: DC Jack 5.5/2.1mm

🛡️ Protection Features:
   - ESD Protection on all I/O
   - Fuse protection on power rails
   - TVS diodes on motor outputs
   - Thermal pads under regulators
```

### 🎨 Component Placement

```
    Top View PCB Layout:
    
    ┌─────────────────────────────────┐
    │ [J1]              [LED1][LED2] │ ← Status LEDs
    │  Power            [LED3][LED4] │
    │                                │
    │ [U1]           [J2]            │ ← Raspberry Pi
    │ Buck           GPIO             │   connector
    │ Conv.          Header           │
    │                                │
    │ [U2]    [U3]         [Q1][Q2]  │ ← Motor drivers
    │ Motor   Sensor       FETs       │
    │ Driver  Mux                     │
    │                                │
    │ [J3][J4]      [J5][J6]         │ ← Motor/Sensor
    │ Motor         Sensors           │   connectors
    └─────────────────────────────────┘

Component Count: 
- ICs: 8
- Passives: 45 (R:20, C:15, L:3, D:7)
- Connectors: 6
- LEDs: 4
```

## 📋 Üretim ve Test Dosyaları

### 🏭 Üretim Gereksinimleri

#### Gerber Files
```
📁 Manufacturing Files:
├── PCB-Top-Copper.gbr
├── PCB-Bottom-Copper.gbr  
├── PCB-Top-Soldermask.gbr
├── PCB-Bottom-Soldermask.gbr
├── PCB-Top-Silkscreen.gbr
├── PCB-Bottom-Silkscreen.gbr
├── PCB-Drill-File.drl
├── PCB-Pick-Place.csv
└── PCB-BOM.xlsx

🔧 Assembly Notes:
- Solder paste: Type 3, SAC305
- Reflow profile: Standard RoHS
- Wave solder: Not required
- Manual components: Connectors, through-hole
```

#### Bill of Materials (BOM)
```
Top 10 Critical Components:

1. U1 - LM2596S-5.0 (Buck Converter)
   Manufacturer: Texas Instruments
   Package: TO-263-5
   Quantity: 1

2. U2 - L298N (Motor Driver)  
   Manufacturer: STMicroelectronics
   Package: Multiwatt15
   Quantity: 1

3. J2 - 2×20 Pin Header (GPIO)
   Manufacturer: Samtec
   Part: TSW-120-07-T-D
   Quantity: 1

4. C1 - 1000μF/16V (Power Filter)
   Manufacturer: Panasonic  
   Package: Radial 10mm
   Quantity: 2

5. L1 - 100μH Power Inductor
   Manufacturer: Bourns
   Package: SRR1260
   Quantity: 1
```

### 🧪 Test Prosedürleri

#### In-Circuit Test (ICT)
```
🔍 Test Points:
TP1: +12V Input
TP2: +5V Rail
TP3: +3.3V Rail  
TP4: Ground
TP5: Motor 1 Output
TP6: Motor 2 Output
TP7: I2C Clock
TP8: I2C Data

Test Sequence:
1. Power-on test
2. Voltage rail verification
3. Digital I/O test
4. Analog measurement
5. Communication test
6. Load test
```

#### Functional Test
```python
def pcb_functional_test():
    """PCB fonksiyonel test prosedürü"""
    
    # 1. Güç sistemi testi
    assert measure_voltage("5V_RAIL") == 5.0 ± 0.1
    assert measure_voltage("3V3_RAIL") == 3.3 ± 0.1
    
    # 2. GPIO testi
    for pin in GPIO_PINS:
        set_gpio_high(pin)
        assert read_gpio(pin) == HIGH
        set_gpio_low(pin)  
        assert read_gpio(pin) == LOW
    
    # 3. I2C haberleşme testi
    devices = scan_i2c_bus()
    assert 0x68 in devices  # MPU6050
    assert 0x40 in devices  # INA219
    
    # 4. Motor sürücü testi
    set_motor_pwm(1, 128)  # %50 duty cycle
    assert measure_motor_voltage(1) == 6.0 ± 0.5
    
    # 5. Sensör arayüz testi
    trigger_ultrasonic()
    echo_time = measure_echo_pulse()
    assert 0.1 < echo_time < 10  # ms
    
    print("✅ Tüm testler BAŞARILI!")
```

## 📚 Referans Dökümanları

### 📖 Datasheet Referansları

#### Ana Bileşenler
```
📄 Önemli Datasheetler:
1. Raspberry Pi 4 - Hardware Manual
2. L298N - Dual Motor Driver Datasheet  
3. LM2596 - Buck Converter Datasheet
4. HC-SR04 - Ultrasonic Sensor Manual
5. MPU6050 - 6-axis IMU Datasheet
6. Pi Camera v2 - Technical Specifications

🔗 Download Links:
- RPi4: raspberrypi.org/documentation
- L298N: st.com/resource/en/datasheet
- LM2596: ti.com/lit/ds/symlink
- HC-SR04: micropik.com/PDF
- MPU6050: invensense.tdk.com/download-pdf
```

#### Uygulama Notları
```
📝 Application Notes:
AN001: Motor Drive Circuit Design
AN002: Power Supply Noise Filtering  
AN003: I2C Bus Design Guidelines
AN004: EMI/EMC Considerations
AN005: Thermal Management

📐 Design Rules:
- Minimum trace width: 0.2mm (8 mil)
- Via size: 0.2mm drill, 0.45mm pad
- Clearance: 0.15mm minimum
- Ground pour: Solid on L2
- Power pour: Split on L3 (5V/3.3V)
```

## 🔄 Versiyon Kontrolü ve Güncellemeler

### 📊 Şema Versiyon Geçmişi

```
🗓️ Version History:

v1.0 (Jan 2024)
├─ Initial design
├─ Basic motor control
└─ Single sensor support

v1.1 (Mar 2024)  
├─ Added IMU sensor
├─ Improved power filtering
└─ Status LED array

v1.2 (Jun 2024)
├─ Enhanced motor driver
├─ BMS integration  
├─ EMI improvements
└─ Cost optimization

v2.0 (Dec 2024) ← Current
├─ 4-layer PCB design
├─ Advanced sensor hub
├─ Modular connectors
├─ Production ready
└─ CE/FCC compliance

v2.1 (Planned Q1 2025)
├─ USB-C power delivery
├─ Wireless charging pad
├─ Additional sensor ports
└─ Miniaturization
```

### 🔧 Engineering Change Orders (ECO)

```
📋 Active ECOs:

ECO-024-001: Kamera bağlantı güçlendirme
├─ Problem: Ribbon cable kopması
├─ Çözüm: Strain relief ekleme
├─ Durum: Implemented in v2.0
└─ Test: ✅ Passed

ECO-024-002: Motor akım limitleme  
├─ Problem: Aşırı akım çekimi
├─ Çözüm: Current sense resistor
├─ Durum: Design review
└─ Target: v2.1

ECO-024-003: WiFi performans iyileştirme
├─ Problem: Sinyal zayıflaması  
├─ Çözüm: Antenna placement optimization
├─ Durum: Prototyping
└─ Target: v2.1
```

## 🎯 Sonuç ve Öneriler

Bu şemalar OBA robotumuzun elektronik beynini oluşturuyor! Her bir devre özenle tasarlanmış ve test edilmiş durumda.

**🟢 Güçlü Yanlarımız:**
- ✅ Modüler tasarım
- ✅ Güvenilir güç sistemi
- ✅ Kapsamlı koruma devreleri  
- ✅ Kolay üretim

**🔧 Geliştirilecek Alanlar:**
- USB-C güç girişi
- Daha kompakt tasarım
- Kablosuz şarj desteği
- Ekstra sensör portları

**💡 Hacı Abi'nin Tavsiyeleri:**
1. Şemaları anlama sürenizi ayırın
2. Test noktalarını öğrenin  
3. Hata durumlarını bilin
4. Güvenlik önlemlerini ihmal etmeyin!

---

**📞 Teknik Destek:**
- E-posta: hardware@oba-robot.com
- Slack: #hardware-design
- Ofis: Electronics Lab, B1 katı

**Son Güncelleme**: Aralık 2024  
**Hazırlayan**: Hacı Abi & Hardware Team ⚡  
**Onay**: Chief Hardware Engineer ✅

*"İyi bir şema, iyi bir robotun başlangıcıdır!"* - Hacı Abi'nin elektronik felsefesi 🔌
