"""
Motor Kontrol Modülü
Robot hareket ve biçme motorlarını kontrol eder
"""

import time
import logging
import json
import math
from typing import Dict, Tuple, Optional, Any, List
from dataclasses import dataclass
from enum import Enum
import threading


class MotorType(Enum):
    """Motor türleri"""

    LEFT_DRIVE = "left_drive"
    RIGHT_DRIVE = "right_drive"
    BLADE = "blade"
    HEIGHT_ACTUATOR = "height_actuator"


class MotorState(Enum):
    """Motor durumları"""

    STOPPED = "stopped"
    RUNNING = "running"
    BRAKING = "braking"
    ERROR = "error"


@dataclass
class MotorParameters:
    """Motor parametreleri"""

    max_rpm: int
    max_current: float
    encoder_ticks_per_rev: int
    gear_ratio: float
    wheel_diameter: float  # sadece sürüş motorları için


@dataclass
class MotorStatus:
    """Motor durum bilgisi"""

    rpm: float
    current: float
    temperature: float
    encoder_position: int
    state: MotorState
    error_code: int = 0


class MotorController:
    """Motor kontrol sınıfı"""

    def __init__(self, config_path: str = "config/motor_config.json"):
        self.logger = logging.getLogger("MotorController")

        # Konfigürasyon
        self.config = self._load_config(config_path)

        # Motor durumları
        self.motor_status: Dict[MotorType, MotorStatus] = {}
        self.motor_params: Dict[MotorType, MotorParameters] = {}

        # Robot fiziksel parametreleri
        self.wheel_base = 0.5  # tekerlekler arası mesafe
        self.track_width = 0.4  # iz genişliği
        self.max_speed = 1.0  # m/s
        self.max_angular_speed = 1.0  # rad/s

        # Kontrol parametreleri
        self.speed_control_enabled = True
        self.position_control_enabled = False

        # PID kontrolörleri
        self.pid_controllers = {}

        # Güvenlik
        self.emergency_stop_active = False
        self.motor_timeout = 5.0  # saniye

        # İzleme
        self.monitoring_active = False
        self.monitoring_thread = None

        # Biçme bıçağı
        self.blade_height_levels = [3, 5, 7, 9, 11]  # cm
        self.current_blade_height = 5  # cm
        self.blade_running = False

        # Enkoder sayaçları
        self.encoder_counts = {MotorType.LEFT_DRIVE: 0, MotorType.RIGHT_DRIVE: 0}
        self.last_encoder_time = time.time()

        self._initialize_motors()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Konfigürasyon dosyasını yükle"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Motor config dosyası bulunamadı: {config_path}")
            return self._default_motor_config()

    def _default_motor_config(self) -> Dict[str, Any]:
        """Varsayılan motor konfigürasyonu"""
        return {
            "left_drive": {
                "max_rpm": 300,
                "max_current": 10.0,
                "encoder_ticks_per_rev": 1000,
                "gear_ratio": 20.0,
                "wheel_diameter": 0.2,
                "pwm_pin": 18,
                "dir_pin": 19,
                "encoder_pins": [20, 21],
            },
            "right_drive": {
                "max_rpm": 300,
                "max_current": 10.0,
                "encoder_ticks_per_rev": 1000,
                "gear_ratio": 20.0,
                "wheel_diameter": 0.2,
                "pwm_pin": 12,
                "dir_pin": 13,
                "encoder_pins": [16, 17],
            },
            "blade": {
                "max_rpm": 3000,
                "max_current": 15.0,
                "encoder_ticks_per_rev": 500,
                "gear_ratio": 1.0,
                "pwm_pin": 22,
                "dir_pin": 23,
            },
            "height_actuator": {
                "max_rpm": 100,
                "max_current": 5.0,
                "encoder_ticks_per_rev": 200,
                "gear_ratio": 50.0,
                "pwm_pin": 24,
                "dir_pin": 25,
                "encoder_pins": [26, 27],
            },
            "pid": {
                "speed": {"kp": 1.0, "ki": 0.1, "kd": 0.05},
                "position": {"kp": 2.0, "ki": 0.0, "kd": 0.1},
            },
        }

    def _initialize_motors(self):
        """Motorları başlat"""
        try:
            # Motor parametrelerini yükle
            for motor_type in MotorType:
                config_key = motor_type.value
                if config_key in self.config:
                    motor_config = self.config[config_key]

                    self.motor_params[motor_type] = MotorParameters(
                        max_rpm=motor_config.get("max_rpm", 300),
                        max_current=motor_config.get("max_current", 10.0),
                        encoder_ticks_per_rev=motor_config.get(
                            "encoder_ticks_per_rev", 1000
                        ),
                        gear_ratio=motor_config.get("gear_ratio", 1.0),
                        wheel_diameter=motor_config.get("wheel_diameter", 0.2),
                    )

                    self.motor_status[motor_type] = MotorStatus(
                        rpm=0.0,
                        current=0.0,
                        temperature=25.0,
                        encoder_position=0,
                        state=MotorState.STOPPED,
                    )

            # GPIO ve PWM başlatma (simülasyon)
            self._setup_gpio()

            # PID kontrolörleri
            self._setup_pid_controllers()

            self.logger.info("Motorlar başarıyla başlatıldı")

        except Exception as e:
            self.logger.error(f"Motor başlatma hatası: {e}")

    def _setup_gpio(self):
        """GPIO pinlerini ayarla"""
        # Gerçek implementasyonda RPi.GPIO veya gpiozero kullanılacak
        # import RPi.GPIO as GPIO
        # import pigpio

        self.logger.info("GPIO pinleri ayarlandı (simülasyon)")

    def _setup_pid_controllers(self):
        """PID kontrolörlerini ayarla"""

        # PID kontrolör sınıfı implementasyonu
        class PIDController:
            def __init__(self, kp, ki, kd, setpoint=0):
                self.kp = kp
                self.ki = ki
                self.kd = kd
                self.setpoint = setpoint
                self.integral = 0
                self.previous_error = 0
                self.last_time = time.time()

            def update(self, measurement):
                current_time = time.time()
                dt = current_time - self.last_time

                error = self.setpoint - measurement
                self.integral += error * dt
                derivative = (error - self.previous_error) / dt if dt > 0 else 0

                output = (
                    self.kp * error + self.ki * self.integral + self.kd * derivative
                )

                self.previous_error = error
                self.last_time = current_time

                return output

        pid_config = self.config.get("pid", {})

        # Hız kontrolörleri
        for motor_type in [MotorType.LEFT_DRIVE, MotorType.RIGHT_DRIVE]:
            speed_pid = pid_config.get("speed", {"kp": 1.0, "ki": 0.1, "kd": 0.05})
            self.pid_controllers[f"{motor_type.value}_speed"] = PIDController(
                **speed_pid
            )

    def start_monitoring(self):
        """Motor izlemesini başlat"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop, daemon=True
            )
            self.monitoring_thread.start()
            self.logger.info("Motor izlemesi başlatıldı")

    def stop_monitoring(self):
        """Motor izlemesini durdur"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
        self.logger.info("Motor izlemesi durduruldu")

    def _monitoring_loop(self):
        """Motor izleme döngüsü"""
        while self.monitoring_active:
            try:
                # Motor durumlarını güncelle
                for motor_type in self.motor_status.keys():
                    self._update_motor_status(motor_type)

                # Enkoder güncellemeleri
                self._update_encoders()

                time.sleep(0.1)  # 10Hz

            except Exception as e:
                self.logger.error(f"Motor izleme hatası: {e}")
                time.sleep(1)

    def _update_motor_status(self, motor_type: MotorType):
        """Motor durumunu güncelle"""
        # Gerçek motor verilerini oku (simülasyon)
        status = self.motor_status[motor_type]

        # RPM simulasyonu
        import random

        if status.state == MotorState.RUNNING:
            status.rpm += random.uniform(-10, 10)
            status.current = random.uniform(2, 8)
        else:
            status.rpm = 0
            status.current = 0

        status.temperature = 25 + random.uniform(-5, 15)

    def _update_encoders(self):
        """Enkoder sayaçlarını güncelle"""
        current_time = time.time()
        dt = current_time - self.last_encoder_time

        # Simüle edilmiş enkoder sayıları
        for motor_type in [MotorType.LEFT_DRIVE, MotorType.RIGHT_DRIVE]:
            if motor_type in self.motor_status:
                status = self.motor_status[motor_type]
                if status.state == MotorState.RUNNING:
                    # RPM'den enkoder sayısına çevir
                    rps = status.rpm / 60
                    ticks_per_second = (
                        rps * self.motor_params[motor_type].encoder_ticks_per_rev
                    )
                    new_ticks = int(ticks_per_second * dt)

                    self.encoder_counts[motor_type] += new_ticks
                    status.encoder_position = self.encoder_counts[motor_type]

        self.last_encoder_time = current_time

    def move(self, linear_velocity: float, angular_velocity: float):
        """Robot hareketi - linear (m/s) ve angular (rad/s)"""
        if self.emergency_stop_active:
            self.logger.warning("Acil durdurma aktif - hareket engellendi")
            return

        # Kinematik hesaplamalar
        left_wheel_speed, right_wheel_speed = self._differential_kinematics(
            linear_velocity, angular_velocity
        )

        # Motor hızlarını ayarla
        self.set_motor_speed(MotorType.LEFT_DRIVE, left_wheel_speed)
        self.set_motor_speed(MotorType.RIGHT_DRIVE, right_wheel_speed)

    def _differential_kinematics(
        self, linear_vel: float, angular_vel: float
    ) -> Tuple[float, float]:
        """Diferansiyel kinematik hesaplamaları"""
        # v_left = v - (w * L) / 2
        # v_right = v + (w * L) / 2

        left_velocity = linear_vel - (angular_vel * self.wheel_base) / 2
        right_velocity = linear_vel + (angular_vel * self.wheel_base) / 2

        # Hız sınırlaması
        max_wheel_speed = self.max_speed
        left_velocity = max(-max_wheel_speed, min(max_wheel_speed, left_velocity))
        right_velocity = max(-max_wheel_speed, min(max_wheel_speed, right_velocity))

        return left_velocity, right_velocity

    def set_motor_speed(self, motor_type: MotorType, speed: float):
        """Motor hızını ayarla (m/s tekerlek hızı veya RPM)"""
        if motor_type not in self.motor_status:
            self.logger.error(f"Bilinmeyen motor türü: {motor_type}")
            return

        # Hızı RPM'e çevir
        if motor_type in [MotorType.LEFT_DRIVE, MotorType.RIGHT_DRIVE]:
            wheel_diameter = self.motor_params[motor_type].wheel_diameter
            rpm = (speed * 60) / (math.pi * wheel_diameter)
        else:
            rpm = speed  # Diğer motorlar için direkt RPM

        # Hız sınırlaması
        max_rpm = self.motor_params[motor_type].max_rpm
        rpm = max(-max_rpm, min(max_rpm, rpm))

        # PWM sinyali hesapla ve gönder
        pwm_value = self._rpm_to_pwm(motor_type, rpm)
        self._send_pwm_signal(motor_type, pwm_value)

        # Durum güncelle
        if abs(rpm) > 1:
            self.motor_status[motor_type].state = MotorState.RUNNING
        else:
            self.motor_status[motor_type].state = MotorState.STOPPED

        self.logger.debug(f"{motor_type.value} motor hızı: {rpm:.1f} RPM")

    def _rpm_to_pwm(self, motor_type: MotorType, rpm: float) -> int:
        """RPM'i PWM değerine çevir"""
        max_rpm = self.motor_params[motor_type].max_rpm
        pwm_range = 255  # 8-bit PWM

        if max_rpm > 0:
            pwm_value = int((abs(rpm) / max_rpm) * pwm_range)
            return min(pwm_range, max(0, pwm_value))

        return 0

    def _send_pwm_signal(self, motor_type: MotorType, pwm_value: int):
        """PWM sinyalini motora gönder"""
        # Gerçek implementasyonda GPIO PWM kullanılacak
        # GPIO.output(motor_pin, GPIO.HIGH/LOW)
        # pwm.ChangeDutyCycle(pwm_value)

        pass  # Simülasyon

    def move_to_position(self, target_position: Dict[str, float]):
        """Belirli pozisyona git"""
        target_x = target_position["x"]
        target_y = target_position["y"]

        # Basit pozisyon kontrolü (geliştirilmesi gerekebilir)
        current_pos = self._get_current_position()

        dx = target_x - current_pos["x"]
        dy = target_y - current_pos["y"]

        distance = math.sqrt(dx**2 + dy**2)
        target_heading = math.atan2(dy, dx)

        # Önce hedefe yönel
        current_heading = current_pos["heading"]
        heading_error = target_heading - current_heading

        # Açıyı normalize et
        while heading_error > math.pi:
            heading_error -= 2 * math.pi
        while heading_error < -math.pi:
            heading_error += 2 * math.pi

        if abs(heading_error) > 0.1:  # 0.1 radyan tolerans
            angular_vel = 0.5 if heading_error > 0 else -0.5
            self.move(0, angular_vel)
        else:
            # Hedefe doğru git
            linear_vel = min(0.5, distance * 0.5)
            self.move(linear_vel, 0)

    def move_to_waypoint(self, waypoint):
        """Waypoint'e git"""
        target_pos = {"x": waypoint.position.x, "y": waypoint.position.y}
        self.move_to_position(target_pos)

    def _get_current_position(self) -> Dict[str, float]:
        """Mevcut pozisyonu al (odometri modülünden)"""
        # Gerçek implementasyonda odometri modülünden alınacak
        return {"x": 0, "y": 0, "heading": 0}

    def start_blade(self, rpm: Optional[float] = None):
        """Biçme bıçağını başlat"""
        if rpm is None:
            rpm = self.motor_params[MotorType.BLADE].max_rpm * 0.8  # %80 hız

        self.set_motor_speed(MotorType.BLADE, rpm)
        self.blade_running = True
        self.logger.info(f"Biçme bıçağı başlatıldı: {rpm} RPM")

    def stop_blade(self):
        """Biçme bıçağını durdur"""
        self.set_motor_speed(MotorType.BLADE, 0)
        self.blade_running = False
        self.logger.info("Biçme bıçağı durduruldu")

    def set_blade_height(self, height_level: int):
        """Biçme yüksekliğini ayarla"""
        if height_level < 0 or height_level >= len(self.blade_height_levels):
            self.logger.error(f"Geçersiz yükseklik seviyesi: {height_level}")
            return

        target_height = self.blade_height_levels[height_level]
        current_height = self.current_blade_height

        # Yükseklik farkını hesapla
        height_diff = target_height - current_height

        # Lineer aktüatör ile ayarlama
        actuator_speed = 50 if height_diff > 0 else -50  # RPM
        self.set_motor_speed(MotorType.HEIGHT_ACTUATOR, actuator_speed)

        # Hareket süresini hesapla (basitleştirilmiş)
        movement_time = abs(height_diff) * 0.5  # saniye

        # Hareket tamamlandıktan sonra durdur
        def stop_actuator():
            time.sleep(movement_time)
            self.set_motor_speed(MotorType.HEIGHT_ACTUATOR, 0)
            self.current_blade_height = target_height
            self.logger.info(f"Biçme yüksekliği ayarlandı: {target_height} cm")

        threading.Thread(target=stop_actuator, daemon=True).start()

    def stop_all(self):
        """Tüm motorları durdur"""
        for motor_type in self.motor_status.keys():
            self.set_motor_speed(motor_type, 0)
            self.motor_status[motor_type].state = MotorState.STOPPED

        self.blade_running = False
        self.logger.info("Tüm motorlar durduruldu")

    def emergency_stop(self):
        """Acil durdurma"""
        self.emergency_stop_active = True
        self.stop_all()
        self.logger.critical("ACİL DURDURMA - Tüm motorlar durduruldu")

    def clear_emergency_stop(self):
        """Acil durdurma kaldır"""
        self.emergency_stop_active = False
        self.logger.info("Acil durdurma kaldırıldı")

    def brake(self, motor_type: Optional[MotorType] = None):
        """Motor frenleme"""
        if motor_type:
            self.motor_status[motor_type].state = MotorState.BRAKING
            # Frenleme PWM sinyali (gerçek implementasyonda)
            time.sleep(0.5)
            self.motor_status[motor_type].state = MotorState.STOPPED
        else:
            # Tüm sürüş motorlarını frenle
            for mt in [MotorType.LEFT_DRIVE, MotorType.RIGHT_DRIVE]:
                self.brake(mt)

    def get_motor_status(self, motor_type: MotorType) -> Optional[MotorStatus]:
        """Motor durumunu al"""
        return self.motor_status.get(motor_type)

    def get_all_motor_status(self) -> Dict[str, Dict[str, Any]]:
        """Tüm motor durumlarını al"""
        result = {}
        for motor_type, status in self.motor_status.items():
            result[motor_type.value] = {
                "rpm": status.rpm,
                "current": status.current,
                "temperature": status.temperature,
                "encoder_position": status.encoder_position,
                "state": status.state.value,
                "error_code": status.error_code,
            }
        return result

    def get_encoder_counts(self) -> Dict[str, int]:
        """Enkoder sayılarını al"""
        return {
            motor_type.value: count for motor_type, count in self.encoder_counts.items()
        }

    def reset_encoders(self):
        """Enkoder sayaçlarını sıfırla"""
        for motor_type in self.encoder_counts.keys():
            self.encoder_counts[motor_type] = 0
            if motor_type in self.motor_status:
                self.motor_status[motor_type].encoder_position = 0

        self.logger.info("Enkoder sayaçları sıfırlandı")

    def calibrate_motors(self):
        """Motor kalibrasyonu"""
        self.logger.info("Motor kalibrasyonu başlatıldı")

        # Her motoru test et
        for motor_type in [MotorType.LEFT_DRIVE, MotorType.RIGHT_DRIVE]:
            self.logger.info(f"{motor_type.value} motoru test ediliyor")

            # Düşük hızda test
            self.set_motor_speed(motor_type, 50)  # 50 RPM
            time.sleep(2)

            # Durdur
            self.set_motor_speed(motor_type, 0)
            time.sleep(1)

        self.logger.info("Motor kalibrasyonu tamamlandı")

    def get_robot_velocity(self) -> Dict[str, float]:
        """Robot hızını hesapla"""
        left_status = self.motor_status.get(MotorType.LEFT_DRIVE)
        right_status = self.motor_status.get(MotorType.RIGHT_DRIVE)

        if not left_status or not right_status:
            return {"linear": 0.0, "angular": 0.0}

        # RPM'i m/s'ye çevir
        wheel_diameter = self.motor_params[MotorType.LEFT_DRIVE].wheel_diameter
        left_velocity = (left_status.rpm * math.pi * wheel_diameter) / 60
        right_velocity = (right_status.rpm * math.pi * wheel_diameter) / 60

        # Robot linear ve angular hızı
        linear_velocity = (left_velocity + right_velocity) / 2
        angular_velocity = (right_velocity - left_velocity) / self.wheel_base

        return {"linear": linear_velocity, "angular": angular_velocity}


if __name__ == "__main__":
    # Test kodu
    logging.basicConfig(level=logging.INFO)

    motor_controller = MotorController()
    motor_controller.start_monitoring()

    try:
        # Hareket testi
        print("İleri hareket...")
        motor_controller.move(0.5, 0)
        time.sleep(3)

        print("Dönüş...")
        motor_controller.move(0, 0.5)
        time.sleep(2)

        print("Dur...")
        motor_controller.stop_all()

        # Biçme testi
        print("Biçme bıçağı testi...")
        motor_controller.start_blade()
        time.sleep(2)
        motor_controller.stop_blade()

        # Durum kontrolü
        status = motor_controller.get_all_motor_status()
        print(f"Motor durumları: {status}")

    except KeyboardInterrupt:
        pass
    finally:
        motor_controller.stop_all()
        motor_controller.stop_monitoring()
        print("Motor kontrolcü durduruldu")
