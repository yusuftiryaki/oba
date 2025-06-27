"""
Güç Yönetimi Modülü
Batarya seviyelerini izler ve şarj kararlarını verir
"""

import time
import logging
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import threading


class PowerState(Enum):
    """Güç durumları"""

    NORMAL = "normal"
    LOW_BATTERY = "low_battery"
    CRITICAL_BATTERY = "critical_battery"
    CHARGING = "charging"
    FULL = "full"
    ERROR = "error"


class ChargingPhase(Enum):
    """Şarj aşamaları"""

    BULK = "bulk"  # Yoğun şarj
    ABSORPTION = "absorption"  # Absorpsiyon
    FLOAT = "float"  # Yüzer şarj
    COMPLETED = "completed"  # Tamamlandı


@dataclass
class BatteryReading:
    """Batarya okuması"""

    voltage: float
    current: float
    temperature: float
    timestamp: float
    state_of_charge: float  # %0-100


@dataclass
class PowerConsumption:
    """Güç tüketimi verisi"""

    component: str
    current_draw: float  # Amper
    power: float  # Watt
    efficiency: float  # %0-100


class PowerManager:
    """Güç yönetimi sınıfı"""

    def __init__(self, config_path: str = "config/power_config.json"):
        self.logger = logging.getLogger("PowerManager")

        # Konfigürasyon
        self.config = self._load_config(config_path)

        # Durum
        self.power_state = PowerState.NORMAL
        self.charging_phase = ChargingPhase.BULK

        # Batarya parametreleri
        self.battery_capacity = 20  # Ah
        self.battery_voltage_nominal = 24  # V
        self.battery_cells = 8  # LiFePO4 hücre sayısı
        self.cell_voltage_min = 2.5  # V
        self.cell_voltage_max = 3.65  # V

        # Voltaj seviyeleri
        self.voltage_full = self.battery_cells * 3.6  # 28.8V
        self.voltage_nominal = self.battery_cells * 3.2  # 25.6V
        self.voltage_low = self.battery_cells * 3.0  # 24V
        self.voltage_critical = self.battery_cells * 2.8  # 22.4V
        self.voltage_cutoff = self.battery_cells * 2.5  # 20V

        # Şarj parametreleri
        self.charge_current_max = 10  # A
        self.charge_voltage_max = self.voltage_full
        self.absorption_voltage = self.battery_cells * 3.55  # 28.4V
        self.float_voltage = self.battery_cells * 3.4  # 27.2V

        # Mevcut değerler
        self.current_reading: Optional[BatteryReading] = None
        self.charging_current = 0.0
        self.is_charging = False
        self.is_connected_to_charger = False

        # Geçmiş veriler
        self.reading_history: List[BatteryReading] = []
        self.max_history_size = 1000

        # Güç tüketimi takibi
        self.power_consumers: Dict[str, PowerConsumption] = {}
        self.total_power_consumption = 0.0

        # İstatistikler
        self.total_charge_cycles = 0
        self.total_discharge_time = 0
        self.total_charge_time = 0
        self.battery_health = 100.0  # %

        # Thread kontrol
        self.monitoring_active = False
        self.monitoring_thread = None

        # Alarm ve uyarılar
        self.low_battery_warned = False
        self.critical_battery_warned = False

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Konfigürasyon dosyasını yükle"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Power config dosyası bulunamadı: {config_path}")
            return self._default_power_config()

    def _default_power_config(self) -> Dict[str, Any]:
        """Varsayılan güç konfigürasyonu"""
        return {
            "battery": {
                "capacity_ah": 20,
                "voltage_nominal": 24,
                "cells": 8,
                "chemistry": "LiFePO4",
            },
            "thresholds": {
                "low_battery": 25,  # %25
                "critical_battery": 15,  # %15
                "full_battery": 95,  # %95
            },
            "charging": {
                "max_current": 10,  # A
                "absorption_time": 120,  # dakika
                "float_time": 60,  # dakika
            },
            "monitoring": {
                "update_interval": 1,  # saniye
                "save_interval": 300,  # 5 dakika
            },
            "power_consumers": {
                "raspberry_pi": 3,  # W
                "motors": 50,  # W
                "blade_motor": 150,  # W
                "camera": 2,  # W
                "sensors": 1,  # W
                "wifi": 2,  # W
            },
        }

    def start_monitoring(self):
        """Güç izlemesini başlat"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop, daemon=True
            )
            self.monitoring_thread.start()
            self.logger.info("Güç izlemesi başlatıldı")

    def stop_monitoring(self):
        """Güç izlemesini durdur"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
        self.logger.info("Güç izlemesi durduruldu")

    def _monitoring_loop(self):
        """Ana izleme döngüsü"""
        last_save_time = time.time()
        update_interval = self.config.get("monitoring", {}).get("update_interval", 1)
        save_interval = self.config.get("monitoring", {}).get("save_interval", 300)

        while self.monitoring_active:
            try:
                # Batarya okuması al
                reading = self._read_battery()
                if reading:
                    self.current_reading = reading
                    self._add_to_history(reading)

                    # Durum kontrolü
                    self._update_power_state(reading)

                    # Şarj kontrolü
                    if self.is_charging:
                        self._manage_charging(reading)

                # Periyodik kayıt
                current_time = time.time()
                if current_time - last_save_time > save_interval:
                    self._save_battery_data()
                    last_save_time = current_time

                time.sleep(update_interval)

            except Exception as e:
                self.logger.error(f"Güç izleme hatası: {e}")
                time.sleep(5)

    def _read_battery(self) -> Optional[BatteryReading]:
        """Batarya verilerini oku"""
        try:
            # ADC'den voltaj ve akım okuması (simülasyon)
            voltage = self._read_battery_voltage()
            current = self._read_battery_current()
            temperature = self._read_battery_temperature()

            # State of Charge hesapla
            soc = self._calculate_soc(voltage)

            return BatteryReading(
                voltage=voltage,
                current=current,
                temperature=temperature,
                timestamp=time.time(),
                state_of_charge=soc,
            )

        except Exception as e:
            self.logger.error(f"Batarya okuma hatası: {e}")
            return None

    def _read_battery_voltage(self) -> float:
        """Batarya voltajını oku"""
        # Gerçek implementasyonda ADC kullanılacak
        # import board, busio, adafruit_ads1x15.ads1115 as ADS

        # Simülasyon için
        import random

        base_voltage = 25.6  # Nominal voltaj
        if self.is_charging:
            base_voltage = min(28.8, base_voltage + 1.0)

        return base_voltage + random.uniform(-0.5, 0.5)

    def _read_battery_current(self) -> float:
        """Batarya akımını oku"""
        # Şarj akımı sensörü okuması (simülasyon)
        import random

        if self.is_charging:
            return random.uniform(5, 10)  # Şarj akımı
        else:
            # Tüketim akımı (negatif)
            total_consumption = sum(
                consumer.current_draw for consumer in self.power_consumers.values()
            )
            return -total_consumption - random.uniform(0, 1)

    def _read_battery_temperature(self) -> float:
        """Batarya sıcaklığını oku"""
        # Sıcaklık sensörü okuması (simülasyon)
        import random

        return random.uniform(20, 35)  # °C

    def _calculate_soc(self, voltage: float) -> float:
        """Voltajdan State of Charge hesapla"""
        # LiFePO4 voltaj-SoC eğrisi (basitleştirilmiş)
        voltage_per_cell = voltage / self.battery_cells

        if voltage_per_cell >= 3.6:
            return 100.0
        elif voltage_per_cell >= 3.4:
            return 90.0 + (voltage_per_cell - 3.4) * 50
        elif voltage_per_cell >= 3.2:
            return 50.0 + (voltage_per_cell - 3.2) * 200
        elif voltage_per_cell >= 3.0:
            return 20.0 + (voltage_per_cell - 3.0) * 150
        elif voltage_per_cell >= 2.8:
            return 5.0 + (voltage_per_cell - 2.8) * 75
        else:
            return max(0.0, (voltage_per_cell - 2.5) * 16.7)

    def _update_power_state(self, reading: BatteryReading):
        """Güç durumunu güncelle"""
        soc = reading.state_of_charge

        if self.is_charging:
            if soc >= self.config["thresholds"]["full_battery"]:
                self.power_state = PowerState.FULL
            else:
                self.power_state = PowerState.CHARGING
        else:
            if soc <= self.config["thresholds"]["critical_battery"]:
                self.power_state = PowerState.CRITICAL_BATTERY
                if not self.critical_battery_warned:
                    self.logger.critical(f"KRİTİK BATARYA SEVİYESİ: %{soc:.1f}")
                    self.critical_battery_warned = True
            elif soc <= self.config["thresholds"]["low_battery"]:
                self.power_state = PowerState.LOW_BATTERY
                if not self.low_battery_warned:
                    self.logger.warning(f"Düşük batarya seviyesi: %{soc:.1f}")
                    self.low_battery_warned = True
            else:
                self.power_state = PowerState.NORMAL
                self.low_battery_warned = False
                self.critical_battery_warned = False

    def _manage_charging(self, reading: BatteryReading):
        """Şarj yönetimi"""
        voltage = reading.voltage
        current = reading.current

        if self.charging_phase == ChargingPhase.BULK:
            # Yoğun şarj aşaması
            if voltage >= self.absorption_voltage:
                self.charging_phase = ChargingPhase.ABSORPTION
                self.logger.info("Absorpsiyon aşamasına geçildi")

        elif self.charging_phase == ChargingPhase.ABSORPTION:
            # Absorpsiyon aşaması
            if current < 1.0:  # Akım 1A'nın altına düştü
                self.charging_phase = ChargingPhase.FLOAT
                self.logger.info("Float aşamasına geçildi")

        elif self.charging_phase == ChargingPhase.FLOAT:
            # Float aşaması
            if reading.state_of_charge >= 99:
                self.charging_phase = ChargingPhase.COMPLETED
                self.logger.info("Şarj tamamlandı")

    def _add_to_history(self, reading: BatteryReading):
        """Geçmişe kayıt ekle"""
        self.reading_history.append(reading)

        # Maksimum boyutu aş
        if len(self.reading_history) > self.max_history_size:
            self.reading_history.pop(0)

    def start_charging(self) -> bool:
        """Şarjı başlat"""
        if not self.is_connected_to_charger:
            self.logger.error("Şarj cihazına bağlı değil")
            return False

        self.is_charging = True
        self.charging_phase = ChargingPhase.BULK
        self.total_charge_cycles += 1

        self.logger.info("Şarj başlatıldı")
        return True

    def stop_charging(self):
        """Şarjı durdur"""
        self.is_charging = False
        self.charging_phase = ChargingPhase.BULK
        self.logger.info("Şarj durduruldu")

    def connect_charger(self):
        """Şarj cihazı bağlandı"""
        self.is_connected_to_charger = True
        self.logger.info("Şarj cihazı bağlandı")

    def disconnect_charger(self):
        """Şarj cihazı bağlantısı kesildi"""
        self.is_connected_to_charger = False
        self.is_charging = False
        self.logger.info("Şarj cihazı bağlantısı kesildi")

    def register_power_consumer(
        self, component: str, current_draw: float, efficiency: float = 100
    ):
        """Güç tüketicisi kaydet"""
        power = current_draw * self.battery_voltage_nominal * (efficiency / 100)

        self.power_consumers[component] = PowerConsumption(
            component=component,
            current_draw=current_draw,
            power=power,
            efficiency=efficiency,
        )

        self._update_total_consumption()
        self.logger.info(f"Güç tüketicisi kaydedildi: {component} ({power:.1f}W)")

    def unregister_power_consumer(self, component: str):
        """Güç tüketicisini kaldır"""
        if component in self.power_consumers:
            del self.power_consumers[component]
            self._update_total_consumption()
            self.logger.info(f"Güç tüketicisi kaldırıldı: {component}")

    def _update_total_consumption(self):
        """Toplam güç tüketimini güncelle"""
        self.total_power_consumption = sum(
            consumer.power for consumer in self.power_consumers.values()
        )

    def get_battery_level(self) -> float:
        """Batarya seviyesi %"""
        if self.current_reading:
            return self.current_reading.state_of_charge
        return 0.0

    def get_battery_voltage(self) -> float:
        """Batarya voltajı"""
        if self.current_reading:
            return self.current_reading.voltage
        return 0.0

    def get_battery_current(self) -> float:
        """Batarya akımı"""
        if self.current_reading:
            return self.current_reading.current
        return 0.0

    def get_remaining_runtime(self) -> float:
        """Kalan çalışma süresi (dakika)"""
        if not self.current_reading or self.is_charging:
            return 0.0

        soc = self.current_reading.state_of_charge
        usable_capacity = self.battery_capacity * (soc - 15) / 100  # %15'e kadar kullan

        if self.total_power_consumption > 0:
            runtime_hours = usable_capacity / (
                self.total_power_consumption / self.battery_voltage_nominal
            )
            return runtime_hours * 60  # dakikaya çevir

        return 0.0

    def get_charging_time_remaining(self) -> float:
        """Kalan şarj süresi (dakika)"""
        if not self.is_charging or not self.current_reading:
            return 0.0

        current_soc = self.current_reading.state_of_charge
        target_soc = 95  # %95'e kadar şarj et

        remaining_capacity = self.battery_capacity * (target_soc - current_soc) / 100

        if self.charging_current > 0:
            charge_time_hours = remaining_capacity / self.charging_current
            return charge_time_hours * 60  # dakikaya çevir

        return 0.0

    def get_power_status(self) -> Dict[str, Any]:
        """Güç durumu bilgisi"""
        status = {
            "state": self.power_state.value,
            "battery_level": self.get_battery_level(),
            "voltage": self.get_battery_voltage(),
            "current": self.get_battery_current(),
            "is_charging": self.is_charging,
            "charging_phase": self.charging_phase.value if self.is_charging else None,
            "remaining_runtime": self.get_remaining_runtime(),
            "total_power_consumption": self.total_power_consumption,
            "temperature": (
                self.current_reading.temperature if self.current_reading else 0
            ),
            "health": self.battery_health,
        }

        if self.is_charging:
            status["charging_time_remaining"] = self.get_charging_time_remaining()

        return status

    def get_power_consumption_breakdown(self) -> Dict[str, float]:
        """Güç tüketimi dağılımı"""
        return {
            component: consumer.power
            for component, consumer in self.power_consumers.items()
        }

    def get_battery_statistics(self) -> Dict[str, Any]:
        """Batarya istatistikleri"""
        return {
            "total_charge_cycles": self.total_charge_cycles,
            "total_discharge_time": self.total_discharge_time,
            "total_charge_time": self.total_charge_time,
            "battery_health": self.battery_health,
            "readings_count": len(self.reading_history),
        }

    def _save_battery_data(self):
        """Batarya verilerini kaydet"""
        try:
            if not self.reading_history:
                return

            # Son 100 okumanın ortalamasını al
            recent_readings = self.reading_history[-100:]

            data = {
                "timestamp": time.time(),
                "battery_level": self.get_battery_level(),
                "voltage": self.get_battery_voltage(),
                "current": self.get_battery_current(),
                "power_state": self.power_state.value,
                "is_charging": self.is_charging,
                "statistics": self.get_battery_statistics(),
            }

            # CSV dosyasına kaydet
            filename = f"battery_log_{time.strftime('%Y%m%d')}.csv"
            with open(filename, "a", encoding="utf-8") as f:
                if f.tell() == 0:  # Dosya boşsa header ekle
                    f.write(
                        "timestamp,battery_level,voltage,current,power_state,is_charging\n"
                    )

                f.write(
                    f"{data['timestamp']},{data['battery_level']:.2f},"
                    f"{data['voltage']:.2f},{data['current']:.2f},"
                    f"{data['power_state']},{data['is_charging']}\n"
                )

        except Exception as e:
            self.logger.error(f"Batarya veri kaydetme hatası: {e}")

    def emergency_shutdown(self):
        """Acil kapatma"""
        self.logger.critical("ACİL KAPATMA - Düşük batarya")

        # Tüm gereksiz sistemleri kapat
        self.unregister_power_consumer("blade_motor")
        self.unregister_power_consumer("motors")

        # Sadece temel sistemleri çalıştır
        essential_consumers = ["raspberry_pi", "sensors"]
        for component in list(self.power_consumers.keys()):
            if component not in essential_consumers:
                self.unregister_power_consumer(component)


if __name__ == "__main__":
    # Test kodu
    logging.basicConfig(level=logging.INFO)

    power_manager = PowerManager()

    # Test güç tüketicileri
    power_manager.register_power_consumer("test_motor", 2.0, 85)
    power_manager.register_power_consumer("test_sensor", 0.1, 95)

    # İzlemeyi başlat
    power_manager.start_monitoring()

    try:
        for i in range(10):
            status = power_manager.get_power_status()
            print(
                f"Batarya: %{status['battery_level']:.1f}, "
                f"Voltaj: {status['voltage']:.1f}V, "
                f"Durum: {status['state']}"
            )
            time.sleep(2)

    except KeyboardInterrupt:
        pass
    finally:
        power_manager.stop_monitoring()
        print("Güç yönetimi durduruldu")
