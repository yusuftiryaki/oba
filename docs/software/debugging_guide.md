# 🐛 Hata Ayıklama ve Sorun Giderme

## 🔍 Sistemik Troubleshooting Yaklaşımı

### Tanılama Hiyerarşisi

```
🔍 Sorun Tanılama Sırası:
├── 1️⃣ Güvenlik Sistemleri
├── 2️⃣ Güç ve Elektrik
├── 3️⃣ İletişim ve Network
├── 4️⃣ Sensörler ve Veri
├── 5️⃣ Motorlar ve Hareket
├── 6️⃣ Navigation ve Algoritmalar
└── 7️⃣ Yazılım ve Logic
```

### 🚨 Acil Durum Protokolü

```python
#!/usr/bin/env python3
"""Acil tanılama scripti - İlk müdahale"""

import subprocess
import time
from datetime import datetime

class EmergencyDiagnostics:
    def __init__(self):
        self.timestamp = datetime.now()
        self.critical_issues = []
        self.warnings = []
        
    def run_emergency_check(self):
        """Acil durum tanılama - 30 saniyede temel kontroller"""
        print("🚨 ACİL TANILAMABAŞLIYOR!")
        print("=" * 40)
        
        # 1. Sistem durumu (5 saniye)
        print("1️⃣ Sistem durumu kontrol ediliyor...")
        self.check_system_vitals()
        
        # 2. Güç durumu (5 saniye)
        print("2️⃣ Güç sistemi kontrol ediliyor...")
        self.check_power_systems()
        
        # 3. İletişim (5 saniye)
        print("3️⃣ İletişim sistemleri kontrol ediliyor...")
        self.check_communications()
        
        # 4. Sensörler (5 saniye)
        print("4️⃣ Kritik sensörler kontrol ediliyor...")
        self.check_critical_sensors()
        
        # 5. Emergency stop durumu (5 saniye)
        print("5️⃣ Acil durdurma sistemleri kontrol ediliyor...")
        self.check_emergency_systems()
        
        # 6. Rapor oluştur (5 saniye)
        print("6️⃣ Tanılama raporu hazırlanıyor...")
        self.generate_emergency_report()
        
    def check_system_vitals(self):
        """Sistem vital kontrolleri"""
        try:
            # CPU sıcaklığı
            temp_cmd = "cat /sys/class/thermal/thermal_zone0/temp"
            temp_result = subprocess.run(temp_cmd, shell=True, 
                                       capture_output=True, text=True)
            cpu_temp = int(temp_result.stdout.strip()) / 1000
            
            if cpu_temp > 70:
                self.critical_issues.append(f"⚠️ CPU sıcaklığı kritik: {cpu_temp}°C")
            elif cpu_temp > 60:
                self.warnings.append(f"⚠️ CPU sıcaklığı yüksek: {cpu_temp}°C")
                
            # Memory kullanımı
            mem_cmd = "free -m | grep Mem | awk '{print ($3/$2)*100}'"
            mem_result = subprocess.run(mem_cmd, shell=True,
                                      capture_output=True, text=True)
            mem_usage = float(mem_result.stdout.strip())
            
            if mem_usage > 90:
                self.critical_issues.append(f"⚠️ Bellek kullanımı kritik: {mem_usage}%")
            elif mem_usage > 75:
                self.warnings.append(f"⚠️ Bellek kullanımı yüksek: {mem_usage}%")
                
            # Disk kullanımı
            disk_cmd = "df -h / | awk 'NR==2{print $5}' | sed 's/%//'"
            disk_result = subprocess.run(disk_cmd, shell=True,
                                       capture_output=True, text=True)
            disk_usage = int(disk_result.stdout.strip())
            
            if disk_usage > 95:
                self.critical_issues.append(f"⚠️ Disk dolmuş: {disk_usage}%")
            elif disk_usage > 85:
                self.warnings.append(f"⚠️ Disk doluyor: {disk_usage}%")
                
            print(f"   ✅ CPU: {cpu_temp}°C, RAM: {mem_usage:.1f}%, Disk: {disk_usage}%")
            
        except Exception as e:
            self.critical_issues.append(f"❌ Sistem vitals okunamıyor: {e}")
            
    def check_power_systems(self):
        """Güç sistemi kontrolleri"""
        try:
            # Batarya voltajı (simulated - gerçekte ADC'den okunacak)
            import random
            battery_voltage = 24.5 + random.uniform(-2, 2)
            
            if battery_voltage < 22.0:
                self.critical_issues.append(f"🔋 Batarya voltajı kritik: {battery_voltage:.1f}V")
            elif battery_voltage < 23.0:
                self.warnings.append(f"🔋 Batarya voltajı düşük: {battery_voltage:.1f}V")
                
            # GPIO kontrolleri
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            
            # Motor enable pinlerini kontrol et
            motor_pins = [8, 9, 10]  # Motor enable pinleri
            for pin in motor_pins:
                try:
                    GPIO.setup(pin, GPIO.OUT)
                    GPIO.output(pin, GPIO.LOW)  # Güvenlik için kapat
                    print(f"   ✅ Motor {pin} pin'i erişilebilir")
                except Exception as e:
                    self.critical_issues.append(f"❌ Motor {pin} pin hatası: {e}")
                    
            print(f"   ✅ Batarya: {battery_voltage:.1f}V, Motor pinleri: OK")
            
        except Exception as e:
            self.critical_issues.append(f"❌ Güç sistemi kontrol hatası: {e}")
            
    def check_communications(self):
        """İletişim sistemleri kontrolleri"""
        try:
            # Network bağlantısı
            ping_cmd = "ping -c 1 -W 2 8.8.8.8"
            ping_result = subprocess.run(ping_cmd, shell=True,
                                       capture_output=True, text=True)
            
            if ping_result.returncode == 0:
                print("   ✅ Internet bağlantısı: OK")
            else:
                self.warnings.append("⚠️ Internet bağlantısı yok")
                
            # Local network
            local_ping = "ping -c 1 -W 1 192.168.1.1"
            local_result = subprocess.run(local_ping, shell=True,
                                        capture_output=True, text=True)
            
            if local_result.returncode == 0:
                print("   ✅ Yerel ağ: OK")
            else:
                self.critical_issues.append("❌ Yerel ağ bağlantısı yok")
                
            # WiFi signal strength
            iwconfig_cmd = "iwconfig wlan0 | grep 'Signal level' | awk '{print $4}' | sed 's/level=//'"
            wifi_result = subprocess.run(iwconfig_cmd, shell=True,
                                       capture_output=True, text=True)
            
            if wifi_result.returncode == 0 and wifi_result.stdout.strip():
                signal_level = int(wifi_result.stdout.strip())
                if signal_level < -70:
                    self.warnings.append(f"⚠️ WiFi sinyali zayıf: {signal_level}dBm")
                else:
                    print(f"   ✅ WiFi sinyali: {signal_level}dBm")
                    
        except Exception as e:
            self.critical_issues.append(f"❌ İletişim kontrol hatası: {e}")
            
    def check_critical_sensors(self):
        """Kritik sensör kontrolleri"""
        try:
            # I2C bus taraması
            i2c_cmd = "i2cdetect -y 1"
            i2c_result = subprocess.run(i2c_cmd, shell=True,
                                      capture_output=True, text=True)
            
            if "28" in i2c_result.stdout or "29" in i2c_result.stdout:
                print("   ✅ IMU sensörü (BNO055) algılandı")
            else:
                self.critical_issues.append("❌ IMU sensörü bulunamadı")
                
            # Enkoder pinleri kontrol
            encoder_pins = [18, 19, 20, 21]
            GPIO.setmode(GPIO.BCM)
            
            for pin in encoder_pins:
                try:
                    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                    state = GPIO.input(pin)
                    print(f"   ✅ Enkoder pin {pin}: {state}")
                except Exception as e:
                    self.critical_issues.append(f"❌ Enkoder pin {pin} hatası: {e}")
                    
            # Kamera kontrolü
            camera_cmd = "vcgencmd get_camera"
            camera_result = subprocess.run(camera_cmd, shell=True,
                                         capture_output=True, text=True)
            
            if "detected=1" in camera_result.stdout:
                print("   ✅ Kamera algılandı")
            else:
                self.warnings.append("⚠️ Kamera algılanmadı")
                
        except Exception as e:
            self.critical_issues.append(f"❌ Sensör kontrol hatası: {e}")
            
    def check_emergency_systems(self):
        """Acil durdurma sistemleri"""
        try:
            # Emergency stop pin kontrolü
            emergency_pin = 27  # Örnek pin
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(emergency_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
            emergency_state = GPIO.input(emergency_pin)
            
            if emergency_state == 0:  # Active low
                self.critical_issues.append("🚨 ACİL DURDURMA AKTİF!")
            else:
                print("   ✅ Acil durdurma sistemi: Normal")
                
            # Tilt sensor kontrolü (varsa)
            tilt_pin = 23
            GPIO.setup(tilt_pin, GPIO.IN)
            tilt_state = GPIO.input(tilt_pin)
            
            if tilt_state == 1:  # Robot devrilmiş
                self.critical_issues.append("⚠️ Robot devrilme algılandı!")
            else:
                print("   ✅ Tilt sensor: Normal")
                
        except Exception as e:
            self.critical_issues.append(f"❌ Acil durum sistemi hatası: {e}")
            
    def generate_emergency_report(self):
        """Acil tanılama raporu"""
        print("\n" + "=" * 50)
        print("📋 ACİL TANILAMARAPORU")
        print("=" * 50)
        
        # Kritik sorunlar
        if self.critical_issues:
            print("\n🚨 KRİTİK SORUNLAR:")
            for issue in self.critical_issues:
                print(f"  {issue}")
        else:
            print("\n✅ Kritik sorun yok")
            
        # Uyarılar
        if self.warnings:
            print("\n⚠️ UYARILAR:")
            for warning in self.warnings:
                print(f"  {warning}")
        else:
            print("\n✅ Uyarı yok")
            
        # Tavsiyeler
        print("\n💡 TAVSİYELER:")
        
        if len(self.critical_issues) > 0:
            print("  🔴 Robotu ÇALIŞTIRMAYINIZ!")
            print("  🔧 Kritik sorunları çözün")
            print("  📞 Teknik destek ile iletişime geçin")
        elif len(self.warnings) > 0:
            print("  🟡 Dikkatli çalıştırın")
            print("  🔧 Uyarıları değerlendirin")
            print("  📊 Performansı izleyin")
        else:
            print("  🟢 Robot çalışmaya hazır")
            print("  🚀 Normal operasyona başlayabilirsiniz")
            
        # Rapor dosyasına kaydet
        report_file = f"/home/pi/oba/logs/emergency_diag_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.log"
        
        try:
            with open(report_file, 'w') as f:
                f.write(f"Emergency Diagnostics Report\n")
                f.write(f"Timestamp: {self.timestamp}\n")
                f.write(f"Critical Issues: {len(self.critical_issues)}\n")
                f.write(f"Warnings: {len(self.warnings)}\n\n")
                
                f.write("CRITICAL ISSUES:\n")
                for issue in self.critical_issues:
                    f.write(f"{issue}\n")
                    
                f.write("\nWARNINGS:\n")
                for warning in self.warnings:
                    f.write(f"{warning}\n")
                    
            print(f"\n📁 Rapor kaydedildi: {report_file}")
            
        except Exception as e:
            print(f"❌ Rapor kayıt hatası: {e}")

# Ana fonksiyon
def main():
    try:
        diagnostics = EmergencyDiagnostics()
        diagnostics.run_emergency_check()
        
    except KeyboardInterrupt:
        print("\n🛑 Tanılama kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"❌ Kritik hata: {e}")
        print("📞 Acil teknik destek gerekli!")

if __name__ == "__main__":
    main()
```

## 🔧 Sistemik Troubleshooting

### Robot Hareket Etmiyor

#### Tanılama Adımları

```python
#!/usr/bin/env python3
"""Robot hareket problemi tanılama"""

def diagnose_movement_issue():
    """Hareket problemi tanılama"""
    print("🚗 Robot Hareket Problemi Tanılama")
    print("=" * 35)
    
    # 1. Motor güç kontrolü
    print("1️⃣ Motor güç sistemi kontrol ediliyor...")
    
    # Motor röle kontrolü
    relay_pins = [8, 9, 10]  # Motor enable röleleri
    for i, pin in enumerate(relay_pins):
        print(f"   Motor {i+1} rölesi (GPIO {pin}) test ediliyor...")
        
        # Röle test
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(0.5)
        
        # Voltaj ölçümü (simulated)
        voltage = measure_motor_voltage(i+1)
        
        if voltage < 20:
            print(f"   ❌ Motor {i+1} voltajı düşük: {voltage}V")
        else:
            print(f"   ✅ Motor {i+1} voltajı normal: {voltage}V")
            
        GPIO.output(pin, GPIO.LOW)
        
    # 2. Motor sürücü kartları
    print("\n2️⃣ Motor sürücü kartları kontrol ediliyor...")
    
    # PWM sinyal kontrolü
    pwm_pins = [12, 16, 6]  # PWM pinleri
    for i, pin in enumerate(pwm_pins):
        print(f"   Motor {i+1} PWM (GPIO {pin}) test ediliyor...")
        
        # PWM test
        pwm = GPIO.PWM(pin, 1000)  # 1kHz test frekansı
        pwm.start(50)  # %50 duty cycle
        time.sleep(1)
        
        # PWM sinyali ölçümü (oscilloscope gerekli)
        pwm_ok = test_pwm_signal(pin)
        
        if pwm_ok:
            print(f"   ✅ Motor {i+1} PWM sinyali OK")
        else:
            print(f"   ❌ Motor {i+1} PWM sinyali bozuk")
            
        pwm.stop()
        
    # 3. Motor mekanik kontrol
    print("\n3️⃣ Motor mekanik sistem kontrol ediliyor...")
    
    # Manuel motor test
    for i in range(3):
        motor_name = ["Sol Palet", "Sağ Palet", "Biçme"][i]
        print(f"   {motor_name} motoru test ediliyor...")
        
        # Motor kısa süreli çalıştır
        run_motor_test(i+1, duration=2)
        
        # Enkoder feedback (palet motorları için)
        if i < 2:
            encoder_count = read_encoder_during_test(i+1)
            if encoder_count > 0:
                print(f"   ✅ {motor_name} enkoder feedback OK: {encoder_count} pulse")
            else:
                print(f"   ❌ {motor_name} enkoder feedback yok")
        
        # Akım ölçümü
        current = measure_motor_current(i+1)
        print(f"   Motor akımı: {current:.1f}A")
        
        if current < 0.5:
            print(f"   ⚠️ {motor_name} motor yük almıyor (açık devre?)")
        elif current > 15:
            print(f"   ⚠️ {motor_name} motor aşırı akım çekiyor (sıkışma?)")
        else:
            print(f"   ✅ {motor_name} motor akımı normal")

def measure_motor_voltage(motor_id):
    """Motor voltajını ölç (simulated)"""
    import random
    return 24.0 + random.uniform(-2, 2)

def test_pwm_signal(pin):
    """PWM sinyal kalitesini test et"""
    # Gerçek uygulamada oscilloscope veya logic analyzer gerekli
    # Burada simulated
    import random
    return random.choice([True, True, True, False])  # %75 başarı

def run_motor_test(motor_id, duration=2):
    """Motor kısa süreli test çalıştırması"""
    print(f"     Motor {motor_id} {duration}s test çalıştırması...")
    
    # Motor çalıştır
    if motor_id == 1:  # Sol palet
        GPIO.output(8, GPIO.HIGH)   # Röle
        pwm = GPIO.PWM(12, 20000)   # PWM
        pwm.start(30)               # %30 hız
    elif motor_id == 2:  # Sağ palet
        GPIO.output(9, GPIO.HIGH)
        pwm = GPIO.PWM(16, 20000)
        pwm.start(30)
    elif motor_id == 3:  # Biçme
        GPIO.output(10, GPIO.HIGH)
        pwm = GPIO.PWM(6, 20000)
        pwm.start(50)
        
    time.sleep(duration)
    
    # Motor durdur
    pwm.stop()
    GPIO.output([8, 9, 10], GPIO.LOW)
    
    print(f"     Motor {motor_id} test tamamlandı")

def read_encoder_during_test(motor_id):
    """Test sırasında enkoder okuma"""
    # Encoder pin'leri
    encoder_pins = {1: [18, 19], 2: [20, 21]}
    
    if motor_id not in encoder_pins:
        return 0
        
    pin_a, pin_b = encoder_pins[motor_id]
    
    # Enkoder okuma setup
    GPIO.setup([pin_a, pin_b], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    # 2 saniye boyunca pulse say
    pulse_count = 0
    start_time = time.time()
    last_a_state = GPIO.input(pin_a)
    
    while time.time() - start_time < 2:
        a_state = GPIO.input(pin_a)
        if a_state != last_a_state:
            pulse_count += 1
            last_a_state = a_state
        time.sleep(0.001)
        
    return pulse_count

def measure_motor_current(motor_id):
    """Motor akımını ölç (simulated)"""
    import random
    # Normal çalışma akımları
    base_currents = [8, 8, 12]  # Sol, Sağ, Biçme
    base = base_currents[motor_id - 1]
    return base + random.uniform(-2, 3)
```

### Navigasyon Problemi

#### GPS'siz Konum Kaybı

```python
def diagnose_localization_issue():
    """Konum belirleme problemi tanılama"""
    print("🧭 Navigasyon Sistemi Tanılama")
    print("=" * 30)
    
    # 1. IMU sensörü kontrol
    print("1️⃣ IMU sensörü kontrol ediliyor...")
    
    try:
        import adafruit_bno055
        import board
        import busio
        
        i2c = busio.I2C(board.SCL, board.SDA)
        bno = adafruit_bno055.BNO055_I2C(i2c)
        
        # Kalibrasyon durumu
        cal_status = bno.calibration_status
        sys_cal, gyro_cal, accel_cal, mag_cal = cal_status
        
        print(f"   IMU Kalibrasyon Durumu:")
        print(f"   System: {sys_cal}/3, Gyro: {gyro_cal}/3")
        print(f"   Accel: {accel_cal}/3, Mag: {mag_cal}/3")
        
        if sys_cal < 2:
            print("   ⚠️ IMU kalibrasyonu düşük - recalibration gerekli")
        else:
            print("   ✅ IMU kalibrasyonu yeterli")
            
        # Sensör verileri test
        acceleration = bno.acceleration
        gyro = bno.gyro
        magnetometer = bno.magnetic
        
        print(f"   Accelerometer: {acceleration}")
        print(f"   Gyroscope: {gyro}")
        print(f"   Magnetometer: {magnetometer}")
        
        # Veri kalitesi kontrol
        if acceleration and all(val is not None for val in acceleration):
            print("   ✅ Accelerometer veri kalitesi OK")
        else:
            print("   ❌ Accelerometer veri hatası")
            
    except Exception as e:
        print(f"   ❌ IMU sensör hatası: {e}")
        
    # 2. Enkoder hassasiyeti
    print("\n2️⃣ Enkoder hassasiyeti kontrol ediliyor...")
    
    # Enkoder test - robot 1 metre hareket ettir
    print("   1 metre test hareketi başlatılıyor...")
    
    # Başlangıç enkoder değerleri
    left_start = read_encoder_value('left')
    right_start = read_encoder_value('right')
    
    # Robot 1 metre ileri hareket ettir
    move_robot_distance(1.0)  # 1 metre
    
    # Son enkoder değerleri
    left_end = read_encoder_value('left')
    right_end = read_encoder_value('right')
    
    # Pulse farkları
    left_pulses = abs(left_end - left_start)
    right_pulses = abs(right_end - right_start)
    
    # Beklenen pulse sayısı (600 pulse/tur, tekerlek çapı 0.2m)
    wheel_circumference = 0.2 * 3.14159
    expected_pulses = (1.0 / wheel_circumference) * 600
    
    print(f"   Sol enkoder: {left_pulses} pulse (beklenen: {expected_pulses:.0f})")
    print(f"   Sağ enkoder: {right_pulses} pulse (beklenen: {expected_pulses:.0f})")
    
    # Hata hesaplama
    left_error = abs(left_pulses - expected_pulses) / expected_pulses * 100
    right_error = abs(right_pulses - expected_pulses) / expected_pulses * 100
    
    if left_error > 10:
        print(f"   ⚠️ Sol enkoder hatası yüksek: {left_error:.1f}%")
    else:
        print(f"   ✅ Sol enkoder hassasiyeti OK: {left_error:.1f}%")
        
    if right_error > 10:
        print(f"   ⚠️ Sağ enkoder hatası yüksek: {right_error:.1f}%")
    else:
        print(f"   ✅ Sağ enkoder hassasiyeti OK: {right_error:.1f}%")
        
    # 3. Kalman filtre parametreleri
    print("\n3️⃣ Kalman filtre parametreleri kontrol ediliyor...")
    
    # Pozisyon drift testi - 10 saniye statik bekle
    print("   10 saniye pozisyon drift testi...")
    
    initial_position = get_current_position()
    time.sleep(10)
    final_position = get_current_position()
    
    drift_distance = calculate_distance(initial_position, final_position)
    
    if drift_distance > 0.1:  # 10cm üstü drift
        print(f"   ⚠️ Pozisyon drift problemi: {drift_distance:.2f}m")
        print("   Kalman filtre Q/R parametrelerini kontrol edin")
    else:
        print(f"   ✅ Pozisyon drift normal: {drift_distance:.2f}m")

def read_encoder_value(side):
    """Enkoder değerini oku"""
    # Bu fonksiyon gerçek enkoder okuma implementasyonu
    # Interrupt based encoder reading
    import random
    return random.randint(1000, 5000)

def move_robot_distance(distance):
    """Robotu belirli mesafe hareket ettir"""
    print(f"   Robot {distance}m hareket ettiriliyor...")
    
    # Motor kontrolü ile robot hareket ettir
    # Bu örnekte simulated
    time.sleep(3)  # 3 saniye hareket sim
    
    print("   ✅ Hareket tamamlandı")

def get_current_position():
    """Mevcut robot pozisyonunu al"""
    # Kalman filtre çıkışından pozisyon
    import random
    return (random.uniform(0, 10), random.uniform(0, 10))

def calculate_distance(pos1, pos2):
    """İki pozisyon arası mesafe"""
    import math
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
```

### Web Arayüzü Erişim Problemi

```python
def diagnose_web_interface_issue():
    """Web arayüzü erişim problemi tanılama"""
    print("🌐 Web Arayüzü Tanılama")
    print("=" * 23)
    
    # 1. Flask server durumu
    print("1️⃣ Flask server durumu kontrol ediliyor...")
    
    # Process kontrolü
    flask_cmd = "ps aux | grep flask | grep -v grep"
    flask_result = subprocess.run(flask_cmd, shell=True,
                                capture_output=True, text=True)
    
    if flask_result.stdout:
        print("   ✅ Flask server çalışıyor")
        print(f"   Process: {flask_result.stdout.strip()}")
    else:
        print("   ❌ Flask server çalışmıyor")
        print("   Server'ı başlatmayı deneyin: python3 web_server.py")
        
    # 2. Port durumu
    print("\n2️⃣ Port durumu kontrol ediliyor...")
    
    # Port 5000 kontrolü
    netstat_cmd = "netstat -tuln | grep :5000"
    port_result = subprocess.run(netstat_cmd, shell=True,
                               capture_output=True, text=True)
    
    if port_result.stdout:
        print("   ✅ Port 5000 dinleniyor")
        print(f"   {port_result.stdout.strip()}")
    else:
        print("   ❌ Port 5000 kullanımda değil")
        
    # 3. Firewall kontrolü
    print("\n3️⃣ Firewall durumu kontrol ediliyor...")
    
    # UFW durumu
    ufw_cmd = "ufw status"
    ufw_result = subprocess.run(ufw_cmd, shell=True,
                              capture_output=True, text=True)
    
    if "Status: active" in ufw_result.stdout:
        print("   ⚠️ UFW firewall aktif")
        if ":5000" in ufw_result.stdout:
            print("   ✅ Port 5000 firewall'da açık")
        else:
            print("   ❌ Port 5000 firewall'da kapalı")
            print("   Çözüm: sudo ufw allow 5000")
    else:
        print("   ✅ UFW firewall pasif")
        
    # 4. Network bağlantısı
    print("\n4️⃣ Network bağlantısı kontrol ediliyor...")
    
    # IP adresi
    ip_cmd = "hostname -I"
    ip_result = subprocess.run(ip_cmd, shell=True,
                             capture_output=True, text=True)
    
    if ip_result.stdout:
        ip_address = ip_result.stdout.strip().split()[0]
        print(f"   Robot IP adresi: {ip_address}")
        
        # Local erişim testi
        curl_cmd = f"curl -s -o /dev/null -w '%{{http_code}}' http://{ip_address}:5000"
        curl_result = subprocess.run(curl_cmd, shell=True,
                                   capture_output=True, text=True)
        
        if curl_result.stdout == "200":
            print("   ✅ Web arayüzü erişilebilir")
            print(f"   URL: http://{ip_address}:5000")
        else:
            print(f"   ❌ Web arayüzü erişim hatası: HTTP {curl_result.stdout}")
    else:
        print("   ❌ IP adresi alınamıyor")
        
    # 5. Log kontrolleri
    print("\n5️⃣ Web server logları kontrol ediliyor...")
    
    # Flask log dosyası
    log_file = "/home/pi/oba/logs/web_server.log"
    
    try:
        tail_cmd = f"tail -n 10 {log_file}"
        log_result = subprocess.run(tail_cmd, shell=True,
                                  capture_output=True, text=True)
        
        if log_result.stdout:
            print("   Son 10 log satırı:")
            for line in log_result.stdout.strip().split('\n'):
                print(f"     {line}")
        else:
            print("   ⚠️ Log dosyası boş veya bulunamadı")
            
    except Exception as e:
        print(f"   ❌ Log okuma hatası: {e}")
```

## 📊 Performance Profiling

### Sistem Performans Ölçümü

```python
#!/usr/bin/env python3
"""Sistem performans profiling aracı"""

import psutil
import time
import threading
import json
from datetime import datetime

class PerformanceProfiler:
    def __init__(self, duration=60):
        self.duration = duration
        self.data = {
            'cpu_usage': [],
            'memory_usage': [],
            'disk_io': [],
            'network_io': [],
            'temperature': [],
            'timestamps': []
        }
        self.running = False
        
    def start_profiling(self):
        """Profiling başlat"""
        print(f"📊 {self.duration}s sistem performans ölçümü başlıyor...")
        
        self.running = True
        start_time = time.time()
        
        while self.running and (time.time() - start_time) < self.duration:
            timestamp = datetime.now()
            
            # CPU kullanımı
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory kullanımı
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            
            # Network I/O
            network_io = psutil.net_io_counters()
            
            # CPU sıcaklığı
            try:
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    temp = int(f.read()) / 1000
            except:
                temp = 0
                
            # Verileri kaydet
            self.data['timestamps'].append(timestamp.isoformat())
            self.data['cpu_usage'].append(cpu_percent)
            self.data['memory_usage'].append(memory_percent)
            self.data['disk_io'].append({
                'read_bytes': disk_io.read_bytes if disk_io else 0,
                'write_bytes': disk_io.write_bytes if disk_io else 0
            })
            self.data['network_io'].append({
                'bytes_sent': network_io.bytes_sent if network_io else 0,
                'bytes_recv': network_io.bytes_recv if network_io else 0
            })
            self.data['temperature'].append(temp)
            
            time.sleep(1)  # 1 saniye interval
            
        self.generate_report()
        
    def generate_report(self):
        """Performans raporu oluştur"""
        print("\n📋 PERFORMANS RAPORU")
        print("=" * 30)
        
        # CPU istatistikleri
        cpu_avg = sum(self.data['cpu_usage']) / len(self.data['cpu_usage'])
        cpu_max = max(self.data['cpu_usage'])
        
        print(f"🖥️  CPU Kullanımı:")
        print(f"   Ortalama: {cpu_avg:.1f}%")
        print(f"   Maksimum: {cpu_max:.1f}%")
        
        if cpu_avg > 80:
            print("   ⚠️ Yüksek CPU kullanımı!")
        else:
            print("   ✅ CPU kullanımı normal")
            
        # Memory istatistikleri
        mem_avg = sum(self.data['memory_usage']) / len(self.data['memory_usage'])
        mem_max = max(self.data['memory_usage'])
        
        print(f"\n💾 Bellek Kullanımı:")
        print(f"   Ortalama: {mem_avg:.1f}%")
        print(f"   Maksimum: {mem_max:.1f}%")
        
        if mem_avg > 85:
            print("   ⚠️ Yüksek bellek kullanımı!")
        else:
            print("   ✅ Bellek kullanımı normal")
            
        # Sıcaklık istatistikleri
        temp_avg = sum(self.data['temperature']) / len(self.data['temperature'])
        temp_max = max(self.data['temperature'])
        
        print(f"\n🌡️  Sıcaklık:")
        print(f"   Ortalama: {temp_avg:.1f}°C")
        print(f"   Maksimum: {temp_max:.1f}°C")
        
        if temp_max > 70:
            print("   ⚠️ Yüksek sıcaklık! Soğutma kontrol edin")
        elif temp_max > 60:
            print("   ⚠️ Sıcaklık yükseliyor")
        else:
            print("   ✅ Sıcaklık normal")
            
        # Raporu dosyaya kaydet
        report_file = f"/home/pi/oba/logs/performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w') as f:
                json.dump(self.data, f, indent=2)
            print(f"\n📁 Detaylı rapor kaydedildi: {report_file}")
        except Exception as e:
            print(f"❌ Rapor kayıt hatası: {e}")
            
    def stop_profiling(self):
        """Profiling durdur"""
        self.running = False

# Ana profiling fonksiyonu
def main():
    """Ana profiling uygulaması"""
    duration = 60  # saniye
    
    try:
        profiler = PerformanceProfiler(duration)
        profiler.start_profiling()
        
    except KeyboardInterrupt:
        print("\n🛑 Profiling kullanıcı tarafından durduruldu")
        if 'profiler' in locals():
            profiler.stop_profiling()
            
if __name__ == "__main__":
    main()
```

---

**🎯 Hacı Abi Notu:** Debugging robotun doktor muayenesi gibi, sistemli yaklaş yoksa yanlış teşhis koyarsın! Acil tanılama scriptini her zaman hazır tut, kritik durumlarda hayat kurtarır. Log dosyalarını takip et, sessiz hatalar çok tehlikeli. Performance profiling yap, darboğazları önceden yakala. Test scriptlerini otomatize et, manuel kontroller unutulur. Multimeter kullanmayı bil, yazılım her şeyi çözemez! 🤖🔧
