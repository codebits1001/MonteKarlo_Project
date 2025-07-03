# Variable	                                 Purpose
# self.cluster_labels	           3D array, each atom labeled by its cluster ID
# self.num_clusters	           Number of detected clusters
# self.cluster_sizes	           Dictionary: cluster ID → size
# self.critical_size	           Critical size for nucleation (from energy)

# Function	                             Purpose
# _detect_clusters()	           Detects clusters of type 2 atoms using scipy.ndimage.label()
# _update_cluster_info()	       Calls _detect_clusters, stores cluster sizes, critical ones
# get_nucleated_clusters()       (optional)	Returns info of clusters ≥ critical for visualization


import numpy as np
from scipy.ndimage import label, center_of_mass
from typing import Dict, List
from constants import STRUCTURE_3D, STATES

class ClusterAnalyzer:
    def __init__(self, critical_size: int):
        self.critical_size = critical_size
        self.cluster_labels = None
        self.num_clusters = 0
        self.cluster_sizes: Dict[int, int] = {}
        self.cluster_properties: Dict[int, dict] = {}

    def update_cluster_info(self, lattice: np.ndarray):
        """Detect and analyze clusters in the lattice."""
        binary = (lattice == STATES['MOBILE']).astype(int)
        self.cluster_labels, self.num_clusters = label(binary, structure=STRUCTURE_3D)
        
        self.cluster_sizes.clear()
        self.cluster_properties.clear()
        
        for cluster_id in range(1, self.num_clusters + 1):
            mask = (self.cluster_labels == cluster_id)
            indices = np.argwhere(mask)
            
            self.cluster_sizes[cluster_id] = int(np.sum(mask))
            self.cluster_properties[cluster_id] = {
                'size': self.cluster_sizes[cluster_id],
                'center': center_of_mass(mask),
                'extent': np.ptp(indices, axis=0),
                'indices': indices
            }

    def get_critical_clusters(self) -> List[dict]:
        """Get clusters exceeding critical size."""
        return [
            {'id': cid, **props}
            for cid, props in self.cluster_properties.items()
            if props['size'] >= self.critical_size
        ]

    def get_cluster_statistics(self) -> Dict:
        """Get summary statistics of all clusters."""
        critical = self.get_critical_clusters()
        sizes = list(self.cluster_sizes.values())
        
        return {
            'total_clusters': self.num_clusters,
            'critical_clusters': critical,
            'largest_size': max(sizes) if sizes else 0,
            'size_distribution': {s: sizes.count(s) for s in set(sizes)}
        }