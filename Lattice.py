'''import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Define lattice parameters
lattice_size = 10  # Grid size (10x10 for a 2D base layer)
a = 1.0  # Lattice constant (1 Ångström)

# FCC unit cell atom positions (relative to unit cell) for the base layer
fcc_positions = np.array([
    [0, 0, 0],       # Atom 1 at (0, 0, 0)
    [0.5, 0.5, 0],   # Atom 2 at (0.5, 0.5, 0)
    [0.5, 0, 0],     # Atom 3 at (0.5, 0, 0)
    [0, 0.5, 0]      # Atom 4 at (0, 0.5, 0)
])

# Function to initialize the base layer for FCC lattice
def initialize_2d_lattice(lattice_size, a):
    atom_positions = []  # To store atom coordinates

    # Place atoms in the FCC structure for the base layer (only 1 layer)
    for i in range(lattice_size):
        for j in range(lattice_size):
            for pos in fcc_positions:
                # Place atoms at corresponding positions in the 2D base layer (z=0)
                x = (i + pos[0]) * a  # Position of atom in x direction
                y = (j + pos[1]) * a  # Position of atom in y direction
                z = 0  # Keep the z-coordinate at 0 for the base layer
                atom_positions.append([x, y, z])  # Store atom's position

    return np.array(atom_positions)

# Initialize the 2D base lattice (z=0)
atom_positions = initialize_2d_lattice(lattice_size, a)

# 3D Plotting for perspective view
fig = plt.figure(figsize=(10, 10))  # Adjusting the figure size
ax = fig.add_subplot(111, projection='3d')

# Plotting the atoms in 3D (but only on the base layer)
ax.scatter(atom_positions[:, 0], atom_positions[:, 1], atom_positions[:, 2], s=20, color='blue', marker='o')

# Set labels and title for the plot
ax.set_xlabel('X (Å)')
ax.set_ylabel('Y (Å)')
ax.set_zlabel('Z (Å)')
ax.set_title('2D FCC Lattice Base Layer')

# Adjust axis limits (for a flat view of the lattice)
ax.set_xlim(0, lattice_size * a)
ax.set_ylim(0, lattice_size * a)
ax.set_zlim(0, 1)  # Keep z-limits fixed for 2D base layer

# Enable interactive rotation and zoom
plt.show()



import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Define lattice parameters
lattice_size = 10  # Grid size (10x10 for a 2D base layer)
a = 1.0  # Lattice constant (1 Ångström)

# FCC unit cell atom positions (relative to unit cell) for the base layer
fcc_positions = np.array([
    [0, 0, 0],       # Atom 1 at (0, 0, 0)
    [0.5, 0.5, 0],   # Atom 2 at (0.5, 0.5, 0)
    [0.5, 0, 0],     # Atom 3 at (0.5, 0, 0)
    [0, 0.5, 0]      # Atom 4 at (0, 0.5, 0)
])

# Function to initialize the base layer for FCC lattice
def initialize_2d_lattice(lattice_size, a):
    atom_positions = []  # To store atom coordinates

    # Place atoms in the FCC structure for the base layer (only 1 layer)
    for i in range(lattice_size):
        for j in range(lattice_size):
            for pos in fcc_positions:
                # Place atoms at corresponding positions in the 2D base layer (z=0)
                x = (i + pos[0]) * a  # Position of atom in x direction
                y = (j + pos[1]) * a  # Position of atom in y direction
                z = 0  # Keep the z-coordinate at 0 for the base layer
                atom_positions.append([x, y, z])  # Store atom's position

    return np.array(atom_positions)

# Initialize the 2D base lattice (z=0)
atom_positions = initialize_2d_lattice(lattice_size, a)

# 3D Plotting for perspective view
fig = plt.figure(figsize=(10, 10))  # Adjusting the figure size
ax = fig.add_subplot(111, projection='3d')

# Plotting the atoms in 3D (but only on the base layer)
scatter = ax.scatter(atom_positions[:, 0], atom_positions[:, 1], atom_positions[:, 2], s=20, color='blue', marker='o')

# Set labels and title for the plot
ax.set_xlabel('X (Å)')
ax.set_ylabel('Y (Å)')
ax.set_zlabel('Z (Å)')
ax.set_title('2D FCC Lattice Base Layer')

# Adjust axis limits (for a flat view of the lattice)
ax.set_xlim(0, lattice_size * a)
ax.set_ylim(0, lattice_size * a)
ax.set_zlim(0, 1)  # Keep z-limits fixed for 2D base layer

# List to store atoms within each unit cell
unit_cells = {}

# Map unit cell center positions to the atoms inside them
for i in range(lattice_size):
    for j in range(lattice_size):
        unit_cells[(i, j)] = []
        for pos in fcc_positions:
            x = (i + pos[0]) * a
            y = (j + pos[1]) * a
            unit_cells[(i, j)].append([x, y, 0])

# Function to handle click events
def on_click(event):
    # Get the click position in data coordinates
    mouse_x = event.xdata
    mouse_y = event.ydata

    if mouse_x is not None and mouse_y is not None:
        # Find which unit cell the click is closest to
        i = int(mouse_x // a)
        j = int(mouse_y // a)

        if (i, j) in unit_cells:
            # Highlight the atoms inside the clicked unit cell
            atoms_in_unit_cell = unit_cells[(i, j)]

            # Plot the 4 atoms in the clicked unit cell
            for atom in atoms_in_unit_cell:
                ax.scatter(atom[0], atom[1], atom[2], color='green', s=100, marker='o')

            plt.draw()  # Redraw the figure

# Register the click event
fig.canvas.mpl_connect('button_press_event', on_click)

# Enable interactive rotation and zoom
plt.show()
'''


import numpy as np
import random
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import Button

# Constants for the system
A = 1e9  # Reduced Pre-exponential factor (1/s)
E_a = 1.5  # Activation energy (eV)
k_B = 8.617333262145e-5  # Boltzmann constant (eV/K)
T = 300  # Temperature (K)

# Define rate constant using Arrhenius equation
def arrhenius(E_a, T):
    return A * np.exp(-E_a / (k_B * T))

# Event: Atom attaches to an empty site
def atom_attachment_rate(atom_position, lattice, temperature):
    rate = arrhenius(E_a, temperature)
    if lattice[atom_position[0], atom_position[1], atom_position[2]] == 0:
        return rate
    else:
        return 0

# Event: Atom moves (diffusion)
def atom_diffusion_rate(atom_position, lattice, temperature):
    rate = arrhenius(E_a, temperature)
    neighbors = get_neighbors(atom_position, lattice)
    vacant_neighbors = sum([lattice[n[0], n[1], n[2]] == 0 for n in neighbors])
    return rate * vacant_neighbors

# Get neighboring sites
def get_neighbors(position, lattice):
    neighbors = []
    x, y, z = position
    neighbor_positions = [
        (x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z),
        (x, y, z + 1), (x, y, z - 1)
    ]
    for nx, ny, nz in neighbor_positions:
        if 0 <= nx < lattice.shape[0] and 0 <= ny < lattice.shape[1] and 0 <= nz < lattice.shape[2]:
            neighbors.append((nx, ny, nz))
    return neighbors

# BKL KMC Step: Select event (either attachment or diffusion)
def bkl_kmc_step(lattice, temperature):
    events = []
    total_rate = 0

    # Loop through lattice sites to find possible events
    for x in range(lattice.shape[0]):
        for y in range(lattice.shape[1]):
            for z in range(lattice.shape[2]):
                rate_attach = atom_attachment_rate((x, y, z), lattice, temperature)
                rate_diffuse = atom_diffusion_rate((x, y, z), lattice, temperature)

                if rate_attach > 0:
                    events.append(('attach', (x, y, z), rate_attach))
                    total_rate += rate_attach
                if rate_diffuse > 0:
                    events.append(('diffuse', (x, y, z), rate_diffuse))
                    total_rate += rate_diffuse

    if total_rate == 0:
        return lattice, 0  # No events to process

    # Calculate time step (waiting time) based on total rate
    time_step = -np.log(random.random()) / total_rate

    # Choose an event based on its rate
    event_probabilities = [event[2] / total_rate for event in events]
    selected_event = random.choices(events, weights=event_probabilities)[0]

    # Perform the selected event (atom attachment or diffusion)
    if selected_event[0] == 'attach':
        x, y, z = selected_event[1]
        lattice[x, y, z] = 1  # Attach atom to site
    elif selected_event[0] == 'diffuse':
        x, y, z = selected_event[1]
        neighbors = get_neighbors((x, y, z), lattice)
        nx, ny, nz = random.choice(neighbors)
        lattice[nx, ny, nz] = 1  # Move atom to new site
        lattice[x, y, z] = 0  # Empty original site

    return lattice, time_step

# Main simulation loop (KMC for crystal growth)
def run_bkl_kmc_simulation(lattice, temperature, num_steps, update_interval=10):
    total_time = 0
    for step in range(num_steps):
        lattice, time_step = bkl_kmc_step(lattice, temperature)
        total_time += time_step

        # Print progress for each step
        if step % update_interval == 0:
            print(f"Step {step}/{num_steps} completed. Time: {total_time} seconds.")
            visualize_lattice(lattice)
            plt.pause(0.01)  # Pause briefly to update the plot

    return lattice, total_time

# Initialize lattice (pure base metal)
lattice_size = 10  # Use a smaller lattice size for testing
lattice = np.zeros((lattice_size, lattice_size, lattice_size))  # Pure base metal (empty sites)

# Visualize lattice
def visualize_lattice(lattice):
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_box_aspect([1, 1, 1])

    # Define the FCC unit cell positions
    unit_cell_size = 1
    fcc_positions = [(0, 0, 0), (0.5, 0.5, 0), (0.5, 0, 0.5), (0, 0.5, 0.5)]
    colors = ['b'] * len(fcc_positions)

    # Plot each FCC unit cell
    for x in range(lattice.shape[0]):
        for y in range(lattice.shape[1]):
            for z in range(lattice.shape[2]):
                if lattice[x, y, z] == 1:
                    for pos in fcc_positions:
                        ax.scatter(x + pos[0], y + pos[1], z + pos[2], c='b', s=50)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title("FCC Lattice Growth")
    plt.draw()
    plt.pause(0.01)  # Pause briefly to update the plot

# Run simulation for 100 steps at room temperature (300K)
def start_simulation(event):
    global lattice
    print("Starting simulation...")
    lattice = np.zeros((lattice_size, lattice_size, lattice_size))  # Pure base metal
    lattice, total_time = run_bkl_kmc_simulation(lattice, 300, 100)
    visualize_lattice(lattice)
    print(f"Total simulation time: {total_time} seconds")

# Create the figure and axis for visualization
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')

# Visualize initial lattice
visualize_lattice(lattice)

# Add Start Simulation button
ax_start = plt.axes([0.35, 0.02, 0.3, 0.075])  # Position and size of button
button = Button(ax_start, 'Start Simulation')
button.on_clicked(start_simulation)

plt.show()
