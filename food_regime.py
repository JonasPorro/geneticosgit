import random
import numpy as np
from config import FOOD_REGIME_TRANSITIONS

class FoodRegime:
    ABUNDANT = 0
    SCARCE = 1
    
    def __init__(self):
        self.state = self.ABUNDANT
        self.transition_matrix = FOOD_REGIME_TRANSITIONS
    
    def update(self):
        if random.random() < self.transition_matrix[self.state][1 - self.state]:
            self.state = 1 - self.state
            
    def get_food_amount(self):
        # Returns number of new food items to add
        return np.random.poisson(lam=[5, 2][self.state])  # More food in abundant state