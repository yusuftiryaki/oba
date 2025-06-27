# Navigasyon Eğitimi 🗺️

## Giriş

Hacı Abi burada! Bu dokümanda robotumuzun navigasyon sistemini nasıl kullanacağını öğreneceksin. SLAM'dan yol planlamaya, engel algılamadan harita oluşturmaya kadar her şey var.

## 1. Temel Kavramlar

### SLAM (Simultaneous Localization and Mapping)
- **Ne yapar?** Robot aynı anda hem kendi konumunu belirler hem de çevrenin haritasını çıkarır
- **Nasıl çalışır?** Sensör verileri + algoritma = harita + konum
- **Neden önemli?** GPS olmayan kapalı alanlarda hayatta kalma rehberi

### Koordinat Sistemi
```
Y (ileri/geri)
^
|
|-----> X (sağ/sol)
|
v
Z (aşağı/yukarı)
```

## 2. Sensör Konfigürasyonu

### LiDAR Ayarları
```python
# LiDAR konfigürasyon örneği
lidar_config = {
    'scan_frequency': 10,  # Hz
    'angle_range': 360,    # derece
    'max_distance': 12.0,  # metre
    'min_distance': 0.12   # metre
}
```

### Kamera Ayarları
```python
# Stereo kamera ayarları
camera_config = {
    'resolution': (640, 480),
    'fps': 30,
    'baseline': 0.12,  # metre
    'focal_length': 525.0
}
```

## 3. Harita Oluşturma

### Yeni Harita Başlatma
1. **Sistem başlatma:**
   ```bash
   roslaunch navigation slam_mapping.launch
   ```

2. **Robot hareket ettirme:**
   - Yavaş ve düzenli hareket et
   - Ani dönüşlerden kaçın
   - Engellere çok yaklaşma

3. **Harita kalitesi kontrol:**
   - Duvarlar düz çizgiler olmalı
   - Köşeler net olmalı
   - Gürültülü veriler varsa yavaşla

### Harita Kaydetme
```bash
# Haritayı kaydet
rosrun map_server map_saver -f my_map

# Dosyalar oluşur:
# - my_map.yaml (metadata)
# - my_map.pgm (harita görüntüsü)
```

## 4. Navigasyon Modları

### Manuel Kontrol
```python
# Joystick ile kontrol
def manual_control():
    linear_speed = 0.5   # m/s
    angular_speed = 0.3  # rad/s
    
    # Güvenlik limitleri
    if linear_speed > 1.0:
        linear_speed = 1.0
    if angular_speed > 1.0:
        angular_speed = 1.0
```

### Otonom Navigasyon
```python
# Hedefe git
def goto_goal(x, y, theta):
    goal = MoveBaseGoal()
    goal.target_pose.header.frame_id = "map"
    goal.target_pose.pose.position.x = x
    goal.target_pose.pose.position.y = y
    goal.target_pose.pose.orientation.z = theta
    
    move_base_client.send_goal(goal)
```

## 5. Yol Planlama

### Global Path Planning
- **A* Algoritması:** Başlangıç-hedef arası en kısa yol
- **Dijkstra:** Tüm olası yolları değerlendir
- **RRT:** Rastgele örnekleme ile yol bul

### Local Path Planning
- **DWA (Dynamic Window Approach):** Hız sınırları içinde optimum yol
- **TEB (Timed Elastic Band):** Zamansal ve uzamsal optimizasyon

```python
# Yol planlama parametreleri
planning_params = {
    'max_vel_x': 0.8,      # m/s
    'max_vel_theta': 1.0,   # rad/s
    'acc_lim_x': 2.0,       # m/s²
    'acc_lim_theta': 3.0,   # rad/s²
    'goal_tolerance': 0.1   # metre
}
```

## 6. Engel Algılama ve Kaçınma

### Statik Engeller
- Duvarlar, mobilyalar, sabit objeler
- Haritada işaretli
- Global planlama ile kaçınılır

### Dinamik Engeller
- İnsanlar, hayvanlar, hareketli objeler
- Gerçek zamanlı algılama gerekli
- Local planlama ile kaçınılır

```python
# Engel algılama örneği
def detect_obstacles():
    scan = get_laser_scan()
    
    for i, distance in enumerate(scan.ranges):
        angle = scan.angle_min + i * scan.angle_increment
        
        if distance < 0.5:  # 50 cm yakınsa
            x = distance * cos(angle)
            y = distance * sin(angle)
            add_dynamic_obstacle(x, y)
```

## 7. Kalibrasyonlar

### Odometri Kalibrasyonu
```python
# Tekerleklerin çapı ve arası mesafe
wheel_diameter = 0.10      # metre
wheel_separation = 0.30    # metre

# Kalibrasyon faktörleri
linear_scale = 1.02        # ölçüm hatası düzeltme
angular_scale = 0.98       # dönüş hatası düzeltme
```

### Sensör Kalibrasyonu
```python
# LiDAR-robot merkezi offset
lidar_offset = {
    'x': 0.05,    # metre
    'y': 0.00,    # metre
    'theta': 0.0  # radyan
}

# Kamera-robot merkezi offset
camera_offset = {
    'x': 0.10,    # metre
    'y': 0.00,    # metre
    'z': 0.15     # metre
}
```

## 8. Sorun Giderme

### Robot Kayboldu
**Belirti:** Haritada konum bulunamıyor
**Çözüm:**
1. Bilinen bir konuma götür
2. `amcl` servisini yeniden başlat
3. Manuel konum belirle

```bash
# AMCL yeniden başlat
rosnode kill /amcl
roslaunch navigation amcl.launch
```

### Yol Bulunamıyor
**Belirti:** "No path found" hatası
**Çözüm:**
1. Harita güncel mi kontrol et
2. Hedef erişilebilir mi kontrol et
3. Inflation parametrelerini ayarla

### Robot Titriyor
**Belirti:** Hedefe yakın yerinde titreme
**Çözüm:**
1. Goal tolerance değerlerini artır
2. PID parametrelerini ayarla
3. Sensör gürültüsünü filtrele

## 9. İleri Düzey Özellikler

### Multi-Robot Koordinasyonu
```python
# Robot takım koordinasyonu
def coordinate_robots():
    robot_positions = get_all_robot_positions()
    
    for robot in robots:
        avoid_collision_with_others(robot, robot_positions)
        update_shared_map(robot.sensor_data)
```

### Adaptif Navigasyon
```python
# Çevre koşullarına göre parametreleri ayarla
def adaptive_navigation():
    if is_crowded_area():
        set_conservative_params()
    elif is_open_area():
        set_aggressive_params()
```

## 10. Performans Optimizasyonu

### CPU Kullanımı
- Sensör verilerini downsample et
- Gereksiz hesaplamaları önle
- Multi-threading kullan

### Bellek Yönetimi
- Eski harita verilerini temizle
- Buffer boyutlarını optimize et
- Memory leak kontrolü yap

### Ağ Trafiği
- Veri sıkıştırma kullan
- Gereksiz mesajları filtrele
- QoS ayarlarını optimize et

## 11. Test Senaryoları

### Temel Testler
1. **Düz koridor:** İleri-geri hareket
2. **L şekli koridor:** 90° dönüşler
3. **Açık alan:** Serbest hareket

### İleri Düzey Testler
1. **Dinamik engeller:** İnsan geçişi simülasyonu
2. **Çoklu hedef:** Waypoint takip etme
3. **Hata kurtarma:** Sensör kaybı simülasyonu

### Performans Metrikleri
- **Yol verimliliği:** Optimal yola yakınlık
- **Zaman performansı:** Hedefe ulaşma süresi
- **Güvenlik:** Çarpışma sayısı
- **Hassasiyet:** Hedef konum hatası

## 12. Bakım ve Kalibrasyonlar

### Günlük Kontroller
- [ ] Sensör temizliği
- [ ] Yazılım güncellemeleri
- [ ] Log dosyası kontrolü
- [ ] Kalibrasyon doğruluğu

### Haftalık Kontroller
- [ ] Harita güncellemesi
- [ ] Performans analizi
- [ ] Donanım kontrolü
- [ ] Yedekleme işlemleri

## Sonuç

Bu eğitim rehberi ile robotumuzun navigasyon sistemini etkili bir şekilde kullanabilirsin. Unutma, pratik yapmak teoriden daha önemli! Başlangıçta basit hareket komutlarıyla başla, sonra karmaşık navigasyon görevlerine geç.

**Hacı Abi İpucu:** İlk başta yavaş git, robotun davranışını anla. Sonra hızı artır. Acele etme, güvenlik her şeyden önemli!

---
*Bu dokümanda anlatılanları tam olarak anlamadıysan, hiç çekinme sorularını sor. Robotik zor iş, birlikte hallediyoruz! 🤖*
