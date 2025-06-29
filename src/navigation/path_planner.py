"""
Rota Planlama Modülü
Alan verilerine göre biçerdöver rotası oluşturur
GPS entegrasyonu ile profesyonel navigasyon
"""

import json
import math
import logging
import time
import utm
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class PatternType(Enum):
    """Biçme deseni türleri"""

    LAWN_MOWER = "lawn_mower"  # Biçerdöver deseni
    SPIRAL = "spiral"  # Spiral desen
    RANDOM = "random"  # Rastgele desen
    PERIMETER_FIRST = "perimeter_first"  # Önce çevre


@dataclass
class Point:
    """2D nokta"""

    x: float
    y: float

    def distance_to(self, other: "Point") -> float:
        """İki nokta arasındaki mesafe"""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def angle_to(self, other: "Point") -> float:
        """İki nokta arasındaki açı (radyan)"""
        return math.atan2(other.y - self.y, other.x - self.x)


@dataclass
class Waypoint:
    """Rota noktası"""

    position: Point
    speed: float = 0.5
    blade_height: int = 5
    action: str = "move"  # "move", "turn", "stop", "blade_on", "blade_off"


@dataclass
class Area:
    """Biçme alanı tanımı"""

    id: str
    name: str
    boundary: List[Point]  # Alan sınırları
    obstacles: List[List[Point]] = None  # Engeller
    pattern: PatternType = PatternType.LAWN_MOWER
    blade_height: int = 5
    speed: float = 0.5
    overlap: float = 0.1  # %10 örtüşme


class PathPlanner:
    """Rota planlama sınıfı - GPS+IMU+Odometry entegrasyonu ile"""

    def __init__(self, config_path: str = "config/areas.json"):
        self.logger = logging.getLogger("PathPlanner")
        self.config_path = config_path
        self.areas: Dict[str, Area] = {}
        self.current_area: Optional[Area] = None
        self.current_path: List[Waypoint] = []
        self.current_waypoint_index = 0

        # Robot fiziksel parametreleri
        self.robot_width = 0.6  # Robot genişliği (metre)
        self.blade_width = 0.5  # Bıçak genişliği (metre)
        self.turning_radius = 0.3  # Dönüş yarıçapı

        # Planlama parametreleri
        self.safety_margin = 0.2  # Güvenlik mesafesi
        self.max_line_length = 50  # Maksimum çizgi uzunluğu

        # GPS koordinat sistemi
        self.gps_origin = None  # GPS koordinat sistemi orjini
        self.utm_zone = None  # UTM zone bilgisi
        self.current_gps_position = None
        self.current_local_position = Point(0, 0)

        # Sensor fusion için
        self.last_sensor_update = time.time()
        self.position_confidence = 0.0

        self._load_areas()

    def set_gps_origin(self, latitude: float, longitude: float):
        """GPS koordinat sistemi orjinini ayarla"""
        try:
            # GPS koordinatını UTM'e çevir
            utm_x, utm_y, zone_number, zone_letter = utm.from_latlon(
                latitude, longitude
            )

            self.gps_origin = {
                "latitude": latitude,
                "longitude": longitude,
                "utm_x": utm_x,
                "utm_y": utm_y,
                "zone": f"{zone_number}{zone_letter}",
            }
            self.utm_zone = (zone_number, zone_letter)

            self.logger.info(f"GPS orjin ayarlandı: {latitude:.6f}, {longitude:.6f}")
            return True

        except Exception as e:
            self.logger.error(f"GPS orjin ayarlama hatası: {e}")
            return False

    def update_position_from_sensors(self, navigation_data: Dict[str, Any]):
        """Sensor fusion ile pozisyon güncelle"""
        try:
            current_time = time.time()
            confidence_total = 0.0
            weight_sum = 0.0

            # GPS pozisyonu
            if navigation_data.get("gps") and navigation_data["gps"].get("fix"):
                gps = navigation_data["gps"]
                local_pos = self.gps_to_local(gps["latitude"], gps["longitude"])
                if local_pos:
                    gps_weight = gps.get("quality", 0.5)
                    self.current_local_position.x = local_pos.x
                    self.current_local_position.y = local_pos.y
                    confidence_total += gps_weight
                    weight_sum += gps_weight

                    self.current_gps_position = {
                        "lat": gps["latitude"],
                        "lon": gps["longitude"],
                        "timestamp": current_time,
                    }

            # Odometry ile pozisyon düzeltmesi
            if navigation_data.get("odometry"):
                odom = navigation_data["odometry"]
                odom_weight = odom.get("quality", 0.3)
                # Odometry verisi zaten local koordinatlarda
                confidence_total += odom_weight
                weight_sum += odom_weight

            # Toplam confidence hesapla
            if weight_sum > 0:
                self.position_confidence = confidence_total / weight_sum
            else:
                self.position_confidence = 0.0

            self.last_sensor_update = current_time

            self.logger.debug(
                f"Pozisyon güncellendi: "
                f"({self.current_local_position.x:.2f}, "
                f"{self.current_local_position.y:.2f}), "
                f"güven: {self.position_confidence:.2f}"
            )

        except Exception as e:
            self.logger.error(f"Sensor fusion hatası: {e}")

    def gps_to_local(self, latitude: float, longitude: float) -> Optional[Point]:
        """GPS koordinatını local koordinata çevir"""
        if not self.gps_origin:
            self.logger.warning("GPS orjin ayarlanmamış")
            return None

        try:
            # GPS'i UTM'e çevir
            utm_x, utm_y, zone_number, zone_letter = utm.from_latlon(
                latitude, longitude
            )

            # Orjine göre relative pozisyon hesapla
            local_x = utm_x - self.gps_origin["utm_x"]
            local_y = utm_y - self.gps_origin["utm_y"]

            return Point(local_x, local_y)

        except Exception as e:
            self.logger.error(f"GPS-local dönüşüm hatası: {e}")
            return None

    def local_to_gps(self, point: Point) -> Optional[Dict[str, float]]:
        """Local koordinatı GPS koordinatına çevir"""
        if not self.gps_origin:
            return None

        try:
            # Local koordinatı UTM'e çevir
            utm_x = self.gps_origin["utm_x"] + point.x
            utm_y = self.gps_origin["utm_y"] + point.y

            # UTM'i GPS'e çevir
            latitude, longitude = utm.to_latlon(
                utm_x, utm_y, self.utm_zone[0], self.utm_zone[1]
            )

            return {"latitude": latitude, "longitude": longitude}

        except Exception as e:
            self.logger.error(f"Local-GPS dönüşüm hatası: {e}")
            return None

    def _load_areas(self):
        """Alan tanımlarını yükle"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for area_data in data.get("areas", []):
                area = Area(
                    id=area_data["id"],
                    name=area_data["name"],
                    boundary=[Point(p["x"], p["y"]) for p in area_data["boundary"]],
                    obstacles=[
                        [Point(p["x"], p["y"]) for p in obs]
                        for obs in area_data.get("obstacles", [])
                    ],
                    pattern=PatternType(area_data.get("pattern", "lawn_mower")),
                    blade_height=area_data.get("blade_height", 5),
                    speed=area_data.get("speed", 0.5),
                    overlap=area_data.get("overlap", 0.1),
                )
                self.areas[area.id] = area

            self.logger.info(f"{len(self.areas)} alan yüklendi")

        except FileNotFoundError:
            self.logger.warning(f"Alan dosyası bulunamadı: {self.config_path}")
            # Test sırasında varsayılan alanlar oluşturma
        except Exception as e:
            self.logger.error(f"Alan yükleme hatası: {e}")
            # Hata durumunda varsayılan alanlar oluşturma

    def _create_default_areas(self):
        """Varsayılan test alanları oluştur"""
        # Kare alan
        square_area = Area(
            id="test_square",
            name="Test Kare Alan",
            boundary=[Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)],
        )

        # L şeklinde alan
        l_area = Area(
            id="test_l_shape",
            name="Test L Şekli",
            boundary=[
                Point(0, 0),
                Point(15, 0),
                Point(15, 8),
                Point(8, 8),
                Point(8, 15),
                Point(0, 15),
            ],
        )

        self.areas = {"test_square": square_area, "test_l_shape": l_area}

        # Varsayılan alanları kaydet
        self._save_areas()

    def _save_areas(self):
        """Alanları dosyaya kaydet"""
        try:
            data = {"areas": []}

            for area in self.areas.values():
                area_data = {
                    "id": area.id,
                    "name": area.name,
                    "boundary": [[p.x, p.y] for p in area.boundary],
                    "obstacles": [
                        [[p.x, p.y] for p in obstacle]
                        for obstacle in (area.obstacles or [])
                    ],
                    "pattern": area.pattern.value,
                    "blade_height": area.blade_height,
                    "speed": area.speed,
                    "overlap": area.overlap,
                }
                data["areas"].append(area_data)

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Alanlar kaydedildi: {self.config_path}")

        except Exception as e:
            self.logger.error(f"Alan kaydetme hatası: {e}")

    def load_area(self, area_id: str) -> bool:
        """Belirli bir alanı yükle ve rota planla"""
        if area_id not in self.areas:
            self.logger.error(f"Alan bulunamadı: {area_id}")
            return False

        self.current_area = self.areas[area_id]
        self.current_path = self._plan_path(self.current_area)
        self.current_waypoint_index = 0

        self.logger.info(
            f"Alan yüklendi: {area_id}, {len(self.current_path)} waypoint oluşturuldu"
        )
        return True

    def _plan_path(self, area: Area) -> List[Waypoint]:
        """Ana rota planlama fonksiyonu"""
        if area.pattern == PatternType.LAWN_MOWER:
            return self._lawn_mower_pattern(area)
        elif area.pattern == PatternType.SPIRAL:
            return self._spiral_pattern(area)
        elif area.pattern == PatternType.PERIMETER_FIRST:
            return self._perimeter_first_pattern(area)
        else:
            return self._lawn_mower_pattern(area)  # Varsayılan

    def _lawn_mower_pattern(self, area: Area) -> List[Waypoint]:
        """Biçerdöver deseni - paralel çizgiler"""
        waypoints = []

        # Alan sınırlarını bul
        min_x = min(p.x for p in area.boundary)
        max_x = max(p.x for p in area.boundary)
        min_y = min(p.y for p in area.boundary)
        max_y = max(p.y for p in area.boundary)

        # Güvenlik marjını ekle
        min_x += self.safety_margin
        max_x -= self.safety_margin
        min_y += self.safety_margin
        max_y -= self.safety_margin

        # Çizgi aralığını hesapla
        line_spacing = self.blade_width * (1 - area.overlap)

        # Y yönünde çizgiler oluştur
        y = min_y
        direction = 1  # 1: sağa, -1: sola

        while y <= max_y:
            if direction == 1:
                # Soldan sağa
                start_point = Point(min_x, y)
                end_point = Point(max_x, y)
            else:
                # Sağdan sola
                start_point = Point(max_x, y)
                end_point = Point(min_x, y)

            # Alan içinde mi kontrol et
            if self._point_in_polygon(start_point, area.boundary):
                waypoints.append(
                    Waypoint(
                        position=start_point,
                        speed=area.speed,
                        blade_height=area.blade_height,
                        action="move",
                    )
                )

            if self._point_in_polygon(end_point, area.boundary):
                waypoints.append(
                    Waypoint(
                        position=end_point,
                        speed=area.speed,
                        blade_height=area.blade_height,
                        action="move",
                    )
                )

            # Sonraki çizgiye geç
            y += line_spacing
            direction *= -1

        # Dönüş waypoint'leri ekle
        waypoints = self._add_turning_waypoints(waypoints)

        return waypoints

    def _spiral_pattern(self, area: Area) -> List[Waypoint]:
        """Spiral desen"""
        waypoints = []

        # Alan merkezini bul
        center_x = sum(p.x for p in area.boundary) / len(area.boundary)
        center_y = sum(p.y for p in area.boundary) / len(area.boundary)
        center = Point(center_x, center_y)

        # Spiral parametreleri
        max_radius = max(p.distance_to(center) for p in area.boundary)
        radius_step = self.blade_width * (1 - area.overlap)
        angle_step = 0.1  # radyan

        radius = radius_step
        angle = 0

        while radius < max_radius:
            x = center.x + radius * math.cos(angle)
            y = center.y + radius * math.sin(angle)
            point = Point(x, y)

            if self._point_in_polygon(point, area.boundary):
                waypoints.append(
                    Waypoint(
                        position=point,
                        speed=area.speed,
                        blade_height=area.blade_height,
                        action="move",
                    )
                )

            angle += angle_step
            radius += radius_step * angle_step / (2 * math.pi)

        return waypoints

    def _perimeter_first_pattern(self, area: Area) -> List[Waypoint]:
        """Önce çevre, sonra iç kısım"""
        waypoints = []

        # Çevre waypoint'leri
        for i, point in enumerate(area.boundary):
            waypoints.append(
                Waypoint(
                    position=Point(point.x, point.y),
                    speed=area.speed * 0.7,  # Çevrede daha yavaş
                    blade_height=area.blade_height,
                    action="move",
                )
            )

        # İlk noktaya dön
        if area.boundary:
            waypoints.append(
                Waypoint(
                    position=Point(area.boundary[0].x, area.boundary[0].y),
                    speed=area.speed * 0.7,
                    blade_height=area.blade_height,
                    action="move",
                )
            )

        # İç kısım için biçerdöver deseni
        inner_area = self._shrink_area(area, self.blade_width)
        if inner_area:
            inner_waypoints = self._lawn_mower_pattern(inner_area)
            waypoints.extend(inner_waypoints)

        return waypoints

    def _add_turning_waypoints(self, waypoints: List[Waypoint]) -> List[Waypoint]:
        """Dönüş waypoint'leri ekle"""
        if len(waypoints) < 2:
            return waypoints

        enhanced_waypoints = [waypoints[0]]

        for i in range(1, len(waypoints)):
            prev_wp = waypoints[i - 1]
            curr_wp = waypoints[i]

            # Açı değişimi hesapla
            if i < len(waypoints) - 1:
                next_wp = waypoints[i + 1]

                # Dönüş açısı
                angle1 = prev_wp.position.angle_to(curr_wp.position)
                angle2 = curr_wp.position.angle_to(next_wp.position)
                turn_angle = abs(angle2 - angle1)

                # Büyük dönüşler için ara waypoint ekle
                if turn_angle > math.pi / 4:  # 45 derece
                    turn_wp = Waypoint(
                        position=curr_wp.position,
                        speed=curr_wp.speed * 0.5,  # Dönüşte yavaşla
                        blade_height=curr_wp.blade_height,
                        action="turn",
                    )
                    enhanced_waypoints.append(turn_wp)

            enhanced_waypoints.append(curr_wp)

        return enhanced_waypoints

    def _point_in_polygon(self, point: Point, polygon: List[Point]) -> bool:
        """Nokta polygon içinde mi kontrolü (Ray Casting)"""
        x, y = point.x, point.y
        n = len(polygon)
        inside = False

        p1x, p1y = polygon[0].x, polygon[0].y
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n].x, polygon[i % n].y
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def _shrink_area(self, area: Area, margin: float) -> Optional[Area]:
        """Alanı küçült (iç çevre için)"""
        # Basit implementasyon - geliştirilmesi gerekebilir
        shrunken_boundary = []

        for point in area.boundary:
            # Her noktayı merkeze doğru kaydır
            center_x = sum(p.x for p in area.boundary) / len(area.boundary)
            center_y = sum(p.y for p in area.boundary) / len(area.boundary)

            dx = point.x - center_x
            dy = point.y - center_y
            length = math.sqrt(dx**2 + dy**2)

            if length > margin:
                factor = (length - margin) / length
                new_x = center_x + dx * factor
                new_y = center_y + dy * factor
                shrunken_boundary.append(Point(new_x, new_y))

        if len(shrunken_boundary) >= 3:
            return Area(
                id=area.id + "_inner",
                name=area.name + " (İç)",
                boundary=shrunken_boundary,
                pattern=area.pattern,
                blade_height=area.blade_height,
                speed=area.speed,
                overlap=area.overlap,
            )

        return None

    def get_next_waypoint(
        self, current_position: Dict[str, float]
    ) -> Optional[Waypoint]:
        """Sonraki waypoint'i al"""
        if not self.current_path or self.current_waypoint_index >= len(
            self.current_path
        ):
            return None

        current_waypoint = self.current_path[self.current_waypoint_index]
        current_pos = Point(current_position["x"], current_position["y"])

        # Waypoint'e ulaştık mı?
        distance = current_pos.distance_to(current_waypoint.position)
        if distance < 0.5:  # 50cm tolerans
            self.current_waypoint_index += 1
            self.logger.debug(f"Waypoint {self.current_waypoint_index-1} tamamlandı")

        # Sonraki waypoint varsa döndür
        if self.current_waypoint_index < len(self.current_path):
            return self.current_path[self.current_waypoint_index]

        return None

    def get_remaining_path(self) -> List[Waypoint]:
        """Kalan rotayı al"""
        if not self.current_path:
            return []

        return self.current_path[self.current_waypoint_index :]

    def get_progress(self) -> Dict[str, Any]:
        """Görev ilerlemesi"""
        if not self.current_path:
            return {"progress": 0, "completed_waypoints": 0, "total_waypoints": 0}

        total = len(self.current_path)
        completed = self.current_waypoint_index
        progress = (completed / total) * 100 if total > 0 else 0

        return {
            "progress": progress,
            "completed_waypoints": completed,
            "total_waypoints": total,
            "current_area": self.current_area.name if self.current_area else None,
        }

    def reset_path(self):
        """Rotayı sıfırla"""
        self.current_waypoint_index = 0
        self.logger.info("Rota sıfırlandı")

    def add_area(self, area: Area):
        """Yeni alan ekle"""
        self.areas[area.id] = area
        self._save_areas()
        self.logger.info(f"Yeni alan eklendi: {area.name}")

    def remove_area(self, area_id: str):
        """Alan sil"""
        if area_id in self.areas:
            del self.areas[area_id]
            self._save_areas()
            self.logger.info(f"Alan silindi: {area_id}")

    def get_areas(self) -> Dict[str, Dict[str, Any]]:
        """Tüm alanları al"""
        result = {}
        for area_id, area in self.areas.items():
            result[area_id] = {
                "id": area.id,
                "name": area.name,
                "boundary": [{"x": p.x, "y": p.y} for p in area.boundary],
                "pattern": area.pattern.value,
                "blade_height": area.blade_height,
                "speed": area.speed,
            }
        return result

    def estimate_completion_time(self, area_id: str) -> float:
        """Tahmini tamamlanma süresi (dakika)"""
        if area_id not in self.areas:
            return 0

        area = self.areas[area_id]

        # Alan büyüklüğünü hesapla (basit poligon alanı)
        area_size = self._calculate_polygon_area(area.boundary)

        # Biçme hızı ve robot genişliği ile süre hesapla
        coverage_rate = area.speed * self.blade_width  # m²/s
        total_time = area_size / coverage_rate  # saniye

        # Dönüş ve hareket süreleri için %20 ekle
        total_time *= 1.2

        return total_time / 60  # dakikaya çevir

    def normalize_angle(self, angle: float) -> float:
        """Açıyı [-π, π) aralığına normalize et - testlerin beklediği fonksiyon"""
        while angle >= math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

    def calculate_polygon_area(self, polygon: List[Point]) -> float:
        """Poligon alanını hesapla - testlerin beklediği fonksiyon"""
        if len(polygon) < 3:
            return 0.0

        area = 0.0
        n = len(polygon)

        for i in range(n):
            j = (i + 1) % n
            area += polygon[i].x * polygon[j].y
            area -= polygon[j].x * polygon[i].y

        return abs(area) / 2.0

    def get_area_center(self, polygon: List[Point]) -> Point:
        """Poligonun merkezini hesapla - testlerin beklediği fonksiyon"""
        if not polygon:
            return Point(0, 0)

        # Basit merkez hesaplama (centroid)
        sum_x = sum(p.x for p in polygon)
        sum_y = sum(p.y for p in polygon)
        n = len(polygon)

        return Point(sum_x / n, sum_y / n)

    def euclidean_distance(self, p1: Point, p2: Point) -> float:
        """İki nokta arasındaki Euclidean mesafe - testlerin beklediği fonksiyon"""
        return math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)

    def manhattan_distance(self, p1: Point, p2: Point) -> float:
        """İki nokta arasındaki Manhattan mesafe"""
        return abs(p2.x - p1.x) + abs(p2.y - p1.y)

    def point_in_polygon(self, point: Point, polygon: List[Point]) -> bool:
        """Noktanın poligon içinde olup olmadığını kontrol et - testlerin beklediği fonksiyon"""
        if len(polygon) < 3:
            return False

        x, y = point.x, point.y
        n = len(polygon)
        inside = False

        p1x, p1y = polygon[0].x, polygon[0].y
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n].x, polygon[i % n].y
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def load_area_from_config(self, config: Dict[str, Any]) -> Area:
        """Konfigürasyondan alan yükle - testlerin beklediği fonksiyon"""
        try:
            boundary_points = []
            for point_data in config.get("boundary", []):
                if isinstance(point_data, dict):
                    boundary_points.append(Point(point_data["x"], point_data["y"]))
                elif isinstance(point_data, list) and len(point_data) >= 2:
                    boundary_points.append(Point(point_data[0], point_data[1]))

            obstacles = []
            for obstacle_data in config.get("obstacles", []):
                obstacle_points = []
                for point_data in obstacle_data:
                    if isinstance(point_data, dict):
                        obstacle_points.append(Point(point_data["x"], point_data["y"]))
                    elif isinstance(point_data, list) and len(point_data) >= 2:
                        obstacle_points.append(Point(point_data[0], point_data[1]))
                obstacles.append(obstacle_points)

            area = Area(
                id=config.get("id", "config_area"),
                name=config.get("name", "Unnamed Area"),
                boundary=boundary_points,
                obstacles=obstacles,
                pattern=PatternType(config.get("pattern", "lawn_mower")),
                blade_height=config.get("blade_height", 5),
                speed=config.get("speed", 0.5),
                overlap=config.get("overlap", 0.1),
            )

            return area

        except Exception as e:
            self.logger.error(f"Konfigürasyondan alan yükleme hatası: {e}")
            raise

    def generate_lawn_mower_pattern(
        self, area: Area, stripe_width: float = 0.5
    ) -> List[Waypoint]:
        """Biçerdöver deseni oluştur - testlerin beklediği fonksiyon"""
        try:
            waypoints = []

            # Alan sınırlarını bul
            min_x = min(p.x for p in area.boundary)
            max_x = max(p.x for p in area.boundary)
            min_y = min(p.y for p in area.boundary)
            max_y = max(p.y for p in area.boundary)

            # Şerit bazlı hareket
            current_y = min_y + stripe_width / 2
            direction = 1  # 1: sağa, -1: sola

            while current_y < max_y:
                if direction == 1:
                    # Soldan sağa
                    start_x = min_x
                    end_x = max_x
                else:
                    # Sağdan sola
                    start_x = max_x
                    end_x = min_x

                # Şerit boyunca waypoint'ler
                num_points = max(2, int(abs(end_x - start_x) / 0.5))
                for i in range(num_points):
                    t = i / (num_points - 1) if num_points > 1 else 0
                    x = start_x + t * (end_x - start_x)
                    point = Point(x, current_y)

                    # Noktanın alan içinde olup olmadığını kontrol et
                    if self.point_in_polygon(point, area.boundary):
                        waypoint = Waypoint(
                            position=point,
                            speed=area.speed,
                            blade_height=area.blade_height,
                            action="move",
                        )
                        waypoints.append(waypoint)

                current_y += stripe_width
                direction *= -1

            return waypoints

        except Exception as e:
            self.logger.error(f"Lawn mower pattern oluşturma hatası: {e}")
            return []

    def generate_spiral_pattern(
        self, area: Area, step_size: float = 0.5
    ) -> List[Waypoint]:
        """Spiral desen oluştur - testlerin beklediği fonksiyon"""
        try:
            waypoints = []
            center = self.get_area_center(area.boundary)

            # Spiral parametreleri - dışarıdan içeriye
            angle = 0
            max_radius = max(self.euclidean_distance(center, p) for p in area.boundary)
            radius = max_radius

            while radius > step_size:
                x = center.x + radius * math.cos(angle)
                y = center.y + radius * math.sin(angle)
                point = Point(x, y)

                # Alan içinde mi kontrol et
                if self.point_in_polygon(point, area.boundary):
                    waypoint = Waypoint(
                        position=point,
                        speed=area.speed,
                        blade_height=area.blade_height,
                        action="move",
                    )
                    waypoints.append(waypoint)

                # Spiral daralt (içeriye doğru)
                angle += 0.1  # radyan
                radius -= step_size * 0.01

            return waypoints

        except Exception as e:
            self.logger.error(f"Spiral pattern oluşturma hatası: {e}")
            return []

    def generate_path(self, area: Area) -> List[Waypoint]:
        """Alan için rota oluştur - testlerin beklediği ana fonksiyon"""
        try:
            # Pattern'e göre temel path oluştur
            if area.pattern == PatternType.LAWN_MOWER:
                path = self.generate_lawn_mower_pattern(area)
            elif area.pattern == PatternType.SPIRAL:
                path = self.generate_spiral_pattern(area)
            else:
                self.logger.warning(f"Desteklenmeyen pattern: {area.pattern}")
                path = self.generate_lawn_mower_pattern(area)

            # Engel kaçınma uygula
            if area.obstacles:
                path = self._apply_obstacle_avoidance(path, area.obstacles)

            return path

        except Exception as e:
            self.logger.error(f"Rota oluşturma hatası: {e}")
            return []

    def _apply_obstacle_avoidance(
        self, path: List[Waypoint], obstacles: List[List[Point]]
    ) -> List[Waypoint]:
        """Path'e engel kaçınma uygula"""
        filtered_path = []

        for waypoint in path:
            # Waypoint herhangi bir engel içinde mi kontrol et
            in_obstacle = False
            for obstacle in obstacles:
                if self.point_in_polygon(waypoint.position, obstacle):
                    in_obstacle = True
                    break

            # Engel içinde değilse ekle
            if not in_obstacle:
                filtered_path.append(waypoint)

        return filtered_path

    def optimize_path(self, waypoints: List[Waypoint]) -> List[Waypoint]:
        """Rotayı optimize et - testlerin beklediği fonksiyon"""
        if len(waypoints) < 2:
            return waypoints

        optimized = [waypoints[0]]  # İlk waypoint'i koru

        for i in range(1, len(waypoints) - 1):
            current = waypoints[i]
            prev = optimized[-1]
            next_wp = waypoints[i + 1]

            # Düz çizgi kontrolü - eğer üç nokta neredeyse düz çizgide ise orta noktayı atla
            vec1 = (
                current.position.x - prev.position.x,
                current.position.y - prev.position.y,
            )
            vec2 = (
                next_wp.position.x - current.position.x,
                next_wp.position.y - current.position.y,
            )

            # Cross product ile doğrusallık kontrolü
            cross = vec1[0] * vec2[1] - vec1[1] * vec2[0]
            if abs(cross) > 0.1:  # Threshold
                optimized.append(current)

        optimized.append(waypoints[-1])  # Son waypoint'i koru

        self.logger.info(
            f"Rota optimize edildi: {len(waypoints)} -> {len(optimized)} waypoint"
        )
        return optimized

    def smooth_path(
        self, waypoints: List[Waypoint], radius: float = 1.0
    ) -> List[Waypoint]:
        """Rotayı yumuşat - testlerin beklediği fonksiyon"""
        if len(waypoints) < 3:
            return waypoints

        smoothed = [waypoints[0]]  # İlk waypoint'i koru

        for i in range(1, len(waypoints) - 1):
            current = waypoints[i]
            prev = waypoints[i - 1]
            next_wp = waypoints[i + 1]

            # Köşe yumuşatma
            prev_dir = (
                current.position.x - prev.position.x,
                current.position.y - prev.position.y,
            )
            next_dir = (
                next_wp.position.x - current.position.x,
                next_wp.position.y - current.position.y,
            )

            # Basit linear interpolation ile yumuşatma
            factor = min(radius, 0.5)
            smooth_x = current.position.x + factor * (prev_dir[0] + next_dir[0]) * 0.1
            smooth_y = current.position.y + factor * (prev_dir[1] + next_dir[1]) * 0.1

            smoothed_wp = Waypoint(
                position=Point(smooth_x, smooth_y),
                speed=current.speed,
                blade_height=current.blade_height,
                action=current.action,
            )
            smoothed.append(smoothed_wp)

        smoothed.append(waypoints[-1])  # Son waypoint'i koru

        return smoothed

    def validate_path(self, path: List[Waypoint], area: Area) -> bool:
        """Path'in geçerliliğini kontrol et - testlerin beklediği fonksiyon"""
        if not path:
            return False

        # Path noktalarının alan içinde olup olmadığını kontrol et
        for wp in path:
            if not self.point_in_polygon(wp.position, area.boundary):
                return False

        # Engellerde olmadığını kontrol et
        for wp in path:
            for obstacle in area.obstacles:
                if self.point_in_polygon(wp.position, obstacle):
                    return False

        return True

    def check_path_continuity(self, path: List[Waypoint], max_gap: float) -> bool:
        """Path'in sürekliliğini kontrol et - testlerin beklediği fonksiyon"""
        if len(path) < 2:
            return True

        for i in range(len(path) - 1):
            distance = path[i].position.distance_to(path[i + 1].position)
            if distance > max_gap:
                return False
        return True

    def calculate_coverage(self, path: List[Waypoint], area: Area) -> float:
        """Path'in alan kapsamasını hesapla - testlerin beklediği fonksiyon"""
        if not path or not area.boundary:
            return 0.0

        # Basitleştirilmiş coverage hesaplama
        # Path noktalarının alan içinde kaç tanesinin olduğunu say
        covered_points = 0
        total_points = len(path)

        for wp in path:
            if self.point_in_polygon(wp.position, area.boundary):
                covered_points += 1

        return covered_points / max(total_points, 1)

    def calculate_path_length(self, path: List[Waypoint]) -> float:
        """Path uzunluğunu hesapla - testlerin beklediği fonksiyon"""
        if len(path) < 2:
            return 0.0

        total_length = 0.0
        for i in range(len(path) - 1):
            total_length += path[i].position.distance_to(path[i + 1].position)

        return total_length

    def generate_perimeter_path(
        self, area: Area, offset: float = 0.0
    ) -> List[Waypoint]:
        """Çevre path'i oluştur - testlerin beklediği fonksiyon"""
        waypoints = []

        # Basit çevre path - sınır noktalarını waypoint olarak ekle
        for i, point in enumerate(area.boundary):
            # Offset hesapla (basitleştirilmiş)
            if offset > 0:
                # Merkeze doğru offset
                center = self.get_area_center(area.boundary)
                direction_x = center.x - point.x
                direction_y = center.y - point.y
                length = math.sqrt(direction_x**2 + direction_y**2)
                if length > 0:
                    direction_x /= length
                    direction_y /= length
                    offset_point = Point(
                        point.x + direction_x * offset, point.y + direction_y * offset
                    )
                    waypoints.append(Waypoint(offset_point))
                else:
                    waypoints.append(Waypoint(point))
            else:
                waypoints.append(Waypoint(point))

        # İlk noktayı sona ekle (kapalı döngü)
        if waypoints:
            waypoints.append(waypoints[0])

        return waypoints

    def get_path_statistics(self, path: List[Waypoint], area: Area) -> Dict[str, float]:
        """Path istatistiklerini al - testlerin beklediği fonksiyon"""
        stats = {
            "total_length": self.calculate_path_length(path),
            "coverage": self.calculate_coverage(path, area),
            "waypoint_count": float(len(path)),
            "area_size": self.calculate_polygon_area(area.boundary),
        }

        if len(path) > 1:
            stats["average_speed"] = 0.5  # Varsayılan hız
            stats["estimated_time"] = stats["total_length"] / stats["average_speed"]
        else:
            stats["average_speed"] = 0.0
            stats["estimated_time"] = 0.0

        return stats

    def combine_paths(self, paths: List[List[Waypoint]]) -> List[Waypoint]:
        """Birden fazla path'i birleştir - testlerin beklediği fonksiyon"""
        combined_path = []

        for path in paths:
            if path:
                combined_path.extend(path)

        return combined_path
