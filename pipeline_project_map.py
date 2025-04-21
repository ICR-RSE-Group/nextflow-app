import yaml

file_path = "custom_files/pipeline_project_map_specifications.yaml"

with open(file_path, "r") as f:
    map_pipeline_project = yaml.safe_load(f)
