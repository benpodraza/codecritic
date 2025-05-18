from importlib import import_module


def load_all_extensions():
    import_module("app.extensions.agents")
    import_module("app.extensions.system_managers")
    import_module("app.extensions.state_managers")
    import_module("app.extensions.prompt_generators")
    import_module("app.extensions.context_providers")
    import_module("app.extensions.tool_providers")
    import_module("app.extensions.scoring_models")
