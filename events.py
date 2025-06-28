import numpy as np
import random
from constants import A, E_a, k_B, T, DIFFUSION_BARRIERS

def arrhenius(E_a, T, verbose=False):
    """Calculate rate using Arrhenius equation.
    Args:
        E_a (float): Activation energy (eV)
        T (float): Temperature (K)
    Returns:
        float: Rate in Hz
    """
    return A * np.exp(-E_a / (k_B * T))

def get_neighbors(position, lattice):
    """Get all periodic neighbors in 3D lattice.
    Args:
        position: (x,y,z) tuple
        lattice: 3D numpy array
    Returns:
        list: 6 neighbor positions (periodic)
    """
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
    """Calculate directional diffusion rate with boundary checks.
    Args:
        position: (x,y,z) of diffusing atom
        lattice: 3D numpy array
        direction: 'x', 'y', or 'z'
        temperature: Current temperature (K)
    Returns:
        float: Diffusion rate in Hz
    """
    # Validate direction input
    direction = direction.lower()
    if direction not in DIFFUSION_BARRIERS:
        raise ValueError(f"Invalid direction '{direction}'. Use 'x', 'y', or 'z'")

    E_a = DIFFUSION_BARRIERS[direction]
    x, y, z = position
    size = lattice.shape[0]  # Assumes cubic lattice
    
    # Get periodic neighbors in specified direction
    if direction == 'x':
        neighbors = [((x+1)%size, y, z), ((x-1)%size, y, z)]
    elif direction == 'y':
        neighbors = [(x, (y+1)%size, z), (x, (y-1)%size, z)]
    else:  # z-direction
        neighbors = [(x, y, (z+1)%size), (x, y, (z-1)%size)]
    
    # Count vacant neighbor sites
    vacant = sum(1 for n in neighbors if lattice[n] == 0)
    
    return arrhenius(E_a, temperature) * vacant

def get_group_rates(lattice, temperature):
    """Calculate total rates for all event groups (BKL optimization).
    Args:
        lattice: Current lattice state
        temperature: Simulation temperature (K)
    Returns:
        dict: {'diffusion': total_diff_rate, 'attachment': total_attach_rate}
    """
    rates = {'diffusion': 0.0, 'attachment': 0.0}
    
    # Diffusion group (mobile atoms)
    mobile_atoms = np.argwhere(lattice == 2)
    for pos in mobile_atoms:
        # Sum rates for all possible diffusion directions
        for direction in ['x', 'y', 'z']:
            rates['diffusion'] += get_diffusion_rate_anisotropic(
                tuple(pos), lattice, direction, temperature
            )
    
    # Attachment group (empty sites)
    empty_sites = np.argwhere(lattice == 0)
    rates['attachment'] = arrhenius(E_a, temperature) * len(empty_sites)
    
    return rates

if __name__ == "__main__":
    # Test anisotropic diffusion
    test_lattice = np.zeros((5,5,5), dtype=int)
    test_lattice[2,2,2] = 2  # Single atom at center
    
    print("=== Diffusion Rate Tests ===")
    print("X-rate:", get_diffusion_rate_anisotropic((2,2,2), test_lattice, 'x', 800))
    print("Y-rate:", get_diffusion_rate_anisotropic((2,2,2), test_lattice, 'y', 800))
    print("Z-rate:", get_diffusion_rate_anisotropic((2,2,2), test_lattice, 'z', 800))