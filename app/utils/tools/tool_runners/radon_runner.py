from radon.complexity import cc_visit

def run_radon(code: str) -> str:
    try:
        blocks = cc_visit(code)
        avg_complexity = sum(b.complexity for b in blocks) / len(blocks) if blocks else 0

        function_count = sum(1 for b in blocks if b.classname is None)
        class_count = len(set(b.classname for b in blocks if b.classname))

        return str({
            "complexity": f"{avg_complexity:.2f}",
            "function_count": function_count,
            "class_count": class_count
        })
    except Exception as e:
        return f'{{"error": "{str(e)}"}}'
