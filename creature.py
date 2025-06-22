# creature.py
import random
import time
import math
from config import GRID_SIZE, TIME_TO_LIVE, REPRODUCTION_THRESHOLD

class Creature:
    unique_id = 0  # Variable de clase para asignar IDs únicos a las criaturas

    def __init__(self, parent_color=None, speed=None, size=None, is_carnivore=None, personality = "neutral"):
        Creature.unique_id += 1
        self.id = Creature.unique_id
        self.energy = 100
        self.food_eaten = 0
        self.food_eaten_total = 0
        self.reproductions = 0
        self.birth_time = time.time()
        self.eat_time = time.time()
        self.death_time = None
        self.time_alive = 0
        self.alive = True
        self.x = random.randint(0, GRID_SIZE - 1)
        self.y = random.randint(0, GRID_SIZE - 1)
        self.parent_color = parent_color if parent_color else self.random_color()
        self.size = size if size is not None else random.randint(10, 35)  # Tamaño aleatorio entre 5 y 20
        self.speed = speed if speed is not None else 40 / self.size  # Velocidad inversamente proporcional al tamaño
        self.is_carnivore = is_carnivore if is_carnivore is not None else random.choice([True, False])
        self.target_x = self.x
        self.target_y = self.y
        self.personality = personality 
        self.position_hist = [(0,0)]

    def random_color(self):
        """Genera un color aleatorio para la criatura."""
        return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

    def move(self, food_sources, population):
        """Mueve la criatura hacia la comida más cercana o hacia otra criatura si es caníbal. Las presas huyen de los caníbales cercanos."""
        if not self.alive:
            return

        if self.is_carnivore:
            # Si es caníbal, busca la criatura más cercana que no sea de su familia
            other_creatures = [c for c in population if c.alive and c.parent_color != self.parent_color]
            if other_creatures:
                nearest_prey = min(other_creatures, key=lambda c: self._distance_to(c))
                if self.personality == "egoista" or (self.personality == "conservadora" and self._evaluate_resources(food_sources, population)) or (self.personality == "neutral" and random.choice([True,False])):
                    self.move_towards(nearest_prey.x, nearest_prey.y)
                else:
                    self.move_randomly()
            else:
                self.move_randomly()
        else:
            # Si no es caníbal, verifica si hay caníbales cerca para huir de ellos
            nearby_carnivores = [c for c in population if c.is_carnivore and c.alive and c.parent_color != self.parent_color]
            if nearby_carnivores:
                nearest_carnivore = min(nearby_carnivores, key=lambda c: self._distance_to(c))
                distance_to_carnivore = self._distance_to(nearest_carnivore)
                
                # Si el caníbal está lo suficientemente cerca, la criatura huye en dirección opuesta
                if distance_to_carnivore < 5:  # Ajusta este valor según el rango de detección
                    self.move_away_from(nearest_carnivore.x, nearest_carnivore.y)
                else:
                    # Si no hay un caníbal cerca, busca la comida más cercana
                    if food_sources:
                        if self.personality == "egoista" or (self.personality == "conservadora" and self._evaluate_resources(food_sources, population)) or (self.personality == "neutral" and random.choice([True,False])):
                            nearest_food = min(food_sources, key=lambda f: self._distance_to(f))
                            self.move_towards(nearest_food.x, nearest_food.y)
                        else:
                            self.move_randomly()
                    else:
                        self.move_randomly()
            else:
                # Si no hay caníbales cerca, busca la comida más cercana
                if food_sources:
                        if self.personality == "egoista" or (self.personality == "conservadora" and self._evaluate_resources(food_sources, population)) or (self.personality == "neutral" and random.choice([True,False])):
                            nearest_food = min(food_sources, key=lambda f: self._distance_to(f))
                            self.move_towards(nearest_food.x, nearest_food.y)
                        else:
                            self.move_randomly()
                else:
                    self.move_randomly()
                    
    def _evaluate_resources(self, food_sources, population):
        """Evalúa los recursos en el entorno considerando el tipo de criatura."""
        if not self.is_carnivore:
            # Herbívoro: cuenta comida y otros herbívoros cercanos
            nearby_food = len(food_sources)
            nearby_herbivores = sum(1 for creature in population if not creature.is_carnivore and creature.alive and creature.parent_color == self.parent_color)
            return nearby_food > nearby_herbivores
        else:
            # Carnívoro: cuenta presas (herbívoros) cercanos
            nearby_prey = sum(1 for creature in population if not creature.is_carnivore and creature.alive)
            return nearby_prey > 2  # Sigue cazando solo si hay más de dos presas
        
    def _distance_to(self, obj):
        """Calcula la distancia a otro objeto (alimento o criatura)."""
        return math.sqrt((self.x - obj.x) ** 2 + (self.y - obj.y) ** 2)
                
    def move_randomly(self):
        """Mueve la criatura de manera aleatoria."""
        random_x = random.choice([-1, 0, 1])
        random_y = random.choice([-1, 0, 1])
        self.x += random_x * int(self.speed)
        self.y += random_y * int(self.speed)
        self.x = max(0, min(self.x, GRID_SIZE - 1))
        self.y = max(0, min(self.y, GRID_SIZE - 1))
        last_hist = self.position_hist[-1]
        self.position_hist.append((last_hist[0] + random_x, last_hist[1] + random_y))
                        
    def move_away_from(self, threat_x, threat_y):
        """Mueve la criatura en dirección opuesta a una amenaza."""
        direction_x = self.x - threat_x
        direction_y = self.y - threat_y
        distance = math.sqrt(direction_x ** 2 + direction_y ** 2)

        if distance != 0:
            # Calcula la nueva posición alejándose de la amenaza
            self.x += int(self.speed * (direction_x / distance))
            self.y += int(self.speed * (direction_y / distance))

        # Asegurar que se mantenga dentro de los límites de la cuadrícula
        self.x = max(0, min(self.x, GRID_SIZE - 1))
        self.y = max(0, min(self.y, GRID_SIZE - 1))

    def move_towards(self, target_x, target_y):
        """Calcula el movimiento hacia un objetivo específico."""
        direction_x = target_x - self.x
        direction_y = target_y - self.y
        distance = math.sqrt(direction_x ** 2 + direction_y ** 2)
        
        if distance < self.speed:
            self.x = target_x
            self.y = target_y
        elif distance > 0:
            self.x += int(self.speed * (direction_x / distance))
            self.y += int(self.speed * (direction_y / distance))
            
        self.x = max(0, min(self.x, GRID_SIZE - 1))
        self.y = max(0, min(self.y, GRID_SIZE - 1))

    def eat(self):
        """Acción de comer si encuentra comida."""
        self.food_eaten += 1
        self.eat_time = time.time()

    def eat_prey(self, prey):
        """Acción de comer otra criatura si es caníbal."""
        self.food_eaten += 1
        self.eat_time = time.time()
        prey.alive = False
        prey.death_time = time.time()
        prey.time_alive = prey.death_time - prey.birth_time

    def can_reproduce(self):
        """Verifica si la criatura puede reproducirse."""
        return self.food_eaten >= REPRODUCTION_THRESHOLD

    def reproduce(self):
        """Marca una reproducción y devuelve una nueva criatura."""
        self.reproductions += 1
        self.food_eaten_total += self.food_eaten
        self.food_eaten = 0
        return Creature(self.parent_color, speed=self.speed, size=self.size, is_carnivore=self.is_carnivore, personality=self.personality)

    def update(self):
        """Verifica si la criatura sigue viva."""
        if time.time() - self.eat_time > TIME_TO_LIVE:
            self.alive = False
            self.death_time = time.time()
            self.time_alive = self.death_time - self.birth_time
            return True
        return False
