# Bakım Eğitimi Kılavuzu

## Giriş

Hacı Abi, bu kılavuz OT-BiCME robotunun bakım ve onarımını öğrenmek isteyenler için hazırlanmıştır. Doğru bakım uygulamaları robotun uzun ömürlü ve güvenilir çalışmasını sağlar.

## İçindekiler

1. [Genel Bakım Prensipleri](#genel-bakım-prensipleri)
2. [Güvenlik Önlemleri](#güvenlik-önlemleri)
3. [Günlük Bakım](#günlük-bakım)
4. [Haftalık Bakım](#haftalık-bakım)
5. [Aylık Bakım](#aylık-bakım)
6. [Yıllık Bakım](#yıllık-bakım)
7. [Mekanik Sistemler](#mekanik-sistemler)
8. [Elektronik Sistemler](#elektronik-sistemler)
9. [Yazılım Bakımı](#yazılım-bakımı)
10. [Sorun Tespiti](#sorun-tespiti)
11. [Yedek Parçalar](#yedek-parçalar)
12. [Bakım Kayıtları](#bakım-kayıtları)

## Genel Bakım Prensipleri

### Bakım Felsefesi
```
Önleyici Bakım > Düzeltici Bakım > Acil Onarım
```

#### Temel İlkeler
1. **Düzenlilik:** Bakım programına uyun
2. **Temizlik:** Her bakımda temizlik yapın
3. **Kontrol:** Tüm sistemleri kontrol edin
4. **Kayıt:** Her işlemi kaydedin
5. **Güvenlik:** Güvenlik prosedürlerini takip edin

#### Bakım Seviyeleri

| Seviye | Kim Yapar | Sıklık | Süre |
|--------|-----------|--------|------|
| Seviye 1 | Operatör | Günlük | 15 dk |
| Seviye 2 | Teknisyen | Haftalık | 1 saat |
| Seviye 3 | Uzman | Aylık | 4 saat |
| Seviye 4 | Mühendis | Yıllık | 1 gün |

## Güvenlik Önlemleri

### Bakım Öncesi Güvenlik

#### Zorunlu Adımlar
```
☐ Robot güç kaynağını kesin
☐ Ana şalteri OFF konuma getirin
☐ "BAKIM YAPILIYOR" tabelası asın
☐ Acil durdur butonunu aktive edin
☐ 5 dakika bekleyin (kapasitör boşalması)
☐ Güvenlik ekipmanlarını giyin
```

#### Güvenlik Ekipmanları
- **Koruyucu Gözlük** (zorunlu)
- **Antiskid Eldiven** (zorunlu)
- **İş Ayakkabısı** (zorunlu)
- **İş Önlüğü** (önerilen)
- **Kask** (gerektiğinde)

#### Yasaklar
❌ **Robot çalışırken bakım yapmayın**
❌ **Batarya çıkarırken sigara içmeyin**
❌ **Elektronik parçaları suya bulaştırmayın**
❌ **Kablolaru çekmeyin**
❌ **Orijinal olmayan parça kullanmayın**

### Elektriksel Güvenlik

#### Voltaj Kontrolleri
```
Ana Güç: 24V DC (Güvenli)
Motor Sürücüleri: 48V DC (DİKKAT!)
Bilgisayar: 12V DC (Güvenli)
Sensörler: 5V DC (Güvenli)
```

#### Statik Elektrik Korunması
1. **ESD bilekliği takın**
2. **Metal yüzeylere dokunarak boşalın**
3. **Elektronik kartları kenarlarından tutun**
4. **Antistatik torba kullanın**

## Günlük Bakım (Seviye 1)

### Sabah Kontrolleri (15 dakika)

#### Görsel Kontrol
```
Kontrol Listesi:
☐ Gövdede hasar var mı?
☐ Tekerleklerde aşınma var mı?
☐ Kablolar düzgün bağlı mı?
☐ Sensörlerde kir var mı?
☐ Sıvı kaçağı var mı?
☐ Vida gevşekliği var mı?
```

#### Temizlik İşlemleri
1. **Gövde Temizliği**
   ```
   Malzemeler:
   - Mikrofiber bez
   - İzopropil alkol (%70)
   - Hava spreyi
   - Yumuşak fırça
   ```

2. **Sensör Temizliği**
   ```
   Lidar: Lens temizleyici + mikrofiber
   Kameralar: Özel lens bezi
   Ultrasonik: Kuru fırça
   IMU: Dokunmayın!
   ```

3. **Teker Temizliği**
   ```
   - Tekerlekleri döndürün
   - Saçakları temizleyin
   - Yağlama noktalarını kontrol edin
   - Teker yataklarını kontrol edin
   ```

#### Fonksiyon Testleri
```
Test Prosedürü:
1. Güç açın (Ana şalter ON)
2. Sistem boot süresini ölçün (< 60 saniye)
3. Tüm LED'lerin yanıp yanmadığını kontrol edin
4. Sensör verilerini kontrol edin
5. Kısa hareket testi yapın (1-2 metre)
6. Acil durdur butonunu test edin
```

### Akşam Kontrolleri (10 dakika)

#### Görev Sonrası
```
☐ Robot home pozisyonunda mı?
☐ Batarya şarj oluyor mu?
☐ Fanlar çalışıyor mu?
☐ Anormal ses var mı?
☐ Sıcaklık normal mi?
☐ Log dosyalarında hata var mı?
```

#### Şarj Durumu
```
Batarya Kontrolleri:
- Mevcut şarj: _____%
- Şarj akımı: _____A
- Batarya sıcaklığı: _____°C
- Tahmini şarj süresi: _____saat
```

## Haftalık Bakım (Seviye 2)

### Pazar Günü Bakımı (1 saat)

#### Detaylı Temizlik
1. **Elektronik Bölmesi**
   ```
   - Fan filtrelerini temizleyin
   - Toz birikimini temizleyin  
   - Kablo düzenini kontrol edin
   - Konektörleri kontrol edin
   ```

2. **Mekanik Bölümler**
   ```
   - Teker rulmanlarını kontrol edin
   - Tahrik kayışlarını kontrol edin
   - Motor bağlantılarını kontrol edin
   - Damperleri kontrol edin
   ```

#### Kalibrasyon Kontrolleri
```
Kalibrasyon Checklist:
☐ Lidar açı kalibrasyonu
☐ Kamera odak ayarı
☐ IMU sıfır noktası
☐ Teker odometresi
☐ Batarya ölçer kalibrasyonu
```

#### Yazılım Güncellemeleri
```bash
# Sistem güncellemesi kontrolü
sudo apt update && sudo apt list --upgradable

# ROS paketleri kontrol
rosdep check --from-paths src --ignore-src

# Python paketleri kontrol  
pip list --outdated

# Docker container'ları kontrol
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.CreatedAt}}"
```

#### Performans Testleri
1. **Hız Testi**
   ```
   Maksimum Hız: _____ m/s (hedef: 2.0 m/s)
   İvmelenme: _____ m/s² (hedef: 1.0 m/s²)
   Dönüş Hızı: _____ rad/s (hedef: 1.0 rad/s)
   ```

2. **Navigasyon Testi**
   ```
   Yol Planlama Süresi: _____ ms (hedef: <500ms)
   Lokalizasyon Hatası: _____ cm (hedef: <10cm)
   Engel Algılama Mesafesi: _____ cm (hedef: >30cm)
   ```

3. **Batarya Testi**
   ```
   Tam Şarj Süresi: _____ saat (hedef: <4 saat)
   Çalışma Süresi: _____ saat (hedef: >8 saat)
   Kapasitesi: _____% (hedef: >80%)
   ```

## Aylık Bakım (Seviye 3)

### Ay Sonu Kapsamlı Bakım (4 saat)

#### Mekanik Sistem Kontrolü

##### Tahrik Sistemi
```
Motor Kontrolleri:
☐ Motor karbonları (fırçalı motorlarda)
☐ Encoder bağlantıları
☐ Tahrik kayışı gerginliği
☐ Redüktör yağ seviyesi
☐ Rulman yağlaması
☐ Titreşim analizi
```

##### Süspansiyon Sistemi
```
Kontrol Noktaları:
☐ Amortisör çalışması
☐ Yay gerginlikleri
☐ Salıncak bağlantıları
☐ Tekerlek balans
☐ Fren sistemi (varsa)
```

#### Elektronik Sistem Kontrolü

##### Ana Kartlar
```
Test Prosedürü:
1. Ana bilgisayar kartını test edin
2. Motor sürücü kartlarını test edin
3. Sensör interface kartlarını test edin
4. Güç dağıtım kartını test edin
5. İletişim kartlarını test edin
```

##### Sensör Kalibrasyonu
```
Detaylı Kalibrasyon:
1. Lidar tam 360° kalibrasyonu
2. Kamera matrisi kalibrasyonu  
3. IMU tam kalibrasyon (6 eksende)
4. Ultrasonik sensör hassasiyet
5. Encoder reset ve kalibrasyon
```

#### Yazılım Bakımı

##### Sistem Optimizasyonu
```bash
# Disk temizliği
sudo apt autoremove
sudo apt autoclean
sudo journalctl --vacuum-time=30d

# Log rotasyonu
sudo logrotate -f /etc/logrotate.conf

# Veritabanı bakımı
sudo -u postgres vacuumdb -a -z

# Docker temizliği
docker system prune -f
```

##### Backup İşlemleri
```bash
# Sistem konfigürasyonu backup
tar -czf /backup/system_config_$(date +%Y%m%d).tar.gz /etc/

# ROS workspace backup
tar -czf /backup/catkin_ws_$(date +%Y%m%d).tar.gz ~/catkin_ws/

# Harita dosyaları backup
cp -r /opt/robot/maps/ /backup/maps_$(date +%Y%m%d)/

# Veritabanı backup
pg_dump robotdb > /backup/robotdb_$(date +%Y%m%d).sql
```

## Yıllık Bakım (Seviye 4)

### Kapsamlı Overhaul (1 gün)

#### Tam Sökme ve İnceleme
1. **Robot Sökümü**
   ```
   Sökme Sırası:
   1. Üst kapak ve sensörler
   2. Elektronik panel
   3. Batarya paketi
   4. Motor grupları
   5. Şasi bileşenleri
   6. Kablo demeti
   ```

2. **Parça İncelemesi**
   ```
   Her Parça İçin:
   ☐ Görsel hasar kontrolü
   ☐ Boyut ölçümü (aşınma)
   ☐ Elektriksel test
   ☐ Mekanik test
   ☐ Değiştirme kararı
   ```

#### Büyük Değişimler
- **Rulman değişimi**
- **Kayış değişimi**
- **Filtre değişimi**
- **Termal pad değişimi**
- **Batarya bakımı/değişimi**

#### Tam Sistem Testi
```
Fabrika Test Süreci:
1. Elektronik sistem testi (2 saat)
2. Mekanik sistem testi (2 saat)
3. Entegrasyon testi (2 saat)  
4. Saha testi (2 saat)
5. Sertifikasyon (belgelendirme)
```

## Mekanik Sistemler

### Motor Bakımı

#### Fırçasız DC Motorlar
```
Bakım Adımları:
1. Motor muhafazasını açın
2. Rotor ve stator temizliği
3. Rulman kontrolü
4. Encoder kontrolü
5. Termal kontrol
6. Elektriksel ölçümler
```

**Ölçüm Değerleri:**
```
Direnç: Phase A-B: ___Ω (hedef: 0.5±0.1Ω)
        Phase B-C: ___Ω (hedef: 0.5±0.1Ω)  
        Phase C-A: ___Ω (hedef: 0.5±0.1Ω)

İzolasyon: Phase-Gnd: ___MΩ (hedef: >10MΩ)

Encoder: A kanalı: ___V (hedef: 3.3±0.3V)
         B kanalı: ___V (hedef: 3.3±0.3V)
         Z kanalı: ___V (hedef: 3.3±0.3V)
```

#### Servo Motorlar
```
Servo Kalibrasyonu:
1. Mekanik sıfır pozisyonu bulun
2. Encoder sıfır pozisyonunu ayarlayın
3. PID parametrelerini optimize edin
4. Maksimum tork testini yapın
5. Hassasiyet testini yapın
```

### Teker ve Süspansiyon

#### Teker Bakımı
```
Kontrol Listesi:
☐ Teker kauçuk aşınması
☐ Jant çatlağı/deformasyonu  
☐ Rulman yumuşaklığı
☐ Balans kontrolü
☐ Basınç kontrolü (havalı tekerlerde)
☐ Sırt pattern derinliği
```

#### Süspansiyon Ayarı
```
Ayar Parametreleri:
Ön Sert.: ___kg/cm (önerilen: 15±2)
Arka Sert.: ___kg/cm (önerilen: 12±2)
Damper: ___cP (önerilen: 500±100)
Yükseklik: ___cm (önerilen: 25±1)
```

## Elektronik Sistemler

### Ana Bilgisayar

#### Donanım Kontrolleri
```bash
# CPU sıcaklığı kontrolü
sensors | grep "Core"

# RAM testi
memtest86+ (offline test)

# Disk sağlığı
sudo smartctl -a /dev/sda

# USB portları testi
lsusb -v

# Ethernet bağlantısı
ethtool eth0
```

#### Performans Testi
```bash
# CPU benchmark
sysbench cpu --threads=4 run

# Disk I/O testi  
sysbench fileio --file-test-mode=rndrw run

# Ağ hızı testi
iperf3 -c server_ip -t 30
```

### Sensör Sistemleri

#### Lidar Bakımı
```
Temizlik Prosedürü:
1. Güç kesin ve 5 dakika bekleyin
2. Döner ünityi durdurun
3. Lens yüzeyini temizleyin
4. Prizma sistemini kontrol edin
5. Motor rulmanlarını kontrol edin
6. Kalibrasyon test edin
```

**Lidar Test Sonuçları:**
```
Dönüş Hızı: ___rpm (hedef: 600±10)
Menzil Doğruluğu: ___cm (hedef: ±2cm)
Açı Çözünürlüğü: ___° (hedef: 0.25°)
Veri Hızı: ___Hz (hedef: 10Hz)
```

#### Kamera Sistemleri
```
Kamera Kontrolleri:
☐ Lens temizliği ve kontrolü
☐ Odaklama motoru testi
☐ IR filtre kontrolü (varsa)
☐ Görüntü sensörü pikselleri
☐ Kablo bağlantıları
☐ Kalibrasyon matrisi kontrolü
```

#### IMU Sistemi
```
IMU Kalibrasyonu:
1. Robot düz zemine yerleştirin
2. 5 dakika bekleyin (termal stabilite)
3. 6 eksende kalibrasyon yapın
4. Gyro bias değerlerini kaydedin
5. Akselerometre bias değerlerini kaydedin
6. Magnetometre offset değerlerini ayarlayın
```

### Güç Sistemleri

#### Batarya Bakımı
```
Litium İyon Batarya Kontrolü:
☐ Hücre voltajları (3.6-4.2V arası)
☐ Hücre sıcaklıkları (20-40°C arası)  
☐ Şarj/deşarj akımları
☐ Kapasitesi test edin
☐ BMS (Battery Management System) kontrol
☐ Termal pad kontrolü
```

**Batarya Test Sonuçları:**
```
Hücre 1: ___V  Hücre 7:  ___V  Hücre 13: ___V
Hücre 2: ___V  Hücre 8:  ___V  Hücre 14: ___V  
Hücre 3: ___V  Hücre 9:  ___V  Hücre 15: ___V
Hücre 4: ___V  Hücre 10: ___V  Hücre 16: ___V
Hücre 5: ___V  Hücre 11: ___V  Hücre 17: ___V
Hücre 6: ___V  Hücre 12: ___V  Hücre 18: ___V

Toplam Voltaj: ___V (hedef: 64.8-75.6V)
Kapasitesi: ___Ah (hedef: >80% nominal)
```

#### Güç Dağıtım Sistemi
```bash
# Voltaj kontrolü
echo "24V Rail: $(cat /sys/class/power_supply/main/voltage_now) µV"
echo "12V Rail: $(cat /sys/class/power_supply/aux/voltage_now) µV"  
echo "5V Rail: $(cat /sys/class/power_supply/logic/voltage_now) µV"

# Akım kontrolü
echo "Ana Akım: $(cat /sys/class/power_supply/main/current_now) µA"

# Güç faktörü
powerstat 1 10
```

## Yazılım Bakımı

### İşletim Sistemi

#### Ubuntu Bakımı
```bash
# Sistem güncellemeleri
sudo apt update
sudo apt upgrade -y
sudo apt dist-upgrade -y

# Gereksiz paket temizliği
sudo apt autoremove -y
sudo apt autoclean

# Snap paketleri güncelleme
sudo snap refresh

# Flatpak güncelleme (varsa)
flatpak update -y
```

#### Log Yönetimi
```bash
# Log boyutlarını kontrol et
sudo du -sh /var/log/*

# Eski logları temizle
sudo journalctl --vacuum-time=30d
sudo journalctl --vacuum-size=1G

# Log rotasyonu zorla
sudo logrotate -f /etc/logrotate.conf

# Sistem loglarını incele
sudo tail -f /var/log/syslog
```

### ROS Sistemi

#### ROS Paket Yönetimi
```bash
# Workspace temizliği
cd ~/catkin_ws
catkin clean -y

# Bağımlılık kontrolü
rosdep check --from-paths src --ignore-src

# Bağımlılıkları güncelle
rosdep update
rosdep install --from-paths src --ignore-src -r -y

# Workspace rebuild
catkin build
```

#### ROS Node Optimizasyonu
```bash
# Node performansını incele
rostopic hz /cmd_vel
rostopic hz /scan
rostopic hz /odom

# Message latency ölçümü
rostopic delay /camera/image_raw

# Network usage
rostopic bw /all

# Node resource usage  
top -p $(pgrep -d',' -f ros)
```

### Docker Yönetimi

#### Container Bakımı
```bash
# Container durumları
docker ps -a

# Image cleanup
docker image prune -f
docker system prune -f

# Volume cleanup
docker volume prune -f

# Container logs kontrolü
docker logs robot_navigation
docker logs robot_perception

# Container resource monitoring
docker stats
```

#### Docker Image Güncelleme
```bash
# Image'ları güncelle
docker pull robotics/navigation:latest
docker pull robotics/perception:latest

# Container'ları yeniden başlat
docker-compose down
docker-compose up -d

# Health check
docker-compose ps
```

## Sorun Tespiti

### Sistem Tanılama

#### Donanım Tanılama
```bash
# Sistem bilgileri
sudo dmidecode -t system
sudo lshw -short

# PCI cihazları
lspci -v

# USB cihazları
lsusb -v

# Disk durumu
sudo fdisk -l
df -h

# Memory test
sudo memtester 1G 1
```

#### Ağ Tanılama
```bash
# Ağ arayüzleri
ip addr show

# Routing tablosu
ip route show

# DNS çözümleme
nslookup google.com

# Port tarama
nmap -p 1-1000 localhost

# Bandwidth test
iperf3 -c 192.168.1.1
```

### Performans Analizi

#### CPU ve Memory
```bash
# CPU kullanımı
top -n 1 -b | head -20

# Memory kullanımı  
free -h
cat /proc/meminfo

# Disk I/O
iostat -x 1 5

# Load average
uptime
```

#### Süreç Analizi
```bash
# En çok CPU kullanan süreçler
ps aux --sort=-%cpu | head -10

# En çok memory kullanan süreçler
ps aux --sort=-%mem | head -10

# ROS node'ları
rosnode list
rosnode info /node_name

# Python süreçleri
ps aux | grep python
```

### Hata Analizi

#### Log Analizi
```bash
# Sistem hataları
sudo grep -i error /var/log/syslog
sudo grep -i warning /var/log/syslog

# ROS logları
roscd
find . -name "*.log" -exec grep -l ERROR {} \;

# Python exception'ları
find /var/log -name "*.log" -exec grep -l "Traceback" {} \;

# Kernel mesajları
dmesg | grep -i error
```

#### Crash Analizi
```bash
# Core dump kontrol
ls -la /var/crash/

# Segmentation fault analizi
gdb program core

# Python traceback analizi
python -u script.py 2>&1 | tee error.log

# Memory leak tespiti
valgrind --leak-check=full ./program
```

## Yedek Parçalar

### Kritik Yedek Parçalar

#### Elektronik Bileşenler
| Parça | Stok Miktarı | Minimum | Tedarikçi |
|-------|--------------|---------|-----------|
| Ana Bilgisayar | 1 | 1 | Nvidia/Intel |
| Motor Sürücü | 2 | 2 | Oriental Motor |
| Lidar Sensör | 1 | 1 | Hokuyo/Sick |
| IMU Sensör | 2 | 1 | Bosch/InvenSense |
| Kamera | 2 | 2 | Basler/Allied |
| Power Supply | 2 | 1 | Mean Well |
| Ethernet Switch | 1 | 1 | Cisco/Netgear |

#### Mekanik Bileşenler  
| Parça | Stok Miktarı | Minimum | Tedarikçi |
|-------|--------------|---------|-----------|
| Tekerlek | 4 | 2 | Colson/Blickle |
| Motor | 2 | 2 | Maxon/Faulhaber |
| Rulman | 10 | 4 | SKF/NSK |
| Kayış | 4 | 2 | Gates/Optibelt |
| Vida Takımı | 1 set | 1 set | DIN/ISO |
| Kablo | 10m | 5m | Lapp/Igus |

#### Sarf Malzemeleri
| Malzeme | Stok | Minimum | Kullanım |
|---------|------|---------|----------|
| Gres Yağı | 2 tüp | 1 tüp | Rulman |
| Temizlik Sprey | 3 kutu | 1 kutu | Genel |
| İzopropil Alkol | 2L | 1L | Elektronik |
| Mikrofiber Bez | 20 adet | 10 adet | Temizlik |
| Kablo Bağı | 100 adet | 50 adet | Organize |
| Termal Pad | 10 adet | 5 adet | Soğutma |

### Tedarik Planlaması

#### Sipariş Zamanlaması
```
Lead Time Tablosu:
Standart Parçalar: 1-2 hafta
Özel Parçalar: 4-6 hafta  
Elektronik Kartlar: 8-12 hafta
Mekanik İşleme: 2-4 hafta
İthal Parçalar: 6-8 hafta
```

#### Stok Yönetimi
```python
# Otomatik sipariş sistemi
def check_stock_levels():
    for part in critical_parts:
        if part.current_stock <= part.minimum_stock:
            send_order_alert(part)
            auto_order(part, part.order_quantity)
```

## Bakım Kayıtları

### Günlük Kayıt Formu

```
TARİH: ___/___/______
TEKNİSYEN: ___________________
VARDIYA: ☐ Sabah ☐ Öğle ☐ Akşam

GÜNLÜK KONTROLLER:
☐ Görsel muayene tamam
☐ Temizlik yapıldı
☐ Fonksiyon testleri tamam
☐ Batarya durumu normal
☐ Sensör temizliği yapıldı

ÖLÇÜMLER:
Batarya Voltajı: _____V
Çalışma Süresi: _____saat
Kat Edilen Mesafe: _____km
Ortalama Hız: _____m/s

NOTLAR:
________________________________
________________________________
________________________________

İMZA: ___________________
```

### Haftalık Bakım Raporu

```
HAFTA: ___/___/______ - ___/___/______
SORUMLU: ___________________________

YAPILAN İŞLER:
☐ Detaylı temizlik
☐ Kalibrasyon kontrolleri  
☐ Yazılım güncellemeleri
☐ Performans testleri
☐ Yedek parça kontrolü

PERFORMANS SONUÇLARI:
Maksimum Hız: _____m/s (Hedef: 2.0m/s)
Batarya Süresi: _____h (Hedef: 8h)
Lokalizasyon Hatası: _____cm (Hedef: <10cm)
Çalışma Süresi: _____% (Hedef: >95%)

SORUNLAR:
________________________________
________________________________

AKSIYONLAR:
________________________________
________________________________

SONRAKI HAFTA PLANI:
________________________________
________________________________

ONAY: ___________________
```

### Aylık Bakım Protokolü

```
AY/YIL: ___/______
UZMAN TEKNİSYEN: ________________

BÜYÜK BAKIM İŞLERİ:
☐ Mekanik sistem kontrolü
☐ Elektronik detaylı test
☐ Yazılım optimizasyonu
☐ Backup işlemleri
☐ Yedek parça değişimi

DEĞİŞTİRİLEN PARÇALAR:
Parça Adı: _____________ Seri No: _______
Parça Adı: _____________ Seri No: _______
Parça Adı: _____________ Seri No: _______

KALIBRASYON SONUÇLARI:
Lidar Kalibrasyonu: ☐ Tamam ☐ Gerekli
Kamera Kalibrasyonu: ☐ Tamam ☐ Gerekli  
IMU Kalibrasyonu: ☐ Tamam ☐ Gerekli
Motor Kalibrasyonu: ☐ Tamam ☐ Gerekli

PERFORMANS TREND ANALİZİ:
Bu Ay: _____% çalışma oranı
Geçen Ay: _____% çalışma oranı
Trend: ☐ İyileşiyor ☐ Sabit ☐ Kötüleşiyor

ÖNERİLER:
________________________________
________________________________

SONRAKI AY PLANI:
________________________________
________________________________

ONAYI: ___________________
```

### Yıllık Overhaul Raporu

```
YILI: ______
OVERHAUL TARİHİ: ___/___/______
MÜHENDİS: _______________________

BÜYÜK REVİZYON İŞLERİ:
☐ Tam söküm yapıldı
☐ Tüm parçalar incelendi
☐ Gerekli değişimler yapıldı
☐ Sistem entegrasyonu tamam
☐ Fabrika testleri geçti

YAPILAN BÜYÜK DEĞİŞİMLER:
________________________________
________________________________
________________________________

PERFORMANS IYILEŞTİRMELERİ:
Eski Performans: ________
Yeni Performans: ________
İyileşme: _____% 

MALIYET ANALİZİ:
Malzeme Maliyeti: _____TL
İşçilik Maliyeti: _____TL
Toplam Maliyet: _____TL

GARANTİ BİLGİLERİ:
Mekanik Sistem: _____ ay
Elektronik Sistem: _____ ay
Yazılım: _____ ay

SONRAKI YIL ÖNERİLERİ:
________________________________
________________________________

GENEL DEĞERLENDİRME:
☐ Mükemmel ☐ İyi ☐ Orta ☐ Zayıf

MÜHENDİS ONAYI: ________________
```

## Sonuç

Bu bakım eğitimi kılavuzu ile OT-BiCME robotunuzun uzun ömürlü ve güvenilir çalışmasını sağlayabilirsiniz.

### Önemli Hatırlatmalar
✅ **Güvenlik hiçbir zaman ihmal edilmemeli**
✅ **Düzenli bakım programına uyulmalı**
✅ **Tüm işlemler kayıt altına alınmalı**
✅ **Orijinal yedek parça kullanılmalı**
✅ **Uzman desteği alınmalı**

### Acil Durum İletişim
- **Teknik Destek:** +90 555 123 4567
- **Yedek Parça:** parts@ot-bicme.com
- **Eğitim:** training@ot-bicme.com

### Ek Kaynaklar
- [Teknik Dökümanlar](../documentation/)
- [Video Eğitimler](../training/videos/)
- [Yedek Parça Kataloğu](../parts/)
- [Servis Ağı](../service/)

---

**Hazırlayan:** OT-BiCME Bakım Ekibi
**Son Güncelleme:** 2024-01-15
**Versiyon:** 3.0.0
