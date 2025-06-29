"""
Sensör Yönetimi Modülü
Tüm sensörlerden veri toplama ve yönetme
"""

import os
import time
import logging
import threading
from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum

# Local imports
from .dht22_sensor import DHT22Hardware, DHT22Reading


class SensorType(Enum):
    """Sensör türleri"""

    IMU = "imu"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    DISTANCE = "distance"
    GPS = "gps"
    CAMERA = "camera"


@dataclass
class SensorReading:
    """Sensör okuması"""

    sensor_type: SensorType
    value: Any
    unit: str
    timestamp: float
    quality: float = 1.0  # 0-1 arası kalite değeri


class SensorManager:
    """Sensör yönetim sınıfı"""

    def __init__(self, simulate: bool = None):
        self.logger = logging.getLogger("SensorManager")

        # Geliştirme ortamı kontrolü
        if simulate is None:
            # Raspberry Pi kontrolü
            self.simulate = not self._is_raspberry_pi()
        else:
            self.simulate = simulate

        msg = "Simülasyon" if self.simulate else "Gerçek Donanım"
        self.logger.info("Sensör modu: %s", msg)

        # Sensör durumları
        self.sensors_active = False
        self.sensor_thread = None
        self.readings: Dict[SensorType, SensorReading] = {}

        # Hardware interfaces (sadece gerçek modda)
        self.imu = None
        self.temp_sensor = None
        self.distance_sensors = []
        self.gps_module = None

        if not self.simulate:
            self._initialize_hardware()

    def _is_raspberry_pi(self) -> bool:
        """Raspberry Pi kontrolü"""
        try:
            # /proc/cpuinfo kontrolü
            with open("/proc/cpuinfo", "r") as f:
                cpuinfo = f.read()
                return "BCM" in cpuinfo or "Raspberry Pi" in cpuinfo
        except Exception:
            # Docker veya geliştirme ortamı
            return "ROBOT_HARDWARE" in os.environ

    def _initialize_hardware(self):
        """Gerçek donanım başlatma"""
        try:
            self.logger.info("Donanım sensörleri başlatılıyor...")

            # IMU (BNO055)
            try:
                import board
                import busio
                import adafruit_bno055

                i2c = busio.I2C(board.SCL, board.SDA)
                self.imu = adafruit_bno055.BNO055_I2C(i2c)
                self.logger.info("✅ IMU (BNO055) başlatıldı")
            except Exception as e:
                self.logger.warning(f"IMU başlatma hatası: {e}")

            # Sıcaklık/Nem sensörü (DHT22) - Yeni hardware sınıfı
            try:
                self.dht22_hardware = DHT22Hardware(pin_number=4, retry_count=3)
                self.logger.info("✅ DHT22 hardware sınıfı başlatıldı")
            except Exception as e:
                self.logger.warning(f"DHT22 hardware başlatma hatası: {e}")
                self.dht22_hardware = None

            # IR mesafe sensörleri
            try:
                import board
                import busio
                import adafruit_ads1x15.ads1115 as ADS
                from adafruit_ads1x15.analog_in import AnalogIn

                i2c = busio.I2C(board.SCL, board.SDA)
                ads = ADS.ADS1115(i2c)

                # 2 adet Sharp IR sensör
                self.distance_sensors = [
                    AnalogIn(ads, ADS.P0),  # Ön sensör
                    AnalogIn(ads, ADS.P1),  # Yan sensör
                ]
                self.logger.info("✅ IR mesafe sensörleri başlatıldı")
            except Exception as e:
                self.logger.warning(f"IR sensör başlatma hatası: {e}")

            # GPS modülü (UART)
            try:
                import serial

                self.gps_module = serial.Serial("/dev/ttyS0", 9600, timeout=1)
                self.logger.info("✅ GPS modülü başlatıldı")
            except Exception as e:
                self.logger.warning(f"GPS başlatma hatası: {e}")

        except Exception as e:
            self.logger.error(f"Donanım başlatma genel hatası: {e}")

    def start_monitoring(self):
        """Sensör izlemesini başlat"""
        if not self.sensors_active:
            self.sensors_active = True
            self.sensor_thread = threading.Thread(
                target=self._monitoring_loop, daemon=True
            )
            self.sensor_thread.start()
            self.logger.info("Sensör izlemesi başlatıldı")

    def stop_monitoring(self):
        """Sensör izlemesini durdur"""
        self.sensors_active = False
        if self.sensor_thread:
            self.sensor_thread.join(timeout=2)
        self.logger.info("Sensör izlemesi durduruldu")

    def _monitoring_loop(self):
        """Ana sensör okuma döngüsü"""
        while self.sensors_active:
            try:
                # IMU verileri
                self._read_imu()

                # Sıcaklık/Nem
                self._read_temperature_humidity()

                # Mesafe sensörleri
                self._read_distance_sensors()

                # GPS
                self._read_gps()

                time.sleep(0.5)  # 2Hz güncelleme

            except Exception as e:
                self.logger.error(f"Sensör okuma hatası: {e}")
                time.sleep(1)

    def _read_imu(self):
        """IMU sensörü oku"""
        try:
            if self.simulate:
                # Simülasyon verileri
                import random

                self.readings[SensorType.IMU] = SensorReading(
                    sensor_type=SensorType.IMU,
                    value={
                        "heading": random.uniform(0, 360),
                        "inclination": random.uniform(-10, 10),
                        "temperature": random.uniform(20, 40),
                        "calibration": random.choice(["GOOD", "FAIR", "POOR"]),
                    },
                    unit="degrees",
                    timestamp=time.time(),
                    quality=0.8,
                )
            else:
                # Gerçek IMU
                if self.imu:
                    heading = self.imu.euler[0]  # Yaw
                    inclination = self.imu.euler[1]  # Pitch
                    temp = self.imu.temperature
                    cal_status = self.imu.calibration_status

                    # Kalibrasyon kalitesi
                    cal_quality = "GOOD" if cal_status[0] >= 2 else "POOR"

                    self.readings[SensorType.IMU] = SensorReading(
                        sensor_type=SensorType.IMU,
                        value={
                            "heading": heading or 0,
                            "inclination": inclination or 0,
                            "temperature": temp or 25,
                            "calibration": cal_quality,
                        },
                        unit="degrees",
                        timestamp=time.time(),
                        quality=cal_status[0] / 3.0 if cal_status else 0.5,
                    )

        except Exception as e:
            self.logger.error(f"IMU okuma hatası: {e}")

    def _read_temperature_humidity(self):
        """Sıcaklık ve nem sensörü oku"""
        try:
            if self.simulate:
                # Simülasyon
                import random

                self.readings[SensorType.TEMPERATURE] = SensorReading(
                    sensor_type=SensorType.TEMPERATURE,
                    value=round(20 + random.uniform(-5, 15), 1),
                    unit="°C",
                    timestamp=time.time(),
                )

                self.readings[SensorType.HUMIDITY] = SensorReading(
                    sensor_type=SensorType.HUMIDITY,
                    value=round(50 + random.uniform(-20, 30), 1),
                    unit="%",
                    timestamp=time.time(),
                )
            else:
                # Yeni DHT22Hardware sınıfı kullan
                if self.dht22_hardware:
                    reading = self.dht22_hardware.read_sensor()

                    if reading.is_valid:
                        self.readings[SensorType.TEMPERATURE] = SensorReading(
                            sensor_type=SensorType.TEMPERATURE,
                            value=reading.temperature,
                            unit="°C",
                            timestamp=time.time(),
                            quality=1.0,
                        )

                        self.readings[SensorType.HUMIDITY] = SensorReading(
                            sensor_type=SensorType.HUMIDITY,
                            value=reading.humidity,
                            unit="%",
                            timestamp=time.time(),
                            quality=1.0,
                        )
                    else:
                        self.logger.warning(
                            f"DHT22 okuma hatası: {reading.error_message}"
                        )

        except Exception as e:
            self.logger.error(f"Sıcaklık/nem okuma hatası: {e}")

    def _read_distance_sensors(self):
        """IR mesafe sensörleri oku"""
        try:
            if self.simulate:
                # Simülasyon
                import random

                self.readings[SensorType.DISTANCE] = SensorReading(
                    sensor_type=SensorType.DISTANCE,
                    value=round(30 + random.uniform(-20, 50), 1),
                    unit="cm",
                    timestamp=time.time(),
                )
            else:
                # Gerçek IR sensörler
                if self.distance_sensors:
                    # Sharp GP2Y0A21 kalibrasyonu
                    front_voltage = self.distance_sensors[0].voltage

                    # Voltajdan mesafeye çevirme (Sharp IR sensör formülü)
                    if front_voltage > 0.2:
                        distance = 27.726 * (front_voltage**-1.2045)  # cm
                        distance = max(10, min(80, distance))  # Sınırla

                        self.readings[SensorType.DISTANCE] = SensorReading(
                            sensor_type=SensorType.DISTANCE,
                            value=round(distance, 1),
                            unit="cm",
                            timestamp=time.time(),
                            quality=0.9 if 15 <= distance <= 70 else 0.5,
                        )

        except Exception as e:
            self.logger.error(f"Mesafe sensörü okuma hatası: {e}")

    def _read_gps(self):
        """GPS modülü oku"""
        try:
            if self.simulate:
                # Simülasyon
                import random

                satellites = random.randint(4, 12)
                fix = satellites >= 4

                if fix:
                    # OBA Robot test konumu (Ankara yakını)
                    lat = 39.9334 + random.uniform(-0.0001, 0.0001)
                    lon = 32.8597 + random.uniform(-0.0001, 0.0001)
                else:
                    lat, lon = 0, 0

                self.readings[SensorType.GPS] = SensorReading(
                    sensor_type=SensorType.GPS,
                    value={
                        "latitude": round(lat, 6),
                        "longitude": round(lon, 6),
                        "altitude": round(850 + random.uniform(-5, 15), 1),
                        "satellites": satellites,
                        "fix": fix,
                        "speed": round(random.uniform(0, 2.5), 2),  # m/s
                        "course": round(random.uniform(0, 360), 1),  # derece
                        "hdop": round(random.uniform(0.8, 2.5), 1),
                        "timestamp": time.time(),
                    },
                    unit="coords",
                    timestamp=time.time(),
                    quality=0.9 if fix else 0.3,
                )
            else:
                # Gerçek GPS (u-blox NEO-8M NMEA parsing)
                if self.gps_module and self.gps_module.in_waiting:
                    line = (
                        self.gps_module.readline()
                        .decode("ascii", errors="replace")
                        .strip()
                    )

                    if line.startswith("$GPGGA"):
                        # GGA - Global Positioning System Fix Data
                        self._parse_gga_sentence(line)
                    elif line.startswith("$GPRMC"):
                        # RMC - Recommended Minimum Course
                        self._parse_rmc_sentence(line)

        except Exception as e:
            self.logger.error(f"GPS okuma hatası: {e}")

    def _parse_gga_sentence(self, sentence):
        """GGA NMEA sentence parse et"""
        try:
            parts = sentence.split(",")
            if len(parts) >= 15:
                lat = self._parse_coordinate(parts[2], parts[3])
                lon = self._parse_coordinate(parts[4], parts[5])
                fix_quality = int(parts[6]) if parts[6] else 0
                satellites = int(parts[7]) if parts[7] else 0
                hdop = float(parts[8]) if parts[8] else 99.0
                altitude = float(parts[9]) if parts[9] else 0.0

                self.readings[SensorType.GPS] = SensorReading(
                    sensor_type=SensorType.GPS,
                    value={
                        "latitude": lat,
                        "longitude": lon,
                        "altitude": altitude,
                        "satellites": satellites,
                        "fix": fix_quality > 0,
                        "hdop": hdop,
                        "speed": 0.0,  # GGA'da speed yok
                        "course": 0.0,  # GGA'da course yok
                        "timestamp": time.time(),
                    },
                    unit="coords",
                    timestamp=time.time(),
                    quality=0.9 if fix_quality > 0 else 0.1,
                )
        except Exception as e:
            self.logger.error(f"GGA parse hatası: {e}")

    def _parse_rmc_sentence(self, sentence):
        """RMC NMEA sentence parse et"""
        try:
            parts = sentence.split(",")
            if len(parts) >= 12:
                status = parts[2]  # A=valid, V=invalid
                if status == "A":
                    lat = self._parse_coordinate(parts[3], parts[4])
                    lon = self._parse_coordinate(parts[5], parts[6])
                    speed = float(parts[7]) if parts[7] else 0.0  # knots
                    course = float(parts[8]) if parts[8] else 0.0  # degrees

                    # Knots'u m/s'ye çevir
                    speed_ms = speed * 0.514444

                    # Mevcut GPS reading'i güncelle veya yeni oluştur
                    if SensorType.GPS in self.readings:
                        gps_data = self.readings[SensorType.GPS].value.copy()
                    else:
                        gps_data = {}

                    gps_data.update(
                        {
                            "latitude": lat,
                            "longitude": lon,
                            "speed": round(speed_ms, 2),
                            "course": round(course, 1),
                            "fix": True,
                            "timestamp": time.time(),
                        }
                    )

                    self.readings[SensorType.GPS] = SensorReading(
                        sensor_type=SensorType.GPS,
                        value=gps_data,
                        unit="coords",
                        timestamp=time.time(),
                        quality=0.9,
                    )
        except Exception as e:
            self.logger.error(f"RMC parse hatası: {e}")

    def _parse_coordinate(self, coord_str, direction):
        """NMEA koordinat formatını decimal degrees'e çevir"""
        if not coord_str or not direction:
            return 0.0

        try:
            # DDMM.MMMMM veya DDDMM.MMMMM formatı
            if len(coord_str) >= 4:
                if "." in coord_str:
                    # Koordinat string'ini degrees ve minutes'a ayır
                    if len(coord_str.split(".")[0]) == 4:  # latitude (DDMM)
                        degrees = int(coord_str[:2])
                        minutes = float(coord_str[2:])
                    else:  # longitude (DDDMM)
                        degrees = int(coord_str[:3])
                        minutes = float(coord_str[3:])

                    decimal = degrees + minutes / 60.0

                    # Yön kontrolü
                    if direction in ["S", "W"]:
                        decimal = -decimal

                    return round(decimal, 6)
        except Exception as e:
            self.logger.error(f"Koordinat parse hatası: {e}")

        return 0.0

    def get_sensor_data(self) -> Dict[str, Any]:
        """Tüm sensör verilerini al"""
        data = {}

        # IMU verileri
        if SensorType.IMU in self.readings:
            imu_data = self.readings[SensorType.IMU].value
            data.update(
                {
                    "heading": imu_data.get("heading", 0),
                    "inclination": imu_data.get("inclination", 0),
                    "imu_temperature": imu_data.get("temperature", 25),
                    "imu_calibration": imu_data.get("calibration", "UNKNOWN"),
                }
            )

        # Sıcaklık
        if SensorType.TEMPERATURE in self.readings:
            data["temperature"] = self.readings[SensorType.TEMPERATURE].value

        # Nem
        if SensorType.HUMIDITY in self.readings:
            data["humidity"] = self.readings[SensorType.HUMIDITY].value

        # Mesafe
        if SensorType.DISTANCE in self.readings:
            data["distance"] = self.readings[SensorType.DISTANCE].value

        # GPS
        if SensorType.GPS in self.readings:
            gps_data = self.readings[SensorType.GPS].value
            data.update(
                {
                    "gps_satellites": gps_data.get("satellites", 0),
                    "gps_latitude": gps_data.get("latitude", 0),
                    "gps_longitude": gps_data.get("longitude", 0),
                    "gps_fix": gps_data.get("fix", False),
                }
            )

        return data

    def get_sensor_quality(self) -> Dict[str, float]:
        """Sensör kalite bilgileri"""
        quality = {}
        for sensor_type, reading in self.readings.items():
            quality[sensor_type.value] = reading.quality
        return quality

    def get_navigation_data(self) -> Dict[str, Any]:
        """Profesyonel navigasyon için birleştirilmiş sensör verileri"""
        nav_data = {
            "timestamp": time.time(),
            "gps": None,
            "imu": None,
            "lidar": None,
            "odometry": None,
            "fusion": {
                "position": {"x": 0, "y": 0, "z": 0},
                "orientation": {"roll": 0, "pitch": 0, "yaw": 0},
                "velocity": {"linear": 0, "angular": 0},
                "confidence": 0.0,
            },
        }

        try:
            # GPS verileri
            if SensorType.GPS in self.readings:
                gps_reading = self.readings[SensorType.GPS]
                gps_data = gps_reading.value
                nav_data["gps"] = {
                    "latitude": gps_data.get("latitude", 0),
                    "longitude": gps_data.get("longitude", 0),
                    "altitude": gps_data.get("altitude", 0),
                    "speed": gps_data.get("speed", 0),
                    "course": gps_data.get("course", 0),
                    "satellites": gps_data.get("satellites", 0),
                    "fix": gps_data.get("fix", False),
                    "hdop": gps_data.get("hdop", 99.0),
                    "timestamp": gps_reading.timestamp,
                    "quality": gps_reading.quality,
                }

            # IMU verileri
            if SensorType.IMU in self.readings:
                imu_reading = self.readings[SensorType.IMU]
                imu_data = imu_reading.value
                nav_data["imu"] = {
                    "acceleration": {
                        "x": imu_data.get("accel_x", 0),
                        "y": imu_data.get("accel_y", 0),
                        "z": imu_data.get("accel_z", 0),
                    },
                    "gyroscope": {
                        "x": imu_data.get("gyro_x", 0),
                        "y": imu_data.get("gyro_y", 0),
                        "z": imu_data.get("gyro_z", 0),
                    },
                    "magnetometer": {
                        "x": imu_data.get("mag_x", 0),
                        "y": imu_data.get("mag_y", 0),
                        "z": imu_data.get("mag_z", 0),
                    },
                    "heading": imu_data.get("heading", 0),
                    "inclination": imu_data.get("inclination", 0),
                    "temperature": imu_data.get("temperature", 25),
                    "calibration": imu_data.get("calibration", "UNKNOWN"),
                    "timestamp": imu_reading.timestamp,
                    "quality": imu_reading.quality,
                }

            # LiDAR verileri (simülasyon için placeholder)
            if self.simulate:
                import random

                nav_data["lidar"] = {
                    "ranges": [random.uniform(0.1, 10.0) for _ in range(360)],
                    "angle_min": 0.0,
                    "angle_max": 2 * 3.14159,
                    "angle_increment": 2 * 3.14159 / 360,
                    "range_min": 0.1,
                    "range_max": 10.0,
                    "timestamp": time.time(),
                    "quality": 0.8,
                }
            else:
                # Gerçek LiDAR implementasyonu (RPLIDAR A1M8)
                nav_data["lidar"] = self._get_lidar_data()

            # Odometry verileri (enkoder)
            nav_data["odometry"] = self._get_odometry_data()

            # Sensor fusion - basit örnek
            nav_data["fusion"] = self._perform_sensor_fusion(nav_data)

        except Exception as e:
            self.logger.error(f"Navigation data hatası: {e}")

        return nav_data

    def _get_lidar_data(self) -> Dict[str, Any]:
        """LiDAR verilerini al"""
        try:
            if self.simulate:
                import random

                return {
                    "ranges": [random.uniform(0.1, 10.0) for _ in range(360)],
                    "angle_min": 0.0,
                    "angle_max": 2 * 3.14159,
                    "angle_increment": 2 * 3.14159 / 360,
                    "range_min": 0.1,
                    "range_max": 10.0,
                    "timestamp": time.time(),
                    "quality": 0.8,
                }
            else:
                # Gerçek RPLIDAR A1M8 implementasyonu
                # rplidar kütüphanesi gerekli
                return {
                    "ranges": [],
                    "angle_min": 0.0,
                    "angle_max": 0.0,
                    "angle_increment": 0.0,
                    "range_min": 0.0,
                    "range_max": 0.0,
                    "timestamp": time.time(),
                    "quality": 0.0,
                }
        except Exception as e:
            self.logger.error(f"LiDAR data hatası: {e}")
            return {}

    def _get_odometry_data(self) -> Dict[str, Any]:
        """Odometry (enkoder) verilerini al"""
        try:
            # Motor controller'dan enkoder verilerini al
            try:
                from .motor_controller import MotorController

                motor_controller = MotorController()
                motor_status = motor_controller.get_all_motor_status()
            except ImportError:
                motor_status = {}

            # Sol ve sağ tekerlekten pozisyon hesapla
            left_pos = motor_status.get("left_drive", {}).get("encoder_position", 0)
            right_pos = motor_status.get("right_drive", {}).get("encoder_position", 0)

            # Basit diferansiyel kinematik
            wheel_separation = 0.35  # metre (tekerlekler arası mesafe)
            wheel_radius = 0.075  # metre (tekerlek yarıçapı)

            # Pozisyon değişimini hesapla
            linear_pos = (left_pos + right_pos) / 2 * wheel_radius
            angular_pos = (right_pos - left_pos) / wheel_separation * wheel_radius

            return {
                "position": {
                    "x": linear_pos * 0.001,  # mm'den m'ye çevir
                    "y": 0.0,  # Y ekseni hesaplanacak
                    "theta": angular_pos,
                },
                "velocity": {
                    "linear": 0.0,  # Hız hesaplanacak
                    "angular": 0.0,
                },
                "encoder_counts": {
                    "left": left_pos,
                    "right": right_pos,
                },
                "wheel_params": {
                    "separation": wheel_separation,
                    "radius": wheel_radius,
                },
                "timestamp": time.time(),
                "quality": 0.9,
            }

        except Exception as e:
            self.logger.error(f"Odometry data hatası: {e}")
            return {
                "position": {"x": 0, "y": 0, "theta": 0},
                "velocity": {"linear": 0, "angular": 0},
                "encoder_counts": {"left": 0, "right": 0},
                "timestamp": time.time(),
                "quality": 0.0,
            }

    def _perform_sensor_fusion(self, nav_data: Dict[str, Any]) -> Dict[str, Any]:
        """Basit sensor fusion algoritması"""
        try:
            fusion_result = {
                "position": {"x": 0, "y": 0, "z": 0},
                "orientation": {"roll": 0, "pitch": 0, "yaw": 0},
                "velocity": {"linear": 0, "angular": 0},
                "confidence": 0.0,
            }

            confidence_total = 0.0
            weight_sum = 0.0

            # GPS pozisyonu
            if nav_data.get("gps") and nav_data["gps"].get("fix"):
                gps_weight = nav_data["gps"]["quality"]
                # GPS koordinatlarını local koordinatlara çevir (basit)
                # Gerçek uygulamada UTM projection kullanılmalı
                fusion_result["position"]["x"] = nav_data["gps"]["latitude"]
                fusion_result["position"]["y"] = nav_data["gps"]["longitude"]
                fusion_result["position"]["z"] = nav_data["gps"].get("altitude", 0)

                confidence_total += gps_weight
                weight_sum += gps_weight

            # IMU orientation
            if nav_data.get("imu"):
                imu_weight = nav_data["imu"]["quality"]
                fusion_result["orientation"]["yaw"] = nav_data["imu"]["heading"]
                fusion_result["orientation"]["pitch"] = nav_data["imu"]["inclination"]

                confidence_total += imu_weight
                weight_sum += imu_weight

            # Odometry velocity
            if nav_data.get("odometry"):
                odom_weight = nav_data["odometry"]["quality"]
                fusion_result["velocity"]["linear"] = nav_data["odometry"]["velocity"][
                    "linear"
                ]
                fusion_result["velocity"]["angular"] = nav_data["odometry"]["velocity"][
                    "angular"
                ]

                confidence_total += odom_weight
                weight_sum += odom_weight

            # Toplam confidence hesapla
            if weight_sum > 0:
                fusion_result["confidence"] = confidence_total / weight_sum
            else:
                fusion_result["confidence"] = 0.0

            return fusion_result

        except Exception as e:
            self.logger.error(f"Sensor fusion hatası: {e}")
            return {
                "position": {"x": 0, "y": 0, "z": 0},
                "orientation": {"roll": 0, "pitch": 0, "yaw": 0},
                "velocity": {"linear": 0, "angular": 0},
                "confidence": 0.0,
            }


# Global instance
_sensor_manager = None


def get_sensor_manager() -> SensorManager:
    """Global sensör manager'ı al"""
    global _sensor_manager
    if _sensor_manager is None:
        _sensor_manager = SensorManager()
        _sensor_manager.start_monitoring()
    return _sensor_manager


if __name__ == "__main__":
    # Test kodu
    logging.basicConfig(level=logging.INFO)

    sensor_manager = SensorManager(simulate=True)
    sensor_manager.start_monitoring()

    try:
        for i in range(10):
            data = sensor_manager.get_sensor_data()
            print(f"Sensör verileri: {data}")
            time.sleep(2)

    except KeyboardInterrupt:
        pass
    finally:
        sensor_manager.stop_monitoring()
        print("Sensör yönetimi durduruldu")
