import numpy as np
import random
from events import atom_attachment_rate, atom_diffusion_rate, get_neighbors

class KMC_Simulation:
    def __init__(self, lattice_size, temperature):
        self.lattice_size = lattice_size
        self.temperature = temperature
        self.lattice = np.zeros((lattice_size, lattice_size, lattice_size))  # Base metal lattice

    def bkl_kmc_step(self):
        events = []
        total_rate = 0

        # Collect all valid events and their rates
        for x in range(self.lattice.shape[0]):
            for y in range(self.lattice.shape[1]):
                for z in range(self.lattice.shape[2]):
                    attach_rate = atom_attachment_rate((x, y, z), self.lattice, self.temperature)
                    diffuse_rate = atom_diffusion_rate((x, y, z), self.lattice, self.temperature)

                    if attach_rate > 0:
                        events.append(('attach', (x, y, z), attach_rate))
                        total_rate += attach_rate
                    if diffuse_rate > 0:
                        events.append(('diffuse', (x, y, z), diffuse_rate))
                        total_rate += diffuse_rate

        if total_rate == 0 or len(events) == 0:
            return self.lattice, 0, 'none'

        # Time step using exponential waiting time
        time_step = -np.log(random.random()) / total_rate

        # Select event by weighted probability
        probabilities = [e[2] / total_rate for e in events]
        selected_event = random.choices(events, weights=probabilities)[0]
        event_type, (x, y, z), _ = selected_event

        # Execute event
        if event_type == 'attach':
            self.lattice[x, y, z] = 1
        elif event_type == 'diffuse':
            neighbors = get_neighbors((x, y, z), self.lattice)
            vacant_neighbors = [n for n in neighbors if self.lattice[n] == 0]
            if vacant_neighbors:
                nx, ny, nz = random.choice(vacant_neighbors)
                self.lattice[nx, ny, nz] = 1
                self.lattice[x, y, z] = 0

        return self.lattice, time_step, event_type

    def run_simulation(self, num_steps, update_interval=10, visual_callback=None, graph_callback=None):
        total_time = 0

        for step in range(num_steps):
            self.lattice, time_step, event_type = self.bkl_kmc_step()
            total_time += time_step

            if graph_callback and step % update_interval == 0:
                occupied = np.count_nonzero(self.lattice)
                total_sites = self.lattice.size
                unoccupied = total_sites - occupied
                graph_callback(step, occupied, unoccupied, event_type)

            if visual_callback and step % update_interval == 0:
                visual_callback(self.lattice)

            if step % update_interval == 0:
                print(f"Step {step}/{num_steps}, Time: {total_time:.2f} s")

        return self.lattice, total_time
