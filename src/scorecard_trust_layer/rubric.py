from pydantic import BaseModel


class DimensionDefinition(BaseModel):
    key: str
    title: str
    description: str


RUBRIC: list[DimensionDefinition] = [
    DimensionDefinition(
        key="empathy",
        title="Empathy",
        description=(
            "Did the agent acknowledge the customer's frustration or urgency before moving to "
            "problem-solving? A 5 opens with a direct acknowledgment of how the customer feels. "
            "A 1 jumps straight to policy or troubleshooting with no acknowledgment at all."
        ),
    ),
    DimensionDefinition(
        key="accuracy",
        title="Accuracy",
        description=(
            "Is the information or resolution the agent gives technically correct? A 5 gives a "
            "correct, complete answer. A 1 gives information that is factually wrong or would not "
            "actually resolve the customer's issue."
        ),
    ),
    DimensionDefinition(
        key="policy_adherence",
        title="Policy adherence",
        description=(
            "Did the agent follow stated billing, refund, and escalation policy rather than "
            "improvising? A 5 follows policy exactly and explains it. A 1 contradicts policy or "
            "makes an unauthorized exception."
        ),
    ),
    DimensionDefinition(
        key="clarity",
        title="Clarity",
        description="How clear was the agent?",
    ),
]

RUBRIC_BY_KEY: dict[str, DimensionDefinition] = {d.key: d for d in RUBRIC}


def rubric_prompt_block() -> str:
    return "\n".join(f"- {d.title} ({d.key}): {d.description}" for d in RUBRIC)
