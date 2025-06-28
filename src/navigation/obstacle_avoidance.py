"""
Engel Kaçınma Modülü
Real-time engel algılama ve kaçınma algoritmaları
"""

import logging
import time
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ObstacleType(Enum):
    """Engel türleri"""

    IR_DETECTED = "ir_detected"
    LIDAR_DETECTED = "lidar_detected"
    CAMERA_DETECTED = "camera_detected"
    STATIC_KNOWN = "static_known"


@dataclass
class Obstacle:
    """Engel bilgisi"""

    x: float
    y: float
    size: float = 0.3  # metre cinsinden yarıçap
    type: ObstacleType = ObstacleType.IR_DETECTED
    confidence: float = 1.0
    timestamp: float = 0.0


class ObstacleAvoidance:
    """Real-time engel kaçınma sistemi"""

    def __init__(self, simulate: bool = False):
        self.logger = logging.getLogger("ObstacleAvoidance")
        self.simulate = simulate

        # Parametreler
        self.safe_distance = 0.5  # 50cm güvenli mesafe
        self.warning_distance = 1.0  # 1m uyarı mesafesi
        self.emergency_distance = 0.2  # 20cm acil fren mesafesi

        # Sensör parametreleri (doküman uygun: sadece 2 IR sensör)
        self.ir_sensor_angles = [-45, 45]  # 2 sensör: sol ve sağ
        self.ir_sensor_pins = [23, 24]  # GPIO 23, 24
        self.ir_max_range = 2.0  # 2 metre max menzil

        # Mevcut engeller
        self.detected_obstacles: List[Obstacle] = []
        self.last_sensor_update = 0

        # Avoidance state
        self.avoidance_active = False
        self.last_avoidance_command = {"linear": 0, "angular": 0}

        # YENİ: Recovery behavior
        self.stuck_threshold = 3.0  # 3 saniye aynı yerde kalırsa stuck
        self.last_position = (0.0, 0.0)
        self.position_history = []
        self.stuck_start_time = None
        self.recovery_mode = False

        # YENİ: Velocity profiling
        self.max_linear_speed = 1.0
        self.max_angular_speed = 2.0
        self.acceleration_limit = 0.5  # m/s²
        self.last_command_time = time.time()

        # YENİ: Multi-sensor fusion
        self.lidar_data = []
        self.camera_objects = []
        self.sensor_weights = {"ir": 0.4, "lidar": 0.4, "camera": 0.2}

    def update_ir_sensors(self, sensor_readings: Dict[str, float]):
        """IR sensör verilerini güncelle"""
        try:
            current_time = time.time()
            new_obstacles = []

            for i, angle_deg in enumerate(self.ir_sensor_angles):
                sensor_key = f"ir_{i}"
                if sensor_key in sensor_readings:
                    distance = sensor_readings[sensor_key]

                    # Geçerli okuma kontrolü
                    if 0.05 <= distance <= self.ir_max_range:
                        angle_rad = math.radians(angle_deg)

                        # Robot merkezli koordinatlara çevir
                        obs_x = distance * math.cos(angle_rad)
                        obs_y = distance * math.sin(angle_rad)

                        obstacle = Obstacle(
                            x=obs_x,
                            y=obs_y,
                            size=0.2,
                            type=ObstacleType.IR_DETECTED,
                            confidence=0.8,
                            timestamp=current_time,
                        )
                        new_obstacles.append(obstacle)

            # Eski engelleri temizle (5 saniyeden eski)
            self.detected_obstacles = [
                obs
                for obs in self.detected_obstacles
                if current_time - obs.timestamp < 5.0
            ]

            # Yeni engelleri ekle
            self.detected_obstacles.extend(new_obstacles)
            self.last_sensor_update = current_time

            self.logger.debug(
                f"IR sensörler güncellendi: {len(new_obstacles)} yeni engel"
            )

        except Exception as e:
            self.logger.error(f"IR sensör güncelleme hatası: {e}")

    def check_path_clear(
        self,
        target_x: float,
        target_y: float,
        path_points: Optional[List[Tuple[float, float]]] = None,
    ) -> bool:
        """Hedefe giden yol temiz mi kontrol et"""
        if path_points:
            # Path planning ile entegrasyon - tüm path noktalarını kontrol et
            for point in path_points:
                px, py = point
                if not self._is_point_safe(px, py):
                    return False
        else:
            # Basit düz çizgi kontrolü
            if not self._is_line_clear(0, 0, target_x, target_y):
                return False

        return True

    def _is_point_safe(self, x: float, y: float) -> bool:
        """Belirli bir nokta güvenli mi?"""
        for obstacle in self.detected_obstacles:
            # Nokta ile engel arası mesafe
            distance = math.sqrt((x - obstacle.x) ** 2 + (y - obstacle.y) ** 2)
            if distance < (obstacle.size + self.safe_distance):
                return False
        return True

    def _is_line_clear(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        """İki nokta arası çizgi temiz mi?"""
        # Çizgiyi discrete noktalara böl
        steps = int(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) / 0.1)  # 10cm adımlar
        if steps == 0:
            return True

        for i in range(steps + 1):
            t = i / steps if steps > 0 else 0
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            if not self._is_point_safe(x, y):
                return False
        return True

    def get_avoidance_command(
        self,
        current_linear: float,
        current_angular: float,
        current_x: float = 0.0,
        current_y: float = 0.0,
    ) -> Dict[str, float]:
        """Engel kaçınma komutu hesapla - YENİ: Multi-sensor + Recovery"""

        # 1. Sensor fusion yap
        self.fuse_sensor_data()

        # 2. Stuck kontrolü
        self.check_stuck_condition(current_x, current_y)

        # 3. Recovery mode kontrolü
        if self.recovery_mode:
            recovery_cmd = self.get_recovery_command()
            self.last_avoidance_command = recovery_cmd
            return recovery_cmd

        # 4. Normal engel kaçınma
        if not self.detected_obstacles:
            self.avoidance_active = False
            target_cmd = {"linear": current_linear, "angular": current_angular}
        else:
            target_cmd = self._calculate_avoidance(current_linear, current_angular)

        # 5. Velocity smoothing uygula
        smooth_cmd = self.apply_velocity_smoothing(
            target_cmd["linear"], target_cmd["angular"]
        )

        self.last_avoidance_command = smooth_cmd
        return smooth_cmd

    def _calculate_avoidance(
        self, current_linear: float, current_angular: float
    ) -> Dict[str, float]:
        """Ana engel kaçınma hesaplama mantığı"""
        # En yakın engeli bul
        closest_obstacle = min(
            self.detected_obstacles, key=lambda obs: math.sqrt(obs.x**2 + obs.y**2)
        )

        distance = math.sqrt(closest_obstacle.x**2 + closest_obstacle.y**2)

        # Acil fren - çok yakın engel
        if distance < self.emergency_distance:
            self.logger.warning(f"ACİL FREN! Engel {distance:.2f}m mesafede")
            self.avoidance_active = True
            return {"linear": 0.0, "angular": 0.0}

        # Yavaşlama ve kaçınma - yakın engel
        elif distance < self.safe_distance:
            self.avoidance_active = True

            # Engelin hangi tarafta olduğunu belirle
            obstacle_angle = math.atan2(closest_obstacle.y, closest_obstacle.x)

            # Kaçınma stratejisi
            if abs(obstacle_angle) < math.pi / 4:  # Önde
                # Engel solda mı sağda mı?
                avoidance_angular = -1.0 if obstacle_angle > 0 else 1.0

                # Hızı azalt
                safe_linear = max(0.1, current_linear * 0.3)

                self.logger.info(f"Engel kaçınma: {distance:.2f}m, dönerek kaçış")
                return {"linear": safe_linear, "angular": avoidance_angular}

            else:  # Yanlarda - yavaşlayarak devam et
                safe_linear = max(0.1, current_linear * 0.5)
                return {"linear": safe_linear, "angular": current_angular * 0.5}

        # Uyarı mesafesi - sadece yavaşla
        elif distance < self.warning_distance:
            self.avoidance_active = False
            safe_linear = current_linear * 0.7
            self.logger.debug(f"Uyarı: {distance:.2f}m mesafede, yavaşlıyor")
            return {"linear": safe_linear, "angular": current_angular}

        # Güvenli mesafe
        else:
            self.avoidance_active = False
            return {"linear": current_linear, "angular": current_angular}

    def get_sensor_readings_simulation(self) -> Dict[str, float]:
        """Simülasyon için sahte IR sensör verileri"""
        if not self.simulate:
            return {}

        # Simülasyon: rastgele engel scenarios
        import random

        readings = {}

        for i in range(len(self.ir_sensor_angles)):
            # %90 hiç engel yok, %10 engel var
            if random.random() < 0.9:
                readings[f"ir_{i}"] = self.ir_max_range + 1  # Max range dışı
            else:
                readings[f"ir_{i}"] = random.uniform(0.2, 1.5)  # 20cm-1.5m arası

        return readings

    def get_real_ir_readings(self) -> Dict[str, float]:
        """Gerçek IR sensörlerden okuma yap"""
        if self.simulate:
            return self.get_sensor_readings_simulation()

        # Gerçek sensör implementasyonu
        # GPIO pinlerinden analog okuma yapılacak
        try:
            import board
            import busio
            import adafruit_ads1x15.ads1015 as ADS
            from adafruit_ads1x15.analog_in import AnalogIn

            # I2C ve ADC setup
            i2c = busio.I2C(board.SCL, board.SDA)
            ads = ADS.ADS1015(i2c)

            readings = {}
            for i in range(4):  # 4 analog channel
                if i < len(self.ir_sensor_angles):
                    channel = AnalogIn(ads, getattr(ADS, f"P{i}"))
                    voltage = channel.voltage

                    # Voltajdan mesafeye çevir (Sharp IR sensör için)
                    # Örnek kalibrasyon: distance = 27.726 * voltage^(-1.2045)
                    if voltage > 0.2:  # Minimum voltaj kontrolü
                        distance = 27.726 * (voltage**-1.2045) / 100  # cm'den m'ye
                        readings[f"ir_{i}"] = min(distance, self.ir_max_range)
                    else:
                        readings[f"ir_{i}"] = self.ir_max_range + 1

            return readings

        except Exception as e:
            self.logger.error(f"IR sensör okuma hatası: {e}")
            return {}

    def get_statistics(self) -> Dict:
        """Engel kaçınma istatistikleri"""
        return {
            "detected_obstacles": len(self.detected_obstacles),
            "avoidance_active": self.avoidance_active,
            "last_update": self.last_sensor_update,
            "closest_obstacle_distance": (
                min(math.sqrt(obs.x**2 + obs.y**2) for obs in self.detected_obstacles)
                if self.detected_obstacles
                else float("inf")
            ),
        }

    def update_lidar_data(self, lidar_points: List[Tuple[float, float]]):
        """LIDAR nokta bulutunu güncelle"""
        try:
            current_time = time.time()
            new_obstacles = []

            # LIDAR noktalarını engellere çevir
            for point in lidar_points:
                x, y = point
                distance = math.sqrt(x**2 + y**2)

                if 0.1 <= distance <= 10.0:  # LIDAR range: 10m
                    obstacle = Obstacle(
                        x=x,
                        y=y,
                        size=0.1,  # LIDAR daha hassas
                        type=ObstacleType.LIDAR_DETECTED,
                        confidence=0.9,
                        timestamp=current_time,
                    )
                    new_obstacles.append(obstacle)

            self.lidar_data = new_obstacles
            self.logger.debug(f"LIDAR güncellendi: {len(new_obstacles)} nokta")

        except Exception as e:
            self.logger.error(f"LIDAR güncelleme hatası: {e}")

    def update_camera_objects(self, detected_objects: List[Dict]):
        """Kamera nesne algılama sonuçlarını güncelle"""
        try:
            current_time = time.time()
            new_obstacles = []

            for obj in detected_objects:
                if obj.get("class") in ["person", "chair", "table", "obstacle"]:
                    # Kamera koordinatlarından robot koordinatlarına çevir
                    # Bu gerçek implementasyonda camera calibration gerekir
                    x = obj.get("distance", 2.0) * math.cos(obj.get("angle", 0))
                    y = obj.get("distance", 2.0) * math.sin(obj.get("angle", 0))

                    obstacle = Obstacle(
                        x=x,
                        y=y,
                        size=obj.get("size", 0.3),
                        type=ObstacleType.CAMERA_DETECTED,
                        confidence=obj.get("confidence", 0.7),
                        timestamp=current_time,
                    )
                    new_obstacles.append(obstacle)

            self.camera_objects = new_obstacles
            self.logger.debug(f"Kamera güncellendi: {len(new_obstacles)} nesne")

        except Exception as e:
            self.logger.error(f"Kamera güncelleme hatası: {e}")

    def fuse_sensor_data(self):
        """Multi-sensor fusion - tüm sensör verilerini birleştir"""
        try:
            current_time = time.time()

            # Tüm sensörlerden gelen engelleri birleştir
            all_obstacles = []

            # IR sensör engelleri (zaten detected_obstacles'da)
            ir_obstacles = [
                obs
                for obs in self.detected_obstacles
                if obs.type == ObstacleType.IR_DETECTED
            ]

            # Weighted fusion
            for ir_obs in ir_obstacles:
                ir_obs.confidence *= self.sensor_weights["ir"]
                all_obstacles.append(ir_obs)

            for lidar_obs in self.lidar_data:
                lidar_obs.confidence *= self.sensor_weights["lidar"]
                all_obstacles.append(lidar_obs)

            for cam_obs in self.camera_objects:
                cam_obs.confidence *= self.sensor_weights["camera"]
                all_obstacles.append(cam_obs)

            # Yakın engelleri birleştir (clustering)
            fused_obstacles = self._cluster_obstacles(all_obstacles)

            # Son engel listesini güncelle
            self.detected_obstacles = fused_obstacles

        except Exception as e:
            self.logger.error(f"Sensor fusion hatası: {e}")

    def _cluster_obstacles(self, obstacles: List[Obstacle]) -> List[Obstacle]:
        """Yakın engelleri birleştir"""
        if not obstacles:
            return []

        clusters = []
        cluster_threshold = 0.3  # 30cm içindeki engelleri birleştir

        for obs in obstacles:
            added_to_cluster = False

            for cluster in clusters:
                # Cluster merkezi ile mesafe
                cluster_center_x = sum(o.x for o in cluster) / len(cluster)
                cluster_center_y = sum(o.y for o in cluster) / len(cluster)

                distance = math.sqrt(
                    (obs.x - cluster_center_x) ** 2 + (obs.y - cluster_center_y) ** 2
                )

                if distance < cluster_threshold:
                    cluster.append(obs)
                    added_to_cluster = True
                    break

            if not added_to_cluster:
                clusters.append([obs])

        # Her cluster'dan bir engel oluştur
        fused_obstacles = []
        for cluster in clusters:
            if cluster:
                # Weighted average
                total_conf = sum(obs.confidence for obs in cluster)
                if total_conf > 0:
                    avg_x = sum(obs.x * obs.confidence for obs in cluster) / total_conf
                    avg_y = sum(obs.y * obs.confidence for obs in cluster) / total_conf
                    max_size = max(obs.size for obs in cluster)
                    avg_conf = total_conf / len(cluster)

                    fused_obs = Obstacle(
                        x=avg_x,
                        y=avg_y,
                        size=max_size,
                        type=cluster[0].type,  # İlk engelin tipini al
                        confidence=min(1.0, avg_conf),
                        timestamp=max(obs.timestamp for obs in cluster),
                    )
                    fused_obstacles.append(fused_obs)

        return fused_obstacles

    def check_stuck_condition(self, current_x: float, current_y: float):
        """Robot sıkışmış mı kontrol et"""
        current_time = time.time()
        current_pos = (current_x, current_y)

        # Pozisyon geçmişi güncelle
        self.position_history.append((current_pos, current_time))

        # 5 saniyeden eski kayıtları temizle
        self.position_history = [
            (pos, t) for pos, t in self.position_history if current_time - t < 5.0
        ]

        if len(self.position_history) < 10:  # Yeterli veri yok
            return False

        # Son 3 saniyedeki hareket miktarını kontrol et
        recent_positions = [
            pos
            for pos, t in self.position_history
            if current_time - t < self.stuck_threshold
        ]

        if len(recent_positions) < 5:
            return False

        # Maksimum hareket mesafesini hesapla
        max_movement = 0
        for i in range(len(recent_positions) - 1):
            pos1 = recent_positions[i]
            pos2 = recent_positions[i + 1]
            movement = math.sqrt((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2)
            max_movement = max(max_movement, movement)

        # 3 saniyede 10cm'den az hareket ettiyse stuck
        if max_movement < 0.1:
            if not self.recovery_mode:
                self.stuck_start_time = current_time
                self.recovery_mode = True
                self.logger.warning("🚨 Robot sıkışmış! Recovery mode başlatılıyor")
            return True
        else:
            if self.recovery_mode:
                self.recovery_mode = False
                self.logger.info("✅ Recovery başarılı, normal moda dönülüyor")
            return False

    def get_recovery_command(self) -> Dict[str, float]:
        """Sıkışma durumunda recovery komutu"""
        if not self.recovery_mode:
            return {"linear": 0, "angular": 0}

        current_time = time.time()
        recovery_duration = current_time - (self.stuck_start_time or current_time)

        # Recovery stratejisi: geri git, dön, tekrar dene
        if recovery_duration < 2.0:
            # İlk 2 saniye: geri git
            self.logger.debug("Recovery: Geri gidiliyor")
            return {"linear": -0.3, "angular": 0}
        elif recovery_duration < 4.0:
            # Sonraki 2 saniye: sağa dön
            self.logger.debug("Recovery: Sağa dönülüyor")
            return {"linear": 0, "angular": -1.0}
        elif recovery_duration < 6.0:
            # Son 2 saniye: ileri git
            self.logger.debug("Recovery: İleri gidiliyor")
            return {"linear": 0.2, "angular": 0}
        else:
            # 6 saniye sonra recovery'yi bitir
            self.recovery_mode = False
            self.logger.info("Recovery tamamlandı")
            return {"linear": 0, "angular": 0}

    def apply_velocity_smoothing(
        self, target_linear: float, target_angular: float
    ) -> Dict[str, float]:
        """Hız geçişlerini yumuşak yap"""
        current_time = time.time()
        dt = current_time - self.last_command_time
        self.last_command_time = current_time

        if dt > 0.5:  # İlk çalıştırma veya uzun süre beklediyse
            dt = 0.1

        # Mevcut komutları al
        current_linear = self.last_avoidance_command["linear"]
        current_angular = self.last_avoidance_command["angular"]

        # Maksimum ivme sınırlaması
        max_linear_change = self.acceleration_limit * dt
        max_angular_change = 2.0 * dt  # angular için daha yüksek

        # Yumuşak geçiş hesapla
        linear_diff = target_linear - current_linear
        angular_diff = target_angular - current_angular

        if abs(linear_diff) > max_linear_change:
            linear_diff = max_linear_change * (1 if linear_diff > 0 else -1)

        if abs(angular_diff) > max_angular_change:
            angular_diff = max_angular_change * (1 if angular_diff > 0 else -1)

        smooth_linear = current_linear + linear_diff
        smooth_angular = current_angular + angular_diff

        # Maksimum hız sınırlaması
        smooth_linear = max(
            -self.max_linear_speed, min(self.max_linear_speed, smooth_linear)
        )
        smooth_angular = max(
            -self.max_angular_speed, min(self.max_angular_speed, smooth_angular)
        )

        return {"linear": smooth_linear, "angular": smooth_angular}


# Test fonksiyonu
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Simülasyon testi
    avoidance = ObstacleAvoidance(simulate=True)

    print("🚧 Gelişmiş Engel Kaçınma Test Başlıyor...")
    print("✨ Yeni özellikler: Multi-sensor, Recovery, Velocity Smoothing")

    for i in range(15):
        # Simülasyon sensör verileri
        readings = avoidance.get_sensor_readings_simulation()
        avoidance.update_ir_sensors(readings)

        # Simülasyon LIDAR verisi
        import random

        if random.random() < 0.3:  # %30 şans LIDAR engel görür
            lidar_points = [(random.uniform(0.5, 2.0), random.uniform(-0.5, 0.5))]
            avoidance.update_lidar_data(lidar_points)

        # Simülasyon kamera verisi
        if random.random() < 0.2:  # %20 şans kamera nesne görür
            camera_objects = [
                {
                    "class": "person",
                    "distance": random.uniform(1.0, 3.0),
                    "angle": random.uniform(-0.5, 0.5),
                    "confidence": 0.8,
                    "size": 0.4,
                }
            ]
            avoidance.update_camera_objects(camera_objects)

        # Test komutu
        test_linear = 0.5
        test_angular = 0.0

        # Simülasyon pozisyon
        test_x = i * 0.1
        test_y = 0.0

        # Kaçınma komutu al (YENİ parametrelerle)
        command = avoidance.get_avoidance_command(
            test_linear, test_angular, test_x, test_y
        )

        stats = avoidance.get_statistics()

        # Detaylı status
        status_icons = {True: "🔴 AKTİF", False: "🟢 PASİF"}

        recovery_status = "🚨 RECOVERY" if avoidance.recovery_mode else ""

        print(
            f"Test {i+1:2d}: "
            f"Engel: {stats['detected_obstacles']:2d} | "
            f"Kaçınma: {status_icons[stats['avoidance_active']]} | "
            f"Cmd: L={command['linear']:.2f} A={command['angular']:.2f} | "
            f"{recovery_status}"
        )

        time.sleep(0.3)

    print("✅ Gelişmiş test tamamlandı!")
    print(f"📊 Final stats: Recovery kullanıldı: {avoidance.recovery_mode}")
