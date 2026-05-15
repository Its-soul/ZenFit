from dataclasses import dataclass, field


@dataclass
class AgentInput:
    user_id: str
    message: str
    context: dict
    memories: list[dict] = field(default_factory=list)


@dataclass
class AgentOutput:
    message: str
    recommendations: list[dict] = field(default_factory=list)
    memory_to_write: str | None = None
    confidence: float = 0.75


class BaseAgent:
    name = "base_agent"

    def run(self, agent_input: AgentInput) -> AgentOutput:
        raise NotImplementedError

