# Web Arayüzü Kullanım Eğitimi

## Giriş

Hacı Abi, bu kılavuz OT-BiCME web arayüzünü kullanmayı öğrenmek isteyenler için hazırlanmıştır. Web arayüzü, robotun kontrolü, izlenmesi ve yönetimi için ana araçtır.

## İçindekiler

1. [Sistem Gereksinimleri](#sistem-gereksinimleri)
2. [İlk Giriş](#ilk-giriş)
3. [Ana Dashboard](#ana-dashboard)
4. [Robot Kontrolü](#robot-kontrolü)
5. [Harita ve Navigasyon](#harita-ve-navigasyon)
6. [Sensör Verileri](#sensör-verileri)
7. [Görev Yönetimi](#görev-yönetimi)
8. [Sistem Ayarları](#sistem-ayarları)
9. [Sorun Giderme](#sorun-giderme)
10. [Pratik Alıştırmalar](#pratik-alıştırmalar)

## Sistem Gereksinimleri

### Desteklenen Tarayıcılar
- **Chrome 90+** (Önerilen)
- **Firefox 88+**
- **Edge 90+**
- **Safari 14+**

### Minimum Sistem Gereksinimleri
- **RAM:** 4GB (8GB önerilen)
- **İşlemci:** Intel i3 veya AMD Ryzen 3
- **Ekran Çözünürlüğü:** 1366x768 minimum
- **İnternet:** 100 Mbps (lokal ağ için)

### Ağ Ayarları
```
Robot IP: 192.168.1.100
Port: 8080
Protocol: HTTP/WebSocket
```

## İlk Giriş

### 1. Sisteme Bağlanma
```
URL: http://192.168.1.100:8080
Kullanıcı Adı: operator
Şifre: [Yöneticinize danışın]
```

### 2. İlk Kurulum Adımları
1. **Tarayıcıyı açın**
2. **URL'yi girin**
3. **Giriş bilgilerini girin**
4. **"Beni Hatırla" seçeneğini işaretleyin**
5. **"Giriş Yap" butonuna tıklayın**

⚠️ **DİKKAT:** İlk girişte şifre değiştirmeniz istenecektir!

## Ana Dashboard

### Dashboard Bileşenleri

#### 1. Üst Menü Çubuğu
- **Ana Sayfa:** Dashboard'a dönüş
- **Robot Kontrolü:** Manuel kontrol paneli
- **Haritalar:** Harita yönetimi
- **Görevler:** Görev planlama ve takip
- **Ayarlar:** Sistem konfigürasyonu
- **Çıkış:** Güvenli çıkış

#### 2. Sol Panel - Durum Bilgileri
```
┌─────────────────────────┐
│ Robot Durumu            │
├─────────────────────────┤
│ ● Aktif                 │
│ Batarya: %85            │
│ Konum: (12.5, 8.3)      │
│ Hız: 0.5 m/s           │
└─────────────────────────┘
```

#### 3. Ana Görüntü Alanı
- **Canlı Kamera Görüntüsü**
- **Harita Görünümü**
- **Sensör Verileri Grafiği**

#### 4. Alt Panel - Hızlı Komutlar
- **Acil Durdur**
- **Eve Dön**
- **Otomatik Mod**
- **Manuel Mod**

### Dashboard Durum İkonları

| İkon | Anlam | Açıklama |
|------|-------|----------|
| 🟢 | Aktif | Robot çalışıyor |
| 🟡 | Beklemede | Robot durdu |
| 🔴 | Hata | Sorun var |
| 🔵 | Şarj | Şarj oluyor |
| ⚫ | Çevrimdışı | Bağlantı yok |

## Robot Kontrolü

### Manuel Kontrol Modu

#### Temel Hareket Komutları
```
Klavye Kısayolları:
W/↑ : İleri
S/↓ : Geri
A/← : Sola Dön
D/→ : Sağa Dön
SPACE: Durdur
E: Acil Durdur
```

#### Hız Kontrolü
1. **Hız Kaydırıcısı:** 0.1 - 2.0 m/s
2. **Dönüş Hızı:** 0.1 - 1.0 rad/s
3. **Hassas Mod:** 0.05 m/s maksimum

#### Güvenlik Kontrolleri
- **Engel Sensörü:** Otomatik durdurma
- **Düşme Sensörü:** Kenar algılama
- **Maksimum Hız Sınırı**
- **Güvenli Bölge Kontrolü**

### Otomatik Kontrol Modu

#### Navigasyon Ayarları
```yaml
navigasyon:
  planlama_algoritması: "A*"
  engel_mesafesi: 0.3  # metre
  güvenlik_marjı: 0.1  # metre
  maksimum_hız: 1.0    # m/s
  dönüş_hızı: 0.5      # rad/s
```

#### Hedef Belirleme
1. **Haritada Tıklama:** Direkt koordinat
2. **Koordinat Girişi:** X, Y değerleri
3. **Kayıtlı Noktalar:** Önceden tanımlı konumlar
4. **QR Kod:** Hedef kodları

## Harita ve Navigasyon

### Harita Türleri

#### 1. Canlı Harita
- **Gerçek Zamanlı Görüntü**
- **Robot Konumu**
- **Engel Tespiti**
- **Yol Planlama**

#### 2. Kayıtlı Haritalar
- **Kat Planları**
- **3D Haritalar**
- **Güvenlik Bölgeleri**
- **Yasak Alanlar**

### Harita Kontrolleri

#### Zoom ve Pan
```
Mouse Wheel: Zoom In/Out
Sol Tık + Sürükle: Haritayı kaydır
Sağ Tık: Bağlam menüsü
Çift Tık: O noktaya git
```

#### Katman Kontrolü
- ☑️ **Robot Yolu**
- ☑️ **Engellar**
- ☑️ **Güvenlik Bölgeleri**
- ☐ **Sensör Alanı**
- ☐ **WiFi Sinyali**

### Yol Planlama

#### Otomatik Planlama
1. **Hedef Seçin**
2. **"Rota Hesapla" tıklayın**
3. **Rotayı kontrol edin**
4. **"Başlat" butonuna basın**

#### Manuel Rota
1. **"Manuel Rota" modunu seçin**
2. **Ara noktaları tıklayın**
3. **Rotayı kaydedin**
4. **Çalıştırın**

## Sensör Verileri

### Sensör Paneli

#### 1. Lidar Sensörü
```
┌─────────────────────────┐
│ LIDAR - 360°            │
├─────────────────────────┤
│ Menzil: 10m             │
│ Çözünürlük: 0.25°       │
│ Frekans: 10Hz           │
│ Durum: ● Aktif          │
└─────────────────────────┘
```

#### 2. Kamera Sensörleri
- **Ön Kamera:** 1920x1080
- **Arka Kamera:** 1280x720
- **Derinlik Kamerası:** RGB-D
- **Gece Görüş:** IR aktif

#### 3. IMU Sensörü
```
Eğim: X: 0.2° Y: -0.1° Z: 0.0°
İvme: X: 0.1g Y: 0.0g Z: 1.0g
Açısal Hız: X: 0.0°/s Y: 0.0°/s Z: 2.1°/s
```

#### 4. Batarya ve Güç
```
Batarya Seviyesi: %85
Gerilim: 24.2V
Akım: 3.2A
Güç Tüketimi: 77W
Kalan Süre: 2h 15m
```

### Sensör Kalibrasyonu

#### Lidar Kalibrasyonu
1. **Robotu düz zemine yerleştirin**
2. **"Kalibrasyon" menüsüne gidin**
3. **"Lidar Kalibrasyonu" seçin**
4. **Referans noktaları ayarlayın**
5. **"Kalibrasyon Başlat" tıklayın**

#### Kamera Kalibrasyonu
1. **Kalibrasyon kartını hazırlayın**
2. **Kartı farklı açılardan gösterin**
3. **Yazılım otomatik kalibrasyon yapacak**
4. **Sonuçları kaydedin**

## Görev Yönetimi

### Görev Türleri

#### 1. Devriye Görevi
```yaml
görev_adı: "Gece Devriyesi"
başlangıç_zamanı: "22:00"
bitiş_zamanı: "06:00"
rota: ["A", "B", "C", "D", "A"]
tekrar: "günlük"
öncelik: "yüksek"
```

#### 2. Teslimat Görevi
```yaml
görev_adı: "Dokuman Teslimat"
başlangıç: "Ofis A"
hedef: "Ofis B"
yük: "doküman paketi"
maksimum_ağırlık: "2kg"
aciliyet: "normal"
```

#### 3. Temizlik Görevi
```yaml
görev_adı: "Koridor Temizlik"
alan: "koridor_1"
temizlik_modu: "vakum"
süre: "30 dakika"
günler: ["pazartesi", "çarşamba", "cuma"]
```

### Görev Programlama

#### Yeni Görev Oluşturma
1. **"Görevler" menüsüne gidin**
2. **"Yeni Görev" butonuna tıklayın**
3. **Görev türünü seçin**
4. **Parametreleri doldurun**
5. **Kaydet ve çalıştır**

#### Görev Şablonları
- **Günlük Devriye**
- **Haftalık Temizlik**
- **Acil Teslimat**
- **Güvenlik Turu**
- **Özel Görev**

### Görev İzleme

#### Aktif Görevler
```
┌─────────────────────────────────────┐
│ Görev: Gece Devriyesi               │
│ Durum: ● Devam Ediyor              │
│ İlerleme: ████████░░ %80            │
│ Kalan Süre: 45 dakika              │
│ Mevcut Konum: Koridor B             │
└─────────────────────────────────────┘
```

#### Görev Geçmişi
- **Tamamlanan Görevler**
- **İptal Edilen Görevler**
- **Başarısız Görevler**
- **Performans İstatistikleri**

## Sistem Ayarları

### Kullanıcı Ayarları

#### Profil Bilgileri
```
Kullanıcı Adı: operator
E-posta: operator@company.com
Rol: Operatör
Son Giriş: 2024-01-15 14:30
Dil: Türkçe
Tema: Koyu
```

#### Güvenlik Ayarları
- **Şifre Değiştir**
- **İki Faktörlü Kimlik Doğrulama**
- **Oturum Zaman Aşımı**
- **IP Kısıtlamaları**

### Sistem Konfigürasyonu

#### Robot Ayarları
```yaml
robot_id: "OT-BiCME-001"
maksimum_hız: 2.0  # m/s
güvenlik_mesafesi: 0.5  # metre
batarya_uyarı_seviyesi: 20  # %
otomatik_şarj: true
gece_modu: true
```

#### Ağ Ayarları
```yaml
wifi_ssid: "Robot_Network"
ip_adresi: "192.168.1.100"
subnet: "255.255.255.0"
gateway: "192.168.1.1"
dns: "8.8.8.8"
```

#### Sensör Ayarları
```yaml
lidar:
  frekans: 10  # Hz
  menzil: 10   # metre
  çözünürlük: 0.25  # derece

kamera:
  çözünürlük: "1920x1080"
  fps: 30
  otomatik_odaklama: true
  gece_görüş: true
```

### Bakım Ayarları

#### Otomatik Bakım
- **Günlük Sistem Kontrolü**
- **Haftalık Kalibrasyon**
- **Aylık Genel Bakım**
- **Acil Durum Kontrolleri**

#### Alarm Ayarları
```yaml
alarmlar:
  düşük_batarya: true
  sensör_hatası: true
  bağlantı_kopması: true
  engel_algılama: true
  sistem_hatası: true
```

## Sorun Giderme

### Yaygın Sorunlar ve Çözümleri

#### 1. Bağlantı Sorunları

**Sorun:** Web arayüzü açılmıyor
```
Çözüm Adımları:
1. IP adresini kontrol edin (192.168.1.100)
2. Ağ bağlantınızı test edin
3. Tarayıcı önbelleğini temizleyin
4. Farklı tarayıcı deneyin
5. Robot güç durumunu kontrol edin
```

**Sorun:** Yavaş yanıt
```
Çözüm Adımları:
1. Ağ hızını test edin
2. Diğer uygulamaları kapatın
3. Tarayıcı sekmelerini azaltın
4. Router'ı yeniden başlatın
```

#### 2. Kontrol Sorunları

**Sorun:** Robot komutlara yanıt vermiyor
```
Kontrol Listesi:
☐ Robot güç durumu
☐ Acil durdur butonu
☐ Manuel/Otomatik mod
☐ Sensör durumu
☐ Batarya seviyesi
```

**Sorun:** Hareket edememe
```
Olası Nedenler:
- Engel algılandı
- Güvenli bölge dışında
- Motor arızası
- Yazılım hatası
- Kalibrasyon problemi
```

#### 3. Görüntü Sorunları

**Sorun:** Kamera görüntüsü yok
```
Kontrol Adımları:
1. Kamera bağlantısını kontrol edin
2. Lens temizliğini kontrol edin
3. Aydınlatmayı kontrol edin
4. Kamera ayarlarını sıfırlayın
```

### Hata Kodları

| Kod | Açıklama | Çözüm |
|-----|----------|-------|
| E001 | Bağlantı Hatası | Ağ kontrolü |
| E002 | Sensör Hatası | Kalibrasyon |
| E003 | Motor Hatası | Teknisyen çağır |
| E004 | Batarya Hatası | Şarj kontrol |
| E005 | Yazılım Hatası | Restart |

### Acil Durum Prosedürleri

#### Acil Durdur
1. **Büyük kırmızı butona basın**
2. **"EMERGENCY STOP" yazısı görülmeli**
3. **Robot hareketsiz kalacak**
4. **Teknik ekibi arayın**

#### Sistem Restart
```
Güvenli Restart Adımları:
1. Tüm görevleri durdurun
2. Robot'u güvenli konuma alın
3. "Sistem Restart" butonuna basın
4. 2-3 dakika bekleyin
5. Sistem kontrollerini yapın
```

## Pratik Alıştırmalar

### Alıştırma 1: Temel Navigasyon

**Hedef:** Robotu A noktasından B noktasına götürmek

**Adımlar:**
1. Web arayüzüne giriş yapın
2. Manuel kontrol modunu seçin
3. Harita üzerinde A noktasını bulun
4. Klavye ile robotu A noktasına götürün
5. Otomatik moda geçin
6. B noktasını hedef olarak seçin
7. Rotayı hesaplatın ve çalıştırın

**Başarı Kriterleri:**
- Robot güvenli şekilde hareket etti ✓
- Engellere çarpmadı ✓
- Hedef noktaya ulaştı ✓
- Süre: < 5 dakika ✓

### Alıştırma 2: Görev Programlama

**Hedef:** Otomatik devriye görevi oluşturmak

**Adımlar:**
1. "Görevler" menüsüne gidin
2. "Yeni Görev" butonuna tıklayın
3. "Devriye" türünü seçin
4. Rota noktalarını belirleyin
5. Zaman aralığını ayarlayın
6. Görevi kaydedin ve çalıştırın

### Alıştırma 3: Sensör İzleme

**Hedef:** Sensör verilerini analiz etmek

**Adımlar:**
1. Sensör panelini açın
2. Lidar verilerini inceleyin
3. Kamera görüntüsünü kontrol edin
4. Batarya durumunu kaydedin
5. Anormal değerleri tespit edin

### Alıştırma 4: Sorun Giderme

**Senaryo:** Robot hareket etmiyor

**Yapılacaklar:**
1. Durum panelini kontrol edin
2. Hata kodlarını okuyun
3. Sensör durumlarını inceleyin
4. Çözüm adımlarını uygulayın
5. Sorunu raporlayın

## Sonuç

Bu eğitim kılavuzu ile OT-BiCME web arayüzünü etkin şekilde kullanabilirsiniz. Unutmayın:

### Önemli Noktalar
✅ **Güvenlik her zaman öncelik**
✅ **Düzenli sistem kontrolü yapın**
✅ **Sorunları hemen rapor edin**
✅ **Eğitimleri takip edin**
✅ **Yedeklemeyi unutmayın**

### İletişim Bilgileri
- **Teknik Destek:** support@ot-bicme.com
- **Acil Durum:** +90 555 123 4567
- **Dokümantasyon:** docs.ot-bicme.com

### Ek Kaynaklar
- [Video Eğitimler](training/videos/)
- [SSS](support/faq.md)
- [API Dokümantasyonu](api/README.md)
- [Topluluk Forumu](community/forum.md)

---

**Hazırlayan:** OT-BiCME Eğitim Ekibi
**Son Güncelleme:** 2024-01-15
**Versiyon:** 2.1.0
