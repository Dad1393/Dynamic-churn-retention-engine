
import sqlite3
import csv
from collections import defaultdict

DB_FILE = "churn_project.sqlite"
OUTPUT_FILE = "retention_impact_by_offer.csv"

conn = sqlite3.connect(DB_FILE)

# 1. Offer performance
offer_query = """
SELECT
    selected_offer,
    COUNT(*) AS attempts,
    SUM(CASE WHEN outcome = 'retained' THEN 1 ELSE 0 END) AS saved,
    SUM(CASE WHEN outcome = 'canceled' THEN 1 ELSE 0 END) AS canceled,
    SUM(CASE WHEN outcome = 'paused' THEN 1 ELSE 0 END) AS paused
FROM cancellation_events
GROUP BY selected_offer
ORDER BY attempts DESC
"""

offer_rows = conn.execute(offer_query).fetchall()

print("\n1. RETENTION OFFER PERFORMANCE")
print("-" * 65)

for offer, attempts, saved, canceled, paused in offer_rows:
    save_rate = saved / attempts * 100 if attempts else 0
    print(
        f"{offer:24} | Attempts: {attempts:4} | "
        f"Saved: {saved:4} | Save rate: {save_rate:6.2f}%"
    )

# 2. Control vs treatment
experiment_query = """
SELECT
    experiment_group,
    COUNT(*) AS attempts,
    SUM(CASE WHEN outcome = 'retained' THEN 1 ELSE 0 END) AS saved
FROM cancellation_events
WHERE experiment_group IN ('control', 'treatment')
GROUP BY experiment_group
"""

experiment_rows = {
    row[0]: {"attempts": row[1], "saved": row[2]}
    for row in conn.execute(experiment_query).fetchall()
}

print("\n2. CONTROL VS TREATMENT")
print("-" * 65)

for group in ("control", "treatment"):
    data = experiment_rows.get(group, {"attempts": 0, "saved": 0})
    rate = data["saved"] / data["attempts"] * 100 if data["attempts"] else 0
    print(
        f"{group:12} | Attempts: {data['attempts']:4} | "
        f"Saved: {data['saved']:4} | Save rate: {rate:.2f}%"
    )

if all(experiment_rows.get(g, {}).get("attempts", 0) for g in ("control", "treatment")):
    control = experiment_rows["control"]
    treatment = experiment_rows["treatment"]

    control_rate = control["saved"] / control["attempts"]
    treatment_rate = treatment["saved"] / treatment["attempts"]

    difference_pp = (treatment_rate - control_rate) * 100
    relative_lift = (
        (treatment_rate / control_rate - 1) * 100
        if control_rate else 0
    )

    print(f"Absolute lift: {difference_pp:+.2f} percentage points")
    print(f"Relative lift: {relative_lift:+.2f}%")

# 3. Estimate monthly recurring revenue associated with retained customers
# This is an estimate, not causal or realized revenue.
revenue_query = """
SELECT
    ce.selected_offer,
    COUNT(*) AS retained_events,
    SUM(COALESCE(s.monthly_price, 0)) AS estimated_monthly_revenue
FROM cancellation_events ce
JOIN subscriptions s
    ON ce.customer_id = s.customer_id
WHERE ce.outcome = 'retained'
GROUP BY ce.selected_offer
ORDER BY estimated_monthly_revenue DESC
"""

revenue_rows = conn.execute(revenue_query).fetchall()

print("\n3. ESTIMATED MONTHLY REVENUE ASSOCIATED WITH RETAINED EVENTS")
print("-" * 75)

for offer, retained_events, revenue in revenue_rows:
    print(
        f"{offer:24} | Events: {retained_events:4} | "
        f"Monthly revenue: {revenue:,.2f}"
    )

# 4. Export offer-level results
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "selected_offer",
        "attempts",
        "retained_events",
        "canceled_events",
        "paused_events",
        "save_rate_pct",
        "estimated_monthly_revenue_associated"
    ])

    revenue_by_offer = {
        row[0]: row[2] for row in revenue_rows
    }

    for offer, attempts, saved, canceled, paused in offer_rows:
        rate = saved / attempts * 100 if attempts else 0
        writer.writerow([
            offer,
            attempts,
            saved,
            canceled,
            paused,
            round(rate, 2),
            round(revenue_by_offer.get(offer, 0), 2)
        ])

conn.close()

print(f"\nExported report: {OUTPUT_FILE}")
