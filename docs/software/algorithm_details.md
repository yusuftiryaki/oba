# 🧮 Algoritma Detayları

## 🧭 Kalman Filtresi Odometri

### Matematik Temelleri

#### Durum Vektörü Tanımı
Robot durumu 6 boyutlu vektör ile temsil edilir:

```
x = [x, y, θ, vx, vy, ω]ᵀ

Burada:
- x, y: Robot pozisyonu (metre)
- θ: Robot yönelimi (radyan)
- vx, vy: Doğrusal hızlar (m/s)
- ω: Açısal hız (rad/s)
```

#### Süreç Modeli (Motion Model)

```python
def motion_model(x, u, dt):
    """
    Robot motion model - bicycle model
    x: durum vektörü [x, y, θ, vx, vy, ω]
    u: kontrol girişi [v, ω] (linear vel, angular vel)
    dt: zaman adımı
    """
    x_new = np.zeros(6)
    
    # Pozisyon güncellemesi (kinematik model)
    x_new[0] = x[0] + x[3] * dt  # x = x + vx * dt
    x_new[1] = x[1] + x[4] * dt  # y = y + vy * dt
    x_new[2] = x[2] + x[5] * dt  # θ = θ + ω * dt
    
    # Hız güncellemesi (kontrol girişi)
    x_new[3] = u[0] * np.cos(x[2])  # vx = v * cos(θ)
    x_new[4] = u[0] * np.sin(x[2])  # vy = v * sin(θ)
    x_new[5] = u[1]                 # ω = ω_input
    
    return x_new

# Jacobian matrisi (F) - durum geçiş matrisi
F = np.array([
    [1, 0, 0, dt, 0,  0 ],
    [0, 1, 0, 0,  dt, 0 ],
    [0, 0, 1, 0,  0,  dt],
    [0, 0, 0, 0.9, 0, 0 ],  # hız sönümleme
    [0, 0, 0, 0, 0.9, 0 ],
    [0, 0, 0, 0,  0, 0.8]   # açısal hız sönümleme
])
```

#### Ölçüm Modeli (Sensor Model)

```python
def measurement_model(x, wheel_base):
    """
    Sensör ölçüm modeli
    Enkoder ve IMU verilerinden beklenen ölçümleri hesapla
    """
    # Tekerlek hızları (diferansiyel drive)
    v_left = x[3] - x[5] * wheel_base / 2
    v_right = x[3] + x[5] * wheel_base / 2
    
    # Beklenen ölçümler
    h = np.array([
        v_left,     # Sol tekerlek hızı
        v_right,    # Sağ tekerlek hızı
        x[2],       # IMU heading
        x[3],       # GPS velocity (varsa)
        x[4]        # GPS velocity (varsa)
    ])
    
    return h

# Ölçüm Jacobian'ı (H)
def measurement_jacobian(x, wheel_base):
    """Ölçüm modelinin Jacobian matrisi"""
    H = np.array([
        [0, 0, 0, 1, 0, -wheel_base/2],  # sol tekerlek
        [0, 0, 0, 1, 0, +wheel_base/2],  # sağ tekerlek  
        [0, 0, 1, 0, 0, 0],              # IMU heading
        [0, 0, 0, 1, 0, 0],              # GPS vx
        [0, 0, 0, 0, 1, 0]               # GPS vy
    ])
    return H
```

#### Gürültü Modelleri

```python
class NoiseParameters:
    """Kalman filtre gürültü parametreleri"""
    
    def __init__(self):
        # Süreç gürültüsü (Q) - model belirsizlikleri
        self.Q = np.diag([
            0.01,   # x pozisyon gürültüsü (m²)
            0.01,   # y pozisyon gürültüsü (m²)
            0.001,  # θ yönelim gürültüsü (rad²)
            0.1,    # vx hız gürültüsü (m²/s²)
            0.1,    # vy hız gürültüsü (m²/s²)
            0.05    # ω açısal hız gürültüsü (rad²/s²)
        ])
        
        # Ölçüm gürültüsü (R) - sensör belirsizlikleri
        self.R = np.diag([
            0.05,   # Sol enkoder gürültüsü (m²/s²)
            0.05,   # Sağ enkoder gürültüsü (m²/s²)
            0.01,   # IMU heading gürültüsü (rad²)
            0.2,    # GPS vx gürültüsü (m²/s²)
            0.2     # GPS vy gürültüsü (m²/s²)
        ])
        
        # Adaptif gürültü - duruma göre ayarla
        self.adaptive_noise = True
        
    def adapt_process_noise(self, velocity, angular_velocity):
        """Hıza göre süreç gürültüsünü ayarla"""
        if not self.adaptive_noise:
            return self.Q
            
        # Yüksek hızda daha fazla gürültü
        speed_factor = 1 + 0.5 * velocity
        turn_factor = 1 + 2.0 * abs(angular_velocity)
        
        Q_adaptive = self.Q.copy()
        Q_adaptive[0, 0] *= speed_factor  # x gürültüsü
        Q_adaptive[1, 1] *= speed_factor  # y gürültüsü
        Q_adaptive[2, 2] *= turn_factor   # θ gürültüsü
        
        return Q_adaptive
```

### Extended Kalman Filter (EKF) Implementasyonu

```python
class ExtendedKalmanFilter:
    """Extended Kalman Filter - nonlinear sistem için"""
    
    def __init__(self, initial_state, initial_covariance, noise_params):
        self.x = initial_state          # Durum vektörü
        self.P = initial_covariance     # Kovaryans matrisi
        self.noise = noise_params       # Gürültü parametreleri
        
        # Robot parametreleri
        self.wheel_base = 0.54  # metre
        self.wheel_radius = 0.1 # metre
        
    def predict(self, control_input, dt):
        """Tahmin adımı - robot hareket modeli"""
        
        # Kontrol girişi: [linear_velocity, angular_velocity]
        v, omega = control_input
        
        # Nonlinear motion model
        x_pred = np.zeros(6)
        x_pred[0] = self.x[0] + v * np.cos(self.x[2]) * dt  # x
        x_pred[1] = self.x[1] + v * np.sin(self.x[2]) * dt  # y
        x_pred[2] = self.x[2] + omega * dt                  # θ
        x_pred[3] = v * np.cos(self.x[2])                   # vx
        x_pred[4] = v * np.sin(self.x[2])                   # vy  
        x_pred[5] = omega                                   # ω
        
        # Jacobian matrisi hesaplama
        F = self._compute_motion_jacobian(v, omega, dt)
        
        # Kovaryans tahmini
        Q = self.noise.adapt_process_noise(v, abs(omega))
        P_pred = F @ self.P @ F.T + Q
        
        # Durumu güncelle
        self.x = x_pred
        self.P = P_pred
        
    def update(self, measurements, measurement_types):
        """Güncelleme adımı - sensör fusion"""
        
        if len(measurements) == 0:
            return
            
        # Beklenen ölçümleri hesapla
        h_expected = self._measurement_function(measurement_types)
        
        # Ölçüm Jacobian'ı
        H = self._compute_measurement_jacobian(measurement_types)
        
        # Ölçüm gürültüsü matrisini oluştur
        R = self._build_measurement_noise(measurement_types)
        
        # Innovation (ölçüm farkı)
        y = measurements - h_expected
        
        # Açı farkını [-π, π] aralığına getir
        for i, mtype in enumerate(measurement_types):
            if mtype == 'heading':
                y[i] = np.arctan2(np.sin(y[i]), np.cos(y[i]))
        
        # Innovation covariance
        S = H @ self.P @ H.T + R
        
        # Kalman gain
        K = self.P @ H.T @ np.linalg.inv(S)
        
        # Durum güncellemesi
        self.x = self.x + K @ y
        
        # Kovaryans güncellemesi (Joseph form - numerically stable)
        I = np.eye(len(self.x))
        IKH = I - K @ H
        self.P = IKH @ self.P @ IKH.T + K @ R @ K.T
        
        # Heading açısını normalize et
        self.x[2] = np.arctan2(np.sin(self.x[2]), np.cos(self.x[2]))
        
    def _compute_motion_jacobian(self, v, omega, dt):
        """Motion model Jacobian matrisi"""
        theta = self.x[2]
        
        F = np.array([
            [1, 0, -v*np.sin(theta)*dt, np.cos(theta)*dt, 0, 0],
            [0, 1,  v*np.cos(theta)*dt, np.sin(theta)*dt, 0, 0],
            [0, 0,  1,                  0,                0, dt],
            [0, 0, -v*np.sin(theta),    0.9,              0, 0],
            [0, 0,  v*np.cos(theta),    0,                0.9, 0],
            [0, 0,  0,                  0,                0, 0.8]
        ])
        
        return F
        
    def _measurement_function(self, measurement_types):
        """Beklenen ölçümleri hesapla"""
        h = []
        
        for mtype in measurement_types:
            if mtype == 'encoder_left':
                wheel_vel = self.x[3] - self.x[5] * self.wheel_base / 2
                h.append(wheel_vel)
            elif mtype == 'encoder_right':
                wheel_vel = self.x[3] + self.x[5] * self.wheel_base / 2
                h.append(wheel_vel)
            elif mtype == 'heading':
                h.append(self.x[2])
            elif mtype == 'gps_vx':
                h.append(self.x[3])
            elif mtype == 'gps_vy':
                h.append(self.x[4])
                
        return np.array(h)
```

## 🗺️ Path Planning Algoritmaları

### A* Algoritması - Grid Tabanlı

```python
import heapq
import numpy as np
from typing import List, Tuple, Optional

class AStarPlanner:
    """A* path planning algoritması"""
    
    def __init__(self, grid_map: np.ndarray, resolution: float = 0.1):
        self.grid_map = grid_map  # 0: serbest, 1: engel
        self.resolution = resolution
        self.height, self.width = grid_map.shape
        
        # 8-yönlü hareket (diyagonal dahil)
        self.motions = [
            (-1, -1, np.sqrt(2)), (-1, 0, 1), (-1, 1, np.sqrt(2)),
            (0, -1, 1),                        (0, 1, 1),
            (1, -1, np.sqrt(2)),  (1, 0, 1),  (1, 1, np.sqrt(2))
        ]
        
    def plan(self, start: Tuple[float, float], 
             goal: Tuple[float, float]) -> Optional[List[Tuple[float, float]]]:
        """A* path planning"""
        
        # Koordinatları grid indekslerine çevir
        start_idx = self._world_to_grid(start)
        goal_idx = self._world_to_grid(goal)
        
        # Grid sınırları kontrolü
        if not self._is_valid_cell(start_idx) or not self._is_valid_cell(goal_idx):
            return None
            
        # A* algoritması
        open_set = []
        heapq.heappush(open_set, (0, start_idx))
        
        came_from = {}
        g_score = {start_idx: 0}
        f_score = {start_idx: self._heuristic(start_idx, goal_idx)}
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            
            if current == goal_idx:
                # Yolu reconstruct et
                path = self._reconstruct_path(came_from, current)
                # Grid koordinatlarını world koordinatlarına çevir
                world_path = [self._grid_to_world(p) for p in path]
                return world_path
                
            for dx, dy, cost in self.motions:
                neighbor = (current[0] + dx, current[1] + dy)
                
                if not self._is_valid_cell(neighbor):
                    continue
                    
                tentative_g = g_score[current] + cost
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self._heuristic(neighbor, goal_idx)
                    
                    if neighbor not in [item[1] for item in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
                        
        return None  # Yol bulunamadı
        
    def _heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """Heuristic function - Euclidean distance"""
        return np.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)
        
    def _is_valid_cell(self, cell: Tuple[int, int]) -> bool:
        """Grid hücresinin geçerli olup olmadığını kontrol et"""
        x, y = cell
        return (0 <= x < self.height and 0 <= y < self.width and 
                self.grid_map[x, y] == 0)
                
    def _world_to_grid(self, world_pos: Tuple[float, float]) -> Tuple[int, int]:
        """World koordinatlarını grid indeksine çevir"""
        x, y = world_pos
        grid_x = int(x / self.resolution)
        grid_y = int(y / self.resolution)
        return (grid_x, grid_y)
        
    def _grid_to_world(self, grid_pos: Tuple[int, int]) -> Tuple[float, float]:
        """Grid indeksini world koordinatlarına çevir"""
        x, y = grid_pos
        world_x = x * self.resolution
        world_y = y * self.resolution
        return (world_x, world_y)
        
    def _reconstruct_path(self, came_from: dict, current: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Yolu reconstruct et"""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return path[::-1]  # Ters çevir
```

### RRT* Algoritması - Probabilistic Planning

```python
import random
import numpy as np
from typing import List, Tuple, Optional

class RRTNode:
    """RRT ağaç düğümü"""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.parent: Optional['RRTNode'] = None
        self.cost = 0.0

class RRTStarPlanner:
    """RRT* path planning algoritması"""
    
    def __init__(self, grid_map: np.ndarray, resolution: float = 0.1):
        self.grid_map = grid_map
        self.resolution = resolution
        self.height, self.width = grid_map.shape
        
        # RRT* parametreleri
        self.max_iter = 2000
        self.step_size = 0.5  # metre
        self.goal_tolerance = 0.3  # metre
        self.rewire_radius = 1.0  # metre
        
    def plan(self, start: Tuple[float, float], 
             goal: Tuple[float, float]) -> Optional[List[Tuple[float, float]]]:
        """RRT* path planning"""
        
        # Başlangıç düğümü
        start_node = RRTNode(start[0], start[1])
        goal_node = RRTNode(goal[0], goal[1])
        
        # Ağaç listesi
        nodes = [start_node]
        
        for i in range(self.max_iter):
            # Random sample
            if random.random() < 0.1:  # %10 ihtimalle goal'u sample et
                rand_point = (goal[0], goal[1])
            else:
                rand_point = self._sample_random_point()
                
            # En yakın düğümü bul
            nearest_node = self._find_nearest_node(nodes, rand_point)
            
            # Yeni düğüm oluştur
            new_node = self._steer(nearest_node, rand_point)
            
            # Collision check
            if self._is_collision_free(nearest_node, new_node):
                # Near nodes bul (rewiring için)
                near_nodes = self._find_near_nodes(nodes, new_node)
                
                # En iyi parent'ı bul
                best_parent = self._choose_parent(near_nodes, new_node)
                if best_parent:
                    new_node.parent = best_parent
                    new_node.cost = best_parent.cost + self._distance(best_parent, new_node)
                    nodes.append(new_node)
                    
                    # Rewiring
                    self._rewire(nodes, new_node, near_nodes)
                    
                    # Goal'a ulaştık mı kontrol et
                    if self._distance(new_node, goal_node) < self.goal_tolerance:
                        goal_node.parent = new_node
                        goal_node.cost = new_node.cost + self._distance(new_node, goal_node)
                        return self._extract_path(goal_node)
                        
        return None  # Yol bulunamadı
        
    def _sample_random_point(self) -> Tuple[float, float]:
        """Random nokta örnekle"""
        x = random.uniform(0, self.width * self.resolution)
        y = random.uniform(0, self.height * self.resolution)
        return (x, y)
        
    def _find_nearest_node(self, nodes: List[RRTNode], 
                          point: Tuple[float, float]) -> RRTNode:
        """En yakın düğümü bul"""
        min_dist = float('inf')
        nearest_node = None
        
        for node in nodes:
            dist = np.sqrt((node.x - point[0])**2 + (node.y - point[1])**2)
            if dist < min_dist:
                min_dist = dist
                nearest_node = node
                
        return nearest_node
        
    def _steer(self, from_node: RRTNode, to_point: Tuple[float, float]) -> RRTNode:
        """Belirli adım boyutu ile yeni düğüm oluştur"""
        dist = np.sqrt((to_point[0] - from_node.x)**2 + (to_point[1] - from_node.y)**2)
        
        if dist <= self.step_size:
            new_node = RRTNode(to_point[0], to_point[1])
        else:
            # Step size kadar ilerle
            angle = np.arctan2(to_point[1] - from_node.y, to_point[0] - from_node.x)
            new_x = from_node.x + self.step_size * np.cos(angle)
            new_y = from_node.y + self.step_size * np.sin(angle)
            new_node = RRTNode(new_x, new_y)
            
        return new_node
        
    def _is_collision_free(self, node1: RRTNode, node2: RRTNode) -> bool:
        """İki düğüm arasında çarpışma var mı kontrol et"""
        # Line sampling ile collision check
        dist = self._distance(node1, node2)
        num_samples = int(dist / (self.resolution * 0.5))
        
        for i in range(num_samples + 1):
            t = i / max(num_samples, 1)
            x = node1.x + t * (node2.x - node1.x)
            y = node1.y + t * (node2.y - node1.y)
            
            # Grid koordinatlarına çevir
            grid_x = int(x / self.resolution)
            grid_y = int(y / self.resolution)
            
            # Sınır kontrolü
            if (grid_x < 0 or grid_x >= self.height or 
                grid_y < 0 or grid_y >= self.width):
                return False
                
            # Engel kontrolü
            if self.grid_map[grid_x, grid_y] == 1:
                return False
                
        return True
        
    def _find_near_nodes(self, nodes: List[RRTNode], 
                        new_node: RRTNode) -> List[RRTNode]:
        """Yakın düğümleri bul (rewiring için)"""
        near_nodes = []
        for node in nodes:
            if self._distance(node, new_node) < self.rewire_radius:
                near_nodes.append(node)
        return near_nodes
        
    def _choose_parent(self, near_nodes: List[RRTNode], 
                      new_node: RRTNode) -> Optional[RRTNode]:
        """En iyi parent'ı seç (minimum cost)"""
        if not near_nodes:
            return None
            
        best_parent = None
        min_cost = float('inf')
        
        for node in near_nodes:
            if self._is_collision_free(node, new_node):
                cost = node.cost + self._distance(node, new_node)
                if cost < min_cost:
                    min_cost = cost
                    best_parent = node
                    
        return best_parent
        
    def _rewire(self, nodes: List[RRTNode], new_node: RRTNode, 
               near_nodes: List[RRTNode]):
        """Near nodes'ları rewire et"""
        for node in near_nodes:
            if node != new_node.parent:
                new_cost = new_node.cost + self._distance(new_node, node)
                if (new_cost < node.cost and 
                    self._is_collision_free(new_node, node)):
                    node.parent = new_node
                    node.cost = new_cost
                    
    def _distance(self, node1: RRTNode, node2: RRTNode) -> float:
        """İki düğüm arasındaki mesafe"""
        return np.sqrt((node1.x - node2.x)**2 + (node1.y - node2.y)**2)
        
    def _extract_path(self, goal_node: RRTNode) -> List[Tuple[float, float]]:
        """Yolu çıkar"""
        path = []
        current = goal_node
        
        while current is not None:
            path.append((current.x, current.y))
            current = current.parent
            
        return path[::-1]  # Ters çevir
```

## 🌾 Coverage Path Planning - Alan Kaplama

```python
class BoustrophedonPlanner:
    """Boustrophedon (zigzag) pattern ile alan kaplama"""
    
    def __init__(self, field_boundary: List[Tuple[float, float]], 
                 tool_width: float = 0.5):
        self.boundary = field_boundary
        self.tool_width = tool_width
        self.overlap = 0.1  # %10 overlap
        
    def generate_coverage_path(self) -> List[Tuple[float, float]]:
        """Alan kaplama yolu oluştur"""
        
        # Alanın bounding box'ını bul
        min_x = min(p[0] for p in self.boundary)
        max_x = max(p[0] for p in self.boundary)
        min_y = min(p[1] for p in self.boundary)
        max_y = max(p[1] for p in self.boundary)
        
        # Çalışma genişliği (overlap ile)
        working_width = self.tool_width * (1 - self.overlap)
        
        # Yatay şeritler oluştur
        path = []
        y = min_y
        direction = 1  # 1: sağa, -1: sola
        
        while y <= max_y:
            # Bu y seviyesinde alanın kesişimini bul
            intersections = self._find_line_intersections(y)
            
            if len(intersections) >= 2:
                # Intersection'ları sırala
                intersections.sort()
                
                # Çalışma alanını belirle (en dış intersection'lar)
                start_x = intersections[0]
                end_x = intersections[-1]
                
                if direction == 1:  # Sağa git
                    path.append((start_x, y))
                    path.append((end_x, y))
                else:  # Sola git
                    path.append((end_x, y))
                    path.append((start_x, y))
                    
                direction *= -1  # Yönü değiştir
                
            y += working_width
            
        return path
        
    def _find_line_intersections(self, y: float) -> List[float]:
        """Y seviyesinde polygon ile kesişimleri bul"""
        intersections = []
        
        for i in range(len(self.boundary)):
            p1 = self.boundary[i]
            p2 = self.boundary[(i + 1) % len(self.boundary)]
            
            # Yatay çizgi kesişimi
            if p1[1] <= y <= p2[1] or p2[1] <= y <= p1[1]:
                if p1[1] != p2[1]:  # Dikey çizgi değil
                    # Kesişim x koordinatı
                    t = (y - p1[1]) / (p2[1] - p1[1])
                    x = p1[0] + t * (p2[0] - p1[0])
                    intersections.append(x)
                    
        return intersections

# Spiral pattern alternatifi
class SpiralPlanner:
    """Spiral pattern ile alan kaplama"""
    
    def __init__(self, center: Tuple[float, float], 
                 max_radius: float, tool_width: float = 0.5):
        self.center = center
        self.max_radius = max_radius
        self.tool_width = tool_width
        
    def generate_spiral_path(self) -> List[Tuple[float, float]]:
        """Spiral yol oluştur"""
        path = []
        
        # Spiral parametreleri
        a = self.tool_width / (2 * np.pi)  # Spiral tightness
        theta = 0
        
        while True:
            # Polar koordinatlardan Cartesian'a
            r = a * theta
            
            if r > self.max_radius:
                break
                
            x = self.center[0] + r * np.cos(theta)
            y = self.center[1] + r * np.sin(theta)
            
            path.append((x, y))
            
            # Açıyı artır
            theta += 0.1  # radyan
            
        return path
```

---

**🎯 Hacı Abi Notu:** Algoritmalar robotun zekası gibi, iyi ayarlamazsan robot kafasını kaşır! Kalman filtre parametrelerini dikkatli ayarla, gürültü modelini gerçeğe yakın tut. Path planning'de A* hızlı ama grid'e bağımlı, RRT* daha esnek ama yavaş. Coverage planning'de overlap'i unutma, yoksa otları kaçırırsın! Test verisiyle algoritmaları validate et, simülasyonda çalışan gerçekte çalışmayabilir! 🤖🧮
