import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json
from enum import Enum
from typing import Optional, Dict


class ChartType(Enum):
    LINE = "line"
    BAR = "bar"
    AREA = "area"


class ChartGenerator:
    def generate_chart(
        self,
        chart_type: ChartType,
        df: pd.DataFrame,
        mappings: Dict[str, str],
        title: str = "",
    ) -> str:
        fig = None

        common_args = dict(
            title=title,
            labels={
                mappings.get("x_axis", ""): mappings.get("x_axis", ""),
                mappings.get("y_axis", ""): mappings.get("y_axis", ""),
            },
        )

        if chart_type == ChartType.LINE:
            fig = px.line(
                df,
                x=mappings["x_axis"],
                y=mappings["y_axis"],
                color=mappings.get("color"),
                line_shape="spline",
                markers=True,
                **common_args
            )
            fig.update_traces(fill="tonexty", mode="lines+markers")

        elif chart_type == ChartType.BAR:
            fig = px.bar(
                df,
                x=mappings["x_axis"],
                y=mappings["y_axis"],
                color=mappings.get("color"),
                barmode="stack",
                **common_args
            )

        elif chart_type == ChartType.AREA:
            fig = px.area(
                df,
                x=mappings["x_axis"],
                y=mappings["y_axis"],
                color=mappings.get("color"),
                line_shape="spline",
                groupnorm="percent",
                **common_args
            )

        else:
            return "<div>Ungültiger Diagrammtyp.</div>"

        fig.update_layout(
            margin=dict(l=30, r=30, t=50, b=30),
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        )

        graph_json = json.dumps(fig, cls=PlotlyJSONEncoder)
        return f"""
        <div class="plotly-chart">
            <div id="{title.replace(' ', '_')}"></div>
            <script>
                Plotly.newPlot("{title.replace(' ', '_')}", {graph_json}, {{responsive: true}});
            </script>
        </div>
        """


# ==========================
# Individual Chart Functions
# ==========================

def generate_performance_chart(df: Optional[pd.DataFrame]) -> str:
    if df is None or not {'Performance', 'Year', 'Emittententicker'}.issubset(df.columns):
        return "<div>Performance-Daten fehlen oder Spaltennamen sind inkorrekt.</div>"

    perf_df = (
        df.groupby(['Year', 'Emittententicker'])['Performance']
        .mean().reset_index()
        .rename(columns={'Emittententicker': 'Series', 'Performance': 'Value'})
    )

    return ChartGenerator().generate_chart(
        ChartType.LINE,
        perf_df,
        {"x_axis": "Year", "y_axis": "Value", "color": "Series"},
        title="Performance Chart"
    )


def generate_top_positions_chart(df: Optional[pd.DataFrame]) -> str:
    if df is None or not {'Gewichtung (%)', 'Year', 'Emittententicker'}.issubset(df.columns):
        return "<div>Gewichtungsdaten fehlen oder Spaltennamen sind inkorrekt.</div>"

    latest_year = df['Year'].max()
    latest_df = df[df['Year'] == latest_year].copy()

    top_weights = (
        latest_df[['Emittententicker', 'Gewichtung (%)']]
        .groupby('Emittententicker')
        .mean()
        .reset_index()
        .sort_values(by='Gewichtung (%)', ascending=False)
        .head(20)
        .rename(columns={'Emittententicker': 'Position', 'Gewichtung (%)': 'Share'})
    )

    return ChartGenerator().generate_chart(
        ChartType.BAR,
        top_weights,
        {"x_axis": "Position", "y_axis": "Share"},
        title="Top 20 Positionen im Portfolio"
    )


def generate_drawdown_chart(df: Optional[pd.DataFrame]) -> str:
    if df is None or not {'Drawdown (%)', 'Year'}.issubset(df.columns):
        return "<div>Drawdown-Daten fehlen oder Spaltennamen sind inkorrekt.</div>"

    drawdown_df = (
        df.groupby('Year')['Drawdown (%)']
        .mean()
        .reset_index()
        .rename(columns={'Drawdown (%)': 'Drawdown'})
    )

    return ChartGenerator().generate_chart(
        ChartType.LINE,
        drawdown_df,
        {"x_axis": "Year", "y_axis": "Drawdown"},
        title="Durchschnittlicher Drawdown pro Jahr"
    )


def generate_allocation_chart(df: Optional[pd.DataFrame]) -> str:
    if df is None or not {'Allocation (%)', 'Year', 'Emittententicker'}.issubset(df.columns):
        return "<div>Allokationsdaten fehlen oder Spaltennamen sind inkorrekt.</div>"

    alloc_df = (
        df.groupby(['Year', 'Emittententicker'])['Allocation (%)']
        .mean()
        .reset_index()
        .rename(columns={'Emittententicker': 'Asset', 'Allocation (%)': 'Allocation'})
    )

    return ChartGenerator().generate_chart(
        ChartType.AREA,
        alloc_df,
        {"x_axis": "Year", "y_axis": "Allocation", "color": "Asset"},
        title="Portfolio Allokation über die Zeit"
    )
