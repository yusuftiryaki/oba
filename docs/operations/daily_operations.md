# 📋 Günlük Operasyon Kılavuzu

Bu doküman, OBA robotunuzun günlük operasyonu için adım adım prosedürleri içermektedir.

## 🌅 Sabah Rutini (Sistem Başlatma)

### 1. Pre-Flight Kontrol (5 dakika)
```bash
# Güvenlik kontrol scriptini çalıştır
python scripts/safety_check.py

# Sistem durumunu kontrol et
python scripts/system_status.py --quick
```

**Manuel Kontroller:**
- [ ] Batarya seviyesi >50%
- [ ] Acil durdurma butonu test edildi
- [ ] Biçme koruma kapağı takılı
- [ ] Çalışma alanı temiz (engel yok)
- [ ] Hava durumu uygun (yağmur yok)
- [ ] Wi-Fi bağlantısı stabil

### 2. Sistem Başlatma
```bash
# Ana robotu başlat
python main.py

# Web arayüzüne bağlan (tarayıcıda)
http://robot-ip:5000
```

**Başlangıç Doğrulama:**
- ✅ Robot durumu: "BEKLEME"
- ✅ Tüm sensörler aktif
- ✅ Kamera görüntüsü geliyor
- ✅ GPS alternatifi (odometri) kalibre

## 🎯 Görev Planlama

### Günlük Görev Oluşturma
1. **Web arayüzünde "Alan Yönetimi" sayfasına git**
2. **Biçilecek alanı seç:**
   - Alan boyutuna göre biçme süresi hesapla
   - Batarya kapasitesini kontrol et
   - Weather forecast kontrol et

3. **Biçme parametrelerini ayarla:**
   ```
   Biçme Yüksekliği: 3-4 (orta seviye)
   Hız: 0.4 m/s (normal)
   Düzen: Biçerdöver (en verimli)
   ```

### Haftalık Planlama
| Gün | Alan | Süre | Özel Notlar |
|-----|------|------|-------------|
| Pazartesi | Doğu Bahçe | 45 dk | Sabah erkenden (çiy kurumadan önce) |
| Salı | Batı Alan | 30 dk | Öğleden sonra |
| Çarşamba | - | - | Bakım günü |
| Perşembe | Doğu Bahçe | 45 dk | |
| Cuma | Batı Alan | 30 dk | |
| Cumartesi | Spot temizlik | 20 dk | Gerekirse |
| Pazar | - | - | İstirahat |

## 🏃‍♂️ Operasyon Süreci

### Standart Biçme Operasyonu

1. **Görev Başlatma:**
   ```
   Web Arayüzü → Kontrol Paneli → Alan Seç → "Biçme Başlat"
   ```

2. **İzleme (Operation Monitoring):**
   - **Canlı takip:** Robot pozisyonu haritada
   - **Batarya izleme:** %20'nin üstünde olmalı
   - **Hata takibi:** Kırmızı uyarılar varsa müdahale et
   - **Hız kontrolü:** Aşırı yavaşsa engel var demektir

3. **Normal Sonlandırma:**
   - Robot başlangıç noktasına döner
   - "Görev Tamamlandı" mesajı
   - İstatistikleri kaydet (süre, alan, batarya kullanımı)

### Acil Durumlar

#### 🚨 Acil Durdurma Prosedürü
```
1. FİZİKSEL BUTON → Kırmızı butona bas
2. WEB ARAYÜZÜ → "Emergency Stop" butonu
3. UZAKTAN → Telefon uygulaması panic button
```

#### ⚠️ Yaygın Sorunlar ve Çözümler

**Robot hareket etmiyor:**
```bash
# Sistem durumunu kontrol et
python scripts/system_status.py

# Motor testini çalıştır
python tests/hardware_test.py --test motors
```

**Biçme motoru çalışmıyor:**
- Koruma kapağını kontrol et
- Misina sıkışması var mı?
- Motor aşırı ısınmış olabilir (10 dk bekle)

**Yön bulma problemi:**
- IMU kalibrasyonu gerekebilir
- Enkoder temizliği yap
- Kalman filtre parametrelerini reset et

**Batarya hızla bitiyor:**
- Biçme yüksekliği çok düşük olabilir
- Motor akım çekimi kontrol et
- Çalışma hızını azalt (0.2 m/s)

## 📊 Günlük Raporlama

### Operasyon Logları
Her görev sonunda şunları kaydet:

```
Tarih: 27 Haziran 2025
Alan: Doğu Bahçe (600 m²)
Başlangıç: 09:00 - Bitiş: 09:45
Süre: 45 dakika
Batarya: %78 → %45 (33% kullanım)
Ortalama Hız: 0.4 m/s
Duraklamalar: 2 kez (5 dk toplam)
Sorunlar: Yok
```

### Performans Metrikleri
**Günlük Takip:**
- Biçilen alan (m²)
- Enerji verimliliği (m²/Wh)
- Ortalama hız
- Hata sayısı
- Bakım gereksinimleri

**Haftalık Analiz:**
- Toplam çalışma saati
- En verimli günler
- Sorun trendleri
- Parça değişim ihtiyaçları

## 🌙 Akşam Rutini

### 1. Günlük Temizlik (10 dakika)
- [ ] Biçme bölümündeki ot parçalarını temizle
- [ ] Kamerayı nemli bezle sil
- [ ] Sensörlerde toz/kir kontrol et
- [ ] Palet bölümlerini kontrol et

### 2. Şarj Kontrolü
```bash
# Batarya durumunu kontrol et
python scripts/system_status.py --json | grep battery

# Gerekirse şarj istasyonuna yönlendir
# Web arayüzü → "Şarj İstasyonuna Git"
```

### 3. Veri Yedekleme
```bash
# Günlük logları yedekle
cp logs/*.log backup/$(date +%Y%m%d)/

# Konfigürasyonu kaydet
python scripts/export_config.py --daily
```

### 4. Güvenlik Kontrolleri
- [ ] Robot güvenli alanda
- [ ] Acil durdurma erişilebilir
- [ ] Hava durumu ertesi gün için kontrol
- [ ] Şarj istasyonu güneş paneli temiz

## 📱 Uzaktan İzleme

### Mobil Takip
Web arayüzü mobil cihazlarda da çalışır:
```
http://robot-ip:5000
```

**Önemli Bildirimler:**
- Düşük batarya uyarısı
- Görev tamamlandı
- Hata/problem uyarıları
- Bakım zamanı geldi

### WhatsApp/SMS Bildirimleri (Opsiyonel)
Configuration ile aktifleştirilebilir:
```json
{
  "notifications": {
    "whatsapp": "+90555XXXXXXX",
    "critical_only": true,
    "daily_summary": true
  }
}
```

## 🎯 Verimlilik İpuçları

### Optimum Çalışma Saatleri
- **Sabah 08:00-10:00:** En iyi (çiy kuruduktan sonra)
- **Öğlen 12:00-14:00:** Kaçın (çok sıcak)
- **Akşam 16:00-18:00:** İdeal (güneş az, serin)

### Batarya Optimizasyonu
- Düşük hızda çalış (0.3 m/s) → +%30 menzil
- Biçme yüksekliğini artır → Az direnc
- Eğimli alanlarda hız azalt → Motor koruması

### Alan Planlaması
- Büyük alanları parçalara böl
- Engelli bölgeleri son bırak
- Dar geçitleri manuel kontrol et

---

**💡 Hacı Abi İpucu:** Her gün aynı rutini takip et, robot da alışır! Makine bile disiplin sever! 😄

Bu kılavuzu yazdır ve robot yanında tut. İlk 1 hafta adım adım takip et, sonra zaten alışkanlık olur!
