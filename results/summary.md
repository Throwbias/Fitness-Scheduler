# Experimental Results Summary

## Overview
This project evaluates three approaches to constructing weekly workout schedules:

- Greedy heuristic scheduler
- Random baseline scheduler
- Greedy + local search refinement

Experiments were conducted using a fixed dataset and 30 randomized trials for the baseline.

---

## Key Findings

### 1. Greedy vs Random Baseline
The greedy scheduler consistently produced stable and feasible plans with a total score of approximately 70.56.  

The random baseline exhibited high variance, with total scores ranging from approximately 66.16 to 92.78. This demonstrates that while many feasible schedules exist, their quality varies significantly depending on exercise selection.

---

### 2. Impact of Local Search Refinement
The local search refinement significantly improved the greedy solution:

- Greedy total score: ~70.56  
- Refined total score: ~93.83  

This represents a substantial improvement in overall schedule quality.

The most notable improvement occurred in fatigue balance:

- Greedy fatigue balance: ~0.11  
- Refined fatigue balance: 1.00  

This indicates that the greedy algorithm tends to produce uneven workload distribution across sessions, while local search effectively corrects this imbalance.

---

### 3. Comparison to Random Baseline
While some random trials achieved high scores (up to ~92.78), these were inconsistent and not guaranteed.

The refined algorithm consistently produced near-optimal results, outperforming the average random baseline and approaching the best observed random outcomes.

---

### 4. Runtime Analysis
All algorithms executed quickly on the current dataset:

- Greedy: ~0.0002 seconds  
- Random: ~0.0001 seconds  
- Refined: ~0.0046 seconds  

Although local search is more computationally expensive than greedy, the absolute runtime remains negligible for this problem size. This suggests that refinement is a practical addition for improving solution quality.

---

## Interpretation

The results highlight a key distinction between constructive and refinement-based algorithms:

- The greedy algorithm efficiently constructs a feasible schedule but does not account for global optimization.
- The local search algorithm improves the schedule by evaluating the plan holistically and correcting local imbalances.

This combination produces a strong balance between computational efficiency and solution quality.

---

## Limitations

- The dataset is relatively small, limiting the complexity of scheduling decisions.
- The scoring function heavily weights fatigue balance, which amplifies the impact of refinement.
- Local search uses a simple neighborhood (single replacement), which may miss more complex improvements.

---

## Future Work

- Implement more advanced local search moves (swaps, multi-step replacements)
- Introduce multi-week scheduling with progression
- Refine scoring weights for better balance across objectives
- Evaluate scalability on larger exercise datasets

---

## Conclusion

The experimental results demonstrate that while greedy heuristics are effective for quickly generating feasible solutions, they benefit significantly from refinement. Local search provides a simple yet powerful mechanism for improving global schedule quality, making it a valuable addition to the system.