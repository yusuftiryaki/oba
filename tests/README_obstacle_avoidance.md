# Engel Kaçınma Test Suite 🧪

Bu dizinde OBA Robot'un engel kaçınma sisteminin comprehensive test suite'i bulunmaktadır.

## Test Kategorileri

### 🔬 Unit Tests
- **TestObstacleAvoidance**: Ana engel kaçınma fonksiyonları
- **TestMultiSensorFusion**: Multi-sensor veri birleştirme
- **TestRecoveryBehavior**: Sıkışma durumu recovery sistemi
- **TestVelocitySmoothing**: Hız yumuşatma algoritması
- **TestStatistics**: İstatistik hesaplamaları

### 🔗 Integration Tests
- **TestIntegration**: End-to-end senaryo testleri

## Çalıştırma

### Temel Test
```bash
pytest tests/test_obstacle_avoidance.py -v
```

### Coverage Report ile
```bash
pytest tests/test_obstacle_avoidance.py -v --cov=src.navigation.obstacle_avoidance --cov-report=term-missing
```

### VS Code Tasks
- **Test Obstacle Avoidance**: Engel kaçınma testleri
- **Test All with Coverage**: Tüm testler + HTML coverage
- **Quick Tests**: Hızlı test (ilk hatada dur)

## Test Sonuçları

**✅ Son Test Sonuçları:**
- **22/22 test geçti** (100% pass rate)
- **%76 code coverage**
- **2.48s** test süresi

### Coverage Detayları
- Toplam satır: 329
- Kapsanan: 251
- Eksik: 78

### Kapsanmayan Alanlar
- Gerçek hardware I/O kodları (GPIO, I2C)
- Exception handling edge cases
- Simülasyon olmayan sensör okuma

## Test Senaryoları

### 🚨 Acil Durum Testleri
- Acil fren (20cm altında)
- Emergency stop verification

### 🎯 Normal Operasyon
- Güvenli mesafe kaçınma
- Uyarı mesafesi yavaşlama
- Engel yok durumu

### 🔄 Recovery Behavior
- Sıkışma algılama (3 saniye hareketsizlik)
- Geri git → Dön → İleri git stratejisi
- Otomatik normal moda dönüş

### 📡 Multi-Sensor
- IR, LIDAR, Kamera fusion
- Obstacle clustering (30cm threshold)
- Weighted confidence sistemi

### ⚡ Velocity Control
- Smooth acceleration/deceleration
- Speed limits (1.0 m/s linear, 2.0 rad/s angular)
- Acceleration limiting (0.5 m/s²)

## Sürekli Entegrasyon

Bu testler CI/CD pipeline'da her commit'de çalışır:

```yaml
# .github/workflows/tests.yml
- name: Test Obstacle Avoidance
  run: pytest tests/test_obstacle_avoidance.py --cov=src.navigation.obstacle_avoidance
```

## Test Ekleme

Yeni test eklemek için:

1. Uygun test sınıfına ekle
2. `setUp()` ve `tearDown()` kullan
3. Descriptive test isimleri
4. Edge case'leri dahil et
5. Coverage'ı kontrol et

## Mock ve Simülasyon

- Hardware bağımlılıkları mock'lanmış
- `simulate=True` ile test modunda çalışır
- Deterministik test sonuçları

## Performans

- Ortalama test süresi: ~2.5 saniye
- Memory usage: Minimal
- Paralel test desteği: Evet

---

**Son güncelleme:** 28 Haziran 2025
**Test coverage:** %76
**Test sayısı:** 22
**Status:** ✅ TÜM TESTLER GEÇİYOR
