
# Dynamic Churn Prevention & Retention Growth Engine

## 1. Project Overview

**Role:** Growth Product Management  
**Project type:** Synthetic-data product analytics project  
**Tools:** Python, SQL/SQLite, Pandas, Streamlit, Plotly

I built a prototype retention engine to analyse subscription cancellation patterns, segment customers by churn risk, and recommend targeted retention interventions.

## 2. Business Problem

Subscription businesses can lose customers when users do not engage with the product, perceive the price as too high, encounter missing features, or experience payment issues.

The goal was to explore how customer data could help a product team identify retention opportunities and design more relevant interventions.

## 3. Data Analysis

The synthetic dataset contained 8,000 customer records.

Key cancellation-attempt findings:
- Low usage: 773 attempts (27.65%)
- Too expensive: 738 attempts (26.39%)

These findings suggest that product engagement and perceived value are useful areas to investigate.

## 4. Product Solution

I developed a prototype that:
- Calculates rule-based customer churn-risk scores.
- Segments customers by risk.
- Maps recorded cancellation reasons to suggested retention offers.
- Separates canceled customers from active retention campaigns.
- Displays analysis through an interactive dashboard.

Example interventions:
- Low usage → personalized usage guidance.
- Price concern → lower-cost plan.
- Temporary break → account-pause option.
- Payment issue → payment recovery support.

## 5. Experiment Analysis

In the synthetic experiment:
- Control save rate: 24.97% (359/1,438)
- Treatment save rate: 32.55% (442/1,358)
- Observed difference: +7.58 percentage points
- Z-score: 4.432
- P-value: 0.000009

The difference was statistically significant under the two-proportion test assumptions. The synthetic data does not establish real-world or causal impact without validation of group assignment and experiment design.

## 6. Measurement Plan

If piloted with real customers, I would measure:
- Primary metric: retained customers after a defined follow-up period.
- Secondary metrics: save rate by intervention and customer segment.
- Guardrails: refunds, discount costs, complaints, and subsequent cancellations.
- Business outcome: incremental retained revenue compared with a valid control group.

## 7. Limitations

- The dataset is synthetic, not real customer evidence.
- Churn-risk scores are rule-based, not a validated predictive model.
- Historical cancellation reasons may not reflect current customer intent.
- Recommended offers have not been proven effective for each segment.
- Observed retained revenue is not necessarily incremental revenue caused by an intervention.

## 8. Next Steps

1. Validate risk scores against future cancellation outcomes.
2. Test intervention-specific hypotheses using randomized experiments.
3. Evaluate longer-term retention and offer costs.
4. Improve the dashboard to track outcomes over time.
