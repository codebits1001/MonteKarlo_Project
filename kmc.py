'''import numpy as np
import random
import time
from events import atom_attachment_rate, atom_diffusion_rate, get_neighbors

class KMC_Simulation:
    def __init__(self, lattice_size, temperature):
        self.lattice_size = lattice_size
        self.temperature = temperature
        self.lattice = np.zeros((lattice_size,)*3, dtype=int)
        self.verbose = False
        self.paused = False
        self._event_counts = {'attach': 0, 'diffuse': 0}
        self.empty_sites = set(np.ndindex(self.lattice.shape))
        self.occupied_sites = set()
        
        # Initialize substrate and seed atom
        self._initialize_substrate()

    def _initialize_substrate(self):
        """Create fixed substrate layer and one mobile seed atom"""
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
        """Execute one KMC step"""
        if self.paused:
            return self.lattice, 0, 'paused'

        events = []
        total_rate = 0

        # Collect diffusion events (only for mobile atoms - type 2)
        for pos in self.occupied_sites:
            if self.lattice[pos] == 2:  # Only mobile atoms can diffuse
                rate = atom_diffusion_rate(pos, self.lattice, self.temperature)
                if rate > 0:
                    events.append(('diffuse', pos, rate))
                    total_rate += rate

        # Collect attachment events
        for pos in self.empty_sites:
            rate = atom_attachment_rate(pos, self.lattice, self.temperature)
            if rate > 0:
                events.append(('attach', pos, rate))
                total_rate += rate

        if total_rate == 0:
            if self.verbose:
                print("No possible events")
            return self.lattice, 0, 'none'

        # Select and execute event
        time_step = -np.log(random.random()) / total_rate
        event_type, pos, _ = random.choices(events, weights=[e[2] for e in events])[0]

        if event_type == 'attach':
            self._execute_attachment(pos)
        else:
            self._execute_diffusion(pos)

        return self.lattice, time_step, event_type

    def _execute_attachment(self, pos):
        """Handle atom attachment (new atoms are mobile type 2)"""
        self.lattice[pos] = 2  # New atoms are mobile
        self.empty_sites.remove(pos)
        self.occupied_sites.add(pos)
        self._event_counts['attach'] += 1

    def _execute_diffusion(self, pos):
        """Handle atom diffusion (only for mobile type 2 atoms)"""
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

    def run_simulation(self, num_steps, update_interval=10, 
                      visual_callback=None, graph_callback=None, verbose=False):
        """Run complete simulation"""
        self.verbose = verbose
        total_time = 0
        
        for step in range(num_steps):
            while self.paused:
                time.sleep(0.1)
                continue
                
            _, dt, event_type = self.bkl_kmc_step()
            total_time += dt

            if step % update_interval == 0:
                if visual_callback:
                    visual_callback(self.lattice)
                if graph_callback:
                    occupied = len([p for p in self.occupied_sites if self.lattice[p] == 2])  # Count only mobile atoms
                    empty = len(self.empty_sites)
                    graph_callback(step, occupied, empty, event_type)

        return self.lattice, total_time

    def reset(self):
        """Reset simulation state"""
        self.lattice.fill(0)
        self._event_counts = {'attach': 0, 'diffuse': 0}
        self.empty_sites = set(np.ndindex(self.lattice.shape))
        self.occupied_sites = set()
        self._initialize_substrate()  # Recreate substrate on reset
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

    '''def run_simulation(self, num_steps, update_interval=10, 
                      visual_callback=None, graph_callback=None, verbose=False):
        """Your original unchanged method"""
        self.verbose = verbose
        total_time = 0
        
        for step in range(num_steps):
            while self.paused:
                time.sleep(0.1)
                continue
                
            _, dt, event_type = self.bkl_kmc_step()
            total_time += dt

            if step % update_interval == 0:
                if visual_callback:
                    visual_callback(self.lattice)
                if graph_callback:
                    occupied = len([p for p in self.occupied_sites if self.lattice[p] == 2])
                    empty = len(self.empty_sites)
                    graph_callback(step, occupied, empty, event_type)

        return self.lattice, total_time
'''
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
        self._initialize_substrate()