"""
setup_databases.py
==================
Downloads the three HuggingFace datasets and converts them to SQLite databases.

Run ONCE before starting the agent:
    python setup_databases.py
"""

import sqlite3
import os
from datasets import load_dataset
import pandas as pd

# ── Column rename maps ─────────────────────────────────────────────────────
# We normalise messy HuggingFace column names into clean snake_case names.

INSTITUTIONS_RENAME = {
    # add/edit mappings after inspecting actual columns
    "Name":           "name",
    "Type":           "type",
    "District":       "district",
    "Division":       "division",
    "Address":        "address",
    "Founded Year":   "founded_year",
    "Contact":        "contact",
    "Website":        "website",
}

HOSPITALS_RENAME = {
    "Name":              "name",
    "Type":              "type",
    "District":          "district",
    "Division":          "division",
    "Address":           "address",
    "Beds":              "beds",
    "Doctors":           "doctors",
    "Contact":           "contact",
    "Established Year":  "established_year",
}

RESTAURANTS_RENAME = {
    "Name":         "name",
    "Cuisine":      "cuisine",
    "District":     "district",
    "Division":     "division",
    "Address":      "address",
    "Rating":       "rating",
    "Price Range":  "price_range",
    "Contact":      "contact",
}


# ── Column dtype maps (SQLite types) ───────────────────────────────────────

INSTITUTIONS_TYPES = {
    "founded_year": "INTEGER",
}

HOSPITALS_TYPES = {
    "beds":              "INTEGER",
    "doctors":           "INTEGER",
    "established_year":  "INTEGER",
}

RESTAURANTS_TYPES = {
    "rating": "REAL",
}


def load_and_clean(hf_dataset_id: str, rename_map: dict) -> pd.DataFrame:
    """Load a HuggingFace dataset and return a cleaned DataFrame."""
    print(f"  Downloading '{hf_dataset_id}' …")
    ds = load_dataset(hf_dataset_id, split="train")
    df = ds.to_pandas()

    print(f"  Raw columns: {list(df.columns)}")

    # Rename only the columns that exist
    actual_rename = {k: v for k, v in rename_map.items() if k in df.columns}
    df = df.rename(columns=actual_rename)

    # Lowercase any remaining columns
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]

    # Drop fully-empty rows
    df = df.dropna(how="all")

    print(f"  Cleaned columns: {list(df.columns)}  |  rows: {len(df)}")
    return df


def save_to_sqlite(df: pd.DataFrame, db_path: str, table: str, type_map: dict):
    """Save a DataFrame to a SQLite database with typed columns."""
    con = sqlite3.connect(db_path)

    # Build CREATE TABLE with explicit types
    col_defs = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
    for col in df.columns:
        sql_type = type_map.get(col, "TEXT")
        col_defs.append(f'"{col}" {sql_type}')

    create_sql = f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(col_defs)});"
    con.execute(f"DROP TABLE IF EXISTS {table};")
    con.execute(create_sql)

    # Insert rows
    placeholders = ", ".join(["?"] * len(df.columns))
    cols_str = ", ".join(f'"{c}"' for c in df.columns)
    insert_sql = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders})"

    for _, row in df.iterrows():
        con.execute(insert_sql, tuple(row))

    con.commit()
    con.close()
    print(f"  ✅  Saved {len(df)} rows → {db_path}  (table: {table})")


def main():
    datasets = [
        {
            "id":     "Mahadih534/Institutional-Information-of-Bangladesh",
            "db":     "institutions.db",
            "table":  "institutions",
            "rename": INSTITUTIONS_RENAME,
            "types":  INSTITUTIONS_TYPES,
        },
        {
            "id":     "Mahadih534/all-bangladeshi-hospitals",
            "db":     "hospitals.db",
            "table":  "hospitals",
            "rename": HOSPITALS_RENAME,
            "types":  HOSPITALS_TYPES,
        },
        {
            "id":     "Mahadih534/Bangladeshi-Restaurant-Data",
            "db":     "restaurants.db",
            "table":  "restaurants",
            "rename": RESTAURANTS_RENAME,
            "types":  RESTAURANTS_TYPES,
        },
    ]

    for cfg in datasets:
        print(f"\n{'─'*55}")
        print(f"Processing: {cfg['id']}")
        df = load_and_clean(cfg["id"], cfg["rename"])
        save_to_sqlite(df, cfg["db"], cfg["table"], cfg["types"])

    print("\n✅  All databases created successfully!\n")
    print("Files created:")
    for cfg in datasets:
        size = os.path.getsize(cfg["db"]) if os.path.exists(cfg["db"]) else 0
        print(f"  {cfg['db']}  ({size // 1024} KB)")


if __name__ == "__main__":
    main()
