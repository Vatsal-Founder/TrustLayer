from typing import Literal

from pydantic import BaseModel, Field

DimensionKey = Literal["empathy", "accuracy", "policy_adherence", "clarity"]


class DimensionScore(BaseModel):
    score: int = Field(ge=1, le=5)
    citation: str
    rationale: str


class ScoreResult(BaseModel):
    """Structured output the LLM must return for one scoring pass."""

    empathy: DimensionScore
    accuracy: DimensionScore
    policy_adherence: DimensionScore
    clarity: DimensionScore


class ScoreRequest(BaseModel):
    transcript_id: str


class DimensionResult(BaseModel):
    score: float
    stddev: float
    confidence: Literal["high", "low"]
    citation: str
    rationale: str


class ScoreResponse(BaseModel):
    transcript_id: str
    scorer_version_id: str
    dimensions: dict[str, DimensionResult]
    gaps: list[str]


class LabelRequest(BaseModel):
    dimension: DimensionKey
    human_score: int = Field(ge=1, le=5)


class CalibrationRunRequest(BaseModel):
    use_cheap_model: bool = False


class RegressionItem(BaseModel):
    dimension: str
    before_mae: float
    after_mae: float
    delta: float


class CalibrationRunResponse(BaseModel):
    run_id: int
    scorer_version_id: str
    model_used: str
    mae_by_dimension: dict[str, float]
    agreement_rate: float
    regressions: list[RegressionItem]


class SimulationStartRequest(BaseModel):
    transcript_id: str
    gap_dimension: DimensionKey


class SimulationTurnRequest(BaseModel):
    session_id: str
    message: str


class SimulationFinishRequest(BaseModel):
    session_id: str
