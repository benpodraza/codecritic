from ...abstract_classes.prompt_generator_base import PromptGeneratorBase


class DummyPromptGenerator(PromptGeneratorBase):
    def _generate_prompt(self, *args, **kwargs) -> str:
        self.logger.info("Dummy prompt generated")
        return "dummy prompt"
