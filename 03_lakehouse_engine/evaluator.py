import math
from typing import List, Dict, Any, Tuple

def calculate_discrepancies(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Computes discrepancies between predicted and actual metrics for each record.
    Expected keys per record:
      - 'transaction_id': str
      - 'predicted_cost': float
      - 'actual_cost': float
      - 'predicted_delay_hours': float
      - 'actual_delay_hours': float
    """
    evaluated_records = []
    for r in records:
        pred_cost = float(r.get("predicted_cost", 0.0))
        act_cost = float(r.get("actual_cost", 0.0))
        pred_delay = float(r.get("predicted_delay_hours", 0.0))
        act_delay = float(r.get("actual_delay_hours", 0.0))

        cost_discrepancy = round(act_cost - pred_cost, 2)
        delay_discrepancy = round(act_delay - pred_delay, 2)

        cost_pct_error = round(abs(cost_discrepancy) / act_cost * 100, 2) if act_cost > 0 else 0.0

        evaluated = dict(r)
        evaluated["cost_discrepancy"] = cost_discrepancy
        evaluated["delay_discrepancy"] = delay_discrepancy
        evaluated["cost_error_pct"] = cost_pct_error
        evaluated_records.append(evaluated)

    return evaluated_records

def compute_aggregate_metrics(evaluated_records: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculates overall operational accuracy metrics (MAE, RMSE, Mean Error Pct).
    """
    n = len(evaluated_records)
    if n == 0:
        return {"mae_cost": 0.0, "rmse_cost": 0.0, "mae_delay": 0.0, "mape_cost": 0.0}

    total_abs_cost_err = sum(abs(r["cost_discrepancy"]) for r in evaluated_records)
    total_sq_cost_err = sum(r["cost_discrepancy"] ** 2 for r in evaluated_records)
    total_abs_delay_err = sum(abs(r["delay_discrepancy"]) for r in evaluated_records)
    total_mape_cost = sum(r["cost_error_pct"] for r in evaluated_records)

    return {
        "mae_cost": round(total_abs_cost_err / n, 2),
        "rmse_cost": round(math.sqrt(total_sq_cost_err / n), 2),
        "mae_delay": round(total_abs_delay_err / n, 2),
        "mape_cost": round(total_mape_cost / n, 2),
    }

if __name__ == "__main__":
    print("[EVALUATOR] Running operational discrepancy test batch...")
    sample_records = [
        {"transaction_id": "tx_201", "predicted_cost": 120.0, "actual_cost": 125.5, "predicted_delay_hours": 2.0, "actual_delay_hours": 2.5},
        {"transaction_id": "tx_202", "predicted_cost": 45.0, "actual_cost": 44.0, "predicted_delay_hours": 1.0, "actual_delay_hours": 1.0},
        {"transaction_id": "tx_203", "predicted_cost": 300.0, "actual_cost": 340.0, "predicted_delay_hours": 4.0, "actual_delay_hours": 6.5},
    ]

    discrepancies = calculate_discrepancies(sample_records)
    metrics = compute_aggregate_metrics(discrepancies)

    print(f"✓ Processed {len(discrepancies)} evaluation records.")
    for d in discrepancies:
        print(f"  - {d['transaction_id']}: Cost Diff: ${d['cost_discrepancy']} ({d['cost_error_pct']}%), Delay Diff: {d['delay_discrepancy']}h")
    print(f"\n[SUMMARY METRICS]")
    print(f"  Cost MAE  : ${metrics['mae_cost']}")
    print(f"  Cost RMSE : ${metrics['rmse_cost']}")
    print(f"  Delay MAE : {metrics['mae_delay']} hours")
    print(f"  Cost MAPE : {metrics['mape_cost']}%")