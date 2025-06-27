import numpy as np
import random
from constants import A, E_a, k_B, T, DIFFUSION_BARRIERS  # Added DIFFUSION_BARRIERS

def arrhenius(E_a, T, verbose=False):
    """Calculate rate using Arrhenius equation"""
    return A * np.exp(-E_a / (k_B * T))

def get_neighbors(position, lattice):
    """Get periodic neighbors in 3D lattice"""
    x, y, z = position
    shape = lattice.shape
    return [
        ((x+1)%shape[0], y, z),
        ((x-1)%shape[0], y, z),
        (x, (y+1)%shape[1], z),
        (x, (y-1)%shape[1], z),
        (x, y, (z+1)%shape[2]),
        (x, y, (z-1)%shape[2])
    ]

def get_diffusion_rate_anisotropic(position, lattice, direction, temperature):
    """Calculate directional diffusion rate with proper boundary checks"""
    E_a = DIFFUSION_BARRIERS[direction.lower()]
    x, y, z = position
    size = lattice.shape[0]  # Assuming cubic lattice
    
    # Get periodic neighbors
    if direction.lower() == 'x':
        neighbors = [
            ((x + 1) % size, y, z),
            ((x - 1) % size, y, z)
        ]
    else:  # y-direction
        neighbors = [
            (x, (y + 1) % size, z),
            (x, (y - 1) % size, z)
        ]
    
    vacant = sum(1 for n in neighbors if lattice[n] == 0)
    return arrhenius(E_a, temperature) * vacant


def atom_diffusion_rate(position, lattice, temperature):
    """Original isotropic version (maintains backward compatibility)"""
    return get_diffusion_rate_anisotropic(position, lattice, 'x', temperature)

def get_group_rates(lattice, temperature):
    """Calculate total rates for all event groups (BKL optimization)"""
    rates = {
        'diffusion': 0.0,
        'attachment': 0.0
    }
    
    # Diffusion group (mobile atoms)
    mobile_atoms = np.argwhere(lattice == 2)
    for pos in mobile_atoms:
        rates['diffusion'] += get_diffusion_rate_anisotropic(pos, lattice, 'x', temperature)  # Using x as default
    
    # Attachment group (empty sites)
    empty_sites = np.argwhere(lattice == 0)
    rates['attachment'] = arrhenius(E_a, temperature) * len(empty_sites)
    
    return rates

if __name__ == "__main__":
    # Test anisotropic diffusion
    test_lattice = np.zeros((5,5,5), dtype=int)
    test_lattice[2,2,2] = 2  # Single atom at center
    print("X-rate:", get_diffusion_rate_anisotropic((2,2,2), test_lattice, 'x', 800))
    print("Y-rate:", get_diffusion_rate_anisotropic((2,2,2), test_lattice, 'y', 800))