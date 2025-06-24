import matplotlib.pyplot as plt

class RealTimeGraph:
    def __init__(self):
        plt.ion()  # Enable interactive mode for real-time updates

        self.fig, self.axs = plt.subplots(1, 2, figsize=(10, 4))
        self.steps = []
        self.occupied = []
        self.unoccupied = []
        self.attachments = 0
        self.diffusions = 0

        self.bar_labels = ['Attachment', 'Diffusion']
        self.bar_vals = [0, 0]
        self.bar_plot = self.axs[1].bar(self.bar_labels, self.bar_vals, color=['green', 'orange'])

        self.axs[0].set_title("Site Occupancy Over Time")
        self.axs[0].set_xlabel("Step")
        self.axs[0].set_ylabel("Number of Sites")
        self.occupied_plot, = self.axs[0].plot([], [], label="Occupied", color='blue')
        self.unoccupied_plot, = self.axs[0].plot([], [], label="Unoccupied", color='red')
        self.axs[0].legend()
        self.fig.tight_layout()

    def update(self, step, occupied_count, unoccupied_count, event_type):
        self.steps.append(step)
        self.occupied.append(occupied_count)
        self.unoccupied.append(unoccupied_count)

        if event_type == 'attach':
            self.attachments += 1
        elif event_type == 'diffuse':
            self.diffusions += 1

        # Update line plots
        self.occupied_plot.set_data(self.steps, self.occupied)
        self.unoccupied_plot.set_data(self.steps, self.unoccupied)
        self.axs[0].relim()
        self.axs[0].autoscale_view()

        # Update bar plot
        self.bar_vals = [self.attachments, self.diffusions]
        for bar, new_height in zip(self.bar_plot, self.bar_vals):
            bar.set_height(new_height)

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
