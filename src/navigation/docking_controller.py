"""
Docking Controller Modülü
Kamera/IR verilerini işleyerek hassas yanaşma manevralarını yönetir
"""

import time
import logging
import math
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
from enum import Enum


class DockingState(Enum):
    """Docking durumları"""

    SEARCHING = "searching"  # İstasyon aranıyor
    APPROACHING = "approaching"  # İstasyona yaklaşılıyor
    ALIGNING = "aligning"  # Hizalanıyor
    FINAL_APPROACH = "final_approach"  # Son yaklaşma
    DOCKED = "docked"  # Bağlandı
    FAILED = "failed"  # Başarısız


@dataclass
class DockingTarget:
    """Docking hedef bilgisi"""

    x: float  # Görüntüdeki x koordinatı
    y: float  # Görüntüdeki y koordinatı
    distance: float  # Tahmini mesafe
    angle: float  # Hedefin açısı (radyan)
    confidence: float  # Güven seviyesi (0-1)
    marker_type: str  # "apriltag" veya "ir_led"


class DockingController:
    """Hassas docking maneuvralarını yöneten sınıf"""

    def __init__(self):
        self.logger = logging.getLogger("DockingController")
        self.state = DockingState.SEARCHING

        # Docking parametreleri
        self.target_distance = 0.05  # 5cm hedef mesafe
        self.alignment_tolerance = 0.02  # 2cm hizalama toleransı
        self.angle_tolerance = 0.05  # ~3 derece açı toleransı

        # Kamera parametreleri
        self.camera_width = 640
        self.camera_height = 480
        self.camera_fov = math.pi / 3  # 60 derece

        # Kontrol parametreleri
        self.max_search_time = 120  # 2 dakika arama süresi
        self.approach_speed = 0.1  # Yaklaşma hızı (m/s)
        self.alignment_speed = 0.05  # Hizalama hızı (m/s)

        # AprilTag parametreleri
        self.apriltag_size = 0.1  # 10cm AprilTag boyutu

        # IR LED parametreleri
        self.ir_led_pattern = [(0, 0), (0.1, 0), (0.05, 0.1)]  # Üçgen desen

        # İstatistikler
        self.docking_attempts = 0
        self.successful_dockings = 0
        self.average_docking_time = 0

        # Başlangıç zamanı
        self.start_time = None

    def dock_to_station(self) -> bool:
        """Ana docking fonksiyonu"""
        self.docking_attempts += 1
        self.start_time = time.time()
        self.state = DockingState.SEARCHING

        self.logger.info("Docking işlemi başlatıldı")

        try:
            while True:
                if self.state == DockingState.SEARCHING:
                    if not self._search_for_station():
                        if time.time() - self.start_time > self.max_search_time:
                            self.state = DockingState.FAILED
                            break
                        continue

                elif self.state == DockingState.APPROACHING:
                    if not self._approach_station():
                        break

                elif self.state == DockingState.ALIGNING:
                    if not self._align_with_station():
                        break

                elif self.state == DockingState.FINAL_APPROACH:
                    if not self._final_approach():
                        break

                elif self.state == DockingState.DOCKED:
                    self.successful_dockings += 1
                    docking_time = time.time() - self.start_time
                    self._update_average_time(docking_time)
                    self.logger.info(f"Docking başarılı! Süre: {docking_time:.1f}s")
                    return True

                elif self.state == DockingState.FAILED:
                    break

                time.sleep(0.1)  # 10Hz kontrol döngüsü

        except Exception as e:
            self.logger.error(f"Docking hatası: {e}")
            self.state = DockingState.FAILED

        self.logger.warning("Docking başarısız")
        return False

    def _search_for_station(self) -> bool:
        """Şarj istasyonunu ara"""
        # Önce AprilTag ara
        apriltag_target = self._detect_apriltag()
        if apriltag_target and apriltag_target.confidence > 0.7:
            self.current_target = apriltag_target
            self.state = DockingState.APPROACHING
            self.logger.info("AprilTag tespit edildi")
            return True

        # AprilTag bulunamazsa IR LED ara
        ir_target = self._detect_ir_leds()
        if ir_target and ir_target.confidence > 0.5:
            self.current_target = ir_target
            self.state = DockingState.APPROACHING
            self.logger.info("IR LED pattern tespit edildi")
            return True

        # Hiçbiri bulunamazsa robot hareket ettir
        self._search_rotation()
        return False

    def _approach_station(self) -> bool:
        """İstasyona yaklaş"""
        target = self._detect_target()
        if not target:
            self.state = DockingState.SEARCHING
            return True

        self.current_target = target

        # Mesafe kontrolü
        if target.distance < 0.5:  # 50cm'den yakınsa hizalama moduna geç
            self.state = DockingState.ALIGNING
            return True

        # Hedefe doğru hareket et
        movement_command = self._calculate_approach_movement(target)
        self._send_movement_command(movement_command)

        return True

    def _align_with_station(self) -> bool:
        """İstasyonla hizala"""
        target = self._detect_target()
        if not target:
            self.state = DockingState.SEARCHING
            return True

        self.current_target = target

        # Hizalama kontrolü
        center_x = self.camera_width / 2
        x_error = abs(target.x - center_x)
        angle_error = abs(target.angle)

        if (
            x_error < self.alignment_tolerance * self.camera_width
            and angle_error < self.angle_tolerance
        ):
            self.state = DockingState.FINAL_APPROACH
            self.logger.info("Hizalama tamamlandı")
            return True

        # Hizalama hareketi
        alignment_command = self._calculate_alignment_movement(target)
        self._send_movement_command(alignment_command)

        return True

    def _final_approach(self) -> bool:
        """Son yaklaşma ve bağlanma"""
        target = self._detect_target()
        if not target:
            self.state = DockingState.FAILED
            return False

        # Hedef mesafeye ulaştık mı?
        if target.distance <= self.target_distance:
            # Fiziksel bağlantıyı kontrol et
            if self._check_physical_connection():
                self.state = DockingState.DOCKED
                return True
            else:
                # Biraz daha yaklaş
                self._send_movement_command({"linear": 0.02, "angular": 0})

        # Yavaş yaklaşma
        approach_command = self._calculate_final_approach_movement(target)
        self._send_movement_command(approach_command)

        return True

    def _detect_apriltag(self) -> Optional[DockingTarget]:
        """AprilTag tespit et"""
        try:
            # Kamera görüntüsü al
            image = self._get_camera_image()
            if image is None:
                return None

            # AprilTag detection (basit simülasyon)
            # Gerçek implementasyonda apriltag kütüphanesi kullanılacak
            apriltag_data = self._simulate_apriltag_detection(image)

            if apriltag_data:
                # AprilTag'den mesafe ve açı hesapla
                distance = self._calculate_distance_from_apriltag(apriltag_data)
                angle = self._calculate_angle_from_apriltag(apriltag_data)

                return DockingTarget(
                    x=apriltag_data["center"][0],
                    y=apriltag_data["center"][1],
                    distance=distance,
                    angle=angle,
                    confidence=apriltag_data["confidence"],
                    marker_type="apriltag",
                )

        except Exception as e:
            self.logger.error(f"AprilTag tespit hatası: {e}")

        return None

    def _detect_ir_leds(self) -> Optional[DockingTarget]:
        """IR LED pattern tespit et"""
        try:
            # IR kamera görüntüsü al
            ir_image = self._get_ir_camera_image()
            if ir_image is None:
                return None

            # LED pattern detection (basit simülasyon)
            led_pattern = self._simulate_ir_led_detection(ir_image)

            if led_pattern:
                # Pattern'den mesafe ve açı hesapla
                distance = self._calculate_distance_from_leds(led_pattern)
                angle = self._calculate_angle_from_leds(led_pattern)

                center_x = sum(led["x"] for led in led_pattern) / len(led_pattern)
                center_y = sum(led["y"] for led in led_pattern) / len(led_pattern)

                return DockingTarget(
                    x=center_x,
                    y=center_y,
                    distance=distance,
                    angle=angle,
                    confidence=0.8,  # LED pattern güven seviyesi
                    marker_type="ir_led",
                )

        except Exception as e:
            self.logger.error(f"IR LED tespit hatası: {e}")

        return None

    def _detect_target(self) -> Optional[DockingTarget]:
        """Mevcut hedefe göre tespit yap"""
        if hasattr(self, "current_target"):
            if self.current_target.marker_type == "apriltag":
                return self._detect_apriltag()
            else:
                return self._detect_ir_leds()

        # Her ikisini de dene
        apriltag = self._detect_apriltag()
        if apriltag:
            return apriltag
        return self._detect_ir_leds()

    def _calculate_approach_movement(self, target: DockingTarget) -> Dict[str, float]:
        """Yaklaşma hareketi hesapla"""
        # Kamera merkezine göre hedef pozisyonu
        center_x = self.camera_width / 2
        x_error = (target.x - center_x) / (self.camera_width / 2)

        # Açısal hız (hedefin merkeze gelmesi için)
        angular_velocity = -x_error * 0.5

        # Doğrusal hız (mesafeye göre)
        linear_velocity = min(self.approach_speed, target.distance * 0.3)

        return {"linear": linear_velocity, "angular": angular_velocity}

    def _calculate_alignment_movement(self, target: DockingTarget) -> Dict[str, float]:
        """Hizalama hareketi hesapla"""
        center_x = self.camera_width / 2
        x_error = (target.x - center_x) / (self.camera_width / 2)

        # Sadece dönüş hareketi (çok yavaş)
        angular_velocity = -x_error * 0.2

        # Çok küçük ileri hareket
        linear_velocity = 0.01 if abs(x_error) < 0.1 else 0

        return {"linear": linear_velocity, "angular": angular_velocity}

    def _calculate_final_approach_movement(
        self, target: DockingTarget
    ) -> Dict[str, float]:
        """Son yaklaşma hareketi hesapla"""
        # Çok yavaş ve hassas hareket
        linear_velocity = min(0.02, target.distance * 0.1)

        # Minimal açısal düzeltme
        center_x = self.camera_width / 2
        x_error = (target.x - center_x) / (self.camera_width / 2)
        angular_velocity = -x_error * 0.1

        return {"linear": linear_velocity, "angular": angular_velocity}

    def _search_rotation(self):
        """Arama için dönüş hareketi"""
        self._send_movement_command({"linear": 0, "angular": 0.2})
        time.sleep(0.5)
        self._send_movement_command({"linear": 0, "angular": 0})

    def _send_movement_command(self, command: Dict[str, float]):
        """Hareket komutunu motor kontrolcüye gönder"""
        # Motor kontrolcüye komut gönderme (simülasyon)
        self.logger.debug(
            f"Hareket komutu: linear={command['linear']:.3f}, angular={command['angular']:.3f}"
        )

        # Gerçek implementasyonda motor kontrolcü çağrılacak
        # self.motor_controller.move(command['linear'], command['angular'])

    def _get_camera_image(self):
        """Kamera görüntüsü al"""
        # Kamera modülünden görüntü alma (simülasyon)
        # Gerçek implementasyonda Raspberry Pi Camera kullanılacak
        return "simulated_image"

    def _get_ir_camera_image(self):
        """IR kamera görüntüsü al"""
        # IR kamera veya filtreli görüntü alma (simülasyon)
        return "simulated_ir_image"

    def _simulate_apriltag_detection(self, image) -> Optional[Dict]:
        """AprilTag tespit simülasyonu"""
        # Gerçek implementasyonda apriltag kütüphanesi kullanılacak
        # import apriltag

        # Simülasyon için rastgele tespit
        import random

        if random.random() > 0.7:  # %30 tespit şansı
            return {
                "center": (
                    320 + random.randint(-50, 50),
                    240 + random.randint(-30, 30),
                ),
                "corners": [(300, 220), (340, 220), (340, 260), (300, 260)],
                "confidence": random.uniform(0.5, 1.0),
                "id": 0,
            }
        return None

    def _simulate_ir_led_detection(self, ir_image) -> Optional[List[Dict]]:
        """IR LED tespit simülasyonu"""
        # Gerçek implementasyonda OpenCV blob detection kullanılacak
        import random

        if random.random() > 0.6:  # %40 tespit şansı
            return [
                {"x": 310, "y": 240, "intensity": 255},
                {"x": 330, "y": 240, "intensity": 250},
                {"x": 320, "y": 220, "intensity": 245},
            ]
        return None

    def _calculate_distance_from_apriltag(self, apriltag_data: Dict) -> float:
        """AprilTag'den mesafe hesapla"""
        # AprilTag boyutu ve görüntüdeki boyutu kullanarak mesafe hesapla
        corners = apriltag_data["corners"]
        tag_width_pixels = abs(corners[1][0] - corners[0][0])

        # Kamera focal length (pixel cinsinden)
        focal_length = self.camera_width / (2 * math.tan(self.camera_fov / 2))

        # Mesafe = (gerçek_boyut * focal_length) / pixel_boyutu
        distance = (self.apriltag_size * focal_length) / tag_width_pixels

        return max(0.01, distance)  # Minimum 1cm

    def _calculate_angle_from_apriltag(self, apriltag_data: Dict) -> float:
        """AprilTag'den açı hesapla"""
        corners = apriltag_data["corners"]

        # Tag'in eğim açısını hesapla
        top_left = corners[0]
        top_right = corners[1]

        dx = top_right[0] - top_left[0]
        dy = top_right[1] - top_left[1]

        return math.atan2(dy, dx)

    def _calculate_distance_from_leds(self, led_pattern: List[Dict]) -> float:
        """LED pattern'den mesafe hesapla"""
        # LED'ler arası mesafe kullanarak hesaplama
        if len(led_pattern) >= 2:
            led1 = led_pattern[0]
            led2 = led_pattern[1]

            pixel_distance = math.sqrt(
                (led1["x"] - led2["x"]) ** 2 + (led1["y"] - led2["y"]) ** 2
            )
            real_distance = 0.1  # LED'ler arası gerçek mesafe (10cm)

            # Kamera focal length
            focal_length = self.camera_width / (2 * math.tan(self.camera_fov / 2))

            distance = (real_distance * focal_length) / pixel_distance
            return max(0.01, distance)

        return 1.0  # Varsayılan mesafe

    def _calculate_angle_from_leds(self, led_pattern: List[Dict]) -> float:
        """LED pattern'den açı hesapla"""
        if len(led_pattern) >= 2:
            led1 = led_pattern[0]
            led2 = led_pattern[1]

            dx = led2["x"] - led1["x"]
            dy = led2["y"] - led1["y"]

            return math.atan2(dy, dx)

        return 0.0

    def _check_physical_connection(self) -> bool:
        """Fiziksel bağlantıyı kontrol et"""
        # Şarj pinlerinde voltaj kontrolü
        # Gerçek implementasyonda ADC ile pin voltajı okunacak

        # Simülasyon
        import random

        return random.random() > 0.1  # %90 başarı şansı

    def _update_average_time(self, new_time: float):
        """Ortalama docking süresini güncelle"""
        if self.successful_dockings == 1:
            self.average_docking_time = new_time
        else:
            alpha = 0.1  # Öğrenme oranı
            self.average_docking_time = (
                alpha * new_time + (1 - alpha) * self.average_docking_time
            )

    def get_docking_stats(self) -> Dict[str, float]:
        """Docking istatistikleri"""
        success_rate = (
            self.successful_dockings / self.docking_attempts * 100
            if self.docking_attempts > 0
            else 0
        )

        return {
            "total_attempts": self.docking_attempts,
            "successful_dockings": self.successful_dockings,
            "success_rate": success_rate,
            "average_time": self.average_docking_time,
        }

    def reset_stats(self):
        """İstatistikleri sıfırla"""
        self.docking_attempts = 0
        self.successful_dockings = 0
        self.average_docking_time = 0
        self.logger.info("Docking istatistikleri sıfırlandı")

    def calibrate_camera(self):
        """Kamera kalibrasyonu"""
        # Kamera kalibrasyon parametrelerini ayarla
        # Gerçek implementasyonda OpenCV kalibrasyon kullanılacak
        self.logger.info("Kamera kalibrasyonu başlatıldı")

        # Kalibrasyon işlemi burada yapılacak
        # - Checkerboard pattern kullanarak
        # - Distortion düzeltmesi
        # - Focal length hesaplaması

        self.logger.info("Kamera kalibrasyonu tamamlandı")

    def emergency_undock(self):
        """Acil undocking"""
        self.logger.warning("Acil undocking başlatıldı")

        # Geriye doğru hareket
        self._send_movement_command({"linear": -0.1, "angular": 0})
        time.sleep(2)
        self._send_movement_command({"linear": 0, "angular": 0})

        self.state = DockingState.SEARCHING


if __name__ == "__main__":
    # Test kodu
    logging.basicConfig(level=logging.INFO)

    docking = DockingController()

    print("Docking test başlıyor...")

    # Simüle edilmiş docking
    success = docking.dock_to_station()

    if success:
        print("Docking başarılı!")
    else:
        print("Docking başarısız!")

    stats = docking.get_docking_stats()
    print(f"İstatistikler: {stats}")
