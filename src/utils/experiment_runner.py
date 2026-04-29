import csv
import os
from datetime import datetime

def save_results(results_with_names: list[tuple[str, dict]], filename: str = "results/raw/experiment_results.csv"):
    """
    Saves the metrics from multiple algorithm runs into a CSV file.
    
    Args:
        results_with_names: A list of (algorithm_name, metrics_dict) tuples.
        filename: Path to the output CSV.
    """
    # 1. Ensure the directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # 2. Flatten the data for the CSV
    # We combine the algorithm name and the metrics into one flat dictionary
    flattened_data = []
    for algo_name, metrics in results_with_names:
        row = {"algorithm": algo_name, "timestamp": datetime.now().isoformat()}
        row.update(metrics)
        flattened_data.append(row)

    if not flattened_data:
        return

    # 3. Determine headers from the first row
    headers = flattened_data[0].keys()

    # 4. Write to CSV
    # 'a' (append) mode is used so you can run the script multiple times 
    # and compare different sessions in one file.
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode='a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        
        # Only write header if the file is new
        if not file_exists:
            writer.writeheader()
            
        writer.writerows(flattened_data)

    print(f"[SUCCESS] Results successfully appended to {filename}")