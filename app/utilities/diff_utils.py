import difflib

def summarize_diff(before: str, after: str) -> str:
    """Returns a human-readable summary of what changed between two versions."""
    before_lines = before.strip().splitlines()
    after_lines = after.strip().splitlines()
    diff = list(difflib.unified_diff(before_lines, after_lines, lineterm=""))
    if not diff:
        return "No differences detected."

    summary = ["Changes:"]
    for line in diff:
        if line.startswith("+ ") and not line.startswith("+++"):
            summary.append(f"Added: {line[2:]}")
        elif line.startswith("- ") and not line.startswith("---"):
            summary.append(f"Removed: {line[2:]}")

    return "\n".join(summary[:10])  # Limit to first 10 lines
