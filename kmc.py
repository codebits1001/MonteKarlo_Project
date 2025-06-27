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
from events import get_neighbors, arrhenius, get_group_rates, get_diffusion_rate_anisotropic

class KMC_Simulation:
    def __init__(self, lattice_size, temperature):
        """Initialize simulation with time tracking"""
        self.lattice_size = lattice_size
        self.temperature = temperature
        self.lattice = np.zeros((lattice_size,)*3, dtype=int)
        self.verbose = False
        self.paused = False
        self._event_counts = {'attach': 0, 'diffuse_x': 0, 'diffuse_y': 0}  # Updated for anisotropy
        self.empty_sites = set(np.ndindex(self.lattice.shape))
        self.occupied_sites = set()
        self.time = 0.0
        self._initialize_substrate()

    def _initialize_substrate(self):
        """Create substrate layer and seed atom"""
        size = self.lattice_size
        # Create fixed substrate (z=0 plane)
        for x, y in np.ndindex(size, size):
            pos = (x, y, 0)
            self.lattice[pos] = 1
            self.occupied_sites.add(pos)
            self.empty_sites.discard(pos)
        # Add mobile seed atom
        center = size // 2
        seed_pos = (center, center, 1)
        self.lattice[seed_pos] = 2
        self.occupied_sites.add(seed_pos)
        self.empty_sites.discard(seed_pos)

    def bkl_kmc_step(self):
        """Execute one KMC step with anisotropic diffusion"""
        if self.paused:
            return self.lattice, 0, 'paused'

        if not hasattr(self, '_initialized'):
            self._initialized = True
            return self.lattice, 0, 'init'

        # Get rates and select event
        group_rates = get_group_rates(self.lattice, self.temperature)
        total_rate = sum(group_rates.values())
        if total_rate == 0:
            return self.lattice, 0, 'none'

        event_group = random.choices(
            list(group_rates.keys()),
            weights=list(group_rates.values())
        )[0]

        # Execute event
        if event_group == 'diffusion':
            event_pos = random.choice([p for p in self.occupied_sites if self.lattice[p] == 2])
            event_type = self._execute_diffusion_anisotropic(event_pos)  # Updated to anisotropic
        else:
            event_pos = random.choice(list(self.empty_sites))
            self._execute_attachment(event_pos)
            event_type = 'attach'

        # Advance time
        time_step = -np.log(random.random()) / total_rate
        self.time += time_step
        return self.lattice, time_step, event_type

    def _execute_diffusion_anisotropic(self, pos):
        """Handle anisotropic diffusion with directional rates and proper boundary checks"""
        # Calculate directional rates
        x_rate = get_diffusion_rate_anisotropic(pos, self.lattice, 'x', self.temperature)
        y_rate = get_diffusion_rate_anisotropic(pos, self.lattice, 'y', self.temperature)
        
        # Choose direction
        direction = random.choices(['x', 'y'], weights=[x_rate, y_rate])[0]
        
        # Get candidate positions with periodic boundaries
        x, y, z = pos
        size = self.lattice_size
        
        if direction == 'x':
            candidates = [
                ((x + 1) % size, y, z),
                ((x - 1) % size, y, z)
            ]
        else:  # y-direction
            candidates = [
                (x, (y + 1) % size, z),
                (x, (y - 1) % size, z)
            ]
        
        # Check vacancy
        vacant = [n for n in candidates if self.lattice[n] == 0]
        
        if vacant:
            new_pos = random.choice(vacant)
            self._move_atom(pos, new_pos)
            self._event_counts[f'diffuse_{direction}'] += 1
            return f'diffuse_{direction}'
        return 'none'  # No move occurred

    def _move_atom(self, old_pos, new_pos):
        """Helper method to move atoms and update tracking sets"""
        self.lattice[new_pos] = 2
        self.lattice[old_pos] = 0
        self.occupied_sites.remove(old_pos)
        self.occupied_sites.add(new_pos)
        self.empty_sites.add(old_pos)
        self.empty_sites.remove(new_pos)

    def _execute_attachment(self, pos):
        """Handle atom attachment"""
        self.lattice[pos] = 2
        self.empty_sites.remove(pos)
        self.occupied_sites.add(pos)
        self._event_counts['attach'] += 1

    def run_simulation(self, num_steps, update_interval=10, 
                      visual_callback=None, graph_callback=None, verbose=False):
        """Run complete simulation"""
        self.verbose = verbose
        simulation_time = 0.0
        
        for step in range(num_steps):
            while self.paused:
                time.sleep(0.1)
                continue
                
            _, dt, event_type = self.bkl_kmc_step()
            simulation_time += dt

            if step % update_interval == 0:
                if visual_callback:
                    visual_callback(self.lattice)
                if graph_callback:
                    occupied = len([p for p in self.occupied_sites if self.lattice[p] == 2])
                    empty = len(self.empty_sites)
                    graph_callback(step, occupied, empty, event_type)

        return self.lattice, simulation_time

    def reset(self):
        """Reset simulation state"""
        self.lattice.fill(0)
        self._event_counts = {'attach': 0, 'diffuse_x': 0, 'diffuse_y': 0}
        self.empty_sites = set(np.ndindex(self.lattice.shape))
        self.occupied_sites = set()
        self._initialize_substrate()