echo -e "1. Creating new virtual environment..."

python3 -m venv holy_grail

echo -e "2. Installing Requirements..."

source holy_grail/bin/activate
pip3 install -r requirements.txt

echo -e "Install is complete."

echo -e "Starting application."

python3 app.py

