# 🔩 Mekanik Tasarım ve Montaj Detayları

## 🚜 Genel Şasi Tasarımı

### Ana Yapı Malzemeleri

#### Şasi Çerçevesi
- **Malzeme**: 6061-T6 Alüminyum Profil (40x40mm)
- **Et Kalınlığı**: 3mm
- **Boyutlar**: 800mm (L) x 600mm (W) x 400mm (H)
- **Ağırlık**: ~12kg (şasi + bağlantı elemanları)
- **Dayanım**: 250 MPa akma mukavemeti

#### Kaportalar ve Paneller
- **Malzeme**: 2mm Alüminyum Levha (5754 H22)
- **Kaportalar**: Su geçirmez tasarım (IP65)
- **Erişim Kapakları**: Quick-release mekanizması
- **Renk**: RAL 6010 (Çimen Yeşili) + Reflektif Şeritler

```
Şasi Layout (Üstten Görünüm):
┌────────────────────────────────────────┐ ← 800mm
│  [Kamera]     [Anten]      [GPS?]     │
│                                        │
│ ┌─────────┐              ┌─────────┐  │
│ │ Sol     │   [Batarya]  │ Sağ     │  │ ← 600mm
│ │ Palet   │   [Bölümü]   │ Palet   │  │
│ │ Motor   │              │ Motor   │  │
│ └─────────┘              └─────────┘  │
│                                        │
│     [Biçme Motor]    [Elektronik]     │
│        [Bölümü]       [Bölümü]        │
└────────────────────────────────────────┘
```

### 🎨 3D Model ve Teknik Çizimler

#### CAD Dosya Yapısı
```
📁 3D_Models/
├── 📄 OBA_Assembly_v1.0.step     - Ana montaj
├── 📄 Chassis_Frame.step         - Şasi çerçevesi
├── 📄 Track_Assembly.step        - Palet sistemi
├── 📄 Mower_Deck.step           - Biçme platformu
├── 📄 Battery_Compartment.step  - Batarya bölümü
├── 📄 Electronics_Housing.step  - Elektronik kutusu
└── 📄 Charging_Dock.step        - Şarj istasyonu
```

#### Ana Boyutlar ve Toleranslar
| Bileşen | Nominal (mm) | Tolerans | Kritiklik |
|---------|-------------|----------|-----------|
| Şasi Uzunluk | 800 | ±2 | Yüksek |
| Şasi Genişlik | 600 | ±2 | Yüksek |
| Tekerlek Arası | 540 | ±1 | Kritik |
| Yer Clearance | 120 | +5/-0 | Orta |
| Biçme Yükseklik | 30-80 | ±1 | Kritik |

## 🚗 Palet (Track) Sistemi

### Palet Mekanizması Tasarımı

#### Sürücü Dişli (Drive Sprocket)
- **Malzeme**: 7075-T6 Alüminyum
- **Diş Sayısı**: 20 diş
- **Modül**: 2.0
- **Çap**: 42mm
- **Genişlik**: 25mm
- **Yağlama**: Sealed bearing + gres

#### Palet Zinciri
- **Tip**: Kauçuk + fiber takviyeli
- **Genişlik**: 150mm
- **Kalınlık**: 12mm
- **Pattern**: Çapraz desenli (grip için)
- **Uzunluk**: 1200mm (her palet için)
- **Yaşam Süresi**: 2000+ çalışma saati

#### Gergi Sistemi
```
Palet Gergi Mekanizması:
                Motor Dişlisi
                     ●
                    /│\
                   / │ \
    Gergi Mili ──●   │   ●── Boşta Dönen Mil
                  \  │  /
                   \ │ /
                    \│/
                     ●
                Destek Mili

- Gergi Ayarı: 10-15mm sarkma
- Gergi Kuvveti: 200N nominal
- Ayar Mekanizması: M8 threaded rod
- Kilitleme: Nylock nut
```

### Motor Montaj Detayları

#### Sol Palet Motor Montajı
```python
# Motor montaj koordinatları (şasi referansı)
LEFT_MOTOR_POSITION = {
    'x': 100,    # mm (şasi önünden)
    'y': -270,   # mm (merkez çizgiden)
    'z': 150,    # mm (zeminden)
    'rotation': 0  # derece
}

# Bağlantı detayları
mounting_bolts = {
    'count': 4,
    'size': 'M6x20',
    'material': 'Stainless Steel A2',
    'torque': '8 Nm',
    'thread_locker': 'Blue Loctite'
}
```

#### Sağ Palet Motor Montajı (Mirror)
```python
RIGHT_MOTOR_POSITION = {
    'x': 100,    # mm (şasi önünden)
    'y': +270,   # mm (merkez çizgiden) 
    'z': 150,    # mm (zeminden)
    'rotation': 180  # derece (mirror)
}
```

### Palet Bakım ve Ayar

#### Günlük Kontroller
- [ ] Palet gerginliği (10-15mm sarkma)
- [ ] Kauçuk yüzeyde yırtık/aşınma var mı?
- [ ] Motor yağ sızıntısı var mı?
- [ ] Yabancı madde (çakıl, dal) sıkışmış mı?

#### Haftalık Bakım
```python
def weekly_track_maintenance():
    """Haftalık palet bakımı"""
    
    print("🔧 Haftalık Palet Bakımı")
    print("=" * 25)
    
    # 1. Palet gerginlik kontrolü
    print("1. Palet gerginlik ölçümü:")
    print("   - Sol palet: __ mm sarkma")
    print("   - Sağ palet: __ mm sarkma")
    print("   (Hedef: 10-15mm)")
    
    # 2. Aşınma kontrolü
    print("2. Kauçuk aşınma kontrolü:")
    print("   - Desenin %80'i mevcut mu?")
    print("   - Yırtık/çatlak var mı?")
    
    # 3. Yağlama
    print("3. Bearing yağlama:")
    print("   - Gres miktarı yeterli mi?")
    print("   - Hareket akıcı mı?")
    
    # 4. Temizlik
    print("4. Temizlik:")
    print("   - Çakıl/dal temizlemesi")
    print("   - Su ile yıkama")
    print("   - Kurulama")
```

## 🌱 Biçme Sistemi Mekanizması

### Biçme Motoru ve Bıçak Montajı

#### Motor Montaj Konumu
```
Biçme Motor Pozisyonu:
┌─────────────────────────────┐
│         Şasi                │
│                             │
│  ┌─────────────────────┐    │
│  │    Biçme Motoru     │    │
│  │        ●            │    │
│  └─────────┬───────────┘    │
│            │                │
│      ┌─────┴─────┐          │
│      │   Bıçak   │          │
│      │  Sistemi  │          │
│      └───────────┘          │
└─────────────────────────────┘

Koordinatlar:
- X: 650mm (şasi önünden)
- Y: 0mm (merkez çizgi)  
- Z: 60mm (zeminden bıçak ucu)
```

#### Bıçak Konfigürasyonu
- **Tip**: 3-bıçaklı rotor sistemi
- **Malzeme**: Yüksek karbon çelik (HRC 58-62)
- **Çap**: 300mm (cutting circle)
- **Dönüş Hızı**: 2400 RPM
- **Biçme Genişliği**: 280mm etkili
- **Yükseklik Ayarı**: 30-80mm (lineer aktüatör ile)

#### Lineer Aktüatör Sistemi
```python
class MowerHeightController:
    def __init__(self):
        self.min_height = 30    # mm
        self.max_height = 80    # mm
        self.current_height = 50  # mm default
        
        # Lineer aktüatör specs
        self.stroke_length = 50   # mm
        self.load_capacity = 500  # N
        self.speed = 10          # mm/s
        self.position_accuracy = 0.5  # mm
        
    def set_cutting_height(self, target_height):
        """Biçme yüksekliğini ayarla"""
        if not (self.min_height <= target_height <= self.max_height):
            raise ValueError(f"Height must be between {self.min_height}-{self.max_height}mm")
            
        # Actuator position hesapla
        position_mm = target_height - self.min_height
        position_percent = (position_mm / self.stroke_length) * 100
        
        # PWM ile actuator kontrolü
        self.move_actuator_to_position(position_percent)
        self.current_height = target_height
        
        print(f"Biçme yüksekliği {target_height}mm olarak ayarlandı")
        
    def emergency_raise(self):
        """Acil durum - bıçağı maksimum yüksekliğe kaldır"""
        self.set_cutting_height(self.max_height)
        print("🚨 Acil durum: Bıçak maksimum yükseklikte!")
```

### Güvenlik Sistemleri

#### Bıçak Korumaları
```
Güvenlik Önlemleri:
├── Çevre Koruması: Plastik deflektör
├── Alt Koruma: Çarpma sensörü
├── Acil Durdurma: Bumper switch
├── Tip Switch: Devrilme sensörü
└── Lift Detection: Kaldırılma algılama
```

#### Sensör Montaj Noktaları
| Sensör | Konum | Bağlantı | Fonksiyon |
|--------|--------|----------|----------|
| Tip Switch | Şasi altı | GPIO 23 | Devrilme algılama |
| Lift Sensor | Motor üstü | GPIO 24 | Kaldırılma algılama |
| Bump Sensor | Ön tampon | GPIO 25 | Çarpışma algılama |
| Vibration | Motor gövde | I2C | Bıçak sıkışması |

## 🔋 Batarya Bölümü Tasarımı

### Batarya Muhafazası

#### Yapısal Özellikler
- **Malzeme**: Alüminyum 5754 H22 (deniz tipi)
- **Kalınlık**: 3mm
- **Boyutlar**: 350 x 200 x 150mm
- **Ağırlık**: 2.1kg (kutu + bağlantılar)
- **Koruma Sınıfı**: IP66 (toz/su geçirmez)

#### Soğutma Sistemi
```
Batarya Soğutma Tasarımı:
                     ┌─ Fan (12V, 0.3A)
                     │
    Hava Giriş ──────┼────→ Batarya ──────→ Hava Çıkış
    (Alt filtresiz)   │    (Soğutma)      (Üst ızgaralı)
                     │
                     └─ Temp Sensör (NTC)
                     
Soğutma Algoritması:
- 25°C altı: Fan OFF
- 25-35°C: Fan %30
- 35-45°C: Fan %60  
- 45°C üstü: Fan %100 + Uyarı
```

#### Batarya Montaj Detayları
```python
class BatteryMounting:
    def __init__(self):
        # Batarya fiziksel özellikleri
        self.battery_dimensions = {
            'length': 330,    # mm
            'width': 175,     # mm  
            'height': 220,    # mm
            'weight': 28,     # kg
            'center_of_gravity': (165, 87.5, 110)  # mm
        }
        
        # Montaj noktaları
        self.mounting_points = [
            {'x': 50, 'y': 25, 'z': 10},    # Sol ön
            {'x': 280, 'y': 25, 'z': 10},   # Sağ ön
            {'x': 50, 'y': 150, 'z': 10},   # Sol arka
            {'x': 280, 'y': 150, 'z': 10}   # Sağ arka
        ]
        
        # Bağlantı elemanları
        self.fasteners = {
            'type': 'M8x25 Allen bolt',
            'material': 'Stainless Steel A4',
            'torque': '25 Nm',
            'washer': 'Lock washer + flat washer',
            'thread_locker': 'Red Loctite (high strength)'
        }
        
    def calculate_mounting_load(self):
        """Montaj noktası yük hesaplaması"""
        weight_n = self.battery_dimensions['weight'] * 9.81  # N
        
        # Statik yük (ağırlık)
        static_load_per_point = weight_n / 4  # 4 montaj noktası
        
        # Dinamik yük faktörü (3G acceleration)
        dynamic_factor = 3.0
        dynamic_load_per_point = static_load_per_point * dynamic_factor
        
        # Güvenlik faktörü
        safety_factor = 2.0
        design_load = dynamic_load_per_point * safety_factor
        
        return {
            'static_load': static_load_per_point,  # ~69N
            'dynamic_load': dynamic_load_per_point,  # ~206N
            'design_load': design_load  # ~412N per mounting point
        }
```

## 📦 Elektronik Kutusu Tasarımı

### Ana Elektronik Muhafazası

#### Kutu Özellikleri
- **Boyutlar**: 300 x 250 x 100mm
- **Malzeme**: ABS plastik + alüminyum taban
- **Koruma**: IP65 (outdoor kullanım)
- **Soğutma**: Passive heatsink + fan (opsiyonel)
- **Montaj**: 4x rubber isolator (titreşim damperi)

#### İç Yerleşim Planı
```
Elektronik Kutu Layout (Üstten Görünüm):
┌─────────────────────────────────────────┐ ← 300mm
│ [Power Distribution]  [DC-DC Modules]  │
│                                         │
│ ┌─────────────────┐  ┌───────────────┐  │
│ │ Raspberry Pi 4B │  │ Motor Drivers │  │ ← 250mm
│ │ + Heatsink      │  │ (3x BLDC)     │  │
│ └─────────────────┘  └───────────────┘  │
│                                         │
│ [I/O Terminal]      [Relay Board]      │
│ [Blocks]            [6x Relays]        │
└─────────────────────────────────────────┘

Z-Layer (Dikey Yerleşim):
├── Layer 1 (Bottom): Mounting plate
├── Layer 2: Power distribution board
├── Layer 3: Motor driver modules  
├── Layer 4: Raspberry Pi + cooling
└── Layer 5 (Top): Cable management
```

### Kablo Yönetimi

#### Kablo Geçişleri
- **Güç Kabloları**: M20 cable gland (su geçirmez)
- **Sinyal Kabloları**: M16 cable gland  
- **Anten Kabloları**: SMA connector (panel mount)
- **USB Portları**: Waterproof USB panel connector

#### Kablo Etiketleme Sistemi
```python
cable_labeling_system = {
    'power_cables': {
        'P01': '24V Main Power (Red)',
        'P02': '24V Ground (Black)',
        'P03': '12V Rail (Orange)',
        'P04': '5V Rail (Yellow)'
    },
    
    'motor_cables': {
        'M01': 'Left Track Motor (Blue)',
        'M02': 'Right Track Motor (Green)', 
        'M03': 'Mower Motor (Purple)'
    },
    
    'sensor_cables': {
        'S01': 'IMU I2C Bus (Gray)',
        'S02': 'Left Encoder (Brown)',
        'S03': 'Right Encoder (White)',
        'S04': 'Camera CSI (Pink)'
    },
    
    'control_cables': {
        'C01': 'Emergency Stop (Red)',
        'C02': 'Status LEDs (Green)',
        'C03': 'Antenna WiFi (Blue)',
        'C04': 'USB Debug (White)'
    }
}
```

## 🛠️ Montaj Prosedürü

### Ana Montaj Sırası

#### 1. Şasi Hazırlığı
```bash
#!/bin/bash
# Şasi montaj kontrolü

echo "🔧 Şasi Montaj Kontrolü"
echo "========================"

echo "□ Alüminyum profillerin kesilmiş boyutları doğru mu?"
echo "□ Köşe bağlantıları için delikler açıldı mı?"
echo "□ Yüzey işlemi (anodizasyon) tamamlandı mı?"
echo "□ Bağlantı elemanları (vidalar, T-slot nuts) hazır mı?"

echo -e "\n✅ Şasi hazırlık tamamlandı!"
```

#### 2. Motor Montajı
```python
def mount_motors():
    """Motor montaj prosedürü"""
    
    print("🔧 Motor Montaj Prosedürü")
    print("=" * 25)
    
    motors = ['left_track', 'right_track', 'mower']
    
    for motor in motors:
        print(f"\n📍 {motor.upper()} motor montajı:")
        
        # 1. Motor bracket kontrolü
        print("  1. Motor bracket'i şasiye monte et")
        print("     - 4x M8x20 vida kullan")
        print("     - Tork: 25 Nm")
        print("     - Thread locker uygula")
        
        # 2. Motor montajı
        print("  2. Motoru bracket'e monte et")
        print("     - 4x M6x16 vida kullan") 
        print("     - Tork: 8 Nm")
        print("     - Gasket kontrolü yap")
        
        # 3. Kablo bağlantısı
        print("  3. Motor kablolarını bağla")
        print("     - Faz sırasına dikkat et")
        print("     - Kablo geçiş contası sık")
        print("     - Enkoder kablolarını bağla")
        
        input(f"  ✅ {motor} montajı tamamlandı mı? (ENTER)")
        
    print("\n🎯 Tüm motorlar monte edildi!")
```

#### 3. Elektronik Kurulum
```python
def install_electronics():
    """Elektronik kurulum prosedürü"""
    
    steps = [
        "Raspberry Pi'yi heatsink ile kutuya monte et",
        "Motor driver kartlarını yerleştir", 
        "Güç dağıtım kartını bağla",
        "Kablo bağlantılarını yap",
        "İlk güç verme testi",
        "Software yükleme ve test"
    ]
    
    for i, step in enumerate(steps, 1):
        print(f"{i}. {step}")
        input("   Tamamlandı mı? (ENTER)")
        
    print("✅ Elektronik kurulum tamamlandı!")
```

### 🔧 Özel Aletler ve Malzemeler

#### Gerekli Aletler
```python
required_tools = {
    'cutting_tools': [
        'Metal kesme testeresi (alüminyum için)',
        'Drill press (hassas delme için)',
        'Tap set (M6, M8 kılavuzu)',
        'File set (kenar düzeltme)'
    ],
    
    'assembly_tools': [
        'Torque wrench (2-50 Nm)',
        'Allen key set (2-10mm)',
        'Socket set (metric)',
        'Crimping tool (terminal için)',
        'Heat gun (shrink tube için)'
    ],
    
    'measurement_tools': [
        'Digital caliper (0.01mm hassasiyet)',
        'Square (90° kontrolü)',
        'Level (düzlem kontrolü)',
        'Multimeter (elektrik testi)'
    ],
    
    'special_tools': [
        'Bearing puller/installer',
        'Thread locker (blue, red)',
        'Cable ties (various sizes)',
        'Heat shrink tubes'
    ]
}
```

#### Montaj Malzemeleri
| Malzeme | Adet | Boyut | Spec |
|---------|------|-------|------|
| M8x20 Bolt | 16 | Allen head | A2 Stainless |
| M6x16 Bolt | 12 | Allen head | A2 Stainless |
| M8 Washer | 32 | Flat + Lock | A2 Stainless |
| T-Slot Nut | 20 | M8 | Alüminyum |
| Cable Tie | 50 | 200mm | UV resistant |
| Thread Locker | 2 | 10ml | Blue + Red |

### 📋 Kalite Kontrol Listesi

#### Montaj Sonrası Kontroller
```python
def quality_control_checklist():
    """Montaj sonrası kalite kontrol"""
    
    mechanical_checks = [
        "Tüm vidalar belirtilen torkta sıkıldı mı?",
        "Hareketli parçalar serbestçe dönüyor mu?",
        "Kablolar gergm tutuyor ve doğru rotada mı?",
        "Su geçirmez contalar yerinde mi?",
        "Keskin kenarlar var mı? (güvenlik)",
        "Ağırlık dağılımı dengeli mi?"
    ]
    
    electrical_checks = [
        "Tüm güç bağlantıları doğru polaritede mi?",
        "İzolasyon direnci >1MΩ mu?",
        "Motor dirençleri spesifikasyonda mı?",
        "Enkoder sinyalleri temiz mi?",
        "Emergency stop fonksiyonel mi?",
        "LED status ışıkları çalışıyor mu?"
    ]
    
    functional_checks = [
        "Robot düz çizgide gidiyor mu?",
        "Dönüş manevrası doğru mu?",
        "Biçme motoru titreşimsiz çalışıyor mu?",
        "Yükseklik ayarı hassas çalışıyor mu?",
        "Batarya şarj/deşarj normal mi?",
        "Web arayüzü erişilebilir mi?"
    ]
    
    print("🔍 Kalite Kontrol Listesi")
    print("=" * 26)
    
    sections = [
        ("Mekanik Kontroller", mechanical_checks),
        ("Elektrik Kontroller", electrical_checks), 
        ("Fonksiyonel Testler", functional_checks)
    ]
    
    for section_name, checks in sections:
        print(f"\n📋 {section_name}:")
        for check in checks:
            answer = input(f"  □ {check} (y/n): ")
            if answer.lower() != 'y':
                print(f"    ❌ Düzeltme gerekli: {check}")
                
    print("\n✅ Kalite kontrol tamamlandı!")

if __name__ == "__main__":
    quality_control_checklist()
```

---

**🎯 Hacı Abi Notu:** Mekanik tasarım robotun iskeleti gibi, sağlam yapmazsan robot dağılır! CAD çizimlerini doğru yap, toleransları hesapla. Motor montajında alignment önemli, titreşim yapar. Batarya güvenliğini es geçme, yangın riski var. Kablo yönetimini iyi yap, karışık kablolar sorun çıkarır. Kalite kontrol listesini atlama, sonradan sorun çıkarsa çok zor bulursun! 🤖🔧
