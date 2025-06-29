#!/bin/bash
# DHT22 Sensörü Kurulum Scripti
# Hacı Abi'nin Gerçek Donanım Kurulum Aracı

set -e

echo "🌡️ DHT22 Sensörü Kurulum Scripti"
echo "Hacı Abi - Gerçek Donanım Hazırlama"
echo "=" * 50

# Root kontrolü
if [[ $EUID -eq 0 ]]; then
   echo "❌ Bu script root ile çalıştırılmamalı!"
   echo "   Normal kullanıcı ile çalıştırın: ./setup_dht22_hardware.sh"
   exit 1
fi

# Raspberry Pi kontrolü
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️ Bu script Raspberry Pi'de çalışacak şekilde tasarlanmış"
    echo "   Devam etmek istiyor musunuz? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "❌ Kurulum iptal edildi"
        exit 1
    fi
fi

echo "📋 Sistem bilgileri kontrol ediliyor..."

# Python ve pip kontrolü
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 bulunamadı! Lütfen Python3 kurun:"
    echo "   sudo apt update && sudo apt install python3 python3-pip -y"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 bulunamadı! Lütfen pip3 kurun:"
    echo "   sudo apt install python3-pip -y"
    exit 1
fi

echo "✅ Python3 ve pip3 mevcut"

# GPIO kütüphaneleri kontrolü
echo "📦 GPIO kütüphaneleri kontrol ediliyor..."

# I2C ve SPI etkinleştir (Raspberry Pi)
if [[ -f /boot/config.txt ]]; then
    echo "🔧 I2C ve SPI ayarları kontrol ediliyor..."

    # I2C kontrolü
    if ! grep -q "^dtparam=i2c_arm=on" /boot/config.txt; then
        echo "  I2C etkinleştiriliyor..."
        echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
        I2C_CHANGED=1
    fi

    # SPI kontrolü
    if ! grep -q "^dtparam=spi=on" /boot/config.txt; then
        echo "  SPI etkinleştiriliyor..."
        echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
        SPI_CHANGED=1
    fi

    # GPIO grup ekleme
    echo "👥 Kullanıcı GPIO grubuna ekleniyor..."
    sudo usermod -a -G gpio,i2c,spi $USER
fi

# Python kütüphaneleri kurulumu
echo "📚 Python kütüphaneleri kuruluyor..."

# Adafruit kütüphaneleri
pip3 install --user adafruit-circuitpython-dht
pip3 install --user adafruit-blinka
pip3 install --user adafruit-circuitpython-bno055

echo "✅ Python kütüphaneleri kuruldu"

# Proje dizini kontrol
PROJECT_DIR="/home/$USER/oba-robot"
if [[ ! -d "$PROJECT_DIR" ]]; then
    echo "📁 Proje dizini oluşturuluyor: $PROJECT_DIR"
    mkdir -p "$PROJECT_DIR"
fi

# GPIO pin test scripti
echo "🧪 GPIO pin test scripti oluşturuluyor..."

cat > "$PROJECT_DIR/test_gpio_pins.py" << 'EOF'
#!/usr/bin/env python3
"""GPIO Pin Test Scripti - DHT22 için"""

import sys
import time

def test_gpio_access():
    """GPIO erişimi test et"""
    print("🔌 GPIO erişim testi...")

    try:
        import board
        print("✅ board kütüphanesi yüklendi")

        # GPIO4 pin erişimi
        pin = board.D4
        print(f"✅ GPIO4 pin nesnesi oluşturuldu: {pin}")

        return True
    except Exception as e:
        print(f"❌ GPIO erişim hatası: {e}")
        return False

def test_dht22_import():
    """DHT22 kütüphane import testi"""
    print("📚 DHT22 kütüphane testi...")

    try:
        import adafruit_dht
        print("✅ adafruit_dht kütüphanesi yüklendi")

        # DHT22 sensör nesnesi oluştur (sadece test)
        import board
        sensor = adafruit_dht.DHT22(board.D4)
        print("✅ DHT22 sensör nesnesi oluşturuldu")

        # Temizlik
        sensor.deinit()
        print("✅ Sensör temizlendi")

        return True
    except Exception as e:
        print(f"❌ DHT22 import hatası: {e}")
        return False

def main():
    print("🧪 DHT22 GPIO Test Scripti")
    print("=" * 30)

    all_tests_passed = True

    # GPIO test
    if not test_gpio_access():
        all_tests_passed = False

    print()

    # DHT22 test
    if not test_dht22_import():
        all_tests_passed = False

    print()

    if all_tests_passed:
        print("🎉 Tüm testler başarılı!")
        print("   DHT22 sensörü kullanıma hazır")
    else:
        print("❌ Bazı testler başarısız!")
        print("   Lütfen hataları kontrol edin")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

chmod +x "$PROJECT_DIR/test_gpio_pins.py"

echo "✅ Test scripti oluşturuldu: $PROJECT_DIR/test_gpio_pins.py"

# DHT22 hardware test scripti kopyala
if [[ -f "src/hardware/dht22_sensor.py" ]]; then
    echo "📋 DHT22 hardware scripti kopyalanıyor..."
    mkdir -p "$PROJECT_DIR/src/hardware"
    cp "src/hardware/dht22_sensor.py" "$PROJECT_DIR/src/hardware/"
    echo "✅ DHT22 hardware scripti kopyalandı"
fi

# Kurulum sonuç özeti
echo ""
echo "🎯 Kurulum Tamamlandı!"
echo "=" * 30

echo "📋 Yapılan işlemler:"
echo "  ✅ Python kütüphaneleri kuruldu"
echo "  ✅ GPIO erişimi yapılandırıldı"
echo "  ✅ Test scriptleri oluşturuldu"

if [[ "${I2C_CHANGED:-0}" -eq 1 ]] || [[ "${SPI_CHANGED:-0}" -eq 1 ]]; then
    echo ""
    echo "⚠️ DİKKAT: Sistem yeniden başlatma gerekli!"
    echo "   I2C/SPI ayarları değiştirildi"
    echo "   Lütfen sistemi yeniden başlatın: sudo reboot"
fi

echo ""
echo "🧪 Test Adımları:"
echo "1. GPIO test: python3 $PROJECT_DIR/test_gpio_pins.py"
echo "2. DHT22 test: python3 $PROJECT_DIR/src/hardware/dht22_sensor.py"

echo ""
echo "🔌 Hardware Bağlantıları:"
echo "  DHT22 Pin 1 (VCC)  -> Raspberry Pi 3.3V (Pin 1)"
echo "  DHT22 Pin 2 (DATA) -> Raspberry Pi GPIO4 (Pin 7)"
echo "  DHT22 Pin 3 (NC)   -> Bağlanmaz"
echo "  DHT22 Pin 4 (GND)  -> Raspberry Pi GND (Pin 6)"
echo ""
echo "  ⚠️ UNUTMAYIN: 10kΩ pull-up direnci (VCC-DATA arası)"

echo ""
echo "🎉 DHT22 sensörü kullanıma hazır!"
echo "   Hacı Abi'nin tavsiyesi: Önce testleri çalıştır!"
