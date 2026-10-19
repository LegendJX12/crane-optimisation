"""Re-run only E5 (sequence + two pickup bays) and update outputs.   python experiments/rerun_e5.py"""
import os, sys, json
import numpy as np, pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT)
from crane_opt.config import realistic_settings, GASettings
from crane_opt.data import load_components
from crane_opt.model import Problem
from crane_opt import optimizers as O
from crane_opt import sequence as S
from crane_opt import plotting as PL
Q = False; OUT = os.path.join(ROOT, "outputs"); FIG = os.path.join(OUT, "figures")
crR, moR, siR, _ = realistic_settings()
compsR = load_components(os.path.join(ROOT, "data", "components_case3.csv"), storeys=12, floor_height=moR.floor_height)
pR = Problem(compsR, crR, moR, siR)
summary = json.load(open(os.path.join(OUT, "summary.json"))); tables = {}
xR = np.array(summary["realistic"]["x"])
def log(m): print(m, flush=True)
# =====================================================================
# E5  Sequence + two pickup bays
# =====================================================================
log("E5 sequence / two bays")
rng = np.random.default_rng(0)
# (a) single bay: order makes (almost) no difference
xs = xR
pR.set_order(S.index_order(pR)); base1 = pR.evaluate(xs[:2], [xs[2:]])["movement"]
rand1 = []
for k in range(20):
    pR.set_order(S.random_order(pR, rng)); rand1.append(pR.evaluate(xs[:2], [xs[2:]])["movement"])
# (b) two bays by module type
assign_row = (compsR["type"].to_numpy() == "small").astype(int)       # large -> bay1, small -> bay2
pR.set_order(S.index_order(pR))
ga2 = O.run_ga(pR, K=2, assign=assign_row[pR.order], settings=GASettings(seed=0))
x2 = ga2["x"]; C2 = x2[:2]; P2 = x2[2:].reshape(-1, 2)
for it in range(2):    # re-optimise positions with the better (grouped) order
    pR.set_order(S.grouped_order(pR, C2, assign_row))
    ga2 = O.run_ga(pR, K=2, assign=assign_row[pR.order], settings=GASettings(seed=it + 1))
    if ga2["res"]["feasible"]:
        x2 = ga2["x"]; C2 = x2[:2]; P2 = x2[2:].reshape(-1, 2)
seq_rows = []
def cost(order):
    pR.set_order(order); return pR.evaluate(C2, P2, assign_row[order])
o_idx = S.index_order(pR); r_idx = cost(o_idx)
r_rand = [cost(S.random_order(pR, rng))["movement"] for _ in range(20)]
o_grp = S.grouped_order(pR, C2, assign_row); r_grp = cost(o_grp)
o_imp, _ = S.improve_order(pR, C2, P2, assign_row, o_grp, iters=500 if Q else 6000)
r_imp = cost(o_imp)
seq_rows += [
    dict(case="1 bay, listed order", movement_h=base1 / 3600, note="v2 realistic optimum layout"),
    dict(case="1 bay, 20 random orders (mean)", movement_h=np.mean(rand1) / 3600,
         note=f"spread max-min = {max(rand1) - min(rand1):.1f} s (order-independent)"),
    dict(case="2 bays, listed order", movement_h=r_idx["movement"] / 3600, note="large/small modules alternate"),
    dict(case="2 bays, random truck order (mean of 20)", movement_h=np.mean(r_rand) / 3600, note=""),
    dict(case="2 bays, grouped by bay (heuristic)", movement_h=r_grp["movement"] / 3600, note=""),
    dict(case="2 bays, optimised order (local search)", movement_h=r_imp["movement"] / 3600, note="storey precedence kept"),
]
tables["E5_sequence"] = pd.DataFrame(seq_rows)
summary["sequence"] = {r["case"]: r["movement_h"] for r in seq_rows}
summary["two_bays_x"] = list(np.round(x2, 2)); summary["two_bays_feasible"] = bool(r_imp["feasible"])
PL.layout(pR, x2, "Two pickup bays (large / small modules)", os.path.join(FIG, "E5_layout_two_bays.png"), K=2,
          note=f"Optimised order: movement {r_imp['movement']/3600:.1f} h")
pR.set_order(S.index_order(pR))


print(tables["E5_sequence"].to_string(index=False)); print("bays", np.round(x2, 2), "feasible", r_imp["feasible"])
with pd.ExcelWriter(os.path.join(OUT, "v2_results.xlsx"), mode="a", if_sheet_exists="replace", engine="openpyxl") as w:
    tables["E5_sequence"].to_excel(w, sheet_name="E5_sequence", index=False)
json.dump(summary, open(os.path.join(OUT, "summary.json"), "w"), indent=2, default=str)
