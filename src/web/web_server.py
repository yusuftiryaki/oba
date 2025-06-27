"""
Web Server Modülü
Uzaktan kontrol ve izleme için web arayüzü sunar
"""

import os
import json
import time
import logging
import threading
from typing import Dict, Any, Optional
from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO, emit
import base64
import io


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

        @self.app.route("/api/emergency_stop", methods=["POST"])
        def api_emergency_stop():
            """Acil durdurma"""
            if self.main_controller:
                self.main_controller.emergency_stop_triggered()
                return jsonify({"success": True})
            return jsonify({"error": "Main controller not available"}), 503

        @self.app.route("/api/clear_emergency", methods=["POST"])
        def api_clear_emergency():
            """Acil durdurma kaldır"""
            if self.main_controller:
                self.main_controller.clear_emergency_stop()
                return jsonify({"success": True})
            return jsonify({"error": "Main controller not available"}), 503

        @self.app.route("/api/manual_control", methods=["POST"])
        def api_manual_control():
            """Manuel kontrol komutları"""
            data = request.get_json()

            if not data:
                return jsonify({"error": "No data provided"}), 400

            # Manuel kontrol modunu aktifleştir
            if not self.manual_control_active:
                self._activate_manual_control()

            # Hareket komutları
            linear = data.get("linear", 0.0)
            angular = data.get("angular", 0.0)

            if self.motor_controller:
                self.motor_controller.move(linear, angular)
                self.last_manual_command_time = time.time()
                return jsonify({"success": True})

            return jsonify({"error": "Motor controller not available"}), 503

        @self.app.route("/api/blade/start", methods=["POST"])
        def api_start_blade():
            """Biçme bıçağını başlat"""
            if self.motor_controller:
                self.motor_controller.start_blade()
                return jsonify({"success": True})
            return jsonify({"error": "Motor controller not available"}), 503

        @self.app.route("/api/blade/stop", methods=["POST"])
        def api_stop_blade():
            """Biçme bıçağını durdur"""
            if self.motor_controller:
                self.motor_controller.stop_blade()
                return jsonify({"success": True})
            return jsonify({"error": "Motor controller not available"}), 503

        @self.app.route("/api/blade/height", methods=["POST"])
        def api_set_blade_height():
            """Biçme yüksekliğini ayarla"""
            data = request.get_json()
            height_level = data.get("height_level", 2)

            if self.motor_controller:
                self.motor_controller.set_blade_height(height_level)
                return jsonify({"success": True})
            return jsonify({"error": "Motor controller not available"}), 503

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
        try:
            import cv2
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

        except ImportError:
            # OpenCV yoksa None döndür
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
