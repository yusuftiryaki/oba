# Otonom Bahçe Asistanı (OBA) - Sistem Mimarisi

## Genel Sistem Yapısı

```mermaid
graph TB
    subgraph "Robot Sistemi"
        A[Raspberry Pi 4B Kontrolcü] --> B[main_controller.py]
        B --> C[Durum Makinesi]
        C --> D1[BIÇME]
        C --> D2[ŞARJA_DÖNME]
        C --> D3[ŞARJ_OLMA]
        C --> D4[BEKLEME]
        
        B --> E[kalman_odometry.py]
        B --> F[path_planner.py]
        B --> G[docking_controller.py]
        B --> H[power_manager.py]
        B --> I[motor_controller.py]
        B --> J[web_server.py]
    end
    
    subgraph "Donanım Bileşenleri"
        K[2x BLDC Motor - Paletler]
        L[1x BLDC Motor - Biçme]
        M[2x Enkoder]
        N[BNO055 IMU]
        O[Pi Kamera V3]
        P[IR Sensörler]
        Q[Lineer Aktüatör]
        R[24V LiFePO4 Batarya]
        S[Wi-Fi Modülü]
    end
    
    subgraph "Şarj İstasyonu"
        T[150W Güneş Paneli]
        U[100Ah İstasyon Bataryası]
        V[MPPT Şarj Regülatörü]
        W[DC-DC Şarj Devresi]
        X[IR LED/AprilTag]
    end
    
    subgraph "Kullanıcı Arayüzü"
        Y[Web Arayüzü]
        Z[Canlı Kamera]
        AA[Manuel Kontrol]
        BB[Durum İzleme]
    end
    
    I --> K
    I --> L
    I --> Q
    E --> M
    E --> N
    G --> O
    G --> P
    H --> R
    J --> S
    J --> Y
    Y --> Z
    Y --> AA
    Y --> BB
    
    X --> G
    W --> H
    T --> V
    V --> U
    U --> W
```

## Veri Akış Diyagramı

```mermaid
flowchart LR
    A[Enkoder Verileri] --> B[kalman_odometry.py]
    C[IMU Verileri] --> B
    B --> D[Konum Tahmini x,y,θ]
    
    D --> E[path_planner.py]
    F[Alan Tanımları] --> E
    E --> G[Hedef Rotalar]
    
    G --> H[motor_controller.py]
    I[Kamera/IR] --> J[docking_controller.py]
    J --> H
    
    K[Batarya Sensörü] --> L[power_manager.py]
    L --> M[Durum Kararları]
    M --> N[main_controller.py]
    
    D --> N
    G --> N
    N --> O[Durum Değişiklikleri]
    O --> H
    
    P[Web İstekleri] --> Q[web_server.py]
    Q --> N
    N --> Q
    Q --> R[Web Yanıtları]
```

## Modül Bağımlılık Matrisi

| Modül | main_controller | kalman_odometry | path_planner | docking_controller | power_manager | motor_controller | web_server |
|-------|----------------|-----------------|--------------|-------------------|---------------|------------------|------------|
| main_controller | - | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| kalman_odometry | - | - | - | - | - | - | - |
| path_planner | - | ✓ | - | - | - | - | - |
| docking_controller | - | ✓ | - | - | - | - | - |
| power_manager | - | - | - | - | - | - | - |
| motor_controller | - | - | - | - | - | - | - |
| web_server | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | - |

## Donanım Bağlantı Şeması

### GPIO Pin Kullanımı (Raspberry Pi 4B)
- **Enkoder 1**: GPIO 18, 19 (Sol Palet)
- **Enkoder 2**: GPIO 20, 21 (Sağ Palet)
- **IMU (I2C)**: GPIO 2, 3 (SDA, SCL)
- **Motor Sürücü PWM**: GPIO 12, 13, 16, 26
- **Biçme Motor PWM**: GPIO 6, 7
- **IR Sensörler**: GPIO 23, 24
- **Lineer Aktüatör**: GPIO 25
- **Kamera**: CSI Portu
- **Wi-Fi**: Dahili

### Güç Dağıtımı
```
24V LiFePO4 Batarya
├── 24V → Motor Sürücüler
├── 12V → Biçme Motoru (DC-DC Dönüştürücü)
├── 5V → Raspberry Pi (DC-DC Dönüştürücü)
├── 5V → Sensörler
└── 3.3V → IMU, GPIO
```
