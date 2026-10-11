
import re


def extract_intents(text):
    """Extract basic intents and possible safety concerns from text."""
    text = text.strip()
    lower = text.lower()

    result = {
        "text": text,
        "intent": "general_statement",
        "requests": [],
        "offers": [],
        "refusals": [],
        "promises": [],
        "accusations": [],
        "safety_flag": False,
        "verified_events": []
    }

    if not text:
        return result

    if any(word in lower for word in [
        "need", "please", "could you", "should", "request"
    ]):
        result["intent"] = "request"
        result["requests"].append(text)

    if any(word in lower for word in [
        "i can help", "i will help", "i can take", "i offer"
    ]):
        result["intent"] = "offer"
        result["offers"].append(text)

    if any(word in lower for word in [
        "i refuse", "i won't", "i cannot agree", "i disagree"
    ]):
        result["intent"] = "refusal"
        result["refusals"].append(text)

    if any(word in lower for word in [
        "i will complete", "i will deliver",
        "i promise", "i will finish"
    ]):
        result["intent"] = "promise"
        result["promises"].append(text)

    if any(word in lower for word in [
        "you always", "you never", "you lied",
        "unfair treatment", "blame you"
    ]):
        result["accusations"].append(text)

    safety_terms = [
        "threat", "threatened", "harassment",
        "discrimination", "unsafe", "violence",
        "physical harm", "sexual harassment"
    ]

    if any(term in lower for term in safety_terms):
        result["safety_flag"] = True

    return result
