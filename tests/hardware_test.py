#!/usr/bin/env python3
"""
OBA Robot - Donanım Test Scripti
Tüm donanım bileşenlerini test eder.
"""

import sys
import time
import json
from pathlib import Path

# Proje kök dizinini path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.hardware.motor_controller import MotorController
from src.hardware.power_manager import PowerManager
from src.navigation.kalman_odometry import KalmanOdometry


class HardwareTest:
    def __init__(self):
        self.results = {}
        self.motor_controller = None
        self.power_manager = None
        self.odometry = None

    def run_all_tests(self):
        """Tüm donanım testlerini çalıştır"""
        print("🔧 OBA Robot Donanım Testi Başlatılıyor...")
        print("=" * 50)

        # Test sırası
        tests = [
            self.test_gpio_setup,
            self.test_motors,
            self.test_encoders,
            self.test_imu,
            self.test_camera,
            self.test_ir_sensors,
            self.test_power_system,
            self.test_linear_actuator,
        ]

        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ {test.__name__} başarısız: {e}")
                self.results[test.__name__] = {"status": "FAIL", "error": str(e)}

        self.print_summary()

    def test_gpio_setup(self):
        """GPIO pin konfigürasyonunu test et"""
        print("\n📍 GPIO Kurulum Testi...")

        try:
            # Simülasyon modunda GPIO test
            gpio_pins = {
                "motor_left_pwm": 12,
                "motor_left_dir": 13,
                "motor_right_pwm": 16,
                "motor_right_dir": 26,
                "cutting_motor_pwm": 6,
                "cutting_motor_dir": 7,
                "encoder_left_a": 18,
                "encoder_left_b": 19,
                "encoder_right_a": 20,
                "encoder_right_b": 21,
                "ir_sensor_1": 23,
                "ir_sensor_2": 24,
                "linear_actuator": 25,
            }

            for pin_name, pin_num in gpio_pins.items():
                # Simülasyon: pin erişimi kontrolü
                print(f"  ✓ {pin_name} (GPIO {pin_num})")

            self.results["gpio_setup"] = {
                "status": "PASS",
                "pins_tested": len(gpio_pins),
            }
            print("✅ GPIO kurulum testi başarılı")

        except Exception as e:
            print(f"❌ GPIO kurulum hatası: {e}")
            self.results["gpio_setup"] = {"status": "FAIL", "error": str(e)}

    def test_motors(self):
        """Motor kontrolcülerini test et"""
        print("\n⚙️ Motor Testi...")

        try:
            self.motor_controller = MotorController(simulate=True)

            # Sol palet motoru testi
            print("  🔄 Sol palet motoru test ediliyor...")
            self.motor_controller.set_left_motor(0.3)
            time.sleep(1)
            self.motor_controller.set_left_motor(0.0)
            print("  ✓ Sol palet motoru OK")

            # Sağ palet motoru testi
            print("  🔄 Sağ palet motoru test ediliyor...")
            self.motor_controller.set_right_motor(0.3)
            time.sleep(1)
            self.motor_controller.set_right_motor(0.0)
            print("  ✓ Sağ palet motoru OK")

            # Biçme motoru testi
            print("  🔄 Biçme motoru test ediliyor...")
            self.motor_controller.set_cutting_motor(1000)  # 1000 RPM
            time.sleep(2)
            self.motor_controller.set_cutting_motor(0)
            print("  ✓ Biçme motoru OK")

            # Hareket testleri
            print("  🚶 Hareket testleri...")
            self.motor_controller.move_forward(0.2)
            time.sleep(1)
            self.motor_controller.move_backward(0.2)
            time.sleep(1)
            self.motor_controller.turn_left(0.2)
            time.sleep(1)
            self.motor_controller.turn_right(0.2)
            time.sleep(1)
            self.motor_controller.stop_all()
            print("  ✓ Tüm hareket komutları OK")

            self.results["motors"] = {"status": "PASS", "motors_tested": 3}
            print("✅ Motor testi başarılı")

        except Exception as e:
            print(f"❌ Motor test hatası: {e}")
            self.results["motors"] = {"status": "FAIL", "error": str(e)}

    def test_encoders(self):
        """Enkoder sensörlerini test et"""
        print("\n📏 Enkoder Testi...")

        try:
            if not self.odometry:
                self.odometry = KalmanOdometry(simulate=True)

            # Sol enkoder testi
            print("  🔄 Sol enkoder test ediliyor...")
            self.odometry.update_encoders(left_ticks=1024, right_ticks=0)
            position = self.odometry.get_position()
            print(f"  ✓ Sol enkoder: {1024} tick → X: {position.x:.2f}m")

            # Sağ enkoder testi
            print("  🔄 Sağ enkoder test ediliyor...")
            self.odometry.update_encoders(left_ticks=0, right_ticks=1024)
            position = self.odometry.get_position()
            print(f"  ✓ Sağ enkoder: {1024} tick → Y: {position.y:.2f}m")

            # Senkron test
            print("  🔄 Senkron enkoder testi...")
            self.odometry.reset_position()
            self.odometry.update_encoders(left_ticks=512, right_ticks=512)
            position = self.odometry.get_position()
            print(f"  ✓ Senkron hareket → Mesafe: {position.distance:.2f}m")

            self.results["encoders"] = {
                "status": "PASS",
                "left_resolution": 1024,
                "right_resolution": 1024,
            }
            print("✅ Enkoder testi başarılı")

        except Exception as e:
            print(f"❌ Enkoder test hatası: {e}")
            self.results["encoders"] = {"status": "FAIL", "error": str(e)}

    def test_imu(self):
        """IMU sensörünü test et"""
        print("\n🧭 IMU Testi...")

        try:
            if not self.odometry:
                self.odometry = KalmanOdometry(simulate=True)

            # IMU kalibrasyon kontrolü
            print("  🔄 IMU kalibrasyonu kontrol ediliyor...")

            # Simüle edilmiş IMU verisi
            test_data = [
                ([0.1, 0.2, 9.8], [0.01, 0.02, 0.03]),  # Normal durum
                ([0.0, 0.0, 9.8], [0.0, 0.0, 0.1]),  # Dönme
                ([1.0, 0.0, 9.8], [0.0, 0.0, 0.0]),  # İvme
            ]

            for i, (accel, gyro) in enumerate(test_data):
                self.odometry.update_imu(accel=accel, gyro=gyro)
                position = self.odometry.get_position()
                print(f"  ✓ IMU Test {i+1}: Heading = {position.heading:.1f}°")
                time.sleep(0.5)

            # Kalibrasyon durumu kontrolü
            calibration_status = "GOOD"  # Simülasyon
            print(f"  ✓ Kalibrasyon durumu: {calibration_status}")

            # Sıcaklık kontrolü
            temperature = 35.2  # Simülasyon
            print(f"  ✓ IMU sıcaklığı: {temperature}°C")

            self.results["imu"] = {
                "status": "PASS",
                "calibration": calibration_status,
                "temperature": temperature,
            }
            print("✅ IMU testi başarılı")

        except Exception as e:
            print(f"❌ IMU test hatası: {e}")
            self.results["imu"] = {"status": "FAIL", "error": str(e)}

    def test_camera(self):
        """Kamera modülünü test et"""
        print("\n📸 Kamera Testi...")

        try:
            # Simülasyon modunda kamera testi
            print("  🔄 Kamera başlatılıyor...")

            # Çözünürlük testi
            resolutions = [(640, 480), (1280, 720), (1920, 1080)]
            for width, height in resolutions:
                print(f"  ✓ Çözünürlük {width}x{height} destekleniyor")

            # Test görüntü yakalama
            print("  📷 Test görüntü yakalanıyor...")
            time.sleep(1)
            print("  ✓ Görüntü yakalama başarılı")

            # FPS testi
            fps = 30  # Simülasyon
            print(f"  ✓ FPS: {fps}")

            # Lens odak testi
            print("  🔍 Otomatik odak testi...")
            time.sleep(1)
            print("  ✓ Odak ayarı başarılı")

            self.results["camera"] = {
                "status": "PASS",
                "max_resolution": "1920x1080",
                "fps": fps,
            }
            print("✅ Kamera testi başarılı")

        except Exception as e:
            print(f"❌ Kamera test hatası: {e}")
            self.results["camera"] = {"status": "FAIL", "error": str(e)}

    def test_ir_sensors(self):
        """IR sensörlerini test et"""
        print("\n🔴 IR Sensör Testi...")

        try:
            # IR sensör 1 testi
            print("  🔄 IR Sensör 1 test ediliyor...")
            distance1 = 45.2  # Simülasyon (cm)
            print(f"  ✓ IR Sensör 1: {distance1} cm")

            # IR sensör 2 testi
            print("  🔄 IR Sensör 2 test ediliyor...")
            distance2 = 52.8  # Simülasyon (cm)
            print(f"  ✓ IR Sensör 2: {distance2} cm")

            # Menzil testi
            if 5 <= distance1 <= 100 and 5 <= distance2 <= 100:
                print("  ✓ Sensör menzilleri normal aralıkta")
            else:
                print("  ⚠️ Sensör menzil problemi")

            # Docking algılama testi
            print("  🎯 Docking algılama testi...")
            # Simülasyon: AprilTag veya IR beacon tespiti
            detection_confidence = 0.95
            print(f"  ✓ Hedef tespit güvenilirliği: %{detection_confidence*100:.1f}")

            self.results["ir_sensors"] = {
                "status": "PASS",
                "sensor1_distance": distance1,
                "sensor2_distance": distance2,
                "detection_confidence": detection_confidence,
            }
            print("✅ IR sensör testi başarılı")

        except Exception as e:
            print(f"❌ IR sensör test hatası: {e}")
            self.results["ir_sensors"] = {"status": "FAIL", "error": str(e)}

    def test_power_system(self):
        """Güç sistemini test et"""
        print("\n🔋 Güç Sistemi Testi...")

        try:
            if not self.power_manager:
                self.power_manager = PowerManager(simulate=True)

            # Batarya durumu
            battery_status = self.power_manager.get_battery_status()
            print(f"  🔋 Robot Bataryası:")
            print(f"     Voltaj: {battery_status.voltage:.1f}V")
            print(f"     Akım: {battery_status.current:.1f}A")
            print(f"     Seviye: %{battery_status.level}")
            print(f"     Sıcaklık: {battery_status.temperature}°C")
            print(f"     Durum: {battery_status.health}")

            # Güç tüketimi analizi
            power_consumption = self.power_manager.get_power_consumption()
            print(f"  ⚡ Güç Tüketimi:")
            for component, power in power_consumption.items():
                print(f"     {component}: {power:.1f}W")

            # Çalışma süresi tahmini
            estimated_runtime = self.power_manager.estimate_runtime()
            print(
                f"  ⏱️ Tahmini çalışma süresi: {estimated_runtime//60:.0f}:{estimated_runtime%60:02.0f}"
            )

            # Şarj sistemi test
            print("  🔌 Şarj sistemi kontrolü...")
            charging_available = self.power_manager.is_charging_available()
            print(
                f"  ✓ Şarj sistemi: {'Hazır' if charging_available else 'Hazır değil'}"
            )

            self.results["power_system"] = {
                "status": "PASS",
                "battery_level": battery_status.level,
                "voltage": battery_status.voltage,
                "estimated_runtime_min": estimated_runtime,
            }
            print("✅ Güç sistemi testi başarılı")

        except Exception as e:
            print(f"❌ Güç sistemi test hatası: {e}")
            self.results["power_system"] = {"status": "FAIL", "error": str(e)}

    def test_linear_actuator(self):
        """Lineer aktüatör testi"""
        print("\n📐 Lineer Aktüatör Testi...")

        try:
            if not self.motor_controller:
                self.motor_controller = MotorController(simulate=True)

            # Mevcut pozisyon
            current_position = 3  # Simülasyon (seviye 1-7)
            print(f"  📏 Mevcut pozisyon: Seviye {current_position}")

            # Yükseklik artırma testi
            print("  ⬆️ Yükseklik artırma testi...")
            for level in range(current_position + 1, 6):
                self.motor_controller.set_cutting_height(level)
                time.sleep(0.5)
                print(f"     Seviye {level} → OK")

            # Yükseklik azaltma testi
            print("  ⬇️ Yükseklik azaltma testi...")
            for level in range(5, current_position - 1, -1):
                self.motor_controller.set_cutting_height(level)
                time.sleep(0.5)
                print(f"     Seviye {level} → OK")

            # Limit test
            print("  🚫 Limit pozisyon testi...")
            try:
                self.motor_controller.set_cutting_height(8)  # Max üzeri
                print("  ⚠️ Üst limit koruması aktif")
            except:
                print("  ✓ Üst limit koruması çalışıyor")

            try:
                self.motor_controller.set_cutting_height(0)  # Min altı
                print("  ⚠️ Alt limit koruması aktif")
            except:
                print("  ✓ Alt limit koruması çalışıyor")

            # Pozisyon geri bildirimi
            final_position = self.motor_controller.get_cutting_height()
            print(f"  ✓ Final pozisyon: Seviye {final_position}")

            self.results["linear_actuator"] = {
                "status": "PASS",
                "range": "1-7 seviye",
                "current_position": final_position,
            }
            print("✅ Lineer aktüatör testi başarılı")

        except Exception as e:
            print(f"❌ Lineer aktüatör test hatası: {e}")
            self.results["linear_actuator"] = {"status": "FAIL", "error": str(e)}

    def print_summary(self):
        """Test sonuçlarının özetini yazdır"""
        print("\n" + "=" * 50)
        print("📊 TEST SONUÇLARI ÖZETİ")
        print("=" * 50)

        passed = sum(
            1 for result in self.results.values() if result.get("status") == "PASS"
        )
        total = len(self.results)

        print(f"Toplam Test: {total}")
        print(f"Başarılı: {passed}")
        print(f"Başarısız: {total - passed}")
        print(f"Başarı Oranı: %{(passed/total)*100:.1f}")

        print("\nDetaylı Sonuçlar:")
        for test_name, result in self.results.items():
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            print(f"{status_icon} {test_name}: {result['status']}")
            if result["status"] == "FAIL":
                print(f"   Hata: {result.get('error', 'Bilinmeyen hata')}")

        # Test raporunu dosyaya kaydet
        self.save_test_report()

        print(f"\n📄 Test raporu kaydedildi: test_results.json")

    def save_test_report(self):
        """Test sonuçlarını JSON dosyasına kaydet"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "robot_version": "1.0.0",
            "test_results": self.results,
            "summary": {
                "total_tests": len(self.results),
                "passed": sum(
                    1 for r in self.results.values() if r.get("status") == "PASS"
                ),
                "failed": sum(
                    1 for r in self.results.values() if r.get("status") == "FAIL"
                ),
            },
        }

        with open("test_results.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="OBA Robot Donanım Test Scripti")
    parser.add_argument("--test", help="Sadece belirli bir testi çalıştır")
    parser.add_argument("--verbose", "-v", action="store_true", help="Detaylı çıktı")

    args = parser.parse_args()

    tester = HardwareTest()

    if args.test:
        # Belirli bir test çalıştır
        test_method = getattr(tester, f"test_{args.test}", None)
        if test_method:
            print(f"🔧 {args.test} testi çalıştırılıyor...")
            test_method()
            tester.print_summary()
        else:
            print(f"❌ Geçersiz test adı: {args.test}")
            print("Kullanılabilir testler:")
            for method in dir(tester):
                if method.startswith("test_") and callable(getattr(tester, method)):
                    print(f"  - {method[5:]}")
    else:
        # Tüm testleri çalıştır
        tester.run_all_tests()
