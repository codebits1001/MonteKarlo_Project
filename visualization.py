import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from constants import VISUALIZATION, STATES

class CrystalVisualizer:
    def __init__(self):
        """Initialize the visualizer with enhanced settings."""
        self.cmap = ListedColormap(VISUALIZATION['colors'])
        self.fig = plt.figure(figsize=(12, 9), facecolor='white')
        self.ax = self.fig.add_subplot(111, projection='3d')
        plt.tight_layout()
        self._setup_axes()

    def _setup_axes(self):
        """Configure axes with consistent styling."""
        self.ax.grid(False)
        self.ax.xaxis.pane.fill = False
        self.ax.yaxis.pane.fill = False
        self.ax.zaxis.pane.fill = False
        self.ax.xaxis.pane.set_edgecolor('w')
        self.ax.yaxis.pane.set_edgecolor('w')
        self.ax.zaxis.pane.set_edgecolor('w')

    def visualize_crystal(self, lattice, metrics=None, cluster_map=None, view_angle=None):
        """Render 3D crystal with enhanced visualization features."""
        try:
            self.ax.clear()
            size = lattice.shape[0]
            
            # Prepare grid with proper scaling
            x, y, z = np.indices((size+1, size+1, size+1))
            colors = np.empty(lattice.shape + (4,))
            
            # Apply state colors with better contrast
            for state, color in enumerate(VISUALIZATION['colors']):
                mask = lattice == state
                colors[mask] = self.cmap(state)
                if state == STATES['MOBILE']:  # Enhance mobile atoms
                    colors[mask] = np.array(self.cmap(state)) * [1, 1, 1, 1.2]
            
            # Enhanced cluster highlighting
            if cluster_map is not None:
                self._process_clusters(lattice, colors, cluster_map, metrics)
            
            # Plot voxels with improved rendering
            self._plot_voxels(x, y, z, lattice, colors)
            
            # Add cluster boxes if needed
            if cluster_map is not None:
                self._draw_cluster_boxes(cluster_map)
            
            # Configure view and labels
            self._configure_view(size, view_angle)
            
            # Add metrics with better layout
            if metrics:
                self._add_enhanced_metrics(metrics)
            
            plt.draw()
            plt.pause(0.001)
            
        except Exception as e:
            print(f"Visualization error: {str(e)}")

    def _process_clusters(self, lattice, colors, cluster_map, metrics):
        """Process and highlight clusters with improved visualization."""
        # Highlight all clusters
        cluster_mask = cluster_map > 0
        colors[cluster_mask] = self.cmap(STATES['CLUSTER'])
        
        # Highlight critical clusters with special color
        if metrics and 'critical_clusters' in metrics.get('cluster_stats', {}):
            crit_color = np.array(self.cmap(STATES['NUCLEATION']))
            crit_color[:3] *= 1.3  # Brighter color for critical clusters
            for cluster in metrics['cluster_stats']['critical_clusters']:
                for idx in cluster['indices']:
                    colors[tuple(idx)] = crit_color

    def _plot_voxels(self, x, y, z, lattice, colors):
        """Plot voxels with optimized rendering settings."""
        self.ax.voxels(
            x, y, z, 
            lattice != STATES['EMPTY'],
            facecolors=colors,
            edgecolor='k',
            linewidth=0.15,  # Thinner edges
            alpha=VISUALIZATION['voxel_alpha'],
            shade=True  # Enable shading for better depth perception
        )

    def _configure_view(self, size, view_angle):
        """Configure the 3D view with consistent settings."""
        self.ax.view_init(*(view_angle or VISUALIZATION['view_angle']))
        self.ax.set(
            xlabel='X (nm)', 
            ylabel='Y (nm)', 
            zlabel='Z (nm)',
            xlim=(0, size),
            ylim=(0, size),
            zlim=(0, size)
        )
        self.ax.set_xticks(np.linspace(0, size, 5))
        self.ax.set_yticks(np.linspace(0, size, 5))
        self.ax.set_zticks(np.linspace(0, size, 5))

    def _draw_cluster_boxes(self, cluster_map):
        """Draw bounding boxes around clusters with improved styling."""
        from scipy.ndimage import find_objects
        
        for cluster_slice in find_objects(cluster_map):
            if cluster_slice is None:
                continue
                
            min_coords = [s.start for s in cluster_slice]
            max_coords = [s.stop for s in cluster_slice]
            
            vertices = np.array([
                [min_coords[0], min_coords[1], min_coords[2]],
                [max_coords[0], min_coords[1], min_coords[2]],
                [max_coords[0], max_coords[1], min_coords[2]],
                [min_coords[0], max_coords[1], min_coords[2]],
                [min_coords[0], min_coords[1], max_coords[2]],
                [max_coords[0], min_coords[1], max_coords[2]],
                [max_coords[0], max_coords[1], max_coords[2]],
                [min_coords[0], max_coords[1], max_coords[2]]
            ])
            
            faces = [
                [vertices[0], vertices[1], vertices[2], vertices[3]],
                [vertices[4], vertices[5], vertices[6], vertices[7]],
                [vertices[0], vertices[1], vertices[5], vertices[4]],
                [vertices[2], vertices[3], vertices[7], vertices[6]],
                [vertices[1], vertices[2], vertices[6], vertices[5]],
                [vertices[0], vertices[3], vertices[7], vertices[4]]
            ]
            
            self.ax.add_collection3d(Poly3DCollection(
                faces,
                facecolors=(0.7, 0.2, 0.7, 0.05),  # More transparent
                edgecolors='purple',
                linewidths=1.5,  # Slightly thicker lines
                linestyles=':'
            ))

    def _add_enhanced_metrics(self, metrics):
        """Add simulation metrics with improved layout and styling."""
        # Main title with more information
        self.ax.set_title(
            f"Crystal Growth Simulation\n"
            f"Step: {metrics.get('step', 0):,} | "
            f"Time: {metrics.get('time', 0):.2e} s | "
            f"Coverage: {metrics.get('coverage', 0):.1%}",
            fontsize=12, 
            pad=25,
            loc='left'
        )
        
        # Cluster info box with enhanced metrics
        if 'cluster_stats' in metrics:
            stats = metrics['cluster_stats']
            cluster_text = (
                f"Clusters: {stats.get('total_clusters', 0)}\n"
                f"Critical: {len(stats.get('critical_clusters', []))}\n"
                f"Largest: {stats.get('largest_size', 0)}\n"
                f"Avg Size: {stats.get('avg_size', 0):.1f}"
            )
            self._add_text_box(
                0.02, 0.92, 
                cluster_text,
                fontsize=9,
                bbox_alpha=0.85
            )
        
        # Event counts with better formatting
        if 'events' in metrics:
            event_text = (
                "Event Counts:\n"
                f"Attach: {metrics['events'].get('attach', 0)}\n"
                f"X-diff: {metrics['events'].get('diffuse_x', 0)}\n"
                f"Y-diff: {metrics['events'].get('diffuse_y', 0)}\n"
                f"Z-diff: {metrics['events'].get('diffuse_z', 0)}\n"
                f"Nucleate: {metrics['events'].get('nucleation', 0)}"
            )
            self._add_text_box(
                0.78, 0.92,
                event_text,
                fontsize=9,
                bbox_alpha=0.85
            )

    def _add_text_box(self, x, y, text, fontsize=10, bbox_alpha=0.8):
        """Helper method to add consistent text boxes."""
        self.ax.text2D(
            x, y,
            text,
            transform=self.ax.transAxes,
            bbox=dict(
                facecolor='white',
                alpha=bbox_alpha,
                edgecolor='lightgray',
                boxstyle='round,pad=0.5'
            ),
            fontsize=fontsize,
            verticalalignment='top'
        )

    def save_visualization(self, filename):
        """Save visualization with higher quality settings."""
        try:
            self.fig.savefig(
                filename, 
                dpi=300, 
                bbox_inches='tight',
                facecolor=self.fig.get_facecolor(),
                transparent=False
            )
        except Exception as e:
            print(f"Error saving visualization: {str(e)}")

    def __del__(self):
        """Clean up resources safely."""
        try:
            if hasattr(self, 'fig'):
                plt.close(self.fig)
        except:
            pass