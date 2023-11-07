test:
	@coverage run -m pytest
	@coverage report
	@coverage xml

lint:
	@flake8 --max-complexity 10 favaghost

rebuild-env:
	git clean -dfx
	python3 -m venv .venv
	. .venv/bin/activate && pip install -e '.[test]' && pip install -e .
