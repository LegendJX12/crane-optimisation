"""
sequence.py - Optimise the ORDER in which modules are installed.

Rules (hard constraints)
  * Storey precedence: every module on storey k is installed before any
    module on storey k+1 (floor-by-floor erection, standard PPVC practice).

Why order matters
  With ONE pickup bay every cycle is 'pickup -> module -> back to pickup', so
  the order does not change the time at all (a finding of v2).  Order only
  matters when there are several pickup bays (e.g. one per module type):
  the empty hook then returns to the bay of the NEXT module.

Methods
  index_order      the order the modules are listed in (v1)
  random_order     simulates trucks arriving in random order
  grouped_order    heuristic: per storey, all modules of bay A then bay B,
                   each group swept around the crane by angle
  improve_order    local search (swap + move) from the grouped order
"""
import numpy as np


def _cost(prob, C, pickups, assign_by_row, order):
    prob.set_order(order)
    return prob.evaluate(C, pickups, assign_by_row[order])["total"]


def index_order(prob):
    return np.lexsort((np.arange(prob.N), prob.df["storey"].to_numpy()))


def random_order(prob, rng):
    st = prob.df["storey"].to_numpy()
    return np.lexsort((rng.random(prob.N), st))


def grouped_order(prob, C, assign_by_row):
    st = prob.df["storey"].to_numpy()
    xy = prob.df[["x", "y"]].to_numpy()
    ang = np.arctan2(xy[:, 1] - C[1], xy[:, 0] - C[0])
    # alternate sweep direction per storey/bay so the hook ends near the next start
    return np.lexsort((ang, assign_by_row, st))


def improve_order(prob, C, pickups, assign_by_row, start, iters=4000, seed=0):
    rng = np.random.default_rng(seed)
    st = prob.df["storey"].to_numpy()
    order = np.array(start)
    best = _cost(prob, C, pickups, assign_by_row, order)
    for _ in range(iters):
        i, j = sorted(rng.integers(0, prob.N, 2))
        if i == j or st[order[i]] != st[order[j]]:
            continue                                 # keep storey precedence
        cand = order.copy()
        if rng.random() < 0.5:
            cand[i], cand[j] = cand[j], cand[i]      # swap
        else:
            cand[i:j + 1] = cand[i:j + 1][::-1]      # 2-opt style reversal
        c = _cost(prob, C, pickups, assign_by_row, cand)
        if c < best - 1e-9:
            order, best = cand, c
    prob.set_order(order)
    return order, best
