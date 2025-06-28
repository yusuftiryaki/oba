#!/usr/bin/env python3
"""
OBA Robot - Otonom Bahçe Asistanı
Ana başlatma dosyası
"""

import os
import sys
import time
import signal
import logging
import threading
from pathlib import Path

# Proje root dizinini path'e ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.main_controller import MainController
from src.navigation.kalman_odometry import KalmanOdometry
from src.navigation.path_planner import PathPlanner
from src.navigation.docking_controller import DockingController
from src.hardware.power_manager import PowerManager
from src.hardware.motor_controller import MotorController
from src.web.web_server import WebServer


class OBArobot:
    """OBA Robot ana sınıfı"""

    def __init__(self, simulate: bool = False):
        self.simulate = simulate
        self.logger = self._setup_logging()

        if self.simulate:
            self.logger.info("OBA Robot simülasyon modunda başlatılıyor...")
        else:
            self.logger.info("OBA Robot gerçek donanım modunda başlatılıyor...")

        # Tüm bileşenler
        self.main_controller = None
        self.power_manager = None
        self.motor_controller = None
        self.odometry = None
        self.path_planner = None
        self.docking_controller = None
        self.web_server = None

        # Durum
        self.running = False
        self.shutdown_requested = False

        # Signal handler'ları ayarla
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _setup_logging(self):
        """Logging sistemini kur"""
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        # Log dizinini oluştur
        log_dir = project_root / "logs"
        log_dir.mkdir(exist_ok=True)

        # Log dosyası
        log_file = log_dir / f"oba_robot_{time.strftime('%Y%m%d')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
        )

        return logging.getLogger("OBArobot")

    def _signal_handler(self, signum, frame):
        """Signal handler - graceful shutdown"""
        self.logger.info(f"Signal {signum} alındı, graceful shutdown başlatılıyor...")
        self.shutdown_requested = True

    def initialize_components(self):
        """Tüm bileşenleri başlat"""
        try:
            self.logger.info("Bileşenler başlatılıyor...")

            # Güç yönetimi (ilk başlatılmalı)
            self.logger.info("Güç yönetimi başlatılıyor...")
            self.power_manager = PowerManager(simulate=self.simulate)
            self.power_manager.start_monitoring()

            # Motor kontrolcü
            self.logger.info("Motor kontrolcü başlatılıyor...")
            self.motor_controller = MotorController(simulate=self.simulate)
            self.motor_controller.start_monitoring()

            # Odometri
            self.logger.info("Odometri sistemi başlatılıyor...")
            self.odometry = KalmanOdometry(simulate=self.simulate)

            # Rota planlayıcı
            self.logger.info("Rota planlayıcı başlatılıyor...")
            self.path_planner = PathPlanner()

            # Docking kontrolcü
            self.logger.info("Docking kontrolcü başlatılıyor...")
            self.docking_controller = DockingController(simulate=self.simulate)

            # Ana kontrolcü (tüm diğerleri hazır olduktan sonra)
            self.logger.info("Ana kontrolcü başlatılıyor...")
            self.main_controller = MainController(simulate=self.simulate)
            self.main_controller.initialize_modules()

            # Web server
            self.logger.info("Web server başlatılıyor...")
            self.web_server = WebServer()
            self.web_server.set_robot_controllers(
                self.main_controller,
                self.motor_controller,
                self.power_manager,
                self.path_planner,
            )

            self.logger.info("Tüm bileşenler başarıyla başlatıldı")
            return True

        except Exception as e:
            self.logger.error(f"Bileşen başlatma hatası: {e}")
            return False

    def start(self):
        """Robot sistemini başlat"""
        if not self.initialize_components():
            self.logger.error("Bileşenler başlatılamadı, çıkılıyor...")
            return False

        self.running = True

        # Ana kontrolcüyü başlat
        self.main_controller.start()

        # Web server'ı ayrı thread'de başlat
        web_thread = threading.Thread(target=self.web_server.start, daemon=True)
        web_thread.start()

        self.logger.info("OBA Robot tamamen başlatıldı ve çalışıyor")

        # Ana döngü
        try:
            while self.running and not self.shutdown_requested:
                # Sistem durumunu kontrol et
                self._system_health_check()

                # Güvenlik kontrolleri
                self._safety_checks()

                time.sleep(1)  # 1 saniye bekle

        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt alındı")
        except Exception as e:
            self.logger.error(f"Ana döngü hatası: {e}")

        # Shutdown
        self.shutdown()
        return True

    def _system_health_check(self):
        """Sistem sağlığını kontrol et"""
        try:
            # Batarya kontrolü
            if self.power_manager:
                battery_level = self.power_manager.get_battery_level()
                if battery_level < 5:  # %5'in altında kritik
                    self.logger.critical("KRİTİK BATARYA SEVİYESİ - Acil kapatma!")
                    self.power_manager.emergency_shutdown()
                    self.shutdown_requested = True

            # Bileşen durumlarını kontrol et
            components_ok = all(
                [
                    self.main_controller and self.main_controller.running,
                    self.power_manager and self.power_manager.monitoring_active,
                    self.motor_controller and self.motor_controller.monitoring_active,
                ]
            )

            if not components_ok:
                self.logger.warning("Bazı bileşenler düzgün çalışmıyor")

        except Exception as e:
            self.logger.error(f"Sistem sağlık kontrolü hatası: {e}")

    def _safety_checks(self):
        """Güvenlik kontrolleri"""
        try:
            # Emergency stop kontrolü
            if self.main_controller and self.main_controller.emergency_stop:
                # Emergency stop aktifken hiçbir hareket yapma
                if self.motor_controller:
                    self.motor_controller.stop_all()

            # Maksimum çalışma süresi kontrolü (8 saat)
            if hasattr(self.main_controller, "stats"):
                runtime = self.main_controller.stats.get("total_runtime", 0)
                if runtime > 8 * 3600:  # 8 saat
                    self.logger.warning(
                        "Maksimum çalışma süresi aşıldı, şarja dönülüyor"
                    )
                    if self.main_controller.state.value != "charging":
                        self.main_controller.state = (
                            self.main_controller.RobotState.RETURNING_TO_CHARGE
                        )

        except Exception as e:
            self.logger.error(f"Güvenlik kontrolü hatası: {e}")

    def shutdown(self):
        """Sistemi güvenli şekilde kapat"""
        self.logger.info("Sistem kapatılıyor...")

        self.running = False

        # Acil durumda tüm motorları durdur
        if self.motor_controller:
            self.motor_controller.emergency_stop()
            self.motor_controller.stop_monitoring()

        # Ana kontrolcüyü durdur
        if self.main_controller:
            self.main_controller.stop()

        # Web server'ı durdur
        if self.web_server:
            self.web_server.stop()

        # Güç yönetimini durdur (son olarak)
        if self.power_manager:
            self.power_manager.stop_monitoring()

        self.logger.info("Sistem güvenli şekilde kapatıldı")

    def status(self):
        """Sistem durumunu yazdır"""
        print("=" * 50)
        print("OBA Robot Sistem Durumu")
        print("=" * 50)

        if self.main_controller:
            status = self.main_controller.get_status()
            print(f"Robot Durumu: {status['state']}")
            print(f"Batarya: %{status['battery_level']:.1f}")
            print(
                f"Pozisyon: X:{status['position']['x']:.2f}, Y:{status['position']['y']:.2f}"
            )
            print(f"Çalışma Süresi: {status['uptime']:.1f} saniye")
            print(f"Biçme Süresi: {status['mowing_time']:.1f} saniye")
            print(f"Şarj Döngüleri: {status['charging_cycles']}")

        if self.power_manager:
            power_stats = self.power_manager.get_battery_statistics()
            print(f"Toplam Şarj Döngüsü: {power_stats['total_charge_cycles']}")
            print(f"Batarya Sağlığı: %{power_stats['battery_health']:.1f}")

        if self.motor_controller:
            motor_status = self.motor_controller.get_all_motor_status()
            print("Motor Durumları:")
            for motor, status in motor_status.items():
                print(f"  {motor}: {status['state']} ({status['rpm']:.1f} RPM)")

        print("=" * 50)


def main():
    """Ana fonksiyon"""
    import argparse

    parser = argparse.ArgumentParser(description="OBA Robot - Otonom Bahçe Asistanı")
    parser.add_argument(
        "--config",
        "-c",
        default="config/config.json",
        help="Konfigürasyon dosyası yolu",
    )
    parser.add_argument(
        "--status", "-s", action="store_true", help="Sadece durumu göster"
    )
    parser.add_argument("--test", "-t", action="store_true", help="Test modu")
    parser.add_argument(
        "--web-only", "-w", action="store_true", help="Sadece web arayüzünü başlat"
    )
    parser.add_argument("--debug", "-d", action="store_true", help="Debug modu")
    parser.add_argument(
        "--simulate",
        "--sim",
        action="store_true",
        help="Simülasyon modu (gerçek donanım olmadan çalıştır)",
    )

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Robot instance oluştur
    robot = OBArobot(simulate=args.simulate)

    if args.status:
        # Sadece durum göster
        robot.status()
        return

    if args.test:
        # Test modu
        print("Test modu - geliştirme aşamasında...")
        return

    if args.web_only:
        # Sadece web arayüzü
        from src.web.web_server import WebServer

        web_server = WebServer()
        try:
            web_server.start()
        except KeyboardInterrupt:
            web_server.stop()
        return

    # Normal başlatma
    try:
        success = robot.start()
        if not success:
            print("Robot başlatılamadı!")
            sys.exit(1)
    except Exception as e:
        print(f"Beklenmeyen hata: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
