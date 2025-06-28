import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from constants import COLOR_MAP
from matplotlib.colors import ListedColormap

class CrystalVisualizer:
    def __init__(self):
        self.fig = None
        self.ax = None
        self.color_map = ListedColormap([COLOR_MAP[i] for i in sorted(COLOR_MAP.keys())])
        self._setup_plot_style()

    def _setup_plot_style(self):
        plt.style.use('seaborn-v0_8')
        plt.rcParams.update({
            'font.size': 10,
            'axes.titlesize': 12,
            'axes.labelsize': 10,
            'xtick.labelsize': 8,
            'ytick.labelsize': 8
        })

    def visualize(self, lattice, metrics=None, highlight_defects=True):
        """
        Interactive 3D visualization of crystal growth with real-time metrics
        
        Args:
            lattice: 3D numpy array of atomic positions
            metrics: Dictionary containing:
                - x_events: X-direction diffusion count
                - y_events: Y-direction diffusion count  
                - aspect_ratio: Current X/Y ratio
                - coverage: Surface coverage fraction
            highlight_defects: Whether to emphasize defect sites
        """
        self._create_figure()
        self._plot_atoms(lattice, highlight_defects)
        
        if metrics:
            self._add_annotations(metrics)
        
        self._configure_axes()
        plt.draw()
        plt.pause(0.001)  # Allows for interactive updates

    def _create_figure(self):
        """Initialize or clear the 3D figure"""
        if self.fig is None:
            self.fig = plt.figure(figsize=(12, 8))
            self.ax = self.fig.add_subplot(111, projection='3d')
        else:
            self.ax.clear()

    def _plot_atoms(self, lattice, highlight_defects):
        """Render atomic positions with proper styling"""
        positions = np.argwhere(lattice > 0)
        atom_types = lattice[lattice > 0]
        
        # Size scaling
        sizes = np.where(atom_types == 1, 20, 40)  # Substrate atoms smaller
        
        # Enhanced defect highlighting
        if highlight_defects and 3 in atom_types:
            sizes[atom_types == 3] = 60  # Larger for defects
            edgecolors = np.where(atom_types == 3, 'gold', 'k')
        else:
            edgecolors = 'k'
            
        scatter = self.ax.scatter(
            positions[:, 0],
            positions[:, 1], 
            positions[:, 2],
            c=atom_types,
            cmap=self.color_map,
            s=sizes,
            alpha=0.9,
            edgecolors=edgecolors,
            linewidth=0.8,
            depthshade=True
        )

    def _add_annotations(self, metrics):
        """Display simulation metrics on plot"""
        title = (
    f"X-diffusions: {metrics.get('x_events',0)} | "
    f"Y-diffusions: {metrics.get('y_events',0)} | "
    f"Z-diffusions: {metrics.get('z_events',0)}\n"  # Add this line
    f"Aspect Ratio: {metrics.get('aspect_ratio',1.0):.2f}"
)
        
        self.ax.set_title(title, pad=20)
        self.ax.set_xlabel('X (Fast Axis)', labelpad=12)
        self.ax.set_ylabel('Y (Slow Axis)', labelpad=12)
        self.ax.set_zlabel('Z Growth', labelpad=12)

    def _configure_axes(self):
        """Set optimal viewing parameters"""
        self.ax.grid(True, alpha=0.3)
        self.ax.set_box_aspect([1, 1, 0.7])  # Slight Z compression
        
        # Dynamic viewing angle
        self.ax.view_init(elev=25, azim=45)
        
        # Cleaner tick marks
        self.ax.xaxis.set_major_locator(plt.MaxNLocator(5))
        self.ax.yaxis.set_major_locator(plt.MaxNLocator(5))
        self.ax.zaxis.set_major_locator(plt.MaxNLocator(3))

    def save_animation_frame(self, filename):
        """Save current view to file for animation"""
        self.fig.savefig(filename, dpi=150, bbox_inches='tight')

# Maintain legacy function for compatibility
def visualize_lattice(lattice, x_events=0, y_events=0, aspect_ratio=1.0):
    visualizer = CrystalVisualizer()
    visualizer.visualize(
        lattice,
        metrics={
            'x_events': x_events,
            'y_events': y_events,
            'aspect_ratio': aspect_ratio
        }
    )