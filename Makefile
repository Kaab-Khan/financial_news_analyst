#include .env
############################################
# GLOBALS
############################################
PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PROJECT_NAME = financial_analyst
BUCKET_NAME = $(PROJECT_NAME)-$(USER)
PYTHON_INTERPRETER = python3

ifeq (,$(shell which conda))
HAS_CONDA=False
else
HAS_CONDA=True
endif
############################################
# COMMANDS
############################################
## Install Python Dependencies
requirements: test_environment
	$(PYTHON_INTERPRETER) -m pip install -U pip setuptools wheel
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt
	$(PYTHON_INTERPRETER) -m pip install -e .make

# Install development dependencies from requirements-dev.txt
requirements-dev:
	$(PYTHON_INTERPRETER) -m pip install -r requirements-dev.txt
run_dev:
    source ~/anaconda3/etc/profile.d/conda.sh && conda activate $(ENV_NAME) && cd src && uvicorn main:app --reload --host 0.0.0.0

run_prod:
    source ~/anaconda3/etc/profile.d/conda.sh && conda activate $(ENV_NAME) && cd src && uvicorn main:app --host 0.0.0.0

# Makefile for managing the conda environment

# Name of the conda environment
ENV_NAME = financial_analyst

# Create the conda environment
create_env:
	conda create --name $(ENV_NAME) python=3.10 -y

# Activate the conda environment
activate_env:
	source ~/anaconda3/etc/profile.d/conda.sh && conda activate $(ENV_NAME)

# Install dependencies from requirements.txt
install_deps:
	conda install --name $(ENV_NAME) --file requirements.txt -y
	conda install --name $(ENV_NAME) --file requirements-dev.txt -y

requirements: test_environment
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt
	$(PYTHON_INTERPRETER) -m pip install -r requirements-dev.txt
	$(PYTHON_INTERPRETER) -m pip install setuptools wheel

# Format code using black
quality:
	black src
	flake8 src --ignore=E501,W503
    
create_environment:
ifeq (True,$(HAS_CONDA))
	@echo ">>> Detected conda, creating conda environment."
ifeq (3,$(findstring 3,$(PYTHON_INTERPRETER)))
	conda create --name $(PROJECT_NAME) python=3.10
else
	conda create --name $(PROJECT_NAME) python=2.7
endif
	@echo ">>> New conda env created. Activate with:\nsource activate $(PROJECT_NAME)"
else
	$(PYTHON_INTERPRETER) -m pip install -q virtualenv virtualenvwrapper
	@echo ">>> Installing virtualenvwrapper if not already installed.\nMake sure the following lines are in shell startup file\n\
	export WORKON_HOME=$$HOME/.virtualenvs\nexport PROJECT_HOME=$$HOME/Devel\nsource /usr/local/bin/virtualenvwrapper.sh\n"
	@bash -c "source `which virtualenvwrapper.sh`;mkvirtualenv $(PROJECT_NAME) --python=$(PYTHON_INTERPRETER)"
	@echo ">>> New virtualenv created. Activate with:\nworkon $(PROJECT_NAME)"
endif

## Test python environment is setup correctly
test_environment:
	$(PYTHON_INTERPRETER) test_environment.py
# clean:
# Initialize the local Postgres DB using schema.sql
db-init:
	psql -U postgres -d finance_db -f resources/schema.sql
