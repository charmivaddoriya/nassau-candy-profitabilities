"""Core analytics for the Nassau Candy Product Line Profitability project."""
import numpy as np
import pandas as pd

FACTORY_MAP = {
    "Wonka Bar - Nutty Crunch Surprise": "Lot's O' Nuts",
    "Wonka Bar - Fudge Mallows": "Lot's O' Nuts",
    "Wonka Bar - Scrumdiddlyumptious": "Lot's O' Nuts",
    "Wonka Bar - Milk Chocolate": "Wicked Choccy's",
    "Wonka Bar - Triple Dazzle Caramel": "Wicked Choccy's",
    "Laffy Taffy": "Sugar Shack", "SweeTARTS": "Sugar Shack", "Nerds": "Sugar Shack",
    "Fun Dip": "Sugar Shack", "Fizzy Lifting Drinks": "Sugar Shack",
    "Everlasting Gobstopper": "Secret Factory", "Lickable Wallpaper": "Secret Factory",
    "Wonka Gum": "Secret Factory", "Hair Toffee": "The Other Factory",
    "Kazookles": "The Other Factory",
}


def load_and_clean(path):
    """Load the CSV, validate it and return (clean_df, cleaning_log dict)."""
    raw = pd.read_csv(path)
    log = {"rows_raw": len(raw)}
    df = raw.copy()
    df.columns = [c.strip() for c in df.columns]

    # standardise labels
    for c in ["Division", "Product Name", "Region", "State/Province", "City", "Ship Mode"]:
        df[c] = df[c].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
    df["Division"] = df["Division"].str.title()
    df["Product Name"] = df["Product Name"].str.replace(r"Wonka Bar -(?=\S)", "Wonka Bar - ", regex=True)

    df["Order Date"] = pd.to_datetime(df["Order Date"], format="%d-%m-%Y", errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%d-%m-%Y", errors="coerce")
    log["bad_order_dates"] = int(df["Order Date"].isna().sum())

    # duplicates
    log["duplicate_rows"] = int(df.duplicated(subset=[c for c in df.columns if c != "Row ID"]).sum())
    df = df.drop_duplicates(subset=[c for c in df.columns if c != "Row ID"])

    # missing units -> impute from sales / median unit price of that product
    log["missing_units"] = int(df["Units"].isna().sum() + (df["Units"] <= 0).sum())
    unit_price = (df["Sales"] / df["Units"].where(df["Units"] > 0)).groupby(df["Product Name"]).transform("median")
    miss = df["Units"].isna() | (df["Units"] <= 0)
    df.loc[miss, "Units"] = (df.loc[miss, "Sales"] / unit_price[miss]).round().clip(lower=1)

    # invalid records
    bad = (df["Sales"] <= 0) | df["Cost"].isna() | df["Gross Profit"].isna() | df["Order Date"].isna()
    log["zero_or_invalid_sales_profit"] = int(bad.sum())
    df = df[~bad]

    # validate Gross Profit = Sales - Cost
    gap = (df["Sales"] - df["Cost"] - df["Gross Profit"]).abs()
    log["gp_formula_mismatch"] = int((gap > 0.02).sum())
    log["negative_profit_rows"] = int((df["Gross Profit"] < 0).sum())
    log["cost_gt_sales_rows"] = int((df["Cost"] > df["Sales"]).sum())

    df["Factory"] = df["Product Name"].map(FACTORY_MAP)
    df["Margin %"] = df["Gross Profit"] / df["Sales"] * 100
    df["Month"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()
    log["rows_clean"] = len(df)
    return df.reset_index(drop=True), log


def product_metrics(df, margin_threshold=None):
    g = df.groupby(["Product Name", "Division", "Factory"], dropna=False).agg(
        Sales=("Sales", "sum"), Cost=("Cost", "sum"), Profit=("Gross Profit", "sum"),
        Units=("Units", "sum"), Orders=("Order ID", "nunique")).reset_index()
    g["Margin %"] = g["Profit"] / g["Sales"] * 100
    g["Profit per Unit"] = g["Profit"] / g["Units"]
    g["Cost per Unit"] = g["Cost"] / g["Units"]
    g["Price per Unit"] = g["Sales"] / g["Units"]
    g["Revenue Contribution %"] = g["Sales"] / g["Sales"].sum() * 100
    g["Profit Contribution %"] = g["Profit"] / g["Profit"].sum() * 100
    # margin volatility = std dev of monthly margin (pp)
    m = df.groupby(["Product Name", "Month"]).agg(S=("Sales", "sum"), P=("Gross Profit", "sum"))
    m["mm"] = m["P"] / m["S"] * 100
    vol = m.groupby("Product Name")["mm"].std().rename("Margin Volatility (pp)")
    g = g.merge(vol, on="Product Name", how="left")
    g["Margin Volatility (pp)"] = g["Margin Volatility (pp)"].fillna(0)
    g["Segment"] = classify(g, margin_threshold)
    g["Action Flag"] = flags(g, margin_threshold)
    return g.sort_values("Profit", ascending=False).reset_index(drop=True)


def classify(g, margin_threshold=None):
    sm = g["Sales"].median()
    avg_margin = margin_threshold if margin_threshold is not None else g["Profit"].sum() / g["Sales"].sum() * 100
    out = []
    for _, r in g.iterrows():
        hs, hm = r["Sales"] >= sm, r["Margin %"] >= avg_margin
        if hs and hm: out.append("Star (high sales / high margin)")
        elif hs and not hm: out.append("Volume trap (high sales / low margin)")
        elif (not hs) and hm: out.append("Niche earner (low sales / high margin)")
        else: out.append("Underperformer (low sales / low margin)")
    return out


def flags(g, margin_threshold=None):
    avg_margin = g["Profit"].sum() / g["Sales"].sum() * 100
    thr = margin_threshold if margin_threshold is not None else avg_margin * 0.9
    cost_ratio_q75 = (g["Cost"] / g["Sales"]).quantile(0.75)
    out = []
    for _, r in g.iterrows():
        cr = r["Cost"] / r["Sales"]
        if r["Margin %"] < thr and r["Sales"] < g["Sales"].median():
            out.append("Discontinuation review")
        elif r["Margin %"] < thr and cr >= cost_ratio_q75:
            out.append("Cost renegotiation")
        elif r["Margin %"] < thr:
            out.append("Repricing")
        else:
            out.append("Healthy")
    return out


def division_metrics(df):
    d = df.groupby("Division").agg(Sales=("Sales", "sum"), Cost=("Cost", "sum"),
                                   Profit=("Gross Profit", "sum"), Units=("Units", "sum"),
                                   Products=("Product Name", "nunique")).reset_index()
    d["Margin %"] = d["Profit"] / d["Sales"] * 100
    d["Revenue Share %"] = d["Sales"] / d["Sales"].sum() * 100
    d["Profit Share %"] = d["Profit"] / d["Profit"].sum() * 100
    d["Profit - Revenue Share (pp)"] = d["Profit Share %"] - d["Revenue Share %"]
    d["Profit per Unit"] = d["Profit"] / d["Units"]
    return d.sort_values("Profit", ascending=False)


def pareto(pm, col):
    s = pm.sort_values(col, ascending=False).reset_index(drop=True)
    s["Cum %"] = s[col].cumsum() / s[col].sum() * 100
    s["Rank"] = np.arange(1, len(s) + 1)
    s["Product %"] = s["Rank"] / len(s) * 100
    n80 = int((s["Cum %"] < 80).sum() + 1)
    return s, n80, n80 / len(s) * 100


def hhi(shares_pct):
    return float(((shares_pct / 100) ** 2).sum() * 10000)


def monthly_margin(df):
    m = df.groupby("Month").agg(Sales=("Sales", "sum"), Profit=("Gross Profit", "sum")).reset_index()
    m["Margin %"] = m["Profit"] / m["Sales"] * 100
    return m


def division_volatility(df):
    """Std-dev of monthly margin (pp) per division and for the whole portfolio."""
    out = {d: monthly_margin(x)["Margin %"].std() for d, x in df.groupby("Division")}
    out["Portfolio"] = monthly_margin(df)["Margin %"].std()
    return pd.Series(out, name="Margin Volatility (pp)")
