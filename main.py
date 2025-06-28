import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from kmc import KMC_Simulation
from visualization import CrystalVisualizer
import numpy as np
import time
import sys

import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from kmc import KMC_Simulation
from visualization import CrystalVisualizer
import numpy as np
import time
import sys

# Configuration
'''CONFIG = {
    'lattice_size': 20,
    'temperature': 800,
    'num_steps': 1000,
    'update_interval': 10,
    'visualize_every': 5,
    'viewpoint': (30, 45)
}
'''

# Change JUST these values in your CONFIG dictionary:
CONFIG = {
    'lattice_size': 20,       # Keep unchanged
    'temperature': 800,       # Keep unchanged
    'num_steps': 10000,       # Only changed value (from 1000)
    'update_interval': 100,   # Sparse output (every 100 steps)
    'visualize_every': 500   # Update visualization every 1000 steps
}
class SimulationApp:
    def __init__(self):
        # Setup visualization and UI
        self._setup_ui()
        self.visualizer = CrystalVisualizer()
        self._initialize_simulation()
        self._running = False
        self._current_step = 0
        
        # Initial state
        self.update_display()
        plt.show()

    def _setup_ui(self):
        """Initialize the user interface"""
        self.fig = plt.figure(figsize=(12, 8), num="KMC Simulation Controller")
        self.ax = self.fig.add_subplot(111, projection='3d')
        plt.subplots_adjust(bottom=0.2)
        
        # Create control buttons
        self._create_buttons()
        
        # Add status text
        self.status_text = self.fig.text(
            0.05, 0.15, 
            "Initializing simulation...",
            fontsize=10,
            bbox=dict(facecolor='white', alpha=0.7)
        )

    def _create_buttons(self):
        """Create and configure control buttons"""
        self.start_btn = Button(
            plt.axes([0.15, 0.05, 0.2, 0.075]),
            'Start', 
            color='0.85',
            hovercolor='0.95'
        )
        self.pause_btn = Button(
            plt.axes([0.4, 0.05, 0.2, 0.075]),
            'Pause', 
            color='0.85',
            hovercolor='0.95'
        )
        self.reset_btn = Button(
            plt.axes([0.65, 0.05, 0.2, 0.075]),
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
            self.sim = KMC_Simulation(
                CONFIG['lattice_size'],
                CONFIG['temperature']
            )
            print("Simulation initialized successfully")
        except Exception as e:
            print(f"Initialization error: {str(e)}")
            sys.exit(1)

    def start_simulation(self, event=None):
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
        self._update_button_states()
        
        self._run_simulation()

    def _run_simulation(self):
        """Main simulation loop"""
        start_time = time.time()
        
        while self._current_step < CONFIG['num_steps'] and self._running:
            if self.sim.paused:
                plt.pause(0.1)
                continue
                
            # Execute KMC step
            _, dt, event_type = self.sim.bkl_kmc_step()
            self._current_step += 1
            
            # Periodic updates
            if self._current_step % CONFIG['update_interval'] == 0:
                self._update_display(event_type)
                
            # Visualization
            if self._current_step % CONFIG['visualize_every'] == 0:
                self.update_display()

        # Final output
        if self._current_step >= CONFIG['num_steps']:
            self._print_final_stats(start_time)
            
        self._running = False
        self._update_button_states()

    def _update_display(self, event_type):
        """Update visualization and statistics"""
        occupied = len([p for p in self.sim.occupied_sites if self.sim.lattice[p] == 2])
        empty = len(self.sim.empty_sites)
        
        # Update console output
        stats = self._get_stats_text(occupied, empty, event_type)
        print(stats, end='\r')
        
        # Update figure text
        self.status_text.set_text(stats)

    def _get_stats_text(self, occupied, empty, event_type):
        """Generate formatted statistics string"""
        coverage = 100 * occupied / (CONFIG['lattice_size']**3)
        aspect_ratio = self.sim.get_aspect_ratio()
        
        return (
            f"Step {self._current_step:4d}/{CONFIG['num_steps']} | "
            f"Event: {event_type.upper():7s} | "
            f"Mobile: {occupied:3d} | "
            f"Coverage: {coverage:5.1f}% | "
            f"Aspect Ratio: {aspect_ratio:.2f}"
        )

    def _print_final_stats(self, start_time):
        """Print simulation completion statistics"""
        real_time = time.time() - start_time
        print("\n" + "="*50)
        print("Simulation Complete")
        print(f"KMC time: {self.sim.time:.2e} s")
        print(f"Real time: {real_time:.2f} s")
        print("\nEvent counts:")
        print(f"X-diffusions: {self.sim._event_counts['diffuse_x']}")
        print(f"Y-diffusions: {self.sim._event_counts['diffuse_y']}")
        print(f"Attachments: {self.sim._event_counts['attach']}")
        print("="*50)

    def toggle_pause(self, event):
        """Toggle pause state"""
        if not self._running:
            print("\nStart the simulation first before pausing")
            return
            
        self.sim.paused = not self.sim.paused
        self._update_button_states()
        
        if self.sim.paused:
            print("\nSimulation PAUSED")
        else:
            print("\nSimulation RESUMED")

    def reset_simulation(self, event):
        """Reset to initial state"""
        print("\n=== Resetting Simulation ===")
        self._running = False
        self._current_step = 0
        self.sim.reset()
        self._update_button_states()
        self.update_display()

    def _update_button_states(self):
        """Update button appearances based on state"""
        self.start_btn.set_active(not self._running)
        self.pause_btn.label.set_text('Resume' if self.sim.paused else 'Pause')
        self.pause_btn.set_active(self._running)

    def update_display(self):
        """Update the full visualization"""
        metrics = {
            'x_events': self.sim._event_counts['diffuse_x'],
            'y_events': self.sim._event_counts['diffuse_y'],
            'aspect_ratio': self.sim.get_aspect_ratio(),
            'coverage': len(self.sim.occupied_sites)/self.sim.lattice.size
        }
        
        self.visualizer.visualize(
            self.sim.lattice,
            metrics=metrics,
            highlight_defects=True
        )

if __name__ == "__main__":
    try:
        app = SimulationApp()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)