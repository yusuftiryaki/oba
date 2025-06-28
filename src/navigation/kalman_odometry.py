"""
Kalman Filtresi Tabanlı Odometri Modülü
Enkoder ve IMU verilerini birleştirerek hassas konum tahmini yapar
"""

import numpy as np
import time
import logging
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Position:
    """Robot pozisyon bilgisi"""

    x: float = 0.0
    y: float = 0.0
    heading: float = 0.0  # radyan cinsinden
    timestamp: float = 0.0


class KalmanOdometry:
    """
    Kalman Filtresi kullanarak enkoder ve IMU verilerini birleştiren odometri sınıfı
    State Vector: [x, y, heading, vx, vy, angular_velocity]
    """

    def __init__(self, simulate: bool = False):
        self.logger = logging.getLogger("KalmanOdometry")

        # Simülasyon kontrolü
        self.simulate = simulate
        if self.simulate:
            self.logger.info("Odometri simülasyon modunda başlatılıyor")
        else:
            self.logger.info("Odometri gerçek donanım modunda başlatılıyor")

        # Durum vektörü [x, y, theta, vx, vy, omega]
        self.state = np.zeros(6)

        # Durum kovaryans matrisi
        self.P = np.eye(6) * 0.1

        # Süreç gürültü kovaryansı
        self.Q = np.diag([0.01, 0.01, 0.001, 0.1, 0.1, 0.01])

        # Ölçüm gürültü kovaryansı
        self.R_encoder = np.diag([0.05, 0.05, 0.01])  # x, y, theta for encoder
        self.R_imu = np.diag([0.01])  # heading for IMU

        # Robot fiziksel parametreleri
        self.wheel_base = 0.5  # tekerlekler arası mesafe (metre)
        self.wheel_radius = 0.1  # tekerlek yarıçapı (metre)

        # Son güncelleme zamanı
        self.last_update_time = time.time()

        # Kalibrasyon parametreleri
        self.position_offset = Position()
        self.heading_offset = 0.0

        # İstatistikler
        self.total_distance = 0.0
        self.last_position = Position()

    def reset_position(self, x: float = 0.0, y: float = 0.0, heading: float = 0.0):
        """Pozisyonu sıfırla"""
        self.state[0] = x
        self.state[1] = y
        self.state[2] = heading
        self.state[3:] = 0  # Hızları sıfırla

        self.P = np.eye(6) * 0.1  # Kovaryansı sıfırla
        self.last_update_time = time.time()

        self.logger.info(f"Pozisyon sıfırlandı: x={x}, y={y}, heading={heading}")

    def predict(self, dt: float):
        """
        Kalman Filtresi tahmin aşaması
        """
        # State transition matrix (kinematik model)
        F = np.eye(6)
        F[0, 3] = dt  # x = x + vx * dt
        F[1, 4] = dt  # y = y + vy * dt
        F[2, 5] = dt  # theta = theta + omega * dt

        # Tahmin
        self.state = F @ self.state

        # Açıyı [-pi, pi] aralığında tut
        self.state[2] = self._normalize_angle(self.state[2])

        # Kovaryans tahmini
        self.P = F @ self.P @ F.T + self.Q * dt

    def update_encoder(
        self, left_ticks: int, right_ticks: int, ticks_per_revolution: int
    ):
        """
        Enkoder verilerini kullanarak güncelleme
        """
        current_time = time.time()
        dt = current_time - self.last_update_time

        if dt <= 0:
            return

        # Enkoder verilerinden hız hesapla
        left_distance = (
            (left_ticks / ticks_per_revolution) * 2 * np.pi * self.wheel_radius
        )
        right_distance = (
            (right_ticks / ticks_per_revolution) * 2 * np.pi * self.wheel_radius
        )

        # Ortalama hız ve açısal hız
        linear_velocity = (left_distance + right_distance) / (2 * dt)
        angular_velocity = (right_distance - left_distance) / (self.wheel_base * dt)

        # Tahmin aşaması
        self.predict(dt)

        # Ölçüm modeli (enkoder verilerinden pozisyon hesapla)
        theta = self.state[2]
        dx = linear_velocity * dt * np.cos(theta)
        dy = linear_velocity * dt * np.sin(theta)
        dtheta = angular_velocity * dt

        # Ölçüm vektörü
        z = np.array([self.state[0] + dx, self.state[1] + dy, self.state[2] + dtheta])

        # Ölçüm matrisi
        H = np.zeros((3, 6))
        H[0, 0] = 1  # x
        H[1, 1] = 1  # y
        H[2, 2] = 1  # theta

        # Kalman güncellemesi
        self._kalman_update(z, H, self.R_encoder)

        # Hızları güncelle
        self.state[3] = linear_velocity * np.cos(theta)
        self.state[4] = linear_velocity * np.sin(theta)
        self.state[5] = angular_velocity

        self.last_update_time = current_time

        # Mesafe istatistiği
        distance = np.sqrt(dx**2 + dy**2)
        self.total_distance += distance

    def update_imu(self, heading: float, angular_velocity: float = None):
        """
        IMU verilerini kullanarak güncelleme
        """
        # Heading'i normalize et
        heading = self._normalize_angle(heading - self.heading_offset)

        # Ölçüm vektörü (sadece heading)
        z = np.array([heading])

        # Ölçüm matrisi
        H = np.zeros((1, 6))
        H[0, 2] = 1  # theta

        # Kalman güncellemesi
        self._kalman_update(z, H, self.R_imu)

        # Eğer açısal hız varsa güncelle
        if angular_velocity is not None:
            self.state[5] = angular_velocity

    def _kalman_update(self, z: np.ndarray, H: np.ndarray, R: np.ndarray):
        """
        Kalman Filtresi güncelleme aşaması
        """
        # Yenilik (innovation)
        y = z - H @ self.state

        # Açıları normalize et
        if len(y) >= 3:  # Enkoder güncellemesinde
            y[2] = self._normalize_angle(y[2])
        elif len(y) == 1:  # IMU güncellemesinde
            y[0] = self._normalize_angle(y[0])

        # Yenilik kovaryansı
        S = H @ self.P @ H.T + R

        # Kalman kazancı
        try:
            K = self.P @ H.T @ np.linalg.inv(S)
        except np.linalg.LinAlgError:
            self.logger.warning("Kalman kazancı hesaplanamadı")
            return

        # Durum güncellemesi
        self.state = self.state + K @ y

        # Açıyı normalize et
        self.state[2] = self._normalize_angle(self.state[2])

        # Kovaryans güncellemesi
        I = np.eye(len(self.state))
        self.P = (I - K @ H) @ self.P

    def _normalize_angle(self, angle: float) -> float:
        """Açıyı [-pi, pi] aralığında normalize et"""
        while angle > np.pi:
            angle -= 2 * np.pi
        while angle < -np.pi:
            angle += 2 * np.pi
        return angle

    def get_position(self) -> Position:
        """Mevcut pozisyonu Position objesi olarak döndür - testlerin beklediği format"""
        return Position(
            x=float(self.state[0]),
            y=float(self.state[1]),
            heading=float(self.state[2]),
            timestamp=time.time(),
        )

    def get_position_dict(self) -> Dict[str, float]:
        """Mevcut pozisyonu dict olarak döndür"""
        return {
            "x": float(self.state[0]),
            "y": float(self.state[1]),
            "heading": float(self.state[2]),
            "timestamp": time.time(),
        }

    def get_velocity(self) -> Dict[str, float]:
        """Mevcut hızı döndür"""
        return {
            "linear_x": float(self.state[3]),
            "linear_y": float(self.state[4]),
            "angular": float(self.state[5]),
        }

    def get_covariance(self) -> np.ndarray:
        """Pozisyon kovaryansını döndür"""
        return self.P[:3, :3].copy()

    def get_position_uncertainty(self) -> Dict[str, float]:
        """Pozisyon belirsizliğini döndür (standart sapma)"""
        std_devs = np.sqrt(np.diag(self.P[:3, :3]))
        return {
            "x_std": float(std_devs[0]),
            "y_std": float(std_devs[1]),
            "heading_std": float(std_devs[2]),
        }

    def calibrate_heading(self, true_heading: float):
        """Başlık kalibrasyonu"""
        current_heading = self.state[2]
        self.heading_offset = true_heading - current_heading
        self.logger.info(f"Başlık kalibre edildi: offset = {self.heading_offset}")

    def set_position_offset(self, x_offset: float, y_offset: float):
        """Pozisyon offseti ayarla"""
        self.position_offset.x = x_offset
        self.position_offset.y = y_offset
        self.logger.info(f"Pozisyon offseti ayarlandı: x={x_offset}, y={y_offset}")

    def get_statistics(self) -> Dict[str, float]:
        """İstatistikleri döndür"""
        position_uncertainty = np.sqrt(np.trace(self.P[:2, :2]))  # X-Y belirsizliği

        stats = {
            "total_distance": self.total_distance,
            "position_uncertainty": position_uncertainty,
            "heading_uncertainty": np.sqrt(self.P[2, 2]),
            "velocity_uncertainty": np.sqrt(self.P[3, 3] + self.P[4, 4]),
            "angular_velocity_uncertainty": np.sqrt(self.P[5, 5]),
            "position": {  # Testlerin beklediği format
                "x": self.state[0],
                "y": self.state[1],
                "heading": self.state[2],
            },
            "velocity": {  # Testlerin beklediği format
                "vx": self.state[3],
                "vy": self.state[4],
                "angular": self.state[5],
            },
            "covariance_trace": float(np.trace(self.P)),
            "last_update": getattr(self, "last_update_time", 0.0),
            "filter_stable": bool(np.trace(self.P) < 10.0),  # Stability threshold
        }

        return stats

    def update_from_encoder(self, encoder_data: Dict[str, float]) -> None:
        """Enkoder verilerinden güncelleme - testlerin beklediği fonksiyon"""
        try:
            left_ticks = int(encoder_data.get("left_ticks", 0))
            right_ticks = int(encoder_data.get("right_ticks", 0))
            ticks_per_rev = int(encoder_data.get("ticks_per_revolution", 1000))

            self.update_encoder(left_ticks, right_ticks, ticks_per_rev)

        except Exception as e:
            self.logger.error(f"Enkoder güncellemesi hatası: {e}")

    def update_from_imu(self, imu_data: Dict[str, float]) -> None:
        """IMU verilerinden güncelleme - testlerin beklediği fonksiyon"""
        try:
            heading = imu_data.get("heading", 0.0)
            angular_velocity = imu_data.get("angular_velocity")

            self.update_imu(heading, angular_velocity)

        except Exception as e:
            self.logger.error(f"IMU güncellemesi hatası: {e}")

    def set_position(self, x: float, y: float, heading: float) -> None:
        """Pozisyonu manuel olarak ayarla - testlerin beklediği fonksiyon"""
        self.reset_position(x, y, heading)

    def predict_state(self, dt: float) -> Dict[str, float]:
        """Durum tahmini yap - testlerin beklediği fonksiyon"""
        # Geçici durum kopyası oluştur
        temp_state = self.state.copy()
        temp_P = self.P.copy()

        # Tahmin yap
        self.predict(dt)

        # Sonuçları kaydet
        predicted_state = {
            "x": self.state[0],
            "y": self.state[1],
            "heading": self.state[2],
            "vx": self.state[3],
            "vy": self.state[4],
            "angular_velocity": self.state[5],
        }

        # Durumu geri yükle
        self.state = temp_state
        self.P = temp_P

        return predicted_state

    def prediction_step(self, dt: float) -> None:
        """Sadece tahmin aşaması - testlerin beklediği fonksiyon"""
        self.predict(dt)

    def correction_step(
        self, measurement: np.ndarray, H: np.ndarray, R: np.ndarray
    ) -> None:
        """Sadece düzeltme aşaması - testlerin beklediği fonksiyon"""
        self._kalman_update(measurement, H, R)

    def encoder_to_position(
        self, left_ticks: int, right_ticks: int, ticks_per_rev: int = 1000
    ) -> Dict[str, float]:
        """Enkoder verilerini pozisyona çevir - testlerin beklediği fonksiyon"""
        try:
            # Mesafe hesapla
            left_distance = (left_ticks / ticks_per_rev) * 2 * np.pi * self.wheel_radius
            right_distance = (
                (right_ticks / ticks_per_rev) * 2 * np.pi * self.wheel_radius
            )

            # Robot kinematik
            linear_distance = (left_distance + right_distance) / 2
            angular_change = (right_distance - left_distance) / self.wheel_base

            # Mevcut heading kullanarak pozisyon değişimi hesapla
            current_heading = self.state[2]
            dx = linear_distance * np.cos(current_heading)
            dy = linear_distance * np.sin(current_heading)

            return {
                "dx": dx,
                "dy": dy,
                "dheading": angular_change,
                "linear_distance": linear_distance,
                "angular_distance": angular_change,
            }

        except Exception as e:
            self.logger.error(f"Enkoder pozisyon hesaplama hatası: {e}")
            return {
                "dx": 0.0,
                "dy": 0.0,
                "dheading": 0.0,
                "linear_distance": 0.0,
                "angular_distance": 0.0,
            }


# Test ve simülasyon için yardımcı sınıf
class OdometrySimulator:
    """Odometri test ve simülasyon sınıfı"""

    def __init__(self, odometry: KalmanOdometry):
        self.odometry = odometry
        self.true_position = Position()

    def simulate_movement(
        self,
        linear_vel: float,
        angular_vel: float,
        duration: float,
        noise_level: float = 0.01,
    ):
        """Hareket simülasyonu"""
        dt = 0.1  # 10Hz simülasyon
        steps = int(duration / dt)

        for _ in range(steps):
            # Gerçek pozisyonu güncelle
            self.true_position.x += linear_vel * np.cos(self.true_position.heading) * dt
            self.true_position.y += linear_vel * np.sin(self.true_position.heading) * dt
            self.true_position.heading += angular_vel * dt
            self.true_position.heading = self.odometry._normalize_angle(
                self.true_position.heading
            )

            # Enkoder simülasyonu (gürültü ile)
            left_vel = linear_vel - (angular_vel * self.odometry.wheel_base / 2)
            right_vel = linear_vel + (angular_vel * self.odometry.wheel_base / 2)

            # Gürültü ekle
            left_vel += np.random.normal(0, noise_level)
            right_vel += np.random.normal(0, noise_level)

            # Tick'lere çevir
            ticks_per_rev = 1000
            left_ticks = int(
                left_vel * dt / (2 * np.pi * self.odometry.wheel_radius) * ticks_per_rev
            )
            right_ticks = int(
                right_vel
                * dt
                / (2 * np.pi * self.odometry.wheel_radius)
                * ticks_per_rev
            )

            # Odometri güncelle
            self.odometry.update_encoder(left_ticks, right_ticks, ticks_per_rev)

            # IMU güncellemesi (az gürültü ile)
            imu_heading = self.true_position.heading + np.random.normal(0, 0.001)
            self.odometry.update_imu(imu_heading, angular_vel)

            time.sleep(dt)

    def get_error(self) -> Dict[str, float]:
        """Gerçek pozisyon ile tahmin arasındaki hata"""
        estimated = self.odometry.get_position()

        return {
            "x_error": abs(self.true_position.x - estimated["x"]),
            "y_error": abs(self.true_position.y - estimated["y"]),
            "heading_error": abs(
                self.odometry._normalize_angle(
                    self.true_position.heading - estimated["heading"]
                )
            ),
        }


if __name__ == "__main__":
    # Test kodu
    logging.basicConfig(level=logging.INFO)

    odometry = KalmanOdometry()
    simulator = OdometrySimulator(odometry)

    print("Odometri testi başlıyor...")

    # Kare rota simülasyonu
    simulator.simulate_movement(0.5, 0, 2)  # İleri git
    simulator.simulate_movement(0, np.pi / 2, 1)  # 90 derece dön
    simulator.simulate_movement(0.5, 0, 2)  # İleri git
    simulator.simulate_movement(0, np.pi / 2, 1)  # 90 derece dön
    simulator.simulate_movement(0.5, 0, 2)  # İleri git
    simulator.simulate_movement(0, np.pi / 2, 1)  # 90 derece dön
    simulator.simulate_movement(0.5, 0, 2)  # İleri git

    # Sonuçları kontrol et
    final_pos = odometry.get_position()
    error = simulator.get_error()
    stats = odometry.get_statistics()

    print(
        f"Final pozisyon: x={final_pos['x']:.3f}, y={final_pos['y']:.3f}, heading={final_pos['heading']:.3f}"
    )
    print(
        f"Pozisyon hatası: x={error['x_error']:.3f}, y={error['y_error']:.3f}, heading={error['heading_error']:.3f}"
    )
    print(f"Toplam mesafe: {stats['total_distance']:.3f} metre")
    print(f"Pozisyon belirsizliği: {stats['position_uncertainty']:.3f}")
