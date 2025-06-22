import matplotlib.pyplot as plt
import numpy as np

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
    ax.legend(
        loc='center left',
        bbox_to_anchor=(1.1, 0.5),
        borderaxespad=0,
        title='Criaturas'
    )

    plt.tight_layout()
    plt.show()
