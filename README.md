AuraFit: Evolutionary Exercise

Scheduler

AuraFit is a high-performance heuristic optimization engine designed to solve the
Resource-Constrained Project Scheduling Problem (RCPSP) as applied to human
physiology. Using a Genetic Algorithm, AuraFit generates 7-day training microcycles that
maximize volume and movement diversity while strictly adhering to hard recovery and
fatigue constraints.

 Key Features
 Global Optimization: Unlike sequential &quot;workout of the day&quot; apps, AuraFit evaluates
an entire 7-day chromosome simultaneously to flatten the fatigue curve.
 Multi-Objective Fitness: Balances session density, biomechanical taxonomy coverage,
and exercise priority.
 Portable Data Layer: Decoupled SQLite architecture for zero-configuration
deployments.
 Automated Visualization: Generates scaling curves and fatigue distribution charts
using Matplotlib.

 Installation &amp; Setup
1. Clone &amp; Environment
Ensure you have Python 3.11 or higher installed.
# Navigate to project root
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
pip install -r requirements.txt
2. Data Migration (Optional)
The project comes with a pre-populated data/exercise_vault.db. If you need to re-migrate
from a local Microsoft SQL Server instance to the portable format:
python migrate_to_sqlite.py

 Running the Scheduler
To execute the evolutionary search and generate an optimized workout plan:
python -m src.main

The engine will run for the configured generations (default 200) and output the Final
Evolved Workout Plan with a fitness score directly to the terminal.

 Project Structure
 src/ The Evolutionary Core (Engine, Evaluator, Individual models).
 db_connector.py Abstracted Data Access Layer (SQLite-based).
 main.py Application entry point.
 data/ Contains exercise_vault.db and user configuration JSONs.
 results/ Destination for generated performance charts and distribution logs.
 migrate_to_sqlite.py Utility script for migrating from SQL Server to SQLite.

Algorithmic Logic
Chromosomal Encoding
The genotype is modeled as a discrete map where keys (0-6) represent days of the week.
This allows the GA to swap entire &quot;training blocks&quot; (days) during crossover, preserving
internal session synergy.
The Fitness Judge
The fitness function evaluates three primary metrics:
 Safety (The Stick): Massive penalties for Daily Fatigue &gt; 80 units or Session Time &gt; 60
mins.
 Density (The Carrot): Rewards for reaching &gt;80% time utilization to prevent &quot;Lazy AI&quot;
behavior.
 Taxonomy: Weighted scores for satisfying all biomechanical categories (Squat, Hinge,
Push, Pull, etc.).

 Performance Benchmarks
AuraFit demonstrates O(N) Linear Scaling relative to population size.
Convergence: Typically stabilizes within 100 generations.
 Peak Fitness: ~135.46 utility (achieved through global search) vs. ~38.40 for baseline
greedy heuristics.

