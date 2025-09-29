version =

install:
	pip install -e .

publish:
	@if [ -z "$(version)" ]; then \
		echo "Please set version, e.g., make publish version=0.1.0"; \
		exit 1; \
	fi

	rm -rf dist
	uv version $(version)
	uv build
	uv publish
