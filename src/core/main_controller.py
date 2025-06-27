"""
Otonom Bahçe Asistanı (OBA) - Ana Kontrol Modülü
Ana durum makinesini yönetir: Biçme, Şarja Dönme, Şarj Olma, Bekleme
"""

import time
import threading
import logging
from enum import Enum
from typing import Dict, Any
import json


class RobotState(Enum):
    """Robot durumları"""

    IDLE = "idle"
    MOWING = "mowing"
    RETURNING_TO_CHARGE = "returning_to_charge"
    CHARGING = "charging"
    MANUAL_CONTROL = "manual_control"
    ERROR = "error"
    EMERGENCY_STOP = "emergency_stop"


class MainController:
    """Ana kontrol sınıfı - robot durumlarını ve geçişlerini yönetir"""

    def __init__(self, config_path: str = "config/config.json"):
        self.state = RobotState.IDLE
        self.previous_state = RobotState.IDLE
        self.running = False
        self.emergency_stop = False

        # Konfigürasyon yükleme
        self.config = self._load_config(config_path)

        # Diğer modüllerin referansları (lazy loading)
        self.odometry = None
        self.path_planner = None
        self.power_manager = None
        self.docking_controller = None
        self.motor_controller = None

        # İstatistikler
        self.stats = {
            "total_runtime": 0,
            "mowing_time": 0,
            "charging_cycles": 0,
            "area_covered": 0,
            "current_position": {"x": 0, "y": 0, "heading": 0},
        }

        # Logging kurulumu
        self._setup_logging()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Konfigürasyon dosyasını yükle"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logging.warning(f"Config dosyası bulunamadı: {config_path}")
            return self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """Varsayılan konfigürasyon"""
        return {
            "battery": {
                "low_threshold": 20,
                "critical_threshold": 15,
                "full_threshold": 95,
            },
            "mowing": {
                "speed": 0.5,
                "pattern": "lawn_mower",
                "blade_height_levels": [3, 5, 7],
            },
            "charging_station": {
                "position": {"x": 0, "y": 0},
                "detection_range": 100,
                "docking_precision": 0.01,
            },
            "safety": {
                "max_slope": 15,
                "obstacle_detection": True,
                "emergency_stop_enabled": True,
            },
        }

    def _setup_logging(self):
        """Logging sistemini kur"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("oba_robot.log"), logging.StreamHandler()],
        )
        self.logger = logging.getLogger("OBA_MainController")

    def initialize_modules(self):
        """Diğer modülleri başlat"""
        try:
            from ..navigation.kalman_odometry import KalmanOdometry
            from ..navigation.path_planner import PathPlanner
            from ..hardware.power_manager import PowerManager
            from ..navigation.docking_controller import DockingController
            from ..hardware.motor_controller import MotorController

            self.odometry = KalmanOdometry()
            self.path_planner = PathPlanner()
            self.power_manager = PowerManager()
            self.docking_controller = DockingController()
            self.motor_controller = MotorController()

            self.logger.info("Tüm modüller başarıyla başlatıldı")

        except ImportError as e:
            self.logger.error(f"Modül yükleme hatası: {e}")
            self.state = RobotState.ERROR

    def start(self):
        """Ana kontrol döngüsünü başlat"""
        self.running = True
        self.logger.info("OBA Robot başlatılıyor...")

        # Modülleri başlat
        self.initialize_modules()

        # Ana döngü thread'i
        control_thread = threading.Thread(target=self._main_loop, daemon=True)
        control_thread.start()

        self.logger.info("Ana kontrol döngüsü başlatıldı")

    def stop(self):
        """Robotu durdur"""
        self.running = False
        self.logger.info("Robot durduruluyor...")

    def emergency_stop_triggered(self):
        """Acil durdurma"""
        self.emergency_stop = True
        self.previous_state = self.state
        self.state = RobotState.EMERGENCY_STOP
        self.logger.critical("ACİL DURDURMA AKTİF!")

        # Tüm motorları durdur
        if self.motor_controller:
            self.motor_controller.stop_all()

    def clear_emergency_stop(self):
        """Acil durdurma kaldır"""
        if self.emergency_stop:
            self.emergency_stop = False
            self.state = RobotState.IDLE
            self.logger.info("Acil durdurma kaldırıldı")

    def _main_loop(self):
        """Ana kontrol döngüsü"""
        while self.running:
            try:
                if not self.emergency_stop:
                    self._state_machine()
                else:
                    self._handle_emergency_stop()

                # Pozisyon güncelle
                if self.odometry:
                    pos = self.odometry.get_position()
                    self.stats["current_position"] = pos

                time.sleep(0.1)  # 10Hz kontrol döngüsü

            except Exception as e:
                self.logger.error(f"Ana döngü hatası: {e}")
                self.state = RobotState.ERROR
                time.sleep(1)

    def _state_machine(self):
        """Durum makinesi - robot durumlarını yönet"""

        if self.state == RobotState.IDLE:
            self._handle_idle_state()

        elif self.state == RobotState.MOWING:
            self._handle_mowing_state()

        elif self.state == RobotState.RETURNING_TO_CHARGE:
            self._handle_returning_state()

        elif self.state == RobotState.CHARGING:
            self._handle_charging_state()

        elif self.state == RobotState.MANUAL_CONTROL:
            self._handle_manual_control_state()

        elif self.state == RobotState.ERROR:
            self._handle_error_state()

    def _handle_idle_state(self):
        """Bekleme durumu"""
        # Batarya kontrolü
        if self.power_manager:
            battery_level = self.power_manager.get_battery_level()

            # Düşük batarya varsa şarja git
            if battery_level < self.config["battery"]["low_threshold"]:
                self.state = RobotState.RETURNING_TO_CHARGE
                self.logger.info("Batarya düşük, şarja dönülüyor")

    def _handle_mowing_state(self):
        """Biçme durumu"""
        if not self.path_planner or not self.motor_controller:
            return

        # Batarya kontrolü
        battery_level = self.power_manager.get_battery_level()
        if battery_level < self.config["battery"]["low_threshold"]:
            self.state = RobotState.RETURNING_TO_CHARGE
            self.logger.info("Biçme sırasında batarya düştü, şarja dönülüyor")
            return

        # Rota takibi
        current_pos = self.odometry.get_position()
        next_waypoint = self.path_planner.get_next_waypoint(current_pos)

        if next_waypoint:
            # Hedefe doğru hareket et
            self.motor_controller.move_to_waypoint(next_waypoint)
            self.stats["mowing_time"] += 0.1
        else:
            # Görev tamamlandı
            self.state = RobotState.IDLE
            self.logger.info("Biçme görevi tamamlandı")

    def _handle_returning_state(self):
        """Şarja dönme durumu"""
        if not self.docking_controller:
            return

        # Şarj istasyonuna git
        station_pos = self.config["charging_station"]["position"]
        current_pos = self.odometry.get_position()

        # Mesafe hesapla
        distance = (
            (station_pos["x"] - current_pos["x"]) ** 2
            + (station_pos["y"] - current_pos["y"]) ** 2
        ) ** 0.5

        if distance > self.config["charging_station"]["docking_precision"]:
            # İstasyona doğru hareket et
            self.motor_controller.move_to_position(station_pos)
        else:
            # Docking işlemi
            if self.docking_controller.dock_to_station():
                self.state = RobotState.CHARGING
                self.logger.info("Şarj istasyonuna başarıyla bağlanıldı")

    def _handle_charging_state(self):
        """Şarj durumu"""
        if not self.power_manager:
            return

        battery_level = self.power_manager.get_battery_level()

        if battery_level >= self.config["battery"]["full_threshold"]:
            self.state = RobotState.IDLE
            self.stats["charging_cycles"] += 1
            self.logger.info("Şarj tamamlandı")

    def _handle_manual_control_state(self):
        """Manuel kontrol durumu"""
        # Web arayüzünden gelen komutları işle
        pass

    def _handle_error_state(self):
        """Hata durumu"""
        self.logger.error("Robot hata durumunda")
        time.sleep(5)  # 5 saniye bekle
        self.state = RobotState.IDLE  # İdeal duruma dön

    def _handle_emergency_stop(self):
        """Acil durdurma durumu"""
        # Tüm hareketleri durdur
        if self.motor_controller:
            self.motor_controller.stop_all()

        time.sleep(0.5)

    def start_mowing_task(self, area_id: str):
        """Biçme görevini başlat"""
        if self.state in [RobotState.IDLE, RobotState.MANUAL_CONTROL]:
            if self.path_planner:
                self.path_planner.load_area(area_id)
                self.state = RobotState.MOWING
                self.logger.info(f"Biçme görevi başlatıldı: {area_id}")
                return True
        return False

    def set_manual_control(self, enabled: bool):
        """Manuel kontrol modunu aç/kapat"""
        if enabled and self.state != RobotState.EMERGENCY_STOP:
            self.previous_state = self.state
            self.state = RobotState.MANUAL_CONTROL
            self.logger.info("Manuel kontrol modu aktif")
        elif not enabled and self.state == RobotState.MANUAL_CONTROL:
            self.state = RobotState.IDLE
            self.logger.info("Manuel kontrol modu kapatıldı")

    def get_status(self) -> Dict[str, Any]:
        """Robot durumunu döndür"""
        battery_level = 0
        if self.power_manager:
            battery_level = self.power_manager.get_battery_level()

        return {
            "state": self.state.value,
            "battery_level": battery_level,
            "position": self.stats["current_position"],
            "emergency_stop": self.emergency_stop,
            "uptime": self.stats["total_runtime"],
            "mowing_time": self.stats["mowing_time"],
            "charging_cycles": self.stats["charging_cycles"],
        }


if __name__ == "__main__":
    # Test için
    controller = MainController()
    controller.start()

    try:
        while True:
            status = controller.get_status()
            print(f"Robot Durumu: {status['state']}")
            time.sleep(2)
    except KeyboardInterrupt:
        controller.stop()
        print("Robot durduruldu")
