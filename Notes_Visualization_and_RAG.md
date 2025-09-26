# Brief Notes on the MCPs ‘visualization_dashboard’ and ‘rag_agent’

## visualization_dashboard

For the Visualization Dashboard, I created a Python script named **historic_dummy_data.py**, located in the Uploads folder, to generate dummy data. Running the script from the terminal using:
```bash
python3 historic_dummy_data.py
```
will generate a CSV file named **historic_portfolio.csv**.

By connecting to the MCP servers **filesystem** and **visualization_dashboard** via LibreChat, you can use the following prompt to create the dashboard and its 4 plots:

**`read the csv file historic_portfolio.csv using filesystem <br>
from historic_portfolio.csv create a dashboard using the visualization_dashboard mcp server <br>
save all 4 plots and the dashboard as .html-files under uploads/dashboard using filesystem`**

This will generate the dashboard and four plots, which are saved again in the Uploads folder.

 💡 **Note:**  
With this solution, the content from the CSV file is sent to the MCP server in JSON format. However, this process can occasionally vary — the data may not always be transmitted in the correct format. For example, it might be truncated or structured as nested JSON. Such issues can affect the output and may lead to errors during execution.

## rag_agent

Unfortunately, we were not able to establish a connection between the RAG Agent and LibreChat. However, the RAG Agent can be run directly from the terminal.

To do so, place one or more PDFs in the Upload folder and run:

```bash
python3 main.py
```
This will execute the core RAG solution (chunking and embedding). Parameters such as chunk size and chunk overlap can be adjusted in the **rag_agent.py** file.

After that, you can analyze the output using an LLM prompt input by running:

```bash
python3 ask.py
```