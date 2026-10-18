"""
multicrane.py - Two tower cranes working on the same building.

Decision vector x = [c1x, c1y, c2x, c2y, p1x, p1y, p2x, p2y]
  (each crane has its own pickup bay)

How a layout is scored (a small discrete-event simulation)
  1. For every module, compute its cycle time on each crane (and whether the
     crane can reach it / lift its weight).
  2. Floor by floor, share the modules between cranes so both finish at about
     the same time (greedy 'longest job first' balancing).
  3. Modules inside the OVERLAP of the two jib circles are a shared zone:
     only one crane may work there at a time (anti-collision rule), so the
     other crane waits.  Waiting time is recorded.
  4. Next floor starts only when both cranes have finished the current floor.
  Objective = makespan (time until the last module is installed).

Safety constraints
  * Lower crane's jib must not hit the taller crane's mast:
        distance(masts) >= radius_of_lower_crane + clearance   (2 m)
  * Usual rules for each crane (base not on building, pickup bay clear,
    no-lift radius, reach, load chart).
"""
import time, random
import numpy as np
from .model import Problem

MAST_CLEARANCE = 2.0


class TwoCraneProblem:
    def __init__(self, comps, crane1, crane2, motion, site, interference=True):
        self.interference = interference
        self.p = [Problem(comps, crane1, motion, site), Problem(comps, crane2, motion, site)]
        self.N = self.p[0].N
        self.st = comps["storey"].to_numpy()
        self.D = self.p[0].D
        self.cranes = [crane1, crane2]
        self.low = 0 if crane1.mast_height_rank < crane2.mast_height_rank else 1

    def lo_hi(self):
        b1 = self.p[0].site.bounds("crane"); b2 = self.p[0].site.bounds("pickup")
        lo = [b1[0], b1[2]] * 2 + [b2[0], b2[2]] * 2
        hi = [b1[1], b1[3]] * 2 + [b2[1], b2[3]] * 2
        return np.array(lo, float), np.array(hi, float)

    def simulate(self, x, penalty=1e3, detail=False):
        x = np.asarray(x, float)
        C = [x[0:2], x[2:4]]; P = [x[4:6], x[6:8]]
        viol = 0.0
        dur, ok = [], []
        for j in range(2):
            pr = self.p[j]
            Pd = np.broadcast_to(P[j], (self.N, 2))
            t = pr.cycle_times(C[j], Pd, Pd, drop_last_return=False)
            dur.append(t["deliv"] + t["ret"] + t["delay"])
            r = np.hypot(*(self.D - C[j]).T)
            cap = pr.crane.capacity(np.maximum(r, np.hypot(*(P[j] - C[j])))) \
                if pr.crane.use_load_chart else np.inf
            ok.append((r <= pr.crane.radius) & (pr.W <= cap))
            v = pr.violations(C[j], [P[j]])
            v.pop("reach")                       # reach handled per module below
            viol += sum(float(np.sum(a)) for a in v.values())
            # other crane's pickup bay must not overlap this one
        viol += max(0.0, 12.0 - np.hypot(*(P[0] - P[1])))
        sep = np.hypot(*(C[0] - C[1]))
        viol += max(0.0, self.cranes[self.low].radius + MAST_CLEARANCE - sep)
        dur, ok = np.array(dur), np.array(ok)
        unserved = ~(ok[0] | ok[1])
        viol += unserved.sum() * 10.0
        # shared zone: destination reachable by both jibs, or own pickup under other jib
        rd = [np.hypot(*(self.D - C[j]).T) for j in range(2)]
        both = (rd[0] <= self.cranes[0].radius) & (rd[1] <= self.cranes[1].radius)
        pick_under = [np.hypot(*(P[j] - C[1 - j])) <= self.cranes[1 - j].radius for j in range(2)]

        t_now, wait = 0.0, 0.0
        busy = [0.0, 0.0]; count = [0, 0]
        assign = np.full(self.N, -1)
        for s in np.unique(self.st):
            idx = np.where((self.st == s) & ~unserved)[0]
            load = [0.0, 0.0]; queues = [[], []]
            # forced assignments first, then longest-job-first balancing
            for i in idx:
                if ok[0, i] != ok[1, i]:
                    j = 0 if ok[0, i] else 1
                    queues[j].append(i); load[j] += dur[j, i]
            free = [i for i in idx if ok[0, i] and ok[1, i]]
            free.sort(key=lambda i: -min(dur[0, i], dur[1, i]))
            for i in free:
                j = int(np.argmin([load[0] + dur[0, i], load[1] + dur[1, i]]))
                queues[j].append(i); load[j] += dur[j, i]
            # crane 0 does shared jobs first, crane 1 last (staggering)
            for j in range(2):
                sh = lambda i, j=j: bool(both[i] or pick_under[j])
                queues[j].sort(key=lambda i, j=j: (not sh(i)) if j == 0 else sh(i))
            tc = [t_now, t_now]; zone_free = t_now; ptr = [0, 0]
            while ptr[0] < len(queues[0]) or ptr[1] < len(queues[1]):
                cand = [j for j in range(2) if ptr[j] < len(queues[j])]
                j = min(cand, key=lambda k: tc[k])
                i = queues[j][ptr[j]]; ptr[j] += 1
                start = tc[j]
                if self.interference and (both[i] or pick_under[j]):
                    start = max(start, zone_free)
                    zone_free = start + dur[j, i]
                wait += start - tc[j]
                tc[j] = start + dur[j, i]
                busy[j] += dur[j, i]; count[j] += 1; assign[i] = j
            t_now = max(tc)
        fit = t_now + penalty * viol
        if not detail:
            return fit
        return dict(makespan=t_now, wait=wait, busy=busy, count=count, violation=viol,
                    feasible=viol < 1e-9, assign=assign, shared=int(both.sum()), fitness=fit)


def optimise_two_cranes(tp, pop=120, gens=250, seed=0, patience=50):
    """Elitist real-coded GA (same operators as GA v2)."""
    rng = random.Random(seed); np.random.seed(seed)
    lo, hi = tp.lo_hi(); sig = 0.05 * (hi - lo); n = len(lo)
    clip = lambda v: np.minimum(hi, np.maximum(lo, v))
    P = [lo + np.random.rand(n) * (hi - lo) for _ in range(pop)]
    F = [tp.simulate(p) for p in P]
    hist = [min(F)]; t0 = time.time(); stall = 0
    for g in range(gens):
        kids = []
        while len(kids) < pop:
            a, b = [min(rng.sample(range(pop), 3), key=lambda k: F[k]) for _ in range(2)]
            c = P[a].copy()
            if rng.random() < 0.7:                       # blend crossover
                gamma = (1 + 2 * 0.5) * np.random.rand(n) - 0.5
                c = (1 - gamma) * P[a] + gamma * P[b]
            m = np.random.rand(n) < 0.3                  # gaussian mutation
            c = clip(c + m * np.random.randn(n) * sig)
            kids.append(c)
        KF = [tp.simulate(k) for k in kids]
        allP, allF = P + kids, F + KF
        keep = np.argsort(allF)[:pop]
        P = [allP[k] for k in keep]; F = [allF[k] for k in keep]
        stall = stall + 1 if F[0] >= hist[-1] - 1e-9 else 0
        hist.append(F[0])
        if stall >= patience:
            break
    return dict(x=P[0], res=tp.simulate(P[0], detail=True), history=hist,
                seconds=time.time() - t0)
