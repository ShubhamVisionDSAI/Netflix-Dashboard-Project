import os

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from matplotlib.ticker import FuncFormatter

st.set_page_config(
    page_title="Netflix Streaming Insights Dashboard",
    page_icon="🎬",
    layout="wide",
)

st.markdown(
    """
    <style>
        .stApp {
            background: #111111;
            color: #ffffff;
        }
        [data-testid="stHeader"] {
            background: #111111;
        }
        .block-container {
            max-width: 1440px;
            padding-top: 3rem;
            padding-bottom: 3rem;
        }
        h1, h2, h3, p, label {
            color: #ffffff !important;
        }
        h1 {
            font-size: 2rem !important;
            line-height: 1.25 !important;
            padding-top: 0.2rem;
            overflow: visible;
        }
        .stSidebar {
            background: #7A0006;
        }
        [data-testid="stSidebar"] > div:first-child {
            background: #7A0006;
        }
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label {
            color: #ffffff !important;
        }
        [data-testid="stSidebar"] [data-baseweb="select"] > div:first-child {
            background-color: #FFFFFF !important;
            border: 1px solid #FFFFFF !important;
        }
        [data-testid="stSidebar"] [data-baseweb="select"] > div:first-child div,
        [data-testid="stSidebar"] [data-baseweb="select"] > div:first-child input {
            color: #111111 !important;
            caret-color: #111111;
        }
        [data-testid="stSidebar"] [data-baseweb="select"] > div:first-child svg {
            color: #111111 !important;
            fill: #111111 !important;
        }
        .dashboard-kicker {
            color: #E50914;
            font-size: 0.78rem;
            font-weight: 700;
            line-height: 1.4;
            text-transform: uppercase;
            margin-bottom: 0.2rem;
        }
        .dashboard-subtitle {
            color: #b3b3b3;
            margin-top: -0.4rem;
            margin-bottom: 1.4rem;
        }
        .chart-title {
            box-sizing: border-box;
            width: 100%;
            height: 4rem;
            margin: 0.2rem 0 0.65rem;
            padding: 0.35rem 0.75rem;
            border-left: 4px solid #E50914;
            background: #1b1b1b;
            color: #ffffff;
            display: flex;
            align-items: center;
            font-size: 1.1rem;
            font-weight: 800;
            line-height: 1.3;
        }
        div[data-testid="stMetric"] {
            min-height: 98px;
            background: #1b1b1b;
            border-left: 3px solid #E50914;
            padding: 0.9rem 1rem;
        }
        div[data-testid="stMetricLabel"] p {
            color: #b3b3b3 !important;
        }
        div[data-testid="stMetricValue"] {
            color: #ffffff;
        }
        hr {
            border-color: #303030;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

dataset_name = "Netflix_100_Customers_Dataset.csv"
dataset_paths = (
    dataset_name,
    os.path.join("Netflix project", dataset_name),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), dataset_name),
)
dataset_path = next((path for path in dataset_paths if os.path.exists(path)), None)
if dataset_path is None:
    raise FileNotFoundError(f"Could not find {dataset_name}")

netflix = pd.read_csv(dataset_path)
netflix["Watch_Date"] = pd.to_datetime(netflix["Watch_Date"])

regions = sorted(netflix["Region"].dropna().unique().tolist())
categories = sorted(netflix["Category"].dropna().unique().tolist())
subscription_plans = sorted(netflix["Subscription_Plan"].dropna().unique().tolist())

selected_region = st.sidebar.selectbox(
    "Select Region",
    ["All Regions", *regions],
)
selected_category = st.sidebar.selectbox(
    "Select Category",
    ["All Categories", *categories],
)
selected_plan = st.sidebar.selectbox(
    "Select Subscription Plan",
    ["All Plans", *subscription_plans],
)

filtered_netflix = netflix.copy()
if selected_region != "All Regions":
    filtered_netflix = filtered_netflix.loc[filtered_netflix["Region"] == selected_region]
if selected_category != "All Categories":
    filtered_netflix = filtered_netflix.loc[
        filtered_netflix["Category"] == selected_category
    ]
if selected_plan != "All Plans":
    filtered_netflix = filtered_netflix.loc[
        filtered_netflix["Subscription_Plan"] == selected_plan
    ]

st.markdown('<div class="dashboard-kicker">Streaming insights</div>', unsafe_allow_html=True)
st.title("🎬 Netflix Streaming Insights Dashboard")
st.markdown(
    '<div class="dashboard-subtitle">Subscription, viewing, and revenue insights at a glance.</div>',
    unsafe_allow_html=True,
)

metric_columns = st.columns(3)
metric_columns[0].metric(
    "Customers",
    f"{filtered_netflix['Customer_ID'].nunique():,}",
)
metric_columns[1].metric(
    "Total Revenue",
    f"₹{filtered_netflix['Monthly_Revenue'].sum():,.0f}",
)
metric_columns[2].metric(
    "Average Rating",
    f"{filtered_netflix['Rating'].mean():.1f} / 5"
    if not filtered_netflix.empty
    else "N/A",
)
st.divider()

plt.rcParams.update(
    {
        "figure.facecolor": "#111111",
        "axes.facecolor": "#111111",
        "axes.edgecolor": "#666666",
        "axes.labelcolor": "#ffffff",
        "xtick.color": "#ffffff",
        "ytick.color": "#ffffff",
        "text.color": "#ffffff",
        "font.size": 10,
    }
)


def show_chart(
    column,
    series,
    *,
    kind,
    heading,
    xlabel=None,
    ylabel=None,
    currency_axis=False,
    figsize=(7.2, 4.4),
    **plot_options,
):
    title_markup = f'<div class="chart-title">{heading}</div>'
    if column is None:
        st.markdown(title_markup, unsafe_allow_html=True)
    else:
        column.markdown(title_markup, unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)
    if series.empty or series.dropna().empty or (kind == "pie" and series.sum() <= 0):
        ax.text(
            0.5,
            0.5,
            "No data for selected filters",
            color="#b3b3b3",
            ha="center",
            va="center",
            transform=ax.transAxes,
        )
        ax.set_xticks([])
        ax.set_yticks([])
    elif kind == "pie":
        series.plot(kind=kind, ax=ax, ylabel="", **plot_options)
        ax.set_ylabel("")
        for label in ax.texts:
            label.set_color("#ffffff")
    else:
        series.plot(
            kind=kind,
            ax=ax,
            xlabel=xlabel,
            ylabel=ylabel,
            **plot_options,
        )
        ax.tick_params(colors="#ffffff")
        for spine in ax.spines.values():
            spine.set_color("#555555")
        ax.grid(axis="y", color="#333333", linestyle="--", linewidth=0.6, alpha=0.7)
        ax.set_axisbelow(True)
        if currency_axis:
            ax.yaxis.set_major_formatter(
                FuncFormatter(lambda value, position: f"₹{value:,.0f}")
            )

    ax.xaxis.label.set_color("#ffffff")
    ax.yaxis.label.set_color("#ffffff")
    if column is None:
        st.pyplot(fig, width="stretch")
    else:
        column.pyplot(fig, width="stretch")
    plt.close(fig)


row_left, row_right = st.columns(2, gap="large")
show_chart(
    row_left,
    filtered_netflix.groupby("Region")["Monthly_Revenue"].sum(),
    kind="bar",
    heading="Region Wise Revenue",
    ylabel="Monthly Revenue (₹)",
    currency_axis=True,
    rot=0,
    edgecolor="black",
)
show_chart(
    row_right,
    filtered_netflix.groupby("Subscription_Plan")["Rating"].sum(),
    kind="pie",
    heading="Subscription Plan Wise Rating",
    autopct="%1.1f%%",
    pctdistance=0.72,
    textprops={"color": "white", "fontsize": 10},
)

row_left, row_right = st.columns(2, gap="large")
show_chart(
    row_left,
    filtered_netflix["Rating"].value_counts().sort_index(),
    kind="bar",
    heading="Distribution of Ratings",
    xlabel="Rating",
    ylabel="Count",
    rot=0,
    color="green",
    edgecolor="black",
)
show_chart(
    row_right,
    filtered_netflix.groupby("Category")["Monthly_Revenue"].sum(),
    kind="pie",
    heading="Category Wise Revenue",
    autopct="%1.1f%%",
    pctdistance=0.72,
    textprops={"color": "white", "fontsize": 10},
)

row_left, row_right = st.columns(2, gap="large")
show_chart(
    row_left,
    filtered_netflix.groupby("Subscription_Plan")["Monthly_Revenue"].sum(),
    kind="bar",
    heading="Revenue by Subscription Plan",
    xlabel="Subscription Plan",
    ylabel="Total Revenue (₹)",
    currency_axis=True,
    color="purple",
    edgecolor="black",
    rot=0,
)
device_counts = filtered_netflix.groupby("Device")["Customer_ID"].count().reindex(
    ["Laptop", "Mobile", "TV", "Tablet"], fill_value=0
)
show_chart(
    row_right,
    device_counts[device_counts > 0],
    kind="pie",
    heading="Most Used Devices for Netflix",
    autopct="%1.1f%%",
    pctdistance=0.72,
    textprops={"color": "white", "fontsize": 10},
)

show_chart(
    None,
    filtered_netflix.groupby("Watch_Date")["Monthly_Revenue"].sum().sort_index(),
    kind="line",
    heading="Revenue Trend Over Time",
    xlabel="Watch Date",
    ylabel="Total Revenue (₹)",
    currency_axis=True,
    figsize=(14.4, 5.4),
    marker="o",
    color="green",
)