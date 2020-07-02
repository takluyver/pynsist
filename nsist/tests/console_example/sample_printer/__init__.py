import json
import os.path
import sys

def main():
    data_file = os.path.join(os.path.dirname(__file__), 'data.txt')
    with open(data_file, 'r', encoding='utf-8') as f:
        data_from_file = f.read().strip()

    info = {
        'py_executable': sys.executable,
        'py_version': sys.version,
        'data_file_path': data_file,
        'data_file_content': data_from_file,
    }

    print(json.dumps(info, indent=True))
