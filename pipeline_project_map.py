import json


def load_json_to_dict(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


file_path = "custom_files/pipeline_project_map.json"
map_pipeline_project = load_json_to_dict(file_path)
