-- 1) Subscribers by current status
SELECT status, COUNT(*) AS customers
FROM subscriptions
GROUP BY status
ORDER BY customers DESC;

-- 2) Canceled share by plan (snapshot-level descriptive metric, not monthly churn)
SELECT
  plan,
  COUNT(*) AS subscribers,
  SUM(CASE WHEN status = 'canceled' THEN 1 ELSE 0 END) AS canceled,
  ROUND(100.0 * SUM(CASE WHEN status = 'canceled' THEN 1 ELSE 0 END) / COUNT(*), 2) AS canceled_share_pct
FROM subscriptions
GROUP BY plan
ORDER BY canceled_share_pct DESC;

-- 3) Cancellation reasons
SELECT cancellation_reason, COUNT(*) AS attempts
FROM cancellation_events
GROUP BY cancellation_reason
ORDER BY attempts DESC;

-- 4) Offer acceptance by offer type
SELECT
  selected_offer,
  COUNT(*) AS attempts,
  SUM(CASE WHEN outcome IN ('retained', 'paused') THEN 1 ELSE 0 END) AS non_cancel_outcomes
FROM cancellation_events
GROUP BY selected_offer
ORDER BY attempts DESC;

-- 5) Payment success rate by plan
SELECT
  s.plan,
  COUNT(*) AS payment_attempts,
  SUM(CASE WHEN p.payment_status IN ('paid', 'refunded') THEN 1 ELSE 0 END) AS paid_or_refunded,
  ROUND(100.0 * SUM(CASE WHEN p.payment_status IN ('paid', 'refunded') THEN 1 ELSE 0 END) / COUNT(*), 2) AS paid_or_refunded_pct
FROM payments p
JOIN subscriptions s USING (customer_id)
GROUP BY s.plan
ORDER BY paid_or_refunded_pct DESC;
