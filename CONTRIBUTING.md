# Contributing to OT-BiCME

Hacı Abi, OT-BiCME projesine katkıda bulunmak istediğin için teşekkürler! Bu dokümant projeye nasıl katkıda bulunabileceğin konusunda rehberlik edecek.

## 📋 İçindekiler

1. [Davranış Kuralları](#davranış-kuralları)
2. [Nasıl Katkıda Bulunabilirim?](#nasıl-katkıda-bulunabilirim)
3. [Geliştirme Ortamı Kurulumu](#geliştirme-ortamı-kurulumu)
4. [Katkı Süreci](#katkı-süreci)
5. [Kod Standartları](#kod-standartları)
6. [Testing](#testing)
7. [Dokümantasyon](#dokümantasyon)
8. [Issue Raporlama](#issue-raporlama)
9. [Pull Request Süreci](#pull-request-süreci)
10. [Topluluk](#topluluk)

## 🤝 Davranış Kuralları

Bu proje [Contributor Covenant](CODE_OF_CONDUCT.md) davranış kurallarını benimser. Projeye katılım göstererek bu kurallara uymayı kabul ediyorsun.

### Temel İlkeler
- **Saygılı olun**: Farklı görüşlere ve deneyimlere saygı gösterin
- **Yapıcı olun**: Eleştirileriniz yapıcı ve çözüm odaklı olsun
- **Kapsayıcı olun**: Herkesi dahil eden bir ortam yaratın
- **Öğrenmeye açık olun**: Hatalardan öğrenmeyi benimseyin

## 🚀 Nasıl Katkıda Bulunabilirim?

### Katkı Türleri

#### 1. Kod Katkıları
- **Bug fix'ler**: Mevcut hataları düzeltme
- **Yeni özellikler**: Roadmap'te bulunan özellikleri geliştirme
- **Performans iyileştirmeleri**: Mevcut kodu optimize etme
- **Refactoring**: Kod kalitesini artırma

#### 2. Dokümantasyon
- **API dokümantasyonu**: Kod ve API açıklamaları
- **Kullanıcı kılavuzları**: Son kullanıcı dokümantasyonu
- **Geliştirici rehberleri**: Teknik dokümantasyon
- **Örnek projeler**: Kullanım örnekleri

#### 3. Test ve Kalite
- **Unit testler**: Birim testleri yazma
- **Integration testler**: Entegrasyon testleri
- **Performance testler**: Performans ölçümü
- **Bug raporları**: Hata tespiti ve raporlama

#### 4. Tasarım ve UX
- **UI/UX iyileştirmeleri**: Kullanıcı arayüzü
- **Grafik tasarım**: İkonlar, logolar
- **Kullanılabilirlik testleri**: UX araştırması
- **Accessibility**: Erişilebilirlik iyileştirmeleri

#### 5. Topluluk Katkıları
- **Forum moderasyonu**: Topluluk yönetimi
- **Eğitim içerikleri**: Tutorial ve workshop'lar
- **Çeviriler**: Çoklu dil desteği
- **Etkinlik organizasyonu**: Meetup ve konferanslar

## 🛠️ Geliştirme Ortamı Kurulumu

### Sistem Gereksinimleri

#### Minimum Gereksinimler
```yaml
os: "Ubuntu 20.04 LTS veya daha yeni"
ram: "8GB (16GB önerilen)"
disk: "50GB boş alan"
processor: "Intel i5 veya AMD Ryzen 5"
```

#### Gerekli Yazılımlar
```bash
# Temel araçlar
sudo apt update
sudo apt install -y git curl wget build-essential

# Python geliştirme ortamı
sudo apt install -y python3.9 python3.9-dev python3-pip
pip3 install --upgrade pip setuptools wheel

# ROS 2 Humble
curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | sudo apt-key add -
sudo sh -c 'echo "deb http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" > /etc/apt/sources.list.d/ros2-latest.list'
sudo apt update
sudo apt install -y ros-humble-desktop

# Docker ve Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
sudo apt install -y docker-compose
```

### Repository Kurulumu

#### 1. Fork ve Clone
```bash
# Repository'yi fork edin (GitHub web arayüzünde)
# Kendi fork'unuzu clone edin
git clone https://github.com/YOURUSERNAME/ot-bicme.git
cd ot-bicme

# Upstream repository'yi ekleyin
git remote add upstream https://github.com/orcad-management/ot-bicme.git
```

#### 2. Geliştirme Ortamı
```bash
# Virtual environment oluşturun
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükleyin
pip install -r requirements-dev.txt

# Pre-commit hooks kurulumu
pre-commit install

# ROS workspace kurulumu
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

#### 3. IDE Konfigürasyonu

**VS Code** (Önerilen)
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "files.trimTrailingWhitespace": true
}
```

**Extensions**
- Python
- ROS
- GitLens
- Docker
- YAML

## 📝 Katkı Süreci

### 1. Issue Seçimi

#### Yeni Başlayanlar İçin
```bash
# Good first issue etiketli issue'ları bulun
label:"good first issue"

# Help wanted etiketli issue'ları inceleyin
label:"help wanted"
```

#### Deneyimli Geliştiriciler
- Feature request'ler
- Architecture iyileştirmeleri
- Performance optimizasyonları
- Complex bug fix'ler

### 2. Branch Stratejisi

#### Branch Naming Convention
```bash
# Feature branches
feature/navigation-improvement
feature/web-ui-redesign

# Bug fix branches
fix/sensor-calibration-issue
fix/memory-leak-navigation

# Documentation branches
docs/api-documentation
docs/installation-guide

# Hotfix branches
hotfix/critical-security-fix
```

#### Branch Workflow
```bash
# Ana branch'den yeni branch oluşturun
git checkout main
git pull upstream main
git checkout -b feature/your-feature-name

# Çalışmanızı yapın
git add .
git commit -m "feat: add navigation improvement"

# Remote'a push edin
git push origin feature/your-feature-name
```

### 3. Commit Standartları

#### Conventional Commits
Format: `<type>(<scope>): <description>`

**Types:**
- `feat`: Yeni özellik
- `fix`: Bug fix
- `docs`: Dokümantasyon değişikliği
- `style`: Kod formatı (logic değişikliği yok)
- `refactor`: Kod refactoring
- `test`: Test ekleme/değiştirme
- `chore`: Build/maintenance

**Scopes:**
- `nav`: Navigation sistemi
- `ui`: Web arayüzü
- `sensor`: Sensör sistemleri
- `api`: API değişiklikleri
- `db`: Veritabanı
- `docs`: Dokümantasyon

**Örnekler:**
```bash
feat(nav): implement A* pathfinding algorithm
fix(sensor): resolve lidar calibration issue
docs(api): update REST API documentation
test(nav): add unit tests for path planning
refactor(ui): reorganize component structure
```

## 💻 Kod Standartları

### Python Kod Standartları

#### Formatting
```python
# Black formatter kullanın
black --line-length 88 your_file.py

# Import sıralaması (isort)
isort your_file.py

# Type hints kullanın
def calculate_distance(point1: Tuple[float, float], 
                      point2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
```

#### Code Quality
```python
# Pylint score >= 8.0
pylint your_file.py

# Flake8 kontrolü
flake8 your_file.py

# MyPy type checking
mypy your_file.py
```

#### Docstring Standardı
```python
def navigate_to_point(self, target: Position, speed: float = 1.0) -> bool:
    """Navigate robot to target position.
    
    Args:
        target: Target position (x, y) coordinates
        speed: Movement speed in m/s (default: 1.0)
        
    Returns:
        True if navigation successful, False otherwise
        
    Raises:
        NavigationError: If path planning fails
        SensorError: If sensor data is invalid
        
    Example:
        >>> robot = Robot()
        >>> target = Position(x=10.0, y=5.0)
        >>> success = robot.navigate_to_point(target, speed=0.5)
        >>> print(f"Navigation successful: {success}")
    """
    pass
```

### C++ Kod Standartları

#### Google Style Guide
```cpp
// Header guards
#ifndef OT_BICME_NAVIGATION_PLANNER_H_
#define OT_BICME_NAVIGATION_PLANNER_H_

// Namespace
namespace ot_bicme {
namespace navigation {

// Class naming
class PathPlanner {
 public:
  // Function naming
  bool PlanPath(const Position& start, const Position& goal);
  
 private:
  // Member variable naming
  std::vector<Position> path_points_;
  double max_speed_;
};

}  // namespace navigation
}  // namespace ot_bicme

#endif  // OT_BICME_NAVIGATION_PLANNER_H_
```

### JavaScript/TypeScript

#### ESLint Configuration
```json
{
  "extends": [
    "@typescript-eslint/recommended",
    "prettier/@typescript-eslint"
  ],
  "rules": {
    "prefer-const": "error",
    "no-var": "error",
    "@typescript-eslint/explicit-function-return-type": "error"
  }
}
```

#### Kod Örneği
```typescript
interface RobotStatus {
  position: Position;
  batteryLevel: number;
  isMoving: boolean;
}

class RobotController {
  private robotStatus: RobotStatus;

  public async moveToPosition(target: Position): Promise<boolean> {
    try {
      const path = await this.planPath(target);
      return await this.executePath(path);
    } catch (error) {
      console.error('Navigation failed:', error);
      return false;
    }
  }

  private async planPath(target: Position): Promise<Position[]> {
    // Implementation
    return [];
  }
}
```

## 🧪 Testing

### Test Kategorileri

#### Unit Tests
```python
import unittest
from unittest.mock import Mock, patch
from ot_bicme.navigation import PathPlanner

class TestPathPlanner(unittest.TestCase):
    def setUp(self):
        self.planner = PathPlanner()
        
    def test_plan_straight_path(self):
        start = Position(0, 0)
        goal = Position(10, 0)
        path = self.planner.plan_path(start, goal)
        
        self.assertIsNotNone(path)
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], goal)
        
    @patch('ot_bicme.sensors.lidar')
    def test_plan_with_obstacles(self, mock_lidar):
        mock_lidar.get_scan.return_value = self.sample_scan_data()
        # Test implementation
```

#### Integration Tests
```python
import pytest
from ot_bicme.robot import Robot
from ot_bicme.simulation import SimulationEnvironment

@pytest.fixture
def robot_with_sim():
    sim_env = SimulationEnvironment()
    robot = Robot(simulation=sim_env)
    return robot, sim_env

def test_end_to_end_navigation(robot_with_sim):
    robot, sim_env = robot_with_sim
    
    # Set up environment
    sim_env.add_obstacle(Position(5, 5), radius=1.0)
    
    # Execute navigation
    start = Position(0, 0)
    goal = Position(10, 10)
    success = robot.navigate_to(goal)
    
    assert success
    assert robot.current_position.distance_to(goal) < 0.1
```

#### Performance Tests
```python
import time
import pytest
from ot_bicme.navigation import PathPlanner

class TestPerformance:
    def test_path_planning_performance(self):
        planner = PathPlanner()
        start = Position(0, 0)
        goal = Position(100, 100)
        
        start_time = time.time()
        path = planner.plan_path(start, goal)
        execution_time = time.time() - start_time
        
        assert path is not None
        assert execution_time < 0.5  # Must complete within 500ms
```

### Test Running

#### Local Testing
```bash
# Python tests
pytest tests/ -v --cov=ot_bicme

# C++ tests
cd build
make test

# JavaScript tests
npm test

# Integration tests
pytest tests/integration/ -v

# Performance tests
pytest tests/performance/ -v --benchmark-only
```

#### CI Pipeline
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          pytest tests/ --cov=ot_bicme --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

## 📚 Dokümantasyon

### Dokümantasyon Türleri

#### 1. Code Documentation
```python
class NavigationSystem:
    """Main navigation system for autonomous robot.
    
    This class provides path planning, obstacle avoidance, and
    localization capabilities for the OT-BiCME robot.
    
    Attributes:
        current_position: Current robot position
        target_position: Target destination
        obstacle_map: Current obstacle map
        
    Example:
        >>> nav_system = NavigationSystem()
        >>> nav_system.set_target(Position(10, 5))
        >>> nav_system.start_navigation()
    """
```

#### 2. API Documentation
Swagger/OpenAPI kullanarak API dokümantasyonu:
```yaml
# docs/api/swagger.yml
paths:
  /api/v1/robot/navigate:
    post:
      summary: Start robot navigation
      description: Command robot to navigate to specified position
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/NavigationRequest'
      responses:
        200:
          description: Navigation started successfully
        400:
          description: Invalid navigation parameters
```

#### 3. User Documentation
```markdown
# Robot Navigation Tutorial

## Overview
This tutorial will guide you through basic robot navigation using the web interface.

## Prerequisites
- Robot is powered on and connected
- Web interface is accessible
- User has operator permissions

## Step-by-Step Guide

### 1. Accessing the Interface
1. Open your web browser
2. Navigate to `http://robot-ip:8080`
3. Enter your credentials

### 2. Setting a Destination
1. Click on the map where you want the robot to go
2. Verify the path is clear
3. Click "Start Navigation"
```

### Dokümantasyon Araçları

#### Sphinx (Python)
```bash
# Setup
pip install sphinx sphinx-rtd-theme

# Generate docs
cd docs/
make html

# Auto-generate API docs
sphinx-apidoc -o source/ ../ot_bicme/
```

#### Doxygen (C++)
```cpp
/**
 * @brief Calculate shortest path between two points
 * @param start Starting position
 * @param goal Target position
 * @param obstacles List of obstacle positions
 * @return Vector of waypoints forming the path
 * @throws PathPlanningException if no path exists
 * 
 * This function uses A* algorithm to find the optimal path
 * while avoiding static obstacles.
 * 
 * @code
 * PathPlanner planner;
 * auto path = planner.calculatePath(start, goal, obstacles);
 * @endcode
 */
std::vector<Position> calculatePath(const Position& start,
                                   const Position& goal,
                                   const std::vector<Obstacle>& obstacles);
```

## 🐛 Issue Raporlama

### Bug Report Template

```markdown
**Bug Description**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
A clear description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
 - OS: [e.g. Ubuntu 20.04]
 - ROS Version: [e.g. Humble]
 - Robot Model: [e.g. OT-BiCME v2.1]
 - Software Version: [e.g. 2.1.0]

**Additional Context**
Add any other context about the problem here.

**Logs**
```
Paste relevant log files here
```

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
A clear description of alternative solutions you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.

**Implementation Suggestions**
If you have technical suggestions for implementation, please describe them here.

**Priority**
- [ ] Low
- [ ] Medium
- [ ] High
- [ ] Critical
```

### Issue Labels

#### Priority
- `priority/low`: Düşük öncelik
- `priority/medium`: Orta öncelik
- `priority/high`: Yüksek öncelik
- `priority/critical`: Kritik

#### Type
- `type/bug`: Hata raporu
- `type/feature`: Yeni özellik
- `type/enhancement`: İyileştirme
- `type/documentation`: Dokümantasyon

#### Difficulty
- `good first issue`: Yeni başlayanlar için
- `help wanted`: Yardım aranıyor
- `expert needed`: Uzman gerektiriyor

#### Component
- `component/navigation`: Navigasyon sistemi
- `component/ui`: Web arayüzü
- `component/sensors`: Sensör sistemleri
- `component/api`: API

## 🔄 Pull Request Süreci

### PR Checklist

#### Geliştirme
- [ ] Code review checklist tamamlandı
- [ ] Unit testler yazıldı ve geçiyor
- [ ] Integration testler geçiyor
- [ ] Linting kontrolü geçiyor
- [ ] Type checking geçiyor

#### Dokümantasyon
- [ ] Code comments eklendi
- [ ] API dokümantasyonu güncellendi
- [ ] User dokümantasyonu güncellendi
- [ ] CHANGELOG.md güncellendi

#### Testing
- [ ] Tüm mevcut testler geçiyor
- [ ] Yeni testler eklendi
- [ ] Performance regresyon yok
- [ ] Manual testing yapıldı

### PR Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Related Issues
Fixes #(issue number)

## Additional Notes
Any additional information for reviewers.
```

### Review Process

#### 1. Automated Checks
```yaml
# All checks must pass
- Build successful
- Tests passing
- Code coverage >= 80%
- Linting passed
- Security scan passed
```

#### 2. Human Review
- **Code quality**: Clean, readable, maintainable
- **Architecture**: Fits project architecture
- **Performance**: No performance regressions
- **Security**: No security vulnerabilities
- **Documentation**: Properly documented

#### 3. Approval Process
- 1 approval required for minor changes
- 2 approvals required for major changes
- Maintainer approval for breaking changes

## 👥 Topluluk

### İletişim Kanalları

#### Discord Server
```
OT-BiCME Community Discord
Invite Link: discord.gg/ot-bicme

Channels:
#general - Genel sohbet
#development - Geliştirme tartışmaları
#help - Yardım ve destek
#showcase - Proje vitrin
#announcements - Duyurular
```

#### Forum
```
GitHub Discussions
https://github.com/orcad-management/ot-bicme/discussions

Categories:
💡 Ideas - Yeni fikir önerileri
🙏 Q&A - Soru ve cevaplar
📢 Announcements - Resmi duyurular
💬 General - Genel tartışma
```

#### Social Media
- **Twitter**: @OTBiCME
- **LinkedIn**: OT-BiCME Project
- **YouTube**: OT-BiCME Tutorials

### Etkinlikler

#### Monthly Meetups
- **Zaman**: Her ayın ilk Cumartesi 14:00
- **Format**: Online/Hybrid
- **İçerik**: Technical talks, demos, Q&A

#### Quarterly Hackathons
- **Süre**: 48 saat
- **Ödüller**: GitHub sponsorships
- **Kategoriler**: AI/ML, Hardware, UI/UX

#### Annual Conference
- **OT-BiCME Con**: Yıllık büyük etkinlik
- **Speakers**: Industry experts
- **Workshops**: Hands-on sessions

### Recognition Program

#### Contributor Levels
```yaml
bronze:
  requirements: "5+ commits"
  benefits: ["Discord badge", "README mention"]

silver:
  requirements: "25+ commits or major feature"
  benefits: ["Profile highlight", "Early access"]

gold:
  requirements: "100+ commits or architecture contribution"
  benefits: ["Swag package", "Conference invitation"]

platinum:
  requirements: "Core maintainer status"
  benefits: ["All benefits", "Voting rights"]
```

#### Monthly Awards
- **🏆 Top Contributor**: En çok katkı yapan
- **🐛 Bug Hunter**: En çok bug bulan
- **📚 Documentation Hero**: Dokümantasyon kralı
- **🚀 Innovation Award**: En yaratıcı çözüm

### Mentorship Program

#### Mentees
- Yeni başlayanlar için rehberlik
- 1-on-1 mentoring sessions
- Project assignment
- Progress tracking

#### Mentors
- Experienced contributors
- Code review mentoring
- Career guidance
- Technical leadership

## 📄 Lisans

Bu proje MIT License altında lisanslanmıştır. Katkıda bulunarak:

1. Katkılarınızın aynı lisans altında olacağını kabul ediyorsunuz
2. Katkılarınızın orijinal çalışmanız olduğunu garanti ediyorsunuz
3. Katkılarınızı ticari kullanım dahil olmak üzere serbestçe kullanılabileceğini kabul ediyorsunuz

## 🙏 Teşekkürler

OT-BiCME projesine katkıda bulunduğun için teşekkürler! Her katkı, küçük de olsa, projeyi daha iyi hale getiriyor.

### Hall of Fame
Büyük katkılarıyla projeyi şekillendiren geliştiriciler:

- **Ahmet Tekniker** - Proje kurucusu ve baş mimarı
- **Ayşe Kodcu** - Web arayüzü lead developer
- **Mehmet Robotcu** - Hardware ve elektronik uzmanı
- **Fatma Algoritma** - AI/ML lead developer

### Special Thanks
- ROS Community - Robotik framework
- OpenCV Team - Computer vision library
- TensorFlow Team - Machine learning platform
- All our beta testers and early adopters

---

**İletişim Bilgileri:**
- **Email**: contribute@ot-bicme.com
- **Discord**: OT-BiCME Community
- **GitHub**: @orcad-management/ot-bicme

**Son Güncelleme**: 15 Ocak 2024
**Versiyon**: 1.0.0
