import pytest

from bitcaster_sdk.helpers import JsonUpdateMode, merge_dicts, override_dicts, process_dict, remove_dicts


def test_choices():
    assert JsonUpdateMode.choices() == ["merge", "remove", "override", "ignore", "rewrite"]


def test_process_dict_merge():
    d1 = {"a": 1, "b": {"x": 10}}
    d2 = {"b": {"y": 20}, "c": 3}
    assert process_dict(d1, d2, JsonUpdateMode.MERGE) == {"a": 1, "b": {"x": 10, "y": 20}, "c": 3}


def test_process_dict_override():
    d1 = {"a": 1, "b": {"x": 10}}
    d2 = {"b": 99}
    assert process_dict(d1, d2, JsonUpdateMode.OVERRIDE) == {"a": 1, "b": 99}


def test_process_dict_remove():
    assert process_dict({"a": 1, "b": 2}, {"b": True}, JsonUpdateMode.REMOVE) == {"a": 1}


def test_process_dict_unknown():
    with pytest.raises(ValueError, match="Unknown JsonUpdateMode"):
        process_dict({}, {}, "unknown")


def test_merge_dicts_nested():
    d1 = {"a": {"x": 1, "y": 2}, "b": 3}
    d2 = {"a": {"y": 20, "z": 30}, "c": 4}
    result = merge_dicts(d1, d2)
    assert result == {"a": {"x": 1, "y": 20, "z": 30}, "b": 3, "c": 4}


def test_override_dicts():
    d1 = {"a": 1, "b": {"x": 10}}
    d2 = {"b": {"y": 20}, "c": 3}
    assert override_dicts(d1, d2) == {"a": 1, "b": {"y": 20}, "c": 3}


def test_remove_dicts_key_missing():
    d1 = {"a": 1}
    d2 = {"b": True}
    assert remove_dicts(d1, d2) == {"a": 1}


def test_remove_dicts_nested_result_empty():
    d1 = {"a": {"b": {"c": 1}}}
    d2 = {"a": {"b": {"c": True}}}
    assert remove_dicts(d1, d2) == {}


def test_remove_dicts_nested_result_non_empty():
    d1 = {"a": {"x": 1, "y": 2}}
    d2 = {"a": {"y": True}}
    assert remove_dicts(d1, d2) == {"a": {"x": 1}}
