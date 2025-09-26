import pandas as pd
import plotly.graph_objects as go
from typing import Dict


def generate_performance_chart(df: pd.DataFrame) -> str:
    df.columns = df.columns.str.strip()

    required_cols = ['Date', 'Performance (%)', 'Weight (%)', 'Sector']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in DataFrame: {missing}")

    # Remove 'Ticker' from required_cols as it is not used in this function
    # and will prevent errors if the 'Ticker' column is not in the data.

    def weighted_perf(x):
        weights_sum = x['Weight (%)'].sum()
        if weights_sum == 0:
            return float('nan')
        return (x['Performance (%)'] * x['Weight (%)']).sum() / weights_sum

    # Portfolio: weighted average performance per date
    portfolio_grouped = df.groupby('Date').apply(weighted_perf).reset_index(name='Weighted_Performance').sort_values('Date')

    # Benchmark: mean performance per date
    bench_df = df[df['Sector'] == 'Benchmark']
    if bench_df.empty:
        raise ValueError("No benchmark data found for 'Sector' == 'Benchmark'")

    bench_grouped = bench_df.groupby('Date')['Performance (%)'].mean().reset_index().sort_values('Date')
    bench_grouped.rename(columns={'Performance (%)': 'Performance_Benchmark'}, inplace=True)

    merged = pd.merge(portfolio_grouped, bench_grouped, on='Date', how='outer').sort_values('Date')
    
    # Calculate difference for IBCS highlighting
    merged['Difference'] = merged['Weighted_Performance'] - merged['Performance_Benchmark']
    
    # Plotting based on IBCS principles
    fig = go.Figure()

    # Define IBCS colors
    ibc_portfolio_color = '#136b93'  # Blue for main element
    ibc_benchmark_color = '#f07d00'  # Gray for comparison
    
    # Add fill area to show difference (gain/loss)
    fig.add_trace(go.Scatter(
        x=merged['Date'],
        y=merged['Difference'],
        name='Gain/Loss',
        mode='lines',
        line=dict(width=0),
        stackgroup='one',
        marker=dict(color='#d9dde4'),
        hoverinfo='skip'
    ))

    # Plot Portfolio Performance
    fig.add_trace(go.Scatter(
        x=merged['Date'],
        y=merged['Weighted_Performance'],
        mode='lines',
        name='Portfolio',
        line=dict(color=ibc_portfolio_color, width=2)
    ))

    # Plot Benchmark Performance
    fig.add_trace(go.Scatter(
        x=merged['Date'],
        y=merged['Performance_Benchmark'],
        mode='lines',
        name='Benchmark',
        line=dict(color=ibc_benchmark_color, dash='dash', width=2)
    ))


    fig.update_layout(
        title={},
        margin=dict(t=80,b=50,l=100,r=70),
        # xaxis_title="Date",
        yaxis_title="Performance (%)",
        xaxis=dict(
            tickformat='%Y',
            rangeslider=dict(visible=True),
            rangeselector=dict(
                buttons=[
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(count=3, label="3Y", step="year", stepmode="backward"),
                    dict(count=5, label="5Y", step="year", stepmode="backward"),
                    dict(label="All", step="all")
                ]
            ),
            type="date"
        ),
        yaxis=dict(
            gridcolor='#e6e6e6'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.1,
            xanchor="center",
            x=0.5,
            traceorder="normal"
        ),
        template="plotly_white",
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    return fig.to_html(full_html=False, include_plotlyjs="cdn")


def generate_top_positions_chart(df: pd.DataFrame) -> str:
    df.columns = df.columns.str.strip()

    df = df[df["Sector"] != "Benchmark"]

    required_cols = ["Market Value", "Ticker", "Date"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in DataFrame: {missing}")

    latest_date = df["Date"].max()
    df_latest = df[df["Date"] == latest_date]

    if df_latest.empty:
        raise ValueError("No data found for the latest date.")

    unique_positions = df_latest["Ticker"].nunique()
    top_n = min(unique_positions, 10)

    top_positions = df_latest.groupby("Ticker")["Market Value"].sum().nlargest(top_n)

    # Use a solid color (e.g., black) for bars and add data labels.
    fig = go.Figure(go.Bar(
        x=top_positions.values,
        y=top_positions.index,
        orientation='h',
        marker_color='#136b93', 
        text=top_positions.values.round(2), # Add labels to the bars
        textposition='outside'
    ))

    fig.update_layout(
        title={},
        template="plotly_white",
        yaxis=dict(autorange="reversed", showgrid=False),
        xaxis=dict(gridcolor='#e6e6e6', showgrid=True),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    return fig.to_html(full_html=False, include_plotlyjs="cdn")


def generate_drawdown_chart(df: pd.DataFrame) -> str:
    df.columns = df.columns.str.strip()
    df = df[df["Sector"] != "Benchmark"]

    required_cols = ["Drawdown (%)", "Date"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Ensure "Date" is datetime type
    df["Date"] = pd.to_datetime(df["Date"])

    # Extract year from date
    df["Year"] = df["Date"].dt.year

    # Group by year and calculate mean drawdown
    grouped = df.groupby("Year")["Drawdown (%)"].mean().reset_index().sort_values("Year")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grouped["Year"].astype(str),  # convert years to string for better x-axis labels
        y=grouped["Drawdown (%)"],
        name="Drawdown (%)",
        marker_color='#FF0000'  # Bright red for negative values
    ))

    fig.update_layout(
        bargap=0.2,
        bargroupgap=0.1,
        margin=dict(t=60,b=60,l=100,r=60),
        yaxis_title="Drawdown (%)",
        template="plotly_white",
        xaxis=dict(
            rangeslider=dict(visible=False),
            tickmode='linear'  # ensures all years show on x-axis
        ),
        yaxis=dict(
            gridcolor='#e6e6e6'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    return fig.to_html(full_html=False, include_plotlyjs="cdn")





def generate_allocation_chart(df: pd.DataFrame) -> str:
    df.columns = df.columns.str.strip()

    df = df[df["Sector"] != "Benchmark"]

    required_columns = {"Allocation (%)", "Ticker", "Asset Class", "Date"}
    if not required_columns.issubset(df.columns):
        raise ValueError("Missing required columns: 'Allocation (%)', 'Ticker', 'Asset Class', or 'Date'")

    if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
        df["Date"] = pd.to_datetime(df["Date"])

    latest_date = df["Date"].max()
    df_latest = df[df["Date"] == latest_date]

    if df_latest.empty:
        raise ValueError("No data found for the latest date.")

    grouped = df_latest.groupby(["Asset Class", "Ticker"])["Allocation (%)"].sum().reset_index()
    category_sums = grouped.groupby("Asset Class")["Allocation (%)"].sum().reset_index()
    total_sum = category_sums["Allocation (%)"].sum()

    positions = grouped.copy()
    positions["id"] = "P_" + positions["Ticker"]
    positions["parent"] = "C_" + positions["Asset Class"]

    categories = category_sums.copy()
    categories["id"] = "C_" + categories["Asset Class"]
    categories["parent"] = "Total"

    labels = positions["Ticker"].tolist() + categories["Asset Class"].tolist() + ["Total"]
    ids = positions["id"].tolist() + categories["id"].tolist() + ["Total"]
    parents = positions["parent"].tolist() + categories["parent"].tolist() + [""]
    values = positions["Allocation (%)"].tolist() + categories["Allocation (%)"].tolist() + [total_sum]
    custom_colors = ['#c0d9e6', '#9ac1d6', '#74a9c6', '#4e91b6', '#136b93', '#105377', '#0c3c59', '#072533']

    fig = go.Figure(go.Sunburst(
        labels=labels,
        ids=ids,
        parents=parents,
        values=values,
        branchvalues="total",
        maxdepth=2,
        insidetextorientation='radial',
        hoverinfo='label+value', # Simplified hover text
        textinfo="label+percent parent", # Show percentage of the parent
        leaf=dict(opacity=1.0),
        marker=dict(colorscale=custom_colors) # Use a consistent color scale
    ))

    fig.update_layout(
        title={},
        margin=dict(t=30, b=30),
        autosize=True,
        #width=800,
        # height=600,
        template="plotly_white",
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    #return fig.to_html(full_html=False, include_plotlyjs="cdn")
    return {
        "filename": "allocation.html",
        "title": "Asset Allocation",
        "html": fig.to_html(full_html=False, include_plotlyjs="cdn")
    }




def generate_all_charts(df: pd.DataFrame) -> Dict[str, str]:
    """
    Generates all four chart HTML strings in memory.
    Returns a dictionary mapping chart names to HTML content.
    """
    return {
        "performance.html": generate_performance_chart(df),
        "top_positions.html": generate_top_positions_chart(df),
        "drawdown.html": generate_drawdown_chart(df),
        "allocation.html": generate_allocation_chart(df),
    }