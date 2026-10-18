"""
model.py - The physics: how long the crane takes, and which layouts are allowed.

Plain-English summary
---------------------
For every module the crane does one CYCLE:
  1. DELIVERY: hook the module at the pickup bay, lift it, slew (rotate) and
     trolley (move hook in/out along the jib) to the destination, lower it.
  2. RETURN:   lift the empty hook, slew/trolley back to the pickup bay of the
     NEXT module, lower the hook.

Time of a horizontal move (Zhang et al., 1999):
    Ta = slew angle / slew speed          Tr = radial distance / trolley speed
    Th = max(Ta, Tr) + alpha * min(Ta, Tr)
Vertical movement combines with horizontal using beta in the same way.
alpha = beta = 1 means "one motion after another" -> exactly the v1 model.

All functions use numpy 'broadcasting', so the same code evaluates one layout
or millions of layouts at once (used by the grid search).
"""
import numpy as np


def _wrap(a):
    """Smallest absolute angle difference (radians)."""
    return np.abs(np.arctan2(np.sin(a), np.cos(a)))


def _combine(t1, t2, k):
    """Combine two motion times with overlap factor k (1 = sequential)."""
    return np.maximum(t1, t2) + k * np.minimum(t1, t2)


class Problem:
    """Holds the components + crane + motion model, and evaluates layouts."""

    def __init__(self, comps, crane, motion, site, order=None):
        self.df = comps.reset_index(drop=True)
        self.crane, self.motion, self.site = crane, motion, site
        self.N = len(self.df)
        self.order = np.arange(self.N) if order is None else np.asarray(order)
        self._load_arrays()
        # Building footprints (unique on plan) used for overlap checks
        fp = self.df.drop_duplicates(subset=["x", "y", "width", "length"])
        obs = site.obstacles
        self.fp = np.array(
            [[r.x, r.y, r.width, r.length] for r in fp.itertuples()] +
            [[o["x"], o["y"], o["width"], o["length"]] for o in obs], float)
        # Convex hull of all module corners (for the truck-access rule)
        from scipy.spatial import ConvexHull
        b = self.fp[: len(fp)]
        corners = np.concatenate([np.c_[b[:, 0] + sx * b[:, 2] / 2, b[:, 1] + sy * b[:, 3] / 2]
                                  for sx in (-1, 1) for sy in (-1, 1)])
        hull = ConvexHull(corners)
        self.hull_eq = hull.equations            # rows: nx, ny, c  (n.p + c <= 0 inside)
        self.hull_pts = corners[hull.vertices]

    def _load_arrays(self):
        d = self.df.iloc[self.order]
        self.D = d[["x", "y"]].to_numpy(float)          # destinations (N,2)
        self.H = d["height"].to_numpy(float)
        self.W = d["weight_t"].to_numpy(float)
        # slab level of each module's storey (uses the motion model's floor height)
        self.Z = ((d["storey"].to_numpy(float) - 1) * self.motion.floor_height
                  if "storey" in d else np.zeros(self.N))
        self.types = d["type"].to_numpy() if "type" in d else np.array(["m"] * self.N)

    def set_order(self, order):
        self.order = np.asarray(order)
        self._load_arrays()

    # ------------------------------------------------------------------
    # Vertical distances (metres) for each component
    # ------------------------------------------------------------------
    def _vertical(self):
        m = self.motion
        if m.v1_vertical:                      # v1: fixed 3 m up and 3 m down
            up_d = dn_d = up_r = dn_r = np.full(self.N, 3.0)
        else:
            # load hangs below hook; must clear the floor being built + clearance
            up_d = self.Z + self.H + m.clearance      # pickup (ground) -> clear height
            dn_d = self.H + m.clearance               # clear height -> installed
            up_r = self.H + m.clearance               # empty hook back up to clear
            dn_r = self.Z + self.H + m.clearance      # down to ground at pickup
        return up_d, dn_d, up_r, dn_r

    # ------------------------------------------------------------------
    # Core timing (broadcastable).  C: (...,2)  Pd, Pn: (...,N,2)
    # ------------------------------------------------------------------
    def cycle_times(self, C, Pd, Pn, drop_last_return=True):
        cr, m = self.crane, self.motion
        C = np.asarray(C, float)[..., None, :]             # (...,1,2)
        def polar(P):
            v = P - C
            return np.hypot(v[..., 0], v[..., 1]), np.arctan2(v[..., 1], v[..., 0])
        rp, ap = polar(Pd)
        rd, ad = polar(self.D)
        rn, an = polar(Pn)
        up_d, dn_d, up_r, dn_r = self._vertical()
        vl, ve = cr.hoist_speed_loaded, cr.hoist_speed_empty

        # Delivery
        Ta = _wrap(ad - ap) / cr.slew_speed
        Tr = np.abs(rd - rp) / cr.trolley_speed
        Th = _combine(Ta, Tr, m.alpha)
        deliv = _combine(Th, up_d / vl, m.beta) + dn_d / vl
        # Return (to the NEXT module's pickup bay)
        Ta_r = _wrap(an - ad) / cr.slew_speed
        Tr_r = np.abs(rn - rd) / cr.trolley_speed
        Th_r = _combine(Ta_r, Tr_r, m.alpha)
        ret = up_r / ve + _combine(Th_r, dn_r / ve, m.beta)

        last = np.zeros(self.N, bool); last[-1] = drop_last_return  # no return after last
        ret = np.where(last, 0.0, ret)
        delay = (m.delays_delivery * m.action_delay + m.hook_on_time + m.placement_time
                 + np.where(last, 0.0, m.delays_return * m.action_delay))
        return dict(deliv=deliv, ret=ret, delay=np.broadcast_to(delay, deliv.shape),
                    slew=Ta + np.where(last, 0, Ta_r), trolley=Tr + np.where(last, 0, Tr_r),
                    rp=rp, rd=rd)

    # ------------------------------------------------------------------
    # Constraint violations (0 = feasible). Units: metres / tonnes.
    # ------------------------------------------------------------------
    def violations(self, C, P_list):
        """C: (...,2); P_list: list of pickup centres, each (...,2)."""
        cr, st = self.crane, self.site
        C = np.asarray(C, float)
        v = {}
        xlo, xhi, ylo, yhi = st.bounds("crane")
        h = cr.base_size / 2                      # whole mast base must be inside the site
        xlo, xhi = max(xlo, st.x_range[0] + h), min(xhi, st.x_range[1] - h)
        ylo, yhi = max(ylo, st.y_range[0] + h), min(yhi, st.y_range[1] - h)
        v["crane_bounds"] = (np.maximum(0, xlo - C[..., 0]) + np.maximum(0, C[..., 0] - xhi)
                             + np.maximum(0, ylo - C[..., 1]) + np.maximum(0, C[..., 1] - yhi))
        v["crane_overlap"] = self._overlap(C, cr.base_size, cr.base_size)
        reach_d = np.hypot(self.D[:, 0] - C[..., 0, None], self.D[:, 1] - C[..., 1, None])
        v["reach"] = np.maximum(0, reach_d - cr.radius).sum(-1)
        v["pickup_bounds"] = 0.0; v["pickup_overlap"] = 0.0; v["no_lift"] = 0.0
        xlo, xhi, ylo, yhi = st.bounds("pickup")
        h = min(st.pickup_w, st.pickup_l) / 2     # bay (short side) must be inside the site
        xlo, xhi = max(xlo, st.x_range[0] + h), min(xhi, st.x_range[1] - h)
        ylo, yhi = max(ylo, st.y_range[0] + h), min(yhi, st.y_range[1] - h)
        for P in P_list:
            P = np.asarray(P, float)
            v["pickup_bounds"] = v["pickup_bounds"] + (
                np.maximum(0, xlo - P[..., 0]) + np.maximum(0, P[..., 0] - xhi)
                + np.maximum(0, ylo - P[..., 1]) + np.maximum(0, P[..., 1] - yhi))
            ov = np.minimum(self._overlap(P, st.pickup_w, st.pickup_l),
                            self._overlap(P, st.pickup_l, st.pickup_w))   # either orientation
            v["pickup_overlap"] = v["pickup_overlap"] + ov
            dist = np.hypot(P[..., 0] - C[..., 0], P[..., 1] - C[..., 1])
            v["no_lift"] = v["no_lift"] + np.maximum(0, cr.no_lift_radius - dist)
            v["reach"] = v["reach"] + np.maximum(0, dist - cr.radius)
            if st.pickup_outside_hull:
                # signed distance outside the hull (approx.): >0 outside, <0 inside
                sd = (P[..., None, 0] * self.hull_eq[:, 0] + P[..., None, 1] * self.hull_eq[:, 1]
                      + self.hull_eq[:, 2]).max(-1)
                need = min(st.pickup_w, st.pickup_l) / 2
                v["access"] = v.get("access", 0.0) + np.maximum(0, need - sd)
        v["load"] = 0.0
        return v

    def load_violation(self, C, Pd):
        """Tonnes over capacity at destination and pickup radius."""
        if not self.crane.use_load_chart:
            return 0.0
        C = np.asarray(C, float)[..., None, :]
        rd = np.hypot(*np.moveaxis(self.D - C, -1, 0))
        rp = np.hypot(*np.moveaxis(Pd - C, -1, 0))
        cap = np.minimum(self.crane.capacity(rd), self.crane.capacity(rp))
        return np.maximum(0, self.W - cap).sum(-1)

    def _overlap(self, P, w, l):
        """Sum of overlap depth between a w x l box at P and all footprints."""
        P = np.asarray(P, float)
        fx, fy, fw, fl = self.fp.T
        ox = (w + fw) / 2 - np.abs(P[..., 0, None] - fx)
        oy = (l + fl) / 2 - np.abs(P[..., 1, None] - fy)
        return np.minimum(np.maximum(ox, 0), np.maximum(oy, 0)).sum(-1)

    # ------------------------------------------------------------------
    # Convenience: evaluate one layout with K pickup bays
    # ------------------------------------------------------------------
    def pickups_per_component(self, pickups, assign):
        pickups = np.asarray(pickups, float).reshape(-1, 2)
        Pd = pickups[assign]
        Pn = np.vstack([Pd[1:], Pd[-1:]])
        return Pd, Pn

    def evaluate(self, crane_xy, pickups, assign=None, penalty=1e3):
        pickups = np.asarray(pickups, float).reshape(-1, 2)
        if assign is None:
            assign = np.zeros(self.N, int)
        Pd, Pn = self.pickups_per_component(pickups, assign)
        t = self.cycle_times(crane_xy, Pd, Pn)
        v = self.violations(crane_xy, list(pickups))
        v["load"] = self.load_violation(crane_xy, Pd)
        viol = float(sum(np.sum(x) for x in v.values()))
        move = float(t["deliv"].sum() + t["ret"].sum())
        delay = float(t["delay"].sum())
        return dict(total=move + delay, movement=move, delay=delay,
                    slew=float(t["slew"].sum()), trolley=float(t["trolley"].sum()),
                    violation=viol, violations={k: float(np.sum(x)) for k, x in v.items()},
                    feasible=viol < 1e-9, fitness=move + delay + penalty * viol,
                    per_component=t)
