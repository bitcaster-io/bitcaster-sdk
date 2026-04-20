from bitcaster_sdk.helpers import JsonUpdateMode, process_dict


def test_merge_simple():
    d1 = {"a": 1, "b": 2}
    d2 = {"b": 10, "c": 3}
    assert process_dict(d1, d2, JsonUpdateMode.MERGE) == {"a": 1, "b": 10, "c": 3}


def test_merge_nested():
    d1 = {"a": {"x": 1, "y": 2}}
    d2 = {"a": {"y": 20, "z": 30}}
    assert process_dict(d1, d2, JsonUpdateMode.MERGE) == {"a": {"x": 1, "y": 20, "z": 30}}


def test_override_simple():
    d1 = {"a": 1, "b": 2}
    d2 = {"b": 99}
    assert process_dict(d1, d2, JsonUpdateMode.OVERRIDE) == {"a": 1, "b": 99}


def test_override_nested_replacement():
    d1 = {"a": {"x": 1}}
    d2 = {"a": {"y": 2}}
    # override does NOT deep merge
    assert process_dict(d1, d2, JsonUpdateMode.OVERRIDE) == {"a": {"y": 2}}


def test_remove_simple():
    d1 = {"a": 1, "b": 2, "c": 3}
    d2 = {"b": True}
    assert process_dict(d1, d2, JsonUpdateMode.REMOVE) == {"a": 1, "c": 3}


def test_remove_nested():
    d1 = {"a": {"x": 1, "y": 2}}
    d2 = {"a": {"y": True}}
    assert process_dict(d1, d2, JsonUpdateMode.REMOVE) == {"a": {"x": 1}}


def test_remove_deletes_empty_dict():
    d1 = {"a": {"x": 1}}
    d2 = {"a": {"x": True}}
    assert process_dict(d1, d2, JsonUpdateMode.REMOVE) == {}
