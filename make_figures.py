"""Generate static figures for the research paper (figures/*.png)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from analysis import *

df, log = load_and_clean("data/Nassau_Candy_Distributor.csv")
pm = product_metrics(df)
dm = division_metrics(df)
plt.rcParams.update({"figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False})
col = {"Chocolate": "#6f4e37", "Other": "#e8590c", "Sugar": "#1c7ed6"}

s = pm.sort_values("Margin %")
fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(s["Product Name"], s["Margin %"], color=[col[d] for d in s["Division"]])
ax.axvline(66.1 * .9, color="red", ls="--", lw=1)
ax.set_xlabel("Gross margin (%)"); ax.set_title("Fig 1. Gross margin by product")
plt.tight_layout(); plt.savefig("figures/fig1_margin.png"); plt.close()

fig, ax = plt.subplots(figsize=(8, 4))
x = range(len(dm)); w = .38
ax.bar([i - w/2 for i in x], dm["Revenue Share %"], w, label="Revenue share", color="#adb5bd")
ax.bar([i + w/2 for i in x], dm["Profit Share %"], w, label="Profit share", color="#d6336c")
ax.set_xticks(list(x)); ax.set_xticklabels(dm["Division"]); ax.set_ylabel("%"); ax.legend()
ax.set_title("Fig 2. Revenue share vs profit share by division")
plt.tight_layout(); plt.savefig("figures/fig2_division.png"); plt.close()

fig, axs = plt.subplots(1, 2, figsize=(11, 4))
for ax, c in zip(axs, ["Sales", "Profit"]):
    p, n, _ = pareto(pm, c)
    ax.bar(p["Product Name"], p[c], color="#868e96"); ax.tick_params(axis="x", rotation=80, labelsize=7)
    a2 = ax.twinx(); a2.plot(p["Product Name"], p["Cum %"], "o-", color="#d6336c"); a2.axhline(80, ls="--", c="red", lw=1)
    a2.set_ylim(0, 105); ax.set_title(f"Pareto: {c}")
fig.suptitle("Fig 3. Profit concentration"); plt.tight_layout(); plt.savefig("figures/fig3_pareto.png"); plt.close()

fig, ax = plt.subplots(figsize=(7, 5))
for d, g in pm.groupby("Division"):
    ax.scatter(g["Sales"], g["Cost"], s=60, c=col[d], label=d)
for _, r in pm.iterrows():
    if r["Sales"] > 5000 or r["Product Name"] == "Kazookles":
        ax.annotate(r["Product Name"].replace("Wonka Bar - ", ""), (r["Sales"], r["Cost"]), fontsize=7, xytext=(4, 4), textcoords="offset points")
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("Sales ($)"); ax.set_ylabel("Cost ($)"); ax.legend()
ax.set_title("Fig 4. Cost vs sales by product")
plt.tight_layout(); plt.savefig("figures/fig4_cost_sales.png"); plt.close()

m = monthly_margin(df)
fig, ax = plt.subplots(figsize=(8, 3.5)); ax.plot(m["Month"], m["Margin %"], "o-", color="#d6336c")
ax.set_ylabel("Portfolio margin (%)"); ax.set_title("Fig 5. Monthly portfolio margin"); ax.set_ylim(60, 70)
plt.tight_layout(); plt.savefig("figures/fig5_trend.png"); plt.close()

# numbers for the write-up
print(df.groupby("Factory").apply(lambda x: x["Gross Profit"].sum()/x["Sales"].sum()*100).round(1).to_dict())
print(division_volatility(df).round(2).to_dict())
print("margin overall", df["Gross Profit"].sum()/df["Sales"].sum()*100, df.Sales.sum(), df["Gross Profit"].sum())
cm=pm[pm.Division=="Chocolate"]; print("choc top5 share of profit", cm["Profit Contribution %"].sum())
ps=df.groupby("State/Province")["Gross Profit"].sum(); ps=ps/ps.sum()*100; print(ps.sort_values(ascending=False).head(3).round(1).to_dict())
print("Kazookles loss vs avg margin $", pm.loc[pm["Product Name"]=="Kazookles","Sales"].iloc[0]*(0.661-0.0769))
print("Wallpaper sales share", pm.loc[pm["Product Name"]=="Lickable Wallpaper","Profit Contribution %"].iloc[0])
