"""
Phase 8 - Statistical Analysis
Retail Sales Analytics Project

Tests whether patterns observed in Phase 5 (EDA) are statistically
significant, or could plausibly be due to random variation. Uses
line-item level sales_amount as the unit of observation throughout.
"""
import pandas as pd
import numpy as np
from scipy import stats

df = pd.read_csv("data/cleaned/merged_flat_table.csv", parse_dates=['order_date'])

print("="*70)
print("1. CONFIDENCE INTERVAL: Average Order Value (95% CI)")
print("="*70)
order_totals = df.groupby('order_number')['sales_amount'].sum()
mean_aov = order_totals.mean()
sem = stats.sem(order_totals)
ci = stats.t.interval(0.95, len(order_totals) - 1, loc=mean_aov, scale=sem)
print(f"Mean AOV: ${mean_aov:,.2f}")
print(f"95% Confidence Interval: (${ci[0]:,.2f}, ${ci[1]:,.2f})")
print("Interpretation: we are 95% confident the TRUE average order value for")
print("the full customer population falls within this range.")

print("\n" + "="*70)
print("2. HYPOTHESIS TEST: Is US revenue per order significantly different")
print("   from Australia's? (Independent samples t-test)")
print("="*70)
us_orders = df[df['country'] == 'United States'].groupby('order_number')['sales_amount'].sum()
au_orders = df[df['country'] == 'Australia'].groupby('order_number')['sales_amount'].sum()
t_stat, p_val = stats.ttest_ind(us_orders, au_orders, equal_var=False)
print(f"US mean order value: ${us_orders.mean():,.2f} (n={len(us_orders)})")
print(f"Australia mean order value: ${au_orders.mean():,.2f} (n={len(au_orders)})")
print(f"t-statistic: {t_stat:.3f}, p-value: {p_val:.4f}")
if p_val < 0.05:
    print("Result: STATISTICALLY SIGNIFICANT (p < 0.05) - the difference in")
    print("per-order value between US and Australia is unlikely to be random chance.")
else:
    print("Result: NOT statistically significant (p >= 0.05) - despite similar")
    print("total revenue, we cannot rule out that any per-order difference is random.")

print("\n" + "="*70)
print("3. ANOVA: Does average order value differ significantly across")
print("   ALL countries at once?")
print("="*70)
country_groups = [g['sales_amount'].values for _, g in df.groupby(['country', 'order_number'])['sales_amount'].sum().reset_index().groupby('country')]
f_stat, p_val_anova = stats.f_oneway(*country_groups)
print(f"F-statistic: {f_stat:.3f}, p-value: {p_val_anova:.6f}")
if p_val_anova < 0.05:
    print("Result: SIGNIFICANT - at least one country's average order value")
    print("differs meaningfully from the others (doesn't tell us WHICH one -")
    print("that needs a post-hoc test like Tukey HSD).")

print("\n" + "="*70)
print("4. CORRELATION SIGNIFICANCE: cost vs sales_amount")
print("="*70)
r, p_val_corr = stats.pearsonr(df['cost'], df['sales_amount'])
print(f"Pearson r: {r:.3f}, p-value: {p_val_corr:.6f}")
print("Reminder from Phase 5: this correlation is structural (price is derived")
print("from cost), not a novel business driver - flagging p-value for completeness,")
print("but this is a textbook correlation-vs-causation trap, not an insight.")

print("\n" + "="*70)
print("5. CHI-SQUARE TEST: Is Category independent of Country?")
print("   (tests whether the Country x Category pattern from Phase 5 is real)")
print("="*70)
contingency = pd.crosstab(df['country'], df['category'])
chi2, p_val_chi, dof, expected = stats.chi2_contingency(contingency)
print(f"Chi-square statistic: {chi2:.2f}, p-value: {p_val_chi:.6f}, dof: {dof}")
if p_val_chi < 0.05:
    print("Result: SIGNIFICANT association between country and category mix.")
    print("Caveat: with 60,398 rows, even a tiny, practically meaningless")
    print("association can produce a significant p-value - always check the")
    print("heatmap magnitudes (Phase 5) alongside this, not the p-value alone.")

print("\n" + "="*70)
print("6. AGE vs SPEND: Is there a real correlation, or does it just look")
print("   that way from the bar chart?")
print("="*70)
age_df = df.dropna(subset=['birthdate']).copy()
age_df['age'] = (pd.Timestamp.today() - pd.to_datetime(age_df['birthdate'])).dt.days / 365.25
r_age, p_age = stats.pearsonr(age_df['age'], age_df['sales_amount'])
print(f"Pearson r (age vs line-item sales_amount): {r_age:.3f}, p-value: {p_age:.4f}")
print("Interpretation: a weak/near-zero r here would mean the Phase 5 age-group")
print("bar chart differences are more about AGGREGATE population size per group")
print("than individual purchase behavior scaling with age - important nuance")
print("before recommending marketing budget shifts.")
