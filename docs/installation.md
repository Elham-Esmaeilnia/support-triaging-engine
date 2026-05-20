## Run Locally
```bash
# 1) Copy the example environment file and configure your values
cp .env.example .env

# 2) Create and activate a virtual environment
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows (Command Prompt)
.venv\Scripts\activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# 3) Install dependencies
pip install -r requirements.txt

# 4) Start the application
# If your network requires it, configure your proxy settings before running
bash scripts/run_local.sh
```
Interactive API documentation is available at: http://localhost:8000/docs
