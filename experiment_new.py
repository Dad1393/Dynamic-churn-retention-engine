import math

# Results from your synthetic experiment
control_saved = 359
control_total = 1438

treatment_saved = 442
treatment_total = 1358

# Calculate conversion rates
p_control = control_saved / control_total
p_treatment = treatment_saved / treatment_total

# Difference in percentage points
difference = (p_treatment - p_control) * 100

# Pooled proportion for the two-proportion z-test
pooled = (
    (control_saved + treatment_saved)
    / (control_total + treatment_total)
)

standard_error = math.sqrt(
    pooled * (1 - pooled)
    * (1 / control_total + 1 / treatment_total)
)

z_score = (p_treatment - p_control) / standard_error

# Two-sided p-value using the normal distribution
p_value = math.erfc(abs(z_score) / math.sqrt(2))

print("\nEXPERIMENT SIGNIFICANCE TEST")
print("-" * 40)
print(f"Control rate:      {p_control:.2%}")
print(f"Treatment rate:    {p_treatment:.2%}")
print(f"Improvement:       {difference:+.2f} percentage points")
print(f"Z-score:           {z_score:.3f}")
print(f"P-value:           {p_value:.6f}")

if p_value < 0.05:
    print("Result: Statistically significant at the 5% level.")
else:
    print("Result: Not statistically significant at the 5% level.")