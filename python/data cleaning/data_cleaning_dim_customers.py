import pandas as pd
import numpy as np

# ------------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------------
input_path = 'data/raw/dim_customers.csv'
df = pd.read_csv(input_path)

# ------------------------------------------------------------------
# 2. CLEANING RULES (as specified by user)
# ------------------------------------------------------------------

# Rule 1: Country — 337 missing values
# Label as "Unknown" (don't drop — these customers still have valid
# purchase history in fact_sales; dropping them would silently delete
# real revenue from country-level rollups)
df['country'] = df['country'].fillna('Unknown')

# Rule 2: Gender — 15 missing values
# Label as "Unknown"
df['gender'] = df['gender'].fillna('Unknown')

# Rule 3: Birthdate — 17 missing values
# Leave as null, do NOT impute. Age/generation analysis will simply
# exclude these 17 customers. Faking a birthdate would corrupt any
# age-based segmentation — a common and serious mistake in real analytics.
# (No code needed — already null, we intentionally do nothing)

# ------------------------------------------------------------------
# 3. SAVE CLEANED DATA
# ------------------------------------------------------------------
output_path = 'data/cleaned/dim_customers_cleaned.csv'
df.to_csv(output_path, index=False)

# ------------------------------------------------------------------
# 4. VERIFICATION (optional, for logging/auditing)
# ------------------------------------------------------------------
print("=== CLEANING VERIFICATION ===")
print(f"Total rows: {len(df):,}")
print(f"\nMissing values by column:")
print(df.isnull().sum())
print(f"\nCountry value counts:")
print(df['country'].value_counts())
print(f"\nGender value counts:")
print(df['gender'].value_counts())
print(f"\nBirthdate null count: {df['birthdate'].isnull().sum()}")
