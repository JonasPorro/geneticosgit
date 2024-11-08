import math
import random
import pygame

from config import MAX_FOOD, NEW_FOOD_INTERVAL, SCREEN_SIZE
from creature import Creature
from food import Food
from ui import show_initial_screen, show_statistics, visualize_population
from utils import generate_tmp_csv, save_to_csv


dead_creatures = 0

def add_to_dead_creatures():
    global dead_creatures
    dead_creatures += 1

def create_population(size, params):
    """Crea una población inicial con los parámetros configurados."""
    population = []
    carnivores = 0
    for _ in range(size):
        csize = random.randint(params["size_min"], params["size_max"])
        speed = random.randint(params["speed_min"], params["speed_max"])
        if carnivores < size * params["carnivore_percentage"] / 100:
            is_carnivore = True
            carnivores += 1
        else:
            is_carnivore = False
        population.append(Creature(size=csize, speed=speed, is_carnivore=is_carnivore, personality=random.choice(["egoista", "conservadora", "neutral"])))
    return population

def create_food(amount=MAX_FOOD):
    """Crea una lista de comida aleatoria."""
    return [Food() for _ in range(amount)]

def add_food(food_sources, amount=2):
    """Agrega nueva comida a la lista."""
    food_sources.extend(create_food(amount))

def simulate_generation(population, food_sources):
    """Simula una generación completa."""
    global dead_creatures
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
                    dead_creatures += 1
                    break
        if creature.update(): # Si la criatura en cuestión murió (update retornó True) aumento el contador.
            dead_creatures += 1
        
def reproduce(population):
    """Selecciona criaturas para reproducirse y crear la próxima generación."""
    new_population = []
    for creature in population:
        if creature.alive and creature.can_reproduce():
            new_population.append(creature.reproduce())  # Hijo 1
            new_population.append(creature.reproduce())  # Hijo 2
    return new_population
            
def count_alive_carnivores(population):
    carnivores = 0
    for creature in population:
        if creature.is_carnivore and creature.alive:
            carnivores += 1
    return carnivores
            

def run_simulation():
    while(True):
        """Corre la simulación."""
        params, random_carnivore = show_initial_screen()
        POPULATION_SIZE = params["population_size"]
        screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
        pygame.display.set_caption("Simulación de Criaturas")

        population = create_population(POPULATION_SIZE, params)
        all_creatures = population.copy()  # Mantener un registro de todas las criaturas
        food_sources = create_food(params["initial_food"])
        clock = pygame.time.Clock()
        last_food_time = pygame.time.get_ticks()
        global dead_creatures
        dead_creatures = 0
        stop = False

        # Simular generación
        while (len(food_sources) > 0 or count_alive_carnivores(population) > 0) and len(population) > dead_creatures and not stop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    print("Simulación detenida por el usuario.")
                    stop = True

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

        if params["save_csv"]:
            save_to_csv(all_creatures)
        
        generate_tmp_csv(all_creatures)
        
        # Mostrar estadísticas de todas las criaturas
        show_statistics(screen, all_creatures)

if __name__ == "__main__":
    run_simulation()
