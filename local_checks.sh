echo "--- docker-compose exec web python -m pytest ."
docker-compose exec web python -m pytest .
echo "--- docker-compose exec web python -m pytest --cov='.'"
docker-compose exec web python -m pytest --cov="."
echo "--- docker-compose exec web python -m flake8 ."
docker-compose exec web python -m flake8 .
echo "--- docker-compose exec web python -m black . --check"
docker-compose exec web python -m black . --check
echo "--- docker-compose exec web python -m isort . --check-only"
docker-compose exec web python -m isort . --check-only
echo "--- docker-compose exec web bandit -r ."
docker-compose exec web bandit -r .
