version = 1.0.2

install:
	python setup.py install

.PHONY: install-requirements
install-requirements:
	pip install -r requirements.txt

build-wheel: clean
	sed -i 's/{version}/$(version)/g' setup.py
	python setup.py sdist bdist_wheel

username = __token__
password =
release-pypi: install-requirements clean build-wheel
	python -m twine upload -u $(username) -p $(password) dist/*

clean:
	rm -rf build dist gigrator.egg-info

install-wheel:
	pip install --force-reinstall dist/gigrator-$(version)-py3-none-any.whl
