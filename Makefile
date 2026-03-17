.PHONY: build install collectstatic migrate render-start

build: install collectstatic migrate

install:
	uv sync --no-dev

collectstatic:
	python manage.py collectstatic --noinput

migrate:
	python manage.py migrate --noinput

render-start:
	gunicorn task_manager.wsgi
