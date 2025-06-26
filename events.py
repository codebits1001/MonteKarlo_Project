'''import numpy as np
import random
from constants import A, E_a, k_B, T

def arrhenius(E_a, T, verbose=False):
    """Calculate rate using Arrhenius equation"""
    k = A * np.exp(-E_a / (k_B * T))
    if verbose:
        print(f"Rate at T={T} K: {k:.2e} 1/s")
    return k

def atom_attachment_rate(position, lattice, temperature):
    """Calculate attachment rate with boundary checks"""
    x, y, z = position
    if not (0 <= x < lattice.shape[0] and 
            0 <= y < lattice.shape[1] and 
            0 <= z < lattice.shape[2]):
        return 0
    return arrhenius(E_a, temperature) if lattice[position] == 0 else 0

def atom_diffusion_rate(position, lattice, temperature):
    """Calculate diffusion rate based on neighbors"""
    rate = arrhenius(E_a, temperature)
    neighbors = get_neighbors(position, lattice)
    vacant = sum(lattice[n] == 0 for n in neighbors)
    return rate * vacant

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

    '''

import numpy as np
import random
from constants import A, E_a, k_B, T  # Preserve your original imports

def arrhenius(E_a, T):
    """Your original rate calculation"""
    return A * np.exp(-E_a / (k_B * T))

def get_neighbors(position, lattice):
    """Your original neighbor function (unchanged)"""
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

# New additions for BKL optimization
def get_group_rates(lattice, temperature):
    """Calculate rates for all event groups"""
    rates = {
        'diffusion': 0.0,
        'attachment': 0.0
    }
    
    # Mobile atoms (diffusion)
    mobile_atoms = np.argwhere(lattice == 2)
    base_diffusion_rate = arrhenius(E_a, temperature)
    for pos in mobile_atoms:
        rates['diffusion'] += base_diffusion_rate * sum(
            1 for n in get_neighbors(pos, lattice) if lattice[n] == 0
        )
    
    # Empty sites (attachment)
    empty_sites = np.argwhere(lattice == 0)
    rates['attachment'] = arrhenius(E_a, temperature) * len(empty_sites)
    
    return rates