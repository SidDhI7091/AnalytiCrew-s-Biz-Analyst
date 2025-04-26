import json
import os

def load_ideal_requirements():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "ideal_requirements.json")
    
    with open(file_path, "r") as f:
        ideal_reqs = json.load(f)
    
    return ideal_reqs
