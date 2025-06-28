# 🧪 Test Sonuçları ve Raporlama

OT-BICME robot yazılımının test sonuçları çeşitli formatlarda kaydediliyor ve raporlanıyor.

## 📊 Test Sonuçlarının Kaydedildiği Yerler

### 1. **test_outputs/** Klasörü
Tüm test raporları bu klasörde toplanır:
```
test_outputs/
├── latest_results.json          # En son test sonuçları
├── test_results_YYYYMMDD_HHMMSS.json  # Timestamped sonuçlar
├── test_report.html            # HTML formatında detaylı rapor
├── kalman_report.json          # Kalman modülü detay raporu
├── motor_report.json           # Motor modülü detay raporu
├── obstacle_report.json        # Obstacle avoidance detay raporu
└── path_report.json           # Path planner detay raporu
```

### 2. **Coverage Raporları**
Her modül için ayrı coverage raporları:
```
test_outputs/
├── kalman_coverage/           # Kalman HTML coverage raporu
├── motor_coverage/           # Motor HTML coverage raporu
├── obstacle_coverage/        # Obstacle HTML coverage raporu
├── path_coverage/           # Path HTML coverage raporu
├── kalman_coverage.json     # Kalman JSON coverage
├── motor_coverage.json      # Motor JSON coverage
├── obstacle_coverage.json   # Obstacle JSON coverage
└── path_coverage.json      # Path JSON coverage
```

### 3. **pytest Cache**
```
.pytest_cache/              # pytest geçici dosyaları
└── README.md
```

## 🚀 Test Raporlarını Oluşturma

### Manuel Çalıştırma
```bash
# Tüm testleri çalıştır ve rapor oluştur
python3 scripts/test_reporter.py

# Tek modül testi ve raporu
python3 -m pytest tests/test_kalman_odometry.py --json-report --json-report-file=test_outputs/kalman_report.json -v

# Coverage ile test
python3 -m pytest tests/test_kalman_odometry.py --cov=src --cov-report=html:test_outputs/kalman_coverage --cov-report=json:test_outputs/kalman_coverage.json
```

### VS Code Tasks ile
1. **Ctrl+Shift+P** → "Tasks: Run Task"
2. **"Generate Test Report"** seçin
3. Terminal'de sonuçları göreceksiniz

### Otomatik CI/CD ile
```yaml
# .github/workflows/tests.yml (örnek)
- name: Run Tests and Generate Report
  run: python3 scripts/test_reporter.py

- name: Upload Test Results
  uses: actions/upload-artifact@v3
  with:
    name: test-reports
    path: test_outputs/
```

## 📋 Rapor Formatları

### 1. **JSON Format** (latest_results.json)
```json
{
  "timestamp": "2025-06-28T12:30:45",
  "modules": {
    "kalman_odometry": {
      "status": "PASS",
      "total": 21,
      "passed": 21,
      "failed": 0,
      "duration": 0.875
    }
  },
  "summary": {
    "total_tests": 85,
    "passed": 83,
    "failed": 2,
    "success_rate": 97.6
  }
}
```

### 2. **HTML Format** (test_report.html)
- Modern, responsive web arayüzü
- Modül bazında detaylı sonuçlar
- Grafik ve charts ile görselleştirme
- Browser'da açarak görüntüleyebilirsiniz

### 3. **Coverage Report** (HTML)
- Satır bazında kod kapsaması
- Hangi satırların test edilmediği
- Modül bazında coverage yüzdeleri

## 📈 Test Başarı Metrikleri

### Mevcut Durum
- **Kalman Odometry**: 21/21 ✅ (100%)
- **Motor Controller**: 22/22 ✅ (100%)
- **Obstacle Avoidance**: 22/22 ✅ (100%)
- **Path Planner**: 18/24 🔄 (75%)

### Toplam: 83/89 (%93 başarı)

## 🔧 Test Raporlama Sistemi

`scripts/test_reporter.py` otomatik olarak:
1. Tüm test modüllerini çalıştırır
2. JSON raporları oluşturur
3. Coverage analizi yapar
4. HTML raporu generate eder
5. Başarı oranını hesaplar
6. CI/CD için exit code döndürür

## 📱 Real-time Monitoring

Test sonuçlarını real-time takip etmek için:
```bash
# Test dosyalarını watch et
watch -n 2 'cat test_outputs/latest_results.json | jq .summary'

# HTML raporu browser'da aç
python3 -m http.server 8000 -d test_outputs
# http://localhost:8000/test_report.html
```

## 🎯 Kalite Hedefleri

- **Test Coverage**: >90%
- **Başarı Oranı**: >95%
- **Performance**: <10ms per test
- **Memory**: No leaks detected

---
**📊 Hacı Abi Test Framework** tarafından otomatik oluşturulur.
