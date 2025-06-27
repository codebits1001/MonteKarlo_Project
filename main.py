import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from kmc import KMC_Simulation
from visualization import visualize_lattice
import numpy as np
import time

# Configuration
CONFIG = {
    'lattice_size': 10,
    'temperature': 800,
    'num_steps': 500,
    'update_interval': 1,
    'viewpoint': (25, 45)
}

class SimulationApp:
    def __init__(self):
        # Setup figure and UI
        self.fig = plt.figure(figsize=(10, 8), num="KMC Simulation Controller")
        self.ax = self.fig.add_subplot(111, projection='3d')
        plt.subplots_adjust(bottom=0.25)
        
        # Simulation state tracking
        self._running = False
        self._current_step = 0
        
        # Initialize simulation components
        self._create_buttons()
        self._initialize_simulation()
        
        # Start in paused state
        self.sim.paused = True
        self.pause_btn.label.set_text('Pause')
        
        # Initial visualization
        self.update_visualization(self.sim.lattice)
        self.update_stats(0, 1, CONFIG['lattice_size']**3 - 1, 'init')

    def _create_buttons(self):
        """Create and configure control buttons"""
        self.start_btn = Button(
            plt.axes([0.15, 0.05, 0.25, 0.075]),
            'Start', 
            color='lightblue',
            hovercolor='lightcyan'
        )
        self.pause_btn = Button(
            plt.axes([0.45, 0.05, 0.25, 0.075]),
            'Pause', 
            color='0.85',
            hovercolor='0.95'
        )
        self.reset_btn = Button(
            plt.axes([0.75, 0.05, 0.2, 0.075]),
            'Reset', 
            color='0.95',
            hovercolor='1.0'
        )
        
        # Connect callbacks
        self.start_btn.on_clicked(self.start_simulation)
        self.pause_btn.on_clicked(self.toggle_pause)
        self.reset_btn.on_clicked(self.reset_simulation)

    def _initialize_simulation(self):
        """Initialize simulation state"""
        try:
            self.sim = KMC_Simulation(CONFIG['lattice_size'], CONFIG['temperature'])
            self.sim.verbose = True
            self._seed_initial_atoms()
        except Exception as e:
            print(f"Initialization error: {str(e)}")
            raise

    def _seed_initial_atoms(self):
        """Create substrate layer and seed atom"""
        size = self.sim.lattice_size
        
        # Create fixed substrate (z=0 plane)
        for x in range(size):
            for y in range(size):
                pos = (x, y, 0)
                self.sim.lattice[pos] = 1  # Type 1 = substrate
                self.sim.occupied_sites.add(pos)
                self.sim.empty_sites.discard(pos)
        
        # Add mobile seed atom
        center = size // 2
        seed_pos = (center, center, 1)
        self.sim.lattice[seed_pos] = 2  # Type 2 = mobile
        self.sim.occupied_sites.add(seed_pos)
        self.sim.empty_sites.discard(seed_pos)

    def start_simulation(self, event):
        """Run the simulation"""
        if self._running:
            return
            
        print("\n=== Starting Simulation ===")
        print(f"Parameters: Lattice={CONFIG['lattice_size']}^3, "
              f"Temp={CONFIG['temperature']}K, "
              f"Steps={CONFIG['num_steps']}")
        
        self._running = True
        self._current_step = 0
        self.sim.paused = False
        self.pause_btn.label.set_text('Pause')
        self.start_btn.set_active(False)
        
        self._run_simulation()

    def _run_simulation(self):
        """Internal simulation loop with pause support"""
        start_time = time.time()  # Real clock time for reference
        kmc_time = 0.0  # KMC accumulated time
        
        while self._current_step < CONFIG['num_steps'] and self._running:
            if self.sim.paused:
                plt.pause(0.1)
                continue
                
            _, dt, event_type = self.sim.bkl_kmc_step()
            kmc_time += dt
            self._current_step += 1
            
            if self._current_step % CONFIG['update_interval'] == 0:
                self.update_visualization(self.sim.lattice)
                occupied = len([p for p in self.sim.occupied_sites if self.sim.lattice[p] == 2])
                empty = len(self.sim.empty_sites)
                self.update_stats(self._current_step, occupied, empty, event_type)
                plt.pause(0.01)

        if self._current_step >= CONFIG['num_steps']:
            total_time = kmc_time  # Use accumulated KMC time instead
            print(f"\n=== Completed in {total_time:.2e} seconds ===")
            
            # ADD THESE LINES TO PRINT EVENT COUNTS:
            print("\nEvent counts:")
            print(f"X-direction diffusions: {self.sim._event_counts['diffuse_x']}")
            print(f"Y-direction diffusions: {self.sim._event_counts['diffuse_y']}")
            print(f"Attachments: {self.sim._event_counts['attach']}")
        
            self._running = False
            self.start_btn.set_active(True)

        if self._current_step >= CONFIG['num_steps']:
            real_time = time.time() - start_time
            print(f"\n=== Completed in KMC time: {kmc_time:.2e} s (Real time: {real_time:.2f} s) ===")
        self._running = False
        self.start_btn.set_active(True)

    def toggle_pause(self, event):
        """Toggle pause state"""
        if not self._running:
            print("\nStart the simulation first before pausing")
            return
            
        self.sim.paused = not self.sim.paused
        if self.sim.paused:
            self.pause_btn.label.set_text('Resume')
            print("\nSimulation PAUSED")
        else:
            self.pause_btn.label.set_text('Pause')
            print("\nSimulation RESUMED")
    

    def reset_simulation(self, event):
        """Reset to initial state"""
        print("\n=== Resetting Simulation ===")
        self._running = False
        self._current_step = 0
        self.sim.reset()
        self._seed_initial_atoms()
        self.update_visualization(self.sim.lattice)
        self.sim.paused = True
        self.pause_btn.label.set_text('Pause')
        self.update_stats(0, 1, CONFIG['lattice_size']**3 - 1, 'reset')

    def update_visualization(self, lattice):
        """Update 3D visualization"""
        visualize_lattice(lattice, self.ax, CONFIG['viewpoint'])

    def update_stats(self, step, occupied, empty, event_type):
        """Update and display simulation statistics"""
        mobile_atoms = np.sum(self.sim.lattice == 2)
        coverage = 100 * mobile_atoms / (CONFIG['lattice_size']**3)
        
        stats = (f"Step {step:4d}/{CONFIG['num_steps']} | "
                 f"Event: {event_type.upper():7s} | "
                 f"Mobile: {mobile_atoms:3d} | "
                 f"Coverage: {coverage:5.1f}%")
        
        print(stats, end='\r')
        return stats

    def show(self):
        """Display the application"""
        plt.show()

if __name__ == "__main__":
    try:
        app = SimulationApp()
        app.show()
    except Exception as e:
        print(f"Application error: {str(e)}")