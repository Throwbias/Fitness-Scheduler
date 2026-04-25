import csv
import os

def save_results(metrics_list: list[dict], output_dir: str = "results", filename: str = "summary.csv"):
    """
    Saves the experimental metrics to a CSV file for analysis.

    Args:
        metrics_list (list[dict]): A list of dictionaries containing the scoring metrics.
        output_dir (str): The folder to save the results in.
        filename (str): The name of the output CSV file.
    """
    # Ensure the results directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, filename)
    
    # If the list is empty, do nothing
    if not metrics_list:
        return
        
    # Extract the column headers dynamically from the first dictionary's keys
    headers = metrics_list[0].keys()
    
    # Write the data to a CSV
    with open(filepath, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(metrics_list)