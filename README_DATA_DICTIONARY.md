# Dynamic Churn Prevention & Retention Growth Engine — Synthetic Dataset

## Snapshot
- Generated deterministically with seed 20261014.
- 8,000 customer records.
- Snapshot date: 2026-10-01.
- Currency: illustrative INR.
- All records are synthetic and must not be presented as real company data.

## Files
- `customers.csv`: one row per customer.
- `subscriptions.csv`: one row per customer; current/latest subscription state.
- `product_events.csv`: one summary row per customer, not raw clickstream events.
- `cancellation_events.csv`: cancellation attempts, reasons, offers, outcomes, and experiment groups.
- `payments.csv`: monthly payment records up to 18 months per customer.
- `churn_project.sqlite`: all tables loaded into a SQLite database.

## Join keys
- `customer_id` links all five tables.
- `customers` and `subscriptions` are one-to-one in this dataset.
- `product_events` is one summary row per customer.
- `cancellation_events` and `payments` are one-to-many.

## Important caveats
- This is simulated data for practice, not evidence of actual product performance.
- The cancellation experiment groups and outcomes are synthetic and are not a valid randomized real-world experiment.
- Subscription status is a current snapshot; historical churn analyses should use the relevant dates and an explicitly defined cohort.
- `monthly_price` is a monthly list price in illustrative INR; payment rows can include discounts and failed payments.
- The product activity table is a summary table, not raw events.
- A `cancellation_events.outcome` of `retained` is a simulated outcome and should not automatically be interpreted as proven 30-day retention.
- Some date and status relationships are intentionally simplified for a beginner-friendly dataset.
