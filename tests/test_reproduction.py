"""
Test 1: does v2 give EXACTLY the same time as the original v1 code
when run with v1 assumptions?  (This proves the new engine is a faithful
upgrade, not a different model.)

Run:  python -m pytest tests -q      (or)   python tests/test_reproduction.py
"""
import os, sys, re, random
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from crane_opt.config import v1_settings
from crane_opt.data import load_components
from crane_opt.model import Problem

V1_FILE = os.path.join(ROOT, "legacy", "copy 22.py")


def load_v1_functions():
    """Run only the function definitions of the v1 script (not its GA)."""
    src = open(V1_FILE, encoding="utf-8").read()
    src = src.split("# Setup the DEAP toolbox")[0]
    ns = {}
    exec(compile(src, V1_FILE, "exec"), ns)
    return ns


def test_v2_matches_v1():
    v1 = load_v1_functions()
    crane, motion, site, _ = v1_settings()
    comps = load_components(os.path.join(ROOT, "data", "components_case3.csv"))
    prob = Problem(comps, crane, motion, site)
    rng = random.Random(0)
    checked = 0
    while checked < 200:
        ind = [rng.uniform(20, 80) for _ in range(4)]
        out = v1["evaluate_with_timings"](ind)
        if not np.isfinite(out[0]):
            continue
        r2 = prob.evaluate(ind[:2], [ind[2:]])
        assert abs(r2["total"] - out[0]) < 1e-6, (ind, r2["total"], out[0])
        assert abs(r2["delay"] - out[2]) < 1e-9
        checked += 1
    print(f"OK - v2 matches v1 to 1e-6 s on {checked} random feasible layouts")


if __name__ == "__main__":
    test_v2_matches_v1()
