# 🛡️ Güvenlik Prosedürleri

OBA robot operasyonlarında güvenlik en öncelikli konudur. Bu doküman, tüm güvenlik prosedürlerini ve acil durum planlarını içermektedir.

## ⚠️ Genel Güvenlik Kuralları

### 🚫 Mutlak Yasaklar
- ❌ Robot çalışırken çalışma alanına girme
- ❌ Hareket eden parçalara el sürme
- ❌ Koruma kapağını açık bırakma
- ❌ Elektriksel bağlantıları ıslak elle dokunma
- ❌ Bakım sırasında gücü açık tutma
- ❌ Çocukları robotun yakınında unsupervised bırakma

### ✅ Temel Güvenlik Önlemleri
- ✅ Her operasyon öncesi güvenlik kontrol listesini uygula
- ✅ Koruyucu ekipmanları kullan (eldiven, güvenlik gözlüğü)
- ✅ Acil durdurma butonunun yerini bil
- ✅ İlk yardım kitini hazır tut
- ✅ Yangın söndürücüyü robot yakınında bulundur
- ✅ Telsiz/telefon her zaman yanında olsun

## 📋 Pre-Flight Güvenlik Kontrol Listesi

### Sistem Kontrolleri
```bash
# Otomatik güvenlik kontrol scripti
python scripts/safety_check.py --full

# Beklenen çıktı: "✅ TÜM GÜVENLİK KONTROLLERİ BAŞARILI!"
```

### Manuel Kontroller (5 dakika)

#### 🔋 Güç Sistemi
- [ ] Batarya seviyesi >50%
- [ ] Batarya bağlantıları sıkı
- [ ] Kablo hasarı yok
- [ ] Ana güç şalteri çalışıyor
- [ ] Acil durdurma butonu test edildi

#### ⚙️ Mekanik Sistem
- [ ] Biçme koruma kapağı takılı ve sağlam
- [ ] Misina takılı ve hasar yok
- [ ] Paletler düzgün takılı
- [ ] Motor seslerinde anormallik yok
- [ ] Şasi üzerinde hasar/gevşeklik yok

#### 📡 Elektronik Sistem
- [ ] Tüm sensörler yeşil ışık
- [ ] Kamera görüntüsü net
- [ ] Wi-Fi bağlantısı stabil
- [ ] GPS alternatifi (odometri) kalibre
- [ ] Uzaktan kontrol test edildi

#### 🏞️ Çalışma Alanı
- [ ] Alan sınırları net tanımlı
- [ ] Engeller temizlendi
- [ ] İnsanlar/hayvanlar alan dışında
- [ ] Hava koşulları uygun
- [ ] Şarj istasyonu erişilebilir

## 🚨 Acil Durum Prosedürleri

### Acil Durdurma Seviyeleri

#### Seviye 1: Anında Durdurma
**Tetikleyiciler:**
- İnsan/hayvan çalışma alanına girdi
- Robot kontrolden çıktı
- Yangın/duman tespit edildi
- Şiddetli hava koşulları

**Eylem:**
```
1. FİZİKSEL BUTON → Kırmızı acil durdurma butonuna bas
2. GÜÇÜ KES → Ana güç şalterini kapat
3. ALANI TAHLİYE ET → Herkesi güvenli mesafeye çek
4. YARDIIM ÇAĞIR → Gerekirse 112
```

#### Seviye 2: Kontrollü Durdurma
**Tetikleyiciler:**
- Düşük batarya uyarısı
- Sensör arızası
- Hafif hava bozukluğu
- Biçme kalitesi düşük

**Eylem:**
```
1. WEB ARAYÜZÜ → "Güvenli Durdur" butonuna tıkla
2. POZISYON BEKLE → Robot güvenli konuma gelsin
3. SORUN TESPİT → System_status.py çalıştır
4. MÜDAHALE ET → Sorunu çöz veya uzman çağır
```

### Yaralanma Durumunda

#### Kesik/Ezilme Yaralanması
```
1. DERHAL DURDUR → Acil durdurma
2. KANAMAYA MÜDAHALE ET
   - Temiz bez/gazlı bez ile bask yap
   - Yaralı uzvu kalp seviyesinin üstünde tut
   - Yara büyükse → 112 ara
3. TIBBİ YARDIM → İlk yardım uygula
4. KAZA RAPORU → Incident report doldur
```

#### Elektrik Çarpması
```
1. GÜÇ KES → Ana şalteri derhal kapat
2. KURBANI TEMAS ETTİRME → İzole nesne kullan
3. 112 ARA → Elektrik çarpması ciddidir
4. İLK YARDIM → Nefes/nabız kontrolü
5. ARAYI DOKUMA → Uzman gelene kadar
```

### Yangın Durumunda

#### LiPO Batarya Yangını
```
⚠️ LiPO yangını su ile söndürülmez!

1. ALANI TAHLİYE ET → Minimum 10 metre mesafe
2. KÖPÜK/CO2 → Yangın söndürücü kullan
3. 112 ARA → İtfaiyeyi bilgilendir
4. SOĞUTMA → Yangın söndükten sonra çok su dökerek soğut
5. HAVALANDıR → Toksik gaz çıkabilir
```

#### Elektriksel Yangın
```
1. GÜÇ KES → Ana şalteri kapat
2. CO2/KURU KİMYEVİ → Uygun söndürücü kullan
3. SU KULLANMA → Elektrik riski
4. İTFAİYE → 112 ara
5. GÜVENLİ MESAFE → En az 5 metre uzakta dur
```

### Sistem Arızaları

#### Robot Kontrolden Çıkma
```
1. ACİL DURDUR → Fiziksel buton
2. WİFİ KES → Router'ı restart et
3. MANUEL YAKLAŞ → Güvenli mesafeden
4. GÜÇ KES → Ana şalteri kapat
5. UZMAN ÇAĞIR → Teknik destek
```

#### Sensör Arızası
```
1. GÜVENLE DURDUR → Web arayüzünden
2. DURUM KONTROLü → system_status.py
3. SENSÖR TESPİT → Hangi sensör problemi
4. YEDEKLİ ÇALIŞMA → Mümkünse safe mode
5. TAMİR/DEĞİŞİM → Uzman müdahalesi
```

## 🏥 İlk Yardım ve Acil İletişim

### İlk Yardım Kiti İçeriği
- Steril gazlı bez (10 adet)
- Elastic bandaj (2 adet)
- Antiseptik (250ml)
- Ağrı kesici (paracetamol)
- Termal blanket
- Eldiven (10 çift)
- Makas
- İlk yardım kılavuzu

### Acil İletişim Numaraları
```
🚑 ACİL SERVIS: 112
🚒 İTFAİYE: 112
👮 POLİS: 112
🏥 EN YAKIN HASTANE: [Yerel numara]
⚡ ELEKTRİK ARIZA: [Elektrikçi numarası]
🔧 TEKNİK DESTEK: [Proje geliştirici]
```

## 🔐 Güvenlik Bölgeleri

### Güvenlik Zonları
```
🔴 KIRMIZI BÖLGE (0-2m): Kesinlikle girilmez
   - Robot çalışma yarıçapı
   - Sadece robot durduğunda girilebilir

🟡 SARI BÖLGE (2-5m): Dikkatli yaklaşım
   - İzleme ve müdahale bölgesi
   - Koruyucu ekipman zorunlu

🟢 YEŞİL BÖLGE (5m+): Güvenli alan
   - Normal aktiviteler
   - Kontrol istasyonu burada
```

### Erişim Kontrolü
- **Yetkili Personel:** Tam erişim (eğitim almış)
- **Ziyaretçiler:** Sadece yeşil bölge
- **Çocuklar:** Sürekli gözetim altında
- **Hayvanlar:** Çalışma saatlerinde uzakta

## 📊 Risk Değerlendirmesi

### Yüksek Risk Faktörleri
| Risk | Olasılık | Etki | Önlem |
|------|----------|------|-------|
| Kesik yaralanması | Orta | Yüksek | Koruma kapağı, eğitim |
| Elektrik çarpması | Düşük | Çok Yüksek | İzolasyon, ELCB |
| Batarya yangını | Düşük | Yüksek | BMS, yangın söndürücü |
| Robot kaçması | Düşük | Orta | Çifte kontrol, acil durdurma |

### Risk Azaltma Stratejileri
1. **Eğitim:** Tüm operatörler sertifikalı olmalı
2. **Bakım:** Periyodik güvenlik kontrolleri
3. **Teknoloji:** Çoklu güvenlik katmanları
4. **Prosedür:** Standart operasyon prosedürleri
5. **İzleme:** Sürekli durum takibi

## 🎓 Güvenlik Eğitimi

### Temel Eğitim (4 saat)
- Robot güvenlik kuralları
- Acil durum prosedürleri
- İlk yardım temel bilgileri
- Pratik uygulamalar

### İleri Eğitim (8 saat)
- Teknik arıza giderme
- Risk analizi
- İnsident yönetimi
- Eğitmen sertifikası

### Sertifikasyon
```
✅ Temel Güvenlik Sertifikası: Her 6 ayda yenileme
✅ İleri Operatör Sertifikası: Her 12 ayda yenileme
✅ İlk Yardım Sertifikası: Her 24 ayda yenileme
```

## 📝 Dokümantasyon ve Raporlama

### Günlük Güvenlik Logları
```
Tarih: 27 Haziran 2025
Operatör: [İsim]
Çalışma Saati: 09:00-17:00
Güvenlik Kontrolleri: ✅ Tamamlandı
İnsidentler: Yok
Yakın Miss: Yok
Öneriler: -
```

### İnsident Raporu Formu
```
📋 KAZA/İNSİDENT RAPORU

Tarih/Saat: ___________
Lokasyon: ___________
Rapor Eden: ___________

Olay Açıklaması:
_________________________________

Yaralı Var mı?: □ Evet □ Hayır
Yaralı Sayısı: ___________
Tıbbi Müdahale: □ İlk Yardım □ Hastane □ Yok

Olay Nedeni:
□ İnsan Hatası □ Ekipman Arızası 
□ Prosedür İhlali □ Çevresel Faktör

Alınan Önlemler:
_________________________________

Gelecek İçin Öneriler:
_________________________________

İmza: ___________
```

## 🌦️ Hava Koşulları ve Güvenlik

### Güvenli Çalışma Koşulları
- 🌤️ **İdeal:** Açık, rüzgarsız, +15°C ile +30°C arası
- ⛅ **Kabul Edilebilir:** Hafif bulutlu, 25 km/h altı rüzgar
- 🌧️ **Çalışma Yasak:** Yağmur, kar, don, sis
- ⛈️ **Derhal Durdur:** Fırtına, şimşek, dolu

### Mevsimsel Özel Durumlar

#### Yaz Güvenliği
- Aşırı sıcakta (>35°C) çalışma yasak
- Batarya aşırı ısınma riski
- Operatör güneş çarpması riski
- Su kaynağı yakında bulundur

#### Kış Güvenliği  
- Don/buzlanma riski
- Batarya performans düşüklüğü
- Kaygan zemin tehlikesi
- Soğuk hava elbisesi giyin

---

**🛡️ Hacı Abi'nin Güvenlik Felsefesi:** 
"Güvenlik hiç şaka değil kardeşim! Robot ne kadar akıllı olsa da, en büyük güvenlik sistemi senin beynindir. Her adımı düşün, her hareketi planla. Acele eden robot sahibi, sonunda hastanede kahve içer!" 😄

**💡 Altın Kural:** Emin değilsen, YAPMA! Şüphe varsa, DURDUR! Robot tamirden çıkar, insan hastaneden çıkmaz!
