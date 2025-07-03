


# nucleation.py
import math
import random
from typing import Tuple

class NucleationCalculator:
    def __init__(self, T_m: float, L: float, gamma: float, 
                 theta_deg: float, k_B: float):  # Added k_B parameter
        self.T_m = T_m
        self.L = L
        self.gamma = gamma
        self.theta_deg = theta_deg
        self.k_B = k_B  # Store Boltzmann constant

    def compute_undercooling(self, T: float) -> float:
        """Calculate ΔT = T_m - T."""
        return self.T_m - T

    def compute_volume_energy(self, delta_T: float) -> float:
        """Calculate ΔGv = (L*ΔT)/T_m."""
        return (self.L * delta_T) / self.T_m

    def compute_critical_radius(self, delta_Gv: float) -> float:
        """Calculate r* = 2γ/ΔGv."""
        return (2 * self.gamma) / delta_Gv

    def compute_nucleation_barriers(self, delta_T: float) -> Tuple[float, float]:
        """Calculate both homogeneous and heterogeneous barriers."""
        delta_Gv = self.compute_volume_energy(delta_T)
        delta_G_homo = (16 * math.pi * self.gamma**3) / (3 * delta_Gv**2)
        f_theta = self._compute_hetero_factor()
        delta_G_hetero = f_theta * delta_G_homo
        return delta_G_homo, delta_G_hetero

    def compute_nucleation_probability(self, delta_G: float, T: float) -> float:
        """Calculate P = exp(-ΔG/(k_B*T))."""
        return math.exp(-delta_G / (self.k_B * T))  # Use stored k_B

    def _compute_hetero_factor(self) -> float:
        """Calculate f(θ) = (2+cosθ)(1-cosθ)²/4."""
        theta = math.radians(self.theta_deg)
        return (2 + math.cos(theta)) * (1 - math.cos(theta))**2 / 4