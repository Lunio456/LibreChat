from typing import Any, Dict
import pandas as pd
from io import StringIO
from visualize.chart_types import ChartType
from visualize.chart_generator import create_quick_chart
from mcp.server.fastmcp import FastMCP
import logging
import traceback

logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("visualization")

def _load_csv_into_df(data:str) -> Any:
    """ Load csv data presented as a string into a pandas dataframe"""
    input_data = StringIO()
    input_data.write(data)
    input_data.seek(0)
    return pd.read_csv(input_data)

@mcp.tool()
async def create_visualization(data: str, chart_type: str, mappings: Dict[str, str]) -> Any:
    """Create a visualization of data. There are multiple possible chart types.

    Args:
        data: The data that should be visualized. Has to be provided as
              a comma-separated csv file
        chart_type: The type of chart that should be generated.
                Has to be one of bar, line, scatter, pie, histogram, box, heatmap, area
        mappings: mappings used for the visualization. A dictionary, with 
                keys such as x_axis, y_axis, color, size, values, category.
                Relevant settings depend on chart type.
    """
    dataframe = _load_csv_into_df(data)
    try:
        chart = create_quick_chart(chart_type, dataframe, **mappings)
        return chart
    except Exception as e:
        return str(e) + '\n' + traceback.format_exc()


from visualize.dashboard import build_dashboard

@mcp.tool()
async def generate_dashboard(data: str) -> str:
    """
    Generates an HTML portfolio dashboard from CSV data.

    Args:
        data: A comma-separated CSV file (as a string).

    Returns:
        An HTML string containing the portfolio dashboard.
    """
    try:
        html = build_dashboard(data)
        return html
    except Exception as e:
        logger.error("Dashboard generation failed: %s", str(e))
        return "Error generating dashboard: " + str(e)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
