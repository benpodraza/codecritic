
from enum import Enum


class ModelEngine(str, Enum):
    GPT_4O = "openai/gpt-4o"
    GPT_4 = "openai/gpt-4"
    CLAUDE_OPUS = "anthropic/claude-3-opus"
    GEMINI_25 = "google/gemini-2.5"
    CUSTOM = "custom/fine-tune"

    @property
    def runner_class(self):
        from app.utils.engine.openai_gpt4o_runner import OpenAiGpt4oAgentEngineRunner
        return {
            ModelEngine.GPT_4O: OpenAiGpt4oAgentEngineRunner,
            ModelEngine.GPT_4: OpenAiGpt4oAgentEngineRunner,
            # ModelEngine.CLAUDE_OPUS: ClaudeAgentEngineRunner,
            # ModelEngine.GEMINI_25: GeminiAgentEngineRunner,
            # ModelEngine.CUSTOM: CustomAgentEngineRunner
        }.get(self)


class PromptVariant(str, Enum):
    ZERO_SHOT = "zero_shot"
    FEW_SHOT = "few_shot"
    REFINEMENT_LOOP = "refinement_loop"