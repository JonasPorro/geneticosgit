import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import weibull_min
from config import DEATH_SCALE, DEATH_SHAPE
from mpl_toolkits.mplot3d import Axes3D  # Import necesario para gráficos 3D
from matplotlib import cm  # Colormaps para superficie
from scipy.ndimage import gaussian_filter

def analyze_creature_data(creatures):
    all_positions = []

    for creature in creatures:
        if creature.position_hist:
            all_positions.extend(creature.position_hist)

    if not all_positions:
        print("No hay posiciones para graficar.")
        return

    all_positions = np.array(all_positions)
    x_vals = all_positions[:, 0]
    y_vals = all_positions[:, 1]

    # Rango exacto de posiciones enteras
    x_min, x_max = x_vals.min(), x_vals.max()
    y_min, y_max = y_vals.min(), y_vals.max()

    x_bins = np.arange(x_min - 0.5, x_max + 1.5, 1)
    y_bins = np.arange(y_min - 0.5, y_max + 1.5, 1)

    # Crear figura y eje principal
    fig, ax = plt.subplots(figsize=(10, 8))

    # Histograma 2D
    h = ax.hist2d(
        x_vals, y_vals,
        bins=[x_bins, y_bins],
        cmap='hot',
        density=False,
        alpha=0.6
    )

    # Colorbar al lado derecho del gráfico
    cbar = fig.colorbar(h[3], ax=ax, pad=0.01)
    cbar.set_label('Cantidad de posiciones')

    # Dibujar trayectorias
    for i, creature in enumerate(creatures):
        positions = np.array(creature.position_hist)
        if len(positions) > 0:
            ax.plot(positions[:, 0], positions[:, 1], label=f'Creature {i+1}', linewidth=1)

    # Líneas de referencia
    ax.axvline(0, color='grey', lw=0.8)
    ax.axhline(0, color='grey', lw=0.8)
    ax.set_xlabel('X Position')
    ax.set_ylabel('Y Position')
    ax.set_title('Creature Trajectories with Heatmap (Discrete Grid)')
    ax.grid(True)

    # Leyenda afuera del gráfico, a la derecha del colorbar
    ax.legend().set_visible(False)

    plt.tight_layout()
    plt.savefig("creature_walk.png")
    plt.show()
    
    # Crear un nuevo gráfico 3D
    fig_3d = plt.figure(figsize=(10, 8))
    ax_3d = fig_3d.add_subplot(111, projection='3d')

    # Obtener el histograma de densidades como base para el gráfico 3D
    H, xedges, yedges = np.histogram2d(x_vals, y_vals, bins=[x_bins, y_bins])

    # Crear mallas para las coordenadas X e Y
    xcenters = (xedges[:-1] + xedges[1:]) / 2
    ycenters = (yedges[:-1] + yedges[1:]) / 2
    X, Y = np.meshgrid(xcenters, ycenters)

    # Transponer H para que se alinee con el sistema de coordenadas
    Z = H.T

    # Aplicar suavizado Gaussiano
    Z = gaussian_filter(Z, sigma=1.0)  # A mayor sigma, más suave

    # Gráfico de superficie
    surf = ax_3d.plot_surface(X, Y, Z, cmap=cm.hot, edgecolor='k', linewidth=0.5, alpha=0.9)

    # Ejes y título
    ax_3d.set_xlabel('X Position')
    ax_3d.set_ylabel('Y Position')
    ax_3d.set_zlabel('Density (Count)')
    ax_3d.set_title('3D Density Surface of Creature Positions')

    # Barra de color
    fig_3d.colorbar(surf, ax=ax_3d, shrink=0.5, aspect=10, pad=0.1)

    plt.tight_layout()
    plt.savefig("creature_density_3d.png")
    plt.show()

def analyze_food_supply(food_supply):
    # Calculate median and variance
    median_food = np.median(food_supply)
    variance_food = np.var(food_supply)

    # Plot histogram
    plt.figure(figsize=(10, 6))
    plt.hist(food_supply, bins=np.arange(min(food_supply)-0.5, max(food_supply)+1.5, 1), rwidth=0.8, alpha=0.7)
    plt.xlabel(f"Cantidad de comida\nMedia: {median_food:.2f}, Varianza: {variance_food:.2f}")
    plt.ylabel("Frecuencia")
    plt.title("Histograma de cantida de comida generada")
    plt.xticks(np.arange(min(food_supply), max(food_supply)+1, 1))
    plt.grid(axis='y', alpha=0.75)
    plt.savefig("food_histogram.png")
    plt.show()

    # Plot food amount vs time (position in the array)
    plt.figure(figsize=(10, 6))
    plt.plot(range(len(food_supply)), food_supply, marker='o', linestyle='-', color='skyblue')
    plt.xlabel("Tiempo")
    plt.ylabel("Cantidad de comida")
    plt.title("Comida generada en el timpo")
    plt.grid(True)
    plt.savefig("food_vs_time.png")
    plt.show()
    
def analyze_starvation(creatures):
    # Filtrar criaturas que murieron de hambre
    dead_from_hunger = [c.time_alive for c in creatures if not c.eaten and not c.alive]

    # Convertir a array
    lifespans = np.array(dead_from_hunger)

    # Calcular esperanza empírica
    empirical_mean = lifespans.mean()
    print(f"Esperanza de vida empírica (muertes por hambre): {empirical_mean:.2f} segundos")

    # Esperanza teórica de la Weibull
    from scipy.special import gamma
    theoretical_mean = DEATH_SCALE * gamma(1 + 1/DEATH_SHAPE)
    print(f"Esperanza de vida teórica (Weibull): {theoretical_mean:.2f} segundos")

    # Histograma de densidad
    count, bins, _ = plt.hist(
        lifespans,
        bins=30,
        density=True,
        alpha=0.6,
        color='orange',
        label='Datos simulados (inanición)'
    )

    # Curva teórica de la Weibull
    x = np.linspace(0, max(lifespans) * 1.1, 200)
    pdf_weibull = weibull_min.pdf(x, c=DEATH_SHAPE, scale=DEATH_SCALE)
    plt.plot(x, pdf_weibull, 'r-', lw=2, label='Weibull teórica')

    # Línea vertical para esperanza empírica
    plt.axvline(empirical_mean, color='blue', linestyle='--', label='Media empírica')

    # Línea vertical para esperanza teórica
    plt.axvline(theoretical_mean, color='red', linestyle=':', label='Media teórica')
    # Mostrar las medias como texto debajo del eje X
    ymin, ymax = plt.ylim()
    text_y = -0.05 * ymax  # posición debajo del eje X

    plt.text(empirical_mean, text_y, f'{empirical_mean:.2f}s', color='blue',
            ha='center', va='top', fontsize=10)
    plt.text(theoretical_mean, text_y, f'{theoretical_mean:.2f}s', color='red',
            ha='center', va='top', fontsize=10)
    
    # Gráficos y leyenda
    plt.title('Distribución de tiempos de vida (muertes por inanición)')
    plt.xlabel('Tiempo de vida (segundos)')
    plt.ylabel('Densidad de probabilidad')
    plt.legend()
    plt.grid(True)
    plt.show()