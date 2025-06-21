import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import weibull_min, kstest

def analyze_creature_data(creatures):
    """Generate stochastic analysis visualizations"""
    # 1. Survival Analysis
    survival_times = [c.time_alive for c in creatures if c.death_time]
    if survival_times:
        plt.figure()
        plt.hist(survival_times, bins=20, density=True, alpha=0.6, label='Data')
        
        # Fit Weibull distribution
        shape, loc, scale = weibull_min.fit(survival_times)
        x = np.linspace(min(survival_times), max(survival_times), 100)
        plt.plot(x, weibull_min.pdf(x, shape, loc, scale), 'r-', label='Weibull Fit')
        plt.title('Survival Time Distribution')
        plt.legend()
        plt.savefig('survival_analysis.png')
    
    # 2. Movement Analysis (for first creature)
    if creatures and creatures[0].movement_history:
        x, y, _ = zip(*creatures[0].movement_history)
        plt.figure()
        plt.plot(x, y, 'b-', alpha=0.5)
        plt.title('Creature Movement Path')
        plt.savefig('movement_path.png')
        
        # Calculate turning angles
        angles = []
        for i in range(1, len(x)-1):
            dx1, dy1 = x[i]-x[i-1], y[i]-y[i-1]
            dx2, dy2 = x[i+1]-x[i], y[i+1]-y[i]
            angle = np.arctan2(dy2, dx2) - np.arctan2(dy1, dx1)
            angles.append(angle % (2*np.pi))
        
        plt.figure()
        plt.hist(angles, bins=36)
        plt.title('Turning Angle Distribution')
        plt.savefig('turning_angles.png')