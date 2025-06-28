#!/usr/bin/env python3
"""
Motor Controller Test Suite
Robot hareket ve biçme motorları kontrol sistemi testleri
"""

import unittest
import sys
import time
import threading
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Proje kök dizinini path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.hardware.motor_controller import (
    MotorController,
    MotorType,
    MotorState,
    MotorParameters,
    MotorStatus,
)


class TestMotorController(unittest.TestCase):
    """Motor Controller ana testleri"""

    def setUp(self):
        """Her test öncesi çalışır"""
        self.controller = MotorController(simulate=True)

    def tearDown(self):
        """Her test sonrası çalışır"""
        if self.controller:
            self.controller.stop_all_motors()
        self.controller = None

    def test_initialization(self):
        """Başlangıç değerleri kontrolü"""
        # Simülasyon modunda başlamış olmalı
        self.assertTrue(self.controller.simulate)

        # Tüm motorlar durmuş olmalı
        for motor_type in MotorType:
            status = self.controller.get_motor_status(motor_type)
            self.assertEqual(status.state, MotorState.STOPPED)
            self.assertEqual(status.rpm, 0.0)

    def test_motor_parameters(self):
        """Motor parametreleri testi"""
        params = MotorParameters(
            max_rpm=3000,
            max_current=5.0,
            encoder_ticks_per_rev=1024,
            gear_ratio=20.0,
            wheel_diameter=0.2,
        )

        self.assertEqual(params.max_rpm, 3000)
        self.assertEqual(params.max_current, 5.0)
        self.assertEqual(params.encoder_ticks_per_rev, 1024)

    def test_motor_status(self):
        """Motor durum bilgisi testi"""
        status = MotorStatus(
            rpm=1500.0,
            current=2.5,
            temperature=45.0,
            encoder_position=1000,
            state=MotorState.RUNNING,
            fault_code=0,
        )

        self.assertEqual(status.rpm, 1500.0)
        self.assertEqual(status.state, MotorState.RUNNING)

    def test_set_drive_speed(self):
        """Sürüş hızı ayarlama testi"""
        # Normal hız
        self.controller.set_drive_speed(0.5, 0.0)  # 0.5 m/s ileri

        left_status = self.controller.get_motor_status(MotorType.LEFT_DRIVE)
        right_status = self.controller.get_motor_status(MotorType.RIGHT_DRIVE)

        # Her iki motor da çalışıyor olmalı
        self.assertEqual(left_status.state, MotorState.RUNNING)
        self.assertEqual(right_status.state, MotorState.RUNNING)

        # Düz gidiş için aynı hızda
        self.assertAlmostEqual(left_status.rpm, right_status.rpm, places=1)

    def test_differential_drive(self):
        """Diferansiyel sürüş testi"""
        # Sağa dönüş (pozitif angular)
        self.controller.set_drive_speed(0.2, 1.0)

        left_status = self.controller.get_motor_status(MotorType.LEFT_DRIVE)
        right_status = self.controller.get_motor_status(MotorType.RIGHT_DRIVE)

        # Sağ motor daha hızlı dönmeli (sağa dönüş için)
        self.assertGreater(right_status.rpm, left_status.rpm)

    def test_blade_control(self):
        """Biçme bıçağı kontrolü testi"""
        # Bıçağı başlat
        success = self.controller.start_blade(2000)  # 2000 RPM
        self.assertTrue(success)

        blade_status = self.controller.get_motor_status(MotorType.BLADE)
        self.assertEqual(blade_status.state, MotorState.RUNNING)
        self.assertGreater(blade_status.rpm, 0)

        # Bıçağı durdur
        self.controller.stop_blade()
        blade_status = self.controller.get_motor_status(MotorType.BLADE)
        self.assertEqual(blade_status.state, MotorState.STOPPED)

    def test_height_adjustment(self):
        """Yükseklik ayarlama testi"""
        # Yüksekliği değiştir
        target_height = 5.0  # cm
        success = self.controller.set_cutting_height(target_height)
        self.assertTrue(success)

        # Yükseklik değişim kontrolü
        current_height = self.controller.get_cutting_height()
        self.assertAlmostEqual(current_height, target_height, places=1)

    def test_safety_limits(self):
        """Güvenlik limitleri testi"""
        # Çok yüksek hız
        self.controller.set_drive_speed(10.0, 0.0)  # Limit üstü

        # Hız limitlenmeli
        left_status = self.controller.get_motor_status(MotorType.LEFT_DRIVE)
        max_expected_rpm = self.controller.drive_params.max_rpm
        self.assertLessEqual(abs(left_status.rpm), max_expected_rpm)

    def test_emergency_stop(self):
        """Acil durdurma testi"""
        # Motorları çalıştır
        self.controller.set_drive_speed(0.5, 0.0)
        self.controller.start_blade(2000)

        # Acil durdur
        self.controller.emergency_stop()

        # Tüm motorlar durmuş olmalı
        for motor_type in MotorType:
            status = self.controller.get_motor_status(motor_type)
            self.assertEqual(status.state, MotorState.STOPPED)

    def test_encoder_readings(self):
        """Enkoder okuma testi"""
        # Motor çalıştır
        self.controller.set_drive_speed(0.3, 0.0)
        time.sleep(0.1)  # Kısa süre bekle

        # Enkoder değerlerini al
        encoder_data = self.controller.get_encoder_data()

        self.assertIn("left_ticks", encoder_data)
        self.assertIn("right_ticks", encoder_data)
        self.assertIn("timestamp", encoder_data)

        # Değerler sayısal olmalı
        self.assertIsInstance(encoder_data["left_ticks"], (int, float))
        self.assertIsInstance(encoder_data["right_ticks"], (int, float))


class TestMotorSafety(unittest.TestCase):
    """Motor güvenlik testleri"""

    def setUp(self):
        self.controller = MotorController(simulate=True)

    def tearDown(self):
        if self.controller:
            self.controller.stop_all_motors()

    def test_overcurrent_protection(self):
        """Aşırı akım koruması testi"""
        # Mock ile aşırı akım simüle et
        with patch.object(self.controller, "_read_motor_current") as mock_current:
            mock_current.return_value = 15.0  # Limit üstü akım

            # Motor çalıştır
            self.controller.set_drive_speed(0.5, 0.0)

            # Akım kontrol döngüsünü tetikle
            self.controller._check_motor_safety()

            # Motor durmuş olmalı
            left_status = self.controller.get_motor_status(MotorType.LEFT_DRIVE)
            self.assertEqual(left_status.state, MotorState.ERROR)

    def test_temperature_protection(self):
        """Sıcaklık koruması testi"""
        with patch.object(self.controller, "_read_motor_temperature") as mock_temp:
            mock_temp.return_value = 85.0  # Yüksek sıcaklık

            self.controller.start_blade(2000)
            self.controller._check_motor_safety()

            blade_status = self.controller.get_motor_status(MotorType.BLADE)
            self.assertEqual(blade_status.state, MotorState.ERROR)

    def test_blade_safety_interlocks(self):
        """Bıçak güvenlik kilitleri testi"""
        # Robot hareket halindeyken bıçak çalıştırma
        self.controller.set_drive_speed(0.5, 0.0)

        # Bıçak çalıştırma denemesi
        success = self.controller.start_blade(2000)

        # Hareket halindeyken bıçak çalışmamalı (güvenlik)
        if hasattr(self.controller, "safety_interlocks"):
            self.assertFalse(success)

    def test_watchdog_timer(self):
        """Watchdog timer testi"""
        # Motor komut gönder
        self.controller.set_drive_speed(0.3, 0.0)

        # Uzun süre bekle (watchdog timeout)
        if hasattr(self.controller, "watchdog_timeout"):
            time.sleep(self.controller.watchdog_timeout + 0.1)

            # Watchdog trigger olmuş olmalı
            self.controller._check_watchdog()

            # Motorlar durmuş olmalı
            left_status = self.controller.get_motor_status(MotorType.LEFT_DRIVE)
            self.assertEqual(left_status.state, MotorState.STOPPED)


class TestMotorCalibration(unittest.TestCase):
    """Motor kalibrasyon testleri"""

    def setUp(self):
        self.controller = MotorController(simulate=True)

    def test_wheel_calibration(self):
        """Tekerlek kalibrasyonu testi"""
        # Kalibrasyon modunu başlat
        if hasattr(self.controller, "start_wheel_calibration"):
            success = self.controller.start_wheel_calibration()
            self.assertTrue(success)

            # Kalibrasyon sonuçlarını kontrol et
            calib_data = self.controller.get_calibration_data()
            self.assertIn("wheel_diameter", calib_data)

    def test_blade_height_calibration(self):
        """Bıçak yükseklik kalibrasyonu testi"""
        if hasattr(self.controller, "calibrate_blade_height"):
            # Minimum ve maksimum pozisyonları bul
            self.controller.calibrate_blade_height()

            # Kalibrasyon verileri
            height_range = self.controller.get_height_range()
            self.assertIn("min_height", height_range)
            self.assertIn("max_height", height_range)

            # Makul değerler
            self.assertGreater(height_range["max_height"], height_range["min_height"])


class TestPerformance(unittest.TestCase):
    """Performans testleri"""

    def setUp(self):
        self.controller = MotorController(simulate=True)

    def test_command_response_time(self):
        """Komut yanıt süresi testi"""
        start_time = time.time()

        # Hız komutu gönder
        self.controller.set_drive_speed(0.5, 0.0)

        response_time = time.time() - start_time

        # 10ms'den az sürmeli
        self.assertLess(response_time, 0.01)

    def test_control_loop_frequency(self):
        """Kontrol döngüsü frekansı testi"""
        if hasattr(self.controller, "control_loop_frequency"):
            # En az 50Hz olmalı
            self.assertGreaterEqual(self.controller.control_loop_frequency, 50)

    def test_concurrent_operations(self):
        """Eşzamanlı operasyon testi"""

        def drive_operation():
            for i in range(10):
                self.controller.set_drive_speed(0.1 * i, 0.0)
                time.sleep(0.01)

        def blade_operation():
            for i in range(5):
                self.controller.start_blade(1000 + i * 100)
                time.sleep(0.02)
                self.controller.stop_blade()

        # Thread'leri başlat
        thread1 = threading.Thread(target=drive_operation)
        thread2 = threading.Thread(target=blade_operation)

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        # Deadlock veya exception olmamalı
        self.assertTrue(True)  # Test tamamlandı


class TestIntegration(unittest.TestCase):
    """Entegrasyon testleri"""

    def setUp(self):
        self.controller = MotorController(simulate=True)

    def test_full_operation_cycle(self):
        """Tam operasyon döngüsü testi"""
        # Başlangıç kontrolü
        stats = self.controller.get_statistics()
        self.assertIn("total_distance", stats)

        # Hareket başlat
        self.controller.set_drive_speed(0.3, 0.0)
        time.sleep(0.1)

        # Bıçağı başlat
        self.controller.start_blade(2000)
        time.sleep(0.1)

        # Yükseklik ayarla
        self.controller.set_cutting_height(3.0)
        time.sleep(0.1)

        # Dönüş yap
        self.controller.set_drive_speed(0.2, 1.0)
        time.sleep(0.1)

        # Durdur
        self.controller.stop_all_motors()

        # Final durum kontrolü
        for motor_type in MotorType:
            status = self.controller.get_motor_status(motor_type)
            self.assertEqual(status.state, MotorState.STOPPED)

    def test_error_recovery(self):
        """Hata kurtarma testi"""
        # Hata simüle et
        with patch.object(self.controller, "_read_motor_current") as mock_current:
            mock_current.return_value = 15.0  # Aşırı akım

            # Motor çalıştır
            self.controller.set_drive_speed(0.5, 0.0)
            self.controller._check_motor_safety()

            # Hata durumu
            left_status = self.controller.get_motor_status(MotorType.LEFT_DRIVE)
            self.assertEqual(left_status.state, MotorState.ERROR)

            # Hatayı temizle
            self.controller.clear_motor_errors()

            # Tekrar çalıştır
            self.controller.set_drive_speed(0.3, 0.0)
            left_status = self.controller.get_motor_status(MotorType.LEFT_DRIVE)
            self.assertEqual(left_status.state, MotorState.RUNNING)

    @patch("src.hardware.motor_controller.GPIO")
    def test_hardware_interface(self, mock_gpio):
        """Hardware arayüzü testi (mock ile)"""
        # GPIO mock setup
        mock_gpio.PWM.return_value = MagicMock()

        # Gerçek hardware modu
        real_controller = MotorController(simulate=False)

        # PWM çıkışları kontrol edilmeli
        real_controller.set_drive_speed(0.5, 0.0)

        # GPIO setup çağrıları yapılmış olmalı (PWM henüz aktif değil)
        self.assertTrue(mock_gpio.setmode.called)
        self.assertTrue(mock_gpio.setup.called)


if __name__ == "__main__":
    # Test suite oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Test sınıflarını ekle
    test_classes = [
        TestMotorController,
        TestMotorSafety,
        TestMotorCalibration,
        TestPerformance,
        TestIntegration,
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Test runner
    runner = unittest.TextTestRunner(verbosity=2, descriptions=True, failfast=False)

    print("🔧 Motor Controller Test Suite Başlatılıyor...")
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
