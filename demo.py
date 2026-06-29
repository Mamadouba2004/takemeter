import os
import json
from groq import Groq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
if not GROQ_API_KEY:
    GROQ_API_KEY = input("Paste your Groq API key: ").strip()

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
You are classifying posts and comments from r/soccer, a large Reddit community for football discussion.
Assign each post to exactly one of the following three categories.

analysis: A post that makes a structured argument supported by specific, verifiable evidence — statistics, tactical observations, historical comparisons, or formation breakdowns — where the evidence is doing genuine reasoning work toward the conclusion.
Example: "City's high press wasn't working because Valverde was dropping into the half-space and bypassing the press trigger — Rodri had to cover too much ground, which is why you saw gaps in the 6-8 channel in the second half."

hot_take: A bold, confident opinion stated without meaningful supporting evidence. The author asserts a verdict — sometimes provocative, sometimes contrarian — but does not reason through it.
Example: "Messi is done. He's been coasting on reputation for two years and everyone's too scared to say it."

reaction: An immediate emotional response to a specific moment, result, or event. Little to no argument — the post is expressing a feeling in real time, tied to something that just happened.
Example: "WHAT A GOAL. I don't even support Arsenal but that was absolutely filthy."

Decision rule for borderline cases: if a post cites one stat to support a confident verdict but does not reason toward a nuanced conclusion, label it hot_take. If the post expresses a feeling about a specific just-happened event even if it includes a brief opinion, label it reaction.

Respond with a JSON object with two fields:
- "label": exactly one of "analysis", "hot_take", or "reaction"
- "confidence": your confidence as a float between 0.0 and 1.0

Example response: {"label": "hot_take", "confidence": 0.92}
"""

LABEL_COLORS = {
    "analysis":  "\033[94m",   # blue
    "hot_take":  "\033[93m",   # yellow
    "reaction":  "\033[92m",   # green
}
RESET = "\033[0m"
BOLD  = "\033[1m"

def classify(text: str) -> dict:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Classify this post:\n\n{text}"},
        ],
        temperature=0,
        max_tokens=50,
    )
    raw = response.choices[0].message.content.strip()
    try:
        result = json.loads(raw)
        return result
    except json.JSONDecodeError:
        # fallback: parse label from raw text
        for label in ["analysis", "hot_take", "reaction"]:
            if label in raw.lower():
                return {"label": label, "confidence": None}
        return {"label": "unknown", "confidence": None}

def print_result(result: dict):
    label = result.get("label", "unknown")
    confidence = result.get("confidence")
    color = LABEL_COLORS.get(label, "")
    conf_str = f"{confidence:.0%}" if confidence is not None else "n/a"
    print()
    print(f"  Label:      {color}{BOLD}{label}{RESET}")
    print(f"  Confidence: {color}{BOLD}{conf_str}{RESET}")
    print()

def main():
    print()
    print(f"{BOLD}TakeMeter — r/soccer Discourse Classifier{RESET}")
    print("Labels: analysis | hot_take | reaction")
    print("Type a post and press Enter. Ctrl+C to quit.")
    print("-" * 50)

    while True:
        try:
            print()
            text = input("Post: ").strip()
            if not text:
                continue
            print("Classifying...", end="\r")
            result = classify(text)
            print_result(result)
        except KeyboardInterrupt:
            print("\nDone.")
            break

if __name__ == "__main__":
    main()
