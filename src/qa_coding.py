"""Rule-based coding scheme for student->agent conversational exchanges.

Two coding passes, both keyword/pattern based and fully specified:
  1. Relevance: on-topic vs off-topic (off-topic = games/food/idle chatter with
     no science content).
  2. Function (for on-topic and notable off-topic moves):
       - transfer_initiating  : applies inquiry ideas to a new everyday context
       - authority_challenging: tests the agent's authority / threatens to tell
       - procedural           : asks what to do / how to proceed
       - conceptual           : asks why/how about soil-science content
       - other

The scheme is transparent so inter-rater style validation and error auditing
are straightforward.
"""

from __future__ import annotations

OFFTOPIC_KEYWORDS = (
    "minecraft", "video game", "video games", "play", "boring", "lol",
    "sweet", "sweeter", "sweetest", "fruit", "mineral",
)
SCIENCE_KEYWORDS = (
    "soil", "sand", "clay", "loam", "water", "drain", "drainage", "particle",
    "crop", "corn", "watermelon", "pineapple", "cactus", "plant", "grow",
    "fair test", "characteristic", "colour", "color", "evidence", "claim",
    "worm", "root",
)
TRANSFER_PATTERNS = ("can sandy soil grow", "can watermelon grow", "grow pineapples",
                     "other factors", "cactuses need", "grow in clay")
AUTHORITY_PATTERNS = ("tell the teacher", "why should i believe", "believe you",
                      "why do you keep asking", "do it for me", "do it for me",
                      "give me the sentence", "can you do it for me")
PROCEDURAL_PATTERNS = ("what do i do", "what do i do now", "what should we write",
                       "how do we", "how much water", "how many", "is this right",
                       "next", "answer", "give hint", "what do i do now")


def _contains(text: str, needles) -> bool:
    return any(n in text for n in needles)


def code_exchange(text: str) -> dict:
    t = text.lower().strip()
    on_topic = _contains(t, SCIENCE_KEYWORDS) and not (
        _contains(t, OFFTOPIC_KEYWORDS) and not _contains(t, SCIENCE_KEYWORDS)
    )
    # Off-topic wins if idle/game/food chatter with no science content.
    if _contains(t, OFFTOPIC_KEYWORDS) and not _contains(t, SCIENCE_KEYWORDS):
        on_topic = False

    if _contains(t, TRANSFER_PATTERNS):
        function = "transfer_initiating"
    elif _contains(t, AUTHORITY_PATTERNS):
        function = "authority_challenging"
    elif _contains(t, PROCEDURAL_PATTERNS):
        function = "procedural"
    elif _contains(t, SCIENCE_KEYWORDS):
        function = "conceptual"
    else:
        function = "other"

    return {"relevance": "on_topic" if on_topic else "off_topic", "function": function}


def code_all(rows: list[dict]) -> dict:
    relevance = {"on_topic": 0, "off_topic": 0}
    function: dict[str, int] = {}
    coded = []
    for r in rows:
        c = code_exchange(r["text"])
        relevance[c["relevance"]] += 1
        function[c["function"]] = function.get(c["function"], 0) + 1
        coded.append({"group": r.get("group"), "text": r["text"], **c})
    total = len(rows)
    return {
        "total": total,
        "relevance": {k: {"count": v, "pct": round(v / total, 4) if total else 0.0}
                      for k, v in relevance.items()},
        "function": {k: {"count": v, "pct": round(v / total, 4) if total else 0.0}
                     for k, v in sorted(function.items())},
        "coded": coded,
    }
