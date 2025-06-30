"""
Web Server Modülü
Uzaktan kontrol ve izleme için web arayüzü sunar
"""

import os
import json
import time
import logging
import subprocess
import threading
from typing import Dict, Any, Optional
from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO, emit
import base64
import io

try:
    import cv2

    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


class WebServer:
    """Web server sınıfı - Flask tabanlı"""

    def __init__(self, host: str = "0.0.0.0", port: int = 5000):
        self.logger = logging.getLogger("WebServer")

        # Flask uygulaması
        self.app = Flask(__name__, template_folder="templates", static_folder="static")
        self.app.config["SECRET_KEY"] = "oba_robot_secret_key_2025"

        # SocketIO for real-time communication
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        # Server parametreleri
        self.host = host
        self.port = port
        self.running = False

        # Robot bileşenlerine referanslar
        self.main_controller = None
        self.motor_controller = None
        self.power_manager = None
        self.path_planner = None

        # Kamera stream
        self.camera_enabled = False
        self.stream_quality = "medium"  # low, medium, high

        # Manuel kontrol
        self.manual_control_active = False
        self.last_manual_command_time = 0
        self.manual_timeout = 2.0  # saniye

        # İstatistikler
        self.connected_clients = 0
        self.total_requests = 0
        self.server_start_time = time.time()

        self._setup_routes()
        self._setup_socket_events()

    def set_robot_controllers(
        self, main_controller, motor_controller, power_manager, path_planner
    ):
        """Robot kontrolcü referanslarını ayarla"""
        self.main_controller = main_controller
        self.motor_controller = motor_controller
        self.power_manager = power_manager
        self.path_planner = path_planner
        self.logger.info("Robot kontrolcüleri web server'a bağlandı")

    def _setup_routes(self):
        """Web rotalarını ayarla"""

        @self.app.route("/")
        def index():
            """Ana sayfa"""
            return render_template("index.html")

        @self.app.route("/control")
        def control_panel():
            """Kontrol paneli"""
            return render_template("control.html")

        @self.app.route("/monitoring")
        def monitoring():
            """İzleme paneli"""
            return render_template("monitoring.html")

        @self.app.route("/areas")
        def areas():
            """Alan yönetimi"""
            return render_template("areas.html")

        @self.app.route("/settings")
        def settings():
            """Ayarlar"""
            return render_template("settings.html")

        # API endpoints
        @self.app.route("/api/status")
        def api_status():
            """Robot durum bilgisi"""
            self.total_requests += 1

            status = {
                "timestamp": time.time(),
                "connected": True,
                "robot": self._get_robot_status(),
                "server": self._get_server_status(),
            }
            return jsonify(status)

        @self.app.route("/api/power")
        def api_power():
            """Güç durumu"""
            if self.power_manager:
                return jsonify(self.power_manager.get_power_status())
            return jsonify({"error": "Power manager not available"}), 503

        @self.app.route("/api/motors")
        def api_motors():
            """Motor durumları"""
            if self.motor_controller:
                return jsonify(self.motor_controller.get_all_motor_status())
            return jsonify({"error": "Motor controller not available"}), 503

        @self.app.route("/api/areas")
        def api_areas():
            """Alan listesi"""
            if self.path_planner:
                return jsonify(self.path_planner.get_areas())
            return jsonify({"error": "Path planner not available"}), 503

        @self.app.route("/api/areas/<area_id>/start", methods=["POST"])
        def api_start_mowing(area_id):
            """Biçme görevini başlat"""
            if self.main_controller:
                success = self.main_controller.start_mowing_task(area_id)
                return jsonify({"success": success})
            return jsonify({"error": "Main controller not available"}), 503

        @self.app.route("/api/tasks/start_mowing", methods=["POST"])
        def api_tasks_start_mowing():
            """Web arayüzü için biçme görevini başlat (alan ID'siz)"""
            if self.main_controller:
                # Varsayılan veya ilk alanı kullan
                area_id = None
                if self.path_planner and self.path_planner.areas:
                    area_id = next(iter(self.path_planner.areas.keys()))
                if not area_id:
                    return (
                        jsonify(
                            {"success": False, "error": "Hiçbir alan tanımlı değil"}
                        ),
                        400,
                    )
                success = self.main_controller.start_mowing_task(area_id)
                return jsonify({"success": success})
            return (
                jsonify({"success": False, "error": "Main controller not available"}),
                503,
            )

        @self.app.route("/api/areas", methods=["POST"])
        def api_create_area():
            """Yeni alan oluştur"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"success": False, "error": "No data provided"}), 400

                area_id = data.get("id")
                name = data.get("name")
                boundary = data.get("boundary", [])

                if not area_id or not name or len(boundary) < 3:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "error": "Missing required fields or invalid boundary",
                            }
                        ),
                        400,
                    )

                if self.path_planner:
                    # Yeni alan objesi oluştur
                    from src.navigation.path_planner import Area, Point, PatternType

                    new_area = Area(
                        id=area_id,
                        name=name,
                        boundary=[Point(p["x"], p["y"]) for p in boundary],
                        obstacles=[],
                        pattern=PatternType(data.get("pattern", "lawn_mower")),
                        blade_height=data.get("blade_height", 5),
                        speed=data.get("speed", 0.5),
                        overlap=data.get("overlap", 0.1),
                    )

                    # Path planner'a ekle
                    self.path_planner.areas[area_id] = new_area
                    self.path_planner._save_areas()

                    self.logger.info(f"Yeni alan oluşturuldu: {area_id}")
                    return jsonify({"success": True, "area_id": area_id})
                else:
                    return (
                        jsonify(
                            {"success": False, "error": "Path planner not available"}
                        ),
                        503,
                    )

            except Exception as e:
                self.logger.error(f"Alan oluşturma hatası: {e}")
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/areas/<area_id>", methods=["PUT"])
        def api_update_area(area_id):
            """Alan güncelle"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"success": False, "error": "No data provided"}), 400

                if self.path_planner and area_id in self.path_planner.areas:
                    area = self.path_planner.areas[area_id]

                    # Alan bilgilerini güncelle
                    if "name" in data:
                        area.name = data["name"]
                    if "blade_height" in data:
                        area.blade_height = data["blade_height"]
                    if "speed" in data:
                        area.speed = data["speed"]
                    if "pattern" in data:
                        from src.navigation.path_planner import PatternType

                        area.pattern = PatternType(data["pattern"])
                    if "boundary" in data:
                        from src.navigation.path_planner import Point

                        area.boundary = [
                            Point(p["x"], p["y"]) for p in data["boundary"]
                        ]

                    # Değişiklikleri kaydet
                    self.path_planner._save_areas()

                    self.logger.info(f"Alan güncellendi: {area_id}")
                    return jsonify({"success": True})
                else:
                    return jsonify({"success": False, "error": "Area not found"}), 404

            except Exception as e:
                self.logger.error(f"Alan güncelleme hatası: {e}")
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/areas/<area_id>", methods=["DELETE"])
        def api_delete_area(area_id):
            """Alan sil"""
            try:
                if self.path_planner and area_id in self.path_planner.areas:
                    del self.path_planner.areas[area_id]
                    self.path_planner._save_areas()

                    self.logger.info(f"Alan silindi: {area_id}")
                    return jsonify({"success": True})
                else:
                    return jsonify({"success": False, "error": "Area not found"}), 404

            except Exception as e:
                self.logger.error(f"Alan silme hatası: {e}")
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/areas/<area_id>", methods=["GET"])
        def api_get_area(area_id):
            """Tek alan detayını getir"""
            try:
                if self.path_planner and area_id in self.path_planner.areas:
                    area = self.path_planner.areas[area_id]
                    area_data = {
                        "id": area.id,
                        "name": area.name,
                        "boundary": [{"x": p.x, "y": p.y} for p in area.boundary],
                        "obstacles": [
                            [{"x": p.x, "y": p.y} for p in obs]
                            for obs in (area.obstacles or [])
                        ],
                        "pattern": area.pattern.value,
                        "blade_height": area.blade_height,
                        "speed": area.speed,
                        "overlap": area.overlap,
                    }
                    return jsonify(area_data)
                else:
                    return jsonify({"error": "Area not found"}), 404

            except Exception as e:
                self.logger.error(f"Alan getirme hatası: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/areas/<area_id>/stop", methods=["POST"])
        def api_stop_mowing_area(area_id):
            """Biçme görevini durdur"""
            try:
                if self.main_controller:
                    # Robotu IDLE durumuna geçir
                    from src.core.main_controller import RobotState

                    self.main_controller.state = RobotState.IDLE

                    # Motorları durdur
                    if self.motor_controller:
                        self.motor_controller.stop_all()

                    self.logger.info(f"Biçme görevi durduruldu: {area_id}")
                    return jsonify({"success": True})
                else:
                    return (
                        jsonify(
                            {"success": False, "error": "Main controller not available"}
                        ),
                        503,
                    )

            except Exception as e:
                self.logger.error(f"Biçme durdurma hatası: {e}")
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/tasks/pause", methods=["POST"])
        def api_pause_mowing():
            """Biçme görevini duraklat"""
            try:
                if self.main_controller:
                    # Robotu PAUSED durumuna geçir
                    from src.core.main_controller import RobotState

                    # Mevcut durumu kontrol et
                    if hasattr(self.main_controller, "state"):
                        if self.main_controller.state == RobotState.MOWING:
                            self.main_controller.state = RobotState.PAUSED

                            # Motorları geçici olarak durdur
                            if self.motor_controller:
                                self.motor_controller.stop_movement()

                            self.logger.info("Biçme görevi duraklatıldı")
                            return jsonify(
                                {"success": True, "message": "Biçme duraklatıldı"}
                            )
                        else:
                            return jsonify(
                                {"success": False, "error": "Robot biçme yapmıyor"}
                            )
                    else:
                        return jsonify(
                            {"success": False, "error": "Robot durumu bulunamadı"}
                        )
                else:
                    return jsonify(
                        {"success": False, "error": "Main controller bulunamadı"}
                    )
            except Exception as e:
                self.logger.error(f"Biçme duraklama hatası: {e}")
                return jsonify({"success": False, "error": str(e)})

        @self.app.route("/api/tasks/stop", methods=["POST"])
        def api_stop_mowing_task():
            """Biçme görevini durdur"""
            try:
                if self.main_controller:
                    # Robotu IDLE durumuna geçir
                    from src.core.main_controller import RobotState

                    self.main_controller.state = RobotState.IDLE

                    # Tüm motorları durdur
                    if self.motor_controller:
                        self.motor_controller.stop_all()

                    self.logger.info("Biçme görevi durduruldu")
                    return jsonify({"success": True, "message": "Biçme durduruldu"})
                else:
                    return jsonify(
                        {"success": False, "error": "Main controller bulunamadı"}
                    )
            except Exception as e:
                self.logger.error(f"Biçme durdurma hatası: {e}")
                return jsonify({"success": False, "error": str(e)})

        @self.app.route("/api/logs")
        def api_logs():
            """Sistem loglarını getir"""
            try:
                # Son 100 log girişini getir
                log_entries = []
                log_file = "logs/oba_robot.log"

                if os.path.exists(log_file):
                    with open(log_file, "r") as f:
                        lines = f.readlines()
                        # Son 100 satır
                        for line in lines[-100:]:
                            if line.strip():
                                log_entries.append(line.strip())

                return jsonify({"logs": log_entries})
            except Exception as e:
                return jsonify({"error": str(e), "logs": []})

        @self.app.route("/api/navigation")
        def api_navigation():
            """Profesyonel navigasyon verileri (GPS+IMU+LiDAR+Odometry)"""
            try:
                from ..hardware.sensor_manager import get_sensor_manager

                sensor_manager = get_sensor_manager()
                nav_data = sensor_manager.get_navigation_data()

                return jsonify(
                    {"success": True, "navigation": nav_data, "timestamp": time.time()}
                )
            except Exception as e:
                self.logger.error(f"Navigation API hatası: {e}")
                return jsonify({"success": False, "error": str(e), "navigation": None})

        @self.app.route("/video_feed")
        def video_feed():
            """Kamera video stream"""
            if self.camera_enabled:
                return Response(
                    self._generate_video_stream(),
                    mimetype="multipart/x-mixed-replace; boundary=frame",
                )
            else:
                return "Camera not enabled", 503

        @self.app.route("/api/stats/realtime")
        def api_stats_realtime():
            """Anlık robot ve sistem durumu (eski frontend uyumluluğu için)"""
            return api_status()

        @self.app.route("/api/emergency_stop", methods=["POST"])
        def api_emergency_stop():
            """Acil durdurma komutu"""
            if self.main_controller:
                try:
                    self.main_controller.emergency_stop()
                    return jsonify({"success": True})
                except Exception as e:
                    self.logger.error(f"Acil durdurma hatası: {e}")
                    return jsonify({"success": False, "error": str(e)}), 500
            return (
                jsonify({"success": False, "error": "Main controller not available"}),
                503,
            )

        @self.app.route("/api/clear_emergency", methods=["POST"])
        def api_clear_emergency():
            """Acil durdurmayı kaldır"""
            if self.main_controller:
                try:
                    self.main_controller.clear_emergency_stop()
                    return jsonify({"success": True})
                except Exception as e:
                    self.logger.error(f"Acil durdurma kaldırma hatası: {e}")
                    return jsonify({"success": False, "error": str(e)}), 500
            return (
                jsonify({"success": False, "error": "Main controller not available"}),
                503,
            )

        @self.app.route("/api/return_home", methods=["POST"])
        def api_return_home():
            """Robotu şarj istasyonuna döndür"""
            if self.main_controller and hasattr(
                self.main_controller, "return_to_home_task"
            ):
                try:
                    success = self.main_controller.return_to_home_task()
                    return jsonify({"success": success})
                except Exception as e:
                    self.logger.error(f"Şarja dönme hatası: {e}")
                    return jsonify({"success": False, "error": str(e)}), 500
            return (
                jsonify(
                    {"success": False, "error": "Main controller veya fonksiyon yok"}
                ),
                503,
            )

    def _setup_socket_events(self):
        """SocketIO olaylarını ayarla"""

        @self.socketio.on("connect")
        def handle_connect():
            self.connected_clients += 1
            self.logger.info(f"Client bağlandı. Toplam: {self.connected_clients}")
            emit("status", {"message": "Connected to OBA Robot"})

        @self.socketio.on("disconnect")
        def handle_disconnect():
            self.connected_clients -= 1
            self.logger.info(
                f"Client bağlantısı kesildi. Kalan: {self.connected_clients}"
            )

        @self.socketio.on("request_status")
        def handle_status_request():
            """Durum bilgisi istendi"""
            status = self._get_robot_status()
            emit("robot_status", status)

        @self.socketio.on("manual_control")
        def handle_manual_control(data):
            """Manuel kontrol komutu"""
            if not self.manual_control_active:
                self._activate_manual_control()

            linear = data.get("linear", 0.0)
            angular = data.get("angular", 0.0)

            if self.motor_controller:
                self.motor_controller.move(linear, angular)
                self.last_manual_command_time = time.time()
                emit("control_ack", {"success": True})
            else:
                emit(
                    "control_ack",
                    {"success": False, "error": "Motor controller not available"},
                )

        @self.socketio.on("start_camera")
        def handle_start_camera():
            """Kamera streaming başlat"""
            self.camera_enabled = True
            emit("camera_status", {"enabled": True})

        @self.socketio.on("stop_camera")
        def handle_stop_camera():
            """Kamera streaming durdur"""
            self.camera_enabled = False
            emit("camera_status", {"enabled": False})

    def _activate_manual_control(self):
        """Manuel kontrol modunu aktifleştir"""
        if self.main_controller:
            self.main_controller.set_manual_control(True)
            self.manual_control_active = True

            # Timeout timer başlat
            def manual_control_timeout():
                while self.manual_control_active:
                    if (
                        time.time() - self.last_manual_command_time
                        > self.manual_timeout
                    ):
                        self._deactivate_manual_control()
                        break
                    time.sleep(0.5)

            threading.Thread(target=manual_control_timeout, daemon=True).start()

    def _deactivate_manual_control(self):
        """Manuel kontrol modunu deaktifleştir"""
        if self.main_controller:
            self.main_controller.set_manual_control(False)
            self.manual_control_active = False

            # Hareketi durdur
            if self.motor_controller:
                self.motor_controller.move(0, 0)

    def _get_robot_status(self) -> Dict[str, Any]:
        """Robot durum bilgisini topla"""
        status = {
            "timestamp": time.time(),
            "main_controller": None,
            "power": None,
            "motors": None,
            "navigation": None,
        }

        if self.main_controller:
            status["main_controller"] = self.main_controller.get_status()

        if self.power_manager:
            status["power"] = self.power_manager.get_power_status()

        if self.motor_controller:
            status["motors"] = self.motor_controller.get_all_motor_status()
            status["robot_velocity"] = self.motor_controller.get_robot_velocity()

        if self.path_planner:
            status["navigation"] = self.path_planner.get_progress()

        return status

    def _get_server_status(self) -> Dict[str, Any]:
        """Server durum bilgisi"""
        uptime = time.time() - self.server_start_time

        return {
            "uptime": uptime,
            "connected_clients": self.connected_clients,
            "total_requests": self.total_requests,
            "manual_control_active": self.manual_control_active,
            "camera_enabled": self.camera_enabled,
        }

    def _get_wifi_signal_strength(self) -> int:
        """WiFi sinyal gücünü dBm cinsinden al"""
        try:
            # Linux'ta iwconfig kullanarak WiFi sinyal gücünü al
            result = subprocess.run(
                ["iwconfig"], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                lines = result.stdout.split("\n")
                for line in lines:
                    if "Signal level=" in line:
                        # "Signal level=-45 dBm" formatından değer çıkar
                        import re

                        match = re.search(r"Signal level=(-?\d+)", line)
                        if match:
                            return int(match.group(1))

            # iwconfig başarısız olursa /proc/net/wireless dene
            try:
                with open("/proc/net/wireless", "r") as f:
                    lines = f.readlines()
                    if len(lines) > 2:  # Header'ları atla
                        data = lines[2].split()
                        if len(data) > 3:
                            # Link quality değerini dBm'e dönüştür (yaklaşık)
                            link_quality = float(data[2])
                            # Yaklaşık: 0-70 range -> -90 to -30 dBm
                            signal_dbm = int(-90 + (link_quality * 60 / 70))
                            return signal_dbm
            except (FileNotFoundError, IndexError, ValueError):
                pass

        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            FileNotFoundError,
        ):
            pass

        # Hiçbiri çalışmazsa geliştirme ortamı değeri döndür
        return -45  # Geliştirme ortamı için varsayılan değer

    def _get_wifi_status_text(self, signal_dbm: int) -> str:
        """WiFi sinyal gücüne göre durum metni"""
        if signal_dbm >= -50:
            return "Mükemmel"
        elif signal_dbm >= -60:
            return "Güçlü"
        elif signal_dbm >= -70:
            return "Orta"
        elif signal_dbm >= -80:
            return "Zayıf"
        else:
            return "Çok Zayıf"

    def _get_system_metrics(self) -> Dict[str, Any]:
        """Sistem metriklerini al"""
        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # WiFi sinyal gücü al
            wifi_signal_dbm = self._get_wifi_signal_strength()
            wifi_status = self._get_wifi_status_text(wifi_signal_dbm)

            return {
                "health": 95 if cpu_percent < 80 and memory.percent < 80 else 75,
                "cpu_usage": round(cpu_percent, 1),
                "memory_usage": round(memory.percent, 1),
                "disk_usage": round(disk.percent, 1),
                "network_status": wifi_status,
                "wifi_signal_dbm": wifi_signal_dbm,
            }
        except ImportError:
            # psutil yoksa simulated data
            return {
                "health": 95,
                "cpu_usage": 12.5,
                "memory_usage": 45.2,
                "disk_usage": 67.8,
                "network_status": "Güçlü",
                "wifi_signal_dbm": -45,
            }

    def _get_sensor_data(self) -> Dict[str, Any]:
        """Sensör verilerini al - Yeni sensor_manager kullanarak"""
        try:
            # Sensor manager'dan veri al
            from src.hardware.sensor_manager import get_sensor_manager

            sensor_manager = get_sensor_manager()
            sensor_data = sensor_manager.get_sensor_data()

            # Default değerlerle birleştir
            return {
                "temperature": sensor_data.get("temperature", 25.0),
                "humidity": sensor_data.get("humidity", 60.0),
                "distance": sensor_data.get("distance", 50.0),
                "heading": sensor_data.get("heading", 180.0),
                "inclination": sensor_data.get("inclination", 0.0),
                "gps_satellites": sensor_data.get("gps_satellites", 8),
                "imu_temperature": sensor_data.get("imu_temperature", 35.0),
                "imu_calibration": sensor_data.get("imu_calibration", "GOOD"),
                "gps_fix": sensor_data.get("gps_fix", True),
            }

        except Exception as e:
            self.logger.error("Sensör verisi alma hatası: %s", e)
            # Fallback simülasyon verileri
            import random

            return {
                "temperature": round(20 + random.uniform(-5, 15), 1),
                "humidity": round(50 + random.uniform(-20, 30), 1),
                "distance": round(30 + random.uniform(-20, 50), 1),
                "heading": round(random.uniform(0, 360), 1),
                "inclination": round(random.uniform(-10, 10), 1),
                "gps_satellites": random.randint(6, 12),
                "imu_temperature": round(random.uniform(30, 40), 1),
                "imu_calibration": random.choice(["GOOD", "FAIR", "POOR"]),
                "gps_fix": random.choice([True, False]),
            }

    def _get_detailed_motor_status(self) -> Dict[str, Any]:
        """Detaylı motor durumları - gerçek veriler kullan"""
        if not self.motor_controller:
            return {}

        try:
            base_status = self.motor_controller.get_all_motor_status()

            # Geliştirme ortamı kontrolü
            is_development = os.getenv("ROBOT_HARDWARE") != "true"

            result = {}

            # Sol motor (left_drive)
            if "left_drive" in base_status:
                left_data = base_status["left_drive"]
                result["left"] = {
                    "speed": left_data.get("rpm", 0),
                    "current": left_data.get("current", 0.0),
                    "encoder_position": left_data.get("encoder_position", 0),
                    "state": left_data.get("state", "stopped"),
                    "error_code": left_data.get("error_code", 0),
                }

                # Yük hesapla (akım bazlı)
                max_current = 5.0  # Motor maksimum akımı
                load_percent = min(100, (result["left"]["current"] / max_current) * 100)
                result["left"]["load"] = round(load_percent, 1)

                # Geliştirme ortamında simüle değerler ekle
                if is_development:
                    import random

                    result["left"]["current"] = round(random.uniform(0.5, 3.0), 2)
                    result["left"]["load"] = round(random.uniform(10, 80), 1)

            # Sağ motor (right_drive)
            if "right_drive" in base_status:
                right_data = base_status["right_drive"]
                result["right"] = {
                    "speed": right_data.get("rpm", 0),
                    "current": right_data.get("current", 0.0),
                    "encoder_position": right_data.get("encoder_position", 0),
                    "state": right_data.get("state", "stopped"),
                    "error_code": right_data.get("error_code", 0),
                }

                # Yük hesapla
                load_percent = min(
                    100, (result["right"]["current"] / max_current) * 100
                )
                result["right"]["load"] = round(load_percent, 1)

                # Geliştirme ortamında simüle değerler
                if is_development:
                    import random

                    result["right"]["current"] = round(random.uniform(0.5, 3.0), 2)
                    result["right"]["load"] = round(random.uniform(10, 80), 1)

            # Biçme motoru (cutting_blade)
            if "cutting_blade" in base_status:
                blade_data = base_status["cutting_blade"]
                result["blade"] = {
                    "speed": blade_data.get("rpm", 0),
                    "current": blade_data.get("current", 0.0),
                    "state": blade_data.get("state", "stopped"),
                    "enabled": blade_data.get("state", "stopped") == "running",
                    "error_code": blade_data.get("error_code", 0),
                }

                # Geliştirme ortamında simüle değerler
                if is_development:
                    import random

                    result["blade"]["current"] = round(random.uniform(1.0, 5.0), 2)

            return result

        except Exception as e:
            self.logger.error(f"Motor status error: {e}")
            # Hata durumunda varsayılan değerler
            import random

            return {
                "left": {
                    "speed": 0,
                    "current": round(random.uniform(0.5, 3.0), 2),
                    "load": round(random.uniform(10, 80), 1),
                    "state": "stopped",
                },
                "right": {
                    "speed": 0,
                    "current": round(random.uniform(0.5, 3.0), 2),
                    "load": round(random.uniform(10, 80), 1),
                    "state": "stopped",
                },
                "blade": {
                    "speed": 0,
                    "current": round(random.uniform(1.0, 5.0), 2),
                    "enabled": False,
                    "state": "stopped",
                },
            }

    def _get_real_battery_data(self) -> Dict[str, Any]:
        """Gerçek batarya verilerini sistem dosyalarından al"""
        try:
            battery_data = {
                "level": 85,  # Default
                "voltage": 12.6,
                "current": 2.3,
                "temperature": 25,
                "health": "GOOD",
            }

            # Linux'ta power_supply sisteminden batarya bilgilerini al
            try:
                # Ana batarya (BAT0 veya BAT1)
                for bat_num in ["0", "1"]:
                    bat_path = f"/sys/class/power_supply/BAT{bat_num}"
                    if os.path.exists(bat_path):
                        # Batarya seviyesi (%)
                        capacity_file = f"{bat_path}/capacity"
                        if os.path.exists(capacity_file):
                            with open(capacity_file, "r") as f:
                                battery_data["level"] = int(f.read().strip())

                        # Voltaj (µV -> V)
                        voltage_file = f"{bat_path}/voltage_now"
                        if os.path.exists(voltage_file):
                            with open(voltage_file, "r") as f:
                                voltage_uv = int(f.read().strip())
                                battery_data["voltage"] = round(voltage_uv / 1000000, 2)

                        # Akım (µA -> A)
                        current_file = f"{bat_path}/current_now"
                        if os.path.exists(current_file):
                            with open(current_file, "r") as f:
                                current_ua = int(f.read().strip())
                                battery_data["current"] = round(
                                    abs(current_ua) / 1000000, 2
                                )

                        # Batarya sağlığı
                        health_file = f"{bat_path}/health"
                        if os.path.exists(health_file):
                            with open(health_file, "r") as f:
                                battery_data["health"] = f.read().strip()

                        break  # İlk bulunan bataryayı kullan

            except (FileNotFoundError, ValueError, PermissionError):
                pass

            # Eğer sistem bataryası bulunamazsa, UPS/External power source dene
            try:
                # UPS verisi (örnek: APC UPS)
                result = subprocess.run(
                    ["apcaccess", "status"], capture_output=True, text=True, timeout=3
                )
                if result.returncode == 0:
                    lines = result.stdout.split("\n")
                    for line in lines:
                        if "BCHARGE" in line:  # Battery charge
                            charge = line.split(":")[1].strip().replace("%", "")
                            battery_data["level"] = int(float(charge))
                        elif "BATTV" in line:  # Battery voltage
                            voltage = line.split(":")[1].strip().replace("Volts", "")
                            battery_data["voltage"] = float(voltage)
                        elif "ITEMP" in line:  # Internal temp
                            temp = line.split(":")[1].strip().replace("C", "")
                            battery_data["temperature"] = float(temp)
            except (
                subprocess.TimeoutExpired,
                subprocess.CalledProcessError,
                FileNotFoundError,
            ):
                pass

            return battery_data

        except Exception as e:
            self.logger.error(f"Gerçek batarya verisi alma hatası: {e}")
            # Hata durumunda simüle veri döndür
            import random

            return {
                "level": random.randint(70, 95),
                "voltage": round(random.uniform(12.0, 13.2), 2),
                "current": round(random.uniform(1.5, 3.0), 2),
                "temperature": random.randint(20, 35),
                "health": "GOOD",
            }

    def _get_real_charging_status(self) -> Dict[str, Any]:
        """Gerçek şarj durumu bilgisi"""
        try:
            charging_data = {
                "charging": False,
                "charging_power": 0,
                "charger_connected": False,
            }

            # AC adaptör durumu
            ac_adapters = [
                "/sys/class/power_supply/ADP0",
                "/sys/class/power_supply/ADP1",
                "/sys/class/power_supply/AC",
            ]

            for adapter_path in ac_adapters:
                if os.path.exists(adapter_path):
                    online_file = f"{adapter_path}/online"
                    if os.path.exists(online_file):
                        with open(online_file, "r") as f:
                            online = int(f.read().strip())
                            charging_data["charger_connected"] = bool(online)
                            break

            # Batarya durumu kontrol et
            for bat_num in ["0", "1"]:
                bat_path = f"/sys/class/power_supply/BAT{bat_num}"
                if os.path.exists(bat_path):
                    status_file = f"{bat_path}/status"
                    if os.path.exists(status_file):
                        with open(status_file, "r") as f:
                            status = f.read().strip()
                            charging_data["charging"] = status == "Charging"

                    # Şarj gücü (µW -> W)
                    if charging_data["charging"]:
                        power_file = f"{bat_path}/power_now"
                        if os.path.exists(power_file):
                            with open(power_file, "r") as f:
                                power_uw = int(f.read().strip())
                                charging_data["charging_power"] = round(
                                    power_uw / 1000000, 1
                                )
                    break

            return charging_data

        except Exception as e:
            self.logger.error(f"Şarj durumu alma hatası: {e}")
            return {"charging": False, "charging_power": 0, "charger_connected": False}

    def _get_detailed_power_status(self) -> Dict[str, Any]:
        """Detaylı güç durumu - gerçek veriler kullan"""
        try:
            # Geliştirme ortamı kontrolü
            is_development = os.getenv("ROBOT_HARDWARE") != "true"

            if is_development:
                # Geliştirme ortamında simüle veri
                import random

                return {
                    "main_battery": {
                        "level": random.randint(70, 95),
                        "voltage": round(random.uniform(12.0, 13.2), 2),
                        "current": round(random.uniform(1.5, 3.0), 2),
                        "temperature": random.randint(20, 35),
                        "health": "GOOD",
                    },
                    "charging": random.choice([True, False]),
                    "charging_power": (
                        random.randint(0, 50) if random.choice([True, False]) else 0
                    ),
                    "total_power": round(random.uniform(25, 35), 1),
                    "efficiency": round(random.uniform(85, 95), 1),
                }
            else:
                # Gerçek donanımda gerçek veriler
                main_battery = self._get_real_battery_data()
                charging_info = self._get_real_charging_status()

                # Toplam güç hesapla (ana batarya akımı * voltaj)
                total_power = main_battery["current"] * main_battery["voltage"]

                # Verimlilik hesapla (basit yaklaşım)
                efficiency = min(
                    95, max(70, 100 - (main_battery["temperature"] - 20) * 2)
                )

                return {
                    "main_battery": main_battery,
                    "charging": charging_info["charging"],
                    "charging_power": charging_info["charging_power"],
                    "charger_connected": charging_info["charger_connected"],
                    "total_power": round(total_power, 1),
                    "efficiency": round(efficiency, 1),
                }

        except Exception as e:
            self.logger.error(f"Power status error: {e}")
            # Hata durumunda varsayılan değerler
            return {
                "main_battery": {
                    "level": 85,
                    "voltage": 12.6,
                    "current": 2.3,
                    "temperature": 25,
                    "health": "GOOD",
                },
                "charging": False,
                "charging_power": 0,
                "total_power": 29.0,
                "efficiency": 87,
            }

    def _get_performance_data(self) -> Dict[str, Any]:
        """Performans grafiği için veri"""
        # Son 20 dakikalık simulated data
        import random
        from datetime import datetime, timedelta

        now = datetime.now()
        timestamps = []
        cpu_data = []
        memory_data = []

        for i in range(20):
            time_point = now - timedelta(minutes=19 - i)
            timestamps.append(time_point.strftime("%H:%M"))
            cpu_data.append(round(random.uniform(5, 25), 1))
            memory_data.append(round(random.uniform(40, 60), 1))

        return {
            "timestamps": timestamps,
            "cpu": cpu_data,
            "memory": memory_data,
        }

    def _generate_video_stream(self):
        """Kamera video stream üreteci"""
        while self.camera_enabled:
            try:
                # Kamera görüntüsü al (simülasyon)
                frame = self._get_camera_frame()

                if frame:
                    # JPEG'e encode et
                    _, buffer = cv2.imencode(".jpg", frame)
                    frame_bytes = buffer.tobytes()

                    # HTTP multipart response
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
                    )

                time.sleep(0.1)  # 10 FPS

            except Exception as e:
                self.logger.error(f"Video stream hatası: {e}")
                break

    def _get_camera_frame(self):
        """Kamera frame'i al"""
        # Gerçek implementasyonda Raspberry Pi Camera kullanılacak
        # import picamera

        # Simülasyon için boş frame
        if not CV2_AVAILABLE:
            return None

        try:
            import numpy as np

            # Test pattern oluştur
            frame = np.zeros((480, 640, 3), dtype=np.uint8)

            # Zaman bilgisi ekle
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(
                frame,
                f"OBA Robot Camera - {timestamp}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            # Robot durumu ekle
            if self.power_manager:
                battery_level = self.power_manager.get_battery_level()
                cv2.putText(
                    frame,
                    f"Battery: {battery_level:.1f}%",
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )

            return frame

        except Exception as e:
            self.logger.error(f"Camera frame error: {e}")
            return None

    def start_real_time_updates(self):
        """Gerçek zamanlı güncellemeleri başlat"""

        def update_loop():
            while self.running:
                try:
                    if self.connected_clients > 0:
                        # Robot durumunu tüm client'lara gönder
                        status = self._get_robot_status()
                        self.socketio.emit("robot_status_update", status)

                    time.sleep(1)  # 1 saniyede bir güncelle

                except Exception as e:
                    self.logger.error(f"Real-time update hatası: {e}")
                    time.sleep(5)

        threading.Thread(target=update_loop, daemon=True).start()

    def start(self):
        """Web server'ı başlat"""
        self.running = True

        # Gerçek zamanlı güncellemeleri başlat
        self.start_real_time_updates()

        self.logger.info(f"Web server başlatılıyor: http://{self.host}:{self.port}")

        try:
            self.socketio.run(self.app, host=self.host, port=self.port, debug=False)
        except Exception as e:
            self.logger.error(f"Web server başlatma hatası: {e}")

    def stop(self):
        """Web server'ı durdur"""
        self.running = False
        self.logger.info("Web server durduruluyor...")

        # Manuel kontrolü deaktifleştir
        if self.manual_control_active:
            self._deactivate_manual_control()


# HTML Template'leri oluştur
def create_html_templates():
    """HTML template dosyalarını oluştur"""

    # Ana template (base.html)
    base_html = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}OBA Robot Kontrol Paneli{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <style>
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
        }
        .status-online { background-color: #28a745; }
        .status-offline { background-color: #dc3545; }
        .status-warning { background-color: #ffc107; }

        .battery-bar {
            height: 20px;
            background: linear-gradient(to right, #dc3545, #ffc107, #28a745);
            border-radius: 10px;
            position: relative;
        }

        .control-pad {
            width: 200px;
            height: 200px;
            border: 2px solid #ccc;
            border-radius: 50%;
            position: relative;
            margin: 20px auto;
            cursor: pointer;
        }

        .control-center {
            width: 50px;
            height: 50px;
            background: #007bff;
            border-radius: 50%;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-robot"></i> OBA Robot
            </a>
            <div class="navbar-nav">
                <a class="nav-link" href="/">Ana Sayfa</a>
                <a class="nav-link" href="/control">Kontrol</a>
                <a class="nav-link" href="/monitoring">İzleme</a>
                <a class="nav-link" href="/areas">Alanlar</a>
                <a class="nav-link" href="/settings">Ayarlar</a>
            </div>
            <div class="navbar-text">
                <span class="status-indicator" id="connection-status"></span>
                <span id="connection-text">Bağlanıyor...</span>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Socket.IO bağlantısı
        const socket = io();

        socket.on('connect', function() {
            document.getElementById('connection-status').className = 'status-indicator status-online';
            document.getElementById('connection-text').textContent = 'Bağlı';
        });

        socket.on('disconnect', function() {
            document.getElementById('connection-status').className = 'status-indicator status-offline';
            document.getElementById('connection-text').textContent = 'Bağlantı Kesildi';
        });

        // Durum güncellemeleri
        socket.on('robot_status_update', function(data) {
            updateRobotStatus(data);
        });

        function updateRobotStatus(status) {
            // Battery level güncelle
            if (status.power && status.power.battery_level !== undefined) {
                const batteryElement = document.getElementById('battery-level');
                if (batteryElement) {
                    batteryElement.textContent = status.power.battery_level.toFixed(1) + '%';
                }
            }

            // Robot state güncelle
            if (status.main_controller && status.main_controller.state) {
                const stateElement = document.getElementById('robot-state');
                if (stateElement) {
                    stateElement.textContent = status.main_controller.state;
                }
            }
        }

        // Emergency stop
        function emergencyStop() {
            fetch('/api/emergency_stop', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Acil durdurma aktif!');
                    }
                });
        }

        // Clear emergency
        function clearEmergency() {
            fetch('/api/clear_emergency', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Acil durdurma kaldırıldı');
                    }
                });
        }
    </script>
    {% block scripts %}{% endblock %}
</body>
</html>"""

    # Ana sayfa (index.html)
    index_html = """{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-tachometer-alt"></i> Robot Durumu</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Durum:</strong> <span id="robot-state" class="badge bg-primary">Hazır</span></p>
                        <p><strong>Batarya:</strong> <span id="battery-level">--</span></p>
                        <p><strong>Konum:</strong> <span id="robot-position">--</span></p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Çalışma Süresi:</strong> <span id="uptime">--</span></p>
                        <p><strong>Biçilen Alan:</strong> <span id="mowed-area">--</span></p>
                        <p><strong>Kalan Süre:</strong> <span id="remaining-time">--</span></p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-exclamation-triangle"></i> Acil Kontroller</h5>
            </div>
            <div class="card-body text-center">
                <button class="btn btn-danger btn-lg mb-2" onclick="emergencyStop()">
                    <i class="fas fa-stop"></i> ACİL DURDUR
                </button>
                <br>
                <button class="btn btn-warning" onclick="clearEmergency()">
                    <i class="fas fa-play"></i> Devam Et
                </button>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-video"></i> Kamera Görüntüsü</h5>
            </div>
            <div class="card-body text-center">
                <img id="camera-feed" src="/video_feed" alt="Kamera Görüntüsü" class="img-fluid" style="max-height: 400px;">
                <br><br>
                <button class="btn btn-primary" onclick="toggleCamera()">
                    <i class="fas fa-camera"></i> Kamera Aç/Kapat
                </button>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    function toggleCamera() {
        // Kamera toggle functionality
        socket.emit('start_camera');
    }

    // Periyodik durum güncellemesi
    setInterval(function() {
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                updateRobotStatus(data.robot);
            });
    }, 2000);
</script>
{% endblock %}"""

    return {"base.html": base_html, "index.html": index_html}


if __name__ == "__main__":
    # Test için
    logging.basicConfig(level=logging.INFO)

    web_server = WebServer()

    try:
        web_server.start()
    except KeyboardInterrupt:
        web_server.stop()
        print("Web server durduruldu")
