# green-alma

## Dev setup

1. Virtual environment
```bash
python3 -m venv .nf-env
source .nf-env/bin/activate
```

2. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. Run the app
```bash
streamlit run index.py
```
## CI/CD pipeline:

The current CI/CD workflow tests the streamlit app on the latest ubuntu version and iteratively on
3 different python versions (3.9, 3.10 and 3.11).

In each setup, the workflow checks if the app can start and run for 10s (both return codes 0 and 124 are considered as successful run).
In addition the workflow runs a linting phase and forces flake8 to exit with a status code of 0 even if there are errors.
Flake8 displays a summary of all the errors and warning at the end of the output.

## Setup pre-commit locally:
```
source .nf-env/bin/activate
pip install pre-commit
```

Setup the pre-commit hook in your local git directory:

```
cd nextflow-app
pre-commit install
```

Now, pre-commit hooks will run automatically on every commit to ensure code quality and consistency.


(optional) To run pre-commit manually against all files:

```
pre-commit run --all-files
```
