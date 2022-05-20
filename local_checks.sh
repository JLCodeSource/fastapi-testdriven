docker-compose exec web python -m pytest .
docker-compose exec web python -m pytest --cov="."
docker-compose exec web python -m flake8 .
docker-compose exec web python -m black . --check
docker-compose exec web python -m isort . --check-only