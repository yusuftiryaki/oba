"""
Rota Planlama Modülü
Alan verilerine göre biçerdöver rotası oluşturur
"""

import json
import math
import logging
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
    """Rota planlama sınıfı"""

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

        self._load_areas()

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
            self._create_default_areas()
        except Exception as e:
            self.logger.error(f"Alan yükleme hatası: {e}")
            self._create_default_areas()

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
                data["areas"].append(area_data)

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.info("Alanlar kaydedildi")

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

    def _calculate_polygon_area(self, boundary: List[Point]) -> float:
        """Poligon alanını hesapla (Shoelace formula)"""
        if len(boundary) < 3:
            return 0

        area = 0
        n = len(boundary)

        for i in range(n):
            j = (i + 1) % n
            area += boundary[i].x * boundary[j].y
            area -= boundary[j].x * boundary[i].y

        return abs(area) / 2


if __name__ == "__main__":
    # Test kodu
    logging.basicConfig(level=logging.INFO)

    planner = PathPlanner()

    # Test alanını yükle
    if planner.load_area("test_square"):
        print("Test alanı yüklendi")

        # İlerlemeyi simüle et
        current_pos = {"x": 0, "y": 0, "heading": 0}

        for i in range(10):
            waypoint = planner.get_next_waypoint(current_pos)
            if waypoint:
                print(
                    f"Waypoint {i}: x={waypoint.position.x:.2f}, y={waypoint.position.y:.2f}"
                )
                current_pos["x"] = waypoint.position.x
                current_pos["y"] = waypoint.position.y
            else:
                print("Görev tamamlandı!")
                break

        progress = planner.get_progress()
        print(f"İlerleme: {progress['progress']:.1f}%")

        estimated_time = planner.estimate_completion_time("test_square")
        print(f"Tahmini süre: {estimated_time:.1f} dakika")
