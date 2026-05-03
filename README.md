# AuraFit: Heuristic Exercise Scheduling via Genetic Algorithms (GA)

**Project Lead:** Aaron  
**Academic Context:** CS101 - Final Engineering Project  
**Submission Date:** May 2026  

---

## 📋 Project Overview
This project implements a **Genetic Algorithm (GA)** to solve the problem of automated exercise scheduling. The engine optimizes for user-defined fitness goals while strictly adhering to hard constraints like daily fatigue caps and session time limits. By simulating evolutionary processes, the system finds high-quality schedules that a simple randomized approach cannot achieve.

---

## 🏗️ System Architecture & Design Patterns
The system is built using a modular architecture to ensure separation of concerns, facilitating both unit testing and experimental reproducibility.

### 1. Data Layer (Relational SQLite)
The core of the system is a 3NF (Third Normal Form) relational database. This ensures data integrity and allows for complex relational queries when building the exercise pool.
* **Exercises Table:** Contains fatigue costs, duration, and priority scores.
* **MuscleGroups Table:** Manages many-to-many relationships to prevent overtraining specific anatomical regions.
* **Category Table:** Classifies exercises by biomechanical movement (Compound vs. Isolation).

### 2. Logic Layer (Heuristic Engine)
The `GeneticSolver` acts as the controller. It interfaces with the `Individual` and `Exercise` models to perform evolutionary operations.

### 3. Artifact Layer (Visualization)
A dedicated pipeline (`generate_artifacts.py`) uses `Matplotlib` to convert raw algorithmic performance data into analytical charts for peer review.

---

## 🧬 The Genetic Algorithm: Technical Deep-Dive

### Chromosome Encoding
Each `Individual` object contains a `chromosome` represented as a collection of workout sessions. 
* **Genes:** Individual exercises.
* **Loci:** The specific day/order within the weekly schedule.

### The Heuristic Fitness Function
The engine evaluates "fitness" (score out of 100) using a multi-objective weighted sum:
$$Fitness = (W_p \cdot \text{PrioritySum}) - (W_f \cdot \text{FatigueOverages}) - (W_t \cdot \text{TimeOverages})$$
* **Hard Constraints:** If a schedule exceeds the `daily_fatigue_cap`, it receives a heavy penalty, effectively removing it from the gene pool in the next generation.
* **Soft Constraints:** Priority scores and category diversity act as positive reinforcements.

### Evolutionary Operators
1. **Tournament Selection:** Randomly selects a subset of the population and picks the best to move to the mating pool.
2. **Two-Point Crossover:** Swaps entire training days between two parents to preserve "building blocks" of good workouts.
3. **Random Resetting Mutation:** Occasionally replaces an exercise with a random one from the database to maintain genetic diversity and avoid local optima.

---

## 📊 Experimental Results & Analysis
The `/results/` directory contains 10+ high-quality artifacts proving the system's efficacy.

### Key Findings:
* **Convergence Stability:** The GA consistently reaches a fitness score >90 within 60 generations.
* **Computational Scaling:** Testing reveals that execution time increases linearly ($O(N)$) with population size, proving the algorithm is viable for large-scale enterprise databases.
* **Fatigue Management:** The `02_fatigue_distribution.png` artifact confirms that even under high-intensity requests, no session violates the user-defined safety threshold.

---

## 🛠️ Installation & Reproduction Guide

### 1. Environment Setup
The project requires Python 3.11+ and a virtual environment for dependency isolation.
```bash
# Create and activate environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
2. Database Initialization
Ensure the exercise_vault.db is in the data/ folder. The db_connector.py handles all connections via the standard sqlite3 library.

3. Running the Artifact Pipeline
To reproduce all charts used in the final report, run the root-level script:

Bash
python generate_artifacts.py
4. Running the Test Suite
The project includes a full suite of unit tests to verify GA logic and database connectivity:

Bash
pytest tests/

Developed for Educational Purposes.