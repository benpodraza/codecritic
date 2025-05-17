from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def build_agent_prompt(
    source_code: str,
    template_path: str,
    max_lines: int = 20,
    variant: str = "zero_shot"
) -> str:
    """
    Loads and renders a Jinja2 prompt template with support for includes and variables.

    Args:
        source_code (str): The Python code to embed in the prompt.
        template_path (str): Full path to the main prompt template (e.g. zero_shot.txt).
        max_lines (int): Max allowed lines per function before splitting.
        variant (str): Prompting strategy variant (e.g., zero_shot, few_shot, refinement_loop).

    Returns:
        str: Fully rendered prompt ready for LLM input.
    """
    template_file = Path(template_path).name
    template_dir = Path(template_path).parent

    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template(template_file)

    return template.render(
        code=source_code,
        max_lines_per_function=max_lines,
        variant=variant
    )
