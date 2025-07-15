import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from kmc import CrystalGrowthSimulation
from visualization import CrystalVisualizer
from graph import GraphVisualizer
import time
import sys
import numpy as np
from typing import Dict, List

class SimulationApp:
    def __init__(self):
        # Configuration with enhanced parameters
        self.config = {
            'lattice_size': 30,
            'temperature': 800,
            'num_steps': 10000,
            'update_interval': 150,
            'visualize_every': 20,
            'view_angle': (30, 49),
            'save_plots': True,
            'max_coverage': 0.95  # Stop if coverage reaches this value
        }
        
        # Initialize components with error handling
        try:
            self.setup_ui()
            self.visualizer = CrystalVisualizer()
            self.graph_visualizer = GraphVisualizer()
            self.initialize_simulation()
            
            # Initialize simulation data with starting values
            self.running = False
            self.current_step = 0
            self._init_simulation_data()
            
            plt.show()
        except Exception as e:
            print(f"Initialization failed: {str(e)}")
            sys.exit(1)

    def _init_simulation_data(self):
        """Initialize simulation data with starting values."""
        self.simulation_data = {
            'time_points': [0.0],
            'coverage': [0.0],
            'aspect_ratios': [1.0],
            'events': [{
                'attach': 0,
                'diffuse_x': 0,
                'diffuse_y': 0,
                'diffuse_z': 0,
                'nucleation': 0
            }],
            'cluster_stats': [{
                'total_clusters': 0,
                'critical_clusters': [],
                'largest_size': 0,
                'avg_size': 0.0
            }]
        }

    def setup_ui(self):
        """Initialize interactive UI with improved layout."""
        self.fig = plt.figure(figsize=(16, 10), num="Crystal Growth KMC Simulation")
        self.ax = self.fig.add_subplot(111, projection='3d')
        plt.subplots_adjust(bottom=0.2, top=0.95)
        
        # Control buttons with better styling
        self.create_buttons()
        
        # Enhanced status display
        self.status_text = self.fig.text(
            0.05, 0.15,
            "Ready to start simulation...",
            fontsize=11,
            bbox=dict(facecolor='white', alpha=0.9, edgecolor='lightgray', boxstyle='round')
        )

    def create_buttons(self):
        """Create interactive control buttons with improved feedback."""
        btn_style = {
            'color': 'lightgray',
            'hovercolor': '0.95'
        }
        
        self.start_btn = Button(
            plt.axes([0.15, 0.05, 0.2, 0.075]), 
            'Start', 
            **btn_style
        )
        self.pause_btn = Button(
            plt.axes([0.40, 0.05, 0.2, 0.075]), 
            'Pause',
            **btn_style
        )
        self.reset_btn = Button(
            plt.axes([0.65, 0.05, 0.2, 0.075]), 
            'Reset',
            **btn_style
        )
        
        # Set font sizes separately
        for btn in [self.start_btn, self.pause_btn, self.reset_btn]:
            btn.label.set_fontsize(12)
        
        # Connect callbacks with error handling
        self.start_btn.on_clicked(self._safe_callback(self.start_simulation))
        self.pause_btn.on_clicked(self._safe_callback(self.toggle_pause))
        self.reset_btn.on_clicked(self._safe_callback(self.reset_simulation))
    def _safe_callback(self, func):
        """Wrapper for button callbacks to prevent crashes."""
        def wrapper(event):
            try:
                func(event)
            except Exception as e:
                print(f"Error in callback: {str(e)}")
                self.status_text.set_text(f"Error: {str(e)}")
        return wrapper

    def initialize_simulation(self):
        """Initialize KMC simulation components with validation."""
        try:
            self.sim = CrystalGrowthSimulation(
                self.config['lattice_size'],
                self.config['temperature']
            )
            print("KMC Simulation initialized successfully")
        except Exception as e:
            raise RuntimeError(f"Simulation initialization failed: {str(e)}")

    def start_simulation(self, _=None):
        """Start the simulation run with enhanced checks."""
        if self.running:
            return
            
        print("\n=== Starting Simulation ===")
        print(f"Lattice: {self.config['lattice_size']}^3")
        print(f"Temperature: {self.config['temperature']}K")
        print(f"Steps: {self.config['num_steps']:,}")
        
        self.running = True
        self.current_step = 0
        self.sim.paused = False
        self._init_simulation_data()
        self.update_button_states()
        self.run_simulation()

    def run_simulation(self):
        """Main simulation loop with improved performance and error handling."""
        start_time = time.time()
        last_visualization = 0
        
        try:
            while (self.current_step < self.config['num_steps'] and 
                   self.running and 
                   len(self.sim.occupied_sites)/self.sim.lattice.size < self.config['max_coverage']):
                
                if self.sim.paused:
                    plt.pause(0.1)
                    continue
                    
                # Execute KMC step
                _, dt, event_type = self.sim.execute_simulation_step()
                self.current_step += 1
                
                # Collect data at intervals
                if self.current_step % self.config['update_interval'] == 0:
                    self.collect_simulation_data()
                
                # Visualize at intervals (with throttling)
                current_time = time.time()
                if (self.current_step % self.config['visualize_every'] == 0 and 
                    current_time - last_visualization > 0.1):  # Throttle to 10fps max
                    self.update_visualization()
                    self.update_status(event_type)
                    last_visualization = current_time
                    
            # Final processing
            self.finalize_simulation(start_time)
            
        except Exception as e:
            print(f"Simulation error: {str(e)}")
            self.status_text.set_text(f"Error: {str(e)}")
        finally:
            self.running = False
            self.update_button_states()

    def collect_simulation_data(self):
        """Record current simulation state with enhanced metrics."""
        try:
            coverage = len(self.sim.occupied_sites) / self.sim.lattice.size
            self.simulation_data['time_points'].append(self.sim.time)
            self.simulation_data['coverage'].append(coverage)
            self.simulation_data['aspect_ratios'].append(self.sim.calculate_aspect_ratio())
            self.simulation_data['events'].append(self.sim.event_counts.copy())
            
            # Enhanced cluster statistics
            cluster_stats = self.sim.cluster_analyzer.get_cluster_statistics()
            if cluster_stats['total_clusters'] > 0:
                cluster_stats['avg_size'] = sum(cluster_stats['size_distribution'].values()) / cluster_stats['total_clusters']
            self.simulation_data['cluster_stats'].append(cluster_stats)
            
        except Exception as e:
            print(f"Data collection error: {str(e)}")

    def update_visualization(self):
        """Update 3D visualization with current state using direct simulation data."""
        try:
            # Get current cluster stats
            current_stats = self.sim.cluster_analyzer.get_cluster_statistics()
            
            metrics = {
                'step': self.current_step,
                'time': self.sim.time,
                'coverage': len(self.sim.occupied_sites) / self.sim.lattice.size,
                'aspect_ratio': self.sim.calculate_aspect_ratio(),
                'events': self.sim.event_counts,
                'cluster_stats': current_stats
            }
            
            self.visualizer.visualize_crystal(
                self.sim.lattice,
                metrics=metrics,
                cluster_map=self.sim.cluster_analyzer.cluster_labels,
                view_angle=self.config['view_angle']
            )
            
        except Exception as e:
            print(f"Visualization error: {str(e)}")
    

    def update_visualization(self):
        """Update 3D visualization with current state using direct simulation data."""
        try:
            # Get current cluster stats
            current_stats = self.sim.cluster_analyzer.get_cluster_statistics()
            
            metrics = {
                'step': self.current_step,
                'time': self.sim.time,
                'coverage': len(self.sim.occupied_sites) / self.sim.lattice.size,
                'aspect_ratio': self.sim.calculate_aspect_ratio(),
                'events': self.sim.event_counts,
                'cluster_stats': current_stats
            }
            
            self.visualizer.visualize_crystal(
                self.sim.lattice,
                metrics=metrics,
                cluster_map=self.sim.cluster_analyzer.cluster_labels,
                view_angle=self.config['view_angle']
            )
            
        except Exception as e:
            print(f"Visualization error: {str(e)}")


    def update_status(self, event_type):
        """Update status display with current metrics."""
        try:
            mobile = sum(1 for p in self.sim.occupied_sites if self.sim.lattice[p] == 2)
            coverage = 100 * len(self.sim.occupied_sites) / self.sim.lattice.size
            aspect_ratio = self.sim.calculate_aspect_ratio()
            
            status = (
                f"Step {self.current_step:,}/{self.config['num_steps']:,} | "
                f"Event: {event_type.upper():<10} | "
                f"Mobile: {mobile:<4} | "
                f"Coverage: {coverage:5.1f}% | "
                f"Aspect: {aspect_ratio:.2f} | "
                f"Nucleation: {self.sim.nucleation_count} | "
                f"Clusters: {len(self.sim.cluster_analyzer.get_cluster_statistics().get('critical_clusters', []))}"
            )
            
            print(status, end='\r')
            self.status_text.set_text(status)
        except Exception as e:
            print(f"Status update failed: {str(e)}")

    def finalize_simulation(self, start_time):
        """Handle simulation completion tasks with better error handling."""
        try:
            self.generate_analysis_plots()
            self.print_summary_stats(start_time)
            
            # Force cleanup of resources
            plt.close('all')
            if hasattr(self, 'fig'):
                plt.close(self.fig)
                del self.fig
                
        except Exception as e:
            print(f"Finalization error: {str(e)}")
        finally:
            self.running = False
            self.update_button_states()
            
    def generate_analysis_plots(self):
        """Generate final analysis plots with enhanced visuals."""
        try:
            print("\nGenerating analysis plots...")
            
            # Growth kinetics plot with moving average
            self.graph_visualizer.create_growth_plot(
                time_data=self.simulation_data['time_points'],
                coverage_data=self.simulation_data['coverage'],
                aspect_ratios=self.simulation_data['aspect_ratios']
            )
            
            # Enhanced event distribution plot
            self.graph_visualizer.create_event_plot(
                time_data=self.simulation_data['time_points'],
                event_counts={
                    'x': [e['diffuse_x'] for e in self.simulation_data['events']],
                    'y': [e['diffuse_y'] for e in self.simulation_data['events']],
                    'z': [e['diffuse_z'] for e in self.simulation_data['events']],
                    'attach': [e['attach'] for e in self.simulation_data['events']],
                    'nucleation': [e['nucleation'] for e in self.simulation_data['events']]
                }
            )
            
            if self.config['save_plots']:
                self.graph_visualizer.save_plot("growth_kinetics.pdf")
                self.graph_visualizer.save_plot("event_distribution.pdf")
                self.visualizer.save_visualization("final_state.png")
                
        except Exception as e:
            print(f"Plot generation failed: {str(e)}")
        finally:
            self.graph_visualizer.close()

    def print_summary_stats(self, start_time):
        """Print comprehensive simulation statistics with more metrics."""
        try:
            real_time = time.time() - start_time
            final_coverage = len(self.sim.occupied_sites) / self.sim.lattice.size
            cluster_stats = self.sim.cluster_analyzer.get_cluster_statistics()
            
            print("\n" + "="*80)
            print("SIMULATION SUMMARY".center(80))
            print("="*80)
            print(f"{'Simulated time:':<25} {self.sim.time:.2e} seconds")
            print(f"{'Real time:':<25} {real_time:.2f} seconds")
            print(f"{'Steps completed:':<25} {self.current_step:,}")
            print(f"{'Final coverage:':<25} {final_coverage:.1%}")
            print(f"{'Nucleation events:':<25} {self.sim.nucleation_count}")
            print(f"{'Total clusters:':<25} {cluster_stats.get('total_clusters', 0)}")
            print(f"{'Critical clusters:':<25} {len(cluster_stats.get('critical_clusters', []))}")
            print(f"{'Largest cluster:':<25} {cluster_stats.get('largest_size', 0)}")
            
            print("\nEvent counts:")
            for event, count in self.sim.event_counts.items():
                print(f"  {event+':':<18} {count:,}")
            print("="*80)
            
        except Exception as e:
            print(f"Error printing summary: {str(e)}")

    def toggle_pause(self, _):
        """Toggle pause state with better feedback."""
        if not self.running:
            print("\nStart simulation before pausing")
            return
            
        self.sim.paused = not self.sim.paused
        self.update_button_states()
        status = "PAUSED" if self.sim.paused else "RESUMED"
        print(f"\nSimulation {status}")
        self.status_text.set_text(f"Simulation {status}")

    def reset_simulation(self, _):
        """Reset simulation to initial state with confirmation."""
        print("\n=== Resetting Simulation ===")
        self.running = False
        self.current_step = 0
        self.sim.reset_simulation()
        self._init_simulation_data()
        self.update_button_states()
        self.update_visualization()
        self.status_text.set_text("Simulation reset to initial state")

    def update_button_states(self):
        """Update UI button states with visual feedback."""
        self.start_btn.set_active(not self.running)
        self.pause_btn.label.set_text('Resume' if self.sim.paused else 'Pause')
        self.pause_btn.color = '0.85' if self.sim.paused else 'lightgray'
        self.pause_btn.set_active(self.running)
        self.fig.canvas.draw_idle()

if __name__ == "__main__":
    try:
        app = SimulationApp()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)
    finally:
        import matplotlib.pyplot as plt
        plt.close('all')
        import gc
        gc.collect()