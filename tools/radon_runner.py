import sys
import json
from radon.complexity import cc_visit
from pathlib import Path

def analyze_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        code = file.read()
    complexity = cc_visit(code)
    result = [
        {"name": c.name, "complexity": c.complexity, "lineno": c.lineno}
        for c in complexity
    ]
    return result

if __name__ == "__main__":
    try:
        if len(sys.argv) != 2:
            raise ValueError("Provide exactly one file path.")
        file_path = Path(sys.argv[1])
        if not file_path.exists():
            raise FileNotFoundError("File does not exist.")
        analysis_result = analyze_file(str(file_path))
        print(json.dumps({"result": analysis_result}, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)
