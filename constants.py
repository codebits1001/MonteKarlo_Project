
#Bulk diffusion, also known as lattice diffusion or volume diffusion, refers to the movement of atoms or molecules within the bulk of a solid material, 
# rather than just at the surface. It's a process where these particles move through the crystal lattice, either interstitially (between lattice sites) or substitutionally (replacing other atoms). 
# This movement is typically driven by concentration gradients and temperature, with higher temperatures generally leading to faster diffusion. 

#the diffusion barrier energy (or activation energy for diffusion) is the energy required for an atom or molecule to move from one location to another within a material.
#  It represents the energy needed to overcome the potential energy barrier between two stable positions, 
# such as moving from one lattice site to a neighboring vacancy. This energy barrier significantly influences the rate of diffusion, 
# with higher barriers leading to slower diffusion. 


#june 30
import numpy as np

# Simulation constants
SIMULATION_PARAMS = {
    'A': 1e10,               # Attempt frequency (Hz)
    'E_a': 1.0,              # Base diffusion barrier (eV)
    'k_B': 8.617e-5,         # Boltzmann constant (eV/K)
    'base_temp': 800,        # Default temperature (K)
    'critical_size': 4       # Minimum cluster size for nucleation
}

# State definitions
STATES = {
    'EMPTY': 0,
    'SUBSTRATE': 1,
    'MOBILE': 2,
    'STABLE': 3,
    'DEFECT': 4,
    'NUCLEATION': 5,
    'CLUSTER': 6
}

# Visualization settings
VISUALIZATION = {
    'colors': [
        '#FFFFFF',  # 0: Empty
        '#4E79A7',  # 1: Substrate
        '#E15759',  # 2: Mobile
        '#59A14F',  # 3: Stable
        '#F28E2B',  # 4: Defect
        '#EDC948',  # 5: Nucleation
        '#B07AA1'   # 6: Cluster
    ],
    'view_angle': (30, 45),
    'voxel_alpha': 0.85
}

# Diffusion parameters
DIFFUSION = {
    'x': 0.75,  # X-direction barrier (eV)
    'y': 0.95,  # Y-direction barrier (eV)
    'z': 1.2    # Z-direction barrier (eV)
}

# Nucleation parameters
NUCLEATION = {
    "T_m": 1700.0,      # Melting point (K)
    "L": 1.0e9,         # Latent heat (J/m³)
    "gamma": 0.3,        # Surface energy (J/m²)
    "theta_deg": 60.0,   # Contact angle (degrees)
    "A": 1e10            # Attempt frequency (Hz)
}

# 3D connectivity structure
STRUCTURE_3D = np.ones((3,3,3), dtype=bool)

# Grain boundary parameters
GRAIN_BOUNDARY = {
    'misorientation_threshold': 15.0,  # Degrees
    'energy_model': 'read-shockley',   # Energy calculation model
    'low_angle_cutoff': 15.0,         # Low-angle boundary cutoff (degrees)
    'high_angle_energy': 1.0,         # Energy for high-angle boundaries (J/m²)
    'sigma_3_energy': 0.3,            # Special Σ3 boundary energy (J/m²)
    'preferred_misorientation': 60.0   # Preferred misorientation for texture (degrees)
}