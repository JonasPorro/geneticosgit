import math
import random
import pygame
import time
import csv
import webcolors

# Parámetros
GRID_SIZE = 20
MAX_FOOD = 20
TIME_TO_LIVE = 5  # Tiempo límite sin comer antes de morir
REPRODUCTION_THRESHOLD = 3
POPULATION_SIZE = 10
GENERATIONS = 10
CELL_SIZE = 50  # Tamaño de cada celda en la ventana gráfica
SCREEN_SIZE = GRID_SIZE * CELL_SIZE
NEW_FOOD_INTERVAL = 500  # 5000 ms = 5 segundos

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)  # Color para los caníbales

# Inicializar pygame
pygame.init()
font = pygame.font.Font(None, 30)  # Fuente para dibujar los números
font_large = pygame.font.Font(None, 36)  # Fuente más grande para las estadísticas
dead_creatures = 0

class Creature:
    unique_id = 0  # Variable de clase para asignar IDs únicos a las criaturas

    def __init__(self, parent_color=None, speed=None, size=None, is_carnivore=None):
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
        self.size = size if size is not None else random.randint(10, 40)  # Tamaño aleatorio entre 5 y 20
        self.speed = speed if speed is not None else 40 / self.size  # Velocidad inversamente proporcional al tamaño
        self.is_carnivore = is_carnivore if is_carnivore is not None else random.choice([True, False])
        self.target_x = self.x
        self.target_y = self.y

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
                nearest_prey = min(other_creatures, key=lambda c: math.sqrt((self.x - c.x) ** 2 + (self.y - c.y) ** 2))
                self.move_towards(nearest_prey.x, nearest_prey.y)
            else:
                self.move_randomly()
        else:
            # Si no es caníbal, verifica si hay caníbales cerca para huir de ellos
            nearby_carnivores = [c for c in population if c.is_carnivore and c.alive and c.parent_color != self.parent_color]
            if nearby_carnivores:
                nearest_carnivore = min(nearby_carnivores, key=lambda c: math.sqrt((self.x - c.x) ** 2 + (self.y - c.y) ** 2))
                distance_to_carnivore = math.sqrt((self.x - nearest_carnivore.x) ** 2 + (self.y - nearest_carnivore.y) ** 2)

                # Si el caníbal está lo suficientemente cerca, la criatura huye en dirección opuesta
                if distance_to_carnivore < 5:  # Ajusta este valor según el rango de detección
                    self.move_away_from(nearest_carnivore.x, nearest_carnivore.y)
                else:
                    # Si no hay un caníbal cerca, busca la comida más cercana
                    if food_sources:
                        nearest_food = min(food_sources, key=lambda f: math.sqrt((self.x - f.x) ** 2 + (self.y - f.y) ** 2))
                        self.move_towards(nearest_food.x, nearest_food.y)
                    else:
                        self.move_randomly()
            else:
                # Si no hay caníbales cerca, busca la comida más cercana
                if food_sources:
                    nearest_food = min(food_sources, key=lambda f: math.sqrt((self.x - f.x) ** 2 + (self.y - f.y) ** 2))
                    self.move_towards(nearest_food.x, nearest_food.y)
                else:
                    self.move_randomly()
                    
    def move_randomly(self):
        """Mueve la criatura de manera aleatoria."""
        self.x += random.choice([-1, 1]) * int(self.speed)
        self.y += random.choice([-1, 1]) * int(self.speed)
        self.x = max(0, min(self.x, GRID_SIZE - 1))
        self.y = max(0, min(self.y, GRID_SIZE - 1))
                        
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

        if distance > 0:
            self.x += int(self.speed * (direction_x / distance))
            self.y += int(self.speed * (direction_y / distance))
        self.x = max(0, min(self.x, GRID_SIZE - 1))
        self.y = max(0, min(self.y, GRID_SIZE - 1))

    def eat(self):
        """Acción de comer si encuentra comida o a una presa."""
        self.food_eaten += 1
        self.eat_time = time.time()

    def eat_prey(self, prey):
        """Acción de comer otra criatura si es caníbal."""
        self.food_eaten += 1
        self.eat_time = time.time()
        prey.alive = False
        prey.death_time = time.time()
        global dead_creatures
        dead_creatures += 1
        prey.time_alive = prey.death_time - prey.birth_time

    def can_reproduce(self):
        """Verifica si la criatura puede reproducirse."""
        return self.food_eaten >= REPRODUCTION_THRESHOLD

    def reproduce(self):
        """Marca una reproducción y devuelve una nueva criatura."""
        self.reproductions += 1
        self.food_eaten_total += self.food_eaten
        self.food_eaten = 0
        return Creature(self.parent_color, speed=self.speed, size=self.size, is_carnivore=self.is_carnivore)

    def update(self):
        """Verifica si la criatura sigue viva."""
        if time.time() - self.eat_time > TIME_TO_LIVE:
            self.alive = False
            self.death_time = time.time()
            global dead_creatures
            dead_creatures += 1
            self.time_alive = self.death_time - self.birth_time

class Food:
    def __init__(self):
        self.x = random.randint(0, GRID_SIZE - 1)
        self.y = random.randint(0, GRID_SIZE - 1)

def create_population(size):
    """Crea una población inicial."""
    return [Creature() for _ in range(size)]

def create_food(amount=MAX_FOOD):
    """Crea una lista de comida aleatoria."""
    return [Food() for _ in range(amount)]

def add_food(food_sources, amount=2):
    """Agrega nueva comida cada cierto intervalo."""
    food_sources.extend(create_food(amount))

def simulate_generation(population, food_sources):
    """Simula una generación completa."""
    for creature in population:
        if not creature.alive:
            continue
        creature.move(food_sources, population)
        for food in food_sources:
            direction_x = creature.x - food.x
            direction_y = creature.y - food.y
            distance = math.sqrt(direction_x ** 2 + direction_y ** 2)
            if not creature.is_carnivore and distance <= creature.size/15: #creature.x == food.x and creature.y == food.y:
                creature.eat()
                food_sources.remove(food)
                break
        for prey in population:
            if creature.is_carnivore and prey.alive and prey.parent_color != creature.parent_color:
                direction_x = creature.x - prey.x
                direction_y = creature.y - prey.y
                distance = math.sqrt(direction_x ** 2 + direction_y ** 2) 
                if creature.x == prey.x and distance <= creature.size/15: #creature.y == prey.y:
                    creature.eat_prey(prey)
                    break
        creature.update()
        
def reproduce(population):
    """Selecciona criaturas para reproducirse y crear la próxima generación."""
    new_population = []
    for creature in population:
        if creature.alive and creature.can_reproduce():
            new_population.append(creature.reproduce())  # Hijo 1
            new_population.append(creature.reproduce())  # Hijo 2
    return new_population

def visualize_population(screen, population, food_sources):
    """Visualiza la población y la comida en la ventana de pygame."""
    screen.fill(WHITE)

    # Dibujar comida (verde)
    for food in food_sources:
        pygame.draw.circle(screen, GREEN, (food.x * CELL_SIZE + CELL_SIZE // 2, food.y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)

    # Dibujar criaturas (en colores según el padre)
    for creature in population:
        if creature.alive:
            # Dibujar la criatura como un círculo con el tamaño de la criatura
            pygame.draw.circle(screen, creature.parent_color, 
                               (creature.x * CELL_SIZE + CELL_SIZE // 2, creature.y * CELL_SIZE + CELL_SIZE // 2), 
                               creature.size)
            # Dibujar el ID de la criatura sobre su cabeza
            id_text = font.render(str(creature.id) , True, RED if creature.is_carnivore else BLACK)
            screen.blit(id_text, (creature.x * CELL_SIZE, creature.y * CELL_SIZE))

    pygame.display.flip()

def show_statistics(screen, population):
    """Muestra las estadísticas de las criaturas en la pantalla final."""
    # Ordenar las estadísticas
    top_lived = sorted(population, key=lambda x: x.time_alive, reverse=True)[:3]
    top_eaten = sorted(population, key=lambda x: x.food_eaten_total, reverse=True)[:3]
    top_reproductions = sorted(population, key=lambda x: x.reproductions, reverse=True)[:3]
    top_families = []
    for creature in population:
        found = False
        for color in top_families:
            if color[0] == creature.parent_color:
                found = True
                
        if not found:
            occurences = 0
            for creature2 in population:
                if creature2.parent_color == creature.parent_color:
                    occurences += 1
            top_families.append((get_colour_name(creature.parent_color), occurences))
        
    top_families = sorted(top_families, key=lambda x:x[1], reverse=True)[:3]
    
    screen.fill(WHITE)

    # Títulos
    screen.blit(font_large.render("Top 3 Criaturas por Tiempo Vivido", True, BLACK), (50, 50))
    screen.blit(font_large.render("Top 3 Criaturas por Comidas", True, BLACK), (50, 200))
    screen.blit(font_large.render("Top 3 Criaturas por Reproducciones", True, BLACK), (50, 350))
    screen.blit(font_large.render("Top 3 Familias por tamaño", True, BLACK), (50, 500))

    # Top 3 por tiempo vivido
    for i, creature in enumerate(top_lived):
        text = f"ID {creature.id} - Vivido: {round(creature.time_alive, 2)}s - Vel: {round(creature.speed, 2)} - Tam: {creature.size} - Familia: {creature.parent_color} - carnivoro: {creature.is_carnivore}"
        screen.blit(font.render(text, True, creature.parent_color), (50, 100 + i * 30))

    # Top 3 por comidas
    for i, creature in enumerate(top_eaten):
        text = f"ID {creature.id} - Comidas: {creature.food_eaten_total} - Vel: {round(creature.speed, 2)} - Tam: {creature.size} - Familia: {creature.parent_color} - carnivoro: {creature.is_carnivore}"
        screen.blit(font.render(text, True, creature.parent_color), (50, 250 + i * 30))

    # Top 3 por reproducciones
    for i, creature in enumerate(top_reproductions):
        text = f"ID {creature.id} - Reproducciones: {creature.reproductions} - Vel: {round(creature.speed, 2)} - Tam: {creature.size} - Familia: {creature.parent_color} - carnivoro: {creature.is_carnivore}"
        screen.blit(font.render(text, True, creature.parent_color), (50, 400 + i * 30))

    # Top 3 familias
    for i, family in enumerate(top_families):
        text = f"Familia {family[0]} - Integrantes totales: {family[1]}"
        screen.blit(font.render(text, True, family[0]), (50, 550 + i * 30))

    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False


def save_to_csv(population, index, filename="creatures.csv"):
    """Guarda la información de todas las criaturas en un archivo CSV, agregando nuevas líneas con cada ejecución."""
    # Abrir el archivo en modo 'append' para agregar nuevas líneas en cada simulación.
    with open(filename, "a", newline="") as csvfile:
        fieldnames = ["id", "color", "size", "speed", "time_alive", "food_eaten_total", "reproductions", "is_carnivore"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Escribir el encabezado solo si el archivo está vacío
        csvfile.seek(0)
        if csvfile.tell() == 0:
            writer.writeheader()
        
        # Escribir la información de las criaturas
        for creature in population:
            writer.writerow({
                "id": str(index) +"_"+ str(creature.id),
                "color": get_colour_name(creature.parent_color),
                "size": creature.size,
                "speed": round(creature.speed, 2),
                "time_alive": round(creature.time_alive, 2),
                "food_eaten_total": creature.food_eaten_total,
                "reproductions": creature.reproductions,
                "is_carnivore": creature.is_carnivore
            })
            
def closest_colour(requested_colour):
    myColors = {
        "AliceBlue":"#F0F8FF",
        "AntiqueWhite":"#FAEBD7",
        "Aqua":"#00FFFF",
        "Aquamarine":"#7FFFD4",
        "Azure":"#F0FFFF",
        "Beige":"#F5F5DC",
        "Bisque":"#FFE4C4",
        "Black":"#000000",
        "BlanchedAlmond":"#FFEBCD",
        "Blue":"#0000FF",
        "BlueViolet":"#8A2BE2",
        "Brown":"#A52A2A",
        "BurlyWood":"#DEB887",
        "CadetBlue":"#5F9EA0",
        "Chartreuse":"#7FFF00",
        "Chocolate":"#D2691E",
        "Coral":"#FF7F50",
        "CornflowerBlue":"#6495ED",
        "Cornsilk":"#FFF8DC",
        "Crimson":"#DC143C",
        "Cyan":"#00FFFF",
        "DarkBlue":"#00008B",
        "DarkCyan":"#008B8B",
        "DarkGoldenRod":"#B8860B",
        "DarkGray":"#A9A9A9",
        "DarkGrey":"#A9A9A9",
        "DarkGreen":"#006400",
        "DarkKhaki":"#BDB76B",
        "DarkMagenta":"#8B008B",
        "DarkOliveGreen":"#556B2F",
        "DarkOrange":"#FF8C00",
        "DarkOrchid":"#9932CC",
        "DarkRed":"#8B0000",
        "DarkSalmon":"#E9967A",
        "DarkSeaGreen":"#8FBC8F",
        "DarkSlateBlue":"#483D8B",
        "DarkSlateGray":"#2F4F4F",
        "DarkSlateGrey":"#2F4F4F",
        "DarkTurquoise":"#00CED1",
        "DarkViolet":"#9400D3",
        "DeepPink":"#FF1493",
        "DeepSkyBlue":"#00BFFF",
        "DimGray":"#696969",
        "DimGrey":"#696969",
        "DodgerBlue":"#1E90FF",
        "FireBrick":"#B22222",
        "FloralWhite":"#FFFAF0",
        "ForestGreen":"#228B22",
        "Fuchsia":"#FF00FF",
        "Gainsboro":"#DCDCDC",
        "GhostWhite":"#F8F8FF",
        "Gold":"#FFD700",
        "GoldenRod":"#DAA520",
        "Gray":"#808080",
        "Grey":"#808080",
        "Green":"#008000",
        "GreenYellow":"#ADFF2F",
        "HoneyDew":"#F0FFF0",
        "HotPink":"#FF69B4",
        "IndianRed ":"#CD5C5C",
        "Indigo ":"#4B0082",
        "Ivory":"#FFFFF0",
        "Khaki":"#F0E68C",
        "Lavender":"#E6E6FA",
        "LavenderBlush":"#FFF0F5",
        "LawnGreen":"#7CFC00",
        "LemonChiffon":"#FFFACD",
        "LightBlue":"#ADD8E6",
        "LightCoral":"#F08080",
        "LightCyan":"#E0FFFF",
        "LightGoldenRodYellow":"#FAFAD2",
        "LightGray":"#D3D3D3",
        "LightGrey":"#D3D3D3",
        "LightGreen":"#90EE90",
        "LightPink":"#FFB6C1",
        "LightSalmon":"#FFA07A",
        "LightSeaGreen":"#20B2AA",
        "LightSkyBlue":"#87CEFA",
        "LightSlateGray":"#778899",
        "LightSlateGrey":"#778899",
        "LightSteelBlue":"#B0C4DE",
        "LightYellow":"#FFFFE0",
        "Lime":"#00FF00",
        "LimeGreen":"#32CD32",
        "Linen":"#FAF0E6",
        "Magenta":"#FF00FF",
        "Maroon":"#800000",
        "MediumAquaMarine":"#66CDAA",
        "MediumBlue":"#0000CD",
        "MediumOrchid":"#BA55D3",
        "MediumPurple":"#9370DB",
        "MediumSeaGreen":"#3CB371",
        "MediumSlateBlue":"#7B68EE",
        "MediumSpringGreen":"#00FA9A",
        "MediumTurquoise":"#48D1CC",
        "MediumVioletRed":"#C71585",
        "MidnightBlue":"#191970",
        "MintCream":"#F5FFFA",
        "MistyRose":"#FFE4E1",
        "Moccasin":"#FFE4B5",
        "NavajoWhite":"#FFDEAD",
        "Navy":"#000080",
        "OldLace":"#FDF5E6",
        "Olive":"#808000",
        "OliveDrab":"#6B8E23",
        "Orange":"#FFA500",
        "OrangeRed":"#FF4500",
        "Orchid":"#DA70D6",
        "PaleGoldenRod":"#EEE8AA",
        "PaleGreen":"#98FB98",
        "PaleTurquoise":"#AFEEEE",
        "PaleVioletRed":"#DB7093",
        "PapayaWhip":"#FFEFD5",
        "PeachPuff":"#FFDAB9",
        "Peru":"#CD853F",
        "Pink":"#FFC0CB",
        "Plum":"#DDA0DD",
        "PowderBlue":"#B0E0E6",
        "Purple":"#800080",
        "RebeccaPurple":"#663399",
        "Red":"#FF0000",
        "RosyBrown":"#BC8F8F",
        "RoyalBlue":"#041690",
        "SaddleBrown":"#8B4513",
        "Salmon":"#FA8072",
        "SandyBrown":"#F4A460",
        "SeaGreen":"#2E8B57",
        "SeaShell":"#FFF5EE",
        "Sienna":"#A0522D",
        "Silver":"#C0C0C0",
        "SkyBlue":"#87CEEB",
        "SlateBlue":"#6A5ACD",
        "SlateGray":"#708090",
        "SlateGrey":"#708090",
        "Snow":"#FFFAFA",
        "SpringGreen":"#00FF7F",
        "SteelBlue":"#4682B4",
        "Tan":"#D2B48C",
        "Teal":"#008080",
        "Thistle":"#D8BFD8",
        "Tomato":"#FF6347",
        "Turquoise":"#40E0D0",
        "Violet":"#EE82EE",
        "Wheat":"#F5DEB3",
        "White":"#FFFFFF",
        "WhiteSmoke":"#F5F5F5",
        "Yellow":"#FFFF00",
        "YellowGreen":"#9ACD32"
    }
    
    min_colours = {}
    for name, key in myColors.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

def get_colour_name(requested_colour):
    try:
        closest_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
    return closest_name

def run_simulation(index):
    """Corre la simulación por varias generaciones."""
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    pygame.display.set_caption("Simulación de Criaturas")

    population = create_population(POPULATION_SIZE)
    all_creatures = population.copy()  # Mantener un registro de todas las criaturas
    food_sources = create_food()
    clock = pygame.time.Clock()
    last_food_time = pygame.time.get_ticks()

    for generation in range(GENERATIONS):
        print(f"\nGeneración {generation + 1}")

        # Simular generación
        while len(food_sources) > 0 and len(population) > dead_creatures:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            if pygame.time.get_ticks() - last_food_time > NEW_FOOD_INTERVAL:
                add_food(food_sources, amount=2)
                last_food_time = pygame.time.get_ticks()

            simulate_generation(population, food_sources)
            visualize_population(screen, population, food_sources)
            clock.tick(2)

            # Agregar nuevas criaturas a `all_creatures`
            new_population = reproduce(population)
            all_creatures.extend(new_population)  # Agregar nuevas criaturas a la lista completa
            population.extend(new_population)

        if not population:
            print("¡Toda la población murió!")
            break

    #save_to_csv(all_creatures,index)
    # Mostrar estadísticas de todas las criaturas
    show_statistics(screen, all_creatures)
    pygame.quit()

if __name__ == "__main__":
    run_simulation(13)
