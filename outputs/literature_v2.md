# Literature for FYP v2: Tower crane position and pick-up point optimisation for precast/PPVC construction

Compiled 2026-10-19. I confirmed every entry against a publisher page, an institutional repository, DOAJ or an indexing page (URLs below). Where I could confirm only some details, the entry is marked **[partial]**. I did not invent any DOI. Where I could not confirm a DOI, the entry says so and gives the URL I used.

Tags: **LR** = Literature review, **M** = Method, **D** = Discussion.

---

## Part 1: Verifying the citations used in the student report

| # | Report citation | Status | Correct details / notes |
|---|---|---|---|
| 1 | Huang, Wong & Tam 2011, *Autom Constr* 20(5) | **Verified** | Huang, C., Wong, C. K., & Tam, C. M. (2011). Optimization of tower crane and material supply locations in a high-rise building site by mixed-integer linear programming. *Automation in Construction, 20*(5), 571–580. https://doi.org/10.1016/j.autcon.2010.11.023 |
| 2 | Abdelmegid et al. 2015, *Alexandria Eng J* | **Verified** | Abdelmegid, M. A., Shawki, K. M., & Abdel-Khalek, H. (2015). GA optimization model for solving tower crane location problem in construction sites. *Alexandria Engineering Journal, 54*(3), 519–526. https://doi.org/10.1016/j.aej.2015.05.011 |
| 3 | Huang et al. 2021, *Autom Constr* 127, 103716 | **Verified. Check the context it is cited in.** | Huang, C., Li, W., Lu, W., Xue, F., Liu, M., & Liu, Z. (2021). Optimization of multiple-crane service schedules in overlapping areas through consideration of transportation efficiency and operational safety. *Automation in Construction, 127*, 103716. https://doi.org/10.1016/j.autcon.2021.103716. This is a **multi-crane scheduling / collision** paper, not a crane-location paper. Cite it for overlap/safety scheduling only. |
| 4 | Kim, Oh & Lim 2024, *Buildings* 14(1) 11 | **Verified. High risk of mis-citation.** | Kim, S., Oh, J., & Lim, J. (2024). Development of an algorithm for crane trajectory distance calculation for erection of precast concrete members. *Buildings, 14*(1), 11. https://doi.org/10.3390/buildings14010011. It deals with **large mobile/crawler cranes** (550 t, 54 m jib + 36 m boom) erecting heavy precast members in logistics buildings. It is **not** about tower crane location, and it gives no speed values. Do not cite it for tower-crane kinematics or tower-crane location. |
| 5 | Liu et al. 2022, firefly, *Comput Intell Neurosci* | **[partial]** | The title is confirmed: "Intelligent Optimization of Tower Crane Location and Layout Based on Firefly Algorithm", *Computational Intelligence and Neuroscience*, 2022 (PubMed PMID 35814533, PMCID PMC9259253: https://pubmed.ncbi.nlm.nih.gov/35814533/). I could not read the full author list, article ID or DOI because PMC showed a captcha and PubMed rate-limited me. **Action:** confirm the authors and article ID on the PubMed page, and check for a retraction notice. Hindawi's *CIN* retracted many 2022 papers in 2023, so this check matters before citing. |
| 6 | Yin et al. 2023, *MBE* 20(3) | **Verified. Check the context it is cited in.** | Yin, J., Li, J., Fang, Y., & Yang, A. (2023). Service scheduling optimization for multiple tower cranes considering the interval time of the cross-tasks. *Mathematical Biosciences and Engineering, 20*(3), 5993–6015. https://doi.org/10.3934/mbe.2023259. This is a scheduling paper (NSGA-II, overlapping areas), not a location paper. |
| 7 | Zhang et al. 1999 | **Verified** | Zhang, P., Harris, F. C., Olomolaiye, P. O., & Holt, G. D. (1999). Location optimization for a group of tower cranes. *Journal of Construction Engineering and Management, 125*(2), 115–122. https://doi.org/10.1061/(ASCE)0733-9364(1999)125:2(115). It is the original source of the hook-travel-time model coefficients α (radial–tangential coordination) = 1 and β (vertical–horizontal coordination) = 0.25. A related precursor is Olomolaiye, Zhang & Harris (1996), *Building Research and Information, 24*(2), 113–123 (single-crane simulation model; https://uwe-repository.worktribe.com/index.php/output/1104805). |

### Crane kinematic speeds: what the literature actually reports

| Source (where found) | Hoist V_h | Trolley/radial V_a | Slewing V_ω | Notes |
|---|---|---|---|---|
| Tam, Tong & Chan (2001), *JCEM* 127(4), 315–321. Values taken from the tables in Lien & Cheng (ISARC 2013, https://www.iaarc.org/publications/fulltext/isarc2013Paper115.pdf) and Kaveh & Vazirinia (2018, https://doi.org/10.3311/PPci.11816) | 35–60 m/min (**0.58–1.0 m/s**) | 33.1–53.3 m/min (**0.55–0.89 m/s**) | 2.8–7.57 rad/min (**0.45–1.20 rpm**) | This is the benchmark Hong Kong public-housing case. Kaveh & Vazirinia state that Huang et al. (2011) used the same Tam et al. case. α = 1 and β = 0.25 come from Zhang et al. (1999). |
| Huang & Wong (2018), *Autom Constr* 89 (Liebherr 4000 HC 100 spec sheet) | 136 m/min (2.27 m/s) | 60 m/min (1.0 m/s) | "0.5 rad/min" as printed (≈0.08 rpm; probably a typo for 0.5 rpm) | Taken from the manufacturer's spec sheet, with no academic source cited. |
| Zhang et al. (1999) | – | – | – | The abstract gives no speeds. The paper is the source of the travel-time formulation and of α and β. |
| Zhou et al. (2023); Fu et al. (2024); Shen et al. (2026) | symbols only | symbols only | symbols only | None of the text I could read gave numeric values or a source. |

**Assessment of the report's values** (slewing ~0.5–0.8 rpm, trolley 0.5–1 m/s, hoist 0.3–1 m/s):
- Slewing and trolley ranges sit inside the Tam et al. (2001) ranges. Cite **Tam et al. (2001)**, with α and β from **Zhang et al. (1999)**.
- The hoist lower bound of 0.3 m/s is below the literature range (0.58 m/s minimum). Either justify it with a specific crane spec sheet (e.g., a heavy-duty PPVC crane under full load) or raise it.
- I could not read the full text of Huang (2011) directly. Cite the speeds to Tam et al. (2001), the primary source, not to Huang (2011).
- Tam et al. (2001) itself was verified only through two papers that cite it. Its full title is "Genetic algorithm for optimizing supply locations around tower crane", and I did not confirm its DOI.

---

## Part 2: Annotated bibliography (APA 7)

### (a) Tower crane location and supply/pick-up point optimisation

1. **Huang, C., Wong, C. K., & Tam, C. M. (2011).** Optimization of tower crane and material supply locations in a high-rise building site by mixed-integer linear programming. *Automation in Construction, 20*(5), 571–580. https://doi.org/10.1016/j.autcon.2010.11.023
   - *Finding:* Linearising the quadratic assignment model and solving it as a MILP with branch-and-bound improved the objective by about 7% over GA solutions. The model also allows several materials to share one supply point.
   - *Supports:* **LR, M**. This is the baseline MILP formulation and the benchmark for comparing exact and metaheuristic methods.

2. **Huang, C., & Wong, C. K. (2018).** Optimization of crane setup location and servicing schedule for urgent material requests with non-homogeneous and non-fixed material supply. *Automation in Construction, 89*, 183–198. https://doi.org/10.1016/j.autcon.2018.01.015
   - *Finding:* A binary MILP (Gurobi) that optimises crane location and service sequence together cut total operation time to 40.51 min, against 44–63 min for dispatching heuristics. The model is single-crane only, and multi-crane and spatial-conflict constraints are left as future work.
   - *Supports:* **M, D**. It is the clearest precedent for coupling location with sequence.

3. **Abdelmegid, M. A., Shawki, K. M., & Abdel-Khalek, H. (2015).** GA optimization model for solving tower crane location problem in construction sites. *Alexandria Engineering Journal, 54*(3), 519–526. https://doi.org/10.1016/j.aej.2015.05.011
   - *Finding:* A GA that minimises total hook transportation time finds good crane locations on a numerical example.
   - *Supports:* **LR**. Representative GA approach.

4. **Kaveh, A., & Vazirinia, Y. (2018).** Optimization of tower crane location and material quantity between supply and demand points: A comparative study. *Periodica Polytechnica Civil Engineering*. https://doi.org/10.3311/PPci.11816
   - *Finding:* On single-crane and multi-crane benchmarks, ECBO beat PSO, CBO, VPS and EVPS. The paper reuses the Tam et al. (2001) speed parameters.
   - *Supports:* **LR, M**. Gives benchmark data and kinematic values.

5. **Moussavi Nadoushani, Z. S., Hammad, A. W. A., & Akbarnezhad, A. (2017).** Location optimization of tower crane and allocation of material supply points in a construction site considering operating and rental costs. *Journal of Construction Engineering and Management, 143*(1). https://doi.org/10.1061/(ASCE)CO.1943-7862.0001215
   - *Finding:* Crane position changes the load moment the crane must carry and therefore its rental cost. Ignoring this causes large errors when element weights vary widely, as they do in precast work.
   - *Supports:* **LR, M, D**. This is the key paper for the capacity-radius link (see also section d). Authors confirmed via the published closure, https://doi.org/10.1061/(ASCE)CO.1943-7862.0001558.

6. **Ji, Y., & Leite, F. (2020).** Optimized planning approach for multiple tower cranes and material supply points using mixed-integer programming. *Journal of Construction Engineering and Management, 146*(3). https://doi.org/10.1061/(ASCE)CO.1943-7862.0001781
   - *Finding:* Optimising the cranes and supply points together, instead of one crane at a time, reduced operation time by 6.8% and cost by 3.6% in a two-crane case.
   - *Supports:* **LR, M**.

7. **Dasović, B., Galić, M., & Klanšek, U. (2019).** Active BIM approach to optimize work facilities and tower crane locations on construction sites with repetitive operations. *Buildings, 9*(1), 21. https://doi.org/10.3390/buildings9010021
   - *Finding:* A BIM-to-optimiser-to-BIM loop that minimises cycle duration substantially improved the initial crane and depot positions.
   - *Supports:* **LR, D**. Shows how BIM can supply the inputs.

8. **Hyun, H., Park, M., Lee, D., & Lee, J. (2021).** Tower crane location optimization for heavy unit lifting in high-rise modular construction. *Buildings, 11*(3), 121. https://doi.org/10.3390/buildings11030121
   - *Finding:* A GA jointly chooses the crane model, crane location and trailer (pick-up) location for heavy modular units at minimum cost.
   - *Supports:* **LR, M**. This is the closest analogue to a PPVC pick-up point problem.

9. **Zhou, C., Dai, F., Xiao, Z., & Liu, W. (2023).** Location optimization of tower cranes on high-rise modular housing projects. *Buildings, 13*(1), 115. https://doi.org/10.3390/buildings13010115
   - *Finding:* A MILP selects crane type, crane location and trailer parking positions for multi-crane modular housing at minimum total crane cost.
   - *Supports:* **LR, M**.

10. **Wang, R. D., Zayed, T., Eltoukhy, A. E. E., & Wu, H. (2024).** Integrated planning approach for optimizing tower crane and truck locations in modular integrated construction. *Journal of Construction Engineering and Management, 150*(9), 04024121. https://doi.org/10.1061/JCEMD4.COENG-14200
    - *Finding:* An ILP that places the crane and truck positions together across the whole site cut crane operating time and carbon emissions by 19.4–37.9% on three Hong Kong MiC projects.
    - *Supports:* **LR, M, D**. This is the strongest recent benchmark for MiC/PPVC.

11. **Shen, H., Xu, L., Jiang, K., Wang, W., Xia, Y., Lu, R., & Huang, C. (2026).** Multi-stage tower-crane layout optimization incorporating relocation penalties and operational constraints. *Buildings, 16*(18), 3618. https://doi.org/10.3390/buildings16183618
    - *Finding:* A dynamic multi-stage MILP that includes relocation penalties saved 33.2% against the contractor's plan and 6.24% against a static stage-wise layout. The result is optimal only within the predefined candidate set.
    - *Supports:* **LR, D**. Shows the current state of the art, and the authors' candidate-set limitation is a gap the FYP can cite.

12. **Tam, C. M., & Tong, T. K. L. (2003).** GA–ANN model for optimizing the locations of tower crane and supply points for high-rise public housing construction. *Construction Management and Economics, 21*(3), 257–266. https://doi.org/10.1080/0144619032000049665
    - *Finding:* An ANN predicts crane operation times and a GA uses those predictions to optimise the crane and supply point locations. This is an early surrogate-assisted approach.
    - *Supports:* **LR**. The historical anchor for section (e).

### (b) Lifting/erection sequence for precast and modular construction

13. **Wang, Y., Yuan, Z., & Sun, C. (2018).** Research on assembly sequence planning and optimization of precast concrete buildings. *Journal of Civil Engineering and Management, 24*(2), 106–115. https://doi.org/10.3846/jcem.2018.458
    - *Finding:* A BIM plus improved GA method optimises the PC assembly sequence to reduce assembly difficulty, and the sequence can be adjusted dynamically during construction.
    - *Supports:* **LR, M**. Precedent for GA-based sequence encoding.

14. **Zhang, W., Zhang, H., & Yu, L. (2023).** Collaborative planning for stacking and installation of prefabricated building components regarding crane-collision avoidance. *Journal of Construction Engineering and Management, 149*(6). https://doi.org/10.1061/JCEMD4.COENG-12955
    - *Finding:* Binary PSO plans on-site stacking (pick-up positions) and installation sequence together, under collision-avoidance constraints for overlapping cranes, to shorten the precast schedule.
    - *Supports:* **LR, M**. Very close to the FYP scope.

15. **Jiang, Y., Li, M., Li, M., Liu, X., Zhong, R. Y., Pan, W., & Huang, G. Q. (2022).** Digital twin-enabled real-time synchronization for planning, scheduling, and execution in precast on-site assembly. *Automation in Construction, 141*, 104397. https://doi.org/10.1016/j.autcon.2022.104397
    - *Finding:* A digital-twin framework synchronises assembly planning, scheduling and execution on site. I saw metadata only, not the abstract.
    - *Supports:* **D**. Useful for the future-work and implementation discussion.

16. **Kim, S., Oh, J., & Lim, J. (2024).** Development of an algorithm for crane trajectory distance calculation for erection of precast concrete members. *Buildings, 14*(1), 11. https://doi.org/10.3390/buildings14010011
    - *Finding:* The algorithm computes horizontal and vertical boom-rotation trajectory distances for each candidate crawler-crane erection plan. Those distances feed cost, time, CO₂ and energy estimates.
    - *Supports:* **LR**, scoped to precast erection with mobile cranes only.

17. **Agrawal, A. K., Zou, Y., Jin, H., Abdelmegid, M., & Gonzalez, V. (2025).** Automated assembly sequence planning and scheduling in precast building projects using reinforcement learning. In *Proceedings of the 42nd International Symposium on Automation and Robotics in Construction (ISARC 2025)* (pp. 1355–1362). IAARC. https://www.iaarc.org/publications/fulltext/175_Automated_assembly_sequence_planning_and_scheduling_in_precast_building_projects_using_reinforcement_learning.pdf
    - *Finding:* A PPO agent with temporal graph embeddings enforces structural-support precedence through action masking. On a 34-wall case it beat a DQN+GNN baseline.
    - *Supports:* **LR, M**. Shows precedence encoded as a support matrix with masking, which bridges sections (b) and (e).

### (c) Multi-crane scheduling, overlapping zones and collision avoidance

18. **Huang, C., Li, W., Lu, W., Xue, F., Liu, M., & Liu, Z. (2021).** Optimization of multiple-crane service schedules in overlapping areas through consideration of transportation efficiency and operational safety. *Automation in Construction, 127*, 103716. https://doi.org/10.1016/j.autcon.2021.103716
    - *Finding:* A MILP (Gurobi) for multi-crane service scheduling with non-collision constraints saved 6.54–18.07% of total operation cost compared with earlier methods.
    - *Supports:* **LR, M**.

19. **Yin, J., Li, J., Fang, Y., & Yang, A. (2023).** Service scheduling optimization for multiple tower cranes considering the interval time of the cross-tasks. *Mathematical Biosciences and Engineering, 20*(3), 5993–6015. https://doi.org/10.3934/mbe.2023259
    - *Finding:* NSGA-II with two-layer coding showed that a small increase in makespan buys a large increase in the time gap between cross-tasks in overlap zones. Case study: Daxing Airport.
    - *Supports:* **LR, D**. Supports discussing the safety–efficiency trade-off.

20. **Wang, Y., Zhao, W., Cui, W., & Zhou, G. (2024).** Multi-objective optimization of tasks scheduling problem for overlapping multiple tower cranes. *Buildings, 14*(4), 867. https://doi.org/10.3390/buildings14040867
    - *Finding:* NSGA-III plus TOPSIS allocates prefabricated-component lifts across two overlapping cranes, reducing collision risk and energy cost.
    - *Supports:* **LR, M**.

21. **Al Hattab, M., Zankoul, E., & Hamzeh, F. R. (2017).** Near-real-time optimization of overlapping tower crane operations: A model and case study. *Journal of Computing in Civil Engineering*. https://doi.org/10.1061/(ASCE)CP.1943-5487.0000666
    - *Finding:* Allowing work zones to overlap, combined with look-ahead planning and metaheuristics, shortened the schedule and balanced crane workload.
    - *Supports:* **LR, D**.

22. **Yin, J., Wang, H., Li, J., Zhang, Z., Cai, S., & Liu, W. (2024).** Dispatching rule design for tower crane scheduling in prefabricated construction via genetic programming. *Automation in Construction, 165*, 105588. https://doi.org/10.1016/j.autcon.2024.105588
    - *Finding:* Dispatching rules evolved by genetic programming beat hand-designed rules for dynamic crane scheduling in prefabricated construction, with lower variance.
    - *Supports:* **LR, D**. A learning-based alternative to solving each schedule from scratch.

23. **Zou, C., Zhu, J., Quan, X., Wang, Z., Wang, Q., Mei, Z., & Zhou, K. (2026).** Optimization of multi-building tower crane scheduling for lean prefabricated construction. *Buildings, 16*(13), 2528. https://doi.org/10.3390/buildings16132528
    - *Finding:* PSO beat GA and ABC. Crane operating time fell by 23.9% and 12.2%, and cost by about 8%.
    - *Supports:* **LR, D**. Useful for a metaheuristic comparison.

### (d) Crane load chart / capacity–radius constraints in layout optimisation

24. **Briskorn, D., & Dienstknecht, M. (2019).** Mixed-integer programming models for tower crane selection and positioning with respect to mutual interference. *European Journal of Operational Research, 273*(1), 160–174. https://doi.org/10.1016/j.ejor.2018.07.033
    - *Finding:* The paper presents four MIP formulations for joint crane selection and positioning (radius, height and cost per crane type) with interference and obstacle constraints, plus a complexity analysis and CPLEX benchmarks.
    - *Supports:* **LR, M**. Provides the formal OR framing for selection with capacity.

25. **Fu, Y., Bu, J., Lin, J., Liu, J., & Zhang, C. (2024).** Selection and layout optimization of double tower cranes. *Buildings, 14*(6), 1705. https://doi.org/10.3390/buildings14061705
    - *Finding:* A pair of tower cranes can deliver more than twice the lifting efficiency of one crane of the same model. When lifting times are similar, a value-engineering selection gives the cheapest option.
    - *Supports:* **LR, D**.

Also relevant to (d): Moussavi Nadoushani et al. (2017) (#5, load moment vs location), Hyun et al. (2021) (#8), Zhou et al. (2023) (#9) and Shen et al. (2026) (#11). All of them pick crane type or capacity together with location.

### (e) Surrogate models, ML and RL in crane planning

26. **Li, R., Chi, H.-L., Peng, Z., Li, X., & Chan, A. P. C. (2023).** Automatic tower crane layout planning system for high-rise building construction using generative adversarial network. *Advanced Engineering Informatics, 58*, 102202. https://doi.org/10.1016/j.aei.2023.102202
    - *Finding:* CraneGAN generates crane layouts directly from drawings. It was more robust and much faster than a GA and an exact method.
    - *Supports:* **LR, D**. The leading example of a learned surrogate for layout.

27. **Hu, S., Fang, Y., & Bai, Y. (2021).** Automation and optimization in crane lift planning: A critical review. *Advanced Engineering Informatics, 49*, 101346. https://doi.org/10.1016/j.aei.2021.101346
    - *Finding:* Crane planning research is fragmented: most studies optimise one decision in one scenario. The authors propose an integrated BIM-based lift-planning framework.
    - *Supports:* **LR, D**. Directly supports the FYP's integration argument.

28. **Zhu, A., Zhang, Z., & Pan, W. (2022).** Crane-lift path planning for high-rise modular integrated construction through metaheuristic optimization and virtual prototyping. *Automation in Construction, 141*, 104434. https://doi.org/10.1016/j.autcon.2022.104434
    - *Finding:* A hybrid PSO–simulated annealing algorithm found collision-free MiC lift paths better than other metaheuristics, and was validated in virtual prototyping.
    - *Supports:* **LR, D**.

29. **Tarutani, A., & Ishida, K. (2020).** Accuracy and generality of trained models for lift planning using deep reinforcement learning: Optimization of the crane hook movement between two points. In *Proceedings of the 37th ISARC* (pp. 538–546). https://doi.org/10.22260/ISARC2020/0074
    - *Finding:* The DRL hook-path policy produced paths about 3.6 times the shortest path and failed outside the slewing range it was trained on.
    - *Supports:* **D**. Shows the generalisation limits of RL, an argument for surrogate-assisted optimisation over pure RL.

Also relevant: Tam & Tong (2003) (#12, GA–ANN surrogate), Yin et al. (2024) (#22, GP-learned rules) and Agrawal et al. (2025) (#17, PPO with precedence masking).

### (f) Singapore PPVC / DfMA context

30. **Building and Construction Authority (BCA). (n.d.).** *Prefabricated Prefinished Volumetric Construction (PPVC)*. Retrieved October 19, 2026, from https://www1.bca.gov.sg/buildsg/productivity/design-for-manufacturing-and-assembly-dfma/prefabricated-prefinished-volumetric-construction-ppvc
    - *Finding:* PPVC has been required on selected GLS non-landed residential sites since 1 Nov 2014. BCA claims up to 40% manpower/time productivity gains and up to 30% shorter floor cycle times. It stresses appropriately sized and strategically placed cranes, just-in-time installation without double handling, and module weight as the key hoisting factor.
    - *Supports:* **LR (Introduction), D**.
    - Companion document: BCA *PPVC Guidebook*, https://www1.bca.gov.sg/docs/default-source/docs-corp-buildsg/ppvc_guidebook.pdf

31. **Hwang, B.-G., Shan, M., & Looi, K.-Y. (2018).** Key constraints and mitigation strategies for prefabricated prefinished volumetric construction. *Journal of Cleaner Production, 183*, 183–193. URL: https://faculty.csu.edu.cn/shanming/en/lwcg/77157/content/15131.htm (DOI not confirmed; look it up on ScienceDirect).
    - *Finding:* A Singapore (NUS) study of the constraints on PPVC adoption and how to mitigate them. I confirmed only the title and bibliographic data, so read the paper before citing specific findings.
    - *Supports:* **LR**.

32. **Wuni, I. Y., Shen, G. Q., & Osei-Kyei, R. (2021).** Evaluating the critical success criteria for prefabricated prefinished volumetric construction projects. *Journal of Financial Management of Property and Construction, 26*(2), 279–297. https://doi.org/10.1108/JFMPC-03-2020-0013
    - *Finding:* In a survey of international PPVC experts, schedule adherence, quality, safety, client satisfaction and cost were the top success criteria, with time weighted among the highest.
    - *Supports:* **LR, D**. Justifies using time or makespan as the objective.

---

## Part 3: Gaps this FYP v2 can claim to address

1. **Location, pick-up points and erection sequence are rarely optimised together for PPVC.** Location and pick-up papers (#1, #5, #8–#11) assume fixed or unordered demand. Sequence papers (#13, #14, #17) assume a fixed crane location. Huang & Wong (2018) couples location and sequence but only for one crane, with no precedence and no capacity checks. A bi-level or nested model (outer loop: crane and pick-up location; inner loop: precedence-feasible sequence) is a defensible contribution. Hu et al. (2021) explicitly call for this kind of integration.
2. **Using the radius-dependent load chart, not a single capacity value.** Most models check only the maximum radius, or treat crane type as a cost category (#9, #11, #24). Only Moussavi Nadoushani et al. (2017) link location to the required load moment. PPVC modules (often 20–40 t) are heavy enough that the radius-capacity curve will exclude many candidate pick-up and placement pairs. Modelling capacity as a function of radius for each lift is a clear gap.
3. **Structural precedence in PPVC stacking.** Modules sit on modules below them and cores come before modules. Precedence is handled explicitly mainly in RL/masking work (#17) and older GA work (#13), not in location models. Adding precedence constraints, such as a support matrix, to the crane-time objective is new for tower-crane PPVC.
4. **A continuous search space instead of a predefined candidate set.** Recent exact MILPs (#10, #11, #24) are optimal only within the candidate locations they are given (Shen et al., 2026 say so explicitly). Metaheuristics or a surrogate over a continuous or fine-grid space, benchmarked against the MILP, can show whether a predefined candidate set costs optimality.
5. **Surrogate-assisted optimisation for fast what-if studies.** ML in this area covers either the layout end to end (CraneGAN, #26) or path planning (#28, #29). Using a trained surrogate (e.g., GP or gradient boosting on simulated cycle times) to speed up a GA/PSO search over layout plus sequence is largely unexplored since Tam & Tong (2003).
6. **Singapore PPVC as a case.** Most MiC crane-layout case studies are from Hong Kong (#10, #28), China (#20, #23) or Korea (#8, #16). A case built on a Singapore GLS PPVC project, with BCA's JIT and no-double-handling guidance as constraints, would be new context.
7. **Citing kinematic parameters correctly.** Many papers reuse the Tam et al. (2001) speeds without saying so. Running a sensitivity analysis on slewing, trolley and hoist speeds (±30%) and on α/β shows whether the optimal layout stays the same, which is a cheap but rarely reported robustness check.

---

### Verification notes
- These URLs could not be read: the Crossref API (blocked by the proxy and by a permission timeout), PMC (captcha), PubMed (rate-limited), the Emerald ECAM pages (captcha), and the EdUHK repository ("Integrated reinforcement and imitation learning for tower crane lift path planning", so it is excluded).
- I excluded "Discretized Cell Modeling for Optimal Layout of Multiple Tower Cranes" (*JCEM* 149(8), 2023, https://ascelibrary.com/doi/abs/10.1061/JCEMD4.COENG-13146; MILP on a cell grid, 10.7% rental-cost saving) from the numbered list because I could not confirm its authors. Add it once you have them.
- Article numbers for the ASCE papers #5, #6 and #14 were not shown on the pages I accessed. Add them from the DOI landing pages.
