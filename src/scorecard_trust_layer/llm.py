from langchain_openai import ChatOpenAI

from scorecard_trust_layer.config import CHEAP_MODEL, OPENAI_API_KEY, PRIMARY_MODEL


def get_model(use_cheap: bool = False, temperature: float = 0.3) -> ChatOpenAI:
    model_name = CHEAP_MODEL if use_cheap else PRIMARY_MODEL
    return ChatOpenAI(
        model=model_name,
        api_key=OPENAI_API_KEY,
        temperature=temperature,
    )
