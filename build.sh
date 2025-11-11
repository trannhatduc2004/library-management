#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Initialize database
python -c "from app import app, init_database; init_database()"