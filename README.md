# AI381 Lab 2 - Container and CI

![CI](https://github.com/Alabaas-Ot/ai381-lab2/actions/workflows/ci.yml/badge.svg?branch=main)

A containerised FastAPI churn prediction service with automated testing,
Docker health checks, and GitHub Actions CI/CD.

## Run the service

Start the application with one command:

    docker compose up --build

The API is available at:

- Health: http://localhost:8000/health
- Documentation: http://localhost:8000/docs
- Prediction: POST http://localhost:8000/predict

## Example prediction

    curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"tenure_months":5,"monthly_charges":89.9,"contract":"month-to-month","internet_service":"fiber","support_calls":3}'

## Stop the service

    docker compose down

## Run tests

    python -m pip install -r requirements-dev.txt
    ruff check src tests
    pytest -v

## Project structure

- src/app/main.py: FastAPI application
- src/train/train.py: Model training
- tests/test_api.py: Five API tests
- Dockerfile: Multi-stage container build
- compose.yaml: One-command service startup
- model.joblib: Trained model

## CI/CD

GitHub Actions runs lint and tests on every pull request to main.

On pushes to main, it builds the Docker image, scans it using Trivy,
and pushes it to GitHub Container Registry (GHCR) with the commit SHA tag.

## Pull Request workflow

Changes are developed on separate branches and merged into main
through pull requests after automated checks pass.
