#!/usr/bin/env python3
"""
Path Planner Test Suite
Rota planlama sistemi testleri
"""

import unittest
import sys
import math
import json
from pathlib import Path
from unittest.mock import Mock, patch

# Proje kök dizinini path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.navigation.path_planner import PathPlanner, Point, Waypoint, Area, PatternType


class TestPathPlanner(unittest.TestCase):
    """Path Planner ana testleri"""

    def setUp(self):
        """Her test öncesi çalışır"""
        # Test için var olmayan config dosyası ile başlat (boş areas için)
        self.planner = PathPlanner(config_path="nonexistent_test_config.json")

        # Test alanı oluştur
        self.test_area = Area(
            id="test_area_1",
            name="test_area",
            boundary=[Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)],
            obstacles=[],
            pattern=PatternType.LAWN_MOWER,
        )

    def tearDown(self):
        """Her test sonrası çalışır"""
        self.planner = None

    def test_initialization(self):
        """Başlangıç değerleri kontrolü"""
        self.assertIsNotNone(self.planner)
        self.assertEqual(len(self.planner.areas), 0)
        self.assertEqual(len(self.planner.current_path), 0)

    def test_point_operations(self):
        """Point sınıfı operasyonları testi"""
        p1 = Point(0, 0)
        p2 = Point(3, 4)

        # Mesafe hesaplama
        distance = p1.distance_to(p2)
        self.assertAlmostEqual(distance, 5.0, places=2)

        # Açı hesaplama
        angle = p1.angle_to(p2)
        expected_angle = math.atan2(4, 3)
        self.assertAlmostEqual(angle, expected_angle, places=3)

    def test_waypoint_creation(self):
        """Waypoint oluşturma testi"""
        wp = Waypoint(position=Point(5, 5), speed=0.3, blade_height=3, action="move")

        self.assertEqual(wp.position.x, 5)
        self.assertEqual(wp.position.y, 5)
        self.assertEqual(wp.speed, 0.3)
        self.assertEqual(wp.action, "move")

    def test_area_creation(self):
        """Alan oluşturma testi"""
        area = Area(
            id="test_area_square",
            name="square_area",
            boundary=[Point(0, 0), Point(5, 0), Point(5, 5), Point(0, 5)],
            obstacles=[],
            pattern=PatternType.LAWN_MOWER,
        )

        self.assertEqual(area.name, "square_area")
        self.assertEqual(len(area.boundary), 4)
        self.assertEqual(area.pattern, PatternType.LAWN_MOWER)

    def test_load_area_from_config(self):
        """Konfigürasyondan alan yükleme testi"""
        # Test config oluştur
        test_config = {
            "name": "test_config_area",
            "boundary": [
                {"x": 0, "y": 0},
                {"x": 8, "y": 0},
                {"x": 8, "y": 8},
                {"x": 0, "y": 8},
            ],
            "obstacles": [],
            "pattern": "lawn_mower",
        }

        area = self.planner.load_area_from_config(test_config)

        self.assertEqual(area.name, "test_config_area")
        self.assertEqual(len(area.boundary), 4)
        self.assertEqual(area.pattern, PatternType.LAWN_MOWER)

    def test_lawn_mower_pattern(self):
        """Biçerdöver deseni oluşturma testi"""
        path = self.planner.generate_lawn_mower_pattern(
            self.test_area, stripe_width=2.0
        )

        # Path oluşmuş olmalı
        self.assertGreater(len(path), 0)

        # İlk ve son nokta boundary içinde olmalı
        first_point = path[0].position
        last_point = path[-1].position

        self.assertTrue(
            self.planner.point_in_polygon(first_point, self.test_area.boundary)
        )
        self.assertTrue(
            self.planner.point_in_polygon(last_point, self.test_area.boundary)
        )

    def test_spiral_pattern(self):
        """Spiral desen oluşturma testi"""
        spiral_area = Area(
            id="spiral_test_area",
            name="spiral_test",
            boundary=self.test_area.boundary,
            obstacles=[],
            pattern=PatternType.SPIRAL,
        )

        path = self.planner.generate_spiral_pattern(spiral_area, step_size=1.0)

        self.assertGreater(len(path), 0)

        # Spiral path merkeze doğru hareket etmeli
        center = self.planner.get_area_center(spiral_area.boundary)
        distances = [wp.position.distance_to(center) for wp in path]

        # Genel olarak azalan mesafe trendi olmalı
        self.assertLess(distances[-1], distances[0])

    def test_point_in_polygon(self):
        """Nokta polygon içinde mi testi"""
        # Kare polygon
        polygon = [Point(0, 0), Point(4, 0), Point(4, 4), Point(0, 4)]

        # İçeride olan nokta
        inside_point = Point(2, 2)
        self.assertTrue(self.planner.point_in_polygon(inside_point, polygon))

        # Dışarıda olan nokta
        outside_point = Point(5, 5)
        self.assertFalse(self.planner.point_in_polygon(outside_point, polygon))

        # Sınır üzerinde olan nokta
        boundary_point = Point(0, 2)
        result = self.planner.point_in_polygon(boundary_point, polygon)
        # Sınır durumu implementation'a bağlı

    def test_obstacle_avoidance_planning(self):
        """Engel kaçınmalı planlama testi"""
        # Engelli alan oluştur
        obstacle_area = Area(
            id="obstacle_test_area",
            name="obstacle_test",
            boundary=self.test_area.boundary,
            obstacles=[
                [Point(3, 3), Point(7, 3), Point(7, 7), Point(3, 7)]  # Merkez engel
            ],
            pattern=PatternType.LAWN_MOWER,
        )

        path = self.planner.generate_path(obstacle_area)

        # Path oluşmuş olmalı
        self.assertGreater(len(path), 0)

        # Hiçbir waypoint engel içinde olmamalı
        for wp in path:
            for obstacle in obstacle_area.obstacles:
                self.assertFalse(self.planner.point_in_polygon(wp.position, obstacle))

    def test_path_optimization(self):
        """Path optimizasyonu testi"""
        # Basit zigzag path oluştur
        original_path = [
            Waypoint(Point(0, 0)),
            Waypoint(Point(1, 0)),
            Waypoint(Point(2, 0)),
            Waypoint(Point(3, 0)),
            Waypoint(Point(4, 0)),
        ]

        optimized_path = self.planner.optimize_path(original_path)

        # Optimizasyon sonucu daha az waypoint olmalı
        self.assertLessEqual(len(optimized_path), len(original_path))

    def test_path_smoothing(self):
        """Path yumuşatma testi"""
        # Keskin dönüşlü path
        sharp_path = [
            Waypoint(Point(0, 0)),
            Waypoint(Point(5, 0)),
            Waypoint(Point(5, 5)),
            Waypoint(Point(0, 5)),
        ]

        smoothed_path = self.planner.smooth_path(sharp_path, radius=1.0)

        # Yumuşatma sonucu daha fazla waypoint olmalı
        self.assertGreaterEqual(len(smoothed_path), len(sharp_path))


class TestPathValidation(unittest.TestCase):
    """Path doğrulama testleri"""

    def setUp(self):
        self.planner = PathPlanner(config_path="nonexistent_test_config.json")

        self.test_area = Area(
            id="validation_area_1",
            name="validation_area",
            boundary=[Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)],
            obstacles=[],
            pattern=PatternType.LAWN_MOWER,
        )

    def test_path_validation(self):
        """Path geçerlilik testi"""
        # Geçerli path
        valid_path = [
            Waypoint(Point(1, 1)),
            Waypoint(Point(5, 1)),
            Waypoint(Point(5, 5)),
        ]

        is_valid = self.planner.validate_path(valid_path, self.test_area)
        self.assertTrue(is_valid)

        # Geçersiz path (boundary dışı)
        invalid_path = [
            Waypoint(Point(1, 1)),
            Waypoint(Point(15, 1)),  # Boundary dışı
            Waypoint(Point(5, 5)),
        ]

        is_valid = self.planner.validate_path(invalid_path, self.test_area)
        self.assertFalse(is_valid)

    def test_path_continuity(self):
        """Path süreklilik testi"""
        # Kesikli path
        discontinuous_path = [
            Waypoint(Point(1, 1)),
            Waypoint(Point(9, 9)),  # Çok büyük atlama
        ]

        max_gap = 2.0
        is_continuous = self.planner.check_path_continuity(discontinuous_path, max_gap)
        self.assertFalse(is_continuous)

        # Sürekli path
        continuous_path = [
            Waypoint(Point(1, 1)),
            Waypoint(Point(2, 1)),
            Waypoint(Point(3, 1)),
        ]

        is_continuous = self.planner.check_path_continuity(continuous_path, max_gap)
        self.assertTrue(is_continuous)

    def test_coverage_analysis(self):
        """Kapsama analizi testi"""
        # Grid path oluştur
        grid_path = []
        for x in range(1, 10):
            for y in range(1, 10):
                grid_path.append(Waypoint(Point(x, y)))

        coverage = self.planner.calculate_coverage(grid_path, self.test_area)

        # Yüksek kapsama olmalı
        self.assertGreater(coverage, 0.8)  # %80'in üstü

    def test_path_length_calculation(self):
        """Path uzunluğu hesaplama testi"""
        path = [Waypoint(Point(0, 0)), Waypoint(Point(3, 0)), Waypoint(Point(3, 4))]

        total_length = self.planner.calculate_path_length(path)
        expected_length = 3 + 4  # 3 + 4 = 7

        self.assertAlmostEqual(total_length, expected_length, places=1)


class TestPatternGeneration(unittest.TestCase):
    """Desen oluşturma testleri"""

    def setUp(self):
        self.planner = PathPlanner(config_path="nonexistent_test_config.json")
        self.square_area = Area(
            id="square_pattern_area",
            name="square",
            boundary=[Point(0, 0), Point(8, 0), Point(8, 8), Point(0, 8)],
            obstacles=[],
            pattern=PatternType.LAWN_MOWER,
        )

    def test_different_patterns(self):
        """Farklı desen türleri testi"""
        patterns = [
            PatternType.LAWN_MOWER,
            PatternType.SPIRAL,
            PatternType.PERIMETER_FIRST,
        ]

        for pattern in patterns:
            area = Area(
                id=f"test_{pattern.value}_area",
                name=f"test_{pattern.value}",
                boundary=self.square_area.boundary,
                obstacles=[],
                pattern=pattern,
            )

            path = self.planner.generate_path(area)
            self.assertGreater(len(path), 0, f"Pattern {pattern.value} failed")

    def test_stripe_width_effect(self):
        """Şerit genişliği etkisi testi"""
        narrow_path = self.planner.generate_lawn_mower_pattern(
            self.square_area, stripe_width=1.0
        )

        wide_path = self.planner.generate_lawn_mower_pattern(
            self.square_area, stripe_width=2.0
        )

        # Dar şerit daha fazla waypoint üretmeli
        self.assertGreater(len(narrow_path), len(wide_path))

    def test_boundary_following(self):
        """Sınır takip etme testi"""
        perimeter_path = self.planner.generate_perimeter_path(
            self.square_area, offset=0.5
        )

        # Perimeter path boundary'yi takip etmeli
        self.assertGreater(len(perimeter_path), 0)

        # Tüm noktalar offset mesafesinde olmalı
        for wp in perimeter_path:
            # En yakın boundary noktasına mesafe ~offset olmalı
            min_dist = min(
                wp.position.distance_to(bp) for bp in self.square_area.boundary
            )
            self.assertLess(min_dist, 1.0)  # Makul range


class TestUtilityFunctions(unittest.TestCase):
    """Yardımcı fonksiyon testleri"""

    def setUp(self):
        self.planner = PathPlanner(config_path="nonexistent_test_config.json")

    def test_area_calculation(self):
        """Alan hesaplama testi"""
        # Kare alan (5x5 = 25)
        square = [Point(0, 0), Point(5, 0), Point(5, 5), Point(0, 5)]
        area = self.planner.calculate_polygon_area(square)

        self.assertAlmostEqual(area, 25.0, places=1)

    def test_center_calculation(self):
        """Merkez hesaplama testi"""
        square = [Point(0, 0), Point(4, 0), Point(4, 4), Point(0, 4)]
        center = self.planner.get_area_center(square)

        self.assertAlmostEqual(center.x, 2.0, places=1)
        self.assertAlmostEqual(center.y, 2.0, places=1)

    def test_angle_normalization(self):
        """Açı normalizasyonu testi"""
        # Çeşitli açılar
        angles = [math.pi * 3, -math.pi * 2, math.pi / 2]

        for angle in angles:
            normalized = self.planner.normalize_angle(angle)
            self.assertGreaterEqual(normalized, -math.pi)
            self.assertLess(normalized, math.pi)

    def test_distance_calculations(self):
        """Mesafe hesaplamaları testi"""
        p1 = Point(0, 0)
        p2 = Point(3, 4)

        # Euclidean distance
        euclidean = self.planner.euclidean_distance(p1, p2)
        self.assertAlmostEqual(euclidean, 5.0, places=2)

        # Manhattan distance
        manhattan = self.planner.manhattan_distance(p1, p2)
        self.assertAlmostEqual(manhattan, 7.0, places=2)


class TestIntegration(unittest.TestCase):
    """Entegrasyon testleri"""

    def setUp(self):
        self.planner = PathPlanner(config_path="nonexistent_test_config.json")

    def test_full_planning_workflow(self):
        """Tam planlama iş akışı testi"""
        # Alan tanımla
        area = Area(
            id="integration_test_area",
            name="integration_test",
            boundary=[Point(0, 0), Point(20, 0), Point(20, 15), Point(0, 15)],
            obstacles=[[Point(5, 5), Point(10, 5), Point(10, 10), Point(5, 10)]],
            pattern=PatternType.LAWN_MOWER,
        )

        # Path oluştur
        path = self.planner.generate_path(area)

        # Doğrula
        is_valid = self.planner.validate_path(path, area)
        self.assertTrue(is_valid)

        # Optimize et
        optimized_path = self.planner.optimize_path(path)

        # İstatistikleri hesapla
        stats = self.planner.get_path_statistics(optimized_path, area)

        self.assertIn("total_length", stats)
        self.assertIn("coverage", stats)
        self.assertIn("waypoint_count", stats)

        # Makul değerler
        self.assertGreater(stats["coverage"], 0.5)
        self.assertGreater(stats["total_length"], 0)

    def test_multi_area_planning(self):
        """Çoklu alan planlama testi"""
        areas = [
            Area(
                id=f"area_{i}_id",
                name=f"area_{i}",
                boundary=[
                    Point(i * 10, 0),
                    Point((i + 1) * 10, 0),
                    Point((i + 1) * 10, 10),
                    Point(i * 10, 10),
                ],
                obstacles=[],
                pattern=PatternType.LAWN_MOWER,
            )
            for i in range(3)
        ]

        # Her alan için path oluştur
        all_paths = []
        for area in areas:
            path = self.planner.generate_path(area)
            all_paths.append(path)

        # Birleştir
        combined_path = self.planner.combine_paths(all_paths)

        # Toplam uzunluk tek tek toplamından büyük olmalı (geçişler)
        individual_lengths = sum(
            self.planner.calculate_path_length(path) for path in all_paths
        )
        combined_length = self.planner.calculate_path_length(combined_path)

        self.assertGreaterEqual(combined_length, individual_lengths)


if __name__ == "__main__":
    # Test suite oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Test sınıflarını ekle
    test_classes = [
        TestPathPlanner,
        TestPathValidation,
        TestPatternGeneration,
        TestUtilityFunctions,
        TestIntegration,
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Test runner
    runner = unittest.TextTestRunner(verbosity=2, descriptions=True, failfast=False)

    print("🗺️  Path Planner Test Suite Başlatılıyor...")
    print("=" * 60)

    result = runner.run(suite)

    print("=" * 60)
    print(f"✅ Başarılı: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Başarısız: {len(result.failures)}")
    print(f"⚠️  Hata: {len(result.errors)}")

    if result.wasSuccessful():
        print("🎉 Tüm testler başarılı!")
        sys.exit(0)
    else:
        print("💥 Bazı testler başarısız!")
        sys.exit(1)
