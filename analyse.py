import sqlite3

# Connect to the project database
conn = sqlite3.connect("churn_project.sqlite")

# ==========================================
# ANALYSIS 1: SUBSCRIPTION STATUS
# ==========================================

print("\n1. CUSTOMER STATUS ANALYSIS")
print("-" * 60)

query1 = """
SELECT
    status,
    COUNT(*) AS total_customers
FROM subscriptions
GROUP BY status
ORDER BY total_customers DESC;
"""

for status, count in conn.execute(query1):
    print(f"{status}: {count} customers")


# ==========================================
# ANALYSIS 2: CANCELLATION REASONS
# ==========================================

print("\n2. CANCELLATION REASON ANALYSIS")
print("-" * 60)

query2 = """
SELECT
    cancellation_reason,
    COUNT(*) AS total_attempts,
    ROUND(
        100.0 * COUNT(*) /
        (SELECT COUNT(*) FROM cancellation_events),
        2
    ) AS percentage
FROM cancellation_events
GROUP BY cancellation_reason
ORDER BY total_attempts DESC;
"""

for reason, count, percentage in conn.execute(query2):
    print(f"{reason}: {count} attempts ({percentage}%)")


# ==========================================
# ANALYSIS 3: RETENTION OFFER PERFORMANCE
# ==========================================

print("\n3. RETENTION OFFER PERFORMANCE")
print("-" * 75)

query3 = """
SELECT
    selected_offer,
    COUNT(*) AS total_attempts,
    SUM(
        CASE
            WHEN outcome IN ('retained', 'paused')
            THEN 1
            ELSE 0
        END
    ) AS saved_customers,
    ROUND(
        100.0 * SUM(
            CASE
                WHEN outcome IN ('retained', 'paused')
                THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS save_rate_pct
FROM cancellation_events
GROUP BY selected_offer
ORDER BY save_rate_pct DESC;
"""

for offer, attempts, saved, rate in conn.execute(query3):
    print(
        f"{offer:25} | Attempts: {attempts:4} "
        f"| Saved: {saved:4} | Save rate: {rate:.2f}%"
    )


# ==========================================
# ANALYSIS 4: CONTROL VS TREATMENT
# ==========================================

print("\n4. CONTROL VS TREATMENT ANALYSIS")
print("-" * 75)

query4 = """
SELECT
    experiment_group,
    COUNT(*) AS total_attempts,
    SUM(
        CASE
            WHEN outcome IN ('retained', 'paused')
            THEN 1
            ELSE 0
        END
    ) AS saved_customers,
    ROUND(
        100.0 * SUM(
            CASE
                WHEN outcome IN ('retained', 'paused')
                THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS save_rate_pct
FROM cancellation_events
GROUP BY experiment_group
ORDER BY experiment_group;
"""

results = list(conn.execute(query4))

for group, attempts, saved, rate in results:
    print(
        f"{group:12} | Attempts: {attempts:4} "
        f"| Saved: {saved:4} | Save rate: {rate:.2f}%"
    )

# Calculate the treatment-control difference
rates = {row[0]: row[3] for row in results}

if "control" in rates and "treatment" in rates:
    difference = rates["treatment"] - rates["control"]

    print("\nEXPERIMENT SUMMARY")
    print("-" * 40)
    print(f"Control save rate:   {rates['control']:.2f}%")
    print(f"Treatment save rate: {rates['treatment']:.2f}%")
    print(f"Difference:          {difference:+.2f} percentage points")
else:
    print("\nCould not compare groups. Check experiment_group values.")


# ==========================================
# CLOSE DATABASE (ONLY ONCE)
# ==========================================

conn.close()

print("\nAll four analyses completed successfully.")

