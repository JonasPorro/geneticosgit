import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

class MonteCarloCreatureSimulation:
    def __init__(self, data_path='creatures.csv'):
        """Initialize with path to your simulation data CSV"""
        self.df = pd.read_csv(data_path)
        self.param_distributions = None
        self.simulation_results = None
        
    def analyze_data(self):
        """Analyze parameter distributions from historical data"""
        # Extract generation from ID
        self.df['generation'] = self.df['id'].str.split('_').str[0].astype(int)
        
        # Fit probability distributions to each parameter
        self.param_distributions = {
            'size': stats.lognorm.fit(self.df['size']),
            'speed': stats.norm.fit(self.df['speed']),
            'time_alive': stats.weibull_min.fit(self.df['time_alive'].dropna()),
            'reproductions': (self.df['reproductions'].mean(),),
            'carnivore_prob': self.df['is_carnivore'].mean(),
            'personality': {
                'egoista': (self.df['personality'] == 'egoista').mean(),
                'conservadora': (self.df['personality'] == 'conservadora').mean(),
                'neutral': (self.df['personality'] == 'neutral').mean()
            }
        }
        
    def simulate_creature_lineage(self, generations=10):
        """Simulate a single creature lineage through generations"""
        if self.param_distributions is None:
            self.analyze_data()
            
        lineage = []
        current_gen = 1
        
        # Create ancestor
        ancestor = {
            'size': max(5, stats.lognorm.rvs(*self.param_distributions['size'])),
            'speed': max(0.1, stats.norm.rvs(*self.param_distributions['speed'])),
            'is_carnivore': np.random.random() < self.param_distributions['carnivore_prob'],
            'personality': np.random.choice(
                ['egoista', 'conservadora', 'neutral'],
                p=list(self.param_distributions['personality'].values())
            ),
            'generation': current_gen
        }
        lineage.append(ancestor)
        
        while current_gen < generations:
            parent = lineage[-1]
            
            # Reproduction probability based on traits
            base_rate = 0.3
            repro_prob = min(0.9, base_rate + 
                           (parent['speed'] * 0.05) - 
                           (parent['size'] * 0.01))
            
            if np.random.random() < repro_prob:
                current_gen += 1
                child = {
                    'size': max(5, min(100, parent['size'] * np.random.normal(1, 0.1))),
                    'speed': max(0.1, parent['speed'] * np.random.normal(1, 0.1)),
                    'is_carnivore': parent['is_carnivore'] if np.random.random() < 0.9 
                                  else not parent['is_carnivore'],
                    'personality': parent['personality'] if np.random.random() < 0.8 
                                 else np.random.choice(
                                     ['egoista', 'conservadora', 'neutral'],
                                     p=list(self.param_distributions['personality'].values())
                                 ),
                    'generation': current_gen
                }
                lineage.append(child)
            else:
                break
                
        # Calculate lifespan for each generation
        for creature in lineage:
            creature['lifespan'] = stats.weibull_min.rvs(*self.param_distributions['time_alive'])
            
        return lineage
    
    def run_simulation(self, n_simulations=1000, max_generations=15):
        """Run full Monte Carlo simulation"""
        results = []
        
        for _ in range(n_simulations):
            lineage = self.simulate_creature_lineage(max_generations)
            if lineage:
                results.append({
                    'generations': len(lineage),
                    'final_size': lineage[-1]['size'],
                    'final_speed': lineage[-1]['speed'],
                    'final_carnivore': lineage[-1]['is_carnivore'],
                    'final_personality': lineage[-1]['personality'],
                    'max_size': max(c['size'] for c in lineage),
                    'total_lifespan': sum(c['lifespan'] for c in lineage),
                    'avg_reproductions': np.mean([np.random.poisson(self.param_distributions['reproductions'][0]) 
                                               for _ in lineage])
                })
        
        self.simulation_results = pd.DataFrame(results)
        return self.simulation_results
    
    def visualize_results(self):
        """Generate comprehensive visualizations"""
        if self.simulation_results is None:
            print("Run simulation first using run_simulation()")
            return
            
        plt.figure(figsize=(18, 12))
        sns.set_style('whitegrid')
        
        # 1. Lineage Longevity
        plt.subplot(2, 2, 1)
        sns.histplot(data=self.simulation_results, x='generations', bins=20, kde=True)
        plt.title('Distribution of Lineage Longevity')
        plt.xlabel('Generations Survived')
        
        # 2. Trait Evolution
        plt.subplot(2, 2, 2)
        sns.scatterplot(data=self.simulation_results, x='final_size', y='final_speed',
                       hue='generations', palette='viridis', size='generations')
        plt.title('Final Creature Traits by Generation')
        plt.xlabel('Size')
        plt.ylabel('Speed')
        
        # 3. Survival Analysis
        plt.subplot(2, 2, 3)
        sns.boxplot(data=self.simulation_results, x='final_personality', y='total_lifespan',
                   hue='final_carnivore')
        plt.title('Lifespan by Personality and Diet')
        plt.xlabel('Personality')
        plt.ylabel('Total Lineage Lifespan')
        
        # 4. Trait Correlation
        plt.subplot(2, 2, 4)
        sns.heatmap(self.simulation_results[['final_size', 'final_speed', 'generations', 
                                          'total_lifespan']].corr(),
                   annot=True, cmap='coolwarm', vmin=-1, vmax=1)
        plt.title('Trait Correlation Matrix')
        
        plt.tight_layout()
        plt.savefig('monte_carlo_results.png', dpi=300)
        plt.show()
        
        # Print summary statistics
        print("\nSimulation Summary Statistics:")
        print(f"Average generations: {self.simulation_results['generations'].mean():.1f}")
        print(f"Max generations: {self.simulation_results['generations'].max()}")
        print(f"Carnivore prevalence: {self.simulation_results['final_carnivore'].mean():.1%}")
        print("\nTop Personality Traits:")
        print(self.simulation_results['final_personality'].value_counts(normalize=True))


# Example Usage
if __name__ == "__main__":
    print("Running Monte Carlo Simulation...")
    
    # Initialize with your CSV path
    simulator = MonteCarloCreatureSimulation('creatures.csv')
    
    # Run simulation (1000 lineages, max 15 generations)
    results = simulator.run_simulation(n_simulations=1000, max_generations=15)
    
    # Generate visualizations
    simulator.visualize_results()
    
    # Save results to new CSV
    results.to_csv('monte_carlo_output.csv', index=False)
    print("Results saved to 'monte_carlo_output.csv'")