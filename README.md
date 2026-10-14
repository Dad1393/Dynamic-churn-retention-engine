
# Dynamic Churn Prevention & Retention Growth Engine

A Growth Product Management portfolio project exploring subscription churn, customer risk segmentation, and targeted retention strategies using synthetic data.

## Problem
Subscription businesses need to understand why customers cancel and identify appropriate opportunities to improve retention.

## Solution
This prototype includes:
- Churn and cancellation analysis
- Rule-based customer risk segmentation
- Customer-level retention recommendations
- Control-versus-treatment experiment analysis
- Interactive Streamlit dashboard

## Tools
Python, Pandas, SQLite, Streamlit, Plotly

## Key Findings
- Low usage represented 27.65% of recorded cancellation attempts.
- Price concerns represented 26.39% of recorded cancellation attempts.
- The synthetic experiment showed a 7.58-percentage-point difference in save rates between treatment and control.

## Run the Dashboard
Install dependencies:

```bash
python -m pip install pandas plotly streamlit
```

Launch the dashboard:

```bash
python -m streamlit run dashboard.py
```

## Limitations
This project uses synthetic data and rule-based risk scoring. The experiment results are illustrative and do not establish real-world causal impact. Historical cancellation reasons may not reflect current customer intent.

## Author
Growth Product Management Portfolio Project
