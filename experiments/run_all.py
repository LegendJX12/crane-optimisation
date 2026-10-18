"""
run_all.py - Runs every v2 experiment and saves tables + figures to outputs/.

    python experiments/run_all.py            # full run  (~30-40 min)
    python experiments/run_all.py --quick    # fast check (~3 min, fewer seeds)

Experiments
  E1  Reproduce v1 exactly (validation)
  E2  Algorithm benchmark on the v1 model (GA v1 vs GA v2 vs DE vs random
      vs rule-of-thumb vs exhaustive grid = global optimum)
  E3  Truck-access rule (pickup outside the building outline)
  E4  Realistic 12-storey model (3D hoisting, load chart, handling times)
  E5  Installation sequence + two pickup bays
  E6  Two tower cranes with anti-collision shared zone
  E7  Sensitivity analysis (tornado)
  E8  Machine-learning surrogate (fast estimator of crane time)
"""
import os, sys, json, time, argparse, copy
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from dataclasses import replace
from crane_opt.config import v1_settings, realistic_settings, GASettings, CraneSpec
from crane_opt.data import load_components
from crane_opt.model import Problem
from crane_opt import optimizers as O
from crane_opt import sequence as S
from crane_opt import plotting as PL
from crane_opt.multicrane import TwoCraneProblem, optimise_two_cranes

ap = argparse.ArgumentParser()
ap.add_argument("--quick", action="store_true")
args = ap.parse_args()
Q = args.quick
SEEDS = 4 if Q else 20
OUT = os.path.join(ROOT, "outputs"); FIG = os.path.join(OUT, "figures")
os.makedirs(FIG, exist_ok=True)
CSV = os.path.join(ROOT, "data", "components_case3.csv")
STOREYS = 3 if Q else 12
tables, summary = {}, {}
T0 = time.time()


def log(msg):
    print(f"[{time.time() - T0:6.0f}s] {msg}", flush=True)


def row(r, extra=None):
    d = dict(method=r["method"], crane_x=r["x"][0], crane_y=r["x"][1],
             pickup_x=r["x"][2], pickup_y=r["x"][3], total_s=r["res"]["total"],
             movement_s=r["res"]["movement"], delay_s=r["res"]["delay"],
             feasible=r["res"]["feasible"], evaluations=r["evals"], runtime_s=r["seconds"])
    d.update(extra or {})
    return d


# =====================================================================
# E1 + E2  v1 model: reproduction and algorithm benchmark
# =====================================================================
log("E1/E2 v1 model benchmark")
cr, mo, si, ga = v1_settings()
comps1 = load_components(CSV)
p1 = Problem(comps1, cr, mo, si)
grid_step = 2.0 if Q else 1.0
G = O.grid_refine(p1, step=grid_step)
ref = G["res"]["total"]
log(f"  grid optimum {ref:.2f} at {np.round(G['x'], 2)}")
rot = O.rule_of_thumb(p1)
runs = {"GA v1 (original set-up)": [], "GA v2 (improved)": [], "Differential evolution": [], "Random search": []}
hist = {"GA v1 (original set-up)": [], "GA v2 (improved)": []}
for s in range(SEEDS):
    gs = GASettings(seed=s, generations=150 if Q else 500)
    a = O.run_ga(p1, settings=gs, mode="v1"); runs["GA v1 (original set-up)"].append(a); hist["GA v1 (original set-up)"].append(a["history"])
    b = O.run_ga(p1, settings=gs, mode="v2"); runs["GA v2 (improved)"].append(b); hist["GA v2 (improved)"].append(b["history"])
    runs["Differential evolution"].append(O.run_de(p1, seed=s, maxiter=150 if Q else 300))
    runs["Random search"].append(O.run_random(p1, seed=s, n=int(np.median([b["evals"]]))))
    log(f"  seed {s}: GAv1 {a['res']['total']:.1f}  GAv2 {b['res']['total']:.1f}  DE {runs['Differential evolution'][-1]['res']['total']:.1f}")
bench = []
for name, rs in runs.items():
    t = np.array([r["res"]["total"] if r["res"]["feasible"] else np.nan for r in rs])
    bench.append(dict(method=name, runs=len(rs), best_s=np.nanmin(t), mean_s=np.nanmean(t),
                      std_s=np.nanstd(t), worst_s=np.nanmax(t),
                      hit_global_within_0_5pct=f"{np.mean(t <= ref * 1.005) * 100:.0f}%",
                      mean_gap_to_global=f"{(np.nanmean(t) / ref - 1) * 100:.2f}%",
                      mean_evaluations=np.mean([r["evals"] for r in rs]),
                      mean_runtime_s=np.mean([r["seconds"] for r in rs])))
bench.append(dict(method="Rule of thumb (centroid)", runs=1, best_s=rot["res"]["total"], mean_s=rot["res"]["total"],
                  std_s=0, worst_s=rot["res"]["total"], hit_global_within_0_5pct="-",
                  mean_gap_to_global=f"{(rot['res']['total'] / ref - 1) * 100:.2f}%", mean_evaluations=0, mean_runtime_s=0))
bench.append(dict(method=G["method"] + " (reference)", runs=1, best_s=ref, mean_s=ref, std_s=0, worst_s=ref,
                  hit_global_within_0_5pct="-", mean_gap_to_global="0.00%",
                  mean_evaluations=G["evals"], mean_runtime_s=G["seconds"]))
tables["E2_benchmark_v1model"] = pd.DataFrame(bench)
v1_report_x = np.array([63.0, 5.88, 33.87, 41.5])          # reproduces report Table 3 (3942.93 s)
v1r = p1.evaluate(v1_report_x[:2], [v1_report_x[2:]])
tables["E1_reproduction"] = pd.DataFrame([
    dict(item="Report Table 3, 43 modules, best total (s)", value=3942.930),
    dict(item="v2 engine at the v1 optimum (s)", value=round(v1r["total"], 3)),
    dict(item="v2 engine delay at that layout (s)", value=v1r["delay"]),
    dict(item="Max |v2 - v1| over 200 random layouts (s)", value="< 1e-6 (tests/test_reproduction.py)"),
])
summary["v1_report_total"] = 3942.93
summary["global_opt_v1model"] = dict(total=ref, x=list(np.round(G["x"], 2)), improvement_vs_report_pct=(1 - ref / 3942.93) * 100)
summary["rule_of_thumb_v1model"] = dict(total=rot["res"]["total"], x=list(np.round(rot["x"], 2)))
PL.convergence(list(hist.values()), list(hist.keys()), os.path.join(FIG, "E2_convergence.png"), ref=ref)
PL.benchmark_box([[r["res"]["total"] for r in rs] for rs in runs.values()], list(runs.keys()),
                 os.path.join(FIG, "E2_benchmark_box.png"), ref=ref,
                 title=f"{SEEDS} independent runs per method (43 modules, v1 model)")
PL.layout(p1, v1_report_x, "v1 report optimum (3942.9 s) - GA local optimum", os.path.join(FIG, "E1_layout_v1_report.png"),
          note="Pickup bay sits inside the L-shaped courtyard")
PL.layout(p1, G["x"], f"Global optimum, v1 model ({ref:.1f} s)", os.path.join(FIG, "E2_layout_global.png"),
          note="Found by exhaustive grid + polishing")

# =====================================================================
# E3  Truck-access rule
# =====================================================================
log("E3 access rule")
si_acc = replace(si, pickup_outside_hull=True)
p3 = Problem(comps1, cr, mo, si_acc)
G3 = O.grid_refine(p3, step=grid_step)
ga3 = O.run_ga(p3, settings=GASettings(seed=0))
summary["access_opt_v1model"] = dict(total=G3["res"]["total"], x=list(np.round(G3["x"], 2)),
                                     ga_total=ga3["res"]["total"])
v_rep = p3.evaluate(v1_report_x[:2], [v1_report_x[2:]])
tables["E3_access_rule"] = pd.DataFrame([
    row(G, dict(scenario="No access rule (v1)")),
    dict(row(dict(method="v1 report layout", x=v1_report_x, res=v_rep, evals=0, seconds=0)),
         scenario="v1 layout checked with access rule", violations=str({k: round(v, 2) for k, v in v_rep["violations"].items() if v > 0})),
    row(G3, dict(scenario="With access rule (grid)")),
    row(ga3, dict(scenario="With access rule (GA v2)")),
])
PL.layout(p3, G3["x"], f"Optimum with truck-access rule ({G3['res']['total']:.1f} s)",
          os.path.join(FIG, "E3_layout_access.png"), note="Pickup bay must be outside the building outline")

# =====================================================================
# E4  Realistic multi-storey model
# =====================================================================
log(f"E4 realistic model, {STOREYS} storeys")
crR, moR, siR, _ = realistic_settings()
compsR = load_components(CSV, storeys=STOREYS, floor_height=moR.floor_height)
pR = Problem(compsR, crR, moR, siR)
GR = O.grid_refine(pR, step=2.5 if not Q else 4.0)
gaR = O.run_ga(pR, settings=GASettings(seed=0))
rotR = O.rule_of_thumb(pR)
xR = GR["x"] if GR["res"]["fitness"] <= gaR["res"]["fitness"] else gaR["x"]
resR = pR.evaluate(xR[:2], [xR[2:]])
# v1-optimal layout judged under the realistic model
v1_in_R = pR.evaluate(v1_report_x[:2], [v1_report_x[2:]])
glob_in_R = pR.evaluate(G["x"][:2], [G["x"][2:]])
fixed_per = moR.hook_on_time + moR.placement_time
def brk(r):
    n = pR.N
    return {"Crane movement (hoist, slew, trolley)": r["movement"],
            "Signal delays": r["delay"] - n * fixed_per, "Hook-on + placement": n * fixed_per}
# note: with alpha<1 slew+trolley overlap, so 'Hoist/lower + overlap' can be smaller than pure hoist
tables["E4_realistic"] = pd.DataFrame([
    dict(layout="v2 optimum (realistic)", crane_x=xR[0], crane_y=xR[1], pickup_x=xR[2], pickup_y=xR[3],
         total_h=resR["total"] / 3600, movement_h=resR["movement"] / 3600, feasible=resR["feasible"],
         violations=""),
    dict(layout="GA v2 check", crane_x=gaR["x"][0], crane_y=gaR["x"][1], pickup_x=gaR["x"][2], pickup_y=gaR["x"][3],
         total_h=gaR["res"]["total"] / 3600, movement_h=gaR["res"]["movement"] / 3600, feasible=gaR["res"]["feasible"], violations=""),
    dict(layout="Rule of thumb", crane_x=rotR["x"][0], crane_y=rotR["x"][1], pickup_x=rotR["x"][2], pickup_y=rotR["x"][3],
         total_h=rotR["res"]["total"] / 3600, movement_h=rotR["res"]["movement"] / 3600, feasible=rotR["res"]["feasible"],
         violations=str({k: round(v, 1) for k, v in rotR["res"]["violations"].items() if v > 0})),
    dict(layout="v1 report layout", crane_x=v1_report_x[0], crane_y=v1_report_x[1], pickup_x=v1_report_x[2], pickup_y=v1_report_x[3],
         total_h=v1_in_R["total"] / 3600, movement_h=v1_in_R["movement"] / 3600, feasible=v1_in_R["feasible"],
         violations=str({k: round(v, 1) for k, v in v1_in_R["violations"].items() if v > 0})),
    dict(layout="v1-model global optimum", crane_x=G["x"][0], crane_y=G["x"][1], pickup_x=G["x"][2], pickup_y=G["x"][3],
         total_h=glob_in_R["total"] / 3600, movement_h=glob_in_R["movement"] / 3600, feasible=glob_in_R["feasible"],
         violations=str({k: round(v, 1) for k, v in glob_in_R["violations"].items() if v > 0})),
])
summary["realistic"] = dict(storeys=STOREYS, modules=pR.N, total_h=resR["total"] / 3600, movement_h=resR["movement"] / 3600,
                            x=list(np.round(xR, 2)), rule_movement_h=rotR["res"]["movement"] / 3600,
                            rule_feasible=bool(rotR["res"]["feasible"]))
PL.stacked_breakdown([("v2 optimum", brk(resR)), ("Rule of thumb", brk(rotR["res"]))],
                     os.path.join(FIG, "E4_time_breakdown.png"), f"Where the crane time goes ({STOREYS} storeys, {pR.N} lifts)")
PL.layout(pR, xR, f"Realistic model optimum - {STOREYS} storeys, load chart, access rule",
          os.path.join(FIG, "E4_layout_realistic.png"),
          note=f"Movement {resR['movement']/3600:.1f} h of {resR['total']/3600:.1f} h total")

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

# =====================================================================
# E6  Two cranes
# =====================================================================
log("E6 two cranes")
c1 = replace(crR, name="TC1", mast_height_rank=1)
c2 = replace(crR, name="TC2", radius=45.0, max_load_t=25.0, load_moment_tm=900.0, mast_height_rank=0)
mc_rows = []
best2 = None
for interf in (True, False):
    tp = TwoCraneProblem(compsR, c1, c2, moR, siR, interference=interf)
    rs = [optimise_two_cranes(tp, pop=60 if Q else 120, gens=60 if Q else 250, seed=s) for s in range(1 if Q else 3)]
    b = min(rs, key=lambda r: r["res"]["fitness"])
    if interf:
        best2 = (tp, b)
    mc_rows.append(dict(case="2 cranes, shared-zone lock" if interf else "2 cranes, no interference (ideal bound)",
                        makespan_h=b["res"]["makespan"] / 3600, waiting_h=b["res"]["wait"] / 3600,
                        TC1_lifts=b["res"]["count"][0], TC2_lifts=b["res"]["count"][1],
                        TC1_util=b["res"]["busy"][0] / b["res"]["makespan"], TC2_util=b["res"]["busy"][1] / b["res"]["makespan"],
                        feasible=b["res"]["feasible"], layout=str(np.round(b["x"], 1))))
mc_rows.insert(0, dict(case="1 crane (v2 optimum)", makespan_h=resR["total"] / 3600, waiting_h=0,
                       TC1_lifts=pR.N, TC2_lifts=0, TC1_util=1.0, TC2_util=0, feasible=resR["feasible"], layout=str(np.round(xR, 1))))
tables["E6_two_cranes"] = pd.DataFrame(mc_rows)
summary["two_cranes"] = mc_rows
tp, b = best2
PL.layout(tp.p[0], b["x"], "Two-crane layout (shared zone = overlap of jib circles)",
          os.path.join(FIG, "E6_layout_two_cranes.png"), cranes=[c1, c2],
          note=f"Makespan {b['res']['makespan']/3600:.1f} h vs {resR['total']/3600:.1f} h with one crane")

# =====================================================================
# E7  Sensitivity (re-optimised for each change)
# =====================================================================
log("E7 sensitivity")
def opt_move(crane, motion):
    pp = Problem(compsR, crane, motion, siR)
    r = O.run_ga(pp, settings=GASettings(seed=0, patience=40))
    return r["res"]["movement"]
baseM = opt_move(crR, moR)
sens = []
tests = [("Slew speed", "crane", "slew_speed"), ("Trolley speed", "crane", "trolley_speed"),
         ("Hoist speed (loaded)", "crane", "hoist_speed_loaded"), ("Hoist speed (empty)", "crane", "hoist_speed_empty"),
         ("Signal delay per action", "motion", "action_delay"), ("Slew/trolley overlap alpha", "motion", "alpha"),
         ("Floor height", "motion", "floor_height")]
for lab, which, attr in tests:
    vals = []
    for f in (0.8, 1.2):
        if which == "crane":
            vals.append(opt_move(replace(crR, **{attr: getattr(crR, attr) * f}), moR))
        else:
            vals.append(opt_move(crR, replace(moR, **{attr: getattr(moR, attr) * f})))
    sens.append((lab, vals[0], vals[1]))
tables["E7_sensitivity"] = pd.DataFrame([dict(parameter=l, movement_h_minus20=a / 3600, movement_h_plus20=b / 3600,
                                              change_minus20_pct=(a / baseM - 1) * 100, change_plus20_pct=(b / baseM - 1) * 100)
                                         for l, a, b in sens])
PL.tornado(sens, baseM, os.path.join(FIG, "E7_tornado.png"), "Sensitivity of optimal crane movement time (+/-20%)")
# check of report claim: slew 0.07 -> 0.05 rad/s in the v1 model
p_slow = Problem(comps1, replace(cr, slew_speed=0.05), mo, si)
g_slow = O.grid_refine(p_slow, step=2.0)
summary["v1_slew_0.05_change_pct"] = (g_slow["res"]["total"] / O.grid_refine(p1, step=2.0)["res"]["total"] - 1) * 100

# =====================================================================
# E8  ML surrogate
# =====================================================================
log("E8 ML surrogate")
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_percentage_error
lo, hi = O.bounds_vector(pR, 1)
Xs, ys = [], []
rngm = np.random.default_rng(1)
while len(Xs) < (800 if Q else 4000):
    x = lo + rngm.random(4) * (hi - lo)
    r = pR.evaluate(x[:2], [x[2:]])
    if r["feasible"]:
        Xs.append(x); ys.append(r["movement"])
Xs, ys = np.array(Xs), np.array(ys)
def feats(X):
    d = np.hypot(X[:, 0] - X[:, 2], X[:, 1] - X[:, 3])
    cen = pR.D.mean(0)
    dc = np.hypot(X[:, 0] - cen[0], X[:, 1] - cen[1]); dp = np.hypot(X[:, 2] - cen[0], X[:, 3] - cen[1])
    return np.c_[X, d, dc, dp]
Xtr, Xte, ytr, yte = train_test_split(feats(Xs), ys, test_size=0.25, random_state=0)
ml_rows = []
for name, mdl in [("Gradient boosting", GradientBoostingRegressor(n_estimators=400, max_depth=4, random_state=0)),
                  ("Neural network (MLP)", MLPRegressor(hidden_layer_sizes=(64, 64), max_iter=3000, random_state=0))]:
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    pipe = make_pipeline(StandardScaler(), mdl)
    t = time.time(); pipe.fit(Xtr, ytr); tfit = time.time() - t
    yh = pipe.predict(Xte)
    t = time.time(); pipe.predict(Xte); tpred = (time.time() - t) / len(Xte)
    ml_rows.append(dict(model=name, R2=r2_score(yte, yh), MAPE_pct=mean_absolute_percentage_error(yte, yh) * 100,
                        fit_s=tfit, predict_ms_per_layout=tpred * 1000))
    if name == "Gradient boosting":
        PL.parity(yte, yh, os.path.join(FIG, "E8_surrogate_parity.png"), f"Surrogate (GB): R2 = {r2_score(yte, yh):.3f}")
        # use surrogate to pick the best of 50k random layouts, then check with simulator
        cand = lo + rngm.random((50000, 4)) * (hi - lo)
        pred = pipe.predict(feats(cand)); order = np.argsort(pred)
        for j in order:
            rr = pR.evaluate(cand[j][:2], [cand[j][2:]])
            if rr["feasible"]:
                summary["surrogate_pick_gap_pct"] = (rr["movement"] / resR["movement"] - 1) * 100
                break
t = time.time(); [pR.evaluate(x[:2], [x[2:]]) for x in Xs[:200]]
ml_rows.append(dict(model="Physics simulator (reference)", R2=1.0, MAPE_pct=0, fit_s=0,
                    predict_ms_per_layout=(time.time() - t) / 200 * 1000))
tables["E8_surrogate"] = pd.DataFrame(ml_rows)

# =====================================================================
# Save
# =====================================================================
xl = os.path.join(OUT, "v2_results.xlsx")
with pd.ExcelWriter(xl) as w:
    for k, df in tables.items():
        df.to_excel(w, sheet_name=k[:31], index=False)
    pd.DataFrame([dict(parameter=k, value=str(v)) for k, v in
                  {**vars(crR), **vars(moR), "storeys": STOREYS}.items()]).to_excel(w, sheet_name="Realistic inputs", index=False)
def conv(o):
    if isinstance(o, (np.floating, np.integer)): return o.item()
    if isinstance(o, np.bool_): return bool(o)
    if isinstance(o, np.ndarray): return o.tolist()
    return str(o)
json.dump(summary, open(os.path.join(OUT, "summary.json"), "w"), indent=2, default=conv)
for k, df in tables.items():
    print("\n==", k); print(df.to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
log(f"DONE. Results in {xl}")
