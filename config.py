# config.py
import pygame

# Parámetros generales
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
font = pygame.font.Font(None, 25)  # Fuente para dibujar los números
font_large = pygame.font.Font(None, 30)  # Fuente más grande para las estadísticas
font_huge = pygame.font.Font(None, 50)  # Fuente más grande para las estadísticas
dead_creatures = 0