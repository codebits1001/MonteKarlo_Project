import numpy as np
import random
from typing import Dict, Set, Tuple
from constants import SIMULATION_PARAMS, STATES, DIFFUSION, NUCLEATION, STRUCTURE_3D
from events import RateCalculator
from clusters import ClusterAnalyzer
from nucleation import NucleationCalculator

class CrystalGrowthSimulation:
    def __init__(self, lattice_size: int, temperature: float):
        self.lattice_size = lattice_size
        self.temperature = temperature
        
        # Initialize lattice
        self.lattice = np.zeros((lattice_size,)*3, dtype=np.int8)
        self.empty_sites: Set[Tuple[int, int, int]] = set()
        self.occupied_sites: Set[Tuple[int, int, int]] = set()
        
        # Simulation components
        self.rate_calc = RateCalculator(lattice_size)
        self.cluster_analyzer = ClusterAnalyzer(SIMULATION_PARAMS['critical_size'])
        
        # Updated nucleation calculator with k_B parameter
        self.nucleation_calc = NucleationCalculator(
            NUCLEATION['T_m'], 
            NUCLEATION['L'], 
            NUCLEATION['gamma'], 
            NUCLEATION['theta_deg'],
            SIMULATION_PARAMS['k_B']  # Added Boltzmann constant
        )
        
        # Simulation state
        self.time = 0.0
        self.step_count = 0
        self.paused = False
        self.nucleation_count = 0
        self.event_counts = {
            'attach': 0,
            'diffuse_x': 0,
            'diffuse_y': 0,
            'diffuse_z': 0,
            'nucleation': 0
        }
        
        self._initialize_lattice()
        # Initialize cluster analysis at start
        self.cluster_analyzer.update_cluster_info(self.lattice)

    def _initialize_lattice(self):
        """Initialize lattice with substrate and seed atom."""
        size = self.lattice_size
        self.empty_sites = set(np.ndindex(self.lattice.shape))
        self.occupied_sites.clear()
        
        # Create substrate
        for x, y in np.ndindex((size, size)):
            pos = (x, y, 0)
            self.lattice[pos] = STATES['SUBSTRATE']
            self.occupied_sites.add(pos)
            self.empty_sites.discard(pos)
        
        # Add seed atom
        seed_pos = (size//2, size//2, 1)
        self.lattice[seed_pos] = STATES['MOBILE']
        self.occupied_sites.add(seed_pos)
        self.empty_sites.discard(seed_pos)

    def execute_simulation_step(self) -> Tuple[np.ndarray, float, str]:
        """Execute one full KMC step."""
        if self.paused:
            return self.lattice, 0.0, 'paused'
        
        # Calculate rates (using current state)
        rates = self.rate_calc.calculate_total_rates(self.lattice, self.temperature)
        if self.cluster_analyzer.get_critical_clusters():
            rates['nucleation'] = self._calculate_nucleation_rate()
        
        # Select and execute event
        event_type = self._select_and_execute_event(rates)
        
        # Update cluster analysis AFTER event execution
        self.cluster_analyzer.update_cluster_info(self.lattice)
        
        # Advance time
        total_rate = sum(rates.values())
        dt = -np.log(random.random()) / total_rate if total_rate > 0 else 0
        self.time += dt
        self.step_count += 1
        
        return self.lattice, dt, event_type

    def _calculate_nucleation_rate(self) -> float:
        """Calculate total nucleation rate for critical clusters."""
        delta_T = self.nucleation_calc.compute_undercooling(self.temperature)
        delta_Gv = self.nucleation_calc.compute_volume_energy(delta_T)
        _, delta_G_hetero = self.nucleation_calc.compute_nucleation_barriers(delta_T)
        
        total_rate = 0.0
        for cluster in self.cluster_analyzer.get_critical_clusters():
            prob = self.nucleation_calc.compute_nucleation_probability(delta_G_hetero, self.temperature)
            total_rate += NUCLEATION['A'] * prob * cluster['size']
            
        return total_rate

    def _select_and_execute_event(self, rates: Dict[str, float]) -> str:
        """Select and execute event based on rates."""
        event_groups = [g for g in rates if rates[g] > 0]
        weights = [rates[g] for g in event_groups]
        selected = random.choices(event_groups, weights=weights)[0]
        
        if selected.startswith('diffuse'):
            return self._execute_diffusion(selected.split('_')[1])
        elif selected == 'attach':
            return self._execute_attachment()
        elif selected == 'nucleation':
            return self._execute_nucleation()
        return 'no_event'

    def _execute_diffusion(self, direction: str) -> str:
        """Execute diffusion event in specified direction."""
        mobile_atoms = [p for p in self.occupied_sites if self.lattice[p] == STATES['MOBILE']]
        if not mobile_atoms:
            return 'no_mobile_atoms'
            
        pos = random.choice(mobile_atoms)
        possible_moves = []
        
        for delta in [-1, 1]:
            x, y, z = pos
            if direction == 'x':
                new_pos = ((x + delta) % self.lattice_size, y, z)
            elif direction == 'y':
                new_pos = (x, (y + delta) % self.lattice_size, z)
            else:
                new_pos = (x, y, (z + delta) % self.lattice_size)
                
            if self.lattice[new_pos] == STATES['EMPTY']:
                possible_moves.append(new_pos)
                
        if not possible_moves:
            return 'no_available_moves'
            
        new_pos = random.choice(possible_moves)
        self._move_atom(pos, new_pos)
        
        event_type = f'diffuse_{direction}'
        self.event_counts[event_type] += 1
        return event_type

    def _execute_attachment(self) -> str:
        """Execute attachment event - UPDATED to allow attachment to stable clusters."""
        candidates = [p for p in self.empty_sites 
                     if any(self.lattice[n] in (STATES['SUBSTRATE'], STATES['STABLE'])
                     for n in self.rate_calc.get_periodic_neighbors(p).values())]
        
        if not candidates:
            return 'no_attachment_sites'
            
        pos = random.choice(candidates)
        self.lattice[pos] = STATES['MOBILE']
        self.empty_sites.remove(pos)
        self.occupied_sites.add(pos)
        
        self.event_counts['attach'] += 1
        return 'attach'

    def _execute_nucleation(self) -> str:
        """Execute nucleation event."""
        critical_clusters = self.cluster_analyzer.get_critical_clusters()
        if not critical_clusters:
            return 'no_critical_clusters'
            
        # Weight by cluster size
        selected = random.choices(
            critical_clusters,
            weights=[c['size'] for c in critical_clusters]
        )[0]
        
        # Convert to stable
        for idx in selected['indices']:
            self.lattice[tuple(idx)] = STATES['STABLE']
        
        self.event_counts['nucleation'] += 1
        self.nucleation_count += 1
        return 'nucleation'

    def _move_atom(self, old_pos: Tuple[int, int, int], new_pos: Tuple[int, int, int]):
        """Move atom between positions."""
        self.lattice[new_pos] = self.lattice[old_pos]
        self.lattice[old_pos] = STATES['EMPTY']
        self.occupied_sites.remove(old_pos)
        self.occupied_sites.add(new_pos)
        self.empty_sites.add(old_pos)
        self.empty_sites.remove(new_pos)

    def calculate_aspect_ratio(self) -> float:
        """Calculate aspect ratio of mobile atoms."""
        mobile = np.argwhere(self.lattice == STATES['MOBILE'])
        if len(mobile) < 2:
            return 1.0
        return (mobile[:,0].max() - mobile[:,0].min()) / (mobile[:,1].max() - mobile[:,1].min() + 1e-6)

    def reset_simulation(self):
        """Reset simulation to initial state."""
        self.lattice.fill(STATES['EMPTY'])
        self.time = 0.0
        self.step_count = 0
        self.nucleation_count = 0
        self.event_counts = {k:0 for k in self.event_counts}
        self._initialize_lattice()
        self.cluster_analyzer = ClusterAnalyzer(SIMULATION_PARAMS['critical_size'])