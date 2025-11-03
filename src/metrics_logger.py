"""
Metrics logging module for tracking API usage, costs, and performance.
"""

import json
import os
import csv
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path


class MetricsLogger:
    """
    Logger for tracking per-query metrics including tokens, latency, and costs.
    Supports both JSON and CSV output formats.
    """
    
    def __init__(self, output_dir: str = None):
        """
        Initialize the metrics logger.
        
        Args:
            output_dir: Directory to save metrics. Defaults to 'metrics' in project root.
        """
        if output_dir is None:
            # Default to metrics directory in project root
            project_root = Path(__file__).parent.parent
            output_dir = project_root / "metrics"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.json_file = self.output_dir / "metrics.json"
        self.csv_file = self.output_dir / "metrics.csv"
        
        # Initialize JSON file if it doesn't exist
        if not self.json_file.exists():
            self._initialize_json()
        
        # Initialize CSV file if it doesn't exist
        if not self.csv_file.exists():
            self._initialize_csv()
    
    def _initialize_json(self):
        """Initialize empty JSON metrics file."""
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump({"metrics": []}, f, indent=2)
    
    def _initialize_csv(self):
        """Initialize CSV file with headers."""
        headers = [
            "timestamp",
            "question",
            "model",
            "tokens_prompt",
            "tokens_completion",
            "total_tokens",
            "latency_ms",
            "estimated_cost_usd",
            "safety_flagged"
        ]
        
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
    
    def log(self, metrics: Dict[str, Any]):
        """
        Log metrics for a single query.
        
        Args:
            metrics: Dictionary containing metrics data
        """
        self._log_to_json(metrics)
        self._log_to_csv(metrics)
    
    def _log_to_json(self, metrics: Dict[str, Any]):
        """Append metrics to JSON file."""
        # Read existing data
        with open(self.json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Append new metrics
        data["metrics"].append(metrics)
        
        # Write back
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def _log_to_csv(self, metrics: Dict[str, Any]):
        """Append metrics to CSV file."""
        # Prepare row data with only the fields we want in CSV
        row = {
            "timestamp": metrics.get("timestamp", ""),
            "question": metrics.get("question", "")[:100],  # Truncate
            "model": metrics.get("model", ""),
            "tokens_prompt": metrics.get("tokens_prompt", 0),
            "tokens_completion": metrics.get("tokens_completion", 0),
            "total_tokens": metrics.get("total_tokens", 0),
            "latency_ms": metrics.get("latency_ms", 0.0),
            "estimated_cost_usd": metrics.get("estimated_cost_usd", 0.0),
            "safety_flagged": metrics.get("safety_flagged", False)
        }
        
        # Append to CSV
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            writer.writerow(row)
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Calculate summary statistics from logged metrics.
        
        Returns:
            Dictionary containing summary statistics
        """
        with open(self.json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        metrics_list = data.get("metrics", [])
        
        if not metrics_list:
            return {
                "total_queries": 0,
                "total_cost_usd": 0.0,
                "total_tokens": 0,
                "avg_latency_ms": 0.0,
                "avg_cost_per_query": 0.0
            }
        
        total_queries = len(metrics_list)
        total_cost = sum(m.get("estimated_cost_usd", 0) for m in metrics_list)
        total_tokens = sum(m.get("total_tokens", 0) for m in metrics_list)
        total_latency = sum(m.get("latency_ms", 0) for m in metrics_list)
        safety_flagged = sum(1 for m in metrics_list if m.get("safety_flagged", False))
        
        return {
            "total_queries": total_queries,
            "total_cost_usd": round(total_cost, 6),
            "total_tokens": total_tokens,
            "avg_latency_ms": round(total_latency / total_queries, 2),
            "avg_cost_per_query": round(total_cost / total_queries, 6),
            "avg_tokens_per_query": round(total_tokens / total_queries, 2),
            "safety_flagged_count": safety_flagged,
            "safety_flag_rate": round(safety_flagged / total_queries, 3) if total_queries > 0 else 0.0
        }
    
    def export_summary(self, output_file: str = None):
        """
        Export summary statistics to a JSON file.
        
        Args:
            output_file: Path to output file. Defaults to 'summary.json' in metrics dir.
        """
        if output_file is None:
            output_file = self.output_dir / "summary.json"
        else:
            output_file = Path(output_file)
        
        summary = self.get_summary_statistics()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        return summary


def main():
    """Test the metrics logger."""
    logger = MetricsLogger()
    
    # Generate test metrics
    test_metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "question": "Test question",
        "model": "gpt-4o-mini",
        "tokens_prompt": 50,
        "tokens_completion": 100,
        "total_tokens": 150,
        "latency_ms": 250.5,
        "estimated_cost_usd": 0.00025,
        "safety_flagged": False
    }
    
    logger.log(test_metrics)
    
    summary = logger.get_summary_statistics()
    print("Summary Statistics:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
