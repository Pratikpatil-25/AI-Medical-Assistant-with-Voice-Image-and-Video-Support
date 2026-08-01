from test_read_yaml import read_yaml
from pathlib import Path 

params = read_yaml(Path("params.yaml"))

print(params["temperature"])
print(params["gemini_model"])