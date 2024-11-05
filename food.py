# food.py
import random
from config import GRID_SIZE

class Food:
    def __init__(self):
        self.x = random.randint(0, GRID_SIZE - 1)
        self.y = random.randint(0, GRID_SIZE - 1)