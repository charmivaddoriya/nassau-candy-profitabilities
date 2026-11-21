import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analysis import (division_metrics, division_volatility, hhi, load_and_clean,
                      monthly_margin, pareto, product_metrics)

st.set_page_config(page_title="Nassau Candy | Profitability", page_icon="🍬", layout="wide")

@st.cache_data
def get_data():
    return load_and_clean("data/Nassau_Candy_Distributor.csv")

df_all, log = get_data()

# ---------------- Sidebar filters ----------------
st.sidebar.title("🍬 Filters")
dmin, dmax = df_all["Order Date"].min().date(), df_all["Order Date"].max().date()
date_range = st.sidebar.date_input("Date range", (dmin, dmax), min_value=dmin, max_value=dmax)
divisions = st.sidebar.multiselect("Division", sorted(df_all["Division"].unique()),
                                   default=sorted(df_all["Division"].unique()))
overall_margin = df_all["Gross Profit"].sum() / df_all["Sales"].sum() * 100
threshold = st.sidebar.slider("Margin threshold (%)", 0.0, 90.0, float(round(overall_margin * 0.9, 1)), 0.5,
                              help="Products below this margin are flagged as margin risks.")
search = st.sidebar.text_input("Product search")

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
else:
    start, end = dmin, dmax
df = df_all[(df_all["Order Date"].dt.date >= start) & (df_all["Order Date"].dt.date <= end)
            & (df_all["Division"].isin(divisions))]
if df.empty:
    st.warning("No data for the selected filters.")
    st.stop()

pm = product_metrics(df, threshold)
if search:
    pm_view = pm[pm["Product Name"].str.contains(search, case=False, na=False)]
else:
    pm_view = pm
dm = division_metrics(df)

# ---------------- Header & KPIs ----------------
st.title("Product Line Profitability & Margin Performance")
st.caption("Nassau Candy Distributor · Unified Mentor project")
k = st.columns(5)
k[0].metric("Sales", f"${df['Sales'].sum():,.0f}")
k[1].metric("Gross Profit", f"${df['Gross Profit'].sum():,.0f}")
k[2].metric("Gross Margin", f"{df['Gross Profit'].sum() / df['Sales'].sum() * 100:.1f}%")
k[3].metric("Profit / Unit", f"${df['Gross Profit'].sum() / df['Units'].sum():.2f}")
k[4].metric("Margin Volatility", f"{monthly_margin(df)['Margin %'].std():.2f} pp",
            help="Std. deviation of monthly portfolio margin")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Product Overview", "Division Performance",
                                        "Cost vs Margin", "Profit Concentration", "Data & Method"])

# ---------------- Tab 1 ----------------
with tab1:
    c1, c2 = st.columns([3, 2])
    with c1:
        st.subheader("Margin leaderboard")
        lb = pm_view.sort_values("Margin %")
        fig = px.bar(lb, x="Margin %", y="Product Name", color="Division", orientation="h",
                     text=lb["Margin %"].round(1))
        fig.add_vline(x=threshold, line_dash="dash", line_color="red", annotation_text="threshold")
        fig.update_layout(height=520, yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Profit contribution")
        fig = px.pie(pm_view, names="Product Name", values="Profit", hole=0.45)
        fig.update_layout(height=520, legend=dict(font=dict(size=9)))
        st.plotly_chart(fig, use_container_width=True)
    st.subheader("Product table")
    cols = ["Product Name", "Division", "Factory", "Sales", "Profit", "Units", "Margin %", "Profit per Unit",
            "Revenue Contribution %", "Profit Contribution %", "Segment", "Action Flag"]
    st.dataframe(pm_view[cols].round(2), use_container_width=True, hide_index=True)
    st.download_button("Download product metrics (CSV)", pm[cols].round(3).to_csv(index=False),
                       "product_metrics.csv", "text/csv")
    c3, c4 = st.columns(2)
    c3.subheader("Rank by gross profit")
    c3.dataframe(pm_view[["Product Name", "Profit"]].round(0).reset_index(drop=True), hide_index=True)
    c4.subheader("Rank by gross margin")
    c4.dataframe(pm_view.sort_values("Margin %", ascending=False)[["Product Name", "Margin %"]]
                 .round(1).reset_index(drop=True), hide_index=True)

# ---------------- Tab 2 ----------------
with tab2:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Revenue vs profit by division")
        long = dm.melt(id_vars="Division", value_vars=["Sales", "Profit"], var_name="Metric")
        fig = px.bar(long, x="Division", y="value", color="Metric", barmode="group", log_y=True)
        fig.update_layout(yaxis_title="USD (log scale)")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Revenue share vs profit share (%)")
        long = dm.melt(id_vars="Division", value_vars=["Revenue Share %", "Profit Share %"], var_name="Share")
        st.plotly_chart(px.bar(long, x="Division", y="value", color="Share", barmode="group"),
                        use_container_width=True)
    st.subheader("Margin distribution by division (order level)")
    st.plotly_chart(px.box(df, x="Division", y="Margin %", color="Division", points=False),
                    use_container_width=True)
    st.subheader("Monthly margin trend")
    mm = df.groupby(["Month", "Division"]).agg(S=("Sales", "sum"), P=("Gross Profit", "sum")).reset_index()
    mm["Margin %"] = mm["P"] / mm["S"] * 100
    st.plotly_chart(px.line(mm, x="Month", y="Margin %", color="Division", markers=True),
                    use_container_width=True)
    dm2 = dm.merge(division_volatility(df).rename("Margin Volatility (pp)"), left_on="Division",
                   right_index=True, how="left")
    st.dataframe(dm2.round(2), use_container_width=True, hide_index=True)

# ---------------- Tab 3 ----------------
with tab3:
    st.subheader("Cost vs sales (each point = one product)")
    fig = px.scatter(pm_view, x="Sales", y="Cost", size="Units", color="Action Flag", hover_name="Product Name",
                     text="Product Name", log_x=True, log_y=True,
                     color_discrete_map={"Healthy": "#2ca02c", "Repricing": "#ff7f0e",
                                         "Cost renegotiation": "#d62728", "Discontinuation review": "#7f7f7f"})
    fig.update_traces(textposition="top center", textfont_size=9)
    fig.update_layout(height=560)
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Price vs unit cost")
    fig = px.scatter(pm_view, x="Cost per Unit", y="Price per Unit", color="Margin %", hover_name="Product Name",
                     size="Sales", color_continuous_scale="RdYlGn")
    mx = max(pm_view["Price per Unit"].max(), pm_view["Cost per Unit"].max()) if len(pm_view) else 1
    fig.add_trace(go.Scatter(x=[0, mx], y=[0, mx], mode="lines", line=dict(dash="dot", color="grey"),
                             name="break-even"))
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Margin risk flags")
    risk = pm[pm["Action Flag"] != "Healthy"][["Product Name", "Division", "Factory", "Sales", "Margin %",
                                                "Cost per Unit", "Price per Unit", "Action Flag"]].round(2)
    if risk.empty:
        st.success("No product is below the margin threshold.")
    else:
        st.dataframe(risk, use_container_width=True, hide_index=True)
    st.caption("Rules: below threshold & below-median sales → discontinuation review; below threshold & top-quartile "
               "cost ratio → cost renegotiation; other below-threshold products → repricing.")

# ---------------- Tab 4 ----------------
with tab4:
    metric = st.radio("Pareto on", ["Sales", "Profit"], horizontal=True)
    s, n80, p80 = pareto(pm, metric)
    fig = go.Figure()
    fig.add_bar(x=s["Product Name"], y=s[metric], name=metric)
    fig.add_scatter(x=s["Product Name"], y=s["Cum %"], name="Cumulative %", yaxis="y2", mode="lines+markers")
    fig.add_hline(y=80, line_dash="dash", line_color="red", yref="y2")
    fig.update_layout(yaxis2=dict(overlaying="y", side="right", range=[0, 105], title="Cumulative %"),
                      height=520, xaxis_tickangle=-40)
    st.plotly_chart(fig, use_container_width=True)
    _, n80r, p80r = pareto(pm, "Sales")
    _, n80p, p80p = pareto(pm, "Profit")
    c = st.columns(4)
    c[0].metric("Products for 80% of revenue", f"{n80r} of {len(pm)}", f"{p80r:.0f}% of range")
    c[1].metric("Products for 80% of profit", f"{n80p} of {len(pm)}", f"{p80p:.0f}% of range")
    c[2].metric("Top product profit share", f"{pm['Profit Contribution %'].max():.1f}%")
    c[3].metric("Profit HHI", f"{hhi(pm['Profit Contribution %']):,.0f}",
                help="Herfindahl index: >2,500 = highly concentrated; 1,500–2,500 = moderate")
    top_div = dm.iloc[0]
    if top_div["Profit Share %"] > 70:
        st.error(f"Dependency risk: **{top_div['Division']}** generates {top_div['Profit Share %']:.1f}% of gross profit.")
    top_state = df.groupby("State/Province")["Gross Profit"].sum().pipe(lambda x: x / x.sum() * 100).sort_values(ascending=False)
    st.info(f"Geographic dependency: **{top_state.index[0]}** contributes {top_state.iloc[0]:.1f}% of profit; "
            f"top 3 states = {top_state.head(3).sum():.1f}%.")
    fac = df.groupby("Factory").agg(Sales=("Sales", "sum"), Profit=("Gross Profit", "sum")).reset_index()
    fac["Margin %"] = fac["Profit"] / fac["Sales"] * 100
    st.subheader("Factory view")
    st.dataframe(fac.round(2), use_container_width=True, hide_index=True)

# ---------------- Tab 5 ----------------
with tab5:
    st.subheader("Data cleaning log")
    st.json(log)
    st.markdown("""
**Method:** validate sales/cost/profit → remove duplicates and invalid rows → standardise labels →
compute margin, profit per unit and contribution → rank, segment, flag → Pareto and concentration → dashboards.

**KPIs:** Gross Margin = Profit ÷ Sales · Profit per Unit = Profit ÷ Units · Revenue/Profit Contribution = share of total ·
Margin Volatility = std-dev of monthly margin (percentage points).
""")
