# Constraint-Based Workout Scheduling System

## Overview

This project implements a constraint-based scheduling system for generating weekly workout plans using a greedy heuristic algorithm. The system models training program design as a constrained optimization problem, balancing multiple factors such as time, fatigue, recovery, and movement coverage.

The goal is to construct feasible and high-quality training schedules while demonstrating how algorithmic techniques can be applied to a real-world domain.

---

## Key Features

* Constraint-based exercise filtering (time, fatigue, recovery, equipment)
* Greedy heuristic scheduler for plan construction
* Multi-objective scoring system (priority, coverage, utilization, fatigue balance)
* Random baseline for performance comparison
* Experimental evaluation using a Jupyter notebook

---

## Project Structure

```
FinalProject/
├── src/           # Core implementation (scheduler, models, scoring, etc.)
├── data/          # Input datasets (exercises and requests)
├── docs/          # Proposal and references
├── analysis/      # Experimental notebook
├── tests/         # Unit tests
├── results/       # Placeholder for future outputs
└── README.md
```

---

## How It Works

The system constructs a weekly training plan using a three-stage pipeline:

1. **Feasibility Filtering**
   Exercises are filtered based on constraints such as session time limits, fatigue caps, equipment availability, and recovery requirements.

2. **Scoring**
   Feasible exercises are evaluated using a heuristic scoring function that considers:

   * exercise priority
   * movement category coverage
   * goal alignment
   * time efficiency
   * fatigue cost

3. **Greedy Scheduling**
   The scheduler iteratively selects the highest-scoring feasible exercise until the session is filled.

---

## Experimental Evaluation

The project includes an experimental comparison between:

* **Greedy Scheduler** (heuristic-driven)
* **Random Baseline** (feasible but unguided)

Metrics used:

* Coverage Score
* Priority Score
* Time Utilization
* Fatigue Balance
* Constraint Violations

Experiments are implemented in:

```
analysis/experiments.ipynb
```

---

## Getting Started

### 1. Set up environment

```bash
python -m venv venv
source venv/Scripts/activate  # Windows (Git Bash)
```

### 2. Install dependencies

```bash
pip install matplotlib
```

### 3. Run the scheduler

```bash
python -m src.main
```

### 4. Run experiments

Open:

```
analysis/experiments.ipynb
```

and execute all cells.

---

## Current Status

Chapter 13 deliverables completed:

* Project proposal (docs/proposal.pdf)
* Working prototype (src/)
* Experimental plan and baseline comparison (analysis/)
* Literature review and references (docs/references.bib)

---

## Future Work

* Improve scoring function sensitivity
* Add structural evaluation metrics
* Explore alternative optimization methods (e.g., local search, DP approximations)
* Expand dataset and constraints

---

## Author

Aaron Tobias
