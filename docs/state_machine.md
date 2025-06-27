# OBA Durum Makinesi (State Machine)

## Ana Durum Diyagramı

```mermaid
stateDiagram-v2
    [*] --> BAŞLATMA
    BAŞLATMA --> BEKLEME : Sistem Hazır
    
    BEKLEME --> BIÇME : Manuel Start / Zamanlı Görev
    BEKLEME --> MANUEL_KONTROL : Web Arayüzü İsteği
    BEKLEME --> ŞARJ_OLMA : Düşük Batarya & İstasyonda
    
    BIÇME --> BEKLEME : Görev Tamamlandı
    BIÇME --> ŞARJA_DÖNME : Batarya < %20
    BIÇME --> ACİL_DURDURMA : Emergency Stop
    BIÇME --> MANUEL_KONTROL : Kullanıcı Müdahalesi
    
    ŞARJA_DÖNME --> ŞARJ_OLMA : İstasyona Ulaştı
    ŞARJA_DÖNME --> ACİL_DURDURMA : Emergency Stop
    ŞARJA_DÖNME --> BEKLEME : Şarj İptal
    
    ŞARJ_OLMA --> BEKLEME : Şarj Tamamlandı (%95+)
    ŞARJ_OLMA --> ACİL_DURDURMA : Emergency Stop
    
    MANUEL_KONTROL --> BEKLEME : Manuel Kontrol Bitti
    MANUEL_KONTROL --> BIÇME : Manuel'den Otomatik Göreve
    MANUEL_KONTROL --> ACİL_DURDURMA : Emergency Stop
    
    ACİL_DURDURMA --> BEKLEME : Reset & Güvenlik Onayı
    
    note right of BIÇME
        Alt durumlar:
        - Rota Planlama
        - Navigasyon
        - Ot Biçme
        - Engel Kontrolü
    end note
    
    note right of ŞARJA_DÖNME
        Alt durumlar:
        - İstasyon Arama
        - Yönelme
        - Hassas Yaklaşma
        - Docking
    end note
```

## Biçme Alt-Durum Makinesi

```mermaid
stateDiagram-v2
    [*] --> ROTA_PLANLAMA
    
    ROTA_PLANLAMA --> NAVİGASYON : Rota Hazır
    ROTA_PLANLAMA --> [*] : Hata / İptal
    
    NAVİGASYON --> OT_BIÇME : Hedef Noktaya Ulaştı
    NAVİGASYON --> ENGEL_KONTROLÜ : Engel Tespit
    NAVİGASYON --> [*] : Rota Tamamlandı
    
    OT_BIÇME --> NAVİGASYON : Biçme Tamamlandı
    OT_BIÇME --> ENGEL_KONTROLÜ : Engel Tespit
    
    ENGEL_KONTROLÜ --> NAVİGASYON : Engel Geçildi/Aşıldı
    ENGEL_KONTROLÜ --> [*] : Aşılamaz Engel
    
    note right of ROTA_PLANLAMA
        - Alan sınırları kontrolü
        - Biçerdöver pattern
        - Başlangıç noktası belirleme
    end note
    
    note right of NAVİGASYON
        - Kalman odometri
        - Yön kontrolü
        - Hız ayarı
    end note
    
    note right of OT_BIÇME
        - Biçme motor kontrolü
        - Yükseklik ayarı
        - İlerleme hızı ayarı
    end note
```

## Şarj Alt-Durum Makinesi

```mermaid
stateDiagram-v2
    [*] --> İSTASYON_ARAMA
    
    İSTASYON_ARAMA --> YÖNELİM : İstasyon Bulundu
    İSTASYON_ARAMA --> [*] : İstasyon Bulunamadı
    
    YÖNELİM --> HASSAS_YAKLAŞIM : 5m Mesafede
    YÖNELİM --> İSTASYON_ARAMA : İstasyon Kaybedildi
    
    HASSAS_YAKLAŞIM --> DOCKING : 50cm Mesafede
    HASSAS_YAKLAŞIM --> YÖNELİM : Pozisyon Hatası
    
    DOCKING --> [*] : Bağlantı Başarılı
    DOCKING --> HASSAS_YAKLAŞIM : Bağlantı Başarısız
    
    note right of İSTASYON_ARAMA
        - 360° IR/kamera tarama
        - AprilTag tespiti
        - 100m menzil
    end note
    
    note right of HASSAS_YAKLAŞIM
        - IR sensör tabanlı konum
        - Yavaş yaklaşma (10cm/s)
        - Sürekli görüntü analizi
    end note
    
    note right of DOCKING
        - ±1cm hassasiyet
        - Fiziksel temas kontrolü
        - Şarj bağlantısı doğrulama
    end note
```

## Durum Geçiş Koşulları

### Sensör Tabanlı Geçişler
- **Batarya Seviyesi**: 
  - < %20: ŞARJA_DÖNME tetiklenir
  - > %95: ŞARJ_OLMA'dan çıkış
  - < %5: ACİL_DURDURMA (kritik batarya)

- **Konum Bilgisi**:
  - Hedef alan dışı: Rota yeniden planlanır
  - İstasyon yakınlığı (<5m): Docking prosedürü başlar
  - Başlangıç noktası: Görev tamamlandı

- **Engel Tespiti**:
  - Ön sensör: < 30cm engel → Dur ve değerlendir
  - IMU: Ani eğim değişimi → Güvenlik modu

### Kullanıcı Tetikli Geçişler
- **Web Arayüzü Komutları**:
  - Start/Stop/Pause butonları
  - Manuel kontrol modu
  - Acil durdurma
  - Alan seçimi ve görev tanımlama

### Zaman Tabanlı Geçişler
- **Timeout Kontrolü**:
  - İstasyon arama: 10 dakika
  - Docking denemesi: 5 dakika
  - Manuel kontrol: 30 dakika (güvenlik)

## Hata Durumları ve Kurtarma

```mermaid
stateDiagram-v2
    [*] --> HATA_TESPİT
    
    HATA_TESPİT --> MOTOR_HATASI : Motor Feedback Yok
    HATA_TESPİT --> SENSÖR_HATASI : Sensör Verisi Yok
    HATA_TESPİT --> İLETİŞİM_HATASI : Web Bağlantısı Kesildi
    HATA_TESPİT --> BATARYA_HATASI : Kritik Güç Durumu
    
    MOTOR_HATASI --> GÜVENLE_DUR : Motor Durdurma
    SENSÖR_HATASI --> YEDEKLİ_ÇALIŞMA : Sensör Fuzyon
    İLETİŞİM_HATASI --> OTONOM_MOD : Yerel Karar Verme
    BATARYA_HATASI --> ACİL_ŞARJ : Zorla İstasyona Dön
    
    GÜVENLE_DUR --> [*] : Manuel Müdahale
    YEDEKLİ_ÇALIŞMA --> [*] : Sensör Düzeldi
    OTONOM_MOD --> [*] : Bağlantı Restore
    ACİL_ŞARJ --> [*] : Şarj Başladı
```
