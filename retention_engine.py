
import sqlite3
import csv
from pathlib import Path
from collections import Counter

# Project files
BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "churn_project.sqlite"
INPUT_FILE = BASE_DIR / "churn_risk_segments.csv"
OUTPUT_FILE = BASE_DIR / "retention_recommendations.csv"

# Load customer risk segments
with open(INPUT_FILE, newline="", encoding="utf-8") as f:
    customers = list(csv.DictReader(f))

# Get each customer's most recent recorded cancellation reason.
# This is historical information, not necessarily current intent.
conn = sqlite3.connect(DB_FILE)

query = """
SELECT customer_id, cancellation_reason, attempt_date
FROM cancellation_events
ORDER BY attempt_date DESC
"""

reason_rows = conn.execute(query).fetchall()
conn.close()

latest_reason = {}

for customer_id, reason, attempt_date in reason_rows:
    if customer_id not in latest_reason:
        latest_reason[customer_id] = reason

def recommend_offer(customer):
    status = customer["status"].strip().lower()
    risk = customer["risk_segment"].strip()
    customer_id = customer["customer_id"]

    reason = latest_reason.get(customer_id, "")
    reason = (reason or "").strip().lower()

    # Customers who have already canceled should not receive
    # active retention offers.
    if status == "canceled":
        return "no_offer", "Exclude from active retention campaign"

    # Paused customers need a reactivation approach, not
    # the same campaign used for active subscriptions.
    if status == "paused":
        return (
            "no_offer",
            "Review for a separate reactivation campaign"
        )

    # Only active customers enter the retention rules.
    if status != "active":
        return "no_offer", "Review subscription status before targeting"

    # Match known historical reasons to relevant interventions.
    # Validate these reasons against current customer intent
    # before using the offers in a real product.
    reason_to_offer = {
        "too_expensive": (
            "lower_cost_plan",
            "Present an eligible lower-priced plan"
        ),
        "temporary_break": (
            "account_pause",
            "Offer a suitable time-limited account pause"
        ),
        "low_usage": (
            "usage_guidance",
            "Show a personalized product walkthrough"
        ),
        "missing_feature": (
            "feature_information",
            "Explain relevant available features"
        ),
        "payment_issue": (
            "payment_recovery",
            "Help resolve the payment problem"
        ),
        "competitor_switch": (
            "value_comparison",
            "Explain relevant product differentiators"
        )
    }

    if reason in reason_to_offer:
        return reason_to_offer[reason]

    # When no recognized reason is available, use risk
    # as a fallback signal.
    if risk == "High risk":
        return (
            "personalized_retention",
            "Ask what would help the customer stay"
        )

    if risk == "Medium risk":
        return (
            "engagement_nudge",
            "Send a relevant engagement message"
        )

    return (
        "no_offer",
        "Continue the normal customer experience"
    )

# Generate recommendations
output_rows = []

for customer in customers:
    offer, action = recommend_offer(customer)

    output_rows.append({
        "customer_id": customer["customer_id"],
        "subscription_status": customer["status"],
        "risk_score": customer["risk_score"],
        "risk_segment": customer["risk_segment"],
        "cancellation_reason": latest_reason.get(
            customer["customer_id"], "no_recorded_reason"
        ) or "no_recorded_reason",
        "recommended_offer": offer,
        "recommended_action": action
    })

# Export recommendations
if output_rows:
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=output_rows[0].keys()
        )
        writer.writeheader()
        writer.writerows(output_rows)

# Print summary
print("\nDYNAMIC RETENTION ENGINE")
print("-" * 45)
print(f"Customers processed: {len(output_rows):,}")
print(f"Recommendations saved to: {OUTPUT_FILE.name}")

print("\nOFFER DISTRIBUTION")
offer_counts = Counter(
    row["recommended_offer"] for row in output_rows
)

for offer, count in offer_counts.most_common():
    print(f"{offer}: {count:,}")

print("\nRECOMMENDATIONS BY SUBSCRIPTION STATUS")
for status in sorted({
    row["subscription_status"] for row in output_rows
}):
    count = sum(
        row["subscription_status"] == status
        for row in output_rows
    )
    print(f"{status}: {count:,}")

print("\nNext: review retention_recommendations.csv")
