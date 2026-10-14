
import sqlite3
import csv

# Connect to the existing project database
conn = sqlite3.connect("churn_project.sqlite")
conn.row_factory = sqlite3.Row

query = """
WITH latest_activity AS (
    SELECT
        customer_id,
        MAX(event_date) AS last_active_date
    FROM product_events
    GROUP BY customer_id
),
cancellation_summary AS (
    SELECT
        customer_id,
        COUNT(*) AS cancellation_attempts,
        SUM(
            CASE
                WHEN outcome = 'canceled' THEN 1
                ELSE 0
            END
        ) AS canceled_attempts,
        SUM(
            CASE
                WHEN outcome = 'retained' THEN 1
                ELSE 0
            END
        ) AS retained_attempts,
        MAX(attempt_date) AS last_cancellation_date
    FROM cancellation_events
    GROUP BY customer_id
),
payment_summary AS (
    SELECT
        customer_id,
        SUM(
            CASE
                WHEN payment_status != 'paid' THEN 1
                ELSE 0
            END
        ) AS failed_payments
    FROM payments
    GROUP BY customer_id
)
SELECT
    c.customer_id,
    s.plan,
    s.status,
    s.monthly_price,
    p.last_active_date,
    COALESCE(cs.cancellation_attempts, 0) AS cancellation_attempts,
    COALESCE(cs.canceled_attempts, 0) AS canceled_attempts,
    COALESCE(cs.retained_attempts, 0) AS retained_attempts,
    COALESCE(ps.failed_payments, 0) AS failed_payments
FROM customers c
LEFT JOIN subscriptions s
    ON c.customer_id = s.customer_id
LEFT JOIN latest_activity p
    ON c.customer_id = p.customer_id
LEFT JOIN cancellation_summary cs
    ON c.customer_id = cs.customer_id
LEFT JOIN payment_summary ps
    ON c.customer_id = ps.customer_id
"""

customers = conn.execute(query).fetchall()

# Score active and paused subscriptions only.
# This is a heuristic score, not a trained prediction model.
results = []

for customer in customers:
    status = customer["status"]
    score = 0
    reasons = []

    if status not in ("active", "paused"):
        segment = "Not currently active"
        results.append({
            **dict(customer),
            "risk_score": 0,
            "risk_segment": segment,
            "risk_reasons": "Subscription not active",
            "recommended_action": "Exclude from active churn-risk campaign"
        })
        continue

    # Product inactivity
    if customer["last_active_date"] is None:
        score += 30
        reasons.append("No recorded activity")
    else:
        from datetime import date

        last_active = date.fromisoformat(customer["last_active_date"])
        days_inactive = (date.today() - last_active).days

        if days_inactive >= 30:
            score += 30
            reasons.append("Inactive for 30+ days")
        elif days_inactive >= 14:
            score += 20
            reasons.append("Inactive for 14–29 days")
        elif days_inactive >= 7:
            score += 10
            reasons.append("Inactive for 7–13 days")

    # Previous cancellation behavior
    if customer["cancellation_attempts"] >= 2:
        score += 25
        reasons.append("Repeated cancellation attempts")
    elif customer["cancellation_attempts"] == 1:
        score += 15
        reasons.append("Previous cancellation attempt")

    # Payment issues
    if customer["failed_payments"] >= 2:
        score += 25
        reasons.append("Multiple failed payments")
    elif customer["failed_payments"] == 1:
        score += 15
        reasons.append("Failed payment")

    # Keep score between 0 and 100
    score = min(score, 100)

    if score >= 50:
        segment = "High risk"
        action = "Offer relevant pause, plan change, or payment help"
    elif score >= 25:
        segment = "Medium risk"
        action = "Offer usage guidance or investigate friction"
    else:
        segment = "Low risk"
        action = "Continue normal onboarding and engagement"

    results.append({
        **dict(customer),
        "risk_score": score,
        "risk_segment": segment,
        "risk_reasons": "; ".join(reasons) if reasons else "No major risk signals",
        "recommended_action": action
    })

# Export customer-level results for inspection
output_file = "churn_risk_segments.csv"

if results:
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

# Display segment summary
print("\nCHURN RISK SEGMENTATION")
print("-" * 55)

from collections import Counter

segment_counts = Counter(r["risk_segment"] for r in results)

for segment, count in segment_counts.most_common():
    print(f"{segment}: {count:,} customers")

print(f"\nTotal customers scored: {len(results):,}")
print(f"Exported results to: {output_file}")

conn.close()
