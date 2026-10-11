
from agents.nlu_parser import extract_intents


def test_request():
    result = extract_intents("I need a fairer workload.")
    assert result["intent"] == "request"
    assert result["requests"]


def test_offer():
    result = extract_intents("I can help with the testing tasks.")
    assert result["intent"] == "offer"


def test_refusal():
    result = extract_intents("I refuse to accept this proposal.")
    assert result["intent"] == "refusal"


def test_promise():
    result = extract_intents("I will complete the tasks.")
    assert result["intent"] == "promise"


def test_safety_flag():
    result = extract_intents("I experienced workplace harassment.")
    assert result["safety_flag"] is True


def test_empty_text():
    result = extract_intents("")
    assert result["intent"] == "general_statement"


def test_does_not_verify_claims():
    result = extract_intents("My manager treated me unfairly.")
    assert result["verified_events"] == []
