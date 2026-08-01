import yaml
from pathlib import Path

def read_yaml(path_to_yaml : Path):
    with open(path_to_yaml) as file:
        content = yaml.safe_load(file)

    return content