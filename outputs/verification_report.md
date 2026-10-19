# Independent verification - FYP_Enhanced v2 results

Sources: outputs/v2_results.xlsx (authoritative), outputs/summary.json, outputs/full_run_log.txt, plus independent recomputation with crane_opt (scripts in /tmp/claude-0/verify/). No project files modified.
E6: both 2-crane rows show feasible=False, so E6 numbers were skipped (the logic is reviewed below).

## Claims vs files

| Claim | File / recomputed value | Status |
|---|---|---|
| E1 3942.930 s at report layout | 3942.9298 (xlsx and recomputed at full-precision coords; 3942.954 if the rounded coords 63.00/5.88/33.87/41.50 are used) | OK |
| E1 delay 1695 s | 1695 | OK |
| E1 tests/test_reproduction.py passes | Ran `python tests/test_reproduction.py`: "OK - v2 matches v1 to 1e-6 s on 200 random feasible layouts" (pytest isn't installed, so I ran the file directly) | OK |
| E2 GA v2 best/mean/std/hit/evals/time 3747.02/3747.04/0.01/100%/31,729/9.9 | 3747.024/3747.039/0.0125/100%/31,729.35/9.88 | OK |
| E2 GA v1 mean/std/hit/evals/time 3847.25/128.1/60%/79,208/23.9 | 3847.253/128.12/60%/79,207.8/23.94 | OK |
| E2 DE mean/std/hit/evals 3853.96/152.6/60%/11,085 | 3853.957/152.56/60%/11,084.5 | OK |
| E2 Random best/mean/std/hit 3762.32/4020.06/143.2/5% | 3762.322/4020.057/143.19/5% | OK |
| E2 rule of thumb 6084.44 (+62%) | 6084.436 (+62.38%) | OK |
| E2 grid 1 m 3747.05, 11.1 M evals, 110 s | 3747.048, 11,095,237, 109.8 s | OK |
| "True optimum 3747.05 is 5.0% faster than 3942.93" | 4.97% | OK on the arithmetic. But GA v1, GA v2 and DE all reached 3747.023 (best_s), which is lower than the grid's 3747.048, so the grid result isn't the exact optimum (see concern 4) |
| "GA v2 uses 60% fewer evaluations than GA v1" | 1 - 31,729/79,208 = 59.9% | OK |
| "GA v1 failed in 8 of 20 runs" | Log seeds 1,4,5,10,12,13,14,19 are >0.5% above the optimum = 8 runs (all 20 feasible) | OK |
| E3 access optimum 4109.1 s, crane (63.0,5.9), pickup (91.5,46.9) | 4109.077, (63.004, 5.880), (91.500, 46.917) | OK |
| E3 +9.7% vs unconstrained | 4109.077/3747.048 = +9.66% | OK |
| E3 GA v2 4110.4 within 0.03% | 4110.424, +0.033% | OK |
| E4 optimum crane (53.8,29.2) pickup (54.9,65.5) | (53.819, 29.152), (54.872, 65.500); feasible at full precision | OK |
| E4 movement 16.1 h of 193.9 h | 16.134 / 193.860 | OK |
| E4 hook-on + placement = 172 h | 516 x 1200 s = 172.0 h | OK |
| E4 rule of thumb 20.82 h (+29%), infeasible (access) | 20.817 h, +29.0%, violation {'access': 21.1} | OK |
| E4 v1 report layout 14.86 h, infeasible, ~1,460 t overload | 14.856 h, access 16.1 + load 1459.9 t | OK |
| E4 v1 global optimum 14.44 h, ~1,610 t | 14.436 h, load 1613.2 t (+ access 10.5) | OK |
| E4 "33 t modules lifted at up to 60 m radius where capacity is 20 t" | Load chart: cap = min(40, 1200/r), so 20 t at 60 m is right. But at the v1 report layout the farthest 33 t module is at 53.8 m (governing capacity 22.3 t). Pickup radius is 46.0 m (26 t). Same at the v1 global optimum (53.8 m, pickup 49.1 m). The only modules at 60 m are lighter ones, and only the 33 t modules are overloaded (180 lifts) | MISMATCH: should read "up to ~54 m, where capacity is ~22 t" |
| E5 1 bay any order 16.13-16.14 h | listed 16.1339, random mean 16.1377 | OK |
| E5 random orders vary 23 s | 23.4 s | OK |
| E5 2 bays listed 16.26 / random 16.24 / grouped 16.22 / optimised 16.14 (-0.7%) | 16.257 / 16.241 / 16.224 / 16.140; -0.72% vs listed | OK. Note the optimised 2-bay result (16.1396) is still 0.035% worse than 1 bay (16.1339) |
| E7 base crane time 21.9 h | 21.860 h (the jib-radius rows equal the base) | OK |
| E7 hoist loaded -20% +8.3%, +20% -5.5% | +8.31%, -5.54% | OK |
| E7 delay and floor height +/-5% | delay +/-5.24%, floor +/-5.04% | OK |
| E7 slew +4.1/-2.7 | +4.10 / -2.69 | OK |
| E7 trolley and alpha <2% | trolley +1.99/-1.28, alpha -0.68/+0.68 | OK (trolley is borderline at 1.99%) |
| E7 jib radius 0%, optimum needs ~46 m reach | 0.00%; max crane-to-module distance at the realistic optimum is 45.28 m (pickup 36.4 m), so -20% (48 m) never binds | OK (more precisely ~45 m) |
| E7 v1 slew 0.07 to 0.05 re-optimised +7.0% | 6.957% (summary.json) | OK |
| E8 GB R2 0.997, MAPE 0.23%, 0.007 ms | 0.9974, 0.232%, 0.00684 ms | OK |
| E8 MLP R2 0.999, MAPE 0.17%, 0.002 ms | 0.9987, 0.167%, 0.00167 ms | OK |
| E8 simulator 0.42 ms | 0.418 ms | OK |
| E8 "60-200x faster" | 0.418/0.00684 = 61x (GB), 0.418/0.00167 = 250x (MLP) | MISMATCH: 60-250x. The comparison itself is also questionable (concern 1) |
| E8 surrogate pick within 3.7% | 3.72% | OK |

## Code concerns (ranked)

1. **E8 speed comparison is not like-for-like (moderate, affects a headline claim).** The surrogate time is the batch `predict` time divided by the batch size. The simulator time is 200 separate scalar `Problem.evaluate` calls, each carrying Python/dict/violation overhead. The same engine is vectorised: the E2 grid ran 11.1 M evaluations in 110 s, about 0.01 ms per layout for 43 modules. For 516 modules that should still be roughly 0.1 ms or less. So a batched simulator is within a small factor of the surrogate, and "60-200x faster" overstates the benefit.
2. **multicrane.py drops the pickup-reach constraint (latent bug).** `v.pop("reach")` removes the module-reach term and also the pickup-bay reach term that `violations()` adds into the same key. Module reach is re-handled through `ok`, but nothing then forces a crane's own pickup bay to be within its jib radius. The capacity check still uses max(r, pickup distance), so only the reach rule is lost. The current E6 layouts happen to have pickups inside the jib (35 m and 22 m; 36 m and 26 m), but a re-run could exploit this.
3. **E6 current rows are infeasible because of mast separation.** Both 2-crane layouts in the xlsx have mast spacing (about 34 m and 40 m) below the required 45 + 2 = 47 m. That explains feasible=False. Other crude parts of the logic, in order of severity:
   - Bay-to-bay separation is a 12 m centre distance, which ignores the 12 x 5 m bay shape and orientation.
   - The shared-zone lock serialises whole cycles. That is conservative, but the waiting time depends on the processing order.
   - No crane-base vs other-crane's-bay overlap check.
4. **The grid "true optimum" isn't exact (minor wording issue).** GA v1, GA v2 and DE best_s = 3747.023, which is below the grid's 3747.048. Better to say "~3747.0 s". The hit-rate and gap columns are unaffected.
5. **rerun_e5.py uses the 2-dp rounded layout from summary.json (minor).** It reads `summary["realistic"]["x"]` = (53.82, 29.15, 54.87, 65.5). That layout is slightly infeasible: 0.25 t load violation. Effect on E5 values is under 0.001 h, but strictly the 1-bay rows aren't at the feasible optimum. Same rounded xR is used in rerun_e6 (only for the 1-crane layout string).
6. **model.py inconsistencies (minor; none invalidate results):**
   - `bay_overlap` assumes a fixed orientation (12 m along x), while `pickup_overlap` allows either orientation.
   - The hull access test uses the max edge signed distance, which underestimates distance near hull vertices. It is conservative.
   - No check that the crane base does not overlap a pickup bay. The 5 m no-lift radius doesn't stop this for a 12 m bay, though it doesn't bind at any reported optimum.
   - The empty-hook return lowers by the current module's H, not the next module's.
7. **Physics review: no errors found.**
   - The Zhang-style combine max + k*min is applied correctly for alpha (slew/trolley) and beta (horizontal/vertical lift).
   - Lowering at the destination and the empty lift at the start of the return are sequential.
   - Loaded and empty hoist speeds are used on the correct legs.
   - Realistic vertical distances follow a consistent hook-height bookkeeping: lift to Z+H+clr, lower H+clr, return up H+clr, down Z+H+clr.
   - Delays are 3 per delivery and 5 per return, matching v1; the last return is dropped.
   - The load chart takes the minimum capacity at pickup and destination radius.
   - Penalties are 1e3 s per m or t of violation. Reported layouts are re-evaluated with an explicit `feasible` flag.
   - v1 equivalence is confirmed by the passing test.
8. E7 uses a single GA seed per perturbation, so small effects (trolley 1.99%, alpha 0.68%) carry some optimiser noise. Acceptable, given GA v2's 0.01 s std in E2.
