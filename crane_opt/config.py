"""
config.py - All input parameters in ONE place.

Every number the model uses lives here, so you can change an assumption
without hunting through the code. Each value has a comment saying where it
comes from. Values marked ASSUMED should be replaced with real site data
when you have it.
"""
from dataclasses import dataclass, field, replace
from typing import List, Optional, Tuple


@dataclass
class CraneSpec:
    """One tower crane."""
    name: str = "TC1"
    radius: float = 60.0          # m, max jib reach (v1: 60 m for the 43-module case)
    base_size: float = 5.0        # m, square mast/base footprint (v1)
    no_lift_radius: float = 5.0   # m, no pickup closer than this to the mast (v1)
    slew_speed: float = 0.07      # rad/s  (v1; ~0.67 rpm, typical 0.5-0.8 rpm)
    trolley_speed: float = 1.0    # m/s    (v1 'MOVE_SPEED')
    hoist_speed_loaded: float = 0.6   # m/s (v1 'LIFT_SPEED')
    hoist_speed_empty: float = 0.6    # m/s unloaded hook. v1 used the same value.
    # Load chart: capacity(r) = min(max_load, load_moment / r)
    # ASSUMED illustrative heavy-duty chart (40 t up to 30 m, 20 t at 60 m).
    # Replace with the manufacturer's chart for the real crane.
    max_load_t: float = 40.0
    load_moment_tm: float = 1200.0
    use_load_chart: bool = False  # v1 had no load chart -> off in v1 mode
    mast_height_rank: int = 0     # for multi-crane: higher number = taller crane

    def capacity(self, r):
        import numpy as np
        r = np.maximum(r, 1e-6)
        return np.minimum(self.max_load_t, self.load_moment_tm / r)


@dataclass
class MotionModel:
    """How crane motions combine (Zhang et al., 1999 style).

    alpha: overlap of slewing and trolleying.  1 = one after the other (v1),
           0 = fully simultaneous.
    beta : overlap of horizontal and vertical movement. 1 = sequential (v1).
    """
    alpha: float = 1.0
    beta: float = 1.0
    action_delay: float = 5.0          # s per action (v1 DELAY_TIME)
    delays_delivery: int = 3           # v1: 4 delivery actions -> 3 delays
    delays_return: int = 5             # v1: 1 transition + 4 return delays
    hook_on_time: float = 0.0          # s rigging at pickup  (v1 excluded)
    placement_time: float = 0.0        # s align/secure at destination (v1 excluded)
    v1_vertical: bool = True           # True = v1's fixed 3 m up / 3 m down
    clearance: float = 3.0             # m safety clearance above structure (v1)
    floor_height: float = 2.8          # m storey height (ASSUMED, typical HDB)


@dataclass
class SiteSpec:
    """Site boundary, allowed zones, obstacles."""
    x_range: Tuple[float, float] = (0.0, 100.0)
    y_range: Tuple[float, float] = (0.0, 100.0)
    # Optional allowed sub-areas (v1 ENABLE_AREA_LIMITS). None = whole site.
    crane_x: Optional[Tuple[float, float]] = None
    crane_y: Optional[Tuple[float, float]] = None
    pickup_x: Optional[Tuple[float, float]] = None
    pickup_y: Optional[Tuple[float, float]] = None
    pickup_w: float = 12.0   # m pickup zone (trailer bay) width  (v1)
    pickup_l: float = 5.0    # m pickup zone length (v1)
    # Extra obstacles (existing buildings, hoardings) as rectangles
    # dicts with x, y (centre), width, length
    obstacles: List[dict] = field(default_factory=list)
    # v2 truck-access rule: the pickup bay must sit OUTSIDE the building's
    # outline (convex hull), i.e. not inside a courtyard that trailers cannot
    # drive into once modules are erected. v1 had no such rule.
    pickup_outside_hull: bool = False

    def bounds(self, what):
        """Return (xlo, xhi, ylo, yhi) for 'crane' or 'pickup'."""
        if what == "crane":
            xr = self.crane_x or self.x_range
            yr = self.crane_y or self.y_range
        else:
            xr = self.pickup_x or self.x_range
            yr = self.pickup_y or self.y_range
        return xr[0], xr[1], yr[0], yr[1]


@dataclass
class GASettings:
    pop_size: int = 200          # v1
    generations: int = 500       # v1 (v2 stops early if converged)
    cxpb: float = 0.7            # v1
    mutpb: float = 0.3           # v1
    tournsize: int = 3           # v1
    elitist: bool = True         # v2: (mu+lambda) keeps the best solutions
    patience: int = 60           # (multi-crane GA) stop if no improvement
    islands: int = 8             # v2: number of sub-populations
    island_size: int = 25        # v2: individuals per island (8 x 25 = 200, same as v1)
    island_generations: int = 200  # v2: generations (fewer needed than v1)
    migrate_every: int = 50      # v2: islands swap their best every N generations
    sigma_frac: float = 0.05     # v2: mutation step = 5% of the site width
    penalty: float = 1e3         # v2: seconds of penalty per metre/tonne violated
    seed: int = 42


def v1_settings():
    """Settings that reproduce the original FYP model exactly."""
    return CraneSpec(), MotionModel(), SiteSpec(), GASettings()


def realistic_settings():
    """v2 'realistic' assumptions (all clearly ASSUMED - edit as needed)."""
    crane = CraneSpec(use_load_chart=True, hoist_speed_empty=1.2)
    motion = MotionModel(alpha=0.5, beta=1.0, v1_vertical=False,
                         hook_on_time=300.0, placement_time=900.0)
    site = SiteSpec(pickup_outside_hull=True)
    return crane, motion, site, GASettings()
