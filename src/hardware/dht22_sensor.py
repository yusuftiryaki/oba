#!/usr/bin/env python3
"""
DHT22 Sıcaklık/Nem Sensörü Hardware Sınıfı
Hacı Abi'nin Gerçek Donanım Interface'i
"""

import time
import logging
import threading
from dataclasses import dataclass
from typing import Optional, Tuple
from datetime import datetime

try:
    import board
    import adafruit_dht

    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False
    logging.warning("DHT22 hardware kütüphaneleri bulunamadı - simülasyon modu")


@dataclass
class DHT22Reading:
    """DHT22 okuma verisi"""

    temperature: float
    humidity: float
    timestamp: datetime
    is_valid: bool
    error_message: Optional[str] = None


class DHT22Hardware:
    """DHT22 sensörü için hardware interface"""

    def __init__(self, pin_number: int = 4, retry_count: int = 3):
        """
        DHT22 hardware başlatıcı

        Args:
            pin_number: GPIO pin numarası (varsayılan: 4)
            retry_count: Hata durumunda tekrar deneme sayısı
        """
        self.pin_number = pin_number
        self.retry_count = retry_count
        self.sensor = None
        self.last_reading = None
        self.last_successful_time = None
        self.error_count = 0
        self.lock = threading.Lock()

        # Logger
        self.logger = logging.getLogger(f"DHT22_GPIO{pin_number}")

        # Sensör başlat
        self._initialize_sensor()

    def _initialize_sensor(self) -> bool:
        """DHT22 sensörünü başlat"""
        if not HARDWARE_AVAILABLE:
            self.logger.warning("Hardware kütüphaneleri eksik - simülasyon modu aktif")
            return False

        try:
            # GPIO pin object'i oluştur
            if self.pin_number == 4:
                pin = board.D4
            elif self.pin_number == 17:
                pin = board.D17
            elif self.pin_number == 18:
                pin = board.D18
            elif self.pin_number == 27:
                pin = board.D27
            else:
                raise ValueError(f"Desteklenmeyen GPIO pin: {self.pin_number}")

            # DHT22 sensörü oluştur
            self.sensor = adafruit_dht.DHT22(pin)
            self.logger.info(f"✅ DHT22 sensörü başlatıldı (GPIO{self.pin_number})")
            return True

        except Exception as e:
            self.logger.error(f"❌ DHT22 başlatma hatası: {e}")
            self.sensor = None
            return False

    def read_sensor(self) -> DHT22Reading:
        """
        Sensörden sıcaklık ve nem okuma yap

        Returns:
            DHT22Reading object
        """
        with self.lock:
            return self._perform_reading()

    def _perform_reading(self) -> DHT22Reading:
        """Gerçek okuma işlemini yap"""
        current_time = datetime.now()

        # Simülasyon modu
        if not HARDWARE_AVAILABLE or self.sensor is None:
            return self._simulate_reading(current_time)

        # Son okumadan bu yana yeterli zaman geçti mi? (DHT22 min 2 saniye)
        if (
            self.last_successful_time
            and (current_time - self.last_successful_time).total_seconds() < 2.0
        ):

            if self.last_reading:
                # Son okunan değeri döndür
                return DHT22Reading(
                    temperature=self.last_reading.temperature,
                    humidity=self.last_reading.humidity,
                    timestamp=current_time,
                    is_valid=True,
                    error_message="Cached reading (too frequent)",
                )

        # Gerçek sensör okuma
        for attempt in range(self.retry_count):
            try:
                temp = self.sensor.temperature
                humidity = self.sensor.humidity

                if temp is not None and humidity is not None:
                    # Mantık kontrolleri
                    if not self._validate_readings(temp, humidity):
                        self.logger.warning(f"Geçersiz değerler: {temp}°C, {humidity}%")
                        continue

                    # Başarılı okuma
                    reading = DHT22Reading(
                        temperature=round(temp, 1),
                        humidity=round(humidity, 1),
                        timestamp=current_time,
                        is_valid=True,
                    )

                    self.last_reading = reading
                    self.last_successful_time = current_time
                    self.error_count = 0

                    self.logger.debug(f"📊 DHT22: {temp:.1f}°C, {humidity:.1f}%")
                    return reading

                else:
                    self.logger.warning(f"Deneme {attempt + 1}: None değer döndü")

            except RuntimeError as e:
                # DHT22 checksum hatası vs.
                self.logger.warning(f"Deneme {attempt + 1}: {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(0.5)

            except Exception as e:
                self.logger.error(f"Beklenmeyen hata (deneme {attempt + 1}): {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(1.0)

        # Tüm denemeler başarısız
        self.error_count += 1
        error_msg = f"Tüm okuma denemeleri başarısız ({self.retry_count} deneme)"

        self.logger.error(f"❌ {error_msg}")

        return DHT22Reading(
            temperature=0.0,
            humidity=0.0,
            timestamp=current_time,
            is_valid=False,
            error_message=error_msg,
        )

    def _validate_readings(self, temp: float, humidity: float) -> bool:
        """Okunan değerlerin mantıklı olup olmadığını kontrol et"""
        # Sıcaklık kontrolleri (-40°C ~ +80°C)
        if temp < -40 or temp > 80:
            return False

        # Nem kontrolleri (0% ~ 100%)
        if humidity < 0 or humidity > 100:
            return False

        # Ani değişim kontrolleri (önceki okuma varsa)
        if self.last_reading and self.last_reading.is_valid:
            temp_diff = abs(temp - self.last_reading.temperature)
            hum_diff = abs(humidity - self.last_reading.humidity)

            # 1 dakikada 20°C değişim mantıksız
            if temp_diff > 20:
                self.logger.warning(f"Ani sıcaklık değişimi: {temp_diff:.1f}°C")
                return False

            # 1 dakikada 50% nem değişimi mantıksız
            if hum_diff > 50:
                self.logger.warning(f"Ani nem değişimi: {hum_diff:.1f}%")
                return False

        return True

    def _simulate_reading(self, timestamp: datetime) -> DHT22Reading:
        """Simülasyon verisi üret"""
        import random

        # Rastgele ama mantıklı değerler
        base_temp = 25  # °C
        base_humidity = 60  # %

        temp = base_temp + random.uniform(-10, 15)
        humidity = base_humidity + random.uniform(-20, 30)

        # Sınırları zorla
        temp = max(-10, min(50, temp))
        humidity = max(20, min(90, humidity))

        return DHT22Reading(
            temperature=round(temp, 1),
            humidity=round(humidity, 1),
            timestamp=timestamp,
            is_valid=True,
            error_message="Simulation mode",
        )

    def get_sensor_info(self) -> dict:
        """Sensör durum bilgisi"""
        return {
            "pin": f"GPIO{self.pin_number}",
            "hardware_available": HARDWARE_AVAILABLE,
            "sensor_initialized": self.sensor is not None,
            "error_count": self.error_count,
            "last_reading_time": (
                self.last_successful_time.isoformat()
                if self.last_successful_time
                else None
            ),
            "last_temperature": (
                self.last_reading.temperature if self.last_reading else None
            ),
            "last_humidity": self.last_reading.humidity if self.last_reading else None,
        }

    def cleanup(self):
        """Temizlik işlemleri"""
        if self.sensor:
            try:
                self.sensor.deinit()
                self.logger.info("DHT22 sensörü temizlendi")
            except:
                pass
        self.sensor = None


# Test fonksiyonu
def main():
    """DHT22 hardware test"""
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    print("🌡️ DHT22 Hardware Test")
    print("=" * 30)

    # DHT22 oluştur
    dht = DHT22Hardware(pin_number=4)

    try:
        for i in range(10):
            reading = dht.read_sensor()

            if reading.is_valid:
                print(
                    f"✅ {reading.timestamp.strftime('%H:%M:%S')} | "
                    f"{reading.temperature}°C | {reading.humidity}%"
                )
            else:
                print(
                    f"❌ {reading.timestamp.strftime('%H:%M:%S')} | "
                    f"Hata: {reading.error_message}"
                )

            time.sleep(3)

    except KeyboardInterrupt:
        print("\n⏹️ Test durduruldu")

    finally:
        dht.cleanup()
        print("🧹 Temizlik tamamlandı")


if __name__ == "__main__":
    main()
