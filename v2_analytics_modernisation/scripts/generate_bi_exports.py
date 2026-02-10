"""Generate dashboard-like PNG exports for the library analytics project.

Exports are created under:
- bi_powerbi/exports/

They are generated from curated CSV outputs so the repo remains reproducible.
"""

from __future__ import annotations

from pathlib import Path
import datetime
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

PAGES = [
    (1, "Dashboard Overview", "page_01_01_dashboard_overview.png"),
    (2, "Issues and Returns", "page_02_02_issues_and_returns.png"),
    (3, "Overdues Analysis", "page_03_03_overdues_analysis.png"),
    (4, "Fine Collection", "page_04_04_fine_collection.png"),
    (5, "Inventory Health", "page_05_05_inventory_health.png"),
    (6, "Category Insights", "page_06_06_category_insights.png"),
    (7, "Member Activity", "page_07_07_member_activity.png"),
    (8, "Branch Comparison", "page_08_08_branch_comparison.png"),
    (9, "Stockout Hotspots", "page_09_09_stockout_hotspots.png"),
    (10, "Overdue Ageing Buckets", "page_10_10_overdue_ageing_buckets.png"),
    (11, "Repeat Overdue Members", "page_11_11_repeat_overdue_members.png"),
    (12, "Staff Workload Proxy", "page_12_12_staff_workload_proxy.png"),
    (13, "Export Audit and Run Register", "page_13_13_export_audit_run_register.png"),
    (14, "Data Quality Summary", "page_14_14_data_quality_summary.png"),
    (15, "DQ Exceptions Detail", "page_15_15_dq_exceptions_detail.png"),
    (16, "ETL Run History", "page_16_16_etl_run_history.png"),
    (17, "Refresh Health Monitoring", "page_17_17_refresh_health_monitoring.png"),
    (18, "What-if Policy Simulation", "page_18_18_what_if_policy_simulation.png"),
    (19, "Drill-through Book Profile", "page_19_19_drillthrough_book_profile.png"),
    (
        20,
        "KPI Definitions and Measure Catalogue",
        "page_20_20_kpi_definitions_measure_catalogue.png",
    ),
]


def _header(fig, title: str, subtitle: str):
    ax = fig.add_axes([0, 0.94, 1, 0.06])
    ax.set_axis_off()
    ax.add_patch(Rectangle((0, 0), 1, 1, fill=True, alpha=0.06, linewidth=0))
    ax.text(0.02, 0.55, title, fontsize=16, fontweight="bold", va="center")
    ax.text(0.98, 0.55, subtitle, fontsize=10, ha="right", va="center")
    return ax


def _kpi_card(fig, x, y, w, h, title, value, subtitle=""):
    ax = fig.add_axes([x, y, w, h])
    ax.set_axis_off()
    ax.add_patch(Rectangle((0, 0), 1, 1, fill=False, linewidth=1))
    ax.text(0.05, 0.70, title, fontsize=9, fontweight="bold", va="center")
    ax.text(0.05, 0.35, value, fontsize=16, fontweight="bold", va="center")
    if subtitle:
        ax.text(0.05, 0.12, subtitle, fontsize=8, va="center")
    return ax


def load_curated(base: Path) -> dict[str, pd.DataFrame]:
    curated = base / "data_output/curated"
    required = {
        "dim_book": curated / "dim_book.csv",
        "dim_member": curated / "dim_member.csv",
        "fact_issue_return": curated / "fact_issue_return.csv",
        "kpi_daily": curated / "kpi_daily_issues_returns.csv",
        "kpi_overdue": curated / "kpi_overdue_daily.csv",
        "kpi_fine_weekly": curated / "kpi_fine_weekly.csv",
        "kpi_inventory": curated / "kpi_inventory_health.csv",
        "kpi_category": curated / "kpi_category_insights.csv",
        "kpi_member": curated / "kpi_member_activity_top.csv",
        "kpi_branch": curated / "kpi_branch_comparison.csv",
        "kpi_ageing": curated / "kpi_overdue_aging.csv",
        "export_manifest": curated / "export_manifest.csv",
    }
    out = {}
    for k, p in required.items():
        if not p.exists():
            raise FileNotFoundError(
                f"Missing curated output: {p}. Run etl/run_etl.py first."
            )
        out[k] = pd.read_csv(p)
    # parse dates
    out["kpi_daily"]["date"] = pd.to_datetime(out["kpi_daily"]["date"])
    out["kpi_overdue"]["date"] = pd.to_datetime(out["kpi_overdue"]["date"])
    out["kpi_fine_weekly"]["week_start"] = pd.to_datetime(
        out["kpi_fine_weekly"]["week_start"]
    )
    return out


def render_page_01(fig, data):
    _header(fig, "Dashboard Overview", "Library Analytics (synthetic)")

    books = data["dim_book"]
    members = data["dim_member"]
    fact = data["fact_issue_return"]
    daily = data["kpi_daily"]
    inv = data["kpi_inventory"]

    total_books = int(books.shape[0])
    total_members = int(members.shape[0])
    total_tx = int(fact.shape[0])
    stockouts = int((inv["stockout_flag"] == 1).sum())

    last_day = daily.sort_values("date").tail(1).iloc[0]
    issues_today = int(last_day["issues_count"])
    returns_today = int(last_day["returns_count"])

    _kpi_card(fig, 0.03, 0.80, 0.18, 0.12, "Books", f"{total_books}")
    _kpi_card(fig, 0.22, 0.80, 0.18, 0.12, "Members", f"{total_members}")
    _kpi_card(fig, 0.41, 0.80, 0.18, 0.12, "Transactions", f"{total_tx:,}")
    _kpi_card(
        fig, 0.60, 0.80, 0.18, 0.12, "Stockouts", f"{stockouts}", "est_available=0"
    )
    _kpi_card(
        fig,
        0.79,
        0.80,
        0.18,
        0.12,
        "Latest day",
        f"{issues_today}/{returns_today}",
        "issues/returns",
    )

    ax1 = fig.add_axes([0.03, 0.10, 0.60, 0.64])
    ax1.plot(daily["date"], daily["issues_count"], label="Issues")
    ax1.plot(daily["date"], daily["returns_count"], label="Returns")
    ax1.set_title("Daily issues and returns")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Count")
    ax1.legend(loc="upper left")

    ax2 = fig.add_axes([0.67, 0.10, 0.30, 0.64])
    top_cat = data["kpi_category"].sort_values("issues", ascending=False).head(8)
    ax2.barh(top_cat["category"], top_cat["issues"])
    ax2.invert_yaxis()
    ax2.set_title("Top categories by issues")
    ax2.set_xlabel("Issues")


def render_page_02(fig, data):
    _header(fig, "Issues and Returns", "Operational volume & seasonality")
    daily = data["kpi_daily"].copy().sort_values("date")
    _kpi_card(
        fig,
        0.03,
        0.80,
        0.23,
        0.12,
        "Avg issues/day",
        f"{daily['issues_count'].mean():.1f}",
    )
    _kpi_card(
        fig,
        0.27,
        0.80,
        0.23,
        0.12,
        "Avg returns/day",
        f"{daily['returns_count'].mean():.1f}",
    )
    _kpi_card(
        fig,
        0.51,
        0.80,
        0.23,
        0.12,
        "Peak issues",
        f"{int(daily['issues_count'].max())}",
    )
    _kpi_card(
        fig,
        0.75,
        0.80,
        0.22,
        0.12,
        "Peak returns",
        f"{int(daily['returns_count'].max())}",
    )

    ax1 = fig.add_axes([0.03, 0.10, 0.94, 0.64])
    ax1.plot(daily["date"], daily["issues_count"], label="Issues")
    ax1.plot(daily["date"], daily["returns_count"], label="Returns")
    ax1.set_title("Daily trend")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Count")
    ax1.legend(loc="upper left")


def render_page_03(fig, data):
    _header(fig, "Overdues Analysis", "Risk & compliance indicators")
    od = data["kpi_overdue"].copy().sort_values("date")
    _kpi_card(
        fig,
        0.03,
        0.80,
        0.23,
        0.12,
        "Avg overdue rate",
        f"{(od['overdue_rate'].mean()*100):.2f}%",
    )
    _kpi_card(
        fig,
        0.27,
        0.80,
        0.23,
        0.12,
        "Max overdue rate",
        f"{(od['overdue_rate'].max()*100):.2f}%",
    )
    _kpi_card(
        fig, 0.51, 0.80, 0.23, 0.12, "Total overdues", f"{int(od['overdues'].sum()):,}"
    )
    _kpi_card(
        fig, 0.75, 0.80, 0.22, 0.12, "Fine total", f"{od['fine_total'].sum():.0f}"
    )

    ax1 = fig.add_axes([0.03, 0.42, 0.94, 0.32])
    ax1.plot(od["date"], od["overdue_rate"] * 100)
    ax1.set_title("Overdue rate by return date (%)")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Overdue rate %")

    ax2 = fig.add_axes([0.03, 0.10, 0.46, 0.25])
    ax2.hist(od["overdue_rate"] * 100, bins=15)
    ax2.set_title("Distribution of daily overdue rate (%)")
    ax2.set_xlabel("Overdue rate %")
    ax2.set_ylabel("Days")

    ax3 = fig.add_axes([0.52, 0.10, 0.45, 0.25])
    ax3.plot(od["date"], od["fine_total"])
    ax3.set_title("Daily fine total")
    ax3.set_xlabel("Date")
    ax3.set_ylabel("Fine total")


def render_page_04(fig, data):
    _header(fig, "Fine Collection", "Revenue & policy signals")
    fw = data["kpi_fine_weekly"].copy().sort_values("week_start")
    _kpi_card(
        fig, 0.03, 0.80, 0.23, 0.12, "Total fines", f"{fw['fines_total'].sum():.0f}"
    )
    _kpi_card(
        fig, 0.27, 0.80, 0.23, 0.12, "Avg fine/tx", f"{fw['avg_fine'].mean():.2f}"
    )
    _kpi_card(fig, 0.51, 0.80, 0.23, 0.12, "Weeks", f"{fw.shape[0]}")
    _kpi_card(
        fig, 0.75, 0.80, 0.22, 0.12, "Peak week", f"{fw['fines_total'].max():.0f}"
    )

    ax1 = fig.add_axes([0.03, 0.10, 0.60, 0.64])
    ax1.plot(fw["week_start"], fw["fines_total"], label="Fines total")
    ax1.set_title("Weekly fines total")
    ax1.set_xlabel("Week start")
    ax1.set_ylabel("Fine total")
    ax1.legend(loc="upper left")

    ax2 = fig.add_axes([0.67, 0.10, 0.30, 0.64])
    ax2.bar(fw["week_start"].dt.strftime("%m-%d").tail(10), fw["avg_fine"].tail(10))
    ax2.set_title("Avg fine (last 10 weeks)")
    ax2.set_xlabel("Week")
    ax2.set_ylabel("Avg fine")
    ax2.tick_params(axis="x", rotation=45)


def render_page_05(fig, data):
    _header(fig, "Inventory Health", "Stockouts & demand pressure")
    inv = data["kpi_inventory"].copy()
    stockouts = inv[inv["stockout_flag"] == 1]
    _kpi_card(fig, 0.03, 0.80, 0.23, 0.12, "Books", f"{inv.shape[0]}")
    _kpi_card(fig, 0.27, 0.80, 0.23, 0.12, "Stockouts", f"{stockouts.shape[0]}")
    _kpi_card(
        fig, 0.51, 0.80, 0.23, 0.12, "Avg on loan", f"{inv['on_loan'].mean():.2f}"
    )
    _kpi_card(
        fig, 0.75, 0.80, 0.22, 0.12, "Top on loan", f"{int(inv['on_loan'].max())}"
    )

    top = inv.sort_values(["stockout_flag", "on_loan"], ascending=[False, False]).head(
        12
    )
    ax1 = fig.add_axes([0.03, 0.10, 0.60, 0.64])
    ax1.barh(top["book_id"], top["on_loan"])
    ax1.invert_yaxis()
    ax1.set_title("Top books by on_loan (stockouts bubble to top)")
    ax1.set_xlabel("On loan")

    ax2 = fig.add_axes([0.67, 0.10, 0.30, 0.64])
    by_branch = inv.groupby("branch")["stockout_flag"].mean().reset_index()
    ax2.bar(by_branch["branch"], by_branch["stockout_flag"] * 100)
    ax2.set_title("Stockout rate by branch (%)")
    ax2.set_xlabel("Branch")
    ax2.set_ylabel("Stockout rate %")
    ax2.tick_params(axis="x", rotation=20)


def render_page_06(fig, data):
    _header(fig, "Category Insights", "Demand, overdues and fines by category")
    cat = data["kpi_category"].copy().sort_values("issues", ascending=False)
    _kpi_card(fig, 0.03, 0.80, 0.23, 0.12, "Categories", f"{cat.shape[0]}")
    _kpi_card(fig, 0.27, 0.80, 0.23, 0.12, "Top category", str(cat.iloc[0]["category"]))
    _kpi_card(
        fig, 0.51, 0.80, 0.23, 0.12, "Top issues", f"{int(cat.iloc[0]['issues']):,}"
    )
    _kpi_card(fig, 0.75, 0.80, 0.22, 0.12, "Top fine", f"{cat['fine_total'].max():.0f}")

    ax1 = fig.add_axes([0.03, 0.10, 0.46, 0.64])
    ax1.bar(cat["category"], cat["issues"])
    ax1.set_title("Issues by category")
    ax1.set_xlabel("Category")
    ax1.set_ylabel("Issues")
    ax1.tick_params(axis="x", rotation=20)

    ax2 = fig.add_axes([0.52, 0.10, 0.45, 0.64])
    ax2.bar(cat["category"], cat["overdue_rate"] * 100)
    ax2.set_title("Overdue rate by category (%)")
    ax2.set_xlabel("Category")
    ax2.set_ylabel("Overdue rate %")
    ax2.tick_params(axis="x", rotation=20)


def render_page_07(fig, data):
    _header(fig, "Member Activity", "Top members + risk indicators")
    mem = data["kpi_member"].copy()
    _kpi_card(fig, 0.03, 0.80, 0.23, 0.12, "Members (top list)", f"{mem.shape[0]}")
    _kpi_card(fig, 0.27, 0.80, 0.23, 0.12, "Top issues", f"{int(mem['issues'].max())}")
    _kpi_card(
        fig, 0.51, 0.80, 0.23, 0.12, "Top fine total", f"{mem['fine_total'].max():.0f}"
    )
    _kpi_card(
        fig, 0.75, 0.80, 0.22, 0.12, "Top overdues", f"{int(mem['overdues'].max())}"
    )

    ax1 = fig.add_axes([0.03, 0.10, 0.94, 0.64])
    ax1.axis("off")
    show = mem.head(15)[["member_id", "issues", "overdues", "fine_total"]]
    ax1.table(cellText=show.values, colLabels=show.columns, loc="center")
    ax1.set_title("Top 15 members by issues (synthetic)")


def render_page_08(fig, data):
    _header(fig, "Branch Comparison", "Volume, overdues, stockouts")
    br = data["kpi_branch"].copy()
    _kpi_card(fig, 0.03, 0.80, 0.23, 0.12, "Branches", f"{br.shape[0]}")
    _kpi_card(
        fig,
        0.27,
        0.80,
        0.23,
        0.12,
        "Top issues branch",
        str(br.sort_values("issues", ascending=False).iloc[0]["branch"]),
    )
    _kpi_card(
        fig,
        0.51,
        0.80,
        0.23,
        0.12,
        "Max overdue rate",
        f"{(br['overdue_rate'].max()*100):.2f}%",
    )
    _kpi_card(
        fig,
        0.75,
        0.80,
        0.22,
        0.12,
        "Max stockout rate",
        f"{(br['stockout_rate'].max()*100):.1f}%",
    )

    ax1 = fig.add_axes([0.03, 0.10, 0.46, 0.64])
    ax1.bar(br["branch"], br["issues"])
    ax1.set_title("Issues by branch")
    ax1.set_xlabel("Branch")
    ax1.set_ylabel("Issues")
    ax1.tick_params(axis="x", rotation=20)

    ax2 = fig.add_axes([0.52, 0.10, 0.45, 0.64])
    ax2.bar(br["branch"], br["stockout_rate"] * 100)
    ax2.set_title("Stockout rate by branch (%)")
    ax2.set_xlabel("Branch")
    ax2.set_ylabel("Stockout rate %")
    ax2.tick_params(axis="x", rotation=20)


def render_page_09(fig, data):
    _header(fig, "Stockout Hotspots", "Which categories/branches are under pressure?")
    inv = data["kpi_inventory"].copy()
    hot = (
        inv[inv["stockout_flag"] == 1]
        .groupby(["branch", "category"])
        .size()
        .reset_index(name="stockouts")
    )
    hot = hot.sort_values("stockouts", ascending=False).head(12)

    _kpi_card(
        fig,
        0.03,
        0.80,
        0.30,
        0.12,
        "Total stockouts",
        f"{int((inv['stockout_flag']==1).sum())}",
    )
    _kpi_card(
        fig,
        0.34,
        0.80,
        0.30,
        0.12,
        "Hotspot (top)",
        (
            f"{hot.iloc[0]['branch']} / {hot.iloc[0]['category']}"
            if not hot.empty
            else "n/a"
        ),
    )
    _kpi_card(
        fig,
        0.65,
        0.80,
        0.32,
        0.12,
        "Hotspot stockouts",
        f"{int(hot.iloc[0]['stockouts']) if not hot.empty else 0}",
    )

    ax1 = fig.add_axes([0.03, 0.10, 0.94, 0.64])
    ax1.axis("off")
    if hot.empty:
        ax1.text(0.5, 0.5, "No stockouts in synthetic run.", ha="center", va="center")
    else:
        ax1.table(cellText=hot.values, colLabels=hot.columns, loc="center")
    ax1.set_title("Stockout hotspot table (top rows)")


def render_page_10(fig, data):
    _header(fig, "Overdue Ageing Buckets", "How late are returns when they are late?")
    ageing = data["kpi_ageing"].copy()
    ageing["bucket"] = ageing["bucket"].astype(str)

    _kpi_card(fig, 0.03, 0.80, 0.23, 0.12, "Buckets", f"{ageing.shape[0]}")
    _kpi_card(
        fig,
        0.27,
        0.80,
        0.23,
        0.12,
        "Total overdue tx",
        f"{int(ageing['tx_count'].sum()):,}",
    )
    _kpi_card(
        fig, 0.51, 0.80, 0.23, 0.12, "Fine total", f"{ageing['fine_total'].sum():.0f}"
    )

    ax1 = fig.add_axes([0.03, 0.10, 0.46, 0.64])
    ax1.bar(ageing["bucket"], ageing["tx_count"])
    ax1.set_title("Overdue transactions by ageing bucket")
    ax1.set_xlabel("Days overdue bucket")
    ax1.set_ylabel("Transactions")

    ax2 = fig.add_axes([0.52, 0.10, 0.45, 0.64])
    ax2.bar(ageing["bucket"], ageing["fine_total"])
    ax2.set_title("Fine total by ageing bucket")
    ax2.set_xlabel("Days overdue bucket")
    ax2.set_ylabel("Fine total")


def render_page_11(fig, data):
    _header(fig, "Repeat Overdue Members", "Member-level compliance view")
    fact = pd.read_csv(
        Path(__file__).resolve().parents[1]
        / "data_output/curated/fact_issue_return.csv"
    )
    # compute per member overdue counts
    m = (
        fact.groupby("member_id")
        .agg(
            issues=("transaction_id", "count"),
            overdues=("overdue_flag", "sum"),
            fine_total=("fine_amount", "sum"),
        )
        .reset_index()
    )
    m = (
        m[m["overdues"] > 0]
        .sort_values(["overdues", "fine_total"], ascending=False)
        .head(20)
    )

    _kpi_card(
        fig,
        0.03,
        0.80,
        0.30,
        0.12,
        "Members with overdues",
        f"{int((fact.groupby('member_id')['overdue_flag'].sum()>0).sum())}",
    )
    _kpi_card(
        fig,
        0.34,
        0.80,
        0.30,
        0.12,
        "Top overdue count",
        f"{int(m['overdues'].max()) if not m.empty else 0}",
    )
    _kpi_card(
        fig,
        0.65,
        0.80,
        0.32,
        0.12,
        "Top fine total",
        f"{m['fine_total'].max():.0f}" if not m.empty else "0",
    )

    ax1 = fig.add_axes([0.03, 0.10, 0.94, 0.64])
    ax1.axis("off")
    if m.empty:
        ax1.text(
            0.5, 0.5, "No overdue members in synthetic run.", ha="center", va="center"
        )
    else:
        ax1.table(cellText=m.values, colLabels=m.columns, loc="center")
    ax1.set_title("Members with repeated overdues (top 20)")


def render_page_12(fig, data):
    _header(
        fig,
        "Staff Workload Proxy",
        "Issues processed by branch (proxy for desk workload)",
    )
    fact = pd.read_csv(
        Path(__file__).resolve().parents[1]
        / "data_output/curated/fact_issue_return.csv",
        parse_dates=["issue_date", "return_date"],
    )
    fact["issue_day"] = (
        fact["issue_date"].dt.to_period("W").apply(lambda r: r.start_time)
    )
    by = fact.groupby(["issue_day", "branch"]).size().reset_index(name="issues")
    branches = sorted(by["branch"].dropna().unique())

    _kpi_card(fig, 0.03, 0.80, 0.23, 0.12, "Branches", f"{len(branches)}")
    _kpi_card(fig, 0.27, 0.80, 0.23, 0.12, "Weeks", f"{by['issue_day'].nunique()}")
    _kpi_card(
        fig, 0.51, 0.80, 0.23, 0.12, "Peak weekly issues", f"{int(by['issues'].max())}"
    )

    ax1 = fig.add_axes([0.03, 0.10, 0.94, 0.64])
    for b in branches[:4]:
        s = by[by["branch"] == b].sort_values("issue_day")
        ax1.plot(s["issue_day"], s["issues"], label=b)
    ax1.set_title("Weekly issues by branch (top 4 branches shown)")
    ax1.set_xlabel("Week start")
    ax1.set_ylabel("Issues")
    ax1.legend(loc="upper left")


def render_page_13(fig, data):
    _header(fig, "Export Audit and Run Register", "Are artefacts complete?")
    base = Path(__file__).resolve().parents[1]
    manifest = data["export_manifest"].copy()
    run_reg_path = base / "reports/run_register_snapshot.csv"
    refresh_path = base / "reports/refresh_health_snapshot.csv"

    run_reg = pd.read_csv(run_reg_path) if run_reg_path.exists() else pd.DataFrame()
    refresh = pd.read_csv(refresh_path) if refresh_path.exists() else pd.DataFrame()

    _kpi_card(
        fig, 0.03, 0.80, 0.23, 0.12, "Curated tables", f"{int(manifest.shape[0])}"
    )
    _kpi_card(
        fig,
        0.27,
        0.80,
        0.23,
        0.12,
        "Run ID",
        str(run_reg.iloc[0]["run_id"]) if not run_reg.empty else "n/a",
    )
    _kpi_card(
        fig,
        0.51,
        0.80,
        0.23,
        0.12,
        "Refresh status",
        str(refresh.iloc[0]["status"]) if not refresh.empty else "n/a",
    )
    _kpi_card(
        fig,
        0.75,
        0.80,
        0.22,
        0.12,
        "DQ status",
        str(refresh.iloc[0].get("dq_status", "n/a")) if not refresh.empty else "n/a",
    )

    ax1 = fig.add_axes([0.03, 0.10, 0.46, 0.64])
    ax1.axis("off")
    ax1.table(
        cellText=manifest.head(12).values, colLabels=manifest.columns, loc="center"
    )
    ax1.set_title("Export manifest (top rows)")

    ax2 = fig.add_axes([0.52, 0.10, 0.45, 0.64])
    ax2.axis("off")
    if run_reg.empty:
        ax2.text(
            0.5, 0.5, "run_register_snapshot.csv missing", ha="center", va="center"
        )
    else:
        ax2.table(cellText=run_reg.values, colLabels=run_reg.columns, loc="center")
    ax2.set_title("Run register snapshot")


def render_page_14(fig, data):
    _header(fig, "Data Quality Summary", "Rule health and severity")
    base = Path(__file__).resolve().parents[1]
    dq_path = base / "reports/dq_summary.json"
    if dq_path.exists():
        dq = json.loads(dq_path.read_text(encoding="utf-8"))
        rules = pd.DataFrame(dq["rules"])
        overall = dq["overall_status"]
    else:
        rules = pd.DataFrame(columns=["rule_id", "severity", "status", "fail_rows"])
        overall = "n/a"

    _kpi_card(fig, 0.03, 0.80, 0.30, 0.12, "Overall DQ", str(overall))
    _kpi_card(fig, 0.34, 0.80, 0.20, 0.12, "Rules", f"{rules.shape[0]}")
    _kpi_card(
        fig,
        0.55,
        0.80,
        0.20,
        0.12,
        "WARN",
        f"{int((rules['status']=='WARN').sum()) if not rules.empty else 0}",
    )
    _kpi_card(
        fig,
        0.76,
        0.80,
        0.21,
        0.12,
        "FAIL",
        f"{int((rules['status']=='FAIL').sum()) if not rules.empty else 0}",
    )

    ax1 = fig.add_axes([0.03, 0.10, 0.46, 0.64])
    if rules.empty:
        ax1.text(0.5, 0.5, "dq_summary.json not found", ha="center", va="center")
    else:
        counts = rules.groupby(["severity", "status"]).size().reset_index(name="count")
        # plot as bars: status by severity
        sev = ["INFO", "WARN", "FAIL"]
        status = ["PASS", "WARN", "FAIL"]
        for s in status:
            vals = []
            for v in sev:
                c = counts.loc[
                    (counts["severity"] == v) & (counts["status"] == s), "count"
                ]
                vals.append(int(c.iloc[0]) if len(c) else 0)
            ax1.plot(sev, vals, marker="o", label=s)
        ax1.set_title("Rule counts by severity/status")
        ax1.set_xlabel("Severity")
        ax1.set_ylabel("Count")
        ax1.legend(loc="upper right")

    ax2 = fig.add_axes([0.52, 0.10, 0.45, 0.64])
    ax2.axis("off")
    if not rules.empty:
        show = rules[["rule_id", "severity", "status", "fail_rows"]].copy()
        ax2.table(cellText=show.values, colLabels=show.columns, loc="center")
    ax2.set_title("DQ rule table")


def render_page_15(fig, data):
    _header(fig, "DQ Exceptions Detail", "Rows that triggered WARN/FAIL rules")
    base = Path(__file__).resolve().parents[1]
    issue_path = base / "logs/V2_DQ_ISSUE_REGISTER.csv"
    if issue_path.exists():
        issues = pd.read_csv(issue_path)
    else:
        issues = pd.DataFrame()

    _kpi_card(fig, 0.03, 0.80, 0.30, 0.12, "Open exceptions", f"{issues.shape[0]}")
    _kpi_card(
        fig,
        0.34,
        0.80,
        0.30,
        0.12,
        "Latest rule",
        str(issues.tail(1)["rule_id"].iloc[0]) if not issues.empty else "n/a",
    )

    ax1 = fig.add_axes([0.03, 0.10, 0.94, 0.64])
    ax1.axis("off")
    if issues.empty:
        ax1.text(
            0.5, 0.5, "No issues found (or file missing).", ha="center", va="center"
        )
    else:
        show = issues.tail(15)
        ax1.table(cellText=show.values, colLabels=show.columns, loc="center")
    ax1.set_title("DQ issue register (last rows)")


def render_page_16(fig, data):
    _header(fig, "ETL Run History", "Operational monitoring snapshot")
    base = Path(__file__).resolve().parents[1]
    run_path = base / "reports/run_register_snapshot.csv"
    if run_path.exists():
        run = pd.read_csv(run_path)
    else:
        run = pd.DataFrame()

    _kpi_card(
        fig,
        0.03,
        0.80,
        0.30,
        0.12,
        "Latest run",
        str(run.iloc[0]["run_id"]) if not run.empty else "n/a",
    )
    _kpi_card(
        fig,
        0.34,
        0.80,
        0.30,
        0.12,
        "Transactions",
        f"{int(run.iloc[0]['transactions_rows']):,}" if not run.empty else "0",
    )

    ax1 = fig.add_axes([0.03, 0.10, 0.94, 0.64])
    ax1.axis("off")
    if run.empty:
        ax1.text(
            0.5, 0.5, "run_register_snapshot.csv missing", ha="center", va="center"
        )
    else:
        ax1.table(cellText=run.values, colLabels=run.columns, loc="center")
    ax1.set_title("Run register snapshot (latest)")


def render_page_17(fig, data):
    _header(fig, "Refresh Health Monitoring", "DQ status + exports completeness")
    base = Path(__file__).resolve().parents[1]
    refresh_path = base / "reports/refresh_health_snapshot.csv"
    refresh = pd.read_csv(refresh_path) if refresh_path.exists() else pd.DataFrame()

    _kpi_card(
        fig,
        0.03,
        0.80,
        0.30,
        0.12,
        "Refresh status",
        str(refresh.iloc[0]["status"]) if not refresh.empty else "n/a",
    )
    _kpi_card(
        fig,
        0.34,
        0.80,
        0.30,
        0.12,
        "DQ status",
        str(refresh.iloc[0].get("dq_status", "n/a")) if not refresh.empty else "n/a",
    )
    exp = int(refresh.iloc[0].get("exports_expected", 0)) if not refresh.empty else 0
    gen = int(refresh.iloc[0].get("exports_generated", 0)) if not refresh.empty else 0
    _kpi_card(
        fig, 0.65, 0.80, 0.32, 0.12, "Exports", f"{gen}/{exp}", "generated/expected"
    )

    ax1 = fig.add_axes([0.03, 0.10, 0.94, 0.64])
    ax1.axis("off")
    if refresh.empty:
        ax1.text(
            0.5, 0.5, "refresh_health_snapshot.csv missing", ha="center", va="center"
        )
    else:
        ax1.table(cellText=refresh.values, colLabels=refresh.columns, loc="center")
    ax1.set_title("Refresh snapshot")


def render_page_18(fig, data):
    _header(fig, "What-if Policy Simulation", "Fine policy sensitivity (synthetic)")
    od = data["kpi_overdue"].copy()
    total_overdue_days = int(
        (
            pd.read_csv(
                Path(__file__).resolve().parents[1]
                / "data_output/curated/fact_issue_return.csv"
            )["days_overdue"]
        ).sum()
    )

    fine_per_day_values = np.array([0.5, 1.0, 2.0, 3.0])
    projected = fine_per_day_values * total_overdue_days

    _kpi_card(
        fig, 0.03, 0.80, 0.30, 0.12, "Total overdue days", f"{total_overdue_days:,}"
    )
    _kpi_card(fig, 0.34, 0.80, 0.30, 0.12, "Current policy", "1.0 / day")

    ax1 = fig.add_axes([0.03, 0.10, 0.46, 0.64])
    ax1.bar([str(v) for v in fine_per_day_values], projected)
    ax1.set_title("Projected fine total vs fine_per_day")
    ax1.set_xlabel("Fine per day")
    ax1.set_ylabel("Projected fine total")

    ax2 = fig.add_axes([0.52, 0.10, 0.45, 0.64])
    ax2.plot(od["date"], od["overdue_rate"] * 100)
    ax2.set_title("Overdue rate context (%)")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Overdue rate %")


def render_page_19(fig, data):
    _header(fig, "Drill-through Book Profile", "Single book demand + overdue profile")
    fact = pd.read_csv(
        Path(__file__).resolve().parents[1]
        / "data_output/curated/fact_issue_return.csv",
        parse_dates=["issue_date", "return_date"],
    )
    top_book = fact.groupby("book_id").size().sort_values(ascending=False).index[0]
    book = (
        data["dim_book"].loc[data["dim_book"]["book_id"] == top_book].iloc[0].to_dict()
    )
    bf = fact[fact["book_id"] == top_book].copy()

    _kpi_card(fig, 0.03, 0.80, 0.30, 0.12, "Book", top_book, book.get("title", ""))
    _kpi_card(fig, 0.34, 0.80, 0.20, 0.12, "Issues", f"{bf.shape[0]}")
    _kpi_card(
        fig, 0.55, 0.80, 0.20, 0.12, "Overdues", f"{int(bf['overdue_flag'].sum())}"
    )
    _kpi_card(
        fig, 0.76, 0.80, 0.21, 0.12, "Fine total", f"{bf['fine_amount'].sum():.0f}"
    )

    bf_daily = bf.groupby(bf["issue_date"].dt.date).size().reset_index(name="issues")
    bf_daily["issue_date"] = pd.to_datetime(bf_daily["issue_date"])

    ax1 = fig.add_axes([0.03, 0.10, 0.60, 0.64])
    ax1.plot(bf_daily["issue_date"], bf_daily["issues"])
    ax1.set_title("Issues over time (selected book)")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Issues")

    ax2 = fig.add_axes([0.67, 0.10, 0.30, 0.64])
    ax2.hist(bf["days_on_loan"].dropna(), bins=12)
    ax2.set_title("Days on loan distribution")
    ax2.set_xlabel("Days on loan")
    ax2.set_ylabel("Transactions")


def render_page_20(fig, data):
    _header(fig, "KPI Definitions and Measure Catalogue", "Reference page")
    base = Path(__file__).resolve().parents[1]
    kpi_defs = pd.read_csv(base / "bi_powerbi/kpi_definitions.csv")

    _kpi_card(fig, 0.03, 0.80, 0.30, 0.12, "KPIs defined", f"{kpi_defs.shape[0]}")
    _kpi_card(
        fig,
        0.34,
        0.80,
        0.30,
        0.12,
        "Measure catalogue",
        "bi_powerbi/measure_catalogue.md",
    )

    ax1 = fig.add_axes([0.03, 0.10, 0.94, 0.64])
    ax1.axis("off")
    ax1.table(cellText=kpi_defs.values, colLabels=kpi_defs.columns, loc="center")
    ax1.set_title("KPI definitions (table)")


RENDERERS = {
    1: render_page_01,
    2: render_page_02,
    3: render_page_03,
    4: render_page_04,
    5: render_page_05,
    6: render_page_06,
    7: render_page_07,
    8: render_page_08,
    9: render_page_09,
    10: render_page_10,
    11: render_page_11,
    12: render_page_12,
    13: render_page_13,
    14: render_page_14,
    15: render_page_15,
    16: render_page_16,
    17: render_page_17,
    18: render_page_18,
    19: render_page_19,
    20: render_page_20,
}


def main() -> None:
    base = Path(__file__).resolve().parents[1]  # v2_analytics_modernisation
    exports = base / "bi_powerbi/exports"
    exports.mkdir(parents=True, exist_ok=True)

    data = load_curated(base)

    for page_no, title, filename in PAGES:
        fig = plt.figure(figsize=(16, 9), dpi=120)
        RENDERERS[page_no](fig, data)
        out_path = exports / filename
        fig.savefig(out_path, bbox_inches="tight")
        plt.close(fig)
        print("Wrote", out_path)

    # convenience aliases
    # Dashboard overview
    (exports / "dashboard_overview.png").write_bytes(
        (exports / PAGES[0][2]).read_bytes()
    )
    # KPI defs
    (exports / "kpi_definitions.png").write_bytes((exports / PAGES[-1][2]).read_bytes())

    # Update refresh snapshot with exports count
    refresh_path = base / "reports/refresh_health_snapshot.csv"
    if refresh_path.exists():
        snap = pd.read_csv(refresh_path)
        snap.loc[0, "exports_generated"] = len(list(exports.glob("page_*.png")))
        snap.loc[0, "exports_generated_time"] = (
            datetime.datetime.now().replace(microsecond=0).isoformat(sep=" ")
        )
        snap.to_csv(refresh_path, index=False)


if __name__ == "__main__":
    main()
