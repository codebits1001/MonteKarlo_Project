import matplotlib.pyplot as plt

def visualize_lattice(lattice, ax):
    ax.clear()  # Clear existing plot
    
    ax.set_box_aspect([1,1,1])

    fcc_positions = [(0, 0, 0), (0.5, 0.5, 0), (0.5, 0, 0.5), (0, 0.5, 0.5)]

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
    plt.pause(0.01)
