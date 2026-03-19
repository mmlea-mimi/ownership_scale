import math
import pandas as pd

# --- load data ---
df = pd.read_csv("target_properties_reproduced.csv")

# --- identify & clean owner fields ---
owner_name_col = "owner_name"
owner_address_col = "owner_address"

# Basic normalization: upper-case, strip whitespace, collapse internal whitespace.
def clean_text(series: pd.Series) -> pd.Series:
    return (
        series.fillna("")
        .astype(str)
        .str.upper()
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

# Create clean versions of owner fields.
df["owner_name_clean"] = clean_text(df[owner_name_col])
df["owner_address_clean"] = clean_text(df[owner_address_col])

# Build a combined entity key for grouping/clustering later.
df["owner_entity"] = (
    df["owner_name_clean"]
    + " | "
    + df["owner_address_clean"]
).str.strip(" |")

# --- inspect ---
print("\nColumns:")
print(df.columns.tolist())

print("\nShape:")
print(df.shape)

print("\nFirst 5 rows:")
print(df.head())

print("\nMissing values:")
print(df.isna().sum().sort_values(ascending=False).head(20))

# --- ownership scale summary ---
owner_scale = (
    df.groupby("owner_entity", dropna=False)
    .agg(
        owner_name=("owner_name_clean", "first"),
        owner_address=("owner_address_clean", "first"),
        num_properties=("owner_entity", "size"),
    )
    .reset_index()
    .sort_values("num_properties", ascending=False)
)

print("\nTop 10 owners by property count:")
print(owner_scale.head(10))

# --- ownership scale scoring ---
# Category thresholds are adjustable based on your definition of small/medium/large.
def ownership_scale_category(num_properties: int) -> str:
    if num_properties <= 1:
        return "single-property"
    if num_properties <= 10:
        return "small-scale"
    if num_properties <= 50:
        return "mid-scale"
    if num_properties <= 200:
        return "large-scale"
    return "very-large-scale"

owner_scale["ownership_scale_category"] = owner_scale["num_properties"].apply(ownership_scale_category)
owner_scale["ownership_scale_score"] = owner_scale["num_properties"].apply(lambda n: math.log10(n + 1))

# Merge the scale info back to each parcel and output a new CSV (without modifying the original source).
df_out = df.merge(
    owner_scale[
        [
            "owner_entity",
            "num_properties",
            "ownership_scale_category",
            "ownership_scale_score",
        ]
    ],
    on="owner_entity",
    how="left",
)

# The user wants a minimal output with just the essentials.
# Include coordinates if present, plus a count of *other* properties for that owner.
df_out["num_other_properties"] = df_out["num_properties"].fillna(0).astype(int) - 1

# Drop the original raw columns so we don’t get duplicates like owner_name.1/owner_address.1
# (we keep the cleaned versions for output)
df_out = df_out.drop(columns=[owner_name_col, owner_address_col], errors="ignore")

df_out = df_out.rename(
    columns={
        "owner_name_clean": "owner_name",
        "owner_address_clean": "owner_address",
    }
)

output_cols = [
    "owner_name",
    "owner_address",
    "situs_lat",
    "situs_long",
    "num_other_properties",
    "ownership_scale_score",
]

# Keep only columns that exist in the dataframe (in case coordinates are missing).
output_cols = [c for c in output_cols if c in df_out.columns]
df_out = df_out[output_cols]

df_out.to_csv("target_properties_with_owner_scale.csv", index=False)
print("\nWrote target_properties_with_owner_scale.csv")

owner_scale.to_excel("ownership_scale_per_owner.xlsx", index=False)
print("\nWrote ownership_scale_per_owner.xlsx")
