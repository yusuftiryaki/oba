#!/usr/bin/env python3
"""
OBA Robot - Odometri Kalibrasyon Test Scripti
Enkoder ve IMU verilerini kullanarak odometri doğruluğunu test eder.
"""

import sys
import time
import math
from pathlib import Path

# Proje kök dizinini path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.navigation.kalman_odometry import KalmanOdometry


class OdometryCalibration:
    def __init__(self):
        self.odometry = KalmanOdometry(simulate=True)
        self.test_results = {}

    def run_calibration_tests(self):
        """Tüm kalibrasyon testlerini çalıştır"""
        print("📐 OBA Robot Odometri Kalibrasyon Testi")
        print("=" * 50)

        tests = [
            self.test_straight_line_accuracy,
            self.test_rotation_accuracy,
            self.test_square_path,
            self.test_drift_compensation,
            self.test_imu_integration,
        ]

        for test in tests:
            print(f"\n🔬 {test.__name__} çalıştırılıyor...")
            try:
                test()
                print(f"✅ {test.__name__} tamamlandı")
            except Exception as e:
                print(f"❌ {test.__name__} başarısız: {e}")

        self.print_calibration_summary()

    def test_straight_line_accuracy(self):
        """Düz çizgi hareket doğruluğu testi"""
        print("  📏 1 metre düz hareket testi...")

        # Başlangıç pozisyonu kaydet
        self.odometry.reset_position()
        start_pos = self.odometry.get_position()

        # 1 metre ileri hareket simülasyonu
        # Her adımda 1cm hareket (100 adım = 1m)
        for step in range(100):
            # Her cm için enkoder tick hesapla
            # Örnek: 0.5m çap tekerlek, 1024 PPR enkoder
            wheel_circumference = 0.5 * math.pi  # ~1.57m
            ticks_per_cm = 1024 / (wheel_circumference * 100)  # tick/cm

            left_ticks = int(ticks_per_cm)
            right_ticks = int(ticks_per_cm)

            self.odometry.update_encoders(left_ticks, right_ticks)
            time.sleep(0.01)  # 10ms simülasyon delay

        # Son pozisyonu kontrol et
        end_pos = self.odometry.get_position()
        actual_distance = math.sqrt(
            (end_pos.x - start_pos.x) ** 2 + (end_pos.y - start_pos.y) ** 2
        )

        error_percent = abs(actual_distance - 1.0) / 1.0 * 100

        print(f"     Hedef mesafe: 1.00 m")
        print(f"     Ölçülen mesafe: {actual_distance:.3f} m")
        print(f"     Hata: {error_percent:.2f}%")

        self.test_results["straight_line"] = {
            "target_distance": 1.0,
            "measured_distance": actual_distance,
            "error_percent": error_percent,
            "pass": error_percent < 5.0,  # %5 tolerans
        }

    def test_rotation_accuracy(self):
        """360° dönme doğruluğu testi"""
        print("  🔄 360° dönme testi...")

        self.odometry.reset_position()
        start_pos = self.odometry.get_position()

        # 360° dönme simülasyonu (saat yönünde)
        # Robot genişliği 0.45m varsayım
        robot_width = 0.45
        wheel_circumference = 0.5 * math.pi

        # 360° dönmek için gereken tekerlek hareketi
        rotation_distance = robot_width * math.pi  # ~1.41m
        total_ticks = int(rotation_distance / wheel_circumference * 1024)

        # Sol tekerlek geri, sağ tekerlek ileri
        steps = 360  # Her derece için bir adım
        ticks_per_step = total_ticks // steps

        for step in range(steps):
            # IMU verisi simülasyonu (1° dönem/adım)
            gyro_z = math.radians(1.0)  # 1°/adım
            self.odometry.update_imu(accel=[0, 0, 9.8], gyro=[0, 0, gyro_z])

            # Enkoder verisi
            self.odometry.update_encoders(-ticks_per_step, ticks_per_step)
            time.sleep(0.01)

        end_pos = self.odometry.get_position()
        final_heading = end_pos.heading % 360

        # Pozisyon drift kontrolü
        position_drift = math.sqrt(
            (end_pos.x - start_pos.x) ** 2 + (end_pos.y - start_pos.y) ** 2
        )

        heading_error = abs(final_heading - start_pos.heading) % 360
        if heading_error > 180:
            heading_error = 360 - heading_error

        print(f"     Başlangıç yönü: {start_pos.heading:.1f}°")
        print(f"     Final yönü: {final_heading:.1f}°")
        print(f"     Yön hatası: {heading_error:.2f}°")
        print(f"     Pozisyon drift: {position_drift:.3f} m")

        self.test_results["rotation"] = {
            "target_rotation": 360.0,
            "heading_error": heading_error,
            "position_drift": position_drift,
            "pass": heading_error < 5.0 and position_drift < 0.1,
        }

    def test_square_path(self):
        """Kare path testi (1m x 1m)"""
        print("  ⬜ 1m x 1m kare path testi...")

        self.odometry.reset_position()
        start_pos = self.odometry.get_position()

        # 4 kenar x (1m düz + 90° dönme)
        for side in range(4):
            print(f"     Kenar {side + 1}/4")

            # 1 metre düz hareket
            wheel_circumference = 0.5 * math.pi
            ticks_per_meter = 1024 / wheel_circumference
            total_ticks = int(ticks_per_meter)

            for tick in range(0, total_ticks, 10):  # 10'ar tick adımlar
                self.odometry.update_encoders(10, 10)
                time.sleep(0.001)

            # 90° sağa dönme
            robot_width = 0.45
            rotation_distance = robot_width * math.pi / 4  # 90° için
            rotation_ticks = int(rotation_distance / wheel_circumference * 1024)

            for tick in range(0, rotation_ticks, 5):
                self.odometry.update_encoders(-5, 5)
                # IMU verisi
                self.odometry.update_imu(
                    accel=[0, 0, 9.8], gyro=[0, 0, math.radians(2)]  # 2°/adım
                )
                time.sleep(0.001)

        end_pos = self.odometry.get_position()

        # Başlangıç noktasına dönüş hatası
        return_error = math.sqrt(
            (end_pos.x - start_pos.x) ** 2 + (end_pos.y - start_pos.y) ** 2
        )

        heading_error = abs((end_pos.heading - start_pos.heading) % 360)
        if heading_error > 180:
            heading_error = 360 - heading_error

        print(f"     Başlangıç: ({start_pos.x:.3f}, {start_pos.y:.3f})")
        print(f"     Bitiş: ({end_pos.x:.3f}, {end_pos.y:.3f})")
        print(f"     Geri dönüş hatası: {return_error:.3f} m")
        print(f"     Yön hatası: {heading_error:.2f}°")

        self.test_results["square_path"] = {
            "return_error": return_error,
            "heading_error": heading_error,
            "pass": return_error < 0.2 and heading_error < 10.0,
        }

    def test_drift_compensation(self):
        """Drift kompensasyon testi"""
        print("  🔧 Drift kompensasyon testi...")

        self.odometry.reset_position()

        # Asimetrik enkoder verisi ile drift simülasyonu
        # Sol tekerlek %2 daha hızlı
        base_ticks = 50
        left_ticks = int(base_ticks * 1.02)  # %2 fazla
        right_ticks = base_ticks

        positions = []

        # 10 saniye boyunca hareket
        for second in range(10):
            for step in range(10):  # 10 Hz
                self.odometry.update_encoders(left_ticks, right_ticks)

                # IMU verisi ekle (drift düzeltme için)
                if step % 5 == 0:  # 2 Hz IMU güncelleme
                    self.odometry.update_imu(
                        accel=[0.1, 0, 9.8],  # Hafif yan ivme
                        gyro=[0, 0, 0.01],  # Hafif yaw drift
                    )

                pos = self.odometry.get_position()
                positions.append((pos.x, pos.y, pos.heading))
                time.sleep(0.001)

        # Drift analizi
        final_pos = self.odometry.get_position()
        expected_heading = 0.0  # Düz gitmeyi bekliyoruz
        actual_heading = final_pos.heading

        drift_angle = abs(actual_heading - expected_heading)
        if drift_angle > 180:
            drift_angle = 360 - drift_angle

        print(f"     Asimetrik enkoder verisi: L={left_ticks}, R={right_ticks}")
        print(f"     Beklenen yön: {expected_heading:.1f}°")
        print(f"     Gerçek yön: {actual_heading:.1f}°")
        print(f"     Drift açısı: {drift_angle:.2f}°")

        # Kalman filtresi drift düzeltmesinin etkinliği
        compensation_effective = drift_angle < 5.0

        self.test_results["drift_compensation"] = {
            "drift_angle": drift_angle,
            "compensation_effective": compensation_effective,
            "pass": compensation_effective,
        }

    def test_imu_integration(self):
        """IMU entegrasyonu testi"""
        print("  🧭 IMU entegrasyonu testi...")

        self.odometry.reset_position()

        # Sadece IMU ile dönme testi
        print("     Sadece IMU ile 180° dönme...")
        target_rotation = 180.0

        steps = 180
        for step in range(steps):
            # Her adımda 1° dönme
            gyro_z = math.radians(1.0)
            self.odometry.update_imu(accel=[0, 0, 9.8], gyro=[0, 0, gyro_z])
            time.sleep(0.001)

        imu_only_heading = self.odometry.get_position().heading

        # Enkoder + IMU kombinasyonu testi
        print("     Enkoder + IMU kombinasyonu...")
        self.odometry.reset_position()

        robot_width = 0.45
        wheel_circumference = 0.5 * math.pi
        rotation_distance = robot_width * math.pi / 2  # 180° için
        rotation_ticks = int(rotation_distance / wheel_circumference * 1024)

        steps = 180
        ticks_per_step = rotation_ticks // steps

        for step in range(steps):
            # Enkoder verisi
            self.odometry.update_encoders(-ticks_per_step, ticks_per_step)

            # IMU verisi
            gyro_z = math.radians(1.0)
            self.odometry.update_imu(accel=[0, 0, 9.8], gyro=[0, 0, gyro_z])
            time.sleep(0.001)

        combined_heading = self.odometry.get_position().heading

        imu_error = abs(imu_only_heading - target_rotation)
        combined_error = abs(combined_heading - target_rotation)

        print(f"     Hedef: {target_rotation}°")
        print(f"     Sadece IMU: {imu_only_heading:.1f}° (hata: {imu_error:.1f}°)")
        print(
            f"     Enkoder+IMU: {combined_heading:.1f}° (hata: {combined_error:.1f}°)"
        )

        self.test_results["imu_integration"] = {
            "target_rotation": target_rotation,
            "imu_only_error": imu_error,
            "combined_error": combined_error,
            "pass": combined_error < imu_error and combined_error < 3.0,
        }

    def print_calibration_summary(self):
        """Kalibrasyon sonuçlarını özetle"""
        print("\n" + "=" * 50)
        print("📊 KALIBRASYON TEST ÖZETİ")
        print("=" * 50)

        total_tests = len(self.test_results)
        passed_tests = sum(
            1 for result in self.test_results.values() if result.get("pass", False)
        )

        print(f"Toplam Test: {total_tests}")
        print(f"Başarılı: {passed_tests}")
        print(f"Başarısız: {total_tests - passed_tests}")
        print(f"Başarı Oranı: %{(passed_tests/total_tests)*100:.1f}")

        print("\nDetaylı Sonuçlar:")
        for test_name, result in self.test_results.items():
            status = "✅ GEÇTI" if result.get("pass", False) else "❌ KALDI"
            print(f"{status} {test_name}")

        # Kalibrasyon önerileri
        print("\n🔧 KALIBRASYON ÖNERİLERİ:")

        if "straight_line" in self.test_results:
            error = self.test_results["straight_line"]["error_percent"]
            if error > 2.0:
                print(f"• Tekerlek çap kalibrasyonu gerekli (hata: %{error:.1f})")

        if "rotation" in self.test_results:
            error = self.test_results["rotation"]["heading_error"]
            if error > 2.0:
                print(f"• Robot genişlik kalibrasyonu gerekli (hata: {error:.1f}°)")

        if "drift_compensation" in self.test_results:
            if not self.test_results["drift_compensation"]["compensation_effective"]:
                print("• Kalman filtre parametreleri ayarlanmalı")

        if passed_tests == total_tests:
            print("• ✅ Tüm testler başarılı! Odometri kalibrasyonu iyi.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="OBA Robot Odometri Kalibrasyon")
    parser.add_argument("--test", help="Sadece belirli bir testi çalıştır")
    parser.add_argument("--distance", type=float, help="Belirli mesafe testi (metre)")
    parser.add_argument("--rotation", type=float, help="Belirli dönme testi (derece)")

    args = parser.parse_args()

    calibration = OdometryCalibration()

    if args.distance:
        print(f"🏃 {args.distance}m mesafe testi çalıştırılıyor...")
        # Özel mesafe testi implementasyonu burada olabilir
    elif args.rotation:
        print(f"🔄 {args.rotation}° dönme testi çalıştırılıyor...")
        # Özel dönme testi implementasyonu burada olabilir
    elif args.test:
        test_method = getattr(calibration, f"test_{args.test}", None)
        if test_method:
            test_method()
        else:
            print(f"❌ Geçersiz test: {args.test}")
    else:
        calibration.run_calibration_tests()
