"""
optimizers.py - Different ways of searching for the best crane + pickup layout.

Decision vector x = [crane_x, crane_y, pickup1_x, pickup1_y, ..., pickupK_x, pickupK_y]

Methods
  run_ga(...)          Genetic algorithm (DEAP). mode='v1' copies the original
                       FYP set-up; mode='v2' is the improved version.
  run_de(...)          Differential evolution (scipy) - a second, independent optimiser
  run_random(...)      Pure random search with the same number of evaluations
  rule_of_thumb(...)   What a planner might do by hand: crane at the centroid
                       of the building, pickup as close to the crane as allowed
  grid_refine(...)     Brute-force 2 m grid of ALL crane x pickup positions,
                       then local polishing = near-certain global optimum (K=1)
"""
import time, random
import numpy as np
from deap import base, creator, tools, algorithms
from scipy.optimize import differential_evolution, minimize

if not hasattr(creator, "FitMin"):
    creator.create("FitMin", base.Fitness, weights=(-1.0,))
    creator.create("Ind", list, fitness=creator.FitMin)


# ----------------------------------------------------------------------
def bounds_vector(prob, K):
    c = prob.site.bounds("crane"); p = prob.site.bounds("pickup")
    lo = [c[0], c[2]] + [p[0], p[2]] * K
    hi = [c[1], c[3]] + [p[1], p[3]] * K
    return np.array(lo, float), np.array(hi, float)


class Objective:
    """Wraps Problem.evaluate and counts how many times it is called."""

    def __init__(self, prob, K=1, assign=None, penalty=1e3, death=False):
        self.prob, self.K, self.penalty, self.death = prob, K, penalty, death
        self.assign = np.zeros(prob.N, int) if assign is None else np.asarray(assign)
        self.n = 0
        self.best = (np.inf, None)

    def __call__(self, x):
        self.n += 1
        x = np.asarray(x, float)
        r = self.prob.evaluate(x[:2], x[2:].reshape(-1, 2), self.assign, self.penalty)
        f = (np.inf if (self.death and not r["feasible"]) else r["fitness"])
        if r["feasible"] and r["total"] < self.best[0]:
            self.best = (r["total"], x.copy())
        return f

    def result(self, x):
        x = np.asarray(x, float)
        return self.prob.evaluate(x[:2], x[2:].reshape(-1, 2), self.assign, self.penalty)


# ----------------------------------------------------------------------
def run_ga(prob, K=1, assign=None, settings=None, mode="v2", verbose=False):
    """Genetic algorithm.

    mode='v1' : exact copy of the original FYP set-up - one population of 200,
                500 generations, no elitism (DEAP eaSimple), infeasible = inf.
    mode='v2' : island model - 8 small populations evolve separately (so they
                explore different parts of the site), keep their 2 best
                (elitism), swap their best member every 50 generations,
                use graded penalties instead of 'inf', repair children that
                leave the site, and finish with a local polish
                (Nelder-Mead) of each island's best.
    """
    from .config import GASettings
    s = settings or GASettings()
    random.seed(s.seed); np.random.seed(s.seed)
    obj = Objective(prob, K, assign, s.penalty, death=(mode == "v1"))
    lo, hi = bounds_vector(prob, K)
    sigma = s.sigma_frac * (hi - lo) if mode == "v2" else np.full(len(lo), 5.0)

    def clip(ind):
        for i in range(len(ind)):
            ind[i] = float(min(hi[i], max(lo[i], ind[i])))
        return ind

    def make():
        if mode == "v1":
            # v1: random integer positions, keep only 'valid looking' ones
            while True:
                x = [random.randint(int(lo[i]), int(hi[i])) for i in range(len(lo))]
                v = prob.violations(x[:2], list(np.reshape(x[2:], (-1, 2))))
                if v["crane_overlap"] == 0 and v["pickup_overlap"] == 0 and v["no_lift"] == 0:
                    return creator.Ind(x)
        return creator.Ind([random.uniform(lo[i], hi[i]) for i in range(len(lo))])

    def mutate(ind, indpb=0.2 if mode == "v1" else 0.3):
        for i in range(len(ind)):
            if random.random() < indpb:
                ind[i] += random.gauss(0, sigma[i])
        return (clip(ind),)

    def mate(a, b):
        tools.cxBlend(a, b, 0.5)
        if mode == "v2":       # v2 repairs children back inside the site
            clip(a); clip(b)
        return a, b

    tb = base.Toolbox()
    tb.register("evaluate", lambda ind: (obj(ind),))
    tb.register("mate", mate)
    tb.register("mutate", mutate)
    tb.register("select", tools.selTournament, tournsize=s.tournsize if mode == "v1" else 2)

    t0 = time.time()
    if mode == "v1":
        islands, size, gens, elite = 1, s.pop_size, s.generations, 0
    else:
        islands, size, gens, elite = s.islands, s.island_size, s.island_generations, 2
    pops = [[make() for _ in range(size)] for _ in range(islands)]
    for P in pops:
        for ind in P:
            ind.fitness.values = tb.evaluate(ind)
    best_ever = None
    best_f = lambda: min(tools.selBest(P, 1)[0].fitness.values[0] for P in pops)
    history = [best_f()]
    for gen in range(gens):
        for j, P in enumerate(pops):
            keep = [tb.clone(e) for e in tools.selBest(P, elite)] if elite else []
            off = algorithms.varAnd(tb.select(P, size - elite), tb, s.cxpb, s.mutpb)
            for ind in off:
                if not ind.fitness.valid:
                    ind.fitness.values = tb.evaluate(ind)
            pops[j] = keep + off
            if mode == "v1":       # v1 kept a Hall of Fame of the best ever
                for ind in off:
                    if ind.fitness.values[0] < history[-1]:
                        history[-1] = ind.fitness.values[0]; best_ever = tb.clone(ind)
        if islands > 1 and gen % s.migrate_every == s.migrate_every - 1:
            tools.migRing(pops, 1, tools.selBest)
        history.append(min(history[-1], best_f()))
    cands = [np.array(tools.selBest(P, 1)[0], float) for P in pops]
    if best_ever is not None:
        cands.append(np.array(best_ever, float))
    if mode == "v2":           # local polish of every island's best
        pol = []
        for x0 in cands:
            r = minimize(obj, x0, method="Nelder-Mead", options=dict(xatol=1e-4, fatol=1e-6, maxiter=3000))
            pol.append(r.x)
        cands = pol
    x = min(cands, key=lambda c: obj(c))
    return dict(method=f"GA ({mode})", x=np.array(x), res=obj.result(x), history=history,
                evals=obj.n, seconds=time.time() - t0, generations=len(history) - 1)


def run_de(prob, K=1, assign=None, seed=0, maxiter=300, penalty=1e3):
    obj = Objective(prob, K, assign, penalty)
    lo, hi = bounds_vector(prob, K)
    t0 = time.time()
    r = differential_evolution(obj, list(zip(lo, hi)), seed=seed, maxiter=maxiter,
                               popsize=15, tol=1e-8, polish=True)
    return dict(method="Differential evolution", x=r.x, res=obj.result(r.x),
                evals=obj.n, seconds=time.time() - t0)


def run_random(prob, K=1, assign=None, n=30000, seed=0, penalty=1e3):
    rng = np.random.default_rng(seed)
    obj = Objective(prob, K, assign, penalty)
    lo, hi = bounds_vector(prob, K)
    t0 = time.time()
    best_f, best_x = np.inf, None
    for _ in range(n):
        x = lo + rng.random(len(lo)) * (hi - lo)
        f = obj(x)
        if f < best_f:
            best_f, best_x = f, x
    return dict(method="Random search", x=best_x, res=obj.result(best_x),
                evals=obj.n, seconds=time.time() - t0)


def _nearest_feasible(prob, target, check, step=0.5, rmax=60):
    """Spiral outwards from `target` until check(point) is True."""
    tx, ty = target
    for r in np.arange(0, rmax, step):
        n = max(8, int(2 * np.pi * r / step))
        cands = [(tx + r * np.cos(a), ty + r * np.sin(a))
                 for a in np.linspace(0, 2 * np.pi, n, endpoint=False)] if r else [(tx, ty)]
        ok = [c for c in cands if check(np.array(c))]
        if ok:
            return np.array(ok[0])
    return np.array(target, float)


def rule_of_thumb(prob, K=1, assign=None, penalty=1e3):
    """Manual planning rule: crane near building centroid, pickup next to crane."""
    obj = Objective(prob, K, assign, penalty)
    cen = prob.D.mean(axis=0)
    def crane_ok(c):
        v = prob.violations(c, [])
        return v["crane_overlap"] + v["reach"] + v["crane_bounds"] == 0
    C = _nearest_feasible(prob, cen, crane_ok)
    pick = []
    for k in range(K):
        def pick_ok(p):
            v = prob.violations(C, [p] + pick)
            return (v["pickup_overlap"] + v["no_lift"] + v["pickup_bounds"] + v["reach"]) == 0
        start = C + np.array([prob.crane.no_lift_radius + 1.0, 0.0])
        pick.append(_nearest_feasible(prob, start, pick_ok))
    x = np.concatenate([C] + pick)
    return dict(method="Rule of thumb (centroid)", x=x, res=obj.result(x), evals=obj.n, seconds=0)


def grid_refine(prob, step=2.0, top=15, penalty=1e3):
    """Exhaustive grid over crane AND pickup positions (single pickup bay)."""
    t0 = time.time()
    cx0, cx1, cy0, cy1 = prob.site.bounds("crane")
    px0, px1, py0, py1 = prob.site.bounds("pickup")
    CX, CY = np.meshgrid(np.arange(cx0, cx1 + 1e-9, step), np.arange(cy0, cy1 + 1e-9, step))
    PX, PY = np.meshgrid(np.arange(px0, px1 + 1e-9, step), np.arange(py0, py1 + 1e-9, step))
    P = np.stack([PX.ravel(), PY.ravel()], -1)                  # (M,2)
    Pd = np.broadcast_to(P[:, None, :], (len(P), prob.N, 2))
    cand = []                                                  # (fitness, x)
    nevals = 0
    for C in np.stack([CX.ravel(), CY.ravel()], -1):
        vc = prob.violations(C, [])
        if vc["crane_overlap"] > 0 or vc["reach"] > 0:       # crane itself infeasible
            continue
        t = prob.cycle_times(C, Pd, Pd)
        v = prob.violations(C, [P])
        load = prob.load_violation(C, Pd)
        tot = (t["deliv"] + t["ret"] + t["delay"]).sum(-1)
        viol = sum(np.asarray(x) for x in v.values()) + load
        f = tot + penalty * viol
        nevals += len(P)
        i = np.argsort(f)[:3]
        cand += [(f[j], np.concatenate([C, P[j]])) for j in i]
    cand.sort(key=lambda c: c[0])
    obj = Objective(prob, 1, None, penalty)
    best = None
    for f0, x0 in cand[:top]:          # polish the best grid points
        r = minimize(obj, x0, method="Nelder-Mead",
                     options=dict(xatol=1e-4, fatol=1e-6, maxiter=4000))
        if best is None or r.fun < best[0]:
            best = (r.fun, r.x)
    return dict(method=f"Grid {step} m + polish", x=best[1], res=obj.result(best[1]),
                evals=nevals + obj.n, seconds=time.time() - t0)
