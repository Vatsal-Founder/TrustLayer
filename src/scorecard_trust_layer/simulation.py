import json
import uuid

from fastapi import HTTPException
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from scorecard_trust_layer.db import get_connection
from scorecard_trust_layer.llm import get_model
from scorecard_trust_layer.rubric import RUBRIC_BY_KEY
from scorecard_trust_layer.scorer import format_transcript, score_transcript

SCENARIO_SYSTEM_PROMPT = """You are designing a roleplay scenario to test a support agent's \
{dimension_title}, defined as: {dimension_description}

Here is a real past conversation where an agent scored low on {dimension_title}:

--- past conversation ---
{original_transcript}
--- end past conversation ---

Based on specifically what went wrong in that conversation, write a short opening customer message \
(2-3 sentences) for a NEW scenario — a different situation, but one that stress-tests the same \
underlying weakness the agent showed above.

Return only the customer's opening message, nothing else."""

CUSTOMER_PERSONA_PROMPT = """You are role-playing as a customer in a support chat. Stay in \
character and keep replies to 1-3 sentences. The scenario you are living through: {scenario}"""


def start_simulation(transcript_id: str, gap_dimension: str) -> dict:
    conn = get_connection()
    row = conn.execute(
        "SELECT raw_json FROM transcripts WHERE id = ?", (transcript_id,)
    ).fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="transcript not found")
    conn.close()

    original_transcript = json.loads(row["raw_json"])
    dimension = RUBRIC_BY_KEY[gap_dimension]
    model = get_model(temperature=0.8)
    scenario_prompt = SCENARIO_SYSTEM_PROMPT.format(
        dimension_title=dimension.title,
        dimension_description=dimension.description,
        original_transcript=format_transcript(original_transcript),
    )
    opening_message = model.invoke([SystemMessage(content=scenario_prompt)]).content
    persona_prompt = CUSTOMER_PERSONA_PROMPT.format(scenario=opening_message)

    session_id = str(uuid.uuid4())
    conn = get_connection()
    conn.execute(
        "INSERT INTO simulation_sessions (id, gap_dimension, transcript_id, persona_prompt) "
        "VALUES (?, ?, ?, ?)",
        (session_id, gap_dimension, transcript_id, persona_prompt),
    )
    conn.execute(
        "INSERT INTO simulation_turns (session_id, role, message) VALUES (?, 'customer', ?)",
        (session_id, opening_message),
    )
    conn.commit()
    conn.close()

    return {"session_id": session_id, "opening_message": opening_message}


def run_turn(session_id: str, agent_message: str) -> dict:
    conn = get_connection()
    session = conn.execute(
        "SELECT * FROM simulation_sessions WHERE id = ?", (session_id,)
    ).fetchone()
    prior_turns = conn.execute(
        "SELECT role, message FROM simulation_turns WHERE session_id = ? ORDER BY id",
        (session_id,),
    ).fetchall()

    conn.execute(
        "INSERT INTO simulation_turns (session_id, role, message) VALUES (?, 'agent', ?)",
        (session_id, agent_message),
    )

    # The AI customer persona sees its own prior lines as "assistant" turns and
    # the agent's lines as "user" turns, so it keeps replying in character.
    messages = [SystemMessage(content=session["persona_prompt"])]
    for turn in prior_turns:
        role_cls = AIMessage if turn["role"] == "customer" else HumanMessage
        messages.append(role_cls(content=turn["message"]))
    messages.append(HumanMessage(content=agent_message))

    model = get_model(temperature=0.8)
    customer_reply = model.invoke(messages).content

    conn.execute(
        "INSERT INTO simulation_turns (session_id, role, message) VALUES (?, 'customer', ?)",
        (session_id, customer_reply),
    )
    conn.commit()
    conn.close()

    return {"customer_reply": customer_reply}


def finish_simulation(session_id: str) -> dict:
    conn = get_connection()
    session = conn.execute(
        "SELECT * FROM simulation_sessions WHERE id = ?", (session_id,)
    ).fetchone()
    turns = conn.execute(
        "SELECT role, message FROM simulation_turns WHERE session_id = ? ORDER BY id",
        (session_id,),
    ).fetchall()

    transcript = {"turns": [{"role": t["role"], "message": t["message"]} for t in turns]}
    result, _ = score_transcript(transcript, temperature=0.0)
    dimension = session["gap_dimension"]
    score = getattr(result, dimension).score
    status = "certified" if score >= 4 else "needs_retry"

    conn.execute("UPDATE simulation_sessions SET status = ? WHERE id = ?", (status, session_id))
    conn.commit()
    conn.close()

    return {"status": status, "dimension": dimension, "score": score}
