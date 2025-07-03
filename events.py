

#june 30

import numpy as np
import random
from typing import Dict, Tuple
from constants import SIMULATION_PARAMS, DIFFUSION, STATES

class RateCalculator:
    def __init__(self, lattice_size: int):
        self.size = lattice_size
        self.neighbor_offsets = {
            'x': [(1,0,0), (-1,0,0)],
            'y': [(0,1,0), (0,-1,0)],
            'z': [(0,0,1), (0,0,-1)]
        }

    def calculate_total_rates(self, lattice: np.ndarray, temperature: float) -> Dict[str, float]:
        """Calculate rates for all event types."""
        rates = {
            'diffuse_x': 0.0,
            'diffuse_y': 0.0,
            'diffuse_z': 0.0,
            'attach': 0.0
        }
        
        # Diffusion rates
        mobile_atoms = np.argwhere(lattice == STATES['MOBILE'])
        for pos in mobile_atoms:
            for direction in ['x', 'y', 'z']:
                rates[f'diffuse_{direction}'] += self._calculate_diffusion_rate(
                    tuple(pos), lattice, direction, temperature
                )
        
        # Attachment rate
        empty_sites = np.sum(lattice == STATES['EMPTY'])
        rates['attach'] = self._arrhenius_rate(
            SIMULATION_PARAMS['E_a'], temperature
        ) * empty_sites
        
        return rates

    def _calculate_diffusion_rate(self, pos: Tuple[int,int,int], 
                                lattice: np.ndarray, 
                                direction: str, 
                                temperature: float) -> float:
        """Calculate diffusion rate in specific direction."""
        vacant = 0
        for dx, dy, dz in self.neighbor_offsets[direction]:
            nx = (pos[0] + dx) % self.size
            ny = (pos[1] + dy) % self.size
            nz = (pos[2] + dz) % self.size
            
            if lattice[nx, ny, nz] == STATES['EMPTY']:
                vacant += 1
                
        if vacant == 0:
            return 0.0
            
        return self._arrhenius_rate(DIFFUSION[direction], temperature) * vacant

    def get_periodic_neighbors(self, pos: Tuple[int,int,int]) -> Dict[str,Tuple[int,int,int]]:
        """Get all periodic neighbors with direction labels."""
        x, y, z = pos
        return {
            'x+': ((x+1)%self.size, y, z),
            'x-': ((x-1)%self.size, y, z),
            'y+': (x, (y+1)%self.size, z),
            'y-': (x, (y-1)%self.size, z),
            'z+': (x, y, (z+1)%self.size),
            'z-': (x, y, (z-1)%self.size)
        }

    @staticmethod
    def _arrhenius_rate(barrier: float, temperature: float) -> float:
        """Calculate Arrhenius rate."""
        return SIMULATION_PARAMS['A'] * np.exp(-barrier / (SIMULATION_PARAMS['k_B'] * temperature))