import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Nassau Candy Profitability Analytics",
    page_icon="🍫",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================

st.title("🍫 Nassau Candy Distributor")

st.subheader(
    "Product Line Profitability & Margin Performance Analysis"
)


# =========================================================
# PROJECT OBJECTIVE
# =========================================================

st.markdown(
    """
    ### 📌 Project Objective

    This dashboard evaluates product-line profitability for
    Nassau Candy Distributor by analyzing revenue, cost,
    gross profit, gross margin, division performance,
    margin risk, and profit concentration.

    **Business Goal:** Identify profitable products,
    underperforming products, cost-heavy products, and
    opportunities for pricing and cost optimization.
    """
)


# =========================================================
# HOW TO USE
# =========================================================

with st.expander("📖 How to Use This Dashboard"):

    st.markdown(
        """
        **Step 1:** Use the sidebar to select a date range,
        division, or product.

        **Step 2:** Adjust the **Minimum Gross Margin (%)**
        slider to focus on products meeting your target margin.

        **Step 3:** Review product and division profitability.

        **Step 4:** Use Cost vs Margin Diagnostics to identify
        margin risks.

        **Step 5:** Review Profit Concentration to understand
        which products contribute most to revenue and profit.

        **Step 6:** Review the Management Recommendations
        section for product-level actions.

        **Step 7:** Download the analysis tables as CSV files.
        """
    )


# =========================================================
# LOAD DATA
# =========================================================

try:

    df = pd.read_csv("Nassau_Candy_Analyzed.csv")

except FileNotFoundError:

    st.error(
        "Nassau_Candy_Analyzed.csv was not found. "
        "Make sure the file is in the same folder as app.py."
    )

    st.stop()


# Convert Order Date
df["Order Date"] = pd.to_datetime(
    df["Order Date"],
    errors="coerce"
)


# =========================================================
# DATASET STATUS
# =========================================================

st.success("Dataset loaded successfully.")

st.caption(
    f"Analysis period: "
    f"{df['Order Date'].min().strftime('%d %b %Y')} "
    f"to "
    f"{df['Order Date'].max().strftime('%d %b %Y')} "
    f"| Records: {len(df):,}"
)


# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("🎛️ Dashboard Filters")


# ---------------------------------------------------------
# DATE FILTER
# ---------------------------------------------------------

min_date = df["Order Date"].min().date()

max_date = df["Order Date"].max().date()


date_range = st.sidebar.date_input(
    "📅 Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


# ---------------------------------------------------------
# DIVISION FILTER
# ---------------------------------------------------------

division_options = ["All"] + sorted(
    df["Division"].dropna().unique().tolist()
)


selected_division = st.sidebar.selectbox(
    "🏭 Division",
    division_options
)


# ---------------------------------------------------------
# PRODUCT SEARCH
# ---------------------------------------------------------

product_search = st.sidebar.text_input(
    "🔎 Search Product"
)


# ---------------------------------------------------------
# GROSS MARGIN THRESHOLD
# ---------------------------------------------------------

margin_threshold = st.sidebar.slider(
    "📏 Minimum Gross Margin (%)",
    min_value=0.0,
    max_value=100.0,
    value=0.0,
    step=1.0
)


# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df.copy()


# ---------------------------------------------------------
# DATE FILTER
# ---------------------------------------------------------

if len(date_range) == 2:

    filtered_df = filtered_df[
        (
            filtered_df["Order Date"].dt.date
            >= date_range[0]
        )
        &
        (
            filtered_df["Order Date"].dt.date
            <= date_range[1]
        )
    ]


# ---------------------------------------------------------
# DIVISION FILTER
# ---------------------------------------------------------

if selected_division != "All":

    filtered_df = filtered_df[
        filtered_df["Division"]
        == selected_division
    ]


# ---------------------------------------------------------
# PRODUCT SEARCH
# ---------------------------------------------------------

if product_search:

    filtered_df = filtered_df[
        filtered_df["Product Name"].str.contains(
            product_search,
            case=False,
            na=False
        )
    ]


# =========================================================
# CHECK FILTER RESULTS
# =========================================================

if filtered_df.empty:

    st.warning(
        "No data is available for the selected filters. "
        "Please adjust the date, division, or product search."
    )

    st.stop()


# =========================================================
# KPI CALCULATIONS
# =========================================================

total_revenue = filtered_df["Sales"].sum()

total_cost = filtered_df["Cost"].sum()

total_profit = filtered_df["Gross Profit"].sum()

gross_margin = (
    total_profit / total_revenue * 100
    if total_revenue != 0
    else 0
)

total_units = filtered_df["Units"].sum()

total_products = filtered_df["Product ID"].nunique()


# =========================================================
# KPI SECTION
# =========================================================

st.markdown("---")

st.subheader("📊 Key Performance Indicators")


col1, col2, col3, col4, col5 = st.columns(5)


col1.metric(
    "Total Revenue",
    f"${total_revenue:,.2f}"
)


col2.metric(
    "Total Cost",
    f"${total_cost:,.2f}"
)


col3.metric(
    "Gross Profit",
    f"${total_profit:,.2f}"
)


col4.metric(
    "Gross Margin",
    f"{gross_margin:.2f}%"
)


col5.metric(
    "Products",
    f"{total_products}"
)


# =========================================================
# PRODUCT PROFITABILITY
# =========================================================

st.markdown("---")

st.header("🍬 Product Profitability Overview")


product_summary = filtered_df.groupby(
    [
        "Product ID",
        "Product Name",
        "Division"
    ],
    as_index=False
).agg({
    "Sales": "sum",
    "Units": "sum",
    "Gross Profit": "sum",
    "Cost": "sum"
})


# ---------------------------------------------------------
# GROSS MARGIN
# ---------------------------------------------------------

product_summary["Gross Margin %"] = np.where(
    product_summary["Sales"] != 0,
    (
        product_summary["Gross Profit"]
        / product_summary["Sales"]
    ) * 100,
    0
)


# ---------------------------------------------------------
# PROFIT PER UNIT
# ---------------------------------------------------------

product_summary["Profit per Unit"] = np.where(
    product_summary["Units"] != 0,
    (
        product_summary["Gross Profit"]
        / product_summary["Units"]
    ),
    0
)


# =========================================================
# APPLY MARGIN THRESHOLD
# =========================================================

product_summary_filtered = product_summary[
    product_summary["Gross Margin %"]
    >= margin_threshold
].copy()


st.info(
    f"Showing products with Gross Margin ≥ "
    f"{margin_threshold:.0f}%."
)


# =========================================================
# CHECK MARGIN FILTER
# =========================================================

if product_summary_filtered.empty:

    st.warning(
        "No products meet the selected gross margin "
        "threshold. Please lower the margin threshold."
    )

    st.stop()


# =========================================================
# GROSS PROFIT CHART
# =========================================================

profit_chart = product_summary_filtered.sort_values(
    "Gross Profit",
    ascending=True
)


fig_profit = px.bar(
    profit_chart,
    x="Gross Profit",
    y="Product Name",
    color="Division",
    orientation="h",
    title="Gross Profit by Product"
)


fig_profit.update_layout(
    height=600,
    xaxis_title="Gross Profit",
    yaxis_title="Product"
)


st.plotly_chart(
    fig_profit,
    use_container_width=True
)


# =========================================================
# GROSS MARGIN CHART
# =========================================================

margin_chart = product_summary_filtered.sort_values(
    "Gross Margin %",
    ascending=True
)


fig_margin = px.bar(
    margin_chart,
    x="Gross Margin %",
    y="Product Name",
    color="Division",
    orientation="h",
    title="Gross Margin % by Product"
)


fig_margin.update_layout(
    height=600,
    xaxis_title="Gross Margin (%)",
    yaxis_title="Product"
)


st.plotly_chart(
    fig_margin,
    use_container_width=True
)


# =========================================================
# PRODUCT DETAILS TABLE
# =========================================================

st.subheader("📋 Product Profitability Details")


display_columns = [
    "Product Name",
    "Division",
    "Sales",
    "Cost",
    "Gross Profit",
    "Gross Margin %",
    "Profit per Unit"
]


product_display = product_summary_filtered[
    display_columns
].copy()


product_display["Sales"] = (
    product_display["Sales"].round(2)
)

product_display["Cost"] = (
    product_display["Cost"].round(2)
)

product_display["Gross Profit"] = (
    product_display["Gross Profit"].round(2)
)

product_display["Gross Margin %"] = (
    product_display["Gross Margin %"].round(2)
)

product_display["Profit per Unit"] = (
    product_display["Profit per Unit"].round(2)
)


st.dataframe(
    product_display.sort_values(
        "Gross Profit",
        ascending=False
    ),
    use_container_width=True,
    hide_index=True
)


# =========================================================
# DIVISION PERFORMANCE
# =========================================================

st.markdown("---")

st.header("🏭 Division Performance")


division_summary = filtered_df.groupby(
    "Division",
    as_index=False
).agg({
    "Sales": "sum",
    "Cost": "sum",
    "Gross Profit": "sum",
    "Units": "sum"
})


division_summary["Gross Margin %"] = np.where(
    division_summary["Sales"] != 0,
    (
        division_summary["Gross Profit"]
        / division_summary["Sales"]
    ) * 100,
    0
)


division_summary["Profit per Unit"] = np.where(
    division_summary["Units"] != 0,
    (
        division_summary["Gross Profit"]
        / division_summary["Units"]
    ),
    0
)


division_summary["Revenue Contribution %"] = (
    division_summary["Sales"]
    / division_summary["Sales"].sum()
) * 100


division_summary["Profit Contribution %"] = (
    division_summary["Gross Profit"]
    / division_summary["Gross Profit"].sum()
) * 100


# =========================================================
# REVENUE VS PROFIT
# =========================================================

fig_division = px.bar(
    division_summary,
    x="Division",
    y=[
        "Sales",
        "Gross Profit"
    ],
    barmode="group",
    title="Revenue vs Gross Profit by Division"
)


fig_division.update_layout(
    yaxis_title="Amount",
    xaxis_title="Division"
)


st.plotly_chart(
    fig_division,
    use_container_width=True
)


# =========================================================
# DIVISION GROSS MARGIN
# =========================================================

fig_division_margin = px.bar(
    division_summary,
    x="Division",
    y="Gross Margin %",
    title="Gross Margin % by Division",
    text="Gross Margin %"
)


fig_division_margin.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)


fig_division_margin.update_layout(
    yaxis_title="Gross Margin (%)",
    xaxis_title="Division"
)


st.plotly_chart(
    fig_division_margin,
    use_container_width=True
)


# =========================================================
# DIVISION DETAILS
# =========================================================

st.subheader("📋 Division Performance Details")


division_display = division_summary.copy()


for column in [
    "Sales",
    "Cost",
    "Gross Profit",
    "Profit per Unit",
    "Gross Margin %",
    "Revenue Contribution %",
    "Profit Contribution %"
]:

    if column in division_display.columns:

        division_display[column] = (
            division_display[column].round(2)
        )


st.dataframe(
    division_display.sort_values(
        "Gross Profit",
        ascending=False
    ),
    use_container_width=True,
    hide_index=True
)


# =========================================================
# COST VS MARGIN DIAGNOSTICS
# =========================================================

st.markdown("---")

st.header("💰 Cost vs Margin Diagnostics")


cost_summary = product_summary_filtered.copy()


cost_summary["Cost %"] = np.where(
    cost_summary["Sales"] != 0,
    (
        cost_summary["Cost"]
        / cost_summary["Sales"]
    ) * 100,
    0
)


# =========================================================
# MARGIN RISK
# =========================================================

margin_median = (
    cost_summary["Gross Margin %"].median()
)


cost_median = (
    cost_summary["Cost %"].median()
)


cost_summary["Margin Risk"] = np.where(
    (
        cost_summary["Gross Margin %"]
        < margin_median
    )
    &
    (
        cost_summary["Cost %"]
        >= cost_median
    ),
    "High Risk",
    "Normal"
)


# =========================================================
# COST VS SALES
# =========================================================

fig_cost_sales = px.scatter(
    cost_summary,
    x="Sales",
    y="Cost",
    size="Gross Profit",
    color="Margin Risk",
    hover_name="Product Name",
    hover_data=[
        "Division",
        "Gross Margin %",
        "Profit per Unit"
    ],
    title="Cost vs Sales by Product"
)


fig_cost_sales.update_layout(
    xaxis_title="Sales",
    yaxis_title="Cost"
)


st.plotly_chart(
    fig_cost_sales,
    use_container_width=True
)


# =========================================================
# COST % VS GROSS MARGIN
# =========================================================

fig_cost_margin = px.scatter(
    cost_summary,
    x="Cost %",
    y="Gross Margin %",
    color="Division",
    size="Gross Profit",
    hover_name="Product Name",
    title="Cost % vs Gross Margin"
)


fig_cost_margin.update_layout(
    xaxis_title="Cost as % of Sales",
    yaxis_title="Gross Margin (%)"
)


st.plotly_chart(
    fig_cost_margin,
    use_container_width=True
)


# =========================================================
# MARGIN RISK PRODUCTS
# =========================================================

st.subheader("⚠️ Margin Risk Products")


risk_products = cost_summary[
    cost_summary["Margin Risk"]
    == "High Risk"
].sort_values(
    "Gross Margin %"
)


if not risk_products.empty:

    st.dataframe(
        risk_products[
            [
                "Product Name",
                "Division",
                "Sales",
                "Cost",
                "Cost %",
                "Gross Profit",
                "Gross Margin %",
                "Margin Risk"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No high-risk products found under "
        "the current filters."
    )


# =========================================================
# PROFIT CONCENTRATION / PARETO ANALYSIS
# =========================================================

st.markdown("---")

st.header("📈 Profit Concentration Analysis")


# ---------------------------------------------------------
# REVENUE CONCENTRATION
# ---------------------------------------------------------

pareto = product_summary_filtered.sort_values(
    "Sales",
    ascending=False
).copy()


total_sales_filtered = (
    pareto["Sales"].sum()
)


if total_sales_filtered > 0:

    pareto["Revenue Contribution %"] = (
        pareto["Sales"]
        / total_sales_filtered
    ) * 100

else:

    pareto["Revenue Contribution %"] = 0


pareto["Cumulative Revenue %"] = (
    pareto["Revenue Contribution %"]
    .cumsum()
)


# ---------------------------------------------------------
# PROFIT CONCENTRATION
# ---------------------------------------------------------

pareto_profit = product_summary_filtered.sort_values(
    "Gross Profit",
    ascending=False
).copy()


total_profit_filtered = (
    pareto_profit["Gross Profit"].sum()
)


if total_profit_filtered > 0:

    pareto_profit["Profit Contribution %"] = (
        pareto_profit["Gross Profit"]
        / total_profit_filtered
    ) * 100

else:

    pareto_profit["Profit Contribution %"] = 0


pareto_profit["Cumulative Profit %"] = (
    pareto_profit["Profit Contribution %"]
    .cumsum()
)


# =========================================================
# REVENUE CONTRIBUTION CHART
# =========================================================

fig_revenue_pareto = px.bar(
    pareto,
    x="Product Name",
    y="Revenue Contribution %",
    title="Revenue Contribution by Product"
)


fig_revenue_pareto.update_layout(
    xaxis_title="Product",
    yaxis_title="Revenue Contribution (%)",
    xaxis_tickangle=-45
)


st.plotly_chart(
    fig_revenue_pareto,
    use_container_width=True
)


# =========================================================
# PROFIT CONTRIBUTION CHART
# =========================================================

fig_profit_pareto = px.bar(
    pareto_profit,
    x="Product Name",
    y="Profit Contribution %",
    title="Profit Contribution by Product"
)


fig_profit_pareto.update_layout(
    xaxis_title="Product",
    yaxis_title="Profit Contribution (%)",
    xaxis_tickangle=-45
)


st.plotly_chart(
    fig_profit_pareto,
    use_container_width=True
)


# =========================================================
# 80% CONCENTRATION
# =========================================================

def products_for_80_percent(
    contribution_series
):

    cumulative = (
        contribution_series.cumsum()
    )

    count = (
        cumulative < 80
    ).sum()

    count = min(
        count + 1,
        len(contribution_series)
    )

    return count


products_80_revenue = (
    products_for_80_percent(
        pareto["Revenue Contribution %"]
    )
)


products_80_profit = (
    products_for_80_percent(
        pareto_profit["Profit Contribution %"]
    )
)


total_products_filtered = len(
    product_summary_filtered
)


if total_products_filtered > 0:

    revenue_concentration = (
        products_80_revenue
        / total_products_filtered
    ) * 100

    profit_concentration = (
        products_80_profit
        / total_products_filtered
    ) * 100

else:

    revenue_concentration = 0
    profit_concentration = 0


# =========================================================
# CONCENTRATION KPIs
# =========================================================

col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Products for 80% Revenue",
    products_80_revenue
)


col2.metric(
    "% Products for 80% Revenue",
    f"{revenue_concentration:.1f}%"
)


col3.metric(
    "Products for 80% Profit",
    products_80_profit
)


col4.metric(
    "% Products for 80% Profit",
    f"{profit_concentration:.1f}%"
)


# =========================================================
# TOP PROFIT PRODUCTS
# =========================================================

st.subheader(
    "🏆 Top Profit-Contributing Products"
)


st.dataframe(
    pareto_profit[
        [
            "Product Name",
            "Division",
            "Gross Profit",
            "Profit Contribution %",
            "Cumulative Profit %"
        ]
    ].head(10),
    use_container_width=True,
    hide_index=True
)


# =========================================================
# MANAGEMENT RECOMMENDATIONS
# =========================================================

st.markdown("---")

st.header("💡 Management Recommendations")


recommendation_data = []


for _, row in cost_summary.iterrows():

    product = row["Product Name"]

    division = row["Division"]

    margin = row["Gross Margin %"]

    cost_pct = row["Cost %"]

    profit = row["Gross Profit"]

    sales = row["Sales"]


    if (
        margin < margin_median
        and cost_pct >= cost_median
    ):

        recommendation = (
            "Priority review: evaluate pricing, "
            "sourcing cost, and product profitability."
        )

        priority = "High"


    elif margin < margin_median:

        recommendation = (
            "Review pricing strategy and consider "
            "improving selling price or product mix."
        )

        priority = "Medium"


    elif cost_pct >= cost_median:

        recommendation = (
            "Review procurement and production costs "
            "to identify cost-saving opportunities."
        )

        priority = "Medium"


    else:

        recommendation = (
            "Maintain performance and monitor profitability."
        )

        priority = "Low"


    recommendation_data.append({

        "Product Name": product,

        "Division": division,

        "Sales": sales,

        "Gross Profit": profit,

        "Gross Margin %": margin,

        "Cost %": cost_pct,

        "Priority": priority,

        "Recommendation": recommendation

    })


recommendation_df = pd.DataFrame(
    recommendation_data
)


# =========================================================
# PRIORITY SUMMARY
# =========================================================

high_priority = (
    recommendation_df["Priority"]
    == "High"
).sum()


medium_priority = (
    recommendation_df["Priority"]
    == "Medium"
).sum()


low_priority = (
    recommendation_df["Priority"]
    == "Low"
).sum()


col1, col2, col3 = st.columns(3)


col1.metric(
    "🔴 High Priority",
    high_priority
)


col2.metric(
    "🟠 Medium Priority",
    medium_priority
)


col3.metric(
    "🟢 Low Priority",
    low_priority
)


# =========================================================
# RECOMMENDATION TABLE
# =========================================================

st.subheader(
    "📋 Product-Level Action Plan"
)


priority_order = {
    "High": 1,
    "Medium": 2,
    "Low": 3
}


recommendation_df["Priority Order"] = (
    recommendation_df["Priority"]
    .map(priority_order)
)


recommendation_display = (
    recommendation_df.sort_values(
        [
            "Priority Order",
            "Gross Margin %"
        ],
        ascending=[
            True,
            True
        ]
    )[
        [
            "Product Name",
            "Division",
            "Sales",
            "Gross Profit",
            "Gross Margin %",
            "Cost %",
            "Priority",
            "Recommendation"
        ]
    ].copy()
)


for column in [
    "Sales",
    "Gross Profit",
    "Gross Margin %",
    "Cost %"
]:

    recommendation_display[column] = (
        recommendation_display[column]
        .round(2)
    )


st.dataframe(
    recommendation_display,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# KEY BUSINESS INSIGHTS
# =========================================================

st.subheader(
    "🎯 Key Business Insights"
)


top_profit_product = (
    product_summary_filtered.loc[
        product_summary_filtered[
            "Gross Profit"
        ].idxmax(),
        "Product Name"
    ]
)


top_margin_product = (
    product_summary_filtered.loc[
        product_summary_filtered[
            "Gross Margin %"
        ].idxmax(),
        "Product Name"
    ]
)


lowest_margin_product = (
    product_summary_filtered.loc[
        product_summary_filtered[
            "Gross Margin %"
        ].idxmin(),
        "Product Name"
    ]
)


top_profit_division = (
    division_summary.loc[
        division_summary[
            "Gross Profit"
        ].idxmax(),
        "Division"
    ]
)


st.markdown(
    f"""
    **1. Top Profit Driver:** {top_profit_product} is the
    strongest product by gross profit under the selected
    filters.

    **2. Highest Margin Product:** {top_margin_product} has
    the highest gross margin percentage.

    **3. Lowest Margin Product:** {lowest_margin_product}
    requires closer profitability monitoring.

    **4. Leading Division:** {top_profit_division} generates
    the highest gross profit among the divisions.

    **5. Management Focus:** Products with high sales but
    relatively low margins should receive pricing and cost
    optimization attention.
    """
)


# =========================================================
# DOWNLOAD ANALYSIS FILES
# =========================================================

st.markdown("---")

st.header("📥 Download Analysis Results")


download_col1, download_col2, download_col3 = (
    st.columns(3)
)


# ---------------------------------------------------------
# PRODUCT ANALYSIS
# ---------------------------------------------------------

product_csv = (
    product_summary_filtered
    .to_csv(index=False)
    .encode("utf-8")
)


download_col1.download_button(
    label="📊 Download Product Analysis",
    data=product_csv,
    file_name="Product_Profitability_Analysis.csv",
    mime="text/csv"
)


# ---------------------------------------------------------
# DIVISION ANALYSIS
# ---------------------------------------------------------

division_csv = (
    division_summary
    .to_csv(index=False)
    .encode("utf-8")
)


download_col2.download_button(
    label="🏭 Download Division Analysis",
    data=division_csv,
    file_name="Division_Performance.csv",
    mime="text/csv"
)


# ---------------------------------------------------------
# RECOMMENDATIONS
# ---------------------------------------------------------

recommendation_download = (
    recommendation_df[
        [
            "Product Name",
            "Division",
            "Sales",
            "Gross Profit",
            "Gross Margin %",
            "Cost %",
            "Priority",
            "Recommendation"
        ]
    ]
)


recommendation_csv = (
    recommendation_download
    .to_csv(index=False)
    .encode("utf-8")
)


download_col3.download_button(
    label="💡 Download Recommendations",
    data=recommendation_csv,
    file_name="Product_Recommendations.csv",
    mime="text/csv"
)


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "Nassau Candy Distributor | Product Line Profitability "
    "& Margin Performance Analytics"
)

st.caption(
    "Developed for Data Analytics Project | Streamlit Dashboard"
)