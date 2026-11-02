from typing import List, Dict, Any
from evaluator import calculate_discrepancies, compute_aggregate_metrics

TOLERANCE_THRESHOLDS = {
    "max_cost_mae": 20.0,         # Maximum acceptable Mean Absolute Error in USD
    "max_cost_rmse": 30.0,        # Maximum acceptable Root Mean Squared Error
    "max_delay_mae_hours": 1.5,   # Maximum acceptable average delay deviation
    "max_mape_cost_pct": 10.0,    # Max percentage error
    "drift_violation_ratio": 0.35 # Flag if >35% of individual records violate bounds
}

def evaluate_drift(discrepancies: List[Dict[str, Any]]) -> Dict[str, Any]:
    metrics = compute_aggregate_metrics(discrepancies)
    total_records = len(discrepancies)
    
    if total_records == 0:
        return {"drift_detected": False, "reason": "No evaluation records provided.", "metrics": metrics}

    breached_records = [
        d for d in discrepancies 
        if abs(d.get("cost_discrepancy", 0.0)) > TOLERANCE_THRESHOLDS["max_cost_mae"]
        or abs(d.get("delay_discrepancy", 0.0)) > TOLERANCE_THRESHOLDS["max_delay_mae_hours"]
    ]
    
    violation_rate = round(len(breached_records) / total_records, 2)
    
    violations = []
    if metrics["mae_cost"] > TOLERANCE_THRESHOLDS["max_cost_mae"]:
        violations.append(f"Cost MAE (${metrics['mae_cost']}) exceeds limit (${TOLERANCE_THRESHOLDS['max_cost_mae']})")
    
    if metrics["rmse_cost"] > TOLERANCE_THRESHOLDS["max_cost_rmse"]:
        violations.append(f"Cost RMSE (${metrics['rmse_cost']}) exceeds limit (${TOLERANCE_THRESHOLDS['max_cost_rmse']})")

    if metrics["mae_delay"] > TOLERANCE_THRESHOLDS["max_delay_mae_hours"]:
        violations.append(f"Delay MAE ({metrics['mae_delay']}h) exceeds limit ({TOLERANCE_THRESHOLDS['max_delay_mae_hours']}h)")

    if violation_rate > TOLERANCE_THRESHOLDS["drift_violation_ratio"]:
        violations.append(f"Record violation rate ({violation_rate * 100}%) exceeds threshold ({TOLERANCE_THRESHOLDS['drift_violation_ratio'] * 100}%)")

    drift_detected = len(violations) > 0

    return {
        "drift_detected": drift_detected,
        "violation_count": len(violations),
        "violations": violations,
        "record_violation_rate": violation_rate,
        "metrics": metrics,
        "retraining_recommended": drift_detected
    }

if __name__ == "__main__":
    print("[DRIFT DETECTOR] Running baseline drift check...")

    test_discrepancies = [
        {"transaction_id": "tx_drift_01", "predicted_cost": 100.0, "actual_cost": 135.0, "predicted_delay_hours": 1.0, "actual_delay_hours": 3.8},
        {"transaction_id": "tx_drift_02", "predicted_cost": 50.0, "actual_cost": 78.0, "predicted_delay_hours": 2.0, "actual_delay_hours": 4.5},
        {"transaction_id": "tx_drift_03", "predicted_cost": 220.0, "actual_cost": 225.0, "predicted_delay_hours": 3.0, "actual_delay_hours": 3.2},
    ]

    calculated = calculate_discrepancies(test_discrepancies)
    report = evaluate_drift(calculated)

    print("\n" + "=" * 55)
    print("PRODUCTION DRIFT DIAGNOSTIC REPORT")
    print("=" * 55)
    print(f"Drift Detected        : {'YES (ACTION REQUIRED)' if report['drift_detected'] else 'NO (STABLE)'}")
    print(f"Retraining Triggered  : {report['retraining_recommended']}")
    print(f"Record Breach Ratio   : {int(report['record_violation_rate'] * 100)}%")
    print(f"Aggregate Metrics     : {report['metrics']}")
    
    if report["violations"]:
        print("\nThreshold Violations:")
        for v in report["violations"]:
            print(f"  [ALERT] {v}")
    print("=" * 55)
    