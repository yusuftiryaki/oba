# 🎯 Sensör Kalibrasyon Prosedürleri

## BNO055 IMU Kalibrasyonu

### 📊 Kalibrasyon Temelleri

BNO055 IMU, dahili olarak 4 farklı sensör türü kalibre eder:
- **Magnetometer**: Manyetik alan sensörü (pusula)
- **Accelerometer**: İvme sensörü (yer çekimi)
- **Gyroscope**: Açısal hız sensörü
- **System**: Tüm sensörlerin birleşik kalibrasyonu

#### Kalibrasyon Seviyeleri (0-3)
- **0**: Kalibrasyon yok
- **1**: Düşük kalibrasyon
- **2**: Orta kalibrasyon
- **3**: Tam kalibrasyon ✅

### 🔧 Otomatik Kalibrasyon Scripti

```python
#!/usr/bin/env python3
"""BNO055 IMU Kalibrasyon Scripti - Hacı Abi"""

import adafruit_bno055
import board
import busio
import time
import json
import numpy as np

class IMUCalibrator:
    def __init__(self):
        # I2C bağlantısı
        i2c = busio.I2C(board.SCL, board.SDA)
        self.bno = adafruit_bno055.BNO055_I2C(i2c)

        # Kalibrasyon verileri
        self.calibration_data = {}
        self.mag_samples = []
        self.accel_samples = []

    def start_calibration(self):
        """Tam kalibrasyon sürecini başlat"""
        print("🧭 Hacı Abi'nin IMU Kalibrasyonu Başlıyor!")
        print("=" * 50)

        # 1. Sistem durumu kontrolü
        self.check_sensor_status()

        # 2. Magnetometer kalibrasyonu
        self.calibrate_magnetometer()

        # 3. Accelerometer kalibrasyonu
        self.calibrate_accelerometer()

        # 4. Gyroscope kalibrasyonu
        self.calibrate_gyroscope()

        # 5. Sistem kalibrasyonu
        self.calibrate_system()

        # 6. Kalibrasyon verilerini kaydet
        self.save_calibration()

        print("🎯 Kalibrasyon tamamlandı!")

    def check_sensor_status(self):
        """Sensör durumunu kontrol et"""
        print("📋 Sensör durumu kontrol ediliyor...")

        status = self.bno.calibration_status
        sys_cal, gyro_cal, accel_cal, mag_cal = status

        print(f"  System: {sys_cal}/3")
        print(f"  Gyroscope: {gyro_cal}/3")
        print(f"  Accelerometer: {accel_cal}/3")
        print(f"  Magnetometer: {mag_cal}/3")

        # Sıcaklık kontrolü
        temp = self.bno.temperature
        print(f"  Sıcaklık: {temp}°C")

        if temp > 60:
            print("⚠️ Dikkat: Yüksek sıcaklık! Soğumasını bekle.")
            return False

        return True

    def calibrate_magnetometer(self):
        """Manyetometre kalibrasyonu"""
        print("\n🧭 Magnetometer Kalibrasyonu")
        print("Robotu yavaşça 360° çevirin...")
        print("X, Y, Z eksenlerinde farklı açılarda tutun")

        target_samples = 100
        sample_count = 0

        while sample_count < target_samples:
            try:
                # Magnetometer verisi oku
                mag_data = self.bno.magnetic
                if mag_data and all(val is not None for val in mag_data):
                    self.mag_samples.append(mag_data)
                    sample_count += 1

                    # İlerleme göster
                    progress = (sample_count / target_samples) * 100
                    print(f"\rİlerleme: {progress:.1f}% ({sample_count}/{target_samples})", end="")

                    # Kalibrasyon seviyesi kontrol
                    status = self.bno.calibration_status
                    if status[3] >= 3:  # Magnetometer tam kalibre
                        print(f"\n✅ Magnetometer kalibrasyonu tamamlandı!")
                        break

                time.sleep(0.1)

            except Exception as e:
                print(f"\n❌ Hata: {e}")
                continue

        # İstatistikleri hesapla
        if self.mag_samples:
            mag_array = np.array(self.mag_samples)
            mag_mean = np.mean(mag_array, axis=0)
            mag_std = np.std(mag_array, axis=0)

            print(f"\nMagnetometer İstatistikleri:")
            print(f"  Ortalama: X={mag_mean[0]:.2f}, Y={mag_mean[1]:.2f}, Z={mag_mean[2]:.2f}")
            print(f"  Std. Sapma: X={mag_std[0]:.2f}, Y={mag_std[1]:.2f}, Z={mag_std[2]:.2f}")

    def calibrate_accelerometer(self):
        """İvmeölçer kalibrasyonu"""
        print("\n📐 Accelerometer Kalibrasyonu")

        positions = [
            ("Düz yatay", "Z ekseni yukarı"),
            ("Sağ yana yatır", "X ekseni yukarı"),
            ("Sol yana yatır", "X ekseni aşağı"),
            ("Öne eğ", "Y ekseni yukarı"),
            ("Arkaya eğ", "Y ekseni aşağı"),
            ("Ters çevir", "Z ekseni aşağı")
        ]

        for position, instruction in positions:
            print(f"\n📍 Pozisyon: {position}")
            print(f"   {instruction}")
            input("   Hazır olduğunuzda ENTER'a basın...")

            # Bu pozisyonda örnekler al
            samples = []
            for i in range(20):
                accel_data = self.bno.acceleration
                if accel_data and all(val is not None for val in accel_data):
                    samples.append(accel_data)
                    print(f"\rÖrnek {i+1}/20", end="")
                time.sleep(0.1)

            # Ortalama hesapla
            if samples:
                avg = np.mean(samples, axis=0)
                self.accel_samples.append({
                    'position': position,
                    'data': avg
                })
                print(f"\n   Ortalama: X={avg[0]:.2f}, Y={avg[1]:.2f}, Z={avg[2]:.2f}")

        print("✅ Accelerometer kalibrasyonu tamamlandı!")

    def calibrate_gyroscope(self):
        """Jiroskop kalibrasyonu"""
        print("\n🌀 Gyroscope Kalibrasyonu")
        print("Robotu tamamen sabit tutun...")
        print("Hareket ettirmeyin!")

        # Statik durum için örnekler al
        gyro_samples = []
        for i in range(100):
            gyro_data = self.bno.gyro
            if gyro_data and all(val is not None for val in gyro_data):
                gyro_samples.append(gyro_data)
                progress = ((i+1) / 100) * 100
                print(f"\rİlerleme: {progress:.1f}%", end="")
            time.sleep(0.05)

        if gyro_samples:
            gyro_array = np.array(gyro_samples)
            gyro_mean = np.mean(gyro_array, axis=0)
            gyro_std = np.std(gyro_array, axis=0)

            print(f"\nGyroscope Bias:")
            print(f"  X: {gyro_mean[0]:.4f} ± {gyro_std[0]:.4f} rad/s")
            print(f"  Y: {gyro_mean[1]:.4f} ± {gyro_std[1]:.4f} rad/s")
            print(f"  Z: {gyro_mean[2]:.4f} ± {gyro_std[2]:.4f} rad/s")

            # Bias değerlerini kaydet
            self.calibration_data['gyro_bias'] = gyro_mean.tolist()

            # Kalibrasyon seviyesi kontrol
            status = self.bno.calibration_status
            if status[1] >= 3:
                print("✅ Gyroscope kalibrasyonu tamamlandı!")
            else:
                print("⚠️ Gyroscope kalibrasyonu düşük, tekrar deneyin")

    def calibrate_system(self):
        """Sistem kalibrasyonu"""
        print("\n🎯 Sistem Kalibrasyonu")
        print("Tüm sensörlerin birleşik kalibrasyonu...")

        max_wait = 60  # 60 saniye maksimum
        start_time = time.time()

        while time.time() - start_time < max_wait:
            status = self.bno.calibration_status
            sys_cal, gyro_cal, accel_cal, mag_cal = status

            print(f"\rDurum: Sys={sys_cal}/3, Gyro={gyro_cal}/3, Accel={accel_cal}/3, Mag={mag_cal}/3", end="")

            if sys_cal >= 3:
                print(f"\n✅ Sistem kalibrasyonu tamamlandı!")
                break

            time.sleep(1)
        else:
            print(f"\n⚠️ Sistem kalibrasyonu {max_wait}s içinde tamamlanamadı")

    def save_calibration(self):
        """Kalibrasyon verilerini kaydet"""
        print("\n💾 Kalibrasyon verileri kaydediliyor...")

        try:
            # Kalibrasyon offset'lerini al
            offsets = self.bno.calibration_offsets

            # Kalibrasyon verilerini hazırla
            calib_data = {
                'timestamp': time.time(),
                'offsets': {
                    'accel_offset_x': offsets[0],
                    'accel_offset_y': offsets[1],
                    'accel_offset_z': offsets[2],
                    'mag_offset_x': offsets[3],
                    'mag_offset_y': offsets[4],
                    'mag_offset_z': offsets[5],
                    'gyro_offset_x': offsets[6],
                    'gyro_offset_y': offsets[7],
                    'gyro_offset_z': offsets[8],
                    'accel_radius': offsets[9],
                    'mag_radius': offsets[10]
                },
                'final_status': self.bno.calibration_status,
                'gyro_bias': self.calibration_data.get('gyro_bias', [0, 0, 0])
            }

            # JSON dosyasına yaz
            with open('/home/pi/oba/config/imu_calibration.json', 'w') as f:
                json.dump(calib_data, f, indent=2)

            print("✅ Kalibrasyon verileri kaydedildi!")
            print("📁 Dosya: /home/pi/oba/config/imu_calibration.json")

        except Exception as e:
            print(f"❌ Kayıt hatası: {e}")

    def load_calibration(self):
        """Kayıtlı kalibrasyonu yükle"""
        try:
            with open('/home/pi/oba/config/imu_calibration.json', 'r') as f:
                calib_data = json.load(f)

            # Offset'leri tuple'a çevir
            offsets = calib_data['offsets']
            offset_tuple = (
                offsets['accel_offset_x'], offsets['accel_offset_y'], offsets['accel_offset_z'],
                offsets['mag_offset_x'], offsets['mag_offset_y'], offsets['mag_offset_z'],
                offsets['gyro_offset_x'], offsets['gyro_offset_y'], offsets['gyro_offset_z'],
                offsets['accel_radius'], offsets['mag_radius']
            )

            # Kalibrasyonu uygula
            self.bno.calibration_offsets = offset_tuple

            print("✅ Kalibrasyon verileri yüklendi!")
            return True

        except FileNotFoundError:
            print("⚠️ Kalibrasyon dosyası bulunamadı")
            return False
        except Exception as e:
            print(f"❌ Yükleme hatası: {e}")
            return False


def main():
    """Ana kalibrasyon fonksiyonu"""
    print("🤖 OBA Robot IMU Kalibrasyon Aracı")
    print("=" * 40)

    calibrator = IMUCalibrator()

    choice = input("1) Yeni kalibrasyon\n2) Mevcut kalibrasyonu yükle\nSeçim (1/2): ")

    if choice == '1':
        calibrator.start_calibration()
    elif choice == '2':
        if calibrator.load_calibration():
            # Test ölçümü
            print("Test ölçümü yapılıyor...")
            time.sleep(2)

            accel = calibrator.bno.acceleration
            gyro = calibrator.bno.gyro
            mag = calibrator.bno.magnetic

            print(f"Accelerometer: {accel}")
            print(f"Gyroscope: {gyro}")
            print(f"Magnetometer: {mag}")
    else:
        print("Geçersiz seçim!")

if __name__ == "__main__":
    main()
```

## 📏 Enkoder Kalibrasyonu

### 🔄 Pulse/Tur Hesaplama

```python
#!/usr/bin/env python3
"""Enkoder Kalibrasyon Scripti"""

import RPi.GPIO as GPIO
import time
import json
import numpy as np

class EncoderCalibrator:
    def __init__(self):
        # Encoder pinleri
        self.LEFT_A = 18
        self.LEFT_B = 19
        self.RIGHT_A = 20
        self.RIGHT_B = 21

        # Pulse sayaçları
        self.left_count = 0
        self.right_count = 0

        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([self.LEFT_A, self.LEFT_B, self.RIGHT_A, self.RIGHT_B],
                  GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Interrupt callback'leri
        GPIO.add_event_detect(self.LEFT_A, GPIO.BOTH,
                            callback=self.left_encoder_callback)
        GPIO.add_event_detect(self.RIGHT_A, GPIO.BOTH,
                            callback=self.right_encoder_callback)

    def left_encoder_callback(self, channel):
        """Sol enkoder interrupt"""
        a_state = GPIO.input(self.LEFT_A)
        b_state = GPIO.input(self.LEFT_B)

        if a_state != b_state:
            self.left_count += 1
        else:
            self.left_count -= 1

    def right_encoder_callback(self, channel):
        """Sağ enkoder interrupt"""
        a_state = GPIO.input(self.RIGHT_A)
        b_state = GPIO.input(self.RIGHT_B)

        if a_state != b_state:
            self.right_count += 1
        else:
            self.right_count -= 1

    def calibrate_pulses_per_revolution(self):
        """Tur başına pulse sayısını kalibre et"""
        print("🔄 Enkoder Pulse/Tur Kalibrasyonu")
        print("Motorları manuel olarak tam 1 tur çevirin")

        # Sayaçları sıfırla
        self.left_count = 0
        self.right_count = 0

        input("Sol motoru 1 tur çevirin, sonra ENTER'a basın...")
        left_ppr = abs(self.left_count)
        self.left_count = 0

        input("Sağ motoru 1 tur çevirin, sonra ENTER'a basın...")
        right_ppr = abs(self.right_count)
        self.right_count = 0

        print(f"Sol Enkoder: {left_ppr} pulse/tur")
        print(f"Sağ Enkoder: {right_ppr} pulse/tur")

        return left_ppr, right_ppr

    def calibrate_wheel_distance(self):
        """Tekerlek mesafesi kalibrasyonu"""
        print("📏 Tekerlek Mesafe Kalibrasyonu")

        # Bilinen mesafe için ölçüm
        test_distance = float(input("Test mesafesi (metre): "))

        # Sayaçları sıfırla
        self.left_count = 0
        self.right_count = 0

        input(f"Robotu {test_distance}m düz ileri hareket ettirin, sonra ENTER...")

        left_pulses = abs(self.left_count)
        right_pulses = abs(self.right_count)

        # Pulse/metre hesapla
        left_ppm = left_pulses / test_distance
        right_ppm = right_pulses / test_distance

        print(f"Sol Tekerlek: {left_ppm:.1f} pulse/metre")
        print(f"Sağ Tekerlek: {right_ppm:.1f} pulse/metre")

        # Tekerlek çapını hesapla
        left_ppr = 600  # Varsayılan
        right_ppr = 600

        left_circumference = left_ppr / left_ppm
        right_circumference = right_ppr / right_ppm

        left_diameter = left_circumference / 3.14159
        right_diameter = right_circumference / 3.14159

        print(f"Sol Tekerlek Çapı: {left_diameter:.3f}m")
        print(f"Sağ Tekerlek Çapı: {right_diameter:.3f}m")

        return left_ppm, right_ppm

    def calibrate_wheelbase(self):
        """Tekerlek arası mesafe kalibrasyonu"""
        print("📐 Wheelbase Kalibrasyonu")

        # 360 derece dönüş testi
        print("Robotu tam 360° saat yönünde çevirin")

        self.left_count = 0
        self.right_count = 0

        input("Dönüş tamamlandığında ENTER'a basın...")

        left_pulses = abs(self.left_count)
        right_pulses = abs(self.right_count)

        # Teorik wheelbase hesaplama
        # circumference = pi * wheelbase
        # pulses = circumference * pulses_per_meter

        avg_pulses = (left_pulses + right_pulses) / 2
        ppm = 3000  # Varsayılan pulse/metre

        circumference = avg_pulses / ppm
        wheelbase = circumference / 3.14159

        print(f"Hesaplanan Wheelbase: {wheelbase:.3f}m")

        return wheelbase
```

## 🎯 Kamera Kalibrasyonu

### 📸 Lens Distortion Kalibrasyonu

```python
#!/usr/bin/env python3
"""Kamera Kalibrasyon Scripti"""

import cv2
import numpy as np
import json
import glob

class CameraCalibrator:
    def __init__(self):
        # Satranç tahtası boyutları (iç köşe sayısı)
        self.board_size = (9, 6)  # 9x6 iç köşe
        self.square_size = 0.025  # 25mm kare boyutu

        # 3D nokta koordinatları
        self.objp = np.zeros((self.board_size[0] * self.board_size[1], 3), np.float32)
        self.objp[:,:2] = np.mgrid[0:self.board_size[0], 0:self.board_size[1]].T.reshape(-1,2)
        self.objp *= self.square_size

        # Nokta listeleri
        self.objpoints = []  # 3D noktalar
        self.imgpoints = []  # 2D görüntü noktaları

    def capture_calibration_images(self):
        """Kalibrasyon görüntülerini yakala"""
        print("📸 Kalibrasyon görüntüleri yakalanıyor...")

        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        count = 0
        target_count = 20

        while count < target_count:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Satranç tahtası köşelerini bul
            ret, corners = cv2.findChessboardCorners(gray, self.board_size, None)

            if ret:
                # Köşeleri göster
                cv2.drawChessboardCorners(frame, self.board_size, corners, ret)
                cv2.putText(frame, f"Images: {count}/{target_count}",
                          (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, "Press SPACE to capture",
                          (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            else:
                cv2.putText(frame, "Chessboard not found!",
                          (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            cv2.imshow('Calibration', frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord(' ') and ret:  # SPACE tuşu
                # Köşeleri kaydet
                self.objpoints.append(self.objp)
                self.imgpoints.append(corners)
                count += 1

                # Görüntüyü kaydet
                cv2.imwrite(f'calibration_{count:02d}.jpg', frame)
                print(f"Görüntü {count} kaydedildi")

            elif key == ord('q'):  # Q tuşu ile çık
                break

        cap.release()
        cv2.destroyAllWindows()

        return len(self.objpoints) >= 10  # En az 10 görüntü gerekli

    def calibrate_camera(self):
        """Kamera kalibrasyonunu gerçekleştir"""
        print("🎯 Kamera kalibrasyonu hesaplanıyor...")

        if len(self.objpoints) < 10:
            print("❌ Yeterli kalibrasyon görüntüsü yok!")
            return None

        # Görüntü boyutu
        img_size = (1280, 720)

        # Kalibrasyon hesaplama
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            self.objpoints, self.imgpoints, img_size, None, None)

        if ret:
            print("✅ Kalibrasyon başarılı!")

            # Reprojection error hesapla
            total_error = 0
            for i in range(len(self.objpoints)):
                imgpoints2, _ = cv2.projectPoints(
                    self.objpoints[i], rvecs[i], tvecs[i], mtx, dist)
                error = cv2.norm(self.imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
                total_error += error

            mean_error = total_error / len(self.objpoints)
            print(f"Reprojection Error: {mean_error:.3f} pixels")

            # Kamera parametreleri
            calib_data = {
                'camera_matrix': mtx.tolist(),
                'distortion_coefficients': dist.tolist(),
                'image_size': img_size,
                'reprojection_error': mean_error,
                'sample_count': len(self.objpoints)
            }

            # JSON'a kaydet
            with open('/home/pi/oba/config/camera_calibration.json', 'w') as f:
                json.dump(calib_data, f, indent=2)

            print("📁 Kalibrasyon verileri kaydedildi")
            return calib_data

        else:
            print("❌ Kalibrasyon başarısız!")
            return None

    def test_undistortion(self):
        """Distortion düzeltme testi"""
        print("🧪 Distortion düzeltme testi...")

        # Kalibrasyon verilerini yükle
        try:
            with open('/home/pi/oba/config/camera_calibration.json', 'r') as f:
                calib_data = json.load(f)

            mtx = np.array(calib_data['camera_matrix'])
            dist = np.array(calib_data['distortion_coefficients'])

            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Distortion düzeltme
                undistorted = cv2.undistort(frame, mtx, dist, None, mtx)

                # Yan yana göster
                combined = np.hstack((frame, undistorted))
                combined = cv2.resize(combined, (1280, 360))

                cv2.putText(combined, "Original", (10, 30),
                          cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(combined, "Undistorted", (650, 30),
                          cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                cv2.imshow('Undistortion Test', combined)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()

        except FileNotFoundError:
            print("❌ Kalibrasyon dosyası bulunamadı!")


def main():
    """Ana kalibrasyon menüsü"""
    print("🎯 Hacı Abi'nin Sensör Kalibrasyon Merkezi")
    print("=" * 45)

    while True:
        print("\n🛠️ Kalibrasyon Seçenekleri:")
        print("1. IMU Kalibrasyonu")
        print("2. Enkoder Kalibrasyonu")
        print("3. Kamera Kalibrasyonu")
        print("4. Distortion Test")
        print("5. Çıkış")

        choice = input("\nSeçiminiz (1-5): ")

        if choice == '1':
            from imu_calibrator import IMUCalibrator
            calibrator = IMUCalibrator()
            calibrator.start_calibration()

        elif choice == '2':
            calibrator = EncoderCalibrator()
            ppr = calibrator.calibrate_pulses_per_revolution()
            ppm = calibrator.calibrate_wheel_distance()
            wheelbase = calibrator.calibrate_wheelbase()

            # Sonuçları kaydet
            encoder_data = {
                'pulses_per_revolution': ppr,
                'pulses_per_meter': ppm,
                'wheelbase': wheelbase
            }

            with open('/home/pi/oba/config/encoder_calibration.json', 'w') as f:
                json.dump(encoder_data, f, indent=2)

        elif choice == '3':
            calibrator = CameraCalibrator()
            if calibrator.capture_calibration_images():
                calibrator.calibrate_camera()
            else:
                print("❌ Yeterli kalibrasyon görüntüsü alınamadı!")

        elif choice == '4':
            calibrator = CameraCalibrator()
            calibrator.test_undistortion()

        elif choice == '5':
            print("👋 Görüşürüz!")
            break

        else:
            print("❌ Geçersiz seçim!")

if __name__ == "__main__":
    main()
```

## 📊 Kalibrasyon Doğrulaması

### 🧪 Test Scriptleri

```bash
#!/bin/bash
# Kalibrasyon test scripti

echo "🧪 Sensör Kalibrasyon Testleri"
echo "=============================="

# IMU test
echo "📍 IMU testi..."
python3 /home/pi/oba/tests/test_imu.py

# Enkoder test
echo "📍 Enkoder testi..."
python3 /home/pi/oba/tests/test_encoders.py

# Kamera test
echo "📍 Kamera testi..."
python3 /home/pi/oba/tests/test_camera.py

echo "✅ Tüm testler tamamlandı!"

---

## 🌡️ DHT22 Sıcaklık/Nem Sensörü Kalibrasyonu

### 📊 Kalibrasyon Temelleri

DHT22 sensörü fabrika kalibrasyonlu gelir, ancak hassas ölçümler için doğrulama gereklidir:
- **Sıcaklık Hassasiyeti**: ±0.5°C
- **Nem Hassasiyeti**: ±2-5% RH
- **Okuma Sıklığı**: En fazla 0.5Hz (2 saniyede bir)

### 🔧 Kalibrasyon Test Scripti

```python
#!/usr/bin/env python3
"""DHT22 Kalibrasyon ve Test Scripti - Hacı Abi"""

import time
import board
import adafruit_dht
import numpy as np
from datetime import datetime

class DHT22Calibrator:
    def __init__(self):
        # DHT22 sensörü (GPIO4)
        self.dht = adafruit_dht.DHT22(board.D4)
        self.readings = []

    def test_sensor(self, duration_minutes=10):
        """Sensör test ve kalibrasyon"""
        print("🌡️ DHT22 Sensör Testi Başlıyor")
        print(f"📅 Test süresi: {duration_minutes} dakika")
        print("=" * 50)

        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)

        while time.time() < end_time:
            try:
                # Sıcaklık ve nem oku
                temp = self.dht.temperature
                humidity = self.dht.humidity

                if temp is not None and humidity is not None:
                    timestamp = datetime.now()
                    reading = {
                        'timestamp': timestamp,
                        'temperature': temp,
                        'humidity': humidity
                    }
                    self.readings.append(reading)

                    print(f"🌡️ {temp:.1f}°C | 💧 {humidity:.1f}% | {timestamp.strftime('%H:%M:%S')}")
                else:
                    print("❌ Okuma hatası - sensör kontrolü gerekli")

                time.sleep(3)  # DHT22 için 2-3 saniye bekle

            except Exception as e:
                print(f"⚠️ Okuma hatası: {e}")
                time.sleep(5)

        self.analyze_readings()

    def analyze_readings(self):
        """Okunan verileri analiz et"""
        if not self.readings:
            print("❌ Analiz için yeterli veri yok!")
            return

        temps = [r['temperature'] for r in self.readings]
        humidities = [r['humidity'] for r in self.readings]

        print("\n📊 Analiz Sonuçları")
        print("=" * 30)

        # Sıcaklık istatistikleri
        temp_mean = np.mean(temps)
        temp_std = np.std(temps)
        temp_min = np.min(temps)
        temp_max = np.max(temps)

        print(f"🌡️ Sıcaklık:")
        print(f"   Ortalama: {temp_mean:.2f}°C")
        print(f"   Std Sapma: {temp_std:.2f}°C")
        print(f"   Min-Max: {temp_min:.1f}°C - {temp_max:.1f}°C")

        # Nem istatistikleri
        hum_mean = np.mean(humidities)
        hum_std = np.std(humidities)
        hum_min = np.min(humidities)
        hum_max = np.max(humidities)

        print(f"💧 Nem:")
        print(f"   Ortalama: {hum_mean:.2f}%")
        print(f"   Std Sapma: {hum_std:.2f}%")
        print(f"   Min-Max: {hum_min:.1f}% - {hum_max:.1f}%")

        # Kalite değerlendirmesi
        self.evaluate_quality(temp_std, hum_std)

        # Kalibrayon önerisi
        self.calibration_suggestion()

    def evaluate_quality(self, temp_std, hum_std):
        """Sensör kalitesini değerlendir"""
        print(f"\n🎯 Kalite Değerlendirmesi:")

        if temp_std < 0.3:
            print("✅ Sıcaklık kararlılığı: MÜKEMMEL")
        elif temp_std < 0.6:
            print("🟡 Sıcaklık kararlılığı: İYİ")
        else:
            print("❌ Sıcaklık kararlılığı: KÖTÜ - Sensör değişimi gerekli")

        if hum_std < 2.0:
            print("✅ Nem kararlılığı: MÜKEMMEL")
        elif hum_std < 4.0:
            print("🟡 Nem kararlılığı: İYİ")
        else:
            print("❌ Nem kararlılığı: KÖTÜ - Sensör değişimi gerekli")

    def calibration_suggestion(self):
        """Kalibrasyon önerisi"""
        print(f"\n💡 Kalibrasyon Önerileri:")
        print("1. Referans termometre ile karşılaştır")
        print("2. Değişik ortam koşullarında test et")
        print("3. Nem kalibrasyonu için nemli/kuru ortam test et")
        print("4. Sensörü koruyucu case içine al")
        print("5. Kablo uzunluğunu minimize et (parazit azalt)")

def main():
    """Ana test fonksiyonu"""
    calibrator = DHT22Calibrator()

    print("🌡️ DHT22 Kalibrasyon Aracı")
    print("Hacı Abi - Sensör Test Scripti")
    print("=" * 40)

    try:
        duration = int(input("Test süresi (dakika, varsayılan 10): ") or "10")
        calibrator.test_sensor(duration)
    except KeyboardInterrupt:
        print("\n⏹️ Test kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"❌ Test hatası: {e}")

if __name__ == "__main__":
    main()
```

### 🔧 Montaj ve Bağlantı

#### Pin Bağlantıları
```
DHT22 Sensör Pinleri:
Pin 1 (VCC) ────► Raspberry Pi 3.3V (Pin 1)
Pin 2 (DATA) ───► Raspberry Pi GPIO4 (Pin 7)
Pin 3 (NC) ─────► Bağlanmaz
Pin 4 (GND) ────► Raspberry Pi GND (Pin 6)

Pull-up Direnci: 10kΩ (VCC ile DATA arasında)
```

#### Montaj Yeri
- Doğrudan güneş ışığından korunmalı
- Yağmur ve neme dayanıklı case içinde
- Hava akımının olduğu yer (sensör kafesi)
- Isı kaynaklarından uzak (motor, elektronik)

### ⚠️ Kritik Dikkat Noktaları

1. **Okuma Sıklığı**: En fazla 0.5Hz (2 saniyede bir)
2. **Güç Gerilimi**: 3.3V-5V (5V daha kararlı)
3. **Pull-up Direnci**: 10kΩ zorunlu
4. **Kablo Uzunluğu**: Max 20cm (parazit önleme)
5. **Ortam Koşulları**: -40°C ~ +80°C, 0-100% RH

### 📋 Kalibrasyon Kontrol Listesi

#### ✅ İlk Kurulum
- [ ] Pin bağlantıları doğru
- [ ] Pull-up direnci takılı (10kΩ)
- [ ] Test scripti çalışıyor
- [ ] Okuma değerleri makul

#### ✅ Günlük Kontrol
- [ ] Sıcaklık değeri makul (±5°C çevre sıcaklığı)
- [ ] Nem değeri makul (%30-90 normal aralık)
- [ ] Okuma hatası yok

#### ✅ Haftalık Kontrol
- [ ] Referans termometre ile karşılaştırma
- [ ] Farklı hava koşullarında test
- [ ] Sensör case kontrolü

---

## 📊 Kalibrasyon Doğrulaması
