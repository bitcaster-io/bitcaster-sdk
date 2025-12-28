from typing import TypeAlias

JSONScalar: TypeAlias = str | int | float | bool | None
JSONValue: TypeAlias = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]
JSONArray: TypeAlias = list[JSONValue]
JSON: TypeAlias = dict[str, JSONValue]
