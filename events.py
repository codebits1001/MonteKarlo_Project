# events.py
import numpy as np
import random
from constants import A, E_a, k_B, T

# Define rate constant using Arrhenius equation
def arrhenius(E_a, T):
    return A * np.exp(-E_a / (k_B * T))

# Event: Atom attaches to an empty site
def atom_attachment_rate(atom_position, lattice, temperature):
    rate = arrhenius(E_a, temperature)
    if lattice[atom_position[0], atom_position[1], atom_position[2]] == 0:
        return rate
    else:
        return 0

# Event: Atom moves (diffusion)
def atom_diffusion_rate(atom_position, lattice, temperature):
    rate = arrhenius(E_a, temperature)
    neighbors = get_neighbors(atom_position, lattice)
    vacant_neighbors = sum([lattice[n[0], n[1], n[2]] == 0 for n in neighbors])
    return rate * vacant_neighbors

# Get neighboring sites
def get_neighbors(position, lattice):
    neighbors = []
    x, y, z = position
    neighbor_positions = [
        (x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z),
        (x, y, z + 1), (x, y, z - 1)
    ]
    for nx, ny, nz in neighbor_positions:
        if 0 <= nx < lattice.shape[0] and 0 <= ny < lattice.shape[1] and 0 <= nz < lattice.shape[2]:
            neighbors.append((nx, ny, nz))
    return neighbors
