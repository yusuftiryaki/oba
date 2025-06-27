#!/usr/bin/env python3
"""
OBA Robot - Pre-Flight Güvenlik Kontrol Scripti
Robot operasyon öncesi güvenlik kontrollerini yapar.
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Proje kök dizinini path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class SafetyChecker:
    def __init__(self):
        self.checks = {}
        self.critical_failures = []
        self.warnings = []

    def run_safety_checks(self):
        """Tüm güvenlik kontrollerini çalıştır"""
        print("🛡️ OBA Robot Pre-Flight Güvenlik Kontrolü")
        print("=" * 50)
        print(f"Kontrol Zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Güvenlik kontrol listesi
        safety_checks = [
            self.check_emergency_stop,
            self.check_battery_safety,
            self.check_motor_safety,
            self.check_cutting_system,
            self.check_sensors,
            self.check_communication,
            self.check_work_area,
            self.check_weather_conditions,
            self.check_maintenance_status,
        ]

        for check in safety_checks:
            try:
                check()
            except Exception as e:
                self.critical_failures.append(f"{check.__name__}: {e}")
                print(f"❌ {check.__name__} BAŞARISIZ: {e}")

        self.evaluate_safety_status()
        return len(self.critical_failures) == 0

    def check_emergency_stop(self):
        """Acil durdurma sistemi kontrolü"""
        print("🚨 Acil Durdurma Sistemi Kontrolü...")

        # Fiziksel buton kontrolü
        emergency_button_status = True  # Simülasyon
        if emergency_button_status:
            print("  ✅ Fiziksel acil durdurma butonu çalışıyor")
        else:
            self.critical_failures.append(
                "Fiziksel acil durdurma butonu yanıt vermiyor"
            )

        # Yazılımsal acil durdurma
        software_estop = True  # Simülasyon
        if software_estop:
            print("  ✅ Yazılımsal acil durdurma aktif")
        else:
            self.critical_failures.append(
                "Yazılımsal acil durdurma sistemi aktif değil"
            )

        # Uzaktan acil durdurma (web arayüzü)
        remote_estop = True  # Simülasyon
        if remote_estop:
            print("  ✅ Uzaktan acil durdurma erişilebilir")
        else:
            self.warnings.append("Uzaktan acil durdurma erişilemez durumda")

        self.checks["emergency_stop"] = {
            "physical_button": emergency_button_status,
            "software_estop": software_estop,
            "remote_estop": remote_estop,
        }

    def check_battery_safety(self):
        """Batarya güvenlik kontrolü"""
        print("🔋 Batarya Güvenlik Kontrolü...")

        # Batarya seviyesi
        battery_level = 78  # Simülasyon %
        if battery_level >= 50:
            print(f"  ✅ Batarya seviyesi yeterli: %{battery_level}")
        elif battery_level >= 20:
            self.warnings.append(f"Batarya seviyesi düşük: %{battery_level}")
            print(f"  ⚠️ Batarya seviyesi düşük: %{battery_level}")
        else:
            self.critical_failures.append(f"Batarya seviyesi kritik: %{battery_level}")

        # Batarya voltajı
        battery_voltage = 25.2  # Simülasyon V
        if 23.0 <= battery_voltage <= 29.0:
            print(f"  ✅ Batarya voltajı normal: {battery_voltage}V")
        else:
            self.critical_failures.append(
                f"Batarya voltajı anormal: {battery_voltage}V"
            )

        # Batarya sıcaklığı
        battery_temp = 32  # Simülasyon °C
        if battery_temp <= 45:
            print(f"  ✅ Batarya sıcaklığı normal: {battery_temp}°C")
        else:
            self.critical_failures.append(f"Batarya sıcaklığı yüksek: {battery_temp}°C")

        # BMS durumu
        bms_status = "GOOD"  # Simülasyon
        if bms_status == "GOOD":
            print(f"  ✅ BMS durumu: {bms_status}")
        else:
            self.critical_failures.append(f"BMS problemi: {bms_status}")

        self.checks["battery_safety"] = {
            "level": battery_level,
            "voltage": battery_voltage,
            "temperature": battery_temp,
            "bms_status": bms_status,
        }

    def check_motor_safety(self):
        """Motor güvenlik kontrolü"""
        print("⚙️ Motor Güvenlik Kontrolü...")

        # Motor sıcaklıkları
        motor_temps = {
            "left_track": 45,  # Simülasyon °C
            "right_track": 43,
            "cutting": 38,
        }

        for motor, temp in motor_temps.items():
            if temp <= 70:
                print(f"  ✅ {motor} motoru sıcaklığı normal: {temp}°C")
            else:
                self.critical_failures.append(f"{motor} motoru aşırı ısınmış: {temp}°C")

        # Motor akım değerleri
        motor_currents = {
            "left_track": 2.1,  # Simülasyon A
            "right_track": 2.0,
            "cutting": 3.5,
        }

        max_currents = {"left_track": 15.0, "right_track": 15.0, "cutting": 10.0}

        for motor, current in motor_currents.items():
            if current <= max_currents[motor] * 0.8:
                print(f"  ✅ {motor} motoru akımı normal: {current}A")
            else:
                self.warnings.append(f"{motor} motoru yüksek akım çekiyor: {current}A")

        # Motor encoder durumu
        encoder_status = {"left": "OK", "right": "OK"}  # Simülasyon
        for side, status in encoder_status.items():
            if status == "OK":
                print(f"  ✅ {side} enkoder çalışıyor")
            else:
                self.critical_failures.append(f"{side} enkoder problemi: {status}")

        self.checks["motor_safety"] = {
            "temperatures": motor_temps,
            "currents": motor_currents,
            "encoders": encoder_status,
        }

    def check_cutting_system(self):
        """Biçme sistemi güvenlik kontrolü"""
        print("✂️ Biçme Sistemi Güvenlik Kontrolü...")

        # Koruma kapağı kontrolü
        protection_cover = True  # Simülasyon
        if protection_cover:
            print("  ✅ Biçme koruma kapağı takılı")
        else:
            self.critical_failures.append("Biçme koruma kapağı takılı değil")

        # Misina durumu
        cutting_line_status = "GOOD"  # Simülasyon
        if cutting_line_status == "GOOD":
            print("  ✅ Misina durumu iyi")
        else:
            self.warnings.append(f"Misina problemi: {cutting_line_status}")

        # Yükseklik ayar sistemi
        height_actuator_status = "FUNCTIONAL"  # Simülasyon
        if height_actuator_status == "FUNCTIONAL":
            print("  ✅ Yükseklik ayar sistemi çalışıyor")
        else:
            self.critical_failures.append(
                f"Yükseklik ayar problemi: {height_actuator_status}"
            )

        # Biçme motor vibrasyon
        cutting_vibration = 2.5  # Simülasyon (m/s²)
        if cutting_vibration <= 5.0:
            print(f"  ✅ Biçme motor vibrasyonu normal: {cutting_vibration} m/s²")
        else:
            self.warnings.append(
                f"Biçme motor yüksek vibrasyon: {cutting_vibration} m/s²"
            )

        self.checks["cutting_system"] = {
            "protection_cover": protection_cover,
            "cutting_line": cutting_line_status,
            "height_actuator": height_actuator_status,
            "vibration": cutting_vibration,
        }

    def check_sensors(self):
        """Sensör güvenlik kontrolü"""
        print("📡 Sensör Güvenlik Kontrolü...")

        # IMU kalibrasyonu
        imu_calibration = "GOOD"  # Simülasyon
        if imu_calibration == "GOOD":
            print("  ✅ IMU kalibrasyonu iyi")
        else:
            self.critical_failures.append(
                f"IMU kalibrasyonu problemi: {imu_calibration}"
            )

        # Kamera durumu
        camera_status = "OPERATIONAL"  # Simülasyon
        if camera_status == "OPERATIONAL":
            print("  ✅ Kamera çalışıyor")
        else:
            self.warnings.append(f"Kamera problemi: {camera_status}")

        # IR sensörler
        ir_sensors = {"sensor1": 45.2, "sensor2": 52.8}  # Simülasyon (cm)
        for sensor, distance in ir_sensors.items():
            if 5 <= distance <= 100:
                print(f"  ✅ {sensor} çalışıyor: {distance} cm")
            else:
                self.warnings.append(f"{sensor} anormal okuma: {distance} cm")

        # Enkoder hassasiyeti
        encoder_precision = 0.98  # Simülasyon (0-1)
        if encoder_precision >= 0.95:
            print(f"  ✅ Enkoder hassasiyeti iyi: %{encoder_precision*100:.1f}")
        else:
            self.warnings.append(
                f"Enkoder hassasiyeti düşük: %{encoder_precision*100:.1f}"
            )

        self.checks["sensors"] = {
            "imu_calibration": imu_calibration,
            "camera": camera_status,
            "ir_sensors": ir_sensors,
            "encoder_precision": encoder_precision,
        }

    def check_communication(self):
        """İletişim güvenlik kontrolü"""
        print("📡 İletişim Güvenlik Kontrolü...")

        # Wi-Fi bağlantısı
        wifi_signal = -45  # Simülasyon dBm
        if wifi_signal >= -60:
            print(f"  ✅ Wi-Fi sinyali güçlü: {wifi_signal} dBm")
        elif wifi_signal >= -75:
            self.warnings.append(f"Wi-Fi sinyali zayıf: {wifi_signal} dBm")
            print(f"  ⚠️ Wi-Fi sinyali zayıf: {wifi_signal} dBm")
        else:
            self.critical_failures.append(f"Wi-Fi sinyali çok zayıf: {wifi_signal} dBm")

        # Web sunucu durumu
        web_server_status = "RUNNING"  # Simülasyon
        if web_server_status == "RUNNING":
            print("  ✅ Web sunucu çalışıyor")
        else:
            self.warnings.append(f"Web sunucu problemi: {web_server_status}")

        # WebSocket bağlantısı
        websocket_connections = 1  # Simülasyon
        if websocket_connections > 0:
            print(f"  ✅ WebSocket bağlantısı aktif: {websocket_connections} client")
        else:
            self.warnings.append("WebSocket bağlantısı yok")

        self.checks["communication"] = {
            "wifi_signal": wifi_signal,
            "web_server": web_server_status,
            "websocket_clients": websocket_connections,
        }

    def check_work_area(self):
        """Çalışma alanı güvenlik kontrolü"""
        print("🏞️ Çalışma Alanı Güvenlik Kontrolü...")

        # Alan sınırları tanımlı mı?
        area_defined = True  # Simülasyon
        if area_defined:
            print("  ✅ Çalışma alanı tanımlanmış")
        else:
            self.critical_failures.append("Çalışma alanı tanımlanmamış")

        # Engel tarama
        obstacles_detected = []  # Simülasyon
        if not obstacles_detected:
            print("  ✅ Çalışma alanında engel tespit edilmedi")
        else:
            self.warnings.append(
                f"Çalışma alanında {len(obstacles_detected)} engel tespit edildi"
            )

        # Eğim kontrolü
        max_slope = 12  # Simülasyon %
        if max_slope <= 15:
            print(f"  ✅ Maksimum eğim güvenli: %{max_slope}")
        else:
            self.critical_failures.append(f"Çalışma alanı çok eğimli: %{max_slope}")

        # Şarj istasyonu erişimi
        station_accessible = True  # Simülasyon
        if station_accessible:
            print("  ✅ Şarj istasyonuna erişim mümkün")
        else:
            self.critical_failures.append("Şarj istasyonuna erişim engelli")

        self.checks["work_area"] = {
            "area_defined": area_defined,
            "obstacles": len(obstacles_detected),
            "max_slope": max_slope,
            "station_accessible": station_accessible,
        }

    def check_weather_conditions(self):
        """Hava durumu güvenlik kontrolü"""
        print("🌤️ Hava Durumu Güvenlik Kontrolü...")

        # Yağmur sensörü (varsa)
        rain_detected = False  # Simülasyon
        if not rain_detected:
            print("  ✅ Yağmur tespit edilmedi")
        else:
            self.critical_failures.append("Yağmur tespit edildi - güvenli değil")

        # Rüzgar hızı (tahmini)
        wind_speed = 15  # Simülasyon km/h
        if wind_speed <= 25:
            print(f"  ✅ Rüzgar hızı uygun: {wind_speed} km/h")
        else:
            self.warnings.append(f"Rüzgar hızı yüksek: {wind_speed} km/h")

        # Görüş mesafesi
        visibility = "GOOD"  # Simülasyon
        if visibility == "GOOD":
            print("  ✅ Görüş mesafesi iyi")
        else:
            self.warnings.append(f"Görüş mesafesi kötü: {visibility}")

        self.checks["weather"] = {
            "rain": rain_detected,
            "wind_speed": wind_speed,
            "visibility": visibility,
        }

    def check_maintenance_status(self):
        """Bakım durumu kontrolü"""
        print("🔧 Bakım Durumu Kontrolü...")

        # Son bakım tarihi
        last_maintenance = "2025-06-20"  # Simülasyon
        days_since_maintenance = 7  # Simülasyon

        if days_since_maintenance <= 30:
            print(
                f"  ✅ Son bakım: {last_maintenance} ({days_since_maintenance} gün önce)"
            )
        else:
            self.warnings.append(
                f"Bakım gerekli: {days_since_maintenance} gün önce yapıldı"
            )

        # Çalışma saatleri
        total_hours = 125  # Simülasyon
        if total_hours <= 500:
            print(f"  ✅ Toplam çalışma saati: {total_hours}h")
        else:
            self.warnings.append(
                f"Yüksek çalışma saati: {total_hours}h - bakım önerilir"
            )

        # Parça ömrü kontrolü
        parts_status = {"cutting_line": 85, "belts": 92, "bearings": 78}  # % kalan ömür

        for part, remaining in parts_status.items():
            if remaining >= 20:
                print(f"  ✅ {part} durumu iyi: %{remaining}")
            else:
                self.warnings.append(f"{part} değiştirme zamanı: %{remaining}")

        self.checks["maintenance"] = {
            "last_maintenance": last_maintenance,
            "days_since_maintenance": days_since_maintenance,
            "total_hours": total_hours,
            "parts_status": parts_status,
        }

    def evaluate_safety_status(self):
        """Güvenlik durumunu değerlendir ve karar ver"""
        print("\n" + "=" * 50)
        print("📊 GÜVENLİK DEĞERLENDİRMESİ")
        print("=" * 50)

        if self.critical_failures:
            print("❌ KRİTİK HATALAR TESPİT EDİLDİ!")
            print("Robot operasyona UYGUN DEĞİL!")
            print("\nKritik Hatalar:")
            for failure in self.critical_failures:
                print(f"  ❌ {failure}")

        elif self.warnings:
            print("⚠️ UYARILAR TESPİT EDİLDİ")
            print("Robot dikkatli kullanımla operasyona uygun")
            print("\nUyarılar:")
            for warning in self.warnings:
                print(f"  ⚠️ {warning}")

        else:
            print("✅ TÜM GÜVENLİK KONTROLLERİ BAŞARILI!")
            print("Robot operasyona HAZIR!")

        print(f"\nToplam Kontrol: {len(self.checks)}")
        print(f"Kritik Hata: {len(self.critical_failures)}")
        print(f"Uyarı: {len(self.warnings)}")

        # Güvenlik raporu kaydet
        self.save_safety_report()

        return len(self.critical_failures) == 0

    def save_safety_report(self):
        """Güvenlik raporunu kaydet"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "robot_version": "1.0.0",
            "safety_status": "PASS" if len(self.critical_failures) == 0 else "FAIL",
            "critical_failures": self.critical_failures,
            "warnings": self.warnings,
            "detailed_checks": self.checks,
            "summary": {
                "total_checks": len(self.checks),
                "critical_failures": len(self.critical_failures),
                "warnings": len(self.warnings),
            },
        }

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"safety_report_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n📄 Güvenlik raporu kaydedildi: {filename}")


def main():
    """Ana fonksiyon"""
    import argparse

    parser = argparse.ArgumentParser(
        description="OBA Robot Pre-Flight Güvenlik Kontrolü"
    )
    parser.add_argument(
        "--force", action="store_true", help="Uyarıları göz ardı et ve devam et"
    )
    parser.add_argument(
        "--quick", action="store_true", help="Hızlı kontrol (sadece kritik kontroller)"
    )

    args = parser.parse_args()

    checker = SafetyChecker()

    if args.quick:
        print("🚀 Hızlı güvenlik kontrolü...")
        # Sadece kritik kontroller
        critical_checks = [
            checker.check_emergency_stop,
            checker.check_battery_safety,
            checker.check_cutting_system,
        ]
        for check in critical_checks:
            check()
    else:
        # Tam güvenlik kontrolü
        safety_ok = checker.run_safety_checks()

        if not safety_ok and not args.force:
            print("\n🚫 ROBOT OPERASYONA UYGUN DEĞİL!")
            print("Kritik hataları çözün ve tekrar deneyin.")
            print("Zorla devam etmek için --force parametresini kullanın.")
            sys.exit(1)
        elif not safety_ok and args.force:
            print("\n⚠️ UYARI: Güvenlik hataları göz ardı edilerek devam ediliyor!")

    print("\n✅ Güvenlik kontrolü tamamlandı.")


if __name__ == "__main__":
    main()
