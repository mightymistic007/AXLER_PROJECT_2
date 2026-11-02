from typing import List, Dict, Any

# Financial impact cost parameters (USD)
COST_PER_DELAY_HOUR = 45.0          # Average warehouse/carrier delay SLA penalty per hour
CUSTOMER_CHURN_RISK_COST = 25.0     # Estimated downstream lifetime value impact of failed/delayed fulfillment
DEFAULT_ACTION_COST = 15.0          # Average compute/re-routing operational cost per automated intervention

def calculate_disruption_impact(record: Dict[str, Any]) -> float:
    """
    Calculates the unmitigated financial disruption cost of a shipment/transaction delay.
    """
    delay_hours = max(0.0, float(record.get("actual_delay_hours", 0.0)))
    direct_delay_penalty = delay_hours * COST_PER_DELAY_HOUR
    
    # Severe delays (> 3 hours) carry customer churn probability risk
    churn_risk = CUSTOMER_CHURN_RISK_COST if delay_hours > 3.0 else 0.0
    return round(direct_delay_penalty + churn_risk, 2)

def evaluate_mitigation_roi(mitigation_events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluates net business value and ROI achieved through automated mitigation actions.
    Expected dict keys per event:
      - 'transaction_id': str
      - 'action_taken': str (e.g., 'REROUTE_EXPEDITED', 'ALTERNATIVE_FULFILLMENT')
      - 'unmitigated_delay_hours': float
      - 'mitigated_delay_hours': float
      - 'intervention_cost': float (optional, defaults to DEFAULT_ACTION_COST)
    """
    total_unmitigated_loss = 0.0
    total_mitigated_loss = 0.0
    total_intervention_cost = 0.0
    action_breakdown = []

    for event in mitigation_events:
        unmitigated_delay = float(event.get("unmitigated_delay_hours", 0.0))
        mitigated_delay = float(event.get("mitigated_delay_hours", 0.0))
        intervention_cost = float(event.get("intervention_cost", DEFAULT_ACTION_COST))

        # Financial impact modeling
        unmitigated_cost = calculate_disruption_impact({"actual_delay_hours": unmitigated_delay})
        mitigated_cost = calculate_disruption_impact({"actual_delay_hours": mitigated_delay})

        gross_saved = round(max(0.0, unmitigated_cost - mitigated_cost), 2)
        net_saved = round(gross_saved - intervention_cost, 2)

        total_unmitigated_loss += unmitigated_cost
        total_mitigated_loss += mitigated_cost
        total_intervention_cost += intervention_cost

        action_breakdown.append({
            "transaction_id": event.get("transaction_id"),
            "action_taken": event.get("action_taken"),
            "gross_saved_usd": gross_saved,
            "intervention_cost_usd": intervention_cost,
            "net_saved_usd": net_saved
        })

    net_business_value = round(total_unmitigated_loss - total_mitigated_loss - total_intervention_cost, 2)
    roi_percent = round((net_business_value / total_intervention_cost * 100), 2) if total_intervention_cost > 0 else 0.0

    return {
        "events_processed": len(mitigation_events),
        "total_unmitigated_loss_usd": round(total_unmitigated_loss, 2),
        "total_mitigated_loss_usd": round(total_mitigated_loss, 2),
        "total_intervention_cost_usd": round(total_intervention_cost, 2),
        "net_business_value_usd": net_business_value,
        "roi_percentage": roi_percent,
        "action_breakdown": action_breakdown
    }

if __name__ == "__main__":
    print("[DECISION ROI] Running financial impact and mitigation analysis...")

    sample_mitigations = [
        {
            "transaction_id": "tx_disrupt_01",
            "action_taken": "REROUTE_EXPEDITED_CARRIER",
            "unmitigated_delay_hours": 5.5,
            "mitigated_delay_hours": 1.0,
            "intervention_cost": 25.0
        },
        {
            "transaction_id": "tx_disrupt_02",
            "action_taken": "ALLOCATE_REGIONAL_BUFFER_STOCK",
            "unmitigated_delay_hours": 3.5,
            "mitigated_delay_hours": 0.5,
            "intervention_cost": 15.0
        },
        {
            "transaction_id": "tx_disrupt_03",
            "action_taken": "AUTOMATED_SUPPLIER_SWITCH",
            "unmitigated_delay_hours": 2.0,
            "mitigated_delay_hours": 0.0,
            "intervention_cost": 10.0
        }
    ]

    report = evaluate_mitigation_roi(sample_mitigations)

    print("\n" + "=" * 60)
    print("DECISION ROI & DISRUPTION MITIGATION FINANCIAL REPORT")
    print("=" * 60)
    print(f"Mitigation Interventions Processed : {report['events_processed']}")
    print(f"Projected Unmitigated Loss (SLA/Churn) : ${report['total_unmitigated_loss_usd']}")
    print(f"Actual Loss Post-Mitigation            : ${report['total_mitigated_loss_usd']}")
    print(f"Total Intervention Cost                : ${report['total_intervention_cost_usd']}")
    print(f"Net Value Added (Savings)              : ${report['net_business_value_usd']}")
    print(f"Return on Investment (ROI)             : {report['roi_percentage']}%")
    print("=" * 60)
    print("\nDetailed Event Savings:")
    for a in report["action_breakdown"]:
        print(f"  - [{a['transaction_id']}] {a['action_taken']} -> Net Saved: ${a['net_saved_usd']}")
    print("=" * 60)
    