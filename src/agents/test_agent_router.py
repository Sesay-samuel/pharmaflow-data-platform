from src.agents.agent_router import route_question


def test_route_top_branches():
    result = route_question("Show me the top 3 branches")

    assert result["status"] == "success"
    assert result["tool"] == "get_top_records"
    assert len(result["result"]) == 3


def test_route_supplier_total():
    result = route_question("What is the total supplier spending?")

    assert result["status"] == "success"
    assert result["tool"] == "get_dataset_summary"
    assert result["result"]["records"] == 12


def test_reject_destructive_request():
    result = route_question("Delete all pharmacy records")

    assert result["status"] == "unsupported"


def test_reject_ambiguous_request():
    result = route_question("Compare branches and medicines")

    assert result["status"] == "unsupported"


def test_reject_empty_question():
    try:
        route_question("")
        assert False, "Expected ValueError"
    except ValueError:
        pass
