#!/usr/bin/env python3
"""
Kalman Odometry Test Suite
Kalman         dt = 0.1
        predicted_state = self.odometry.predict_state(dt)

        # Hareket olmalı (velocity > 0)
        self.assertGreater(predicted_state["x"], 0.0)  # x position
        self.assertGreater(predicted_state["heading"], 0.0)  # heading

        # Velocity'ler değişmemeli (constant velocity model)
        self.assertEqual(predicted_state["vx"], 1.0)  # vx
        self.assertEqual(predicted_state["angular_velocity"], 0.1)  # omega
"""

import unittest
import numpy as np
import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch

# Proje kök dizinini path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.navigation.kalman_odometry import KalmanOdometry, Position


class TestKalmanOdometry(unittest.TestCase):
    """Kalman Odometry ana testleri"""

    def setUp(self):
        """Her test öncesi çalışır"""
        self.odometry = KalmanOdometry(simulate=True)

    def tearDown(self):
        """Her test sonrası çalışır"""
        self.odometry = None

    def test_initialization(self):
        """Başlangıç değerleri kontrolü"""
        # State vector başlangıç kontrolü
        self.assertEqual(len(self.odometry.state), 6)
        np.testing.assert_array_almost_equal(self.odometry.state, np.zeros(6))

        # Covariance matrix kontrolü
        self.assertEqual(self.odometry.P.shape, (6, 6))

        # Process noise kontrolü
        self.assertEqual(self.odometry.Q.shape, (6, 6))

        # Simulation mode kontrolü
        self.assertTrue(self.odometry.simulate)

    def test_position_dataclass(self):
        """Position dataclass testi"""
        pos = Position(x=1.0, y=2.0, heading=0.5, timestamp=time.time())

        self.assertEqual(pos.x, 1.0)
        self.assertEqual(pos.y, 2.0)
        self.assertEqual(pos.heading, 0.5)
        self.assertIsInstance(pos.timestamp, float)

    def test_state_prediction(self):
        """State prediction testi"""
        # Başlangıç state'i
        initial_state = np.array([0.0, 0.0, 0.0, 1.0, 0.0, 0.5])
        self.odometry.state = initial_state.copy()

        dt = 0.1
        predicted_state = self.odometry.predict_state(dt)

        # Hareket olmalı (velocity > 0)
        self.assertGreater(predicted_state["x"], 0.0)  # x position
        self.assertGreater(predicted_state["heading"], 0.0)  # heading

        # Velocity'ler değişmemeli (constant velocity model)
        self.assertEqual(predicted_state["vx"], 1.0)  # vx
        self.assertEqual(predicted_state["angular_velocity"], 0.5)  # omega

    def test_encoder_update(self):
        """Encoder veri güncellemesi testi"""
        # Encoder verisi
        encoder_data = {"left_ticks": 100, "right_ticks": 120, "timestamp": time.time()}

        initial_position = self.odometry.get_position()

        # Update yap
        self.odometry.update_from_encoder(encoder_data)

        new_position = self.odometry.get_position()

        # Pozisyon değişmiş olmalı
        self.assertNotEqual(initial_position.x, new_position.x)

    def test_imu_update(self):
        """IMU veri güncellemesi testi"""
        # IMU verisi
        imu_data = {
            "gyro_z": 0.1,  # rad/s
            "accel_x": 0.5,  # m/s²
            "accel_y": 0.0,
            "heading": 0.2,  # radyan
            "timestamp": time.time(),
        }

        initial_heading = self.odometry.state[2]

        # Update yap
        self.odometry.update_from_imu(imu_data)

        new_heading = self.odometry.state[2]

        # Heading güncellenmiş olmalı
        self.assertNotEqual(initial_heading, new_heading)

    def test_get_position(self):
        """Pozisyon alma testi"""
        # State'i set et
        self.odometry.state = np.array([1.5, 2.5, 0.785, 0.0, 0.0, 0.0])

        position = self.odometry.get_position()

        self.assertAlmostEqual(position.x, 1.5, places=2)
        self.assertAlmostEqual(position.y, 2.5, places=2)
        self.assertAlmostEqual(position.heading, 0.785, places=3)
        self.assertIsInstance(position.timestamp, float)

    def test_reset_position(self):
        """Pozisyon reset testi"""
        # State'i değiştir
        self.odometry.state = np.array([5.0, 5.0, 1.57, 1.0, 1.0, 0.5])

        # Reset et
        self.odometry.reset_position()

        # Sıfırlanmış olmalı
        np.testing.assert_array_almost_equal(self.odometry.state[:3], np.zeros(3))

    def test_set_position(self):
        """Pozisyon set etme testi"""
        new_pos = Position(x=3.0, y=4.0, heading=1.57)

        self.odometry.set_position(new_pos.x, new_pos.y, new_pos.heading)

        self.assertAlmostEqual(self.odometry.state[0], 3.0)
        self.assertAlmostEqual(self.odometry.state[1], 4.0)
        self.assertAlmostEqual(self.odometry.state[2], 1.57)


class TestKalmanFilter(unittest.TestCase):
    """Kalman filtre algoritması testleri"""

    def setUp(self):
        self.odometry = KalmanOdometry(simulate=True)

    def test_prediction_step(self):
        """Prediction step testi"""
        initial_P = self.odometry.P.copy()
        initial_state = self.odometry.state.copy()

        dt = 0.1
        self.odometry.prediction_step(dt)

        # State değişmiş olabilir (velocity varsa)
        # Covariance artmış olmalı (uncertainty increases)
        self.assertGreaterEqual(np.trace(self.odometry.P), np.trace(initial_P))

    def test_correction_step(self):
        """Correction step testi"""
        # Measurement
        z = np.array([1.0, 1.0, 0.1])  # x, y, heading measurement
        H = np.array(
            [[1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0]]
        )  # Measurement matrix
        R = self.odometry.R_encoder

        initial_P = self.odometry.P.copy()

        self.odometry.correction_step(z, H, R)

        # Covariance azalmış olmalı (uncertainty decreases)
        self.assertLessEqual(np.trace(self.odometry.P), np.trace(initial_P))

    def test_encoder_to_position(self):
        """Encoder tick'lerinden pozisyon hesaplama testi"""
        # Test parametreleri
        left_ticks = 100
        right_ticks = 100  # Düz hareket

        # Pozisyon hesapla
        result = self.odometry.encoder_to_position(left_ticks, right_ticks)
        dx, dy, dtheta = result["dx"], result["dy"], result["dheading"]

        # Düz hareket için
        self.assertGreater(dx, 0)  # İleri hareket
        self.assertAlmostEqual(dy, 0, places=3)  # Yana hareket yok
        self.assertAlmostEqual(dtheta, 0, places=3)  # Dönüş yok

    def test_encoder_differential(self):
        """Diferansiyel enkoder hareketi testi"""
        left_ticks = 50
        right_ticks = 100  # Sağ tekerlek daha hızlı → sola dönüş

        result = self.odometry.encoder_to_position(left_ticks, right_ticks)
        dx, dy, dtheta = result["dx"], result["dy"], result["dheading"]

        # Sağ tekerlek daha hızlı için
        self.assertGreater(dx, 0)  # İleri hareket var
        self.assertGreater(dtheta, 0)  # Sola dönüş (pozitif)


class TestNumericalStability(unittest.TestCase):
    """Sayısal kararlılık testleri"""

    def setUp(self):
        self.odometry = KalmanOdometry(simulate=True)

    def test_matrix_symmetry(self):
        """Covariance matrix simetri testi"""
        # Birkaç update yap
        for i in range(10):
            dt = 0.1
            self.odometry.prediction_step(dt)

            # Measurement
            z = np.array([i * 0.1, i * 0.1, 0.0])
            H = np.eye(3, 6)
            self.odometry.correction_step(z, H, self.odometry.R_encoder)

        # P matrisi simetrik olmalı
        np.testing.assert_array_almost_equal(
            self.odometry.P, self.odometry.P.T, decimal=10
        )

    def test_positive_definite(self):
        """Covariance matrix pozitif tanımlı testi"""
        # Birkaç update yap
        for i in range(5):
            dt = 0.1
            self.odometry.prediction_step(dt)

        # Eigenvalue'lar pozitif olmalı
        eigenvalues = np.linalg.eigvals(self.odometry.P)
        self.assertTrue(np.all(eigenvalues > 0))

    def test_numerical_overflow(self):
        """Sayısal taşma testi"""
        # Çok büyük değerlerle test
        self.odometry.state = np.array([1e6, 1e6, 1000, 100, 100, 10])

        dt = 1.0
        try:
            self.odometry.prediction_step(dt)
            # NaN veya inf kontrolü
            self.assertFalse(np.any(np.isnan(self.odometry.state)))
            self.assertFalse(np.any(np.isinf(self.odometry.state)))
        except Exception as e:
            self.fail(f"Numerical overflow occurred: {e}")


class TestIntegration(unittest.TestCase):
    """Entegrasyon testleri"""

    def setUp(self):
        self.odometry = KalmanOdometry(simulate=True)

    def test_full_update_cycle(self):
        """Tam güncelleme döngüsü testi"""
        # Başlangıç pozisyonu
        initial_pos = self.odometry.get_position()

        # Encoder update
        encoder_data = {"left_ticks": 200, "right_ticks": 200, "timestamp": time.time()}
        self.odometry.update_from_encoder(encoder_data)

        # IMU update
        imu_data = {
            "gyro_z": 0.0,
            "accel_x": 1.0,
            "accel_y": 0.0,
            "heading": 0.0,
            "timestamp": time.time(),
        }
        self.odometry.update_from_imu(imu_data)

        # Final pozisyon
        final_pos = self.odometry.get_position()

        # Pozisyon değişmiş olmalı
        self.assertNotEqual(initial_pos.x, final_pos.x)

    def test_timestamp_handling(self):
        """Timestamp işleme testi"""
        current_time = time.time()

        # Geçmişten veri
        old_data = {
            "left_ticks": 100,
            "right_ticks": 100,
            "timestamp": current_time - 1.0,
        }

        # Normal veri
        new_data = {"left_ticks": 150, "right_ticks": 150, "timestamp": current_time}

        # Eski veri önce
        self.odometry.update_from_encoder(old_data)
        pos1 = self.odometry.get_position()

        # Yeni veri sonra
        self.odometry.update_from_encoder(new_data)
        pos2 = self.odometry.get_position()

        # İkinci pozisyon daha ileri olmalı
        self.assertGreater(pos2.x, pos1.x)

    def test_simulation_vs_real(self):
        """Simülasyon vs gerçek mod testi"""
        sim_odometry = KalmanOdometry(simulate=True)
        real_odometry = KalmanOdometry(simulate=False)

        # Her ikisi de çalışmalı
        self.assertTrue(sim_odometry.simulate)
        self.assertFalse(real_odometry.simulate)

        # Temel fonksiyonlar çalışmalı
        sim_pos = sim_odometry.get_position()
        real_pos = real_odometry.get_position()

        self.assertIsInstance(sim_pos, Position)
        self.assertIsInstance(real_pos, Position)


class TestStatistics(unittest.TestCase):
    """İstatistik ve performans testleri"""

    def setUp(self):
        self.odometry = KalmanOdometry(simulate=True)

    def test_get_statistics(self):
        """İstatistik alma testi"""
        stats = self.odometry.get_statistics()

        required_keys = [
            "position",
            "velocity",
            "covariance_trace",
            "last_update",
            "filter_stable",
        ]

        for key in required_keys:
            self.assertIn(key, stats)

        # Değer tipleri
        self.assertIsInstance(stats["position"], dict)
        self.assertIsInstance(stats["velocity"], dict)
        self.assertIsInstance(stats["covariance_trace"], float)
        self.assertIsInstance(stats["filter_stable"], bool)

    def test_performance_timing(self):
        """Performans timing testi"""
        start_time = time.time()

        # 100 update yap
        for i in range(100):
            encoder_data = {
                "left_ticks": i,
                "right_ticks": i + 1,
                "timestamp": time.time(),
            }
            self.odometry.update_from_encoder(encoder_data)

        total_time = time.time() - start_time
        avg_time = total_time / 100

        # Her update 10ms'den az sürmeli
        self.assertLess(avg_time, 0.01)

    def test_memory_usage(self):
        """Bellek kullanımı testi"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Çok sayıda update
        for i in range(1000):
            self.odometry.prediction_step(0.1)

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory leak kontrolü (10MB'dan az artış)
        self.assertLess(memory_increase, 10 * 1024 * 1024)


if __name__ == "__main__":
    # Test suite oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Test sınıflarını ekle
    test_classes = [
        TestKalmanOdometry,
        TestKalmanFilter,
        TestNumericalStability,
        TestIntegration,
        TestStatistics,
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Test runner
    runner = unittest.TextTestRunner(verbosity=2, descriptions=True, failfast=False)

    print("🧮 Kalman Odometry Test Suite Başlatılıyor...")
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
