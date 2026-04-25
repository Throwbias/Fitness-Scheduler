# Constraint-Based Fitness Scheduler

## Overview
This project models weekly workout planning as a constrained optimization problem. It automatically generates feasible, scientifically grounded weekly workout plans by balancing hard physiological constraints (time limits, fatigue caps, equipment availability) with soft constraints (movement category coverage, priority exercises).

---

## System Architecture

The scheduling engine operates in two distinct algorithmic phases to ensure both speed and optimality:

### 1. Constructive Phase (Greedy Heuristic)
Rapidly builds a valid baseline schedule by iteratively evaluating and selecting the highest-scoring feasible exercises.

- Respects all hard constraints
- Produces a working initial solution
- Enables fast schedule construction

**Time Complexity:** `O(D * N * K)`

---

### 2. Refinement Phase (Local Search)
Optimizes the greedy baseline by exploring a neighborhood of adjacent schedules.

Supported mutation types:
- Insertions (build new sessions)
- Relocations (move exercises across days)
- Replacements (swap with unused exercises)
- Swaps (exchange between active days)

This phase helps:
- escape local minima
- improve fatigue balance (via variance minimization)
- better match weekly structure goals

---

## Project Structure

```text
FinalProject/
├── src/
│   ├── algorithms/          # Core schedulers (Greedy, Random, Local Search)
│   ├── data_structures/     # Data classes and models
│   ├── utils/               # Scoring, evaluation, and data loading
│   └── main.py              # Main execution pipeline and CLI
├── data/                    # JSON datasets and user request parameters
├── tests/                   # Pytest suite (correctness + performance)
├── analysis/                # Chart generation and visualization scripts
├── results/                 # Output CSVs and summaries
└── docs/                    # Academic proposals and reports
```

---

## Prerequisites

- Python **3.10+** (required for modern typing features such as `dict[str, Exercise]`)

---

## Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd FinalProject

# Set up a virtual environment
python -m venv venv

# Activate the environment

# macOS / Linux
source venv/bin/activate  

# Windows
venv\Scripts\activate

# Install required tools
pip install pytest black isort
```

---

## Usage

The scheduling pipeline is executed via CLI. Execution steps, constraint evaluations, and final metrics are printed to the console.

### Run with default parameters
```bash
python -m src.main
```

### Run with custom configurations
```bash
python -m src.main \
  --dataset data/exercises_large.json \
  --request data/sample_request.json \
  --iterations 500
```

---

## Running Tests

```bash
python -m pytest -v
```

Covers:
- correctness
- edge cases
- performance behavior

---

## Code Formatting

This project follows **PEP 8** standards.

Format code before committing:

```bash
isort .
black .
```

---

## Summary

This system demonstrates a hybrid optimization pipeline that combines:

- constraint-based filtering
- heuristic search (greedy)
- local optimization (neighborhood search)

to model realistic weekly training plans under competing physiological and structural constraints.