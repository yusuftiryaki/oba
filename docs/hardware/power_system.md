# ⚡ Güç Sistemi Şeması ve Hesaplamaları

## 🔋 Sistem Genel Bakışı

### Ana Güç Bileşenleri

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ 150W Güneş     │────│ MPPT Regülatör   │────│ 100Ah İstasyon │
│ Paneli         │    │ (30A)            │    │ Bataryası       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                    ┌──────────────────┐
                    │ Şarj Konnektörü  │
                    │ (30A, 24V)       │
                    └──────────────────┘
                                │
            ┌─────────────────────────────────────┐
            │        Robot Ana Sistemi            │
            │  ┌───────────────────────────────┐  │
            │  │ 24V LiFePO4 Batarya (20Ah)   │  │
            │  └───────────────────────────────┘  │
            │                 │                   │
            │    ┌─────────────┴─────────────┐    │
            │    │     Güç Dağıtım Kartı    │    │
            │    └─┬─────┬─────┬─────┬─────┬─┘    │
            │      │     │     │     │     │      │
            │   Motor  Motor Motor  5V   12V     │
            │   24V    24V   24V   Rail Rail     │
            └─────────────────────────────────────┘
```

### 🔌 Voltaj Seviyeleri

| Seviye | Nominal | Min | Max | Kullanım Alanı |
|--------|---------|-----|-----|----------------|
| 24V | 24.0V | 20.0V | 29.4V | Motorlar, ana güç |
| 12V | 12.0V | 11.0V | 13.8V | Lineer aktüatör |
| 5V | 5.0V | 4.8V | 5.2V | Raspberry Pi, sensörler |
| 3.3V | 3.3V | 3.0V | 3.6V | I2C, GPIO |

## 🔋 Batarya Sistemi

### Robot Ana Bataryası

#### LiFePO4 Teknik Özellikleri
- **Nominal Voltaj**: 25.6V (8S konfigürasyon)
- **Kapasite**: 20Ah
- **Enerji**: 512Wh
- **Maksimum Akım**: 40A (2C)
- **Şarj Voltajı**: 29.2V (3.65V/hücre)
- **Kesim Voltajı**: 20.0V (2.5V/hücre)
- **Çevrim Ömrü**: >3000 çevrim (%80 kapasite)

#### Batarya Yönetim Sistemi (BMS)
```
BMS Özellikleri:
├── Balancing: Aktif balans (100mA/hücre)
├── Overcurrent: 45A kesim
├── Overvoltage: 3.8V/hücre kesim
├── Undervoltage: 2.3V/hücre kesim
├── Temperature: -10°C ile +60°C arası
└── CAN Bus: Durum iletişimi
```

#### Kapasite Hesaplamaları

**Temel Tüketim Analizi:**
```python
# Güç tüketimi hesaplaması
def calculate_battery_life():
    # Sistem bileşenleri (Watt)
    raspberry_pi = 15      # Pi 4B + accessories
    motors_idle = 50       # 3 motor idle
    motors_working = 550   # Normal biçme modu
    sensors = 10           # IMU, enkoder, kamera
    web_server = 5         # Network + web interface
    
    # Çalışma modları
    active_time = 1.5      # saat (aktif biçme)
    idle_time = 0.5        # saat (navigasyon/bekeme)
    
    # Ortalama güç hesabı
    avg_power = (
        (motors_working * active_time + motors_idle * idle_time) / 2 +
        raspberry_pi + sensors + web_server
    )
    
    battery_capacity = 512  # Wh
    runtime_hours = battery_capacity / avg_power
    
    return runtime_hours

# Sonuç: ~2.1 saat çalışma süresi
```

### Şarj İstasyonu Bataryası

#### Lead-Acid Deep Cycle
- **Nominal Voltaj**: 24V (2x 12V seri)
- **Kapasite**: 100Ah (C20)
- **Enerji**: 2400Wh
- **Maksimum Şarj**: 14.4V/batarya
- **Float Voltaj**: 13.6V/batarya
- **Ömür**: 5+ yıl (proper cycling)

## ☀️ Güneş Enerjisi Sistemi

### 150W Monokristal Panel

#### Elektriksel Özellikler
```
STC Koşulları (1000W/m², 25°C):
├── Maksimum Güç: 150W
├── Vmp: 18.5V (maksimum güç voltajı)
├── Imp: 8.1A (maksimum güç akımı)
├── Voc: 22.7V (açık devre voltajı)
├── Isc: 8.8A (kısa devre akımı)
└── Verimlilik: %18.5
```

#### Sıcaklık Katsayıları
- **Güç**: -0.41%/°C
- **Voltaj**: -0.32%/°C  
- **Akım**: +0.05%/°C

#### Günlük Enerji Üretimi

```python
def calculate_daily_energy(panel_power=150, location="Istanbul"):
    """Günlük enerji üretimi hesaplama"""
    
    # Aylık güneş ışınımı (kWh/m²/gün) - İstanbul
    solar_irradiance = {
        'jan': 1.8, 'feb': 2.6, 'mar': 3.8, 'apr': 5.1,
        'may': 6.4, 'jun': 7.2, 'jul': 7.4, 'aug': 6.8,
        'sep': 5.3, 'oct': 3.9, 'nov': 2.4, 'dec': 1.6
    }
    
    # Sistem verimliliği
    mppt_efficiency = 0.97
    cable_loss = 0.95
    dust_factor = 0.95
    temperature_loss = 0.90  # Yaz ayları için
    
    total_efficiency = (mppt_efficiency * cable_loss * 
                       dust_factor * temperature_loss)
    
    # Aylık enerji üretimi
    monthly_energy = {}
    for month, irradiance in solar_irradiance.items():
        daily_energy = (panel_power / 1000) * irradiance * total_efficiency
        monthly_energy[month] = daily_energy
        
    return monthly_energy

# Sonuç: Yaz 0.9kWh/gün, Kış 0.13kWh/gün
```

### MPPT Şarj Regülatörü

#### Teknik Özellikler
- **Model**: MPPT 30A 12V/24V
- **Maksimum PV Voltaj**: 100V
- **Maksimum PV Akım**: 30A
- **Sistem Voltajı**: Otomatik 12V/24V
- **Verimlilik**: >97%
- **Koruma**: PV reverse, Battery reverse, Overload

#### Şarj Algoritması
```
3-Stage Charging:
├── Bulk Stage: Sabit akım (30A max)
├── Absorption: Sabit voltaj (29.2V)
└── Float: Bakım voltajı (27.6V)

Load Control:
├── LVD: 21.0V (Low Voltage Disconnect)
├── LVR: 25.2V (Low Voltage Reconnect)
└── Load Priority: Solar > Battery > Load
```

## 🔧 DC-DC Konvertörler

### 24V → 5V Buck Konvertör

#### Teknik Özellikler
- **Giriş Voltajı**: 18-32V DC
- **Çıkış Voltajı**: 5.0V ±2%
- **Maksimum Akım**: 8A (40W)
- **Verimlilik**: >90%
- **Koruma**: OCP, OVP, Thermal

#### Yük Dağılımı (5V Rail)
```
5V Güç Dağılımı:
├── Raspberry Pi 4B: 3.0A (15W)
├── IMU Sensörü: 0.05A (0.25W)
├── Enkoder Beslemesi: 0.2A (1W)
├── IR Sensörler: 0.1A (0.5W)
├── Pi Kamera: 0.3A (1.5W)
├── Soğutma Fanı: 0.3A (1.5W)
└── Reserve: 1.05A (5.25W)
────────────────────────────────
Toplam: 5.0A (25W)
```

### 24V → 12V Buck Konvertör

#### Teknik Özellikler
- **Giriş Voltajı**: 18-32V DC
- **Çıkış Voltajı**: 12.0V ±1%
- **Maksimum Akım**: 5A (60W)
- **Verimlilik**: >92%
- **Koruma**: OCP, OVP, SCP

#### Yük Dağılımı (12V Rail)
```
12V Güç Dağılımı:
├── Lineer Aktüatör: 3.0A (36W)
├── Aydınlatma LED: 0.5A (6W)
├── Acil Durum Sistemi: 0.3A (3.6W)
└── Reserve: 1.2A (14.4W)
─────────────────────────────────
Toplam: 5.0A (60W)
```

## ⚡ Güç Dağıtım Kartı

### Kartın Elektriksel Şeması

```
         24V+ (Battery)
              │
    ┌─────────┼─────────┐
    │    Main Fuse      │
    │     (50A)         │
    └─────────┼─────────┘
              │
    ┌─────────┴─────────┐
    │   Power Monitor   │
    │   (V, I, T)       │
    └─────────┼─────────┘
              │
    ┌─────────┼─────────┐
    │  Relay Matrix     │
    │  (Load Control)   │
    └─┬─┬─┬─┬─┼─┬─┬─┬─┬─┘
      │ │ │ │ │ │ │ │ │
      M M M │ │ │ │ │ LED
      O O O │ │ │ │ │
      T T T │ │ │ │ Emergency
      1 2 3 │ │ │ │
            │ │ │ Actuator
            │ │ │
            │ │ 12V Buck
            │ │
            │ 5V Buck
            │
        Emergency Stop
```

### Röle Kontrol Matrisi

| Röle | Yük | Akım | Kontrol Pin | Failsafe |
|------|-----|------|-------------|----------|
| R1 | Sol Palet Motor | 15A | GPIO 8 | NO |
| R2 | Sağ Palet Motor | 15A | GPIO 9 | NO |
| R3 | Biçme Motoru | 25A | GPIO 10 | NO |
| R4 | Lineer Aktüatör | 5A | GPIO 11 | NC |
| R5 | Aydınlatma | 2A | GPIO 22 | NO |
| R6 | Yedek | 10A | GPIO 27 | NO |

### Güvenlik Korumaları

```python
class PowerSafetySystem:
    def __init__(self):
        self.voltage_limits = {
            '24V': {'min': 20.0, 'max': 29.4},
            '12V': {'min': 11.0, 'max': 13.8}, 
            '5V': {'min': 4.8, 'max': 5.2}
        }
        
        self.current_limits = {
            'motor_left': 15,    # Ampere
            'motor_right': 15,
            'motor_mower': 25,
            'actuator': 5,
            'system_total': 45
        }
        
    def monitor_power(self):
        """Güç sistemini sürekli izle"""
        while True:
            # Voltaj kontrolü
            voltages = self.read_all_voltages()
            for rail, voltage in voltages.items():
                limits = self.voltage_limits[rail]
                if not (limits['min'] <= voltage <= limits['max']):
                    self.trigger_emergency_stop(f"Voltage fault: {rail}")
                    
            # Akım kontrolü
            currents = self.read_all_currents()
            for load, current in currents.items():
                if current > self.current_limits[load]:
                    self.shutdown_load(load)
                    
            # Sıcaklık kontrolü
            temp = self.read_system_temperature()
            if temp > 70:  # 70°C kritik sıcaklık
                self.thermal_shutdown()
                
            time.sleep(0.1)  # 100ms monitoring cycle
            
    def emergency_stop(self):
        """Acil durdurma prosedürü"""
        # Tüm motorları durdur
        GPIO.output([8, 9, 10], GPIO.LOW)
        
        # Kritik olmayan yükleri kes
        GPIO.output([22, 27], GPIO.LOW)
        
        # Sistem durumunu kaydet
        self.log_emergency_event()
        
        print("🚨 EMERGENCY STOP ACTIVATED!")
```

## 📊 Güç Analizi ve Optimizasyon

### Günlük Enerji Bütçesi

```python
def daily_energy_budget():
    """Günlük enerji bütçesi hesaplama"""
    
    # Mevcut kapasite
    battery_capacity = 512  # Wh (robot)
    daily_solar = 600      # Wh (ortalama - bahar/sonbahar)
    
    # Enerji tüketimi profili
    work_profile = {
        'morning_prep': {'power': 75, 'duration': 0.25},     # 18.75 Wh
        'morning_work': {'power': 550, 'duration': 1.5},     # 825 Wh
        'midday_charge': {'power': 25, 'duration': 2.0},     # 50 Wh
        'afternoon_work': {'power': 550, 'duration': 1.0},   # 550 Wh
        'evening_return': {'power': 200, 'duration': 0.25},  # 50 Wh
        'night_standby': {'power': 15, 'duration': 8.0}      # 120 Wh
    }
    
    total_consumption = sum(
        profile['power'] * profile['duration'] 
        for profile in work_profile.values()
    )
    
    energy_balance = daily_solar - total_consumption
    
    return {
        'consumption': total_consumption,
        'generation': daily_solar,
        'balance': energy_balance,
        'autonomy_days': battery_capacity / total_consumption if energy_balance < 0 else float('inf')
    }

# Sonuç: 1613 Wh tüketim, 600 Wh üretim → -1013 Wh açık
```

### Enerji Tasarrufu Stratejileri

#### 1. Adaptif Güç Yönetimi
```python
class AdaptivePowerManager:
    def __init__(self):
        self.power_modes = {
            'high_performance': {'cpu_freq': 1800, 'motor_max': 100},
            'balanced': {'cpu_freq': 1400, 'motor_max': 80},
            'eco_mode': {'cpu_freq': 1000, 'motor_max': 60},
            'low_power': {'cpu_freq': 600, 'motor_max': 40}
        }
        
    def select_power_mode(self, battery_percentage, workload):
        """Batarya durumuna göre güç modunu seç"""
        if battery_percentage > 80:
            return 'high_performance'
        elif battery_percentage > 60:
            return 'balanced'
        elif battery_percentage > 30:
            return 'eco_mode'
        else:
            return 'low_power'
```

#### 2. Regenerative Braking
```python
def regenerative_braking_energy():
    """Rejeneratif frenleme ile enerji geri kazanımı"""
    
    # Eğim azalma senaryosu
    robot_mass = 50        # kg
    height_drop = 5        # metre (günlük toplam eğim azalması)
    gravity = 9.81         # m/s²
    efficiency = 0.6       # Motor/kontrol verimi
    
    # Potansiyel enerji
    potential_energy = robot_mass * gravity * height_drop  # Joule
    recoverable_energy = potential_energy * efficiency     # Joule
    
    # Wh'ye çevir
    energy_wh = recoverable_energy / 3600
    
    return energy_wh  # ~4.1 Wh/gün

# Az da olsa enerji katkısı var
```

## 🔧 Bakım ve Test Prosedürleri

### Günlük Kontroller

```bash
#!/bin/bash
# Günlük güç sistemi kontrolü

echo "🔋 Günlük Güç Sistemi Kontrolü"
echo "==============================="

# Batarya voltajı kontrolü
python3 -c "
import power_monitor
pm = power_monitor.PowerMonitor()
voltage = pm.read_battery_voltage()
print(f'Batarya Voltajı: {voltage:.2f}V')
if voltage < 22.0:
    print('⚠️ Düşük Batarya!')
elif voltage > 28.0:
    print('⚠️ Aşırı Şarj!')
else:
    print('✅ Batarya Normal')
"

# Güneş paneli kontrolü
echo "☀️ Güneş paneli kontrol ediliyor..."
python3 -c "
import power_monitor
pm = power_monitor.PowerMonitor()
pv_voltage = pm.read_pv_voltage()
pv_current = pm.read_pv_current()
print(f'PV Voltaj: {pv_voltage:.2f}V')
print(f'PV Akım: {pv_current:.2f}A')
print(f'PV Güç: {pv_voltage * pv_current:.1f}W')
"

# Sistem sıcaklığı
echo "🌡️ Sistem sıcaklığı kontrol ediliyor..."
temp=$(cat /sys/class/thermal/thermal_zone0/temp)
temp_c=$((temp / 1000))
echo "CPU Sıcaklığı: ${temp_c}°C"

if [ $temp_c -gt 70 ]; then
    echo "⚠️ Yüksek Sıcaklık!"
else
    echo "✅ Sıcaklık Normal"
fi
```

### Haftalık Test Scripti

```python
#!/usr/bin/env python3
"""Haftalık güç sistemi testi"""

import time
import json
from datetime import datetime

class PowerSystemTest:
    def __init__(self):
        self.test_results = {}
        
    def run_full_test(self):
        """Tam güç sistemi testi"""
        print("🧪 Haftalık Güç Sistemi Testi")
        print("=" * 35)
        
        # 1. Batarya kapasitesi testi
        self.test_battery_capacity()
        
        # 2. Şarj sistemi testi
        self.test_charging_system()
        
        # 3. DC-DC konvertör testi
        self.test_dc_converters()
        
        # 4. Yük testi
        self.test_load_performance()
        
        # 5. Sonuçları kaydet
        self.save_test_results()
        
    def test_battery_capacity(self):
        """Batarya kapasitesi testi"""
        print("🔋 Batarya kapasitesi test ediliyor...")
        
        # Kontrollü deşarj testi (sadece simülasyon)
        # Gerçek uygulamada bataryayı tamamen deşarj etmeyiz
        
        # Voltaj-kapasite eğrisi kontrolü
        voltage_points = [
            (29.2, 100), (28.8, 95), (28.0, 85), (27.2, 75),
            (26.4, 65), (25.6, 50), (24.8, 35), (24.0, 20),
            (23.2, 10), (22.4, 5), (21.6, 2), (20.8, 0)
        ]
        
        current_voltage = self.read_battery_voltage()
        estimated_capacity = self.interpolate_capacity(current_voltage, voltage_points)
        
        self.test_results['battery'] = {
            'voltage': current_voltage,
            'estimated_capacity': estimated_capacity,
            'status': 'OK' if estimated_capacity > 20 else 'LOW'
        }
        
        print(f"  Voltaj: {current_voltage:.2f}V")
        print(f"  Tahmini Kapasite: {estimated_capacity:.1f}%")
        
    def test_charging_system(self):
        """Şarj sistemi testi"""
        print("⚡ Şarj sistemi test ediliyor...")
        
        # MPPT çıkışlarını kontrol et
        mppt_voltage = self.read_mppt_output_voltage()
        mppt_current = self.read_mppt_output_current()
        
        # Beklenen değerler
        expected_voltage = 28.8  # Absorption stage
        tolerance = 0.5
        
        voltage_ok = abs(mppt_voltage - expected_voltage) < tolerance
        current_ok = mppt_current > 0  # En azından bir akım olmalı
        
        self.test_results['charging'] = {
            'mppt_voltage': mppt_voltage,
            'mppt_current': mppt_current,
            'voltage_ok': voltage_ok,
            'current_ok': current_ok,
            'status': 'OK' if voltage_ok and current_ok else 'FAIL'
        }
        
        print(f"  MPPT Voltaj: {mppt_voltage:.2f}V")
        print(f"  MPPT Akım: {mppt_current:.2f}A")
        
    def save_test_results(self):
        """Test sonuçlarını kaydet"""
        timestamp = datetime.now().isoformat()
        
        report = {
            'timestamp': timestamp,
            'test_type': 'weekly_power_test',
            'results': self.test_results
        }
        
        with open(f'/home/pi/oba/logs/power_test_{timestamp[:10]}.json', 'w') as f:
            json.dump(report, f, indent=2)
            
        print("📁 Test sonuçları kaydedildi")

if __name__ == "__main__":
    tester = PowerSystemTest()
    tester.run_full_test()
```

---

**🎯 Hacı Abi Notu:** Güç sistemi robotun kalbi gibi, iyi hesaplama yapmazsan robot yarı yolda kalır! Batarya kapasitesini doğru hesapla, güneş paneli verimi mevsimlik değişir. DC-DC konvertörlerde verimlilik önemli, kayıpları hesaba kat. Röle kontrolünde failsafe kurallarını unutma. Test scriptlerini düzenli çalıştır, enerji bütçesini takip et. Voltaj düşümlerini hesapla, kablo kalınlığını doğru seç! 🤖⚡
