# Examiner-style audit: "Optimisation of tower crane position and pick up locations for precast construction" (NTU FYP 2024/25)

**Sources checked.** Report text `/tmp/claude-0/report.txt`; code `/mnt/user-data/uploads/FYP/CODING/copy 22.py`; workbooks `Trial 5.xlsx` (43-component run) and `case AA.xlsx`. The other scripts in the CODING folder (`copy 20.py`, `copy 23.py`, `example 1.py`) were checked only to trace where results came from.

**Verification scripts.** `/tmp/claude-0/audit/checks.py` (deterministic re-evaluation) and `/tmp/claude-0/audit/ga_run.py` (instrumented GA, 3 trials x 100 generations, pop 200). `lib.py` in the same folder is `copy 22.py` cut before the run block.

**Key provenance facts established**
- **Appendix B is the same code as `copy 22.py`.** A whitespace-normalised diff shows only differences in line wrapping.
- **`Trial 5.xlsx` is the 43-component case.** It reproduces Table 3 row 3 exactly: 3942.930 s total, 2247.930 s movement, 1695 s delay. Best config: crane (63.000, 5.879), pickup (33.872, 41.5).
- **`case AA.xlsx` was not produced by Appendix B code.** Its Input Parameters sheet gives 11 components, CRANE_RADIUS 50 m and a 15 x 15 m pickup zone. `copy 22.py` uses 43 components, 60 m and 12 x 5 m. None of the supplied scripts has the AA–CC setup, and none has the Table 6 setup (2–9 components, variable speeds). **The code behind Sections 4.4 and 4.5 is not in the report.**
- **The code's delay is a fixed function of n.** `evaluate_with_timings` gives 3 + 1 + 4 = 8 delays per cycle and 3 for the last component, so delay = 40n − 25 s. That gives 375 / 975 / 1695 / 415 s for n = 10 / 25 / 43 / 11, matching Tables 3 and 11. Lift and lower are each a fixed 3 m at 0.6 m/s (5 s). The minimum lift + lower time is therefore 20n − 10 s.

---

## 1. Internal numerical inconsistencies

| # | Location | Conflict | Correct arithmetic / note |
|---|---|---|---|
| 1.1 | §4.1, para after Table 3: "delays… accounting for 32–43% of total time" | Table 3 gives 375/670.25, 975/1975.84 and 1695/3942.93 | Delay share is **55.9%, 49.3%, 43.0%**, so the range is 43–56%, not 32–43%. |
| 1.2 | §4.1 says "488% more time"; §4.6.2 and Conclusions say "1,080% increase" | Both describe Case 1 (10 components) vs Case 3 (43 components) | 3942.93 / 670.25 = 5.883, i.e. **+488.3%**. The 488% is correct and the **1,080% is wrong**; it matches no pair of numbers in the report (7890/670 = +1077% is the nearest, which looks like a coincidence). |
| 1.3 | §4.1 "exponential increase… compounding rigging delays" | Time per component is 67.0, 79.0 and 91.7 s for n = 10, 25, 43 | Growth is mildly superlinear, not exponential. Delay is 40n − 25 and grows linearly, so it cannot "compound". |
| 1.4 | Case numbering | Three different "Case 1–n" schemes are used: Cases 1–3 (10/25/43 components, §4.1, Figs 4–6, labelled "Trial 1–3" in Table 3 and §4.6.2); Cases 1–11 (Table 6, 2–9 components); and **"Case 7 (43 components)"** in §4.6.4 and the Conclusions | Table 6 Case 7 is a 9-component L-shape. The 43-component case is Case 3 / "Trial 3". Rename the schemes (e.g. S1–S3, L1–L11, AA–CC/Free) and rename Table 3's "Trial" column to "Case". |
| 1.5 | §4.6.4 / Conclusions: GA optimum for 43 components = 5,420 s at crane (30.5, 48.2), pickup (72.3, 24.8) | Table 3 and Trial 5.xlsx: best = **3942.93 s** at crane (63.0, 5.88), pickup (33.87, 41.5) | Re-evaluating the claimed (30.5, 48.2)/(72.3, 24.8) with the report's own code gives **5145.07 s**, which is neither 5420 s nor the GA optimum. The 5420/7890 figures cannot be reproduced. |
| 1.6 | §4.6.4: "7,890 → 5,420 s = 31.3%" | Arithmetic: (7890 − 5420)/7890 = 31.31%, which is consistent internally | Re-computed baseline: crane at the component centroid (53.95, 43.41) with the best pickup found by a 0.5 m grid search gives 4974.97 s. GA best is 3942.93 s, a **20.7%** reduction. Note that the centroid crane base also overlaps a PPVC footprint. |
| 1.7 | Table 6 "Δ vs Base" | The base is inconsistent: Cases 3–6 use the Avg column (78.1/32.8 = +138%, 63.6/32.8 = +94%, 93.8/32.8 = +186%, 132.9/32.8 = +305%). Case 2's +138% is wrong on either basis. Cases 7–11 match neither basis. | Correct values (best-basis / avg-basis): C2 +82% / **+140%**; C7 +990% / +831% (stated +1002%); C8 +2077% / +1754% (stated +2096%); C9 +846% / +733% (stated +886%); C10 +412% / +358% (stated +443%); C11 +1306% / +1212% (stated +1407%). |
| 1.8 | Table 6 "Parameter Modification" for Cases 8 and 9: "Rotation speed: 0.03 → 0.07" | §3.6, Table 9 and the Conclusions describe a reduction from 0.07 to 0.03 | The arrow is reversed. It should read 0.07 → 0.03. |
| 1.9 | **Table 6 times are physically impossible under the report's own model** | Case 1 (n = 2) best = 27.7 s. The code's fixed lift + lower alone is 20n − 10 = **30 s**, and the fixed delay is 40n − 25 = 55 s, giving a floor of 85 s. Case 7/8 (n = 9) best is 301.8 s against a floor of 505 s. Every case in Table 6 is below the floor the code imposes. | Table 6 was not generated by the methodology described in §3 or by Appendix B (or the delays and return trips were dropped without saying so). This needs to be explained or the results regenerated. |
| 1.10 | Table 7 Lift % ≠ Lowering % (e.g. C3 22 vs 13, C5 17 vs 8, C6 15 vs 8) | In the code, every lift and every lower is 3 m at 0.6 m/s = 5 s, and they come in pairs. The Trial 5 breakdown gives lift = lower = **425.0 s** exactly. | The Lift and Lowering columns must be equal under the stated model. Table 7 also leaves out delay, which is 43–56% of total time in the code's own runs. |
| 1.11 | Table 9 "6→10: Peripheral impact +11%" | Table 7: 2.1× → 2.8× | That is **+33%**, not +11%. |
| 1.12 | Table 9 "6→10: Rotation/Movement shift 24% → 22%" | Table 7 movement: Case 6 = 19%, Case 10 = 22% | It should read 19% → 22%. (The 24% is Case 7's figure.) |
| 1.13 | Table 9 "7→8: +101%" | 301.8 → 603.1 = +99.8% (best), 305.5 → 608.1 = +99.1% (avg) | Approximately +100%. **Bound check:** for the same layout, the re-optimised time is at most the time at the old optimum with the slower speed. So the increase cannot exceed rotation share × (0.07/0.03 − 1) = 0.64 × 1.333 = **+85%**. The same bound gives +77% for 6→9 (reported +101%) and +24% for 7→11 (reported +29.1%). Tables 6, 7 and 9 are mutually inconsistent. |
| 1.14 | Table 9 "7→11 +29%" uses the best times; the Avg basis gives +40.9% | Mixed bases across Tables 6 and 9 | State which basis is used. |
| 1.15 | §4.5: "crane Y = 60 increased movement times by 15–30% vs Y = 40" | BA/AA = +19.9%, BB/AB = +23.7%, **BC/AC = −18.2%** | The claim fails for the BC/AC pair. It should say "+20% to +24% for two of three pairs; BC is 18% faster than AC". |
| 1.16 | Conclusions: "fixed-position configurations (e.g. Case AC) underperformed dynamic Free by 24%" | The 24% is Free vs **AA** movement time (538.01 vs 706.14 = −23.8%) | Free vs AA total time = −15.0%. Free vs AC: movement −55.9%, total −41.7% (AC is 71.6% slower than Free). |
| 1.17 | §4.5: AA is good because pickup Y = 55 is "close" to crane Y = 40, "minimising vertical displacement"; AC is bad because pickup Y = 40 "forced greater horizontal movement" | Y is a plan coordinate, not vertical. AC's pickup Y equals the crane Y. | The reasoning is incoherent. Explain the results in terms of slew angle and radial distance to the component cloud. |
| 1.18 | Table 4 (components #9, #25, #33 of the 43-component layout), re-checked against Trial 5's best configuration | Stated radial distances 18.2 / 49.8 / 63.4 m; actual from the Trial 5 crane: **41.6 / 40.7 / 60.0 m**. Stated totals 112 / 175 / 214 s; actual cycle times **83.2 / 92.0 / 118.5 s**. Stated mean 146 s; actual mean **91.7 s** (= 3942.93/43). Stated rotation 14 / 33 / 47 s; actual (out + back) 14.3 / 21.3 / 30.6 s. | Table 4 does not match the reported optimum. Internally, the Mean row gives 121 + 35 = **156 ≠ 146**. "Time vs Avg": 112/146 = **−23%** (stated −21), 175/146 = **+20%** (stated +23), 214/146 = **+47%** (stated +51). A radial distance of 63.4 m **exceeds the 60 m reach**, so that configuration would be infeasible. |
| 1.19 | §4.2 text: "#25… 23% longer *movement* time"; Conclusions: "up to 51% longer movement times" | In Table 4 those percentages are *total* time vs average | Movement vs mean (121 s): #25 +17.4%, #33 +38.0%. |
| 1.20 | Radius: §3.6, §4.5 and Table 12 say 50 m; §4.6.4, the Conclusions and the Appendix B code (`CRANE_RADIUS = 60`) say 60 m | Mixed | State the radius per study. Table 8 max distances of 63.2 m (C2, C11) and 58.6 m (C5) exceed 50 m (and 60 m for C2 and C11). |
| 1.21 | §3.6: "eleven standardized PPVC units" "across all test cases"; "eleven distinct layout configurations… three geometric types… 2 to 9 units" | Table 2 lists **6** layouts (4–9 units, speeds 0.05 / 0.8 / 0.7). Table 6 lists 11 cases (2–9 units, speeds 0.03 / 0.07 / 0.5 / 1.0 only). §4.1 uses 10 / 25 / 43 units. | Table 2 does not match Table 6: no 7-unit or 4-unit case appears, and 0.05 rad/s and 0.7/0.8 m/s are never run. The 11 units apply to AA–CC only. |
| 1.22 | §3.2.2: "A fixed delay of 5 seconds per component" | Code: 8 × 5 s = 40 s per cycle (40n − 25 total); §3.6: 83 steps × 5 s = 415 s for 11 units | Say "5 s per operation transition (8 per pick-place-return cycle)". |
| 1.23 | §3.5: trials "enforced strict boundary constraints (crane X ∈ [20, 40], pickup Y ∈ [0, 30])" | Appendix B has `ENABLE_AREA_LIMITS = False`, so 0–100. The 43-component optimum has crane X = 63, pickup Y = 41.5. | Contradiction. |
| 1.24 | Table 8 density | Case 7: 9 modules at 0.18 comp/m² is about 50 m² in total, smaller than the modules themselves (21–55 m² each). Case 1: 2 modules at 0.04 comp/m² is 50 m² in total. | The values are physically implausible. Define what density means. |
| 1.25 | §4.6.4: runtime "2 min (10 components) vs 12 min (43 components)… linear… as depicted in Figure 4" | 4.3× more components but 6× more time. Figure 4 is the Case 1 layout, not a runtime plot. | Fix the figure reference and either show the runtime data or drop the word "linear". |
| 1.26 | §4.5: the Table 12 paragraph appears twice (once before and once after Table 11) | Duplicate text | Delete one. |
| 1.27 | §4.6.4: "(see Table 2)" for the 43-component Case 7 | Table 2 contains no such case | Wrong cross-reference. |

## 2. Method-vs-code mismatches

| # | Report claim | What the code actually does |
|---|---|---|
| 2.1 | §3.2, §3.2.2, §3.3 and Conclusions: constraint handling by "penalty terms… additive time costs" | Death penalty. Every violation is `return (float('inf'),)` in `evaluate`, and no penalty is ever added. (§4.6.1's "hard-constraint" description is the accurate one.) |
| 2.2 | §3.6: the Free case uses "a gradient-descent optimization algorithm… minimized Euclidean distances and angular displacements" | The same GA as every other case: `algorithms.eaSimple(population, toolbox, 0.7, 0.3, 500, …)` with `ENABLE_AREA_LIMITS=False`. There is no gradient code. (This also contradicts §3.2, which says GA was chosen *because* the problem is unsuitable for gradient methods.) |
| 2.3 | §3.1: outputs "the most efficient sequence in which to install components"; Introduction: "consider operational sequence" | No sequence variable exists. The order is fixed at list index (`for i, ppvc in enumerate(PPVC_COMPONENTS)`), which §3.3 admits. With one pickup point and equal heights, each cycle is independent (`adjust_height` = 0), so total time does not depend on order at all. |
| 2.4 | §3.1 / §3.3: AABB used to reject overlaps between "**crane swing paths**, site boundaries and structural elements" | AABB is applied only to pickup-zone vs PPVC rectangles (`is_valid_location`, `pickup_zone_overlaps_ppvc`). There is no swing-path geometry, no boundary rectangle check (only the zone centre is limited to 0–100), and the crane base is checked only at initialisation. |
| 2.5 | §3.6: "eleven standardized PPVC units, each **15 × 15 × 3 m and weighing 20 t**" | `copy 22.py` components are 7×3, 6×5, 5×11 or 11×5 m in plan, height 4.5 m, and there is **no mass field**. `case AA.xlsx` has a 15 × 15 **pickup zone**, which is probably where the 15 × 15 came from. Load is never used, so no load chart or capacity-vs-radius check exists. |
| 2.6 | §3.6: "advanced **discrete-event simulation software** that accurately modelled crane kinematics and component interactions" | A closed-form sum of constant-speed segment times inside a Python loop. There is no DES engine, no events and no component interactions. |
| 2.7 | §3.6: data collection recorded "travel distances, coverage area efficiency, component density, peripheral penalty" | The code exports only Summary, All Trials, per-step timings and input parameters. None of the Table 7/8 spatial metrics or the peripheral penalty is computed anywhere. |
| 2.8 | §3.6: "Horizontal travel time derived from **Euclidean distance** between coordinates / 1.0 m/s" | `radial_move_to_dest = abs(r_dest - r_pickup) / MOVE_SPEED`, i.e. the difference in trolley radius, not Euclidean distance. |
| 2.9 | §3.1: "two-tiered architecture… two submodules in a feedback loop"; constraints from "truck access paths, stacking logistics" | One 4-gene chromosome `[crane_x, crane_y, pickup_x, pickup_y]` and one fitness function. No truck access or stacking constraints exist. |
| 2.10 | Introduction: "3D models in Revit and machine learning algorithms implemented with Python" | No Revit link, no ML. The model is 2D plus fixed 3 m hoists. |
| 2.11 | §3.3: no-lift zone "prohibit lifting activities within a five-meter radius of the crane base" | Only the pickup-zone **centre** is checked (`is_in_no_pickup_zone`). Destinations inside 5 m and pickup rectangles that partly enter the 5 m circle are not checked. |
| 2.12 | §3.2.1: "continuous parameter encoding" | Initialisation uses `random.randint` (integers). Floats appear only after cxBlend or Gaussian mutation. |
| 2.13 | §3.3: "module height assumed 4.5 m to ensure sufficient clearance"; `storeys` field | Every hoist is 3 m (`clearance - PPVC_COMPONENTS[0]['height']` = 3 m, so 5 s). `storeys` is never used. There is no hoisting from the ground to the installation level, so building height does not affect the result. |
| 2.14 | §3.5: "seed-invariant reproducibility through fixed random seeds" | A fixed seed (`random.seed(42)`) gives repeatability, not seed invariance. No multi-seed study was run. |
| 2.15 | §3.4: "configured based on preliminary sensitivity analyses" | No sensitivity code or GA-parameter study is supplied. `copy 23.py` uses GENERATIONS = 100, so parameters varied between versions. |
| 2.16 | §3.2.2: speeds "based on… (Huang et al., 2011)" and the fitness equation | The fitness used by the GA (`evaluate`) is **not** the reported T_total. See 3.1. |

## 3. Code bugs and modelling weaknesses (`copy 22.py`)

Items marked **[verified]** were run in `/tmp/claude-0/audit/`.

1. **`evaluate` (fitness) ≠ `evaluate_with_timings` (reported) [verified].** The reporting function adds one extra 5 s "transition" delay per cycle (lines 240–242) that `evaluate` does not have. For the Trial 5 optimum, the fitness is 3732.93 s but the reported value is 3942.93 s, a difference of 210 s = 5(n − 1). The ranking is unaffected because the offset is constant, but the reported numbers are not what was optimised. `evaluate_with_timings` also skips the area-limit checks (lines 112–119).
2. **`evaluate_with_timings` returns 2 values when infeasible but the caller unpacks 3 [verified].** The returns are `(inf, [])` at lines 189–204, while line 329 does `total_time, timings, total_delay = ...`, which raises a ValueError. This is reachable. Re-evaluating the reported optimum after rounding to 6 dp (63.0, 5.878511) crashes, because the solution sits exactly on the 60 m reach boundary (distance to #33 = 59.99999999999996 m). The hall-of-fame check `if not hof` never catches an infeasible best.
3. **`lift_to_clearance` in `evaluate` uses `PPVC_COMPONENTS[0]['height']` (line 154)** instead of the current hook height. It is harmless only because every height is 4.5 m. With mixed heights the fitness would be wrong, and it would disagree with the `current_hook_height` logic in `evaluate_with_timings`.
4. **Crane-base overlap with PPVC is never checked after initialisation [verified].** `generate_individual` checks it, but `evaluate` does not, and `mutate` / `cxBlend` can move the crane onto a module. In the instrumented run, **1,791 accepted (finite-fitness) evaluations had the 5 × 5 m crane base overlapping a PPVC footprint**. The reported best happened to be clear.
5. **cxBlend (α = 0.5) extrapolates out of bounds [verified].** From parents at 0 and 100 the children span −50 to 150. These are not clamped (only `mutate` clamps) and so receive inf. That wastes evaluations and makes the GA's effective search domain depend on the death penalty.
6. **Pickup orientation logic is redundant and misleading [verified].** `valid_orientations` accepts 12×5 *or* 5×12, but `pickup_zone_overlaps_ppvc` (line 136) then requires 12×5. The rotated orientation is never actually used (286 evaluations were rejected by exactly this case). Pickup zones are also not required to lie within the site, since only the centre is limited to 0–100.
7. **Kinematics are crude.** Slew, trolley and hoist happen strictly one after another (real cranes overlap them), there is no acceleration or deceleration, sway settling or load-dependent speed, the return path mirrors the outbound path, and the hoist is a fixed 3 m regardless of storey. Movement time is overestimated, and the model is insensitive to building height.
8. **The objective is separable and order-independent.** It is a sum over components of g(crane, pickup, cᵢ). With a single pickup point, the "fixed sequence" assumption is moot, so this is not a scheduling model. The report should say so rather than imply sequence effects.
9. **No capacity or load-chart constraint.** The reported optimum puts component #33 at exactly 60.0 m, which is the reach limit. Any real 20 t module (§3.6) at 60 m is far beyond a typical tower-crane load chart.
10. **Delays dominate and are hard-coded.** 8 × 5 s per cycle (40n − 25) is 43–56% of total time and has no effect on the optimisation. The §4.5 statement that "the consistent 415-second delay… confirms that delays were protocol-driven" is circular, because the delay is a constant.
11. **Search reliability and multimodality [verified].** In Trial 5.xlsx only 2 of 10 trials reached 3942.93 s. Seven stopped at about 3977 s (crane ≈ (70.0, 9.3), pickup (67, 62.5)) and one at 4246 s. In the audit run, all 3 trials converged to the same ≈ 3977 s basin. There is no convergence logging (`verbose=False`, no `Statistics`), so convergence claims cannot be checked.
12. **Fixed cases AA–CC are degenerate.** With ranges of the form 50–50, the search space is a single point, and all 10 trials in `case AA.xlsx` are identical (1121.143806 s). These are single evaluations, not GA optimisations, and the report should say so.
13. **Runtime claim [verified, indicative].** 100 generations at population 200 took 7.2–7.9 s here, which extrapolates to about 40 s per 500-generation trial for 43 components. That is about 18× faster than the claimed "about 12 minutes" on an i7-12700H.
14. **Minor.** Visualisation runs even when `best_setup` is None, which crashes. The output path is a hard-coded Windows path and the file is overwritten every run, so provenance depends on manual renaming. `tabulate` is imported but unused. Python 3.13 with Matplotlib 3.8.2 (§3.7) is an unlikely combination, since 3.8.2 predates Python 3.13 wheels; check the stated versions.

## 4. Claims unsupported by any data shown: needs evidence or removal

| Claim | Location | Status |
|---|---|---|
| Table 4 component times | §4.2 | Contradicted by Trial 5 (see 1.18). Regenerate from the Operation Sequence sheet. |
| "≈23% of candidates rejected" and the Table 5 breakdown (48% out of bounds / 32% overlap / 20% no-lift) | §4.3 | The code has no rejection logging. Instrumented re-run [verified]: 25.0% rejected, but the breakdown of rejections is pickup–PPVC overlap 48.4%, **component beyond reach 34.3%**, pickup beyond reach 10.6%, pickup out of bounds 3.7%, **crane out of bounds 2.2%, no-lift 0.7%**. Table 5 is wrong in kind: it omits the reach category entirely. It also says rejection happens "during the mutation phase", but evaluation happens after variation. |
| Table 7 shares and the "peripheral penalty" | §4.4 | The metric is undefined and not computed in the code. Lift ≠ lower contradicts the model (1.10). |
| Table 8 spatial metrics (avg/max distance, coverage %, density) | §4.4 | Not computed by any supplied code. Values are implausible (1.20, 1.24). |
| Table 10 (time reduction vs "Random" 28/19/22%, "crane position error" 4.2/6.8/8.1 m, "pickup zone optimization" 92/87/78%) | §4.4 | No random baseline, no ground truth for "error" and no definition of "optimization %" anywhere. **Remove, or define and show the data.** |
| Figure 8 heatmap | §4.4 | The method used to generate it is not described. |
| GA beats centroid-based placement by 31.3% (7890 → 5420 s) | §4.6.4, Conclusions | Not reproducible (see 1.5–1.6). The code-based re-computation gives 20.7% vs a centroid crane with the best pickup. |
| "Standard deviation of only ±4.2%" | §4.6.1 | The only multi-trial data (Trial 5) gives std 88.6 s, CV **2.2%**. The cross-case std is not defined. Fixed cases have zero variance by construction. |
| Rotation 0.07 → 0.05 gives +22% total; hook 1.5 m/s gives −15% movement | §4.6.3 | Code check at the Trial 5 optimum: 0.05 rad/s gives **+8.4%**, and re-optimisation cannot exceed this, so **+22% is impossible** for this layout. 1.5 m/s gives −8.5% movement (−4.8% total) at fixed configuration; −15% would require re-optimisation evidence. |
| Runtime 2 min vs 12 min, "linear" | §3.7, §4.6.4 | No timing data shown. The audit measured about 40 s per trial. |
| "RL-guided GA can reduce convergence time by up to 40%" (Liu et al., 2022) | §4.7, Conclusions | The cited paper is about a firefly algorithm for crane layout, not RL-guided GA. The "40%" in the Conclusions becomes a claim about this project. **Remove or find a correct source.** |
| "5-second delays mirror industry best practices" (Liu et al., 2022) | §3.3 | Mis-attributed (see §5). Justify the 5 s or present it as an assumption. |
| "Consistently outperforming conventional planning methods" | Abstract | Only one unsupported baseline exists. |
| Table 2 layouts (Linear B, L-shape A/B, Scattered A/B with speeds 0.05/0.7/0.8) | §3.6 | No results for these are reported anywhere. |
| Huang et al. (2021) "cost savings 6.54% to 18.07%" | §2 | Check the figures against the paper. |

## 5. Reference issues

- **Cited in the text but missing from the reference list:** **Liu et al., 2023** (§4.7, LiDAR/voxel) and **Wang & Cheng, 2024** (§4.7, VR operator studies).
- **Liu et al. (2022)**, a firefly algorithm for crane layout, is mis-attributed twice: for the 5 s delay "best practice" (§3.3) and for "RL-guided GA reduces convergence time by up to 40%" (§4.7).
- **Gottschalk et al. (1996)** is about *OBBTree*, i.e. oriented bounding boxes. It is cited for AABB detection. Cite an AABB or collision-detection source, or describe the method as AABB without this reference.
- **Irizarry & Karan (2012)** is cited as "Irizarry et al., 2012" but has two authors. It is a GIS/BIM crane-*location* paper, yet it is cited for "complexities of crane scheduling… conventional methods for minimizing crane overlap fail". That is a probable mis-attribution.
- **Ren & Wu (2015)** is cited as "Ren et al." (two authors). It is a mobile-crane anti-collision system, cited for tower-crane halts. The attribution is weak.
- **Yin et al. (2023)** is a tower-crane service-scheduling optimisation, cited for "AI and machine learning… crane scheduling". This overstates the paper.
- **Datta et al. (2023)** is a BIM sustainability review, cited for multi-crane workflow coordination. The attribution is weak.
- **Huang et al. (2011)** is an MILP crane and supply-location paper. Check that it really reports 0.07 rad/s, 1.0 m/s horizontal and 0.6 m/s vertical speeds.
- **Abdelmegid et al. (2015)** is used for Monte Carlo models and an ACO/PSO/SFL comparison. If those statements come from its literature review, cite the primary sources.
- **Deb (2001)** is a multi-objective EA book cited for the GA vs gradient argument. That is acceptable, but Goldberg (1989) or Holland would be more apt.
- **Formatting:** Huang et al. (2021) and Ren & Wu (2015) entries have DOIs spliced into the middle of the journal name. "Buildings (Basel)" and "Nature (London)" are database artefacts.
- **Missing source for "industry-standard medium-sized tower cranes"** and the speed and capacity values.

## 6. Prioritised fix list

**High: affects validity and could fail examination**
1. **Supply or regenerate the code for Sections 4.4 and 4.5.** Appendix B (43 components, 60 m, 12 × 5 m) cannot produce AA–CC (11 components, 50 m, 15 × 15) or Table 6. Table 6 values are below the model's own minimum possible time (1.9).
2. **Delete or regenerate the fabricated-looking analytics:** Table 4, Table 5 (and the 23%), Tables 7, 8 and 10, the 31.3% / 7890 / 5420 centroid claim, ±4.2%, the +22% / −15% sensitivity figures, and the 40% RL claim. Replace them with instrumented outputs; the audit scripts show how.
3. **Unify case naming** and fix "Case 7 = 43 components", the "Trial" labels in Table 3, and Figure 4 being cited for runtime.
4. **Correct the Methodology to match the code:** death penalty not additive penalties; GA (not gradient descent) for the Free case; no sequence optimisation; AABB only between pickup zone and PPVC; component dimensions and no mass; no DES software; radial trolley distance not Euclidean; no Revit or ML.
5. **Fix the percentage errors:** 32–43% → 43–56%; 1,080% → 488%; Table 6 Δ column (one basis); the Table 6 arrow direction; Table 9 (+33%, 19% → 22%); "15–30%" (BC is −18%); the AC/24% statement in the Conclusions.

**Medium: correctness of the model and code**
6. Make `evaluate` and `evaluate_with_timings` share one cost function, so the reported value equals the optimised value. Fix the 2- vs 3-tuple return.
7. Check crane-base vs PPVC overlap, pickup-zone-within-site and no-lift for destinations inside `evaluate`. Clamp after cxBlend, or use `cxSimulatedBinaryBounded`.
8. Use the current hook height in `evaluate`, model the hoist to the installation level (use `storeys`), and consider simultaneous slew and trolley (max instead of sum).
9. Add a radius-dependent capacity constraint, or state explicitly that it is omitted. Give the reach margin of the optimum (it is currently exactly 60.0 m).
10. Log convergence (`tools.Statistics`) and report the spread over 10 trials with different seeds. Acknowledge multimodality (7 of 10 trials stuck at about 3977 s) and that the fixed cases are single-point evaluations.
11. Run a real sensitivity analysis: rotation speed, trolley speed, delay and radius, re-optimised for each value.
12. Add the two missing references. Re-source or remove the mis-attributed Liu 2022 and Gottschalk claims.

**Low: presentation**
13. Remove the duplicated Table 12 paragraph and the "(see Table 2)" error. Rewrite the "vertical displacement" reasoning.
14. Reconcile Table 2 with Table 6, and the "eleven units / 2–9 units" text.
15. Correct the software versions (Python 3.13 vs Matplotlib 3.8.2) and justify the 12-minute runtime or replace it with measured data.
16. Fix the et al. usage for two-author papers and the garbled DOIs. Remove the unused `tabulate` import and the hard-coded output path.
