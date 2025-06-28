# Recreate substrate on reset
'''

import numpy as np
import time
import random
from events import get_neighbors, arrhenius, get_group_rates

class KMC_Simulation:
    def __init__(self, lattice_size, temperature):
        """Your original init with added time tracking"""
        self.lattice_size = lattice_size
        self.temperature = temperature
        self.lattice = np.zeros((lattice_size,)*3, dtype=int)
        self.verbose = False
        self.paused = False
        self._event_counts = {'attach': 0, 'diffuse': 0}
        self.empty_sites = set(np.ndindex(self.lattice.shape))
        self.occupied_sites = set()
        self.time = 0.0  # New time tracker
        self._initialize_substrate()

    def _initialize_substrate(self):
        """YOUR ORIGINAL METHOD THAT WAS MISSING"""
        size = self.lattice_size
        
        # Create bottom layer (z=0) as fixed substrate
        for x in range(size):
            for y in range(size):
                pos = (x, y, 0)
                self.lattice[pos] = 1  # Type 1 = substrate (immobile)
                self.occupied_sites.add(pos)
                self.empty_sites.discard(pos)
        
        # Add one mobile seed atom above center
        center = size // 2
        seed_pos = (center, center, 1)
        self.lattice[seed_pos] = 2  # Type 2 = mobile atom
        self.occupied_sites.add(seed_pos)
        self.empty_sites.discard(seed_pos)

    def bkl_kmc_step(self):
        if self.paused:
            return self.lattice, 0, 'paused'

    # First step should show initialization

            if not hasattr(self, '_initialized'):
                self._initialized = True
                return self.lattice, 0, 'init'

        # Step 1-2: Get group rates (BKL optimization)
        group_rates = get_group_rates(self.lattice, self.temperature)
        total_rate = sum(group_rates.values())

        if total_rate == 0:
            return self.lattice, 0, 'none'

        # Step 3-4: Select event group
        event_group = random.choices(
            list(group_rates.keys()),
            weights=list(group_rates.values())
        )[0]

        # Step 5: Execute event (using your original methods)
        if event_group == 'diffusion':
            event_pos = random.choice([p for p in self.occupied_sites if self.lattice[p] == 2])
            self._execute_diffusion(event_pos)
            event_type = 'diffuse'
        else:
            event_pos = random.choice(list(self.empty_sites))
            self._execute_attachment(event_pos)
            event_type = 'attach'

        # Step 6: Time advance (your original Poisson step)
        time_step = -np.log(random.random()) / total_rate
        self.time += time_step
        
        return self.lattice, time_step, event_type
    

    def _execute_attachment(self, pos):
        """Your original unchanged method"""
        self.lattice[pos] = 2
        self.empty_sites.remove(pos)
        self.occupied_sites.add(pos)
        self._event_counts['attach'] += 1

    def _execute_diffusion(self, pos):
        """Your original unchanged method"""
        neighbors = get_neighbors(pos, self.lattice)
        vacant = [n for n in neighbors if self.lattice[n] == 0]
        if vacant:
            new_pos = random.choice(vacant)
            self.lattice[new_pos] = 2
            self.lattice[pos] = 0
            self.occupied_sites.remove(pos)
            self.occupied_sites.add(new_pos)
            self.empty_sites.add(pos)
            self.empty_sites.remove(new_pos)
            self._event_counts['diffuse'] += 1

def _execute_diffusion_anisotropic(self, pos):
    
    """Updated diffusion with directional preference"""
    # Step 1: Choose direction weighted by rates
    x_rate = get_diffusion_rate_anisotropic(pos, self.lattice, 'x', self.temperature)
    y_rate = get_diffusion_rate_anisotropic(pos, self.lattice, 'y', self.temperature)
    direction = random.choices(['x', 'y'], weights=[x_rate, y_rate])[0]  # Weighted selection

    # Step 2: Get valid neighbors in chosen direction
    x, y, z = pos
    if direction == 'x':
        candidates = [(x+1, y, z), (x-1, y, z)]
    else:
        candidates = [(x, y+1, z), (x, y-1, z)]

    # Step 3: Apply periodic boundaries and filter vacant
    shape = self.lattice.shape
    vacant = [
        (n[0]%shape[0], n[1]%shape[1], n[2]%shape[2]) 
        for n in candidates if self.lattice[n] == 0
    ]

    # Step 4: Execute hop
    if vacant:
        new_pos = random.choice(vacant)
        self.lattice[new_pos] = 2
        self.lattice[pos] = 0
        self._event_counts[f'diffuse_{direction}'] += 1  # Track direction
        return True
    return False
    


    def run_simulation(self, num_steps, update_interval=10, 
                       visual_callback=None, graph_callback=None, verbose=False):
        """Run complete simulation"""
        self.verbose = verbose
        simulation_time = 0.0  # Track time for this run
    
        for step in range(num_steps):
            while self.paused:
                time.sleep(0.1)
                continue
                
            _, dt, event_type = self.bkl_kmc_step()
            simulation_time += dt  # Accumulate time
            self.time += dt  # Also track total simulation time

            if step % update_interval == 0:
                if visual_callback:
                    visual_callback(self.lattice)
                if graph_callback:
                    occupied = len([p for p in self.occupied_sites if self.lattice[p] == 2])
                    empty = len(self.empty_sites)
                    graph_callback(step, occupied, empty, event_type)

        return self.lattice, simulation_time
    

    def reset(self):
        """Your original unchanged method"""
        self.lattice.fill(0)
        self._event_counts = {'attach': 0, 'diffuse': 0}
        self.empty_sites = set(np.ndindex(self.lattice.shape))
        self.occupied_sites = set()
        self._initialize_substrate() '''

import numpy as np
import time
import random
from scipy import stats
from events import get_diffusion_rate_anisotropic, get_group_rates

class KMC_Simulation:
    NO_EVENT = 'none'
    def __init__(self, lattice_size, temperature):
        """Initialize KMC simulation with anisotropic diffusion support"""
        self.lattice_size = lattice_size
        self.temperature = temperature
        self.lattice = np.zeros((lattice_size,)*3, dtype=int)
        
        # Simulation state
        self.verbose = False
        self.paused = False
        self.time = 0.0
        self.step_count = 0
        self.energy = 0.0
        
        # Tracking structures
        self._event_counts = {
            'attach': 0, 
            'diffuse_x': 0, 
            'diffuse_y': 0,
            'diffuse_z': 0
        }
        self.empty_sites = set(np.ndindex(self.lattice.shape))
        self.occupied_sites = set()
        
        # Initialize simulation
        self._initialize_substrate()

    def _initialize_substrate(self):
        """Create substrate layer and seed atom with periodic boundaries"""
        size = self.lattice_size
        
        # Create fixed substrate (z=0 plane)
        substrate_positions = np.ndindex(size, size)
        for x, y in substrate_positions:
            pos = (x, y, 0)
            self.lattice[pos] = 1  # Type 1 = substrate
            self.occupied_sites.add(pos)
            self.empty_sites.discard(pos)
        
        # Add mobile seed atom
        center = size // 2
        seed_pos = (center, center, 1)
        self.lattice[seed_pos] = 2  # Type 2 = mobile
        self.occupied_sites.add(seed_pos)
        self.empty_sites.discard(seed_pos)

    def bkl_kmc_step(self):
        """Execute one kinetic Monte Carlo step with anisotropic diffusion"""
        if self.paused:
            return self.lattice, 0, 'paused'

        # Initialization handling
        if not hasattr(self, '_initialized'):
            self._initialized = True
            return self.lattice, 0, 'init'

        # Calculate event rates
        group_rates = get_group_rates(self.lattice, self.temperature)
        total_rate = sum(group_rates.values())
        
        # Early exit if no possible events
        if total_rate == 0:
            return self.lattice, 0, 'none'

        # Select event type proportionally to rates
        event_group = random.choices(
            list(group_rates.keys()),
            weights=list(group_rates.values())
        )[0]

        # Execute selected event
        if event_group == 'diffusion':
            mobile_atoms = [p for p in self.occupied_sites if self.lattice[p] == 2]
            if not mobile_atoms:
                return self.lattice, 0, 'none'
                
            event_pos = random.choice(mobile_atoms)
            event_type = self._execute_diffusion_anisotropic(event_pos)
        else:  # attachment
            if not self.empty_sites:
                return self.lattice, 0, 'none'
                
            event_pos = random.choice(list(self.empty_sites))
            self._execute_attachment(event_pos)
            event_type = 'attach'

        # Log aspect ratio periodically
        if self.step_count % 100 == 0:
            ratio = self.get_aspect_ratio()
            print(f"Step {self.step_count:4d} | Aspect Ratio (X/Y): {ratio:.2f}")

        # Advance simulation time
        time_step = -np.log(random.random()) / total_rate
        self.time += time_step
        self.step_count += 1
        
        return self.lattice, time_step, event_type

    def _execute_diffusion_anisotropic(self, pos):
        """Optimized anisotropic diffusion with early vacancy checks"""
        direction_rates = {}
        possible_moves = []
        
        for direction in ['x', 'y', 'z']:
            # Generate both possible hops (±1)
            for delta in [-1, 1]:
                x, y, z = pos
                if direction == 'x':
                    new_pos = ((x + delta) % self.lattice_size, y, z)
                elif direction == 'y':
                    new_pos = (x, (y + delta) % self.lattice_size, z)
                else:  # z
                    new_pos = (x, y, (z + delta) % self.lattice_size)
                
                if self.lattice[new_pos] == 0:  # Only consider vacant sites
                    rate = get_diffusion_rate_anisotropic(pos, self.lattice, direction, self.temperature)
                    if rate > 0:
                        possible_moves.append((direction, new_pos, rate))
        
        if not possible_moves:
            return 'none'
        
        # Weighted selection from valid moves only
        directions, new_positions, rates = zip(*possible_moves)
        selected_idx = random.choices(range(len(rates)), weights=rates)[0]
        
        self._move_atom(pos, new_positions[selected_idx])
        event_type = f'diffuse_{directions[selected_idx]}'
        self._event_counts[event_type] += 1
        return event_type
    

    def _move_atom(self, old_pos, new_pos):
        """Move atom and update all tracking structures"""
        # Update lattice
        self.lattice[new_pos] = 2
        self.lattice[old_pos] = 0
        
        # Update sets
        self.occupied_sites.remove(old_pos)
        self.occupied_sites.add(new_pos)
        self.empty_sites.add(old_pos)
        self.empty_sites.remove(new_pos)
        
        # Update energy (placeholder - implement your energy model)
        self.energy += self._calculate_energy_change(old_pos, new_pos)

    def _calculate_energy_change(self, old_pos, new_pos):
        """Placeholder for energy calculation"""
        return 0.0  # Implement your energy model here

    def _execute_attachment(self, pos):
        """Handle atom attachment to empty site"""
        self.lattice[pos] = 2
        self.empty_sites.remove(pos)
        self.occupied_sites.add(pos)
        self._event_counts['attach'] += 1
    
    def get_aspect_ratio(self):
        mobile_atoms = np.argwhere(self.lattice == 2)
        if len(mobile_atoms) < 10:  # More robust threshold
            return 1.0
        
        # Use interquartile range for better stability
        x_coords = mobile_atoms[:, 0]
        y_coords = mobile_atoms[:, 1]
        x_span = np.percentile(x_coords, 75) - np.percentile(x_coords, 25)
        y_span = np.percentile(y_coords, 75) - np.percentile(y_coords, 25)
        
        # Add small epsilon to prevent division by zero
        return (x_span + 1e-6) / (y_span + 1e-6)

    def run_simulation(self, num_steps, update_interval=10, 
                      visual_callback=None, data_callback=None):
        """
        Run complete simulation with progress tracking
        Args:
            num_steps: Total steps to run
            update_interval: Steps between callbacks
            visual_callback: Function(lattice) for visualization
            data_callback: Function(metrics) for data collection
        Returns:
            (final_lattice, metrics_dict)
        """
        metrics = {
            'time': [],
            'coverage': [],
            'aspect_ratio': [],
            'energy': [],
            'events': []
        }
        
        for step in range(num_steps):
            while self.paused:
                time.sleep(0.1)
                continue
                
            # Execute KMC step
            lattice, dt, event_type = self.bkl_kmc_step()
            metrics['time'].append(self.time)
            
            # Periodic updates
            if step % update_interval == 0:
                # Calculate metrics
                coverage = len(self.occupied_sites)/self.lattice.size
                aspect_ratio = self.get_aspect_ratio()
                
                metrics['coverage'].append(coverage)
                metrics['aspect_ratio'].append(aspect_ratio)
                metrics['energy'].append(self.energy)
                metrics['events'].append(self._event_counts.copy())
                
                # Callbacks
                if visual_callback:
                    visual_callback(lattice)
                if data_callback:
                    data_callback({
                        'step': step,
                        'time': self.time,
                        'coverage': coverage,
                        'aspect_ratio': aspect_ratio,
                        'energy': self.energy,
                        'events': self._event_counts.copy()
                    })

        return self.lattice, metrics

    def reset(self):
        """Reset simulation to initial state"""
        self.lattice.fill(0)
        self.time = 0.0
        self.step_count = 0
        self.energy = 0.0
        self._event_counts = {k:0 for k in self._event_counts}
        self.empty_sites = set(np.ndindex(self.lattice.shape))
        self.occupied_sites = set()
        self._initialize_substrate()