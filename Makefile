install:
	python3 -m venv .venv
	. .venv/bin/activate
	pip3 install -r requirements.txt

up:
	python3 bot.py