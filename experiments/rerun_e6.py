"""Re-run only E6 (two cranes) and update outputs/v2_results.xlsx + figure.
    python experiments/rerun_e6.py
"""
import os, sys, json
import numpy as np, pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT)
from dataclasses import replace
from crane_opt.config import realistic_settings
from crane_opt.data import load_components
from crane_opt.model import Problem
from crane_opt.multicrane import TwoCraneProblem, optimise_two_cranes
from crane_opt import plotting as PL
OUT = os.path.join(ROOT, "outputs"); FIG = os.path.join(OUT, "figures")
crR, moR, siR, _ = realistic_settings()
comps = load_components(os.path.join(ROOT, "data", "components_case3.csv"), storeys=12, floor_height=moR.floor_height)
summ = json.load(open(os.path.join(OUT, "summary.json")))
xR = np.array(summ["realistic"]["x"]); single_h = summ["realistic"]["total_h"]
c1 = replace(crR, name="TC1", mast_height_rank=1)
c2 = replace(crR, name="TC2", radius=45.0, max_load_t=25.0, load_moment_tm=900.0, mast_height_rank=0)
rows = [dict(case="1 crane (v2 optimum)", makespan_h=single_h, waiting_h=0, TC1_lifts=len(comps), TC2_lifts=0,
             TC1_util=1.0, TC2_util=0.0, feasible=True, layout=str(np.round(xR, 1)))]
best = None
for interf in (True, False):
    tp = TwoCraneProblem(comps, c1, c2, moR, siR, interference=interf)
    rs = [optimise_two_cranes(tp, pop=120, gens=250, seed=s) for s in range(3)]
    b = min(rs, key=lambda r: r["res"]["fitness"]); r = b["res"]
    print(interf, round(r["makespan"] / 3600, 2), r["feasible"], r["violation"], np.round(b["x"], 1), flush=True)
    if interf: best = (tp, b)
    rows.append(dict(case="2 cranes, shared-zone lock" if interf else "2 cranes, no interference (ideal bound)",
                     makespan_h=r["makespan"] / 3600, waiting_h=r["wait"] / 3600, TC1_lifts=r["count"][0], TC2_lifts=r["count"][1],
                     TC1_util=r["busy"][0] / r["makespan"], TC2_util=r["busy"][1] / r["makespan"], feasible=bool(r["feasible"]),
                     layout=str(np.round(b["x"], 1))))
df = pd.DataFrame(rows); print(df.to_string(index=False))
xl = os.path.join(OUT, "v2_results.xlsx")
with pd.ExcelWriter(xl, mode="a", if_sheet_exists="replace", engine="openpyxl") as w:
    df.to_excel(w, sheet_name="E6_two_cranes", index=False)
summ["two_cranes"] = rows
json.dump(summ, open(os.path.join(OUT, "summary.json"), "w"), indent=2, default=str)
tp, b = best
PL.layout(tp.p[0], b["x"], "Two-crane layout (shared zone = overlap of jib circles)", os.path.join(FIG, "E6_layout_two_cranes.png"),
          cranes=[c1, c2], note=f"Makespan {b['res']['makespan']/3600:.1f} h vs {single_h:.1f} h with one crane")
