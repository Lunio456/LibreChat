import logging
import traceback
import pandas as pd
from mcp.server.fastmcp import FastMCP
from visualize.dashboard import build_dashboard
from io import StringIO
from typing import Any

# === Logging Configuration ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("visualization.server")

# === Initialize FastMCP Server ===
mcp = FastMCP("visualization")



def _load_csv_into_df(data:str) -> Any:
    """ Load csv data presented as a string into a pandas dataframe"""
    input_data = StringIO()
    input_data.write(data)
    input_data.seek(0)
    return pd.read_csv(input_data)

# === MCP Tool: Dashboard Generator ===
@mcp.tool()
async def generate_dashboard(data: str) -> Any:
    """Create a visualization of data. 
    Args:
        data: The data that should be visualized. Has to be provided as
              a comma-separated csv file.
    """
    try:
        dataframe = _load_csv_into_df(data)
        dashboard_html, chart_htmls = build_dashboard(dataframe)
        success_message = "<p style='color:green;'>Dashboard generated successfully.</p>" 
        return dashboard_html, chart_htmls, success_message
    except Exception as e:
        logger.error("Dashboard generation failed: %s\n%s", e, traceback.format_exc())
        return f"<html><body><h1>Fehler</h1><p>{str(e)}</p></body></html>"

# === Entry Point ===
if __name__ == "__main__":
    logger.info("Starting Visualization MCP Server...")
    mcp.run(transport="stdio")
