from enum import Enum

class ToolProvider(Enum):
    BLACK = 1
    SONARCLOUD = 2
    RUFF = 3
    RADON = 4
    MYPY = 5
    DOCFORMATTER = 6
    SYMBOL_GRAPH = 7

    @classmethod
    def get_name(cls, id_):
        for tool in cls:
            if tool.value == id_:
                return tool.name.lower()
        return f"Unknown ({id_})"
