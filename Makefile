setup:
    python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

run:
    python uflix_gui.py

freeze:
    pip freeze > requirements.txt
