#!/usr/bin/env python3
"""
DHT22 Sıcaklık/Nem Sensörü Test Scripti
Hacı Abi'nin Sensör Test Aracı
"""

import time
import board
import adafruit_dht
import numpy as np
from datetime import datetime
import logging
import sys

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/var/log/dht22_test.log"),
        logging.StreamHandler(sys.stdout),
    ],
)


class DHT22Tester:
    def __init__(self):
        """DHT22 test sınıfı başlatıcı"""
        try:
            self.dht = adafruit_dht.DHT22(board.D4)  # GPIO4
            self.readings = []
            logging.info("✅ DHT22 sensörü başlatıldı (GPIO4)")
        except Exception as e:
            logging.error(f"❌ DHT22 başlatma hatası: {e}")
            sys.exit(1)

    def single_reading(self):
        """Tek seferde okuma yap"""
        try:
            temp = self.dht.temperature
            humidity = self.dht.humidity

            if temp is not None and humidity is not None:
                print(f"🌡️ Sıcaklık: {temp:.1f}°C")
                print(f"💧 Nem: {humidity:.1f}%")
                return temp, humidity
            else:
                print("❌ Sensör okuma hatası")
                return None, None

        except Exception as e:
            print(f"⚠️ Okuma hatası: {e}")
            return None, None

    def continuous_test(self, duration_minutes=5):
        """Sürekli test"""
        print(f"🌡️ DHT22 Sürekli Test - {duration_minutes} dakika")
        print("=" * 50)

        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        error_count = 0
        success_count = 0

        while time.time() < end_time:
            try:
                temp, humidity = self.single_reading()

                if temp is not None and humidity is not None:
                    success_count += 1
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"✅ {timestamp} | {temp:.1f}°C | {humidity:.1f}%")
                else:
                    error_count += 1
                    print("❌ Okuma başarısız")

                time.sleep(3)  # DHT22 için minimum 2 saniye

            except KeyboardInterrupt:
                print("\n⏹️ Test durduruldu")
                break
            except Exception as e:
                error_count += 1
                print(f"⚠️ Beklenmeyen hata: {e}")
                time.sleep(5)

        # Test özeti
        total_attempts = success_count + error_count
        success_rate = (
            (success_count / total_attempts * 100) if total_attempts > 0 else 0
        )

        print(f"\n📊 Test Özeti:")
        print(f"   Başarılı okuma: {success_count}")
        print(f"   Hatalı okuma: {error_count}")
        print(f"   Başarı oranı: {success_rate:.1f}%")

        if success_rate >= 90:
            print("✅ Sensör durumu: MÜKEMMEL")
        elif success_rate >= 70:
            print("🟡 Sensör durumu: İYİ")
        else:
            print("❌ Sensör durumu: KÖTÜ - Kontrol gerekli")

    def calibration_check(self):
        """Kalibrasyon kontrol testi"""
        print("🔧 DHT22 Kalibrasyon Kontrol Testi")
        print("=" * 40)
        print("📝 Manuel olarak karşılaştırma yapın:")
        print("   1. Referans termometre ile sıcaklık")
        print("   2. Referans higrometre ile nem")
        print()

        # 10 okuma yap ve ortalama al
        temps = []
        hums = []

        for i in range(10):
            print(f"Okuma {i+1}/10...")
            temp, humidity = self.single_reading()

            if temp is not None and humidity is not None:
                temps.append(temp)
                hums.append(humidity)

            time.sleep(3)

        if temps and hums:
            avg_temp = np.mean(temps)
            avg_hum = np.mean(hums)
            temp_std = np.std(temps)
            hum_std = np.std(hums)

            print(f"\n📊 Ortalama Değerler:")
            print(f"   Sıcaklık: {avg_temp:.2f}°C (±{temp_std:.2f})")
            print(f"   Nem: {avg_hum:.2f}% (±{hum_std:.2f})")

            print(f"\n💡 Manuel karşılaştırma önerisi:")
            print(f"   - Referans termometre ile {avg_temp:.1f}°C'yi karşılaştır")
            print(f"   - Referans higrometre ile {avg_hum:.1f}%'yi karşılaştır")
            print(f"   - Tolerans: Sıcaklık ±1°C, Nem ±5%")


def main():
    """Ana fonksiyon"""
    print("🌡️ Hacı Abi'nin DHT22 Test Aracı")
    print("=" * 40)

    tester = DHT22Tester()

    while True:
        print("\n📋 Test Seçenekleri:")
        print("1. Tek okuma")
        print("2. Sürekli test (5 dakika)")
        print("3. Kalibrasyon kontrol")
        print("4. Çıkış")

        try:
            choice = input("\nSeçiminiz (1-4): ").strip()

            if choice == "1":
                print("\n🔍 Tek Okuma:")
                tester.single_reading()

            elif choice == "2":
                duration = input("Test süresi (dakika, varsayılan 5): ").strip()
                duration = int(duration) if duration else 5
                tester.continuous_test(duration)

            elif choice == "3":
                tester.calibration_check()

            elif choice == "4":
                print("👋 Çıkılıyor...")
                break

            else:
                print("❌ Geçersiz seçim!")

        except KeyboardInterrupt:
            print("\n👋 Çıkılıyor...")
            break
        except Exception as e:
            print(f"❌ Hata: {e}")


if __name__ == "__main__":
    main()
