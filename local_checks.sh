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
echo "--- docker-compose exec safety check"
docker-compose exec safety check
echo "--- docker-compose exec safety check -r requirements.txt"
docker-compose exec safety check -r requirements.txt
echo "--- docker-compose exec safety check -r requirements-dev.txt"
docker-compose exec safety check -r requirements-dev.txt
echo "--- trivy security check web"
trivy image fastapi-testdriven_web
echo "--- trivy security check web_db"
trivy image fastapi-testdriven_web-db