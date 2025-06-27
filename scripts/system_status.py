#!/usr/bin/env python3
"""
OBA Robot - Sistem Durum İzleme Scripti
Robotun anlık durumunu izler ve raporlar.
"""

import sys
import time
import json
import psutil
import threading
from pathlib import Path
from datetime import datetime, timedelta

# Proje kök dizinini path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class SystemMonitor:
    def __init__(self):
        self.running = False
        self.data = {
            "system": {},
            "robot": {},
            "network": {},
            "storage": {},
            "processes": {},
        }

    def start_monitoring(self, interval=5):
        """Sistem izlemeyi başlat"""
        self.running = True
        print("🖥️ OBA Robot Sistem Durum İzlemesi Başlatıldı")
        print("=" * 60)
        print(f"Güncelleme aralığı: {interval} saniye")
        print("Çıkmak için Ctrl+C tuşlayın\n")

        try:
            while self.running:
                self.collect_system_data()
                self.display_status()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n🛑 İzleme durduruldu.")
            self.running = False

    def collect_system_data(self):
        """Sistem verilerini topla"""
        # Sistem bilgileri
        self.data["system"] = {
            "timestamp": datetime.now().isoformat(),
            "uptime": self.get_uptime(),
            "cpu_usage": psutil.cpu_percent(interval=1),
            "cpu_temperature": self.get_cpu_temperature(),
            "memory": self.get_memory_info(),
            "load_average": (
                psutil.getloadavg() if hasattr(psutil, "getloadavg") else [0, 0, 0]
            ),
        }

        # Robot durumu (simülasyon)
        self.data["robot"] = {
            "state": "BEKLEME",  # BIÇME, ŞARJA_DÖNME, ŞARJ_OLMA, BEKLEME
            "position": {"x": 15.5, "y": 8.2, "heading": 45.0},
            "battery": {
                "level": 78,
                "voltage": 25.2,
                "current": 2.1,
                "temperature": 32,
                "health": "GOOD",
            },
            "motors": {
                "left_track": {"speed": 0.0, "current": 0.1, "temperature": 35},
                "right_track": {"speed": 0.0, "current": 0.1, "temperature": 36},
                "cutting": {"speed": 0, "current": 0.0, "temperature": 28},
            },
            "sensors": {
                "imu": {"calibration": "GOOD", "temperature": 38},
                "encoders": {"left": 15420, "right": 15380},
                "camera": {"status": "ACTIVE", "fps": 30},
                "ir_sensors": {"sensor1": 45.2, "sensor2": 52.8},
            },
        }

        # Ağ durumu
        self.data["network"] = {
            "wifi_signal": -45,  # dBm
            "bytes_sent": psutil.net_io_counters().bytes_sent,
            "bytes_recv": psutil.net_io_counters().bytes_recv,
            "connections": len(psutil.net_connections()),
        }

        # Depolama durumu
        disk_usage = psutil.disk_usage("/")
        self.data["storage"] = {
            "total_gb": round(disk_usage.total / (1024**3), 1),
            "used_gb": round(disk_usage.used / (1024**3), 1),
            "free_gb": round(disk_usage.free / (1024**3), 1),
            "usage_percent": round((disk_usage.used / disk_usage.total) * 100, 1),
        }

        # Proses bilgileri
        self.data["processes"] = self.get_oba_processes()

    def get_uptime(self):
        """Sistem çalışma süresini al"""
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        uptime = timedelta(seconds=int(uptime_seconds))
        return str(uptime)

    def get_cpu_temperature(self):
        """CPU sıcaklığını al"""
        try:
            # Raspberry Pi için
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp = int(f.read().strip()) / 1000
                return round(temp, 1)
        except:
            # Diğer sistemler veya simülasyon
            return 58.2

    def get_memory_info(self):
        """Bellek bilgilerini al"""
        memory = psutil.virtual_memory()
        return {
            "total_mb": round(memory.total / (1024**2)),
            "used_mb": round(memory.used / (1024**2)),
            "available_mb": round(memory.available / (1024**2)),
            "usage_percent": round(memory.percent, 1),
        }

    def get_oba_processes(self):
        """OBA robot proseslerini bul"""
        oba_processes = []

        for proc in psutil.process_iter(
            ["pid", "name", "cpu_percent", "memory_percent"]
        ):
            try:
                if "python" in proc.info["name"].lower():
                    # Python proseslerinin komut satırını kontrol et
                    cmdline = " ".join(proc.cmdline())
                    if any(
                        keyword in cmdline.lower()
                        for keyword in ["oba", "robot", "main.py"]
                    ):
                        oba_processes.append(
                            {
                                "pid": proc.info["pid"],
                                "name": proc.info["name"],
                                "cpu_percent": proc.info["cpu_percent"],
                                "memory_percent": round(proc.info["memory_percent"], 1),
                                "cmdline": (
                                    cmdline[:50] + "..."
                                    if len(cmdline) > 50
                                    else cmdline
                                ),
                            }
                        )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return oba_processes

    def display_status(self):
        """Durum bilgilerini ekranda göster"""
        # Ekranı temizle
        print("\033[2J\033[H", end="")

        # Başlık
        print("🤖 OBA Robot Sistem Durumu")
        print("=" * 60)
        print(f"Son Güncelleme: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Sistem durumu
        sys_data = self.data["system"]
        print("🖥️ SİSTEM DURUMU")
        print(f"├─ Çalışma Süresi: {sys_data['uptime']}")
        print(f"├─ CPU Kullanımı: %{sys_data['cpu_usage']:.1f}")
        print(f"├─ CPU Sıcaklığı: {sys_data['cpu_temperature']}°C")
        print(
            f"├─ RAM Kullanımı: {sys_data['memory']['used_mb']}MB / {sys_data['memory']['total_mb']}MB (%{sys_data['memory']['usage_percent']})"
        )
        print(
            f"└─ Load Average: {sys_data['load_average'][0]:.2f}, {sys_data['load_average'][1]:.2f}, {sys_data['load_average'][2]:.2f}"
        )
        print()

        # Robot durumu
        robot_data = self.data["robot"]
        state_icons = {
            "BEKLEME": "⏸️",
            "BIÇME": "✂️",
            "ŞARJA_DÖNME": "🔄",
            "ŞARJ_OLMA": "🔋",
        }
        state_icon = state_icons.get(robot_data["state"], "❓")

        print("🤖 ROBOT DURUMU")
        print(f"├─ Durum: {state_icon} {robot_data['state']}")
        print(
            f"├─ Konum: X={robot_data['position']['x']:.1f}m, Y={robot_data['position']['y']:.1f}m, θ={robot_data['position']['heading']:.1f}°"
        )

        # Batarya durumu
        battery = robot_data["battery"]
        battery_icon = (
            "🔋" if battery["level"] >= 50 else "🪫" if battery["level"] >= 20 else "⚠️"
        )
        print(
            f"├─ Batarya: {battery_icon} %{battery['level']} ({battery['voltage']}V, {battery['current']}A, {battery['temperature']}°C)"
        )

        # Motor durumları
        motors = robot_data["motors"]
        print(f"├─ Motorlar:")
        print(
            f"│  ├─ Sol Palet: {motors['left_track']['speed']:.1f}m/s, {motors['left_track']['current']}A, {motors['left_track']['temperature']}°C"
        )
        print(
            f"│  ├─ Sağ Palet: {motors['right_track']['speed']:.1f}m/s, {motors['right_track']['current']}A, {motors['right_track']['temperature']}°C"
        )
        print(
            f"│  └─ Biçme: {motors['cutting']['speed']}rpm, {motors['cutting']['current']}A, {motors['cutting']['temperature']}°C"
        )

        # Sensör durumları
        sensors = robot_data["sensors"]
        print(f"└─ Sensörler:")
        print(
            f"   ├─ IMU: {sensors['imu']['calibration']} ({sensors['imu']['temperature']}°C)"
        )
        print(
            f"   ├─ Enkoder: L={sensors['encoders']['left']}, R={sensors['encoders']['right']}"
        )
        print(
            f"   ├─ Kamera: {sensors['camera']['status']} ({sensors['camera']['fps']} FPS)"
        )
        print(
            f"   └─ IR: {sensors['ir_sensors']['sensor1']}cm, {sensors['ir_sensors']['sensor2']}cm"
        )
        print()

        # Ağ durumu
        net_data = self.data["network"]
        print("📡 AĞ DURUMU")
        wifi_icon = (
            "📶"
            if net_data["wifi_signal"] >= -60
            else "📶" if net_data["wifi_signal"] >= -75 else "📵"
        )
        print(f"├─ Wi-Fi: {wifi_icon} {net_data['wifi_signal']} dBm")
        print(f"├─ Gönderilen: {self.format_bytes(net_data['bytes_sent'])}")
        print(f"├─ Alınan: {self.format_bytes(net_data['bytes_recv'])}")
        print(f"└─ Bağlantılar: {net_data['connections']}")
        print()

        # Depolama durumu
        storage = self.data["storage"]
        storage_icon = (
            "💾"
            if storage["usage_percent"] < 80
            else "⚠️" if storage["usage_percent"] < 95 else "🚨"
        )
        print("💾 DEPOLAMA")
        print(f"├─ Toplam: {storage['total_gb']} GB")
        print(
            f"├─ Kullanılan: {storage_icon} {storage['used_gb']} GB (%{storage['usage_percent']})"
        )
        print(f"└─ Boş: {storage['free_gb']} GB")
        print()

        # Prosesler
        processes = self.data["processes"]
        if processes:
            print("🔄 OBA PROSESLERİ")
            for proc in processes[:3]:  # İlk 3 proses
                print(
                    f"├─ PID {proc['pid']}: CPU %{proc['cpu_percent']:.1f}, RAM %{proc['memory_percent']}"
                )
            if len(processes) > 3:
                print(f"└─ ... ve {len(processes)-3} proses daha")
        else:
            print("🔄 OBA PROSESLERİ: Bulunamadı")
        print()

        # Durum özetı
        self.display_health_summary()

    def format_bytes(self, bytes_value):
        """Byte değerini okunabilir formata çevir"""
        for unit in ["B", "KB", "MB", "GB"]:
            if bytes_value < 1024:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024
        return f"{bytes_value:.1f} TB"

    def display_health_summary(self):
        """Sistem sağlık özetini göster"""
        health_issues = []

        # CPU kontrolü
        if self.data["system"]["cpu_usage"] > 80:
            health_issues.append("🔥 Yüksek CPU kullanımı")

        # Sıcaklık kontrolü
        if self.data["system"]["cpu_temperature"] > 70:
            health_issues.append("🌡️ Yüksek CPU sıcaklığı")

        # RAM kontrolü
        if self.data["system"]["memory"]["usage_percent"] > 85:
            health_issues.append("🧠 Yüksek RAM kullanımı")

        # Disk kontrolü
        if self.data["storage"]["usage_percent"] > 90:
            health_issues.append("💾 Disk alanı kritik")

        # Batarya kontrolü
        battery_level = self.data["robot"]["battery"]["level"]
        if battery_level < 20:
            health_issues.append("🔋 Düşük batarya")
        elif battery_level < 50:
            health_issues.append("⚠️ Batarya orta seviyede")

        # Wi-Fi kontrolü
        if self.data["network"]["wifi_signal"] < -75:
            health_issues.append("📶 Zayıf Wi-Fi sinyali")

        print("💊 SAĞLIK ÖZETİ")
        if not health_issues:
            print("└─ ✅ Tüm sistemler normal")
        else:
            for issue in health_issues:
                print(f"├─ {issue}")
            print("└─ ⚠️ Dikkat gerekli")
        print()

    def save_status_report(self):
        """Durum raporunu dosyaya kaydet"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"system_status_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

        return filename

    def generate_alerts(self):
        """Uyarı durumlarını kontrol et"""
        alerts = []

        # Kritik sistem uyarıları
        if self.data["system"]["cpu_temperature"] > 80:
            alerts.append(
                {
                    "level": "CRITICAL",
                    "message": f"CPU sıcaklığı kritik: {self.data['system']['cpu_temperature']}°C",
                }
            )

        if self.data["robot"]["battery"]["level"] < 10:
            alerts.append(
                {
                    "level": "CRITICAL",
                    "message": f"Batarya kritik seviyede: %{self.data['robot']['battery']['level']}",
                }
            )

        if self.data["storage"]["usage_percent"] > 95:
            alerts.append(
                {
                    "level": "CRITICAL",
                    "message": f"Disk alanı kritik: %{self.data['storage']['usage_percent']} dolu",
                }
            )

        # Uyarı seviyesi
        if self.data["system"]["memory"]["usage_percent"] > 90:
            alerts.append(
                {
                    "level": "WARNING",
                    "message": f"RAM kullanımı yüksek: %{self.data['system']['memory']['usage_percent']}",
                }
            )

        return alerts


def main():
    """Ana fonksiyon"""
    import argparse

    parser = argparse.ArgumentParser(description="OBA Robot Sistem Durum İzlemesi")
    parser.add_argument(
        "--interval", "-i", type=int, default=5, help="Güncelleme aralığı (saniye)"
    )
    parser.add_argument(
        "--save", "-s", action="store_true", help="Durumu dosyaya kaydet ve çık"
    )
    parser.add_argument("--json", action="store_true", help="JSON formatında çıktı")

    args = parser.parse_args()

    monitor = SystemMonitor()

    if args.save:
        # Tek sefer durum kaydı
        monitor.collect_system_data()
        filename = monitor.save_status_report()
        print(f"Sistem durumu kaydedildi: {filename}")

    elif args.json:
        # JSON çıktı
        monitor.collect_system_data()
        print(json.dumps(monitor.data, indent=2, ensure_ascii=False))

    else:
        # Sürekli izleme
        monitor.start_monitoring(args.interval)


if __name__ == "__main__":
    main()
