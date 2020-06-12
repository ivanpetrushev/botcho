init-venv:
	sudo apt-get install python3-venv && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt
start:
	python main.py