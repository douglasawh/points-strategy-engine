# pte/nlp/llm_intent_ollama.py
from __future__ import annotations
import json
import re
from typing import Dict, Any
import ollama

SYSTEM_PROMPT = """You are a strict intent extractor for a travel planner.
Return ONLY compact JSON with no explanations and no markdown.
Schema:
{
  "intent": "<one of: set_dates | set_nonstop | set_start_hotel | add_alternate_hotel | show_plan | plan_trip | help | reset>",
  "slots": {
    "start": "YYYY-MM-DD or null",
    "end": "YYYY-MM-DD or null",
    "prefer_nonstop": true/false or null,
    "hotel": "<exact name or null>"
  }
}

Rules:
- Dates: extract if present; otherwise null.
- Nonstop: infer True if user asks for nonstop/direct/no connections; False if they say not nonstop or prefer connections.
- hotel: normalize to either "Park Hyatt Tokyo" or "Andaz Tokyo Toranomon Hills" if mentioned; otherwise null.
- If user asks to generate or show the plan, intent=show_plan.
- If user asks generally to plan a trip or describes preferences without explicit action, intent=plan_trip.
- Return ONLY the JSON object. No prose, no code fences.
"""

def _strip_code_fences(text: str) -> str:
    # Some models wrap JSON in ```json ... ```
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE | re.MULTILINE)

def llm_extract_intent(message: str, model: str = "llama3", temperature: float = 0.1) -> Dict[str, Any]:
    """
    Calls Ollama locally to parse the user's message into an intent JSON.
    Returns a dict: {"intent": "...", "slots": {...}}
    """
    resp = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        options={"temperature": temperature},
    )
    raw = resp["message"]["content"]
    raw = _strip_code_fences(raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: if the model output was noisy, try to extract JSON object heuristically
        m = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if m:
            data = json.loads(m.group(0))
        else:
            # Ultimate fallback: generic plan
            data = {"intent": "plan_trip", "slots": {"start": None, "end": None, "prefer_nonstop": None, "hotel": None}}

    # Normalize hotel slot
    hotel = (data.get("slots") or {}).get("hotel")
    if hotel:
        h = hotel.lower().strip()
        if h.startswith("park"):
            data["slots"]["hotel"] = "Park Hyatt Tokyo"
        elif h.startswith("andaz"):
            data["slots"]["hotel"] = "Andaz Tokyo Toranomon Hills"

    return data
