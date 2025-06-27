1. Proje Tanımı ve Amacı
Bu doküman, meyve bahçelerinde yabancı ot biçme görevini otonom olarak yerine getirecek olan "Otonom Bahçe Asistanı (OBA)" adlı paletli robotun tasarım, geliştirme ve üretim süreçlerini tanımlamaktadır.

Projenin temel amacı, şebekeden bağımsız çalışan bir şarj istasyonuna sahip, kendi konumunu dahili sensörler ile takip ederek belirlenmiş alanları sistematik bir şekilde biçen, görev sonrası istasyonuna dönüp kendi kendine şarj olabilen, dayanıklı ve verimli bir otonom robot geliştirmektir. Proje, harici navigasyon sistemlerine (GPS, Sınır Teli vb.) bağımlı olmayacaktır.

2. Kapsam
2.1. Kapsam Dahilindekiler
Arazi koşullarına uygun, paletli ve dayanıklı bir şasi.
Ayarlanabilir yüksekliğe sahip, misinalı bir ot biçme mekanizması.
Ataletli Seyrüsefer (Dead Reckoning): Tekerlek enkoderleri ve IMU sensörü kullanarak robotun konumunu ve yönünü takip etmesi.
Gelişmiş Odometri: Sensör verilerini birleştirerek konum doğruluğunu artıran Kalman Filtresi implementasyonu.
Otonom Görev Yönetimi: Yazılımsal olarak tanımlanmış alanları sistematik bir rota (biçerdöver metodu) izleyerek biçme.
Otonom Şarj:
Batarya seviyesi kritik eşiğin altına düştüğünde görevi durdurup şarj istasyonuna yönelme.
Şarj istasyonunu görsel veya kızılötesi işaretçilerle bularak hassas yanaşma (docking) yapma.
Fiziksel temas ile şarj işlemini otomatik olarak başlatma ve tam dolunca sonlandırma.
Şarj İstasyonu: Güneş panelleri ile kendi enerjisini üreten ve depolayan şebekeden bağımsız (off-grid) bir yapı.
Uzaktan Erişim ve İzleme: Wi-Fi üzerinden erişilebilen, canlı kamera görüntüsü, robot durumu (batarya, konum vb.) ve manuel kontrol imkanı sunan bir web arayüzü.
Güvenlik: Acil Durdurma butonu ve yazılımsal güvenlik katmanları.
2.2. Kapsam Dışındakiler
GPS, Sınır Teli, LIDAR gibi harici navigasyon ve haritalama sistemleri.
Karmaşık 3D engel tanıma ve dinamik rota planlama (sadece temel ön engel algılama dahildir).
Birden fazla robotun koordineli çalışması (sürü zekası).
3. Fonksiyonel Gereksinimler
FR-01: Hareket: Robot, engebeli arazi koşullarında ±%15 eğime kadar stabil bir şekilde hareket edebilmelidir.
FR-02: Biçme: Biçme başlığının yüksekliği, web arayüzü üzerinden en az 3 farklı seviyede ayarlanabilmelidir.
FR-03: Konumlandırma:
FR-03.1: Robot, kendi konumunu (x,y) ve yönünü (heading) başlangıç noktasına göre sürekli olarak hesaplamalıdır.
FR-03.2: 1 saatlik çalışma sonunda konumlandırma hatası (kümülatif hata), 1 metrelik bir yarıçapın içinde kalmalıdır.
FR-04: Otonom Görev:
FR-04.1: Robot, web arayüzünden seçilen önceden tanımlı alanlarda görev yapabilmelidir.
FR-04.2: Batarya seviyesi %20'nin altına düştüğünde, robot mevcut görevini duraklatıp şarj istasyonuna dönmelidir.
FR-05: Otonom Şarj:
FR-05.1: Robot, şarj istasyonuna 100 metre mesafeden istasyonun konumunu algılayabilmelidir.
FR-05.2: Robot, şarj pedlerine ±1 cm hassasiyetle kenetlenebilmelidir.
FR-06: Uzaktan Kontrol: Kullanıcı, web arayüzü üzerinden robotu manuel olarak kontrol edebilmeli ve <500ms gecikme ile canlı kamera görüntüsünü izleyebilmelidir.
FR-07: Güç Yönetimi:
FR-07.1: Şarj istasyonu, ortalama bir güneşli günde kendi bataryasını ve robotu tam şarj edebilecek kapasitede olmalıdır.
FR-07.2: Robot, tek şarjla en az 2 saat biçme işlemi yapabilmelidir.
4. Teknik Şartname
4.1. Robot Bileşenleri
Kontrolcü: Raspberry Pi 4 Model B (min. 4GB RAM).
Motorlar: 2x Fırçasız DC Motor (BLDC) (paletler için, yüksek tork ve enkoder entegrasyonu için) veya Yüksek Torklu Redüktörlü DC Motorlar.
Biçme Motoru: 1x Fırçasız DC Motor (BLDC).
Güç Kaynağı: 24V LiFePO4 Batarya Paketi (min. 20Ah).
Navigasyon Sensörleri: 2x Yüksek Çözünürlüklü Döner Enkoder, 1x BNO055 (veya üstü) 9-DoF IMU.
Docking Sensörleri: 1x IR Kamera veya standart kamera (AprilTag tespiti için), 1-2x IR Mesafe Sensörü.
Kamera: Raspberry Pi Kamera Modülü V3.
Biçme Yükseklik Ayarı: 1x Lineer Aktüatör veya güçlü bir Servo Motor.
Bağlantı: Dahili Wi-Fi ve harici anten.
4.2. Şarj İstasyonu Bileşenleri
Güneş Paneli: min. 150W Monokristal Panel.
İstasyon Bataryası: 12V/24V min. 100Ah Deep-Cycle AGM veya LiFePO4 Batarya.
Şarj Kontrolcüsü: MPPT Solar Şarj Regülatörü (min. 20A).
Robot Şarj Devresi: İstasyon bataryasından robot bataryasını şarj edecek akıllı DC-DC şarj cihazı.
Docking İşaretçisi: Yüksek güçlü IR LED dizisi veya basılı bir AprilTag.
5. Yazılım Mimarisi
İşletim Sistemi: Raspberry Pi OS.
Programlama Dili: Python 3.
Web Framework: Flask veya FastAPI.
Ana Modüller:
main_controller.py: Ana durum makinesini (STATE: Biçme, Şarja Dönme, Şarj Olma, Bekleme) yönetir.
kalman_odometry.py: Enkoder ve IMU verilerini Kalman Filtresi ile birleştirerek hassas konum tahmini yapar.
path_planner.py: Alan verilerine göre biçerdöver rotası oluşturur.
docking_controller.py: Kamera/IR verilerini işleyerek hassas yanaşma manevralarını yönetir.
web_server.py: Uzaktan kontrol ve izleme için web arayüzünü sunar (ayrı bir thread/process olarak çalışır).
power_manager.py: Batarya seviyelerini izler ve şarj kararlarını verir.
config.json: Tüm sistem parametrelerini ve alan tanımlarını içerir.