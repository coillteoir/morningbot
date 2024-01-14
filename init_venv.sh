set -e

python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt

echo 'execute command: "source venv/bin/activate" to use venv'
