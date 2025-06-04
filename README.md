# Nextflow-app for Alma
Nextflow App is a web-based tool built with Streamlit, hosted on our internal ShinyProxy server. It allows researchers to launch pre-configured Nextflow pipelines on the Alma server with just a click — no command-line work needed.

Before using the app, make sure the following setup steps are completed:

1. Access to Alma
You must have an active user account and access credentials for the Alma server.

2. Configure Mamba
The application relies on Mamba to manage environments. Run the following commands to initialize Mamba:
```bash
srun --pty --mem=12GB -c4 -t 15:00:00 -p interactive bash
mamba init
source ~/.bashrc
```

3. Change the Nextflow Assets Directory and singlarity cache directory
By default, Nextflow stores pipeline files in your home directory, which has limited storage on Alma. We strongly recommend redirecting the asset path to your SCRATCH space. Open ~/.bashrc using vi and write the following lines:
```bash
export NXF_ASSETS=/data/scratch/personal/path/<your_username>/.nextflow/assets
export NXF_SINGULARITY_CACHEDIR=/data/scratch/shared/SINGULARITY-DOWNLOAD/nextflow/.singularity
```
Reload your .bashrc:
```bash
source ~/.bashrc
```

4. Configure Git Access for ICR Pipelines
If you're using one of our ICR-maintained pipelines (e.g., icr-nanopore-pauses), you'll need to configure Git access for Nextflow to pull them directly from our GitLab instance.

a. Set the SCM (Source Code Management) configuration path:
Open ~/.bashrc using vi and write the following command:
```bash
export NXF_SCM_FILE=/data/scratch/personal/path/<your_username>/.nextflow/scm
```

Reload your .bashrc:
```bash
source ~/.bashrc
```

b. Create the SCM file:
Note: Make sure to update the path to the scm file
```bash
echo -e "providers {\n    icr {\n        server = 'https://git.icr.ac.uk'\n        platform = 'gitlab'\n    }\n}" > /data/scratch/personal/path/<your_username>/.nextflow/scm
```

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
