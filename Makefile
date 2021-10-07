.PHONY: install-requirements
install-requirements:
	pip install -r requirements.txt

build-wheel: clean
	python setup.py sdist bdist_wheel

username = __token__
password = 
release-pypi: install-requirements clean build-wheel
	python -m twine upload -u $(username) -p $(password) dist/*

clean:
	rm -rf build dist gigrator.egg-info
