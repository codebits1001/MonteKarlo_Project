# Simulation constants
'''A = 1e12       # Attempt frequency (Hz)
E_a = 0.7      # Diffusion barrier (eV)
T = 800        # Temperature (K)
k_B = 8.617e-5 # Boltzmann constant (eV/K)

# Visualization settings
VISUALIZATION_SCALE = 50
COLOR_MAP = {
    0: 'white',  # Empty
    1: 'blue',   # Host atoms
    2: 'red',    # Reserved
    3: 'green'   # Reserved
}

# Simulation control
MAX_STEPS = 1000
TEMPERATURE = 800  # K

COLOR_MAP = {
    0: 'white',  # Empty
    1: 'gray',   # Substrate (fixed)
    2: 'blue',   # Mobile adatoms
    3: 'red'     # Defects/impurities
}

# In constants.py
EVENT_TYPES = {
    'diffusion': {
        'rate_function': 'atom_diffusion_rate',
        'allowed_types': [2]  # Only mobile atoms
    },
    'attachment': {
        'rate_function': 'atom_attachment_rate',
        'allowed_types': [0]  # Only empty sites
    },
    'desorption': {  # New event type
        'rate_function': 'atom_desorption_rate',
        'allowed_types': [2],
        'E_a': 1.2  # eV, example value
    }
}


'''
import numpy as np
# Simulation constants
A = 1e10  # More typical attempt frequency
E_a = 1.0  # Higher barrier for bulk diffusion
      # Base diffusion barrier (eV)
T = 800        # Temperature (K)
k_B = 8.617e-5 # Boltzmann constant (eV/K)


# Visualization settings
VISUALIZATION_SCALE = 50
COLOR_MAP = {
    0: 'white',  # Empty
    1: 'gray',   # Substrate (fixed)
    2: 'blue',   # Mobile adatoms
    3: 'red'     # Defects/impurities
}


# Add z-direction barrier and clarify comments
DIFFUSION_BARRIERS = {
    'x': 0.75,  # Low barrier for fast x-diffusion
    'y': 0.95,  # Higher barrier for y-diffusion
    'z': 1.2    # Highest barrier for z-diffusion (adjust as needed)
}

# Update event groups to include z-diffusion
EVENT_GROUPS = {
    'diffusion': {
        'rate_constant': A * np.exp(-E_a / (k_B * T)),
        'atom_types': [2],  # Mobile atoms
        'directions': ['x', 'y', 'z']  # Explicit directions
    },
    'attachment': {
        'rate_constant': A * np.exp(-E_a / (k_B * T)),
        'atom_types': [0]  # Empty sites
    }
}