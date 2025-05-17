from app.utils.agents.base_agent.context_filter import ContextFilter

sample_context = {
    "symbol": "foo",
    "source_file": "foo.py",
    "children": [
        {"content": "logger.info('x')\nBREADCRUMB: a"},
        {"content": "no markers"},
        {"content": "BREADCRUMB: only"},
    ],
}


def test_default_strategy_returns_input():
    cf = ContextFilter()
    assert cf.apply(sample_context) == sample_context


def test_only_children_with_logger_filters():
    cf = ContextFilter("only_children_with_logger")
    result = cf.apply(sample_context)
    assert len(result["children"]) == 1
    assert result["logger_calls"] == 1
    assert result["breadcrumbs"] == 1


def test_only_breadcrumb_children_filters():
    cf = ContextFilter("only_breadcrumb_children")
    result = cf.apply(sample_context)
    assert len(result["children"]) == 2
    assert result["breadcrumbs"] == 2


def test_minimal_strategy():
    cf = ContextFilter("minimal")
    result = cf.apply(sample_context)
    assert result == {
        "symbol": "foo",
        "source_file": "foo.py",
        "metadata": []
    }


def test_unknown_strategy_raises():
    cf = ContextFilter("unknown")
    try:
        cf.apply(sample_context)
    except ValueError as e:
        assert "Unknown context filter strategy" in str(e)
    else:
        assert False, "ValueError not raised"
