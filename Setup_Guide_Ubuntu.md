LibreChat Setup Guide (Ubuntu / WSL)
1. Install WSL (Windows Subsystem for Linux)

Open PowerShell or Command Prompt as administrator

Run:

wsl --install


Restart your computer

After restart, Ubuntu will launch automatically

Create your username and password

2. Update Ubuntu and Install Essentials

Open Ubuntu terminal and run:

sudo apt update
sudo apt install -y git python3 python3-pip python3.12-venv

3. Install Docker

Follow the official Docker installation guide for Ubuntu:
👉 https://docs.docker.com/desktop/setup/install/linux/ubuntu/

Make sure Docker is installed and running correctly before proceeding.

4. Setup Workspace and Clone LibreChat Repo

Open VS Code, launch the integrated terminal (in WSL)

Navigate to home directory and create workspace:

cd ~
mkdir -p workspace/LibreChat
cd workspace/LibreChat


Clone the LibreChat repository (replace <SSH_KEY> with your SSH URL):

git clone <SSH_KEY>

5. Prepare Configuration Files

Required config files such as:

.env

docker-compose.override.yml

librechat.yaml

already exist in other repositories (e.g., the VM solution).
Copy them into your LibreChat directory.

Ensure your docker-compose.yml includes this MCP volume:

- ./mcp:/app/mcp

6. Install Additional Tools and Packages

Install uv runtime:

curl -LsSf https://astral.sh/uv/install.sh | sh


Install MCP Python package:

pip install mcp --break-system-packages


Install other MCP-specific packages as needed:

pip install <package_name> --break-system-packages

7. Verify and Run MCP Services

To check for missing dependencies for a specific MCP (e.g., visualization_dashboard), run:

uv run ./mcp/visualization_dashboard/server.py


Install any missing packages based on error messages using pip.

8. Start LibreChat and Access the UI

From the root of your LibreChat project, start the application:

docker compose up


Or to run it in the background:

docker compose up -d


Once running, open your browser and go to:
👉 http://localhost:3080/

On first launch, create a new account to use the UI.