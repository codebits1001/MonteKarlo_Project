import numpy as np
import matplotlib.pyplot as plt
from constants import VISUALIZATION_SCALE, COLOR_MAP

def visualize_lattice(lattice, ax, viewpoint=(30, 45)):
    """3D visualization of lattice"""
    ax.clear()
    ax.set_box_aspect([1, 1, 1])
    ax.view_init(*viewpoint)
    
    # Set consistent limits
    size = lattice.shape[0]
    ax.set(xlim=(0, size), ylim=(0, size), zlim=(0, size),
           xlabel='X', ylabel='Y', zlabel='Z')

    # Plot occupied sites
    occupied = np.argwhere(lattice > 0)
    if len(occupied) > 0:
        colors = [COLOR_MAP[lattice[tuple(pos)]] for pos in occupied]
        x, y, z = occupied.T
        ax.scatter(x, y, z, c=colors, s=VISUALIZATION_SCALE,
                   alpha=0.8, edgecolors='k')

    # Title with stats
    coverage = 100 * len(occupied) / lattice.size
    ax.set_title(f"KMC Simulation | Coverage: {coverage:.1f}%")
    plt.draw()
    plt.pause(0.01)