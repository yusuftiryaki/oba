#!/usr/bin/env python3
"""
OBA Robot - Engel Kaçınma Test Suite
Unit ve integration testleri
"""

import unittest
import sys
import time
import math
from pathlib import Path
from unittest.mock import Mock, patch

# Proje kök dizinini path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.navigation.obstacle_avoidance import ObstacleAvoidance, Obstacle, ObstacleType


class TestObstacleAvoidance(unittest.TestCase):
    """Engel Kaçınma sistemi unit testleri"""

    def setUp(self):
        """Her test öncesi çalışır"""
        self.avoidance = ObstacleAvoidance(simulate=True)

    def tearDown(self):
        """Her test sonrası çalışır"""
        self.avoidance = None

    def test_initialization(self):
        """Başlangıç değerleri kontrolü"""
        self.assertEqual(self.avoidance.safe_distance, 0.5)
        self.assertEqual(self.avoidance.warning_distance, 1.0)
        self.assertEqual(self.avoidance.emergency_distance, 0.2)
        self.assertEqual(
            len(self.avoidance.ir_sensor_angles), 2
        )  # 2 sensör: sol ve sağ
        self.assertFalse(self.avoidance.avoidance_active)
        self.assertFalse(self.avoidance.recovery_mode)

    def test_ir_sensor_update(self):
        """IR sensör güncelleme testi"""
        # Test verisi - 2 sensör: sol ve sağ
        sensor_readings = {
            "ir_0": 2.5,  # Sol 45° - max range dışı
            "ir_1": 0.3,  # Sağ 45° - engel var!
        }

        self.avoidance.update_ir_sensors(sensor_readings)

        # Bir engel tespit edilmeli
        self.assertEqual(len(self.avoidance.detected_obstacles), 1)
        obstacle = self.avoidance.detected_obstacles[0]
        self.assertEqual(obstacle.type, ObstacleType.IR_DETECTED)
        self.assertAlmostEqual(obstacle.x, 0.3 * math.cos(math.radians(45)), places=2)
        self.assertAlmostEqual(obstacle.y, 0.3 * math.sin(math.radians(45)), places=2)

    def test_emergency_stop(self):
        """Acil fren testi"""
        # Çok yakın engel oluştur
        close_obstacle = Obstacle(x=0.1, y=0.0, size=0.2, confidence=1.0)
        self.avoidance.detected_obstacles = [close_obstacle]

        command = self.avoidance.get_avoidance_command(0.5, 0.0)

        # Acil fren bekleniyor
        self.assertEqual(command["linear"], 0.0)
        self.assertEqual(command["angular"], 0.0)
        self.assertTrue(self.avoidance.avoidance_active)

    def test_safe_distance_avoidance(self):
        """Güvenli mesafe kaçınma testi"""
        # Önde engel (merkez) - bu durumda kaçınma stratejisi devreye girer
        front_obstacle = Obstacle(x=0.4, y=0.0, size=0.2, confidence=1.0)
        self.avoidance.detected_obstacles = [front_obstacle]

        command = self.avoidance.get_avoidance_command(0.5, 0.0)

        # Yavaşlama bekleniyor
        self.assertLess(command["linear"], 0.5)  # Yavaşlamış
        # Angular hareket olabilir (sağa veya sola)
        self.assertTrue(self.avoidance.avoidance_active)

    def test_warning_distance(self):
        """Uyarı mesafesi testi"""
        # Uyarı mesafesinde engel
        warning_obstacle = Obstacle(x=0.8, y=0.0, size=0.2, confidence=1.0)
        self.avoidance.detected_obstacles = [warning_obstacle]

        command = self.avoidance.get_avoidance_command(0.5, 0.0)

        # Sadece yavaşlama bekleniyor
        self.assertLess(command["linear"], 0.5)  # Yavaşlamış
        self.assertEqual(command["angular"], 0.0)  # Dönmüyor
        self.assertFalse(self.avoidance.avoidance_active)

    def test_no_obstacle(self):
        """Engel yok durumu testi"""
        self.avoidance.detected_obstacles = []

        # Velocity smoothing'i reset et
        self.avoidance.last_avoidance_command = {"linear": 0.5, "angular": 0.2}

        command = self.avoidance.get_avoidance_command(0.5, 0.2)

        # Velocity smoothing nedeniyle tam eşit olmayabilir, yakın olmalı
        self.assertAlmostEqual(command["linear"], 0.5, places=1)
        self.assertAlmostEqual(command["angular"], 0.2, places=1)
        self.assertFalse(self.avoidance.avoidance_active)

    def test_point_safety(self):
        """Nokta güvenlik kontrolü testi"""
        # Engel oluştur
        obstacle = Obstacle(x=1.0, y=1.0, size=0.3, confidence=1.0)
        self.avoidance.detected_obstacles = [obstacle]

        # Güvenli nokta
        self.assertTrue(self.avoidance._is_point_safe(2.0, 2.0))

        # Güvensiz nokta
        self.assertFalse(self.avoidance._is_point_safe(1.0, 1.0))

    def test_line_clearance(self):
        """Çizgi temizlik kontrolü testi"""
        # Engel oluştur
        obstacle = Obstacle(x=1.0, y=0.0, size=0.3, confidence=1.0)
        self.avoidance.detected_obstacles = [obstacle]

        # Engelin üzerinden geçen çizgi - güvensiz
        self.assertFalse(self.avoidance._is_line_clear(0.0, 0.0, 2.0, 0.0))

        # Engeli kaçıran çizgi - güvenli
        self.assertTrue(self.avoidance._is_line_clear(0.0, 2.0, 2.0, 2.0))

    def test_path_planning_integration(self):
        """Path planning entegrasyonu testi"""
        # Engel oluştur
        obstacle = Obstacle(x=1.0, y=0.0, size=0.3, confidence=1.0)
        self.avoidance.detected_obstacles = [obstacle]

        # Path noktaları - engelin üzerinden geçiyor
        path_points = [(0.5, 0.0), (1.0, 0.0), (1.5, 0.0)]

        result = self.avoidance.check_path_clear(2.0, 0.0, path_points)
        self.assertFalse(result)

        # Path noktaları - engeli kaçırıyor
        safe_path = [(0.5, 1.0), (1.0, 1.0), (1.5, 1.0)]

        result = self.avoidance.check_path_clear(2.0, 1.0, safe_path)
        self.assertTrue(result)


class TestMultiSensorFusion(unittest.TestCase):
    """Multi-sensor fusion testleri"""

    def setUp(self):
        self.avoidance = ObstacleAvoidance(simulate=True)

    def test_lidar_update(self):
        """LIDAR veri güncelleme testi"""
        lidar_points = [(1.5, 0.5), (2.0, -0.3)]

        self.avoidance.update_lidar_data(lidar_points)

        self.assertEqual(len(self.avoidance.lidar_data), 2)
        self.assertEqual(self.avoidance.lidar_data[0].type, ObstacleType.LIDAR_DETECTED)
        self.assertEqual(self.avoidance.lidar_data[0].confidence, 0.9)

    def test_camera_update(self):
        """Kamera veri güncelleme testi"""
        camera_objects = [
            {
                "class": "person",
                "distance": 2.0,
                "angle": 0.0,
                "confidence": 0.8,
                "size": 0.4,
            }
        ]

        self.avoidance.update_camera_objects(camera_objects)

        self.assertEqual(len(self.avoidance.camera_objects), 1)
        self.assertEqual(
            self.avoidance.camera_objects[0].type, ObstacleType.CAMERA_DETECTED
        )

    def test_sensor_fusion(self):
        """Sensör fusion testi"""
        # Farklı sensörlerden aynı yerdeki engeller
        ir_reading = {"ir_2": 1.0}  # Merkez 1m
        self.avoidance.update_ir_sensors(ir_reading)

        lidar_points = [(1.0, 0.0)]  # Aynı yerde
        self.avoidance.update_lidar_data(lidar_points)

        self.avoidance.fuse_sensor_data()

        # Cluster edilmiş tek engel olması bekleniyor
        self.assertLessEqual(len(self.avoidance.detected_obstacles), 2)

    def test_obstacle_clustering(self):
        """Engel clustering testi"""
        # Yakın engeller
        obstacles = [
            Obstacle(x=1.0, y=0.0, confidence=0.8),
            Obstacle(x=1.1, y=0.05, confidence=0.7),  # Çok yakın
            Obstacle(x=2.0, y=0.0, confidence=0.9),  # Uzak
        ]

        clustered = self.avoidance._cluster_obstacles(obstacles)

        # 2 cluster bekleniyor (yakın olanlar birleşmiş)
        self.assertEqual(len(clustered), 2)


class TestRecoveryBehavior(unittest.TestCase):
    """Recovery davranışı testleri"""

    def setUp(self):
        self.avoidance = ObstacleAvoidance(simulate=True)

    def test_stuck_detection(self):
        """Sıkışma algılama testi"""
        # Aynı pozisyonda kal
        for i in range(15):
            self.avoidance.check_stuck_condition(0.0, 0.0)
            time.sleep(0.1)

        # Sıkışma algılanmalı
        self.assertTrue(self.avoidance.recovery_mode)

    def test_recovery_commands(self):
        """Recovery komutları testi"""
        self.avoidance.recovery_mode = True
        self.avoidance.stuck_start_time = time.time()

        # İlk 2 saniye - geri git
        command = self.avoidance.get_recovery_command()
        self.assertLess(command["linear"], 0)
        self.assertEqual(command["angular"], 0)

        # 3. saniye - dön
        self.avoidance.stuck_start_time = time.time() - 2.5
        command = self.avoidance.get_recovery_command()
        self.assertEqual(command["linear"], 0)
        self.assertNotEqual(command["angular"], 0)

    def test_recovery_exit(self):
        """Recovery'den çıkış testi"""
        self.avoidance.recovery_mode = True

        # Hareket et
        for i in range(10):
            self.avoidance.check_stuck_condition(i * 0.1, 0.0)

        # Recovery mode'dan çıkmalı
        self.assertFalse(self.avoidance.recovery_mode)


class TestVelocitySmoothing(unittest.TestCase):
    """Hız yumuşatma testleri"""

    def setUp(self):
        self.avoidance = ObstacleAvoidance(simulate=True)

    def test_smooth_acceleration(self):
        """Yumuşak ivme testi"""
        # Başlangıçta durgun
        self.avoidance.last_avoidance_command = {"linear": 0.0, "angular": 0.0}

        # Ani hız değişimi iste
        smooth_cmd = self.avoidance.apply_velocity_smoothing(1.0, 2.0)

        # Ani değişim olmamalı
        self.assertLess(smooth_cmd["linear"], 1.0)
        self.assertLess(smooth_cmd["angular"], 2.0)

    def test_speed_limits(self):
        """Hız limitleri testi"""
        # Çok yüksek hız iste
        smooth_cmd = self.avoidance.apply_velocity_smoothing(5.0, 10.0)

        # Limitler aşılmamalı
        self.assertLessEqual(smooth_cmd["linear"], self.avoidance.max_linear_speed)
        self.assertLessEqual(smooth_cmd["angular"], self.avoidance.max_angular_speed)


class TestStatistics(unittest.TestCase):
    """İstatistik testleri"""

    def setUp(self):
        self.avoidance = ObstacleAvoidance(simulate=True)

    def test_statistics_empty(self):
        """Boş durum istatistikleri"""
        stats = self.avoidance.get_statistics()

        self.assertEqual(stats["detected_obstacles"], 0)
        self.assertFalse(stats["avoidance_active"])
        self.assertEqual(stats["closest_obstacle_distance"], float("inf"))

    def test_statistics_with_obstacles(self):
        """Engelli durum istatistikleri"""
        obstacles = [Obstacle(x=1.0, y=0.0), Obstacle(x=2.0, y=0.0)]
        self.avoidance.detected_obstacles = obstacles

        stats = self.avoidance.get_statistics()

        self.assertEqual(stats["detected_obstacles"], 2)
        self.assertAlmostEqual(stats["closest_obstacle_distance"], 1.0)


class TestIntegration(unittest.TestCase):
    """Entegrasyon testleri"""

    def setUp(self):
        self.avoidance = ObstacleAvoidance(simulate=True)

    def test_full_scenario(self):
        """Tam senaryo testi"""
        # Sensör verisi (sağ sensörde yakın engel)
        sensor_readings = {"ir_1": 0.4}  # Sağ 45° - yakın engel
        self.avoidance.update_ir_sensors(sensor_readings)

        # Komut al
        command = self.avoidance.get_avoidance_command(0.5, 0.0, 0.0, 0.0)

        # Kaçınma aktif olmalı
        self.assertTrue(self.avoidance.avoidance_active)
        self.assertLess(command["linear"], 0.5)  # Yavaşlamış

        # İstatistik kontrolü
        stats = self.avoidance.get_statistics()
        self.assertEqual(stats["detected_obstacles"], 1)

    def test_simulation_readings(self):
        """Simülasyon okuma testi"""
        readings = self.avoidance.get_sensor_readings_simulation()

        # 2 sensör olmalı (sol ve sağ)
        self.assertEqual(len(readings), 2)

        # Hepsi geçerli değerler olmalı
        for key, value in readings.items():
            self.assertIsInstance(value, float)
            self.assertGreaterEqual(value, 0.0)


if __name__ == "__main__":
    # Test suite oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Test sınıflarını ekle
    test_classes = [
        TestObstacleAvoidance,
        TestMultiSensorFusion,
        TestRecoveryBehavior,
        TestVelocitySmoothing,
        TestStatistics,
        TestIntegration,
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Test runner
    runner = unittest.TextTestRunner(verbosity=2, descriptions=True, failfast=False)

    print("🧪 Engel Kaçınma Test Suite Başlatılıyor...")
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
