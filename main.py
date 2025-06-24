import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from kmc import KMC_Simulation
from visualization import visualize_lattice

lattice_size = 10
temperature = 300
kmc_simulation = KMC_Simulation(lattice_size, temperature)

# Create figure and axis once
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')

# Visualize initial lattice ONCE
visualize_lattice(kmc_simulation.lattice, ax)

# Define visual update function
def update_plot(lattice):
    visualize_lattice(lattice, ax)

# Define a dummy graph callback (can later be connected to a real graph module)
def graph_callback(step, occupied, unoccupied, event_type):
    print(f"Step {step} | Event: {event_type} | Occupied: {occupied} | Vacant: {unoccupied}")

# Button callback
def start_simulation(event):
    print("Starting simulation...")
    lattice, total_time = kmc_simulation.run_simulation(
        num_steps=100,
        update_interval=1,
        visual_callback=update_plot,
        graph_callback=graph_callback
    )
    print(f"Total simulation time: {total_time:.2f} seconds")

# Button widget
ax_button = plt.axes([0.35, 0.02, 0.3, 0.075])
button = Button(ax_button, 'Start Simulation')
button.on_clicked(start_simulation)

plt.show()


