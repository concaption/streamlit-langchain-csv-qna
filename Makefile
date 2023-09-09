install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt
lint:
	pylint app.py
format:
	black *.py
refactor: lint format
test:
	python -m pytest -vv --cov=app test_app.py
run:
	streamlit run app.py