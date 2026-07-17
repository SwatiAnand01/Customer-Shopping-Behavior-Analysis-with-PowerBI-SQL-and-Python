import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# Load Dataset
df = pd.read_csv("customer_shopping_behavior.csv")

# Preview Data
print(df.head())
print(df.info())
print(df.describe())
print(df.isnull().sum())


# Clean Column Names
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("(", "", regex=False)
    .str.replace(")", "", regex=False)
)

# Rename purchase amount column
if "purchase_amount_usd" in df.columns:
    df.rename(columns={"purchase_amount_usd": "purchase_amount"}, inplace=True)

print("\nColumns after cleaning:")
print(df.columns.tolist())


# Handle Missing Values
if "review_rating" in df.columns:
    df["review_rating"] = (
        df.groupby("category")["review_rating"]
        .transform(lambda x: x.fillna(x.median()))
    )

print("\nMissing Values:")
print(df.isnull().sum())

# Create Age Group
labels = ["Young Adult", "Adult", "Middle Age", "Senior"]

df["age_group"] = pd.qcut(
    df["age"],
    q=4,
    labels=labels
)

print(df[["age", "age_group"]].head(10))

# Convert Purchase Frequency to Days
print("\nUnique Purchase Frequencies:")
print(df["frequency_of_purchases"].unique())

frequency_mapping = {
    "Weekly": 7,
    "Bi-Weekly": 14,
    "Fortnightly": 14,
    "Monthly": 30,
    "Quarterly": 90,
    "Every 3 Months": 90,
    "Annually": 365
}

df["purchase_frequency_days"] = (
    df["frequency_of_purchases"]
    .map(frequency_mapping)
)

print(df[["frequency_of_purchases", "purchase_frequency_days"]].head(10))

# Check Discount & Promo Code
if "promo_code_used" in df.columns:

    print("\nDiscount vs Promo Code:")
    print(df[["discount_applied", "promo_code_used"]].head())

    print(
        "\nAre Discount Applied and Promo Code Used identical?",
        (df["discount_applied"] == df["promo_code_used"]).all()
    )

    # Drop Promo Code Column
    df.drop(columns=["promo_code_used"], inplace=True)

print("\nFinal Columns:")
print(df.columns.tolist())

# Load Data into MySQL
username = "root"
password = quote_plus("swati#13")     # Encodes special characters like '#'
host = "localhost"
port = "3306"
database = "company_db"

engine = create_engine(
    f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
)

table_name = "customer"

df.to_sql(
    table_name,
    con=engine,
    if_exists="replace",
    index=False
)

print(f"\nData successfully loaded into '{table_name}' table in '{database}' database.")

# Final Dataset Preview
print("\nFinal Dataset Shape:")
print(df.shape)

print("\nFirst Five Rows:")
print(df.head())