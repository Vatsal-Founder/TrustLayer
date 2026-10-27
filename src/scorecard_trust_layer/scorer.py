import hashlib

from langchain_core.messages import HumanMessage, SystemMessage

from scorecard_trust_layer.llm import get_model
from scorecard_trust_layer.rubric import rubric_prompt_block
from scorecard_trust_layer.schemas import ScoreResult

SCORING_SYSTEM_PROMPT = """You are a strict quality assurance reviewer for customer support \
conversations. Score the given transcript against each rubric dimension below on a 1-5 scale. \
For every dimension, quote the exact line from the transcript that justifies your score, and give \
a one-sentence rationale.

Rubric:
{rubric_block}"""


def format_transcript(transcript: dict) -> str:
    return "\n".join(f"{turn['role']}: {turn['message']}" for turn in transcript["turns"])


def scorer_version_id(model_name: str) -> str:
    raw = rubric_prompt_block() + "|" + model_name
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def score_transcript(
    transcript: dict, use_cheap: bool = False, temperature: float = 0.3
) -> tuple[ScoreResult, str]:
    model = get_model(use_cheap=use_cheap, temperature=temperature)
    structured_model = model.with_structured_output(ScoreResult)

    system = SystemMessage(content=SCORING_SYSTEM_PROMPT.format(rubric_block=rubric_prompt_block()))
    human = HumanMessage(content=format_transcript(transcript))

    result = structured_model.invoke([system, human])
    version_id = scorer_version_id(model.model)
    return result, version_id
