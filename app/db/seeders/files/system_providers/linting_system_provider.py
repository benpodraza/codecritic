from app.providers.system_provider_base import SystemProviderBase
from app.enums.system_enums import Decision


class LintingSystemProvider(SystemProviderBase):
    def _transition(self, state: dict, agent_output: str | None) -> dict:
        if state["state"] == "start":
            return {"state": "generate", "reason": "initial entry"}

        if state["state"] == "generate":
            return {"state": "discriminate", "reason": "completed generation"}

        if state["state"] == "discriminate":
            if agent_output and "[AGENT_DECISION]accept" in agent_output:
                return {"state": "end", "reason": "accepted by discriminator"}
            return {"state": "generate", "reason": "rejected by discriminator, retrying generation"}

        return {"state": "end", "reason": "unknown state or fallback"}
