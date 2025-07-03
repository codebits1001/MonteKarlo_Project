import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List
from constants import VISUALIZATION

class GraphVisualizer:
    def __init__(self):
        sns.set_theme(style="whitegrid", palette=VISUALIZATION['colors'])
        self.figures = []

    def create_growth_plot(self, time_data: List[float], 
                         coverage_data: List[float],
                         aspect_ratios: List[float] = None):
        """Create coverage vs time plot with optional aspect ratio."""
        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        # Plot coverage
        sns.lineplot(x=time_data, y=coverage_data, ax=ax1,
                    color=VISUALIZATION['colors'][2], label='Coverage')
        ax1.set_xlabel("Simulation Time (s)")
        ax1.set_ylabel("Surface Coverage", color=VISUALIZATION['colors'][2])
        ax1.tick_params(axis='y', labelcolor=VISUALIZATION['colors'][2])
        
        # Add aspect ratio if provided
        if aspect_ratios:
            ax2 = ax1.twinx()
            sns.lineplot(x=time_data, y=aspect_ratios, ax=ax2,
                        color=VISUALIZATION['colors'][5], label='Aspect Ratio')
            ax2.set_ylabel("Aspect Ratio", color=VISUALIZATION['colors'][5])
            ax2.tick_params(axis='y', labelcolor=VISUALIZATION['colors'][5])
        
        ax1.set_title("Crystal Growth Kinetics")
        ax1.grid(True, linestyle='--', alpha=0.7)
        self.figures.append(fig)
        return fig

    def create_event_plot(self, time_data: List[float], 
                        event_counts: Dict[str, List[int]]):
        """Create event distribution plot."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for event, counts in event_counts.items():
            if sum(counts) > 0:  # Only plot if events occurred
                sns.lineplot(x=time_data, y=counts, ax=ax,
                            label=event.replace('_', ' ').title())
        
        ax.set_title("Event Distribution Over Time")
        ax.set_xlabel("Simulation Time (s)")
        ax.set_ylabel("Event Count")
        ax.legend(title="Event Type")
        ax.grid(True, linestyle='--', alpha=0.7)
        self.figures.append(fig)
        return fig

    def save_plot(self, filename: str):
        """Save most recent plot to file."""
        if self.figures:
            self.figures[-1].savefig(filename, bbox_inches='tight', dpi=300)

    def close(self):
        """Close all plot figures safely."""
        import matplotlib.pyplot as plt
        for fig in self.figures:
            try:
                plt.close(fig)
            except:
                pass
        self.figures = []
        plt.close('all')  # Ensure all figures are closed