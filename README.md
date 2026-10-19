# FYP Enhanced (v2): crane position, pickup bays, sequence and two cranes

This is the upgraded version of the FYP code *"Optimisation of tower crane position and pick-up locations for precast construction"*.
It reproduces the original results exactly. It then adds the features that the FYP Plan and the CA1 description promised but the final version did not include.

---

## 1. What is in this folder

```
FYP_Enhanced/
├── README.md                ← this file
├── requirements.txt         ← list of Python libraries needed
├── data/
│   └── components_case3.csv ← the 43 PPVC modules (edit this to change the building)
├── crane_opt/               ← the engine (you normally don't need to touch this)
│   ├── config.py            ← ALL input numbers (speeds, radius, delays...) ← edit here
│   ├── data.py              ← reads the CSV, stacks floors
│   ├── model.py             ← physics: crane cycle time + safety rules
│   ├── optimizers.py        ← GA v1, GA v2, DE, random search, rule of thumb, grid search
│   ├── sequence.py          ← installation order optimisation
│   ├── multicrane.py        ← two-crane simulation
│   └── plotting.py          ← figures
├── experiments/
│   └── run_all.py           ← runs every experiment and saves the results
├── tests/
│   └── test_reproduction.py ← proves v2 = v1 when v1 assumptions are used
├── legacy/
│   └── copy 22.py           ← your original code (unchanged, for the comparison test)
└── outputs/
    ├── v2_results.xlsx      ← all result tables (one sheet per experiment)
    ├── summary.json         ← headline numbers
    └── figures/             ← all figures (PNG, 200 dpi, ready for the report)
```

---

## 2. One-time setup (Windows, about 5 minutes)

**Step 1: check that Python is installed**
1. Press the `Windows` key, type `cmd`, then press Enter. A black window (the Command Prompt) opens.
2. Type `python --version` and press Enter.
   - If you see `Python 3.10` or newer, go to Step 2.
   - If you see an error, install Python from https://www.python.org/downloads/. During setup, **tick "Add Python to PATH"**.

**Step 2: go to this folder**

In the same black window, type the line below and press Enter. Change the path if you moved the folder.
```
cd "C:\Users\Besitzer\OneDrive\桌面\study\FYP\FYP_Enhanced"
```

**Step 3: install the libraries**
```
pip install -r requirements.txt
```
Wait until it finishes. A warning about "upgrade pip" is safe to ignore.

---

## 3. Running it

| What you want | Type this and press Enter | Time |
|---|---|---|
| Check that everything works | `python tests\test_reproduction.py` | 5 s |
| Quick test of all experiments (fewer runs) | `python experiments\run_all.py --quick` | ~10 min |
| Full results (as reported) | `python experiments\run_all.py` | ~60–70 min |
| Re-run only the two-crane test | `python experiments\rerun_e6.py` | ~25 min |
| Re-run only the sequence / two-bay test | `python experiments\rerun_e5.py` | ~3 min |

When it finishes:
- open `outputs\v2_results.xlsx` for the tables
- open `outputs\figures\` for the pictures

> Tip: the full run prints progress lines like `[  120s] E2 ...`. If you close the window, the run stops.

---

## 4. Changing the inputs (most common edits)

**A. Different crane speeds, jib length or delays:** open `crane_opt\config.py` in Notepad or VS Code.
- `CraneSpec` holds the crane: `radius`, `slew_speed`, `trolley_speed`, `hoist_speed_loaded`, and the load chart (`max_load_t`, `load_moment_tm`).
- `MotionModel` holds how the motions combine: `alpha`, `beta`, `action_delay`, `hook_on_time`, `placement_time` and `floor_height`.
- `realistic_settings()` lists the v2 assumptions. `v1_settings()` lists the original ones.

**B. A different building:** edit `data\components_case3.csv` in Excel. Keep the column names. Each row is one module on a typical floor:
`id, x, y, width, length, height, weight_t, type`
- `weight_t` is currently **assumed** at 0.6 t/m². Replace it with real weights from the precast drawings (e.g. folder `progress report\327B\precast details`).
- `type` = `large` or `small` decides which pickup bay a module goes to in experiment E5.

**C. Number of storeys:** in `experiments\run_all.py`, change `STOREYS = ... 12`.

---

## 5. What v2 adds (summary)

| # | Upgrade | Why it matters |
|---|---|---|
| 1 | One shared cost function (fixes the v1 mismatch between `evaluate` and `evaluate_with_timings`) | The value optimised is now the value reported |
| 2 | Graded penalties and repair, instead of `inf` | The GA can "see" how close to feasible a layout is |
| 3 | Island-model GA plus local polish | Finds the true optimum in 20/20 runs; v1 got stuck in a local optimum |
| 4 | Exhaustive grid search as a benchmark | Proves the answer is the global optimum |
| 5 | Truck-access rule | The pickup bay can no longer sit inside a courtyard |
| 6 | Crane base checked against modules on every evaluation | v1 checked only the starting population |
| 7 | 3D hoisting: modules lifted from the ground to storey *k* | Building height now matters |
| 8 | Load chart: capacity falls with radius | Heavy modules must be close to the crane |
| 9 | Slew/trolley overlap (α, β, Zhang et al. 1999) | v1 = fully sequential is one special case |
| 10 | Installation sequence with floor-by-floor precedence | The Plan promised sequence optimisation |
| 11 | Two pickup bays (by module type) | Makes the sequence actually matter |
| 12 | Two tower cranes with a shared-zone anti-collision lock | The CA1 promised multi-crane operation |
| 13 | Sensitivity analysis, re-optimised for each change | Replaces the unsupported ±% claims |
| 14 | ML surrogate (gradient boosting / neural network) | The CA1 promised machine learning |

All assumptions marked **ASSUMED** in `config.py` should be confirmed or replaced with site or manufacturer data before you quote the numbers.
