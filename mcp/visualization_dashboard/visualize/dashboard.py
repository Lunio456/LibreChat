import pandas as pd
from io import StringIO

# Import directly from the combined dashboard_chart_generator.py file
from .dashboard_chart_generator import (
    generate_performance_chart,
    generate_top_positions_chart,
    generate_drawdown_chart,
    generate_allocation_chart
)

def _load_csv_into_df(data: str) -> pd.DataFrame:
    input_data = StringIO(data)
    return pd.read_csv(input_data)

def build_dashboard(data: str) -> str:
    df = _load_csv_into_df(data)

    # Generate each chart HTML
    performance_chart = generate_performance_chart(df)
    top_positions_chart = generate_top_positions_chart(df)
    drawdown_chart = generate_drawdown_chart(df)
    allocation_chart = generate_allocation_chart(df)

    # HTML layout with Plotly CDN + grid layout
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Showcase Multi Agent Portfolio Analytics</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f4f9;
                color: #333;
            }}
            header {{
                background-color: #003C4B;
                color: white;
                padding: 20px;
                text-align: center;
            }}
            .container {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                padding: 20px;
            }}
            .card {{
                background: white;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                border-radius: 10px;
                padding: 20px;
                text-align: center;
            }}
            .plotly-graph-div {{
                height: 100%;
            }}
            footer {{
                text-align: center;
                padding: 10px;
                background-color: #003C4B;
                color: white;
                position: fixed;
                bottom: 0;
                width: 100%;
            }}
        </style>
    </head>
    <body>
        <header>
            <h1>Showcase Multi Agent Portfolio Analytics</h1>
        </header>
        <main>
            <div class="container">
                <div class="card">
                    {performance_chart}
                </div>
                <div class="card">
                    {top_positions_chart}
                </div>
                <div class="card">
                    {drawdown_chart}
                </div>
                <div class="card">
                    {allocation_chart}
                </div>
            </div>
        </main>
        <footer>
            <p>&copy; 2025 Portfolio Dashboard</p>
        </footer>
    </body>
    </html>
    """

    return html_template
